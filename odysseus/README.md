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

Version 0.3.19 also handles stale Home Assistant mobile/Ingress login state:
if the browser is still showing the first-run setup form but the server already
has users, Odysseus Lite switches back to the normal Sign In flow when setup is
rejected as already configured.

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

Some SDKs are better installed as user-level tools under `/share` instead of
through the OS package manager. The add-on includes this helper for .NET:

```bash
install-dotnet-sdk --channel 9.0
```

`install-dotnet-sdk` installs .NET into `/share/odysseus-tools/dotnet`, so it
survives add-on rebuilds.

Agent Bash commands run in separate shell sessions. A command such as
`cd project` in one tool call does not affect the next tool call. Ask the
agent to use absolute paths or combine the directory change with the command:

```bash
cd /share/odysseus-workspace/project && npm test
```

Version 0.3.8 also makes standalone `cd <dir>` Bash calls sticky for following
Bash calls in the same running add-on process. This helps small local models
that split navigation and execution into separate tool calls.

For project work, the Agent should create real files under
`/share/odysseus-workspace`, not detached Odysseus document/code panels.

## Small Model Agent Compatibility

Small local models can struggle with Agent mode: they may put `bash` inside a
plain code block, claim files were changed without running a tool, or repeat a
generic checklist after a command already succeeded.

Version 0.3.15 keeps those workarounds scoped to small models. They are enabled
only when the selected model name contains a parameter size at or below:

```text
small_model_max_parameters_b: 8
```

You can disable the behavior entirely with:

```text
small_model_agent_workarounds: false
```

When active, the compatibility layer is generic. It is not tied to any
language, sample app, or framework. It applies to action requests involving
project files, dependencies, builds, tests, linting, typechecking, package
managers, or source directories.

Version 0.3.16 also hard-stops the Agent loop after a successful verification
tool result for small models. If a build, test, lint, typecheck, or smoke
command exits successfully and prints a clear success signal, Odysseus Lite
adds a short completion message instead of letting the model continue into
unnecessary diagnostics.

Version 0.3.17 also stops executing any remaining tool blocks from the same
model round once that successful verification has been detected. This matters
for small models that emit a good build/test command and then append stale
diagnostics in the same response. The guard is generic: it applies to project
verification commands across stacks, not just .NET or a specific sample app.

Version 0.3.18 protects small-model tool parsing when generated documentation
examples contain nested triple-backtick fences inside a shell/python tool
block. Those inner fences are neutralized before execution, so the Agent does
not run a truncated command. It also correctly treats `use_web=false` form
values as false for API clients.

Version 0.3.19 makes that protection aware of heredocs, so README examples
inside `cat <<EOF` style shell writes do not accidentally close the outer tool
block. It also recovers a common small-model error where `write_file ... <<EOF`
is emitted as a shell command inside a `bash` block by translating it to normal
shell redirection. These are generic project-file safeguards and are not tied
to .NET, MiniTasks, or a specific framework.

Version 0.3.20 adds generic scaffold hygiene for small-model project creation
loops. When a model runs common scaffold commands such as `dotnet new`,
`npm create`, `npx create-*`, `pnpm create`, `yarn create`, `cargo new`,
`go mod init`, `django-admin startproject`, or `rails new`, Odysseus Lite also
tracks simple `cd` commands inside larger Bash blocks. If the scaffold target is
a child of `/share/odysseus-workspace`, the wrapper can prepare a clean target
directory before the scaffold runs. It refuses to auto-clean paths outside the
workspace or directories containing `.git`.

Version 0.3.21 applies that normalization to the current native Bash execution
path used by upstream Odysseus, so the Agent no longer bypasses sticky `cd` or
scaffold hygiene. It also recovers the common .NET CLI shorthand mistake
`dotnet new <template> <name-or-csproj>` by converting it to
`dotnet new <template> -n <name> --force` before execution. That recovery is
generic for .NET project scaffolding and is not tied to MiniTasks.

Version 0.3.22 adds one more small-model scaffold correction. If the model has
already changed into the intended project directory, a command that names that
same directory again, such as `dotnet new webapi -n <current-directory>`, is
rewritten to scaffold in the current directory. A redundant following
`cd <current-directory>` is skipped, and guarded cleanup is based on the
effective directory from the multi-line Bash block.

Version 0.3.23 makes the scaffold correction order-aware. Valid root-scaffold
commands such as `dotnet new webapi -n Project` are left intact when the model
has not changed into `Project` yet, while named workspace targets are still
cleaned before recreate-style scaffolds. It also normalizes Windows-style bash
paths like `.\Project.csproj` to `./Project.csproj`.

Version 0.3.24 tightens completion detection for small local models. A
successful build of a freshly scaffolded template is not enough when the model
also described source files, routes, endpoints, or implementation details that
were never written by a real tool. In that case Odysseus Lite sends the model
another action round to edit project files under the workspace and verify
again.

Version 0.3.25 adds another non-interactive shell safety pass for small local
models. Interactive editors such as `nano`, `vi`, `vim`, `emacs`, `code`, and
`notepad` are skipped with a clear warning because Agent tools cannot drive an
editor session. The model must use `write_file`, `edit_file`, or ordinary
non-interactive shell writes such as heredocs. It also normalizes common .NET
CLI mistakes generally: `dotnet new minimal-api` is mapped to the valid
minimal web template, and project commands that reference `Project.csproj` from
the parent directory are pointed at the scaffolded child project file.

Version 0.3.26 makes completion checks stricter without hardcoding any sample
project. If the user request explicitly names HTTP routes such as `GET /tasks`
or `POST /tasks`, a successful build/test command must also be consistent with
the real source files under the project workspace. This catches the common
small-model failure mode where an untouched scaffold template builds
successfully even though the requested routes were never implemented. Project
lifecycle Bash blocks also run in fail-fast mode, so a failed edit, rename, or
generated command cannot be hidden by a later successful build of unrelated
template code.

Version 0.3.27 also recovers executable shell code blocks tagged as `sh`,
`shell`, `zsh`, `dash`, or `ksh` during small-model action requests. Upstream
Odysseus normally treats those tags as display code, which means the model can
accidentally create a document containing a script instead of running the
script. Odysseus Lite only converts them to Bash when the request is clearly
asking for real project artifacts, builds, tests, or file changes.

Version 0.3.28 extends that same compatibility layer to pseudo file-tool calls
that small models put inside shell scripts. Forms like `create_file path
<<EOF`, `write_file path <<EOF`, and simple quoted `write_file path 'content'`
are translated into regular shell writes with parent directories created first.
Recovered project shell blocks also run through Bash when it is available, so
`source` and simple arrays behave as the model usually expects.

Version 0.3.29 preserves the add-on Agent environment while doing that Bash
recovery. This matters because a login shell can reset `PATH` and hide
persistent tools installed under `/share/odysseus-tools`, even though the
normal add-on shell can see them. It also normalizes common mistaken calls to
the built-in persistent .NET helper, for example:

```bash
share/odysseus-tools/install-dotnet-sdk --channel 9.0
```

to:

```bash
install-dotnet-sdk --channel 9.0
```

These are still small-model Agent workarounds only. Larger models and ordinary
chat/code examples are not rewritten unless the turn is clearly an action
request involving real project files, dependencies, builds, or tests.

When a small model still hits a .NET-specific failure, Odysseus Lite adds a
short diagnostic to the tool result. For example, `dotnet: command not found`
points back to `install-dotnet-sdk --channel 9.0`, while `Could not resolve
SDK` points the model at the `.csproj` `Project Sdk` value instead of letting
it drift into package-manager or Windows PATH instructions.

Version 0.3.30 keeps incomplete-verification state across Agent rounds. If a
template builds but requested routes, source edits, or other implementation
details are still missing from real workspace files, a follow-up summary without
tool calls is rejected. The model is sent back to executable tools and reminded
not to use Odysseus documents as project source files.

Version 0.3.31 adds a stronger generic recovery for small models that write
project source as Markdown instead of using tools. If an action request is
answered with filename headings plus language code blocks, Odysseus Lite turns
those snippets into real `write_file` calls under the requested `/share`
workspace and runs them before the next build/test/smoke command. It also
tracks `cd` into newly-created workspace directories inside a multi-line Bash
block, so named scaffold commands do not create accidental nested projects.

Version 0.3.32 adds another small-model guard that is intentionally not tied to
one language or sample app. When a small model writes or scaffolds files but
does not run a successful build/test/smoke command, Odysseus Lite rejects the
summary and asks for executable tool blocks again. It also checks for expected
project manifests for common stacks, including `.csproj`/`.sln`,
`package.json`, `go.mod`, `Cargo.toml`, `pom.xml`, and Gradle build files.
Recovered source snippets are written to disk only; redundant `create_document`
blocks are dropped so project code does not end up in inert editor documents.

Version 0.3.33 adds a failed-verification guard for the same small-model path.
If a build, test, lint, typecheck, or smoke command fails, the next Agent round
is steered back to executable tools that fix source, manifest, dependency, or
configuration files and then rerun the failed verification. Long tool outputs
are compacted before they go back into the small model context, preserving the
useful beginning and error tail without flooding the next round.

Version 0.3.34 catches a prose-only action response for small models. If the
model writes a checklist, commands, or project steps but no executable tool
block, Odysseus Lite rejects that inert round and asks for only real `bash`,
`write_file`, or `edit_file` tool blocks. The detection is based on generic
action/artifact intent and command-like guidance, not a specific framework or
project name.

It also recovers this common malformed tool block:

````text
```
bash
npm test
```
````

For action requests, Odysseus Lite treats it like the executable form:

````text
```bash
npm test
```
````

Useful prompt for small local models:

```text
Use Agent mode.
Work in /share/odysseus-workspace/<project-name>.
Create or edit real files. Do not use create_document for project files.
Install missing tools yourself, preferably under /share/odysseus-tools.
Run the relevant build/test/lint/smoke command.
Stop after verification succeeds and summarize only changed files.
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
Create the project files directly and then run a smoke test.
For Bash commands, use absolute paths or combine cd and the command in one call.
```

Version 0.3.6 injects this environment knowledge into the Agent system prompt
automatically. You should no longer need to repeat the workspace/tooling rules
in every chat. For stubborn small local models, a short direct request still helps:

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
