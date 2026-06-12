# Odysseus Lite Add-ons

Home Assistant add-on repository for Odysseus Lite.

## Add Repository

In Home Assistant, open Settings > Add-ons > Add-on Store, then add this
repository URL:

```text
https://github.com/Jeycob/Odysseus-Lite
```

Install `Odysseus Lite` from the add-on store.

## Agent Workspace

Odysseus Lite 0.3.5 gives the admin agent a persistent workspace:

```text
/share/odysseus-workspace
```

Files created there survive add-on restarts and are visible from Home Assistant
Samba/Studio Code Server under `share/odysseus-workspace`.

Runtime-installed user tools live under:

```text
/share/odysseus-tools
```

Odysseus Lite injects those workspace/tooling rules into the Agent system
prompt automatically. Project files should be created under
`/share/odysseus-workspace`; durable runtime-installed tools should go under
`/share/odysseus-tools`.

Odysseus Lite 0.3.7 also tells the agent that Bash tool calls are stateless.
Use absolute paths or combine `cd` and the command in one call:

```bash
cd /share/odysseus-workspace/project && npm test
```

Odysseus Lite 0.3.8 additionally makes standalone `cd <dir>` Bash calls sticky
for following Bash calls, so small local models are less likely to fail when
they split navigation and execution into two tool calls.

Odysseus Lite 0.3.9 keeps that fix compatible with older cached upstream
Odysseus source layouts used by Home Assistant Docker builds.

Odysseus Lite 0.3.10 makes that compatibility patch tolerant of minor
`tool_execution.py` differences in cached Home Assistant Docker builds.

Odysseus Lite 0.3.11 makes the login page safer in Home Assistant mobile
Ingress: stale or uncertain auth status falls back to Sign In instead of
incorrectly showing first-time setup.

Odysseus Lite 0.3.15 keeps general Agent environment rules separate from
small-model compatibility rules. Extra recovery for malformed tool fences and
false "created/built/changed" completions applies only when the selected model
name looks like a small local model, with the threshold controlled by the
`small_model_max_parameters_b` add-on option.

Odysseus Lite 0.3.16 also stops small-model Agent loops after a successful
build/test/lint/typecheck/smoke tool result, so the model does not continue
into unnecessary diagnostics after the output already proves success.

Odysseus Lite 0.3.17 tightens that behavior further: if a small model emits
several tool blocks in one round, Odysseus stops executing the remaining blocks
immediately after the first successful verification command. This is generic
for project work and is not tied to .NET or any particular sample app.

Odysseus Lite 0.3.18 hardens small-model tool parsing when a shell/python tool
block contains markdown examples for generated docs. Nested triple-backtick
examples are neutralized before parsing so the executable block is not cut
short. It also fixes `use_web=false` form handling for API clients.

Odysseus Lite 0.3.19 makes that parser heredoc-aware and recovers a second
common small-model mistake: `write_file ... <<EOF` accidentally emitted inside
a bash block is treated as normal shell redirection. The login page also
recovers from stale first-run setup state by switching back to Sign In when the
server says auth is already configured.

Odysseus Lite 0.3.20 adds generic scaffold hygiene for small-model project
creation loops. For common scaffold commands such as `dotnet new`,
`npm create`, or `cargo new`, the agent wrapper keeps `cd` state from larger
bash blocks and can prepare a clean target directory under
`/share/odysseus-workspace`. It refuses to auto-clean paths outside the
workspace or directories containing `.git`.

Odysseus Lite 0.3.21 applies that normalization to the current native bash
execution path used by upstream Odysseus and recovers a common .NET CLI
shorthand mistake, `dotnet new <template> <name-or-csproj>`, by converting it
to a valid named project scaffold command.

Odysseus Lite 0.3.22 fixes another small-model scaffold pattern: if the model
has already `cd`'d into the requested project directory, a named scaffold such
as `dotnet new webapi -n <same-name>` is normalized to create files in the
current directory instead of nesting a duplicate project. The cleanup guard now
uses the effective directory from multi-line bash blocks, not only the initial
shell directory.

Odysseus Lite 0.3.23 makes that normalization order-aware, so valid
root-scaffold commands such as `dotnet new webapi -n Project` are preserved
when the following `cd Project` has not happened yet. It also cleans named
workspace scaffold targets and normalizes Windows-style bash paths like
`.\Project.csproj` to `./Project.csproj`.

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
