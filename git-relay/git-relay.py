#!/usr/bin/env python3

import hashlib
import hmac
import os
import threading
import time

import requests
from flask import Flask, jsonify, request


def split_csv(value: str):
    entries = []
    for chunk in (value or "").split(","):
        item = chunk.strip().rstrip("/")
        if item:
            entries.append(item)
    return entries


def parse_int_env(name: str, default: int, minimum: int = 1) -> int:
    value = os.getenv(name, str(default)).strip()
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(parsed, minimum)


class GitRelayService:
    def __init__(self):
        self.timeout_seconds = parse_int_env("RELAY_FANOUT_TIMEOUT_SECONDS", 5)
        self.endpoint_ttl_seconds = parse_int_env("RELAY_ENDPOINT_TTL_SECONDS", 120)
        self.max_payload_bytes = parse_int_env("MAX_PAYLOAD_BYTES", 1024 * 1024)

        self.static_endpoints = set(split_csv(os.getenv("STATIC_ENDPOINTS", "")))
        self.webhook_secret = os.getenv("WEBHOOK_SECRET", "")
        self.registration_token = os.getenv("REGISTRATION_TOKEN", "")

        self._lock = threading.Lock()
        self._dynamic_endpoints = {}

    def registration_allowed(self, token_header: str) -> bool:
        if not self.registration_token:
            return True
        token = (token_header or "").strip()
        return hmac.compare_digest(token, self.registration_token)

    def register(self, endpoint: str) -> int:
        endpoint = endpoint.rstrip("/")
        if not endpoint:
            return 0
        with self._lock:
            self._dynamic_endpoints[endpoint] = time.time()
            return len(self._dynamic_endpoints)

    def unregister(self, endpoint: str) -> int:
        endpoint = endpoint.rstrip("/")
        with self._lock:
            self._dynamic_endpoints.pop(endpoint, None)
            return len(self._dynamic_endpoints)

    def _prune(self):
        if self.endpoint_ttl_seconds <= 0:
            return
        cutoff = time.time() - self.endpoint_ttl_seconds
        with self._lock:
            stale = [endpoint for endpoint, updated_at in self._dynamic_endpoints.items() if updated_at < cutoff]
            for endpoint in stale:
                self._dynamic_endpoints.pop(endpoint, None)

    def endpoints(self):
        self._prune()
        with self._lock:
            dynamic = list(self._dynamic_endpoints.keys())
        return sorted(set(dynamic) | self.static_endpoints)

    def verify_signature(self, body: bytes, headers) -> bool:
        if not self.webhook_secret:
            return True

        provided = (
            headers.get("X-Gitea-Signature")
            or headers.get("X-Hub-Signature-256")
            or headers.get("X-Gogs-Signature")
            or ""
        ).strip()

        if provided.startswith("sha256="):
            provided = provided[7:]

        if not provided:
            return False

        expected = hmac.new(self.webhook_secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(provided, expected)

    def relay(self, payload):
        endpoints = self.endpoints()
        failures = []

        for endpoint in endpoints:
            try:
                response = requests.post(f"{endpoint}/sync", json=payload, timeout=self.timeout_seconds)
                if response.status_code != 200:
                    failures.append({"endpoint": endpoint, "status": response.status_code})
            except requests.RequestException:
                failures.append({"endpoint": endpoint, "status": "error"})

        return {
            "targets": len(endpoints),
            "success": len(endpoints) - len(failures),
            "failed": failures,
        }


app = Flask(__name__)
relay_service = GitRelayService()


@app.route("/register", methods=["POST"])
def register_endpoint():
    if not relay_service.registration_allowed(request.headers.get("X-Relay-Token", "")):
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    endpoint = str(payload.get("endpoint", "")).strip()
    if not endpoint:
        return jsonify({"error": "missing endpoint"}), 400

    total = relay_service.register(endpoint)
    return jsonify({"registered": endpoint, "dynamic_total": total}), 200


@app.route("/unregister", methods=["POST"])
def unregister_endpoint():
    if not relay_service.registration_allowed(request.headers.get("X-Relay-Token", "")):
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    endpoint = str(payload.get("endpoint", "")).strip()
    if not endpoint:
        return jsonify({"error": "missing endpoint"}), 400

    total = relay_service.unregister(endpoint)
    return jsonify({"unregistered": endpoint, "dynamic_total": total}), 200


@app.route("/endpoints", methods=["GET"])
def endpoints_endpoint():
    values = relay_service.endpoints()
    return jsonify({"endpoints": values, "count": len(values)}), 200


@app.route("/webhook", methods=["POST"])
def webhook_endpoint():
    body = request.get_data(cache=True)
    if len(body) > relay_service.max_payload_bytes:
        return jsonify({"error": "payload too large"}), 413

    if not relay_service.verify_signature(body, request.headers):
        return jsonify({"error": "invalid webhook signature"}), 401

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "missing json payload"}), 400

    result = relay_service.relay(payload)
    status = 200 if not result["failed"] else 502
    return jsonify(result), status


@app.route("/health", methods=["GET"])
def health_endpoint():
    values = relay_service.endpoints()
    return (
        jsonify(
            {
                "status": "ok",
                "endpoints": len(values),
                "signature_required": bool(relay_service.webhook_secret),
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=parse_int_env("PORT", 8080))
