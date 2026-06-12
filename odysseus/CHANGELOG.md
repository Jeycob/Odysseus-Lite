# Changelog

## 0.3.19

- Make small-model tool parsing heredoc-aware. Markdown examples inside a
  shell heredoc no longer close the surrounding `bash` tool block early.
- Recover another common small-model mistake by translating `write_file ... <<`
  lines that appear inside a `bash` tool block into normal shell redirection.
  This is generic for generated project files and documentation; it is not
  tied to .NET, MiniTasks, or any specific framework.
- Harden first-login handling further: if a stale/mobile setup screen tries to
  create an admin account after auth is already configured, the page switches
  back to Sign In instead of staying stuck in first-run setup.

## 0.3.18

- For small-model Agent runs, protect tool parsing from nested markdown fences
  inside shell/python tool blocks. README examples such as `echo "```bash"`
  no longer truncate the executable block and produce half-run shell commands.
- Coerce `use_web=false` form values correctly so API clients and tests do not
  accidentally trigger web search context.
- Add a small-model prompt guard to prefer heredoc/printf/tildes for README
  examples inside shell tools. This is a generic tool-parsing safety fix, not
  tied to .NET, MiniTasks, or any one project template.

## 0.3.17

- Stop executing any remaining tool blocks in the same small-model Agent round
  after the first successful verification command. This prevents a weak model
  from running stale follow-up diagnostics such as `sudo dotnet build` after a
  previous `dotnet build`, `npm test`, lint, typecheck, or smoke check already
  proved success.
- Document that this completion guard is generic for build/test/lint/typecheck
  and smoke checks, not tied to .NET or a specific sample project.

## 0.3.16

- Stop small-model Agent loops after a successful verification tool result.
  If a build/test/lint/typecheck/smoke command exits with success and prints a
  clear success signal such as `Build succeeded`, `0 Error(s)`, or tests
  passed, Odysseus Lite now ends the task instead of letting the model continue
  into unnecessary diagnostics.
- Add explicit small-model guidance not to reinstall tools, retry with `sudo`,
  or keep troubleshooting after verification succeeded.

## 0.3.15

- Harden first-login behavior in Home Assistant Ingress/mobile WebViews:
  `/login` starts in a disabled status-checking state, `/api/auth/status` is
  served with no-cache headers, and the client verifies that the login cookie is
  visible before redirecting.
- Split Odysseus Lite Agent guidance into general environment rules and
  small-model compatibility rules.
- Apply malformed tool-fence recovery and false-completion nudges only when the
  selected model name looks like a small local model. The threshold is
  configurable with `small_model_max_parameters_b`.
- Generalize small-model guidance for any language/framework/project, not just
  .NET or a specific sample app.

## 0.3.14

- Recover a common small-model tool formatting mistake where the model writes
  an untagged code fence whose first line is `bash`, `write_file`, or another
  tool name. Odysseus Lite now converts that into a real executable tool block
  for action requests.
- Make the Agent prompt stricter about putting `bash` in the code-fence tag,
  not as the first line inside a generic code block.

## 0.3.13

- Add a false-completion guard for action requests: if a small local model
  claims files were created or verification passed without any tool execution,
  Odysseus nudges it to run real `bash`/file tools instead of accepting the
  answer.
- Add exact fenced tool-call syntax to the Odysseus Lite Agent prompt.
- Tell the Agent not to claim "Changed files", "Created", or "Built" unless
  the current turn contains a successful tool result.

## 0.3.12

- Tighten the Agent system prompt for small local models in Agent mode.
- Tell the Agent to write real project files with file tools instead of
  creating detached code/document panels.
- Tell the Agent to match the requested language, framework, and project type
  instead of falling back to an unrelated template.
- Tell the Agent to stop after a successful build or smoke test instead of
  repeating troubleshooting steps.

## 0.3.11

- Make the login page conservative about first-run setup: show setup only when
  `/api/auth/status` explicitly returns `configured: false`.
- Fetch auth status with `cache: no-store` and a cache buster to avoid stale
  Home Assistant mobile WebView/Ingress state.
- Serve `/login` with `Cache-Control: no-store` when the upstream layout
  supports that patch.

## 0.3.10

- Make the sticky Bash working-directory patch tolerate upstream
  `tool_execution.py` differences so Home Assistant cached builds do not fail
  on an optional `_call_mcp_tool` anchor.

## 0.3.9

- Move sticky Bash working-directory handling into `src/tool_execution.py` so
  the add-on builds against both old and new Odysseus upstream layouts.

## 0.3.8

- Make the native Bash agent tool remember a successful standalone `cd <dir>`
  command and run later Bash commands from that directory.
- This makes small local models more forgiving when they split `cd project`
  and a later build/run command into separate tool calls.

## 0.3.7

- Tell the agent that Bash tool calls are stateless and `cd` does not persist
  between separate tool executions.
- Teach the agent to use absolute project paths or combine `cd ... && command`
  in a single Bash tool call.
- Document that project commands should use explicit paths when the toolchain
  supports them.

## 0.3.6

- Inject an Odysseus Lite environment guide into every Agent system prompt.
- Teach the agent to use `/share/odysseus-workspace` for projects and
  `/share/odysseus-tools` for persistent user tools.
- Teach the agent to use `install-dotnet-sdk --channel 9.0` instead of Debian
  or Microsoft `apt` packages for .NET.
- Tell the agent to act with tools for app/file creation requests instead of
  returning installation tutorials.
- Include recovery guidance for malformed `dotnet.list` apt source files.

## 0.3.5

- Add a persistent Home Assistant `/share/odysseus-workspace` agent workspace.
- Point agent shell, Python, and file tools at the workspace through
  `ODYSSEUS_AGENT_WORKDIR`.
- Add `/share/odysseus-tools` to the agent PATH for runtime-installed tools.
- Add an `install-dotnet-sdk` helper that installs .NET into persistent
  `/share` storage.
- Add an optional trusted workspace bootstrap script for replaying setup after
  add-on updates.
- Include common development/debug tools such as `ripgrep`, `jq`, `zip`,
  `unzip`, `python3-venv`, `sudo`, .NET runtime dependencies, and network
  diagnostics.

## 0.3.4

- Auto-configure a shared Ollama Lite endpoint from add-on options.
- Seed the configured Ollama model into Odysseus so the model picker has a
  server-side model entry immediately.
- Keep local Ollama URLs on port 11434 native instead of forcing `/v1`.
- Move the Home Assistant Ingress bootstrap to the start of `<head>` so API URL
  rewriting is active before Odysseus scripts run.
- Document model picker troubleshooting inside Home Assistant Ingress.

## 0.3.3

- Make Odysseus LLM timeouts configurable from add-on options.
- Patch upstream Odysseus to read local LLM timeout values from environment
  variables.
- Increase default local stream timeout to 600 seconds for slow CPU-only Ollama
  models.
- Document the recommended native Ollama endpoint and blank-reply
  troubleshooting.

## 0.3.2

- Validate `/data/odysseus/auth.json` on every start.
- Create an initial admin account when `auth.json` is missing, invalid, or has
  no users.
- Preserve and normalize legacy single-user auth files.
- Add `reset_admin_password_on_start` for explicit admin password recovery.
- Document first login, reset flow, and local-vs-GitHub add-on data separation.

## 0.3.1

- Fix Odysseus API calls inside Home Assistant Ingress by rewriting same-origin
  absolute URLs such as `http://homeassistant.local/api/sessions` to the
  Ingress base path.
- Stop rewriting normal JSON API responses in the proxy.

## 0.3.0

- Route Home Assistant Ingress through a local wrapper on port 8099.
- Strip iframe-blocking security headers only for Ingress traffic.
- Rewrite absolute Odysseus asset/API paths to the Home Assistant Ingress base
  path.

## 0.2.0

- Add Home Assistant Ingress support.
- Add Odysseus to the Home Assistant sidebar.
- Keep the direct web UI available on port 7000.

## 0.1.0

- Initial experimental single-container Odysseus add-on.
