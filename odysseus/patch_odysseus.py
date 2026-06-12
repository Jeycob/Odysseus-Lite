#!/usr/bin/env python3
import sys
from pathlib import Path


ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/opt/odysseus")


def patch_file(relative_path, replacements):
    path = ROOT / relative_path
    text = path.read_text(encoding="utf-8")
    changed = False
    for old, new in replacements:
        if old not in text:
            raise SystemExit(f"Expected text not found in {relative_path}: {old!r}")
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
            "_AGENT_WORKDIR = DATA_DIR",
            '_AGENT_WORKDIR = os.getenv("ODYSSEUS_AGENT_WORKDIR", DATA_DIR)',
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
    "src/agent_tools/subprocess_tools.py",
    [
        (
            "import asyncio\n"
            "import sys\n"
            "import time\n"
            "import collections\n"
            "from typing import Optional, Callable, Awaitable, Tuple, Dict\n",
            "import asyncio\n"
            "import sys\n"
            "import time\n"
            "import collections\n"
            "import os\n"
            "import shlex\n"
            "from pathlib import Path\n"
            "from typing import Optional, Callable, Awaitable, Tuple, Dict\n",
        ),
        (
            "class BashTool:\n"
            "    async def execute(self, content: str, ctx: dict) -> dict:\n"
            "        from src.tool_execution import _AGENT_WORKDIR, _truncate\n"
            "        progress_cb = ctx.get(\"progress_cb\")\n"
            "        workspace = ctx.get(\"workspace\")\n"
            "        _subproc_env = ctx.get(\"subproc_env\")\n"
            "        proc = await asyncio.create_subprocess_shell(\n"
            "            content,\n"
            "            stdout=asyncio.subprocess.PIPE,\n"
            "            stderr=asyncio.subprocess.PIPE,\n"
            "            env=_subproc_env,\n"
            "            cwd=workspace or _AGENT_WORKDIR,\n"
            "        )\n",
            "class BashTool:\n"
            "    def __init__(self):\n"
            "        self._cwd = None\n\n"
            "    def _base_cwd(self, workspace: Optional[str], agent_workdir: str) -> str:\n"
            "        cwd = self._cwd or workspace or agent_workdir\n"
            "        if not os.path.isdir(cwd):\n"
            "            cwd = workspace or agent_workdir\n"
            "        return cwd\n\n"
            "    def _cd_only_target(self, content: str, cwd: str) -> Optional[str]:\n"
            "        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith('#')]\n"
            "        if len(lines) != 1:\n"
            "            return None\n"
            "        try:\n"
            "            parts = shlex.split(lines[0])\n"
            "        except ValueError:\n"
            "            return None\n"
            "        if not parts or parts[0] != 'cd' or len(parts) > 2:\n"
            "            return None\n"
            "        target = parts[1] if len(parts) == 2 else os.path.expanduser('~')\n"
            "        path = Path(target).expanduser()\n"
            "        if not path.is_absolute():\n"
            "            path = Path(cwd) / path\n"
            "        try:\n"
            "            resolved = path.resolve(strict=True)\n"
            "        except OSError:\n"
            "            return None\n"
            "        return str(resolved) if resolved.is_dir() else None\n\n"
            "    async def execute(self, content: str, ctx: dict) -> dict:\n"
            "        from src.tool_execution import _AGENT_WORKDIR, _truncate\n"
            "        progress_cb = ctx.get(\"progress_cb\")\n"
            "        workspace = ctx.get(\"workspace\")\n"
            "        _subproc_env = ctx.get(\"subproc_env\")\n"
            "        cwd = self._base_cwd(workspace, _AGENT_WORKDIR)\n"
            "        cd_target = self._cd_only_target(content, cwd)\n"
            "        if cd_target:\n"
            "            self._cwd = cd_target\n"
            "            return {\"output\": f\"Working directory: {cd_target}\", \"exit_code\": 0}\n"
            "        proc = await asyncio.create_subprocess_shell(\n"
            "            content,\n"
            "            stdout=asyncio.subprocess.PIPE,\n"
            "            stderr=asyncio.subprocess.PIPE,\n"
            "            env=_subproc_env,\n"
            "            cwd=cwd,\n"
            "        )\n",
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
