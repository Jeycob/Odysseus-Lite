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

For .NET projects, use Agent mode and ask Odysseus to run:

```bash
install-dotnet-sdk
dotnet new web -o MiniTasks
```

The helper installs .NET into persistent `/share` storage.

Odysseus Lite 0.3.6 also injects those workspace/tooling rules into the Agent
system prompt automatically, including the instruction to use
`install-dotnet-sdk --channel 9.0` instead of `apt-get install dotnet-sdk-*`.

Odysseus Lite 0.3.7 also tells the agent that Bash tool calls are stateless.
Use absolute paths or combine `cd` and the command in one call:

```bash
cd /share/odysseus-workspace/MiniTasks && dotnet run
dotnet run --project /share/odysseus-workspace/MiniTasks/MiniTasks.csproj
```

Odysseus Lite 0.3.8 additionally makes standalone `cd <dir>` Bash calls sticky
for following Bash calls, so small local models are less likely to fail when
they split navigation and execution into two tool calls.

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
