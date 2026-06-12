#!/usr/bin/env python3
"""Smoke-test a running Odysseus Lite instance.

The script intentionally has no project dependencies. It uses only the Python
standard library so it can run from WSL, macOS, Linux, or a small admin box.

Examples:

  ODYSSEUS_USERNAME=admin ODYSSEUS_PASSWORD='...' \
    python3 tools/odysseus_smoke.py --base-url http://192.168.0.127:7000

  ODYSSEUS_USERNAME=admin ODYSSEUS_PASSWORD='...' \
    python3 tools/odysseus_smoke.py --chat --chat-model qwen2.5-coder:3b
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


READ_ONLY_ENDPOINTS = [
    "/api/auth/status",
    "/api/auth/features",
    "/api/runtime",
    "/api/ready",
    "/api/sessions",
    "/api/models",
    "/api/model-endpoints",
    "/api/presets",
    "/api/search/config",
    "/api/search/providers",
    "/api/db/stats",
    "/api/rag/stats",
    "/api/notes",
    "/api/tasks",
    "/api/gallery/library",
    "/api/gallery/stats",
    "/api/documents/library",
    "/api/research/library",
    "/api/calendar/config",
    "/api/email/config",
    "/api/prefs",
]

PAGES = [
    "/",
    "/notes",
    "/calendar",
    "/email",
    "/memory",
    "/gallery",
    "/tasks",
    "/library",
]


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


class Client:
    def __init__(self, base_url: str, timeout: float):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            urllib.request.HTTPCookieProcessor(self.jar)
        )

    def request(
        self,
        method: str,
        path_or_url: str,
        data: Any = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> tuple[int, dict[str, str], bytes]:
        url = path_or_url
        if path_or_url.startswith("/"):
            url = self.base_url + path_or_url

        body = None
        request_headers = dict(headers or {})
        if data is not None:
            if isinstance(data, (dict, list)):
                body = json.dumps(data).encode("utf-8")
                request_headers.setdefault("Content-Type", "application/json")
            elif isinstance(data, str):
                body = data.encode("utf-8")
            else:
                body = data

        req = urllib.request.Request(
            url,
            data=body,
            headers=request_headers,
            method=method.upper(),
        )
        try:
            with self.opener.open(req, timeout=timeout or self.timeout) as response:
                return response.status, dict(response.headers), response.read()
        except urllib.error.HTTPError as exc:
            return exc.code, dict(exc.headers), exc.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return 0, {}, str(exc).encode("utf-8", errors="replace")

    def get_json(self, path_or_url: str, timeout: float | None = None) -> tuple[int, Any]:
        status, _headers, body = self.request("GET", path_or_url, timeout=timeout)
        try:
            return status, json.loads(body.decode("utf-8") or "null")
        except Exception:
            return status, None

    def post_json(
        self, path_or_url: str, payload: dict[str, Any], timeout: float | None = None
    ) -> tuple[int, Any]:
        status, _headers, body = self.request(
            "POST", path_or_url, data=payload, timeout=timeout
        )
        try:
            return status, json.loads(body.decode("utf-8") or "null")
        except Exception:
            return status, None


def add(checks: list[Check], name: str, ok: bool, detail: str = "") -> None:
    checks.append(Check(name, ok, detail))


def safe_text(value: Any, max_len: int = 140) -> str:
    text = str(value)
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def test_login(client: Client, username: str, password: str, checks: list[Check]) -> bool:
    status, payload = client.post_json(
        "/api/auth/login",
        {"username": username, "password": password, "remember": True},
    )
    ok = status == 200 and isinstance(payload, dict) and payload.get("ok") is True
    add(checks, "auth login", ok, f"HTTP {status}")
    if not ok:
        return False

    status, payload = client.get_json("/api/auth/status")
    ok = (
        status == 200
        and isinstance(payload, dict)
        and payload.get("authenticated") is True
    )
    user = payload.get("username") if isinstance(payload, dict) else None
    add(checks, "auth status", ok, f"HTTP {status}, user={user}")
    return ok


def test_pages(client: Client, checks: list[Check]) -> None:
    for page in PAGES:
        status, headers, body = client.request("GET", page)
        ctype = headers.get("content-type", "")
        ok = status == 200 and b"<html" in body[:4096].lower()
        add(checks, f"page {page}", ok, f"HTTP {status}, {ctype}")


def test_read_only_api(client: Client, checks: list[Check]) -> None:
    for path in READ_ONLY_ENDPOINTS:
        status, _payload = client.get_json(path)
        add(checks, f"GET {path}", status == 200, f"HTTP {status}")


def test_models(client: Client, checks: list[Check]) -> tuple[list[dict[str, Any]], list[str]]:
    status, endpoints = client.get_json("/api/model-endpoints")
    rows = endpoints if isinstance(endpoints, list) else []
    online = [row for row in rows if row.get("online")]
    models: list[str] = []
    for row in rows:
        for model in row.get("models") or []:
            if model not in models:
                models.append(model)
    add(
        checks,
        "model endpoints",
        status == 200 and bool(rows),
        f"HTTP {status}, endpoints={len(rows)}, online={len(online)}",
    )
    add(
        checks,
        "model list",
        bool(models),
        ", ".join(models) if models else "no models reported",
    )
    return rows, models


def test_ollama(ollama_url: str, chat_model: str, checks: list[Check], timeout: float) -> None:
    if not ollama_url:
        add(checks, "ollama direct", True, "skipped")
        return

    client = Client(ollama_url, timeout)
    status, version = client.get_json("/api/version")
    add(checks, "ollama version", status == 200, f"HTTP {status}, {version}")

    status, tags = client.get_json("/api/tags")
    names = []
    if isinstance(tags, dict):
        names = [m.get("name") for m in tags.get("models", []) if m.get("name")]
    add(checks, "ollama tags", status == 200 and bool(names), ", ".join(names))

    if chat_model and chat_model in names:
        started = time.monotonic()
        status, payload = client.post_json(
            "/api/chat",
            {
                "model": chat_model,
                "messages": [{"role": "user", "content": "Reply with OK only."}],
                "stream": False,
            },
            timeout=max(timeout, 180),
        )
        elapsed = time.monotonic() - started
        text = ""
        if isinstance(payload, dict):
            text = payload.get("message", {}).get("content", "")
        add(
            checks,
            "ollama chat",
            status == 200 and bool(text.strip()),
            f"HTTP {status}, {elapsed:.1f}s, response={safe_text(text)!r}",
        )


def create_session(
    client: Client,
    endpoint_id: str,
    model: str,
    timeout: float,
) -> tuple[bool, str, str]:
    boundary = "----odysseuslite-smoke"
    fields = {
        "name": "Odysseus Lite smoke test",
        "endpoint_id": endpoint_id,
        "model": model,
        "rag": "false",
    }
    body = b""
    for key, value in fields.items():
        body += f"--{boundary}\r\n".encode("ascii")
        body += (
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n{value}\r\n'
        ).encode("utf-8")
    body += f"--{boundary}--\r\n".encode("ascii")

    status, _headers, raw = client.request(
        "POST",
        "/api/session",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        timeout=timeout,
    )
    try:
        payload = json.loads(raw.decode("utf-8") or "{}")
    except Exception:
        payload = {}
    session_id = payload.get("id") if isinstance(payload, dict) else ""
    return status == 200 and bool(session_id), session_id, f"HTTP {status}, {payload}"


def test_odysseus_chat(
    client: Client,
    endpoints: list[dict[str, Any]],
    preferred_model: str,
    checks: list[Check],
    timeout: float,
) -> None:
    endpoint = None
    for row in endpoints:
        if not row.get("online"):
            continue
        models = row.get("models") or []
        if preferred_model and preferred_model in models:
            endpoint = row
            break
    if endpoint is None:
        for row in endpoints:
            if row.get("online") and row.get("models"):
                endpoint = row
                preferred_model = row["models"][0]
                break
    if endpoint is None:
        add(checks, "odysseus chat", False, "no online endpoint with models")
        return

    ok, session_id, detail = create_session(
        client, str(endpoint["id"]), preferred_model, timeout=max(timeout, 60)
    )
    add(checks, "chat session create", ok, detail)
    if not ok:
        return

    started = time.monotonic()
    status, payload = client.post_json(
        "/api/chat",
        {
            "session": session_id,
            "message": "Reply with OK only.",
            "use_web": False,
            "use_research": False,
        },
        timeout=max(timeout, 240),
    )
    elapsed = time.monotonic() - started
    response = payload.get("response") if isinstance(payload, dict) else ""
    add(
        checks,
        "odysseus chat",
        status == 200 and bool(str(response).strip()),
        f"HTTP {status}, {elapsed:.1f}s, response={safe_text(response)!r}",
    )


def print_report(checks: list[Check]) -> int:
    failures = [check for check in checks if not check.ok]
    width = max((len(check.name) for check in checks), default=10)
    for check in checks:
        status = "ok" if check.ok else "FAIL"
        print(f"{status:4} {check.name:<{width}} {check.detail}")
    print()
    print(f"{len(checks) - len(failures)}/{len(checks)} checks passed")
    return 1 if failures else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.getenv("ODYSSEUS_BASE_URL", "http://192.168.0.127:7000"),
        help="Odysseus base URL",
    )
    parser.add_argument(
        "--username",
        default=os.getenv("ODYSSEUS_USERNAME", ""),
        help="Odysseus username, or ODYSSEUS_USERNAME",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("ODYSSEUS_PASSWORD", ""),
        help="Odysseus password, or ODYSSEUS_PASSWORD",
    )
    parser.add_argument(
        "--ollama-url",
        default=os.getenv("OLLAMA_BASE_URL", ""),
        help="Optional Ollama base URL, e.g. http://192.168.0.127:11434",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        default=os.getenv("ODYSSEUS_SMOKE_CHAT", "").lower() in ("1", "true", "yes"),
        help="Also create a temporary chat session and call the LLM",
    )
    parser.add_argument(
        "--chat-model",
        default=os.getenv("ODYSSEUS_SMOKE_MODEL", "qwen2.5-coder:3b"),
        help="Preferred chat model for the optional chat checks",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.getenv("ODYSSEUS_SMOKE_TIMEOUT", "15")),
        help="Default HTTP timeout in seconds",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    checks: list[Check] = []

    if not args.username or not args.password:
        print(
            "ODYSSEUS_USERNAME and ODYSSEUS_PASSWORD are required.",
            file=sys.stderr,
        )
        return 2

    client = Client(args.base_url, args.timeout)
    status, health = client.get_json("/api/health")
    add(checks, "health", status == 200, f"HTTP {status}, {health}")

    if not test_login(client, args.username, args.password, checks):
        return print_report(checks)

    test_pages(client, checks)
    test_read_only_api(client, checks)
    endpoints, _models = test_models(client, checks)
    test_ollama(args.ollama_url.rstrip("/"), args.chat_model, checks, args.timeout)

    if args.chat:
        test_odysseus_chat(client, endpoints, args.chat_model, checks, args.timeout)

    return print_report(checks)


if __name__ == "__main__":
    raise SystemExit(main())
