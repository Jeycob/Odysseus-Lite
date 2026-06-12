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
