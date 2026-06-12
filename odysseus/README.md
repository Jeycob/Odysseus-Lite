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
  native Ollama. Version 0.3.4 can create this endpoint automatically when
  `auto_configure_ollama` is enabled:

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

## Agent Development Workspace

Version 0.3.5 turns Odysseus Lite into a more practical development sandbox for
admin users.

Agent tools default to:

```text
/share/odysseus-workspace
```

That path is Home Assistant `/share` storage. Files created there survive add-on
restarts and updates, and are visible from Samba/Studio Code Server as:

```text
share/odysseus-workspace
```

Runtime-installed user tools should go under:

```text
/share/odysseus-tools
```

The add-on adds these paths to the agent environment:

```text
/share/odysseus-workspace/.local/bin
/share/odysseus-tools/bin
/share/odysseus-tools/dotnet
```

The container includes `apt-get`, build tools, Git, Node.js/npm, Python venv,
`ripgrep`, `jq`, `zip`, `unzip`, `tmux`, and common network diagnostics. An
admin agent can still install additional system packages with `apt-get`, but
packages installed into the container layer can disappear after an add-on
rebuild/update. Keep projects and user tools in `/share`.

For .NET development, ask the agent to run:

```bash
install-dotnet-sdk
dotnet --info
dotnet new web -o MiniTasks
```

`install-dotnet-sdk` installs .NET into `/share/odysseus-tools/dotnet`, so it
survives add-on rebuilds.

Agent Bash commands run in separate shell sessions. A command such as
`cd MiniTasks` in one tool call does not affect the next tool call. Ask the
agent to use absolute paths or combine the directory change with the command:

```bash
cd /share/odysseus-workspace/MiniTasks && dotnet run
dotnet run --project /share/odysseus-workspace/MiniTasks/MiniTasks.csproj
```

Version 0.3.8 also makes standalone `cd <dir>` Bash calls sticky for following
Bash calls in the same running add-on process. This helps small local models
that split `cd MiniTasks` and `dotnet run` into separate tool calls.

For coding tasks, the Agent should create real source files under
`/share/odysseus-workspace`, not detached Odysseus document/code panels. Version
0.3.12 adds that rule to the automatic Agent prompt and also tells the Agent to
stop once a build or smoke test succeeds. This matters most for small local
models such as 3B/7B coders, which can otherwise keep repeating the same
troubleshooting checklist after the tool output already shows success.

For an ASP.NET Core web app, prefer a prompt like:

```text
Create an ASP.NET Core minimal API named MiniTasks.
Use write_file/edit_file for project files. Do not use create_document.
Use dotnet new web or webapi, not console.
Create it in /share/odysseus-workspace/MiniTasks.
Run dotnet build /share/odysseus-workspace/MiniTasks/MiniTasks.csproj.
Stop after the build succeeds and summarize only the changed files.
```

For setup that should replay on every add-on start, create:

```text
/share/odysseus-workspace/bootstrap.sh
```

then enable `run_workspace_bootstrap` in the add-on Configuration tab. Only put
commands there that you trust, because it runs as part of the add-on startup.

Useful Agent prompt:

```text
You are inside the Odysseus Lite Home Assistant add-on.
Use Agent mode. Do not give instructions unless blocked.
Work in /share/odysseus-workspace.
Install missing tools yourself. Prefer persistent installs under /share/odysseus-tools.
If .NET is missing, run install-dotnet-sdk.
Create the project files directly and then run a smoke test.
For Bash commands, use absolute paths or combine cd and the command in one call.
```

Version 0.3.6 injects this environment knowledge into the Agent system prompt
automatically. You should no longer need to repeat the workspace/tooling rules
in every chat. For stubborn small local models, a short direct request still
helps:

```text
Create the app now in /share/odysseus-workspace and verify it builds.
```

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

## Home Assistant Ingress Model Picker

The Home Assistant sidebar runs Odysseus under an Ingress path, not at `/`.
Version 0.3.4 hardens URL rewriting so model and endpoint requests such as
`/api/models` and `/api/model-endpoints` always go to Odysseus, not to Home
Assistant's own `/api`.

It also avoids a common Ollama setup trap: the Add Models UI previously turned
`http://host:11434` into `http://host:11434/v1`. That uses Ollama's
OpenAI-compatible surface. For local Ollama, keep the native URL without `/v1`.

If the model picker still says "No models connected" after an update:

1. Restart Odysseus Lite.
2. Refresh the browser tab.
3. In the add-on log, look for:

   ```text
   [Odysseus Lite] Added Ollama endpoint
   ```

4. If needed, open Settings > Admin > Endpoints and remove the old `/v1`
   Ollama endpoint.

## Home Assistant sidebar

Version 0.3.4 serves Home Assistant Ingress through a small wrapper on port
8099. The wrapper removes iframe-blocking headers from Odysseus and rewrites
absolute `/static` and `/api` paths so the UI can run inside the Home Assistant
sidebar. It also rewrites Odysseus's same-origin absolute API URLs, which the
frontend builds from `window.location.origin`. The direct web UI on port 7000
remains available.

## Smoke Testing

This repository includes a dependency-free smoke test script for a running
Odysseus Lite instance. Run it from the repository root:

```bash
ODYSSEUS_USERNAME=admin \
ODYSSEUS_PASSWORD='your-password' \
python3 tools/odysseus_smoke.py --base-url http://192.168.0.127:7000
```

The default test logs in and checks the main HTML pages plus read-only API
endpoints for auth, sessions, models, notes, tasks, gallery, documents,
research, calendar, email, preferences, and diagnostics.

To also verify Ollama directly:

```bash
ODYSSEUS_USERNAME=admin \
ODYSSEUS_PASSWORD='your-password' \
OLLAMA_BASE_URL=http://192.168.0.127:11434 \
python3 tools/odysseus_smoke.py --base-url http://192.168.0.127:7000
```

To run a real end-to-end chat check, add `--chat`. This creates a temporary
Odysseus chat session and sends a short prompt to the selected model:

```bash
ODYSSEUS_USERNAME=admin \
ODYSSEUS_PASSWORD='your-password' \
OLLAMA_BASE_URL=http://192.168.0.127:11434 \
python3 tools/odysseus_smoke.py \
  --base-url http://192.168.0.127:7000 \
  --chat \
  --chat-model qwen2.5-coder:3b
```
