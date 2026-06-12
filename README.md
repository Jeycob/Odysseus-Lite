# Odysseus Lite Add-ons

Home Assistant add-on repository for Odysseus Lite.

## Add Repository

In Home Assistant, open Settings > Add-ons > Add-on Store, then add this
repository URL:

```text
https://github.com/Jeycob/Odysseus-Lite
```

Install `Odysseus Lite` from the add-on store.

## Smoke Test A Running Instance

The `tools/odysseus_smoke.py` script checks a running Odysseus Lite instance
without any third-party Python dependencies.

Read-only smoke test:

```bash
ODYSSEUS_USERNAME=admin \
ODYSSEUS_PASSWORD='your-password' \
python3 tools/odysseus_smoke.py --base-url http://192.168.0.127:7000
```

Include a direct Ollama check:

```bash
ODYSSEUS_USERNAME=admin \
ODYSSEUS_PASSWORD='your-password' \
OLLAMA_BASE_URL=http://192.168.0.127:11434 \
python3 tools/odysseus_smoke.py --base-url http://192.168.0.127:7000
```

Run a real chat check as well:

```bash
ODYSSEUS_USERNAME=admin \
ODYSSEUS_PASSWORD='your-password' \
OLLAMA_BASE_URL=http://192.168.0.127:11434 \
python3 tools/odysseus_smoke.py \
  --base-url http://192.168.0.127:7000 \
  --chat \
  --chat-model qwen2.5-coder:3b
```

The chat check creates a temporary Odysseus chat session and sends a short
prompt to the selected model.
