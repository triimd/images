#!/usr/bin/env python3
import os
import threading
import time

import requests
from flask import Flask, jsonify, request


def _split_csv(value):
    items = []
    for chunk in (value or "").split(","):
        entry = chunk.strip().rstrip("/")
        if entry:
            items.append(entry)
    return items


class GitRelayService:
    def __init__(self):
        self.timeout_seconds = int(os.getenv("RELAY_FANOUT_TIMEOUT_SECONDS", "5"))
        self.endpoint_ttl_seconds = int(os.getenv("RELAY_ENDPOINT_TTL_SECONDS", "120"))
        self.static_endpoints = set(_split_csv(os.getenv("STATIC_ENDPOINTS", "")))

        self._lock = threading.Lock()
        self._dynamic_endpoints = {}

    def register(self, endpoint):
        endpoint = endpoint.rstrip("/")
        if not endpoint:
            return 0
        with self._lock:
            self._dynamic_endpoints[endpoint] = time.time()
            return len(self._dynamic_endpoints)

    def unregister(self, endpoint):
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

    def relay(self, payload):
        endpoints = self.endpoints()
        failures = []

        for endpoint in endpoints:
            try:
                resp = requests.post(f"{endpoint}/sync", json=payload, timeout=self.timeout_seconds)
                if resp.status_code != 200:
                    failures.append({"endpoint": endpoint, "status": resp.status_code})
            except Exception:
                failures.append({"endpoint": endpoint, "status": "error"})

        return {
            "targets": len(endpoints),
            "success": len(endpoints) - len(failures),
            "failed": failures,
        }


app = Flask(__name__)
relay_service = GitRelayService()


@app.route("/register", methods=["POST"])
def register():
    payload = request.get_json(silent=True) or {}
    endpoint = str(payload.get("endpoint", "")).strip()
    if not endpoint:
        return jsonify({"error": "missing endpoint"}), 400
    total = relay_service.register(endpoint)
    return jsonify({"registered": endpoint, "dynamic_total": total}), 200


@app.route("/unregister", methods=["POST"])
def unregister():
    payload = request.get_json(silent=True) or {}
    endpoint = str(payload.get("endpoint", "")).strip()
    if not endpoint:
        return jsonify({"error": "missing endpoint"}), 400
    total = relay_service.unregister(endpoint)
    return jsonify({"unregistered": endpoint, "dynamic_total": total}), 200


@app.route("/endpoints", methods=["GET"])
def endpoints():
    values = relay_service.endpoints()
    return jsonify({"endpoints": values, "count": len(values)}), 200


@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "missing json payload"}), 400
    result = relay_service.relay(payload)
    return jsonify(result), 200


@app.route("/health", methods=["GET"])
def health():
    values = relay_service.endpoints()
    return jsonify({"status": "ok", "endpoints": len(values)}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
