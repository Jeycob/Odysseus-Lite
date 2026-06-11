# Odysseus Lite Home Assistant Add-on

This is an experimental single-container Home Assistant add-on for Odysseus.

Odysseus upstream is designed as a Docker Compose stack with Odysseus, ChromaDB,
SearXNG, and ntfy. Home Assistant add-ons are single containers, so this package
runs only the Odysseus web app and lets you configure external services from the
add-on options.

## Install from this repository

1. In Home Assistant, open Settings > Add-ons > Add-on Store.
2. Open the top-right menu, select Repositories, and add:

   ```text
   https://github.com/Jeycob/Odysseus-Lite
   ```

3. Install "Odysseus Lite".
4. Open the Configuration tab and adjust options if needed.
5. Start the add-on.
6. Open Odysseus from the Home Assistant sidebar, or use
   `http://192.168.0.127:7000`.

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

## First Login

Odysseus Lite stores users in the add-on data directory:

```text
/data/odysseus/auth.json
```

On the first start, the add-on validates that file before the web UI starts.

- If at least one user exists, the add-on leaves the file unchanged and prints
  the configured users/admins in the log.
- If `auth.json` is missing, invalid, or contains no users, the add-on creates
  the first admin account.
- If `admin_password` is empty, the add-on prints a generated temporary password
  in the add-on log.
- If `admin_password` is set in the Configuration tab, that password is used for
  the initial admin account.

Use the `admin_user` value from the Configuration tab. The default username is:

```text
admin
```

After login, change the password in Odysseus Settings > Account.

## If The Setup Screen Appears Again

The login page should show "Sign In" once `auth.json` contains at least one
user. If it asks you to "Create Admin Account" again, one of these happened:

- the current add-on instance has an empty or missing `auth.json`;
- `auth.json` exists but is invalid JSON;
- you moved from the old local add-on to the GitHub repository add-on.

Home Assistant stores data separately per add-on slug/source. A local add-on
such as `local_odysseus_lite` and the GitHub add-on
`7e8cacbe_odysseus_lite` do not share their `/data` directory. In that case,
the user from the old local instance is not automatically available in the new
GitHub instance.

Version 0.3.2 fixes the common broken/empty `auth.json` case by validating the
file at every start and creating an admin account if the file has no users.

## Reset Admin Password

If an admin user exists but you lost the password:

1. Stop the add-on.
2. Open the Configuration tab.
3. Set `admin_user` to the admin username you want to reset.
4. Set `admin_password` to the new password.
5. Set `reset_admin_password_on_start` to `true`.
6. Start the add-on and log in with the new password.
7. Turn `reset_admin_password_on_start` back to `false`.

Leaving `reset_admin_password_on_start` enabled is safe but annoying: every
restart will reset that admin password again.

## Notes

- The first build can take a long time on thin-client hardware.
- Local LLM serving is not included. Point `ollama_base_url`, `llm_host`, or API
  keys to an external model provider.
- If you use Ollama Lite on the same Home Assistant host, add it in Odysseus as
  native Ollama:

  ```text
  Provider: Ollama
  Base URL: http://192.168.0.127:11434
  Model: qwen2.5-coder:7b
  ```

  Prefer this over OpenAI-compatible `/v1` for local Ollama. The native Ollama
  route lets Odysseus use Ollama-specific request/stream handling.
- Personal document semantic search needs an external ChromaDB server if you
  want that feature.
- Web research works best with an external SearXNG instance.

## Blank Replies With Ollama

If Odysseus creates an empty assistant message and the Ollama Lite log shows
`POST /v1/chat/completions` returning `500`, Odysseus is probably talking to
Ollama through the OpenAI-compatible `/v1` endpoint and the local CPU model is
too slow for the old request timeout.

Use this endpoint in Odysseus instead:

```text
Provider: Ollama
Base URL: http://192.168.0.127:11434
Model: qwen2.5-coder:7b
```

Do not use:

```text
http://192.168.0.127:11434/v1
```

Version 0.3.3 also increases local LLM timeouts:

```text
llm_default_timeout_seconds: 120
llm_stream_timeout_seconds: 600
```

On CPU-only thin-client hardware, the first token from `qwen2.5-coder:7b` can
still take a long time. If it remains unusably slow, switch Ollama Lite to:

```text
qwen2.5-coder:3b
```

## Home Assistant sidebar

Version 0.3.3 serves Home Assistant Ingress through a small wrapper on port
8099. The wrapper removes iframe-blocking headers from Odysseus and rewrites
absolute `/static` and `/api` paths so the UI can run inside the Home Assistant
sidebar. It also rewrites Odysseus's same-origin absolute API URLs, which the
frontend builds from `window.location.origin`. The direct web UI on port 7000
remains available.
