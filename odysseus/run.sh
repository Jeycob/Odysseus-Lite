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
emit("ALLOWED_ORIGINS", options.get("allowed_origins", ""))
emit("LLM_HOST", options.get("llm_host", ""))
emit("LLM_HOSTS", options.get("llm_hosts", ""))
emit("OLLAMA_BASE_URL", options.get("ollama_base_url", ""))
emit("OPENAI_API_KEY", options.get("openai_api_key", ""))
emit("SEARXNG_INSTANCE", options.get("searxng_instance", ""))
emit("CHROMADB_HOST", options.get("chromadb_host", ""))
emit("CHROMADB_PORT", options.get("chromadb_port", ""))
emit("FASTEMBED_MODEL", options.get("fastembed_model", ""))

try:
    upload_mb = int(options.get("chat_upload_max_mb", 10))
except (TypeError, ValueError):
    upload_mb = 10
emit("ODYSSEUS_CHAT_UPLOAD_MAX_BYTES", max(upload_mb, 1) * 1024 * 1024)
PY

# shellcheck disable=SC1090
. "${ENV_FILE}"

mkdir -p /data/odysseus /data/logs /data/odysseus/fastembed /data/odysseus/huggingface

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
