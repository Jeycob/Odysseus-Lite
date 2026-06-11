# Odysseus Lite Home Assistant Add-on

This is an experimental single-container Home Assistant add-on for Odysseus.

Odysseus upstream is designed as a Docker Compose stack with Odysseus, ChromaDB,
SearXNG, and ntfy. Home Assistant add-ons are single containers, so this package
runs only the Odysseus web app and lets you configure external services from the
add-on options.

## Install locally on Home Assistant OS

1. Copy this `odysseus` directory to the Home Assistant `/addons/odysseus`
   directory using Samba, Studio Code Server, or Terminal & SSH.
2. In Home Assistant, open Settings > Add-ons > Add-on Store.
3. Use the top-right menu and select Check for updates.
4. Install "Odysseus Lite" from Local add-ons.
5. Open the Configuration tab and adjust options if needed.
6. Start the add-on.
7. Open Odysseus from the Home Assistant sidebar, or use
   `http://192.168.0.127:7000`.

If `admin_password` is empty, Odysseus should create the first admin user and
print the temporary password in the add-on log.

## Notes

- The first build can take a long time on thin-client hardware.
- Local LLM serving is not included. Point `ollama_base_url`, `llm_host`, or API
  keys to an external model provider.
- Personal document semantic search needs an external ChromaDB server if you
  want that feature.
- Web research works best with an external SearXNG instance.

## Home Assistant sidebar

Version 0.3.0 serves Home Assistant Ingress through a small wrapper on port
8099. The wrapper removes iframe-blocking headers from Odysseus and rewrites
absolute `/static` and `/api` paths so the UI can run inside the Home Assistant
sidebar. The direct web UI on port 7000 remains available.
