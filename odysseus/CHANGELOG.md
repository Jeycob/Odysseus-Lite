# Changelog

## 0.3.32

- Tighten small-model Agent completion checks after recovered source writes.
  If a small model writes or scaffolds real project files but does not run a
  successful build/test/smoke command, Odysseus Lite keeps the loop going
  instead of accepting a prose summary.
- Detect missing project manifests generically for common stacks, including
  `.csproj`/`.sln`, `package.json`, `go.mod`, `Cargo.toml`, `pom.xml`, and
  Gradle build files. This prevents a model from treating loose source files as
  a complete buildable project.
- Drop redundant `create_document` blocks when the small-model recovery has
  already converted filename/code-fence snippets into real `write_file` calls.
  Project source stays on disk under the persistent workspace instead of being
  mirrored into inert editor documents.

## 0.3.31

- Recover another small-model Agent failure mode generically: when a model
  answers an action request with filename headings plus language code fences
  instead of real file tools, Odysseus Lite converts those declared source
  snippets into `write_file` tool calls under the requested `/share` workspace.
  The recovered writes are inserted before build/test/smoke commands, so
  verification checks real project files rather than an untouched scaffold.
- Fix scaffold normalization when a multi-line Bash block creates a workspace
  directory and then immediately `cd`s into it. The compatibility layer now
  tracks that future in-workspace directory before it exists on disk, preventing
  nested duplicate projects such as `Project/Project`.
- Keep both changes scoped to small-model action/artifact turns. Normal code
  examples and larger-model Agent runs are not rewritten by this recovery.

## 0.3.30

- Keep incomplete-verification state across Agent rounds for small models. If a
  build succeeds but requested routes/source changes are still missing from real
  workspace files, a following prose-only summary is rejected and the model is
  forced back to executable tools.
- Apply the false-completion guard even after earlier tool events in the same
  task. This catches the pattern where a small model scaffolds and builds a
  template, stores the requested source in an Odysseus document, then claims the
  project files were edited.

## 0.3.29

- Preserve the add-on Agent environment when recovered small-model shell blocks
  are executed with Bash. Version 0.3.28 used a login shell, which could reset
  `PATH` and hide persistent user tools such as `/share/odysseus-tools/dotnet`.
- Normalize common mistaken invocations of the persistent .NET helper, such as
  `share/odysseus-tools/install-dotnet-sdk --channel 9.0`, back to the
  executable `install-dotnet-sdk --channel 9.0` form.
- Add targeted failure hints for small-model .NET Agent loops so a missing
  `dotnet` command points back to the persistent helper, and invalid `.csproj`
  SDK metadata points the model toward editing the project file instead of
  reinstalling packages or trying Windows paths.
- Keep both changes scoped to the small-model Agent compatibility layer and
  project/dependency execution paths.

## 0.3.28

- Expand small-model Bash recovery for project-generation loops. Pseudo file
  tool commands such as `create_file path <<EOF`, `write_file path <<EOF`, and
  simple quoted `write_file path 'content'` are translated into ordinary shell
  writes with parent directory creation.
- Run recovered project Bash blocks through Bash when available, so common Bash
  syntax such as `source` and array iteration does not fail under `/bin/sh`.
- Recover simple Python-style shell assignments and unique missing `.csproj`
  paths under the persistent workspace. These fixes are generic small-model
  compatibility behavior, not tied to a specific sample project.

## 0.3.27

- Recover another small-model Agent formatting mistake generically: executable
  shell fences tagged as `sh`, `shell`, `zsh`, `dash`, or `ksh` are treated as
  Bash in action requests when upstream would otherwise save them as inert code
  documents. This keeps project-generation scripts executable without making
  the workaround specific to .NET, MiniTasks, or any one framework.
- Keep the recovery scoped to small models and action/artifact requests. Normal
  code examples and large documentation snippets still remain documents.

## 0.3.26

- Make small-model verification stricter after successful build/test commands.
  When the user explicitly requests HTTP routes such as `GET /tasks` or
  `POST /tasks`, Odysseus Lite checks the real project source files before
  marking the task complete. A build of an untouched scaffold template is no
  longer enough.
- Run project lifecycle Bash blocks in fail-fast mode when they scaffold,
  build, test, lint, or typecheck. This prevents an earlier failed edit,
  rename, or generated command from being hidden by a later successful build of
  unrelated template code.
- Recover `edit_file ... <<EOF` inside Bash blocks the same way as
  `write_file ... <<EOF`, while still documenting that proper separate
  `write_file`/`edit_file` tool blocks are preferred.

## 0.3.25

- Add another small-model command normalization pass for non-interactive Agent
  shells. Interactive editors such as `nano`, `vi`, `vim`, `emacs`, `code`,
  and `notepad` are skipped with a clear warning so the model must use real
  file writes or file tools instead of pretending an editor session happened.
- Normalize common .NET scaffold wording by mapping `dotnet new minimal-api`
  style aliases to the valid `dotnet new web` template before execution.
- When a small model scaffolds a .NET project and then runs a project command
  against `Project.csproj` from the parent directory, rewrite that project path
  to the actual scaffolded child project path. This is a generic .NET CLI path
  recovery, not tied to MiniTasks.

## 0.3.24

- Prevent small-model Agent runs from stopping after a successful build of a
  freshly scaffolded template when the same response described source files,
  routes, endpoints, or implementation details that were never actually written
  by a tool.
- Add a follow-up nudge for scaffold-only verification: the model must edit real
  project files in the persistent workspace and rerun verification before
  Odysseus Lite marks the task complete.

## 0.3.23

- Fix the 0.3.22 scaffold normalization so it tracks `cd` commands in order
  instead of looking at a later directory change. This preserves the valid
  pattern `dotnet new <template> -n <project>` from a workspace root while
  still correcting nested scaffolds after the model has already changed into
  the target directory.
- Clean the intended `dotnet new -n/--name/-o/--output` target directory under
  the persistent workspace before recreate-style scaffolds.
- Normalize Windows-style bash path fragments like `.\Project.csproj` to
  `./Project.csproj` before execution.

## 0.3.22

- Normalize another small-model scaffold loop: when a model has already moved
  into the requested project directory, commands such as
  `dotnet new webapi -n <current-directory>` are converted to scaffold in the
  current directory instead of creating a nested duplicate project. A following
  redundant `cd <current-directory>` is skipped.
- Apply guarded cleanup using the effective shell directory from a multi-line
  Bash block, so recreate requests clean the intended workspace child directory
  before the scaffold runs.

## 0.3.21

- Apply the small-model bash normalization layer to the direct native bash
  execution path as well as older MCP-style paths. This makes sticky `cd`,
  guarded scaffold cleanup, and command rewriting effective in current upstream
  Odysseus builds.
- Recover the common invalid .NET scaffold shorthand
  `dotnet new <template> <name-or-csproj>` by translating it to a valid
  `dotnet new <template> -n <name> --force` command before execution.
  This is a generic .NET CLI compatibility fix for project scaffolding, not a
  MiniTasks-specific shortcut.

## 0.3.20

- Make Agent bash execution more deterministic for small local models by
  remembering simple `cd` commands that appear inside larger shell blocks, not
  only standalone `cd` tool calls.
- Add a generic guarded scaffold hygiene layer for project creation commands
  such as `dotnet new`, `npm create`, `cargo new`, and similar tools. When a
  small model scaffolds a project under the persistent workspace, Odysseus Lite
  can prepare a clean target directory while refusing to auto-clean directories
  outside the workspace or directories containing `.git`.
- Document the recreate-project behavior generally, without tying it to .NET,
  MiniTasks, or a specific framework.

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
