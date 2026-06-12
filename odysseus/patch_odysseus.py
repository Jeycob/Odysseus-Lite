#!/usr/bin/env python3
import sys
from pathlib import Path


ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/opt/odysseus")


def patch_file(relative_path, replacements):
    path = ROOT / relative_path
    text = path.read_text(encoding="utf-8")
    changed = False
    for replacement in replacements:
        if len(replacement) == 2:
            old, new = replacement
            required = True
        else:
            old, new, required = replacement
        if old not in text:
            if required:
                raise SystemExit(f"Expected text not found in {relative_path}: {old!r}")
            print(f"[Odysseus Lite] Optional patch skipped in {relative_path}: {old[:80]!r}")
            continue
        text = text.replace(old, new, 1)
        changed = True
    if changed:
        path.write_text(text, encoding="utf-8")
        print(f"[Odysseus Lite] Patched {relative_path}")


patch_file(
    "src/ai_interaction.py",
    [
        ("import json\n", "import json\nimport os\n"),
        (
            "AI_CHAT_TIMEOUT = 120  # seconds for a single LLM call",
            'AI_CHAT_TIMEOUT = int(os.getenv("ODYSSEUS_AI_CHAT_TIMEOUT", os.getenv("ODYSSEUS_LLM_STREAM_TIMEOUT", "600")))  # seconds for a single LLM call',
        ),
    ],
)

patch_file(
    "src/agent_loop.py",
    [
        (
            "import logging\n",
            "import logging\nimport os\n",
        ),
        (
            "logger = logging.getLogger(__name__)\n",
            "logger = logging.getLogger(__name__)\n\n\n"
            "def _odysseus_lite_agent_hint() -> str:\n"
            "    return os.getenv(\"ODYSSEUS_AGENT_SYSTEM_HINT\", \"\").strip()\n",
        ),
        (
            "        parts = [\n"
            "            \"You are an AI assistant with tool access.\",\n"
            "            f\"Available tools: {tool_list}.\",\n"
            "            _API_AGENT_RULES,\n"
            "        ]",
            "        parts = [\n"
            "            \"You are an AI assistant with tool access.\",\n"
            "            f\"Available tools: {tool_list}.\",\n"
            "        ]\n"
            "        _env_hint = _odysseus_lite_agent_hint()\n"
            "        if _env_hint:\n"
            "            parts.append(_env_hint)\n"
            "        parts.append(_API_AGENT_RULES)",
        ),
        (
            "    parts = [_AGENT_PREAMBLE]\n",
            "    parts = [_AGENT_PREAMBLE]\n"
            "    _env_hint = _odysseus_lite_agent_hint()\n"
            "    if _env_hint:\n"
            "        parts.append(_env_hint)\n",
        ),
    ],
)

patch_file(
    "src/agent_loop.py",
    [
        (
            "    _MAX_INTENT_NUDGES = 2\n\n"
            "    # \"I said I would, then didn't\" detector.",
            "    _MAX_INTENT_NUDGES = 2\n"
            "    _ODYSSEUS_LITE_MAX_FALSE_DONE_NUDGES = 2\n"
            "    _odysseus_lite_false_done_nudges = 0\n"
            "    _ODYSSEUS_LITE_ACTION_RE = re.compile(\n"
            "        r\"\\\\b(create|recreate|generate|scaffold|build|fix|install|write|edit|make)\\\\b\",\n"
            "        re.IGNORECASE,\n"
            "    )\n"
            "    _ODYSSEUS_LITE_CODING_RE = re.compile(\n"
            "        r\"(/share/odysseus-workspace|dotnet|asp\\\\.net|webapi|web app|program\\\\.cs|\"\n"
            "        r\"\\\\.csproj|write_file|edit_file|create_document|project files|miniTasks)\",\n"
            "        re.IGNORECASE,\n"
            "    )\n"
            "    _ODYSSEUS_LITE_FALSE_DONE_RE = re.compile(\n"
            "        r\"\\\\b(changed files|created|updated|built|build succeeded|successfully|summary)\\\\b\",\n"
            "        re.IGNORECASE,\n"
            "    )\n\n"
            "    # \"I said I would, then didn't\" detector.",
            False,
        ),
        (
            "            _intent_text = _THINK_RE.sub(\"\", cleaned_round).strip()\n"
            "            _intent_match = _INTENT_RE.search(_intent_text) if _intent_text else None\n"
            "            # Only nudge when the round REALLY looks like an unfinished\n",
            "            _intent_text = _THINK_RE.sub(\"\", cleaned_round).strip()\n"
            "            _intent_match = _INTENT_RE.search(_intent_text) if _intent_text else None\n"
            "            _odysseus_lite_original = _verifier_instruction or \"\"\n"
            "            _odysseus_lite_combined = f\"{_odysseus_lite_original}\\n{_intent_text}\"\n"
            "            _odysseus_lite_false_done = (\n"
            "                not guide_only\n"
            "                and not tool_events\n"
            "                and _intent_text\n"
            "                and _odysseus_lite_false_done_nudges < _ODYSSEUS_LITE_MAX_FALSE_DONE_NUDGES\n"
            "                and _ODYSSEUS_LITE_ACTION_RE.search(_odysseus_lite_original)\n"
            "                and _ODYSSEUS_LITE_CODING_RE.search(_odysseus_lite_combined)\n"
            "                and _ODYSSEUS_LITE_FALSE_DONE_RE.search(_intent_text)\n"
            "            )\n"
            "            if _odysseus_lite_false_done:\n"
            "                _odysseus_lite_false_done_nudges += 1\n"
            "                _workspace = os.getenv(\"ODYSSEUS_AGENT_WORKDIR\", \"/share/odysseus-workspace\")\n"
            "                logger.info(\n"
            "                    \"[odysseus-lite] false coding completion nudge #%s on round %s\",\n"
            "                    _odysseus_lite_false_done_nudges,\n"
            "                    round_num,\n"
            "                )\n"
            "                messages.append({\n"
            "                    \"role\": \"system\",\n"
            "                    \"content\": (\n"
            "                        \"Odysseus Lite detected that your previous answer claimed a coding task \"\n"
            "                        \"was created, changed, or built, but this turn has no tool execution results. \"\n"
            "                        \"That means nothing was proven on disk. Do not apologize, explain, or summarize. \"\n"
            "                        \"Your next response must contain only executable tool blocks. Use fenced blocks \"\n"
            "                        \"tagged bash, write_file, or edit_file. For an ASP.NET Core MiniTasks request, \"\n"
            "                        \"run a bash block like:\\n\"\n"
            "                        \"```bash\\n\"\n"
            "                        f\"install-dotnet-sdk --channel 9.0\\n\"\n"
            "                        f\"dotnet new webapi -o {_workspace}/MiniTasks --force\\n\"\n"
            "                        f\"dotnet build {_workspace}/MiniTasks/MiniTasks.csproj\\n\"\n"
            "                        \"```\\n\"\n"
            "                        \"Only after a successful tool result may you say which files changed.\"\n"
            "                    ),\n"
            "                })\n"
            "                yield f'data: {json.dumps({\"type\": \"agent_step\", \"round\": round_num + 1})}\\n\\n'\n"
            "                continue\n"
            "            # Only nudge when the round REALLY looks like an unfinished\n",
            False,
        ),
    ],
)

patch_file(
    "src/llm_core.py",
    [
        ("import json\n", "import json\nimport os\n"),
        (
            "    DEFAULT_TIMEOUT = 30\n",
            '    DEFAULT_TIMEOUT = int(os.getenv("ODYSSEUS_LLM_DEFAULT_TIMEOUT", "120"))\n',
        ),
        (
            "    STREAM_TIMEOUT = 300\n",
            '    STREAM_TIMEOUT = int(os.getenv("ODYSSEUS_LLM_STREAM_TIMEOUT", "600"))\n',
        ),
    ],
)

patch_file(
    "src/tool_execution.py",
    [
        (
            "import re\n",
            "import re\nimport shlex\n",
        ),
        (
            "_AGENT_WORKDIR = DATA_DIR",
            '_AGENT_WORKDIR = os.getenv("ODYSSEUS_AGENT_WORKDIR", DATA_DIR)\n'
            "_AGENT_SHELL_CWD: Optional[str] = None",
        ),
        (
            "    roots.append(DATA_DIR)\n",
            "    roots.append(_AGENT_WORKDIR)\n"
            "    if os.path.realpath(_AGENT_WORKDIR) != os.path.realpath(DATA_DIR):\n"
            "        roots.append(DATA_DIR)\n",
        ),
    ],
)

patch_file(
    "src/tool_execution.py",
    [
        (
            "_BG_MARKERS = {\"#!bg\", \"#bg\", \"# bg\", \"#background\", \"# background\", \"@background\", \"# @background\"}\n",
            "def _bash_cd_only_target(content: str, cwd: str) -> Optional[str]:\n"
            "    \"\"\"Return the target directory for a standalone `cd` command.\"\"\"\n"
            "    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith('#')]\n"
            "    if len(lines) != 1:\n"
            "        return None\n"
            "    try:\n"
            "        parts = shlex.split(lines[0])\n"
            "    except ValueError:\n"
            "        return None\n"
            "    if not parts or parts[0] != 'cd' or len(parts) > 2:\n"
            "        return None\n"
            "    target = parts[1] if len(parts) == 2 else os.path.expanduser('~')\n"
            "    path = pathlib.Path(target).expanduser()\n"
            "    if not path.is_absolute():\n"
            "        path = pathlib.Path(cwd) / path\n"
            "    try:\n"
            "        resolved = path.resolve(strict=True)\n"
            "    except OSError:\n"
            "        return None\n"
            "    return str(resolved) if resolved.is_dir() else None\n\n"
            "def _prepare_bash_content(content: str, workspace: Optional[str] = None) -> tuple[str, Optional[Dict], str]:\n"
            "    \"\"\"Make separate `cd` and later command tool calls behave like a shell.\"\"\"\n"
            "    global _AGENT_SHELL_CWD\n"
            "    base_cwd = _AGENT_SHELL_CWD or workspace or _AGENT_WORKDIR\n"
            "    if not os.path.isdir(base_cwd):\n"
            "        base_cwd = workspace or _AGENT_WORKDIR\n"
            "    cd_target = _bash_cd_only_target(content, base_cwd)\n"
            "    if cd_target:\n"
            "        _AGENT_SHELL_CWD = cd_target\n"
            "        return content, {\"output\": f\"Working directory: {cd_target}\", \"exit_code\": 0}, cd_target\n"
            "    if _AGENT_SHELL_CWD and os.path.isdir(_AGENT_SHELL_CWD):\n"
            "        return f\"cd {shlex.quote(_AGENT_SHELL_CWD)} &&\\n{content}\", None, _AGENT_SHELL_CWD\n"
            "    return content, None, base_cwd\n\n"
            "_BG_MARKERS = {\"#!bg\", \"#bg\", \"# bg\", \"#background\", \"# background\", \"@background\", \"# @background\"}\n",
        ),
        (
            "    mcp = get_mcp_manager()\n"
            "    if not mcp:\n"
            "        return await _direct_fallback(tool, content, progress_cb=progress_cb) or {\"error\": f\"MCP manager not available for tool '{tool}'\", \"exit_code\": 1}\n\n"
            "    server_id, tool_name = _MCP_TOOL_MAP[tool]\n",
            "    mcp = get_mcp_manager()\n"
            "    if not mcp:\n"
            "        return await _direct_fallback(tool, content, progress_cb=progress_cb) or {\"error\": f\"MCP manager not available for tool '{tool}'\", \"exit_code\": 1}\n\n"
            "    if tool == \"bash\":\n"
            "        content, cd_result, _cwd = _prepare_bash_content(content)\n"
            "        if cd_result:\n"
            "            return cd_result\n\n"
            "    server_id, tool_name = _MCP_TOOL_MAP[tool]\n",
            False,
        ),
        (
            "    try:\n"
            "        ctx = {\n",
            "    try:\n"
            "        if tool == \"bash\":\n"
            "            content, cd_result, workspace = _prepare_bash_content(content, workspace)\n"
            "            if cd_result:\n"
            "                return cd_result\n"
            "        ctx = {\n",
            False,
        ),
    ],
)

patch_file(
    "routes/shell_routes.py",
    [
        (
            "            cwd=str(Path.home()),\n",
            '            cwd=os.environ.get("ODYSSEUS_AGENT_WORKDIR") or str(Path.home()),\n',
        ),
        (
            "        cwd=str(Path.home()),\n",
            '        cwd=os.environ.get("ODYSSEUS_AGENT_WORKDIR") or str(Path.home()),\n',
        ),
        (
            "                    cwd=str(Path.home()),\n",
            '                    cwd=os.environ.get("ODYSSEUS_AGENT_WORKDIR") or str(Path.home()),\n',
        ),
    ],
)

patch_file(
    "static/login.html",
    [
        (
            "  // Check auth status\n"
            "  try {\n"
            "    const res = await fetch('/api/auth/status', { credentials: 'same-origin' });\n"
            "    const data = await res.json();\n"
            "    if (data.authenticated) {\n"
            "      window.location.replace('/');\n"
            "      return;\n"
            "    }\n"
            "    signupAllowed = !!data.signup_enabled;\n"
            "    if (!data.configured) {\n"
            "      setMode('setup');\n"
            "    } else {\n"
            "      setMode('login');\n"
            "    }\n"
            "  } catch (e) {\n"
            "    setMode('login');\n"
            "  }\n",
            "  // Check auth status. Be conservative: only show first-run setup when\n"
            "  // the backend explicitly says configured === false. Mobile WebViews\n"
            "  // and Home Assistant Ingress can serve stale pages or cached responses;\n"
            "  // an uncertain status must fall back to normal login, never setup.\n"
            "  try {\n"
            "    const statusUrl = '/api/auth/status?_=' + Date.now();\n"
            "    const res = await fetch(statusUrl, {\n"
            "      credentials: 'same-origin',\n"
            "      cache: 'no-store',\n"
            "      headers: { 'Accept': 'application/json' }\n"
            "    });\n"
            "    if (!res.ok) throw new Error('status failed');\n"
            "    const data = await res.json();\n"
            "    if (!data || typeof data.configured !== 'boolean') throw new Error('bad status');\n"
            "    if (data.authenticated) {\n"
            "      window.location.replace('/');\n"
            "      return;\n"
            "    }\n"
            "    signupAllowed = !!data.signup_enabled;\n"
            "    if (data.configured === false) {\n"
            "      setMode('setup');\n"
            "    } else {\n"
            "      setMode('login');\n"
            "    }\n"
            "  } catch (e) {\n"
            "    setMode('login');\n"
            "  }\n",
        ),
    ],
)

patch_file(
    "app.py",
    [
        (
            "@app.get(\"/login\")\n"
            "async def serve_login(request: Request):\n"
            "    if not AUTH_ENABLED:\n"
            "        return RedirectResponse(url=\"/\", status_code=302)\n"
            "    return _serve_html_with_nonce(request, abs_join(BASE_DIR, \"static/login.html\"))\n",
            "@app.get(\"/login\")\n"
            "async def serve_login(request: Request):\n"
            "    if not AUTH_ENABLED:\n"
            "        return RedirectResponse(url=\"/\", status_code=302)\n"
            "    response = _serve_html_with_nonce(request, abs_join(BASE_DIR, \"static/login.html\"))\n"
            "    response.headers[\"Cache-Control\"] = \"no-store, max-age=0\"\n"
            "    return response\n",
            False,
        ),
    ],
)

patch_file(
    "static/js/admin.js",
    [
        (
            "    // Ensure /v1 suffix for bare host:port URLs (not cloud providers)\n"
            "    if (!u.includes('api.') && !u.includes('openrouter') && !u.includes('opencode.ai') && !u.includes('ollama.com') && !u.endsWith('/v1')) {\n"
            "      try {\n"
            "        const parsed = new URL(u);\n"
            "        if (!parsed.pathname || parsed.pathname === '/') {\n"
            "          u += '/v1';\n"
            "        }\n"
            "      } catch(e) {}\n"
            "    }",
            "    // Ensure /v1 suffix for bare OpenAI-compatible host:port URLs.\n"
            "    // Local Ollama on 11434 is better handled through native /api/chat,\n"
            "    // so keep http://host:11434 as-is instead of forcing /v1.\n"
            "    if (!u.includes('api.') && !u.includes('openrouter') && !u.includes('opencode.ai') && !u.includes('ollama.com') && !u.endsWith('/v1')) {\n"
            "      try {\n"
            "        const parsed = new URL(u);\n"
            "        const isOllamaPort = parsed.port === '11434';\n"
            "        if (!isOllamaPort && (!parsed.pathname || parsed.pathname === '/')) {\n"
            "          u += '/v1';\n"
            "        }\n"
            "      } catch(e) {}\n"
            "    }",
        ),
        (
            "    return 'http://127.0.0.1:11434/v1';",
            "    return 'http://' + window.location.hostname + ':11434';",
        ),
    ],
)
