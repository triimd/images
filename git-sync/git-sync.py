#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import threading
import time
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import requests
from flask import Flask, jsonify, request


def _utc_now():
    return datetime.utcnow().isoformat() + "Z"


class GitSyncService:
    def __init__(self):
        self.service_id = os.getenv("SERVICE_ID", "git-sync")
        self.node_name = os.getenv("NODE_NAME", "unknown")
        self.gitea_url = os.getenv("GITEA_URL", "https://git.tm0.app").rstrip("/")
        self.gitea_username = os.getenv("GITEA_USERNAME", "git")
        self.gitea_token = os.getenv("GITEA_TOKEN", "")
        self.relay_url = os.getenv("RELAY_URL", "").rstrip("/")
        self.self_endpoint = os.getenv("SELF_ENDPOINT", "").strip()

        self.registration_interval_seconds = int(os.getenv("REGISTER_INTERVAL_SECONDS", "30"))
        self.sync_timeout_seconds = int(os.getenv("SYNC_TIMEOUT_SECONDS", "120"))
        self.archive_retention_days = int(os.getenv("ARCHIVE_RETENTION_DAYS", "90"))

        base_dir = Path(os.getenv("GIT_SYNC_DATA_DIR", "/var/lib/git-sync"))
        self.repos_path = base_dir / "repositories"
        self.archive_path = base_dir / "archived"
        self.state_file = base_dir / "state.json"
        self.log_file = base_dir / "sync.log"

        self.started_at = time.time()
        self.state = self._load_state()
        self._stop = threading.Event()

        self.repos_path.mkdir(parents=True, exist_ok=True)
        self.archive_path.mkdir(parents=True, exist_ok=True)
        self.log_file.touch(exist_ok=True)
        self.askpass_script = self._ensure_askpass_script()

    def _load_state(self):
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {
            "service_id": self.service_id,
            "node_name": self.node_name,
            "started_at": _utc_now(),
            "repos": {},
        }

    def _save_state(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def _log_event(self, action, repo, **fields):
        record = {"ts": _utc_now(), "action": action, "repo": repo, **fields}
        with open(self.log_file, "a") as f:
            f.write(json.dumps(record) + "\n")

    def _repo_path(self, repo_name):
        return self.repos_path / f"{repo_name}.git"

    def _run_git(self, args, env_extra=None):
        env = os.environ.copy()
        env.update(self._git_auth_env())
        if env_extra:
            env.update(env_extra)
        return subprocess.run(args, capture_output=True, text=True, timeout=self.sync_timeout_seconds, env=env)

    def _repo_url(self, repo_name):
        return f"{self.gitea_url}/{repo_name}.git"

    def _ensure_askpass_script(self):
        if not self.gitea_token:
            return ""

        tmp_dir = Path(tempfile.gettempdir())
        script_path = tmp_dir / "git-sync-askpass.sh"
        script_path.write_text(
            "#!/bin/sh\n"
            "case \"$1\" in\n"
            "  *Username*) printf '%s\\n' \"${GIT_ASKPASS_USERNAME}\" ;;\n"
            "  *) printf '%s\\n' \"${GIT_ASKPASS_PASSWORD}\" ;;\n"
            "esac\n"
        )
        script_path.chmod(0o700)
        return str(script_path)

    def _git_auth_env(self):
        if not self.gitea_token or not self.askpass_script:
            return {}

        return {
            "GIT_ASKPASS": self.askpass_script,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_ASKPASS_USERNAME": self.gitea_username,
            "GIT_ASKPASS_PASSWORD": self.gitea_token,
        }

    def sync_repo(self, repo_name):
        repo_path = self._repo_path(repo_name)
        origin = self._repo_url(repo_name)
        if repo_path.exists():
            # Update remote URL in case token changed, then fetch.
            self._run_git(["git", "-C", str(repo_path), "remote", "set-url", "origin", origin])
            result = self._run_git(["git", "-C", str(repo_path), "fetch", "--mirror"])
            action = "fetch"
        else:
            repo_path.parent.mkdir(parents=True, exist_ok=True)
            result = self._run_git(["git", "clone", "--mirror", origin, str(repo_path)])
            action = "clone"

        success = result.returncode == 0
        self._log_event(
            action,
            repo_name,
            result="success" if success else "failed",
            stderr=(result.stderr or "")[-512:],
        )
        return success

    def archive_repo(self, repo_name):
        repo_path = self._repo_path(repo_name)
        if not repo_path.exists():
            return ""

        timestamp = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S")
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
            self.state["repos"][repo_name] = {
                "status": "deleted",
                "deleted_at": _utc_now(),
                "archived_to": archived_to,
            }
            self._save_state()
            return True, "archived"

        if action == "created" or payload.get("ref"):
            synced = self.sync_repo(repo_name)
            if not synced:
                return False, "git sync failed"

            previous = self.state["repos"].get(repo_name, {})
            self.state["repos"][repo_name] = {
                "status": "active",
                "last_synced": _utc_now(),
                "sync_count": int(previous.get("sync_count", 0)) + 1,
            }
            self._save_state()
            return True, "synced"

        return True, "ignored"

    def sync_all(self):
        """Enumerate all repos via Gitea API and clone/fetch each one."""
        if not self.gitea_token:
            return {"error": "GITEA_TOKEN not configured"}, 0, 0, 0

        headers = {"Authorization": f"token {self.gitea_token}"}
        api_base = f"{self.gitea_url}/api/v1"
        page = 1
        limit = 50
        cloned = 0
        updated = 0
        failed = 0

        while True:
            try:
                resp = requests.get(
                    f"{api_base}/repos/search",
                    params={"limit": limit, "page": page},
                    headers=headers,
                    timeout=30,
                )
                if resp.status_code != 200:
                    return {"error": f"Gitea API returned {resp.status_code}"}, cloned, updated, failed
                payload = resp.json()
            except Exception as exc:
                return {"error": str(exc)}, cloned, updated, failed

            repos = payload.get("data", [])
            if not repos:
                break

            for repo in repos:
                full_name = repo.get("full_name")
                if not full_name:
                    continue
                repo_path = self._repo_path(full_name)
                existed = repo_path.exists()
                success = self.sync_repo(full_name)
                if success:
                    if existed:
                        updated += 1
                    else:
                        cloned += 1
                    self.state["repos"][full_name] = {
                        "status": "active",
                        "last_synced": _utc_now(),
                        "sync_count": int(self.state.get("repos", {}).get(full_name, {}).get("sync_count", 0)) + 1,
                    }
                else:
                    failed += 1

            if len(repos) < limit:
                break
            page += 1

        self._save_state()
        return None, cloned, updated, failed

    def restore_from_path(self, source_path):
        """Restore repositories from a local or mounted path using rsync."""
        source = source_path.rstrip("/") + "/"
        dest = str(self.repos_path) + "/"

        result = subprocess.run(
            ["rsync", "-av", "--delete", source, dest],
            capture_output=True, text=True, timeout=600,
        )
        if result.returncode != 0:
            return False, result.stderr[-512:]

        # Rebuild state from restored repos.
        restored = 0
        for owner_dir in self.repos_path.iterdir():
            if not owner_dir.is_dir():
                continue
            for repo_dir in owner_dir.iterdir():
                if repo_dir.is_dir() and repo_dir.name.endswith(".git"):
                    repo_name = f"{owner_dir.name}/{repo_dir.name[:-4]}"
                    self.state["repos"][repo_name] = {
                        "status": "active",
                        "last_synced": _utc_now(),
                        "sync_count": int(self.state.get("repos", {}).get(repo_name, {}).get("sync_count", 0)) + 1,
                    }
                    restored += 1

        self._save_state()
        return True, restored

    def cleanup_old_archives(self):
        cutoff = datetime.utcnow() - timedelta(days=self.archive_retention_days)
        for archive in self.archive_path.rglob("*.git.*"):
            timestamp = archive.name.rsplit(".", 1)[-1]
            try:
                archive_time = datetime.strptime(timestamp, "%Y-%m-%d-%H-%M-%S")
            except ValueError:
                continue

            if archive_time >= cutoff:
                continue

            if archive.is_dir():
                shutil.rmtree(archive, ignore_errors=True)
            else:
                archive.unlink(missing_ok=True)

            self._log_event("cleanup", str(archive.relative_to(self.archive_path)), age_days=(datetime.utcnow() - archive_time).days)

    def register_with_relay(self):
        if not self.relay_url or not self.self_endpoint:
            return False

        payload = {
            "endpoint": self.self_endpoint,
            "service_id": self.service_id,
            "node_name": self.node_name,
        }
        try:
            resp = requests.post(f"{self.relay_url}/register", json=payload, timeout=5)
            return resp.status_code == 200
        except Exception:
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
            "started_at": datetime.fromtimestamp(self.started_at).isoformat() + "Z",
            "uptime_seconds": int(time.time() - self.started_at),
            "relay_registration_enabled": bool(self.relay_url and self.self_endpoint),
            "repos": {"active": active, "deleted": deleted},
        }

    def get_logs(self, lines=100):
        if not self.log_file.exists():
            return []
        with open(self.log_file) as f:
            return [json.loads(line) for line in f.readlines()[-lines:]]


app = Flask(__name__)
service = GitSyncService()


@app.route("/sync", methods=["POST"])
def sync():
    payload = request.get_json(silent=True) or {}
    ok, msg = service.handle_webhook(payload)
    if not ok:
        return jsonify({"error": msg}), 400
    return jsonify({"result": msg}), 200


@app.route("/sync-all", methods=["POST"])
def sync_all():
    error, cloned, updated, failed = service.sync_all()
    status_code = 200 if error is None else 500
    return jsonify({
        "cloned": cloned,
        "updated": updated,
        "failed": failed,
        **({"error": error} if error else {}),
    }), status_code


@app.route("/restore", methods=["POST"])
def restore():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source", "").strip()
    if not source:
        return jsonify({"error": "source path is required"}), 400
    ok, result = service.restore_from_path(source)
    if not ok:
        return jsonify({"error": "rsync failed", "stderr": result}), 500
    return jsonify({"restored": result}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify(service.get_health()), 200


@app.route("/repos", methods=["GET"])
def repos():
    return jsonify(service.state.get("repos", {})), 200


@app.route("/logs", methods=["GET"])
def logs():
    lines = int(request.args.get("lines", "100"))
    return jsonify({"logs": service.get_logs(lines)}), 200


if __name__ == "__main__":
    service.cleanup_old_archives()
    service.start_registration_loop()
    app.run(host="0.0.0.0", port=8080)
