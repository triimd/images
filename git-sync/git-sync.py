#!/usr/bin/env python3

import json
import os
import shutil
import subprocess
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from flask import Flask, jsonify, request


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_int_env(name: str, default: int, minimum: int = 1) -> int:
    value = os.getenv(name, str(default)).strip()
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(parsed, minimum)


def parse_int(value: str, default: int, minimum: int = 1) -> int:
    try:
        parsed = int(value.strip())
    except (AttributeError, ValueError):
        return default
    return max(parsed, minimum)


class GitSyncService:
    def __init__(self):
        self.service_id = os.getenv("SERVICE_ID", "git-sync")
        self.node_name = os.getenv("NODE_NAME", "unknown")
        self.gitea_url = os.getenv("GITEA_URL", "https://git.tm0.app").rstrip("/")
        self.relay_url = os.getenv("RELAY_URL", "").rstrip("/")
        self.self_endpoint = os.getenv("SELF_ENDPOINT", "").rstrip("/")
        self.relay_registration_token = os.getenv("RELAY_REGISTRATION_TOKEN", "")

        self.registration_interval_seconds = parse_int_env("REGISTER_INTERVAL_SECONDS", 30)
        self.sync_timeout_seconds = parse_int_env("SYNC_TIMEOUT_SECONDS", 120)
        self.archive_retention_days = parse_int_env("ARCHIVE_RETENTION_DAYS", 90)

        base_dir = Path(os.getenv("GIT_SYNC_DATA_DIR", "/var/lib/git-sync"))
        self.repos_path = base_dir / "repositories"
        self.archive_path = base_dir / "archived"
        self.state_file = base_dir / "state.json"
        self.log_file = base_dir / "sync.log"

        self.started_at = time.time()
        self._state_lock = threading.Lock()
        self._stop = threading.Event()

        self.repos_path.mkdir(parents=True, exist_ok=True)
        self.archive_path.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self.log_file.touch(exist_ok=True)

        self.state = self._load_state()

    def _default_state(self):
        return {
            "service_id": self.service_id,
            "node_name": self.node_name,
            "started_at": utc_now(),
            "repos": {},
        }

    def _load_state(self):
        if not self.state_file.exists():
            return self._default_state()

        try:
            with self.state_file.open("r", encoding="utf-8") as handle:
                state = json.load(handle)
            if isinstance(state, dict) and isinstance(state.get("repos", {}), dict):
                return state
        except (OSError, json.JSONDecodeError):
            pass

        self._log_event("state", "_service", result="failed", reason="state file unreadable")
        return self._default_state()

    def _save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with self.state_file.open("w", encoding="utf-8") as handle:
            json.dump(self.state, handle, indent=2, sort_keys=True)

    def _log_event(self, action, repo, **fields):
        record = {"ts": utc_now(), "action": action, "repo": repo, **fields}
        with self.log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")

    def _repo_path(self, repo_name: str) -> Path:
        return self.repos_path / f"{repo_name}.git"

    def _origin_url(self, repo_name: str) -> str:
        return f"{self.gitea_url}/{repo_name}.git"

    def _run_git(self, args):
        try:
            return subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=self.sync_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stderr_output = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            stdout_output = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            return subprocess.CompletedProcess(
                args=args,
                returncode=124,
                stdout=stdout_output,
                stderr=stderr_output + "\ngit command timed out",
            )

    def sync_repo(self, repo_name: str) -> bool:
        repo_path = self._repo_path(repo_name)
        repo_path.parent.mkdir(parents=True, exist_ok=True)
        origin = self._origin_url(repo_name)

        if repo_path.exists():
            self._run_git(["git", "-C", str(repo_path), "remote", "set-url", "origin", origin])
            result = self._run_git(
                ["git", "-C", str(repo_path), "fetch", "--prune", "--prune-tags", "--force", "origin"]
            )
            action = "fetch"
        else:
            result = self._run_git(["git", "clone", "--mirror", origin, str(repo_path)])
            action = "clone"

        success = result.returncode == 0
        self._log_event(
            action,
            repo_name,
            result="success" if success else "failed",
            stderr=(result.stderr or "")[-1024:],
        )
        return success

    def archive_repo(self, repo_name: str) -> str:
        repo_path = self._repo_path(repo_name)
        if not repo_path.exists():
            return ""

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
        archive_path = self.archive_path / f"{repo_name}.git.{timestamp}"
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        repo_path.rename(archive_path)
        self._log_event("archive", repo_name, archived_to=str(archive_path))
        return str(archive_path)

    def handle_webhook(self, payload):
        action = payload.get("action")
        repo_name = payload.get("repository", {}).get("full_name")
        if not repo_name:
            return False, "missing repository.full_name"

        if action == "deleted":
            archived_to = self.archive_repo(repo_name)
            with self._state_lock:
                self.state["repos"][repo_name] = {
                    "status": "deleted",
                    "deleted_at": utc_now(),
                    "archived_to": archived_to,
                }
                self._save_state()
            return True, "archived"

        if action == "created" or payload.get("ref"):
            if not self.sync_repo(repo_name):
                return False, "git sync failed"

            with self._state_lock:
                previous = self.state["repos"].get(repo_name, {})
                self.state["repos"][repo_name] = {
                    "status": "active",
                    "last_synced": utc_now(),
                    "sync_count": int(previous.get("sync_count", 0)) + 1,
                }
                self._save_state()
            return True, "synced"

        return True, "ignored"

    def cleanup_old_archives(self):
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.archive_retention_days)
        for archive in self.archive_path.rglob("*.git.*"):
            timestamp = archive.name.rsplit(".", 1)[-1]
            try:
                archive_time = datetime.strptime(timestamp, "%Y-%m-%d-%H-%M-%S").replace(tzinfo=timezone.utc)
            except ValueError:
                continue

            if archive_time >= cutoff:
                continue

            if archive.is_dir():
                shutil.rmtree(archive, ignore_errors=True)
            else:
                archive.unlink(missing_ok=True)

            self._log_event(
                "cleanup",
                str(archive.relative_to(self.archive_path)),
                age_days=(datetime.now(timezone.utc) - archive_time).days,
            )

    def register_with_relay(self) -> bool:
        if not self.relay_url or not self.self_endpoint:
            return False

        payload = {
            "endpoint": self.self_endpoint,
            "service_id": self.service_id,
            "node_name": self.node_name,
        }
        headers = {}
        if self.relay_registration_token:
            headers["X-Relay-Token"] = self.relay_registration_token

        try:
            response = requests.post(f"{self.relay_url}/register", json=payload, headers=headers, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def start_registration_loop(self):
        if not self.relay_url or not self.self_endpoint:
            return

        def loop():
            while not self._stop.is_set():
                self.register_with_relay()
                self._stop.wait(self.registration_interval_seconds)

        thread = threading.Thread(target=loop, name="relay-registration", daemon=True)
        thread.start()

    def get_health(self):
        repos = self.state.get("repos", {})
        active = sum(1 for item in repos.values() if item.get("status") == "active")
        deleted = sum(1 for item in repos.values() if item.get("status") == "deleted")
        return {
            "service_id": self.service_id,
            "node_name": self.node_name,
            "started_at": datetime.fromtimestamp(self.started_at, tz=timezone.utc).isoformat().replace("+00:00", "Z"),
            "uptime_seconds": int(time.time() - self.started_at),
            "relay_registration_enabled": bool(self.relay_url and self.self_endpoint),
            "repos": {"active": active, "deleted": deleted},
        }

    def get_logs(self, lines=100):
        line_count = max(1, min(lines, 1000))
        if not self.log_file.exists():
            return []
        with self.log_file.open("r", encoding="utf-8") as handle:
            rows = handle.readlines()[-line_count:]
        records = []
        for row in rows:
            row = row.strip()
            if not row:
                continue
            try:
                records.append(json.loads(row))
            except json.JSONDecodeError:
                continue
        return records


app = Flask(__name__)
service = GitSyncService()


@app.route("/sync", methods=["POST"])
def sync_endpoint():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "missing json payload"}), 400
    ok, message = service.handle_webhook(payload)
    if not ok:
        return jsonify({"error": message}), 400
    return jsonify({"result": message}), 200


@app.route("/health", methods=["GET"])
def health_endpoint():
    return jsonify(service.get_health()), 200


@app.route("/repos", methods=["GET"])
def repos_endpoint():
    return jsonify(service.state.get("repos", {})), 200


@app.route("/logs", methods=["GET"])
def logs_endpoint():
    lines = parse_int(request.args.get("lines", "100"), default=100, minimum=1)
    return jsonify({"logs": service.get_logs(lines)}), 200


if __name__ == "__main__":
    service.cleanup_old_archives()
    service.start_registration_loop()
    app.run(host="0.0.0.0", port=parse_int_env("PORT", 8080))
