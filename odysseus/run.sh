#!/usr/bin/env bash
set -euo pipefail

OPTIONS_FILE="/data/options.json"
ENV_FILE="/tmp/odysseus-addon.env"

python3 - <<'PY' > "${ENV_FILE}"
import json
import shlex
from pathlib import Path

options_path = Path("/data/options.json")
options = json.loads(options_path.read_text()) if options_path.exists() else {}


def emit(name, value):
    if value is None:
        return
    if isinstance(value, str) and value == "":
        return
    print(f"export {name}={shlex.quote(str(value))}")


emit("APP_BIND", "0.0.0.0")
emit("APP_PORT", "7000")
emit("ODYSSEUS_DATA_DIR", "/data/odysseus")
emit("DATABASE_URL", "sqlite:////data/odysseus/app.db")
emit("FASTEMBED_CACHE_PATH", "/data/odysseus/fastembed")
emit("HF_HOME", "/data/odysseus/huggingface")
emit("HUGGINGFACE_HUB_CACHE", "/data/odysseus/huggingface")
emit("AUTH_ENABLED", "true" if options.get("auth_enabled", True) else "false")
emit("ODYSSEUS_ADMIN_USER", options.get("admin_user", "admin"))
emit("ODYSSEUS_ADMIN_PASSWORD", options.get("admin_password", ""))
emit("ODYSSEUS_RESET_ADMIN_PASSWORD_ON_START", "true" if options.get("reset_admin_password_on_start", False) else "false")
emit("ALLOWED_ORIGINS", options.get("allowed_origins", ""))
emit("LLM_HOST", options.get("llm_host", ""))
emit("LLM_HOSTS", options.get("llm_hosts", ""))
emit("OLLAMA_BASE_URL", options.get("ollama_base_url", ""))
emit("ODYSSEUS_AUTO_CONFIGURE_OLLAMA", "true" if options.get("auto_configure_ollama", True) else "false")
emit("ODYSSEUS_OLLAMA_MODEL", options.get("ollama_model", "qwen2.5-coder:7b"))
emit("OPENAI_API_KEY", options.get("openai_api_key", ""))
emit("SEARXNG_INSTANCE", options.get("searxng_instance", ""))
emit("CHROMADB_HOST", options.get("chromadb_host", ""))
emit("CHROMADB_PORT", options.get("chromadb_port", ""))
emit("FASTEMBED_MODEL", options.get("fastembed_model", ""))

try:
    default_timeout = int(options.get("llm_default_timeout_seconds", 120))
except (TypeError, ValueError):
    default_timeout = 120
try:
    stream_timeout = int(options.get("llm_stream_timeout_seconds", 600))
except (TypeError, ValueError):
    stream_timeout = 600
emit("ODYSSEUS_LLM_DEFAULT_TIMEOUT", max(default_timeout, 30))
emit("ODYSSEUS_LLM_STREAM_TIMEOUT", max(stream_timeout, 60))
emit("ODYSSEUS_AI_CHAT_TIMEOUT", max(stream_timeout, 60))

try:
    upload_mb = int(options.get("chat_upload_max_mb", 10))
except (TypeError, ValueError):
    upload_mb = 10
emit("ODYSSEUS_CHAT_UPLOAD_MAX_BYTES", max(upload_mb, 1) * 1024 * 1024)
emit("ODYSSEUS_AGENT_WORKDIR", options.get("workspace_dir", "/share/odysseus-workspace"))
emit("ODYSSEUS_TOOLS_DIR", options.get("tools_dir", "/share/odysseus-tools"))
emit("ODYSSEUS_RUN_WORKSPACE_BOOTSTRAP", "true" if options.get("run_workspace_bootstrap", False) else "false")
emit("ODYSSEUS_WORKSPACE_BOOTSTRAP_SCRIPT", options.get("workspace_bootstrap_script", "/share/odysseus-workspace/bootstrap.sh"))
PY

# shellcheck disable=SC1090
. "${ENV_FILE}"

mkdir -p /data/odysseus /data/logs /data/odysseus/fastembed /data/odysseus/huggingface

ODYSSEUS_AGENT_WORKDIR="${ODYSSEUS_AGENT_WORKDIR:-/share/odysseus-workspace}"
ODYSSEUS_TOOLS_DIR="${ODYSSEUS_TOOLS_DIR:-/share/odysseus-tools}"
mkdir -p \
  "${ODYSSEUS_AGENT_WORKDIR}" \
  "${ODYSSEUS_AGENT_WORKDIR}/.local/bin" \
  "${ODYSSEUS_TOOLS_DIR}/bin" \
  "${ODYSSEUS_TOOLS_DIR}/dotnet" \
  "${ODYSSEUS_TOOLS_DIR}/tmp"

export ODYSSEUS_AGENT_WORKDIR
export ODYSSEUS_TOOLS_DIR
export PATH="${ODYSSEUS_AGENT_WORKDIR}/.local/bin:${ODYSSEUS_TOOLS_DIR}/bin:${ODYSSEUS_TOOLS_DIR}/dotnet:${PATH}"

if [ ! -f "${ODYSSEUS_AGENT_WORKDIR}/README.md" ]; then
  cat > "${ODYSSEUS_AGENT_WORKDIR}/README.md" <<'EOF'
# Odysseus Workspace

This directory is persistent Home Assistant `/share` storage.

Agent bash, python, read_file, write_file, grep, glob, and ls tools default here.
Project files created here survive add-on restarts and updates and are visible
through Samba/Studio Code Server under `share/odysseus-workspace`.

Runtime-installed user tools should go under `/share/odysseus-tools`.
For .NET, the add-on provides:

```bash
install-dotnet-sdk
```

To replay trusted setup commands on every add-on start, create:

```text
/share/odysseus-workspace/bootstrap.sh
```

then enable `run_workspace_bootstrap` in the add-on Configuration tab.
EOF
fi

if [ "${ODYSSEUS_RUN_WORKSPACE_BOOTSTRAP:-false}" = "true" ]; then
  BOOTSTRAP_SCRIPT="${ODYSSEUS_WORKSPACE_BOOTSTRAP_SCRIPT:-${ODYSSEUS_AGENT_WORKDIR}/bootstrap.sh}"
  if [ -f "${BOOTSTRAP_SCRIPT}" ]; then
    echo "[Odysseus Lite] Running workspace bootstrap: ${BOOTSTRAP_SCRIPT}"
    chmod +x "${BOOTSTRAP_SCRIPT}" || true
    "${BOOTSTRAP_SCRIPT}"
  else
    echo "[Odysseus Lite] Workspace bootstrap enabled but script was not found: ${BOOTSTRAP_SCRIPT}"
  fi
fi

if [ ! -L /opt/odysseus/data ]; then
  rm -rf /opt/odysseus/data
  ln -s /data/odysseus /opt/odysseus/data
fi

if [ ! -L /opt/odysseus/logs ]; then
  rm -rf /opt/odysseus/logs
  ln -s /data/logs /opt/odysseus/logs
fi

cd /opt/odysseus
python setup.py || true

python3 - <<'PY'
import json
import os
import secrets
import shutil
import time
from pathlib import Path

import bcrypt

DATA_DIR = Path(os.environ.get("ODYSSEUS_DATA_DIR", "/data/odysseus"))
AUTH_FILE = DATA_DIR / "auth.json"
ADMIN_USER = (os.environ.get("ODYSSEUS_ADMIN_USER") or "admin").strip().lower() or "admin"
ADMIN_PASSWORD = os.environ.get("ODYSSEUS_ADMIN_PASSWORD") or ""
RESET_PASSWORD = os.environ.get("ODYSSEUS_RESET_ADMIN_PASSWORD_ON_START", "false").lower() == "true"


def _hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _admin_privileges():
    try:
        from core.auth import ADMIN_PRIVILEGES
        return dict(ADMIN_PRIVILEGES)
    except Exception:
        return {}


def _admin_record(password):
    record = {
        "password_hash": _hash_password(password),
        "created": time.time(),
        "is_admin": True,
    }
    privileges = _admin_privileges()
    if privileges:
        record["privileges"] = privileges
    return record


def _read_auth():
    if not AUTH_FILE.exists():
        return {}, "missing"
    try:
        data = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}, "invalid"
        users = data.get("users")
        if users is None:
            if isinstance(data.get("password_hash"), str):
                username = str(data.get("username") or ADMIN_USER).strip().lower() or ADMIN_USER
                data = {
                    "users": {
                        username: {
                            "password_hash": data["password_hash"],
                            "created": data.get("created", time.time()),
                            "is_admin": True,
                        }
                    }
                }
            else:
                data["users"] = {}
        elif not isinstance(users, dict):
            return {}, "invalid"
        return data, "ok"
    except Exception:
        return {}, "invalid"


def _write_auth(data):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = AUTH_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(AUTH_FILE)
    AUTH_FILE.chmod(0o600)


auth, status = _read_auth()
users = auth.get("users", {})

if status == "invalid" and AUTH_FILE.exists():
    backup = AUTH_FILE.with_name(f"auth.json.broken.{int(time.time())}")
    shutil.move(str(AUTH_FILE), str(backup))
    print(f"[Odysseus Lite] Existing auth.json was invalid; moved it to {backup.name}")
    auth = {"users": {}}
    users = auth["users"]

if users:
    normalized = {}
    changed = False
    for username, record in users.items():
        key = str(username or "").strip().lower()
        if not key:
            changed = True
            continue
        if not isinstance(record, dict):
            record = {}
            changed = True
        normalized[key] = record
        if key != username:
            changed = True
    auth["users"] = normalized
    users = normalized

    if RESET_PASSWORD:
        if not ADMIN_PASSWORD:
            print("[Odysseus Lite] reset_admin_password_on_start is enabled, but admin_password is empty; leaving auth.json unchanged")
        else:
            user = users.get(ADMIN_USER)
            if not isinstance(user, dict):
                user = {}
                users[ADMIN_USER] = user
            user.update(_admin_record(ADMIN_PASSWORD))
            _write_auth(auth)
            print(f"[Odysseus Lite] Admin password reset for '{ADMIN_USER}'. Turn reset_admin_password_on_start off after login.")
    elif changed:
        _write_auth(auth)

    admins = sorted(name for name, data in users.items() if isinstance(data, dict) and data.get("is_admin"))
    print(f"[Odysseus Lite] Auth configured: {len(users)} user(s), admin(s): {', '.join(admins) or 'none'}")
else:
    password = ADMIN_PASSWORD or secrets.token_urlsafe(18)
    auth = {"users": {ADMIN_USER: _admin_record(password)}}
    _write_auth(auth)
    print(f"[Odysseus Lite] Initial admin user created ({ADMIN_USER})")
    if ADMIN_PASSWORD:
        print("[Odysseus Lite] Initial admin password was taken from the add-on Configuration tab.")
    else:
        print(f"[Odysseus Lite] Temporary password: {password}")
        print("[Odysseus Lite] Change it after first login, or set admin_password in the add-on Configuration tab.")
PY

python3 - <<'PY'
import json
import os
import uuid

AUTO_CONFIGURE = os.environ.get("ODYSSEUS_AUTO_CONFIGURE_OLLAMA", "true").lower() == "true"
BASE_URL = (os.environ.get("OLLAMA_BASE_URL") or "").strip().rstrip("/")
MODEL = (os.environ.get("ODYSSEUS_OLLAMA_MODEL") or "qwen2.5-coder:7b").strip()

if AUTO_CONFIGURE and BASE_URL and MODEL:
    try:
        from core.database import ModelEndpoint, SessionLocal
        db = SessionLocal()
        try:
            existing = (
                db.query(ModelEndpoint)
                .filter(ModelEndpoint.base_url == BASE_URL)
                .first()
            )
            models_json = json.dumps([MODEL])
            if existing:
                changed = False
                if not existing.name:
                    existing.name = "Ollama Lite"
                    changed = True
                if not existing.is_enabled:
                    existing.is_enabled = True
                    changed = True
                if getattr(existing, "endpoint_kind", None) in (None, "", "auto", "api", "proxy"):
                    existing.endpoint_kind = "local"
                    changed = True
                if not getattr(existing, "model_refresh_mode", None):
                    existing.model_refresh_mode = "auto"
                    changed = True
                cached = []
                try:
                    cached = json.loads(existing.cached_models or "[]")
                except Exception:
                    cached = []
                if MODEL not in cached:
                    cached.append(MODEL)
                    existing.cached_models = json.dumps(cached)
                    changed = True
                pinned = []
                try:
                    pinned = json.loads(existing.pinned_models or "[]")
                except Exception:
                    pinned = []
                if MODEL not in pinned:
                    pinned.append(MODEL)
                    existing.pinned_models = json.dumps(pinned)
                    changed = True
                if changed:
                    db.commit()
                    print(f"[Odysseus Lite] Updated Ollama endpoint: {BASE_URL} ({MODEL})")
                else:
                    print(f"[Odysseus Lite] Ollama endpoint already configured: {BASE_URL} ({MODEL})")
            else:
                ep = ModelEndpoint(
                    id=str(uuid.uuid4())[:8],
                    name="Ollama Lite",
                    base_url=BASE_URL,
                    api_key=None,
                    is_enabled=True,
                    model_type="llm",
                    endpoint_kind="local",
                    model_refresh_mode="auto",
                    cached_models=models_json,
                    pinned_models=models_json,
                    owner=None,
                )
                db.add(ep)
                db.commit()
                print(f"[Odysseus Lite] Added Ollama endpoint: {BASE_URL} ({MODEL})")
        finally:
            db.close()
    except Exception as exc:
        print(f"[Odysseus Lite] Could not auto-configure Ollama endpoint: {exc}")
PY

python -m uvicorn app:app --host 0.0.0.0 --port 7000 &
ODYSSEUS_PID="$!"

cleanup() {
  kill "${ODYSSEUS_PID}" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

python3 - <<'PY'
import time
import urllib.request

for _ in range(90):
    try:
        with urllib.request.urlopen("http://127.0.0.1:7000/api/health", timeout=2) as response:
            if response.status < 500:
                raise SystemExit(0)
    except Exception:
        time.sleep(1)
raise SystemExit("Odysseus did not become healthy on port 7000")
PY

exec python -m uvicorn ingress_proxy:proxy_app --host 0.0.0.0 --port 8099
