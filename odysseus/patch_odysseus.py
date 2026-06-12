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
            "        # Execute each tool block\n"
            "        tool_results = []\n"
            "        tool_result_texts = []  # plain text for native tool role messages\n"
            "        budget_hit = False\n",
            "        # Execute each tool block\n"
            "        tool_results = []\n"
            "        tool_result_texts = []  # plain text for native tool role messages\n"
            "        budget_hit = False\n"
            "        _odysseus_lite_round_had_scaffold = False\n"
            "        _odysseus_lite_round_had_source_edit = False\n"
            "        _odysseus_lite_scaffold_only_verification = False\n",
            False,
        ),
        (
            "            if is_doc_tool:\n"
            "                cmd_display = block.content.split(\"\\n\")[0].strip()[:80]\n"
            "            else:\n"
            "                cmd_display = block.content.strip()\n\n"
            "            if tool_policy and tool_policy.blocks(block.tool_type):\n",
            "            if is_doc_tool:\n"
            "                cmd_display = block.content.split(\"\\n\")[0].strip()[:80]\n"
            "            else:\n"
            "                cmd_display = block.content.strip()\n\n"
            "            if _odysseus_lite_action_recovery_enabled(model):\n"
            "                _block_content = block.content or \"\"\n"
            "                if block.tool_type == \"bash\" and _ODYSSEUS_LITE_SCAFFOLD_COMMAND_RE.search(_block_content):\n"
            "                    _odysseus_lite_round_had_scaffold = True\n"
            "                if block.tool_type in {\"write_file\", \"edit_file\", \"update_document\", \"edit_document\"}:\n"
            "                    _odysseus_lite_round_had_source_edit = True\n"
            "                elif block.tool_type == \"bash\" and _ODYSSEUS_LITE_SOURCE_EDIT_COMMAND_RE.search(_block_content):\n"
            "                    _odysseus_lite_round_had_source_edit = True\n\n"
            "            if tool_policy and tool_policy.blocks(block.tool_type):\n",
            False,
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
            "    if plan_mode and not guide_only:\n"
            "        # Steer the model to investigate-then-propose. Hard tool gating handles\n",
            "    _odysseus_lite_small_hint = _odysseus_lite_small_model_hint(model)\n"
            "    if _odysseus_lite_small_hint and not plan_mode and not guide_only:\n"
            "        if messages and messages[0].get(\"role\") == \"system\":\n"
            "            messages[0][\"content\"] = (messages[0].get(\"content\") or \"\") + \"\\n\\n\" + _odysseus_lite_small_hint\n"
            "        else:\n"
            "            messages.insert(0, {\"role\": \"system\", \"content\": _odysseus_lite_small_hint})\n\n"
            "    if plan_mode and not guide_only:\n"
            "        # Steer the model to investigate-then-propose. Hard tool gating handles\n",
            False,
        ),
    ],
)

patch_file(
    "src/agent_loop.py",
    [
        (
            "def _odysseus_lite_agent_hint() -> str:\n"
            "    return os.getenv(\"ODYSSEUS_AGENT_SYSTEM_HINT\", \"\").strip()\n",
            "def _odysseus_lite_agent_hint() -> str:\n"
            "    return os.getenv(\"ODYSSEUS_AGENT_SYSTEM_HINT\", \"\").strip()\n\n\n"
            "def _odysseus_lite_bool_env(name: str, default: bool = False) -> bool:\n"
            "    value = os.getenv(name)\n"
            "    if value is None:\n"
            "        return default\n"
            "    return value.strip().lower() in {\"1\", \"true\", \"yes\", \"on\"}\n\n\n"
            "def _odysseus_lite_model_size_b(model: str) -> Optional[float]:\n"
            "    text = (model or \"\").lower()\n"
            "    match = re.search(r\"(?:^|[-_:/.])([0-9]+(?:\\.[0-9]+)?)\\s*b(?:$|[-_:/ .])\", text)\n"
            "    if not match:\n"
            "        return None\n"
            "    try:\n"
            "        return float(match.group(1))\n"
            "    except (TypeError, ValueError):\n"
            "        return None\n\n\n"
            "def _odysseus_lite_is_small_model(model: str) -> bool:\n"
            "    if not _odysseus_lite_bool_env(\"ODYSSEUS_SMALL_MODEL_AGENT_WORKAROUNDS\", True):\n"
            "        return False\n"
            "    size_b = _odysseus_lite_model_size_b(model)\n"
            "    if size_b is None:\n"
            "        return False\n"
            "    try:\n"
            "        max_b = float(os.getenv(\"ODYSSEUS_SMALL_MODEL_MAX_PARAMETERS_B\", \"8\"))\n"
            "    except (TypeError, ValueError):\n"
            "        max_b = 8.0\n"
            "    return size_b <= max(max_b, 1.0)\n\n\n"
            "def _odysseus_lite_small_model_hint(model: str) -> str:\n"
            "    if not _odysseus_lite_is_small_model(model):\n"
            "        return \"\"\n"
            "    return os.getenv(\"ODYSSEUS_SMALL_MODEL_AGENT_HINT\", \"\").strip()\n\n\n"
            "def _odysseus_lite_action_recovery_enabled(model: str) -> bool:\n"
            "    return _odysseus_lite_is_small_model(model)\n\n\n"
            "def _odysseus_lite_successful_verification(tool_type: str, command: str, result: Dict) -> str:\n"
            "    if tool_type not in {\"bash\", \"python\"}:\n"
            "        return \"\"\n"
            "    try:\n"
            "        exit_code = int(result.get(\"exit_code\", 1))\n"
            "    except (TypeError, ValueError):\n"
            "        return \"\"\n"
            "    if exit_code != 0:\n"
            "        return \"\"\n"
            "    cmd = command or \"\"\n"
            "    verify_re = re.compile(\n"
            "        r\"\\b(\"\n"
            "        r\"dotnet\\s+(?:build|test)|\"\n"
            "        r\"npm\\s+(?:test|run\\s+(?:build|test|lint|typecheck))|\"\n"
            "        r\"pnpm\\s+(?:test|run\\s+(?:build|test|lint|typecheck))|\"\n"
            "        r\"yarn\\s+(?:test|build|lint|typecheck)|\"\n"
            "        r\"pytest|python\\s+-m\\s+pytest|\"\n"
            "        r\"cargo\\s+(?:build|test|check)|go\\s+(?:build|test)|\"\n"
            "        r\"mvn\\s+test|gradle\\s+test|make\\s+(?:build|test|check)|\"\n"
            "        r\"ruff\\s+check|eslint|tsc\\b|curl\\b|wget\\b\"\n"
            "        r\")\\b\",\n"
            "        re.IGNORECASE,\n"
            "    )\n"
            "    if not verify_re.search(cmd):\n"
            "        return \"\"\n"
            "    out = \"\\n\".join(\n"
            "        str(result.get(k, \"\"))\n"
            "        for k in (\"output\", \"stdout\", \"stderr\", \"results\", \"content\")\n"
            "        if result.get(k) is not None\n"
            "    )\n"
            "    combined = f\"{cmd}\\n{out}\"\n"
            "    success_re = re.compile(\n"
            "        r\"(build\\s+succeeded|build\\s+successful|successfully\\s+built|compiled\\s+successfully|\"\n"
            "        r\"0\\s+error\\(s\\)|0\\s+errors?\\b|tests?\\s+passed|all\\s+tests?\\s+passed|\"\n"
            "        r\"tests?:\\s*\\d+\\s+passed|test\\s+suites?:\\s*\\d+\\s+passed|\"\n"
            "        r\"test\\s+result:\\s+ok|=+\\s*\\d+\\s+passed|\\bpassed\\s+in\\s+\\d|\"\n"
            "        r\"http/\\S+\\s+200\\b|\\b200\\s+ok\\b|finished\\s+.*\\s+target)\",\n"
            "        re.IGNORECASE,\n"
            "    )\n"
            "    if not success_re.search(combined):\n"
            "        return \"\"\n"
            "    for line in cmd.splitlines():\n"
            "        line = line.strip()\n"
            "        if line and not line.startswith(\"#\") and verify_re.search(line):\n"
            "            return line[:160]\n"
            "    return \"verification command\"\n\n\n"
            "def _odysseus_lite_recover_prefixed_tool_blocks(text: str, disabled_tools: Optional[set] = None) -> List[ToolBlock]:\n"
            "    \"\"\"Recover untagged fences whose first line is a tool name.\n\n"
            "    Small local models often emit ```\\nbash\\n...``` instead of\n"
            "    ```bash\\n...```. Upstream treats that as ordinary markdown, so\n"
            "    nothing executes. Odysseus Lite recovers this only for small-model\n"
            "    action turns at the call site.\n"
            "    \"\"\"\n"
            "    disabled_tools = disabled_tools or set()\n"
            "    executable = {\"bash\", \"python\", \"write_file\", \"read_file\", \"edit_file\"}\n"
            "    blocks: List[ToolBlock] = []\n"
            "    for match in re.finditer(r\"```([^`\\n]*)\\n([\\s\\S]*?)```\", text or \"\"):\n"
            "        lang = (match.group(1) or \"\").strip().lower()\n"
            "        if lang in TOOL_TAGS:\n"
            "            continue\n"
            "        lines = match.group(2).splitlines()\n"
            "        while lines and not lines[0].strip():\n"
            "            lines.pop(0)\n"
            "        if not lines:\n"
            "            continue\n"
            "        tool = lines[0].strip().strip(\"`\").lower()\n"
            "        if tool not in executable or tool in disabled_tools:\n"
            "            continue\n"
            "        content = \"\\n\".join(lines[1:]).strip(\"\\n\")\n"
            "        if not content.strip():\n"
            "            continue\n"
            "        blocks.append(ToolBlock(tool, content))\n"
            "    return blocks\n",
            False,
        ),
        (
            "def _odysseus_lite_recover_prefixed_tool_blocks(text: str, disabled_tools: Optional[set] = None) -> List[ToolBlock]:\n",
            "def _odysseus_lite_escape_nested_tool_fences(text: str) -> str:\n"
            "    \"\"\"Keep markdown examples inside tool blocks from ending the tool early.\n\n"
            "    Small models often write README examples like echo \"```bash\" inside a\n"
            "    ```bash tool block. The stock non-greedy fenced-block regex then stops\n"
            "    at that inner fence and executes a truncated shell script. Treat only\n"
            "    a standalone fence outside heredocs as the real close marker and\n"
            "    neutralize inner triple-backtick sequences to markdown-compatible\n"
            "    tildes.\n"
            "    \"\"\"\n"
            "    if not text or \"```\" not in text:\n"
            "        return text or \"\"\n"
            "    tags = \"|\".join(sorted(re.escape(t) for t in TOOL_TAGS))\n"
            "    opener = re.compile(r\"```(\" + tags + r\")\\s*\\n\", re.IGNORECASE)\n"
            "    heredoc_re = re.compile(r\"<<-?\\s*['\\\"]?([A-Za-z_][A-Za-z0-9_]*)['\\\"]?\")\n"
            "    out = []\n"
            "    pos = 0\n"
            "    while True:\n"
            "        match = opener.search(text, pos)\n"
            "        if not match:\n"
            "            out.append(text[pos:])\n"
            "            break\n"
            "        out.append(text[pos:match.end()])\n"
            "        body_start = match.end()\n"
            "        remainder = text[body_start:]\n"
            "        offset = 0\n"
            "        heredoc_end = None\n"
            "        body_parts = []\n"
            "        close_line = \"\"\n"
            "        found_close = False\n"
            "        while offset < len(remainder):\n"
            "            line_end = remainder.find(\"\\n\", offset)\n"
            "            if line_end == -1:\n"
            "                line = remainder[offset:]\n"
            "                next_offset = len(remainder)\n"
            "            else:\n"
            "                line = remainder[offset:line_end + 1]\n"
            "                next_offset = line_end + 1\n"
            "            stripped = line.strip()\n"
            "            if heredoc_end:\n"
            "                body_parts.append(line.replace(\"```\", \"~~~\"))\n"
            "                if stripped == heredoc_end:\n"
            "                    heredoc_end = None\n"
            "            elif stripped == \"```\":\n"
            "                close_line = line\n"
            "                found_close = True\n"
            "                offset = next_offset\n"
            "                break\n"
            "            else:\n"
            "                heredoc = heredoc_re.search(line)\n"
            "                if heredoc:\n"
            "                    heredoc_end = heredoc.group(1)\n"
            "                body_parts.append(line.replace(\"```\", \"~~~\"))\n"
            "            offset = next_offset\n"
            "        out.append(\"\".join(body_parts))\n"
            "        if not found_close:\n"
            "            break\n"
            "        out.append(close_line)\n"
            "        pos = body_start + offset\n"
            "    return \"\".join(out)\n\n\n"
            "def _odysseus_lite_recover_prefixed_tool_blocks(text: str, disabled_tools: Optional[set] = None) -> List[ToolBlock]:\n",
            False,
        ),
        (
            "        tool_blocks, used_native = _resolve_tool_blocks(round_response, native_tool_calls, round_num, is_api_model=_is_api_model)\n\n"
            "        # Force-answer round: we told the model to STOP calling tools and\n",
            "        _parse_response = round_response\n"
            "        if not _force_answer and _odysseus_lite_action_recovery_enabled(model):\n"
            "            _parse_response = _odysseus_lite_escape_nested_tool_fences(round_response)\n"
            "        tool_blocks, used_native = _resolve_tool_blocks(_parse_response, native_tool_calls, round_num, is_api_model=_is_api_model)\n"
            "        if not tool_blocks and not _force_answer and _odysseus_lite_action_recovery_enabled(model):\n"
            "            _odysseus_lite_original = _verifier_instruction or \"\"\n"
            "            _odysseus_lite_combined = f\"{_odysseus_lite_original}\\n{_parse_response}\"\n"
            "            if (_ODYSSEUS_LITE_ACTION_RE.search(_odysseus_lite_original)\n"
            "                    and _ODYSSEUS_LITE_ARTIFACT_RE.search(_odysseus_lite_combined)):\n"
            "                _recovered_blocks = _odysseus_lite_recover_prefixed_tool_blocks(_parse_response, disabled_tools)\n"
            "                if _recovered_blocks:\n"
            "                    logger.info(\n"
            "                        \"[odysseus-lite] recovered %s prefixed fenced tool block(s)\",\n"
            "                        len(_recovered_blocks),\n"
            "                    )\n"
            "                    tool_blocks.extend(_recovered_blocks)\n"
            "                    used_native = False\n\n"
            "        # Force-answer round: we told the model to STOP calling tools and\n",
            False,
        ),
    ],
)

patch_file(
    "routes/chat_routes.py",
    [
        (
            "        use_web = form_data.get(\"use_web\")\n",
            "        use_web = str(form_data.get(\"use_web\", \"\")).lower() == \"true\"\n",
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
            "    _odysseus_lite_completed_verification = \"\"\n"
            "    _odysseus_lite_stop_after_tool = False\n"
            "    _ODYSSEUS_LITE_ACTION_RE = re.compile(\n"
            "        r\"\\b(create|recreate|generate|scaffold|build|fix|install|write|edit|make|implement|add|update|modify|run|test|lint|typecheck)\\b\",\n"
            "        re.IGNORECASE,\n"
            "    )\n"
            "    _ODYSSEUS_LITE_ARTIFACT_RE = re.compile(\n"
            "        r\"(/share/|workspace|project|app|api|web|server|source|file|files|directory|folder|\"\n"
            "        r\"package|dependency|dependencies|build|test|lint|typecheck|npm|node|python|pip|\"\n"
            "        r\"dotnet|go|cargo|rust|java|maven|gradle|dockerfile|compose|\"\n"
            "        r\"package\\.json|requirements\\.txt|pyproject\\.toml|\\.csproj|\\.sln)\",\n"
            "        re.IGNORECASE,\n"
            "    )\n"
            "    _ODYSSEUS_LITE_FALSE_DONE_RE = re.compile(\n"
            "        r\"\\b(changed files?|created|updated|modified|wrote|built|build succeeded|tests? passed|installed|generated|implemented|fixed|summary)\\b\",\n"
            "        re.IGNORECASE,\n"
            "    )\n\n"
            "    _ODYSSEUS_LITE_SCAFFOLD_COMMAND_RE = re.compile(\n"
            "        r\"(?m)^\\s*(dotnet\\s+new|npm\\s+(?:create|init)|npx\\s+(?:create-|create\\s)|\"\n"
            "        r\"pnpm\\s+create|yarn\\s+create|cargo\\s+new|django-admin\\s+startproject|rails\\s+new)\\b\",\n"
            "        re.IGNORECASE,\n"
            "    )\n"
            "    _ODYSSEUS_LITE_SOURCE_EDIT_COMMAND_RE = re.compile(\n"
            "        r\"(?m)^\\s*(cat\\s+>|tee\\s+|sed\\s+-i|perl\\s+-p?i|python3?\\s+.*(?:write_text|open\\(.+['\\\"]w)|\"\n"
            "        r\"node\\s+-e\\s+.*writeFile|printf\\s+.*>\\s*|echo\\s+.*>\\s*)\",\n"
            "        re.IGNORECASE,\n"
            "    )\n"
            "    _ODYSSEUS_LITE_DECLARED_SOURCE_EDIT_RE = re.compile(\n"
            "        r\"(create|write|add|edit|update|modify|implement).{0,120}\"\n"
            "        r\"(file|source|route|endpoint|controller|handler|component|program\\.cs|package\\.json)|```(?:csharp|cs|typescript|javascript|python|json|html|css)\",\n"
            "        re.IGNORECASE | re.DOTALL,\n"
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
            "                and _odysseus_lite_action_recovery_enabled(model)\n"
            "                and not tool_events\n"
            "                and _intent_text\n"
            "                and _odysseus_lite_false_done_nudges < _ODYSSEUS_LITE_MAX_FALSE_DONE_NUDGES\n"
            "                and _ODYSSEUS_LITE_ACTION_RE.search(_odysseus_lite_original)\n"
            "                and _ODYSSEUS_LITE_ARTIFACT_RE.search(_odysseus_lite_combined)\n"
            "                and _ODYSSEUS_LITE_FALSE_DONE_RE.search(_intent_text)\n"
            "            )\n"
            "            if _odysseus_lite_false_done:\n"
            "                _odysseus_lite_false_done_nudges += 1\n"
            "                _workspace = os.getenv(\"ODYSSEUS_AGENT_WORKDIR\", \"/share/odysseus-workspace\")\n"
            "                logger.info(\n"
            "                    \"[odysseus-lite] false action completion nudge #%s on round %s\",\n"
            "                    _odysseus_lite_false_done_nudges,\n"
            "                    round_num,\n"
            "                )\n"
            "                messages.append({\n"
            "                    \"role\": \"system\",\n"
            "                    \"content\": (\n"
            "                        \"Odysseus Lite detected that your previous answer claimed an action request \"\n"
            "                        \"was created, changed, or built, but this turn has no tool execution results. \"\n"
            "                        \"That means nothing was proven on disk. Do not apologize, explain, or summarize. \"\n"
            "                        \"Your next response must contain only executable tool blocks. Use fenced blocks \"\n"
            "                        \"tagged bash, write_file, or edit_file. Run the actual commands requested by the user, \"\n"
            "                        \"using the persistent workspace when creating project files. For example:\\n\"\n"
            "                        \"```bash\\n\"\n"
            "                        f\"cd {_workspace}\\n\"\n"
            "                        \"# run the scaffold/build/test commands for the requested stack here\\n\"\n"
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
    "src/agent_loop.py",
    [
        (
            "            if block.tool_type in _VERIFIER_EFFECTFUL_TOOLS:\n"
            "                _effectful_used = True\n\n"
            "            formatted = format_tool_result(desc, result)\n",
            "            if block.tool_type in _VERIFIER_EFFECTFUL_TOOLS:\n"
            "                _effectful_used = True\n"
            "            if _odysseus_lite_action_recovery_enabled(model):\n"
            "                _success_label = _odysseus_lite_successful_verification(block.tool_type, block.content, result)\n"
            "                if _success_label:\n"
            "                    _scaffold_only = (\n"
            "                        _odysseus_lite_round_had_scaffold\n"
            "                        and not _odysseus_lite_round_had_source_edit\n"
            "                        and _ODYSSEUS_LITE_DECLARED_SOURCE_EDIT_RE.search(round_response or \"\")\n"
            "                    )\n"
            "                    if _scaffold_only:\n"
            "                        _odysseus_lite_scaffold_only_verification = True\n"
            "                        logger.info(\n"
            "                            \"[odysseus-lite] deferring scaffold-only verification after %s\",\n"
            "                            _success_label,\n"
            "                        )\n"
            "                    else:\n"
            "                        _odysseus_lite_completed_verification = _success_label\n"
            "                        _odysseus_lite_stop_after_tool = True\n\n"
            "            formatted = format_tool_result(desc, result)\n",
        ),
        (
            "            tool_results.append(formatted)\n"
            "            tool_result_texts.append(formatted)\n",
            "            tool_results.append(formatted)\n"
            "            tool_result_texts.append(formatted)\n"
            "            if _odysseus_lite_stop_after_tool:\n"
            "                logger.info(\n"
            "                    \"[odysseus-lite] skipping remaining tool blocks after successful verification: %s\",\n"
            "                    _odysseus_lite_completed_verification,\n"
            "                )\n"
            "                break\n",
        ),
        (
            "        # Feed results back to LLM for next round\n"
            "        _append_tool_results(messages, round_response, native_tool_calls,\n",
            "        if _odysseus_lite_scaffold_only_verification:\n"
            "            _workspace = os.getenv(\"ODYSSEUS_AGENT_WORKDIR\", \"/share/odysseus-workspace\")\n"
            "            messages.append({\n"
            "                \"role\": \"system\",\n"
            "                \"content\": (\n"
            "                    \"Odysseus Lite detected that the last successful build only proved a freshly scaffolded template. \"\n"
            "                    \"Your previous response described source files, routes, endpoints, or implementation details, \"\n"
            "                    \"but no real file-write/edit tool ran for those source changes. Continue with executable tools only. \"\n"
            "                    \"Edit real project files under the persistent workspace, then run the verification command again. \"\n"
            "                    f\"Workspace: {_workspace}.\"\n"
            "                ),\n"
            "            })\n\n"
            "        if _odysseus_lite_completed_verification:\n"
            "            logger.info(\n"
            "                \"[odysseus-lite] stopping small-model loop after successful verification: %s\",\n"
            "                _odysseus_lite_completed_verification,\n"
            "            )\n"
            "            _done = f\"\\n\\nDone. Verification passed: `{_odysseus_lite_completed_verification}`.\"\n"
            "            yield f'data: {json.dumps({\"delta\": _done})}\\n\\n'\n"
            "            full_response += _done\n"
            "            break\n\n"
            "        # Feed results back to LLM for next round\n"
            "        _append_tool_results(messages, round_response, native_tool_calls,\n",
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
            "def _translate_bash_pseudo_tools(content: str) -> str:\n"
            "    \"\"\"Recover common pseudo tool calls that small models put in Bash.\"\"\"\n"
            "    if not content:\n"
            "        return content\n"
            "    content = re.sub(r\"(?m)^([ \\t]*)write_file\\s+(.+?)\\s+<<\", r\"\\1cat > \\2 <<\", content)\n"
            "    return content\n\n"
            "def _prepare_bash_content(content: str, workspace: Optional[str] = None) -> tuple[str, Optional[Dict], str]:\n"
            "    \"\"\"Make separate `cd` and later command tool calls behave like a shell.\"\"\"\n"
            "    global _AGENT_SHELL_CWD\n"
            "    content = _translate_bash_pseudo_tools(content)\n"
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
    "src/tool_execution.py",
    [
        (
            '''def _bash_cd_only_target(content: str, cwd: str) -> Optional[str]:
    """Return the target directory for a standalone `cd` command."""
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith('#')]
    if len(lines) != 1:
        return None
    try:
        parts = shlex.split(lines[0])
    except ValueError:
        return None
    if not parts or parts[0] != 'cd' or len(parts) > 2:
        return None
    target = parts[1] if len(parts) == 2 else os.path.expanduser('~')
    path = pathlib.Path(target).expanduser()
    if not path.is_absolute():
        path = pathlib.Path(cwd) / path
    try:
        resolved = path.resolve(strict=True)
    except OSError:
        return None
    return str(resolved) if resolved.is_dir() else None

def _translate_bash_pseudo_tools(content: str) -> str:
    """Recover common pseudo tool calls that small models put in Bash."""
    if not content:
        return content
    content = re.sub(r"(?m)^([ \\t]*)write_file\\s+(.+?)\\s+<<", r"\\1cat > \\2 <<", content)
    return content

def _prepare_bash_content(content: str, workspace: Optional[str] = None) -> tuple[str, Optional[Dict], str]:
    """Make separate `cd` and later command tool calls behave like a shell."""
    global _AGENT_SHELL_CWD
    content = _translate_bash_pseudo_tools(content)
    base_cwd = _AGENT_SHELL_CWD or workspace or _AGENT_WORKDIR
    if not os.path.isdir(base_cwd):
        base_cwd = workspace or _AGENT_WORKDIR
    cd_target = _bash_cd_only_target(content, base_cwd)
    if cd_target:
        _AGENT_SHELL_CWD = cd_target
        return content, {"output": f"Working directory: {cd_target}", "exit_code": 0}, cd_target
    if _AGENT_SHELL_CWD and os.path.isdir(_AGENT_SHELL_CWD):
        return f"cd {shlex.quote(_AGENT_SHELL_CWD)} &&\\n{content}", None, _AGENT_SHELL_CWD
    return content, None, base_cwd

''',
            '''def _odysseus_lite_realpath(path: str) -> str:
    try:
        return os.path.realpath(path)
    except OSError:
        return path


def _odysseus_lite_path_under(path: str, root: str) -> bool:
    try:
        return os.path.commonpath([_odysseus_lite_realpath(path), _odysseus_lite_realpath(root)]) == _odysseus_lite_realpath(root)
    except ValueError:
        return False


def _odysseus_lite_resolve_path(raw_path: str, cwd: str) -> str:
    path = pathlib.Path(os.path.expanduser(str(raw_path).strip()))
    if not path.is_absolute():
        path = pathlib.Path(cwd) / path
    return str(path.resolve(strict=False))


def _bash_cd_only_target(content: str, cwd: str) -> Optional[str]:
    """Return the target directory for a standalone `cd` command."""
    lines = [line.strip() for line in content.splitlines() if line.strip() and not line.strip().startswith('#')]
    if len(lines) != 1:
        return None
    try:
        parts = shlex.split(lines[0])
    except ValueError:
        return None
    if not parts or parts[0] != 'cd' or len(parts) > 2:
        return None
    target = parts[1] if len(parts) == 2 else os.path.expanduser('~')
    resolved = _odysseus_lite_resolve_path(target, cwd)
    return resolved if os.path.isdir(resolved) else None


def _odysseus_lite_last_cd_target(content: str, cwd: str) -> Optional[str]:
    """Track the last simple cd in a multi-command bash block."""
    current = cwd
    last = None
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            parts = shlex.split(line)
        except ValueError:
            continue
        if not parts or parts[0] != "cd" or len(parts) > 2:
            continue
        target = parts[1] if len(parts) == 2 else os.path.expanduser("~")
        resolved = _odysseus_lite_resolve_path(target, current)
        if os.path.isdir(resolved):
            current = resolved
            last = resolved
    return last


def _odysseus_lite_scaffold_command(content: str) -> bool:
    return bool(re.search(
        r"(?m)^\\s*(dotnet\\s+new|npm\\s+(?:create|init)|npx\\s+(?:create-|create\\s)|"
        r"pnpm\\s+create|yarn\\s+create|cargo\\s+new|go\\s+mod\\s+init|"
        r"django-admin\\s+startproject|rails\\s+new|create-react-app\\b)",
        content or "",
        re.IGNORECASE,
    ))


def _odysseus_lite_safe_recreate_shell(target: str) -> str:
    q_target = shlex.quote(target)
    q_workspace = shlex.quote(_AGENT_WORKDIR)
    return (
        f"_odysseus_target={q_target}\\n"
        f"_odysseus_workspace={q_workspace}\\n"
        '_odysseus_target_real=$(realpath -m "$_odysseus_target")\\n'
        '_odysseus_workspace_real=$(realpath -m "$_odysseus_workspace")\\n'
        'case "$_odysseus_target_real" in "$_odysseus_workspace_real"/*)\\n'
        '  if [ -e "$_odysseus_target/.git" ]; then\\n'
        '    echo "[Odysseus Lite] refusing to auto-clean git workspace: $_odysseus_target" >&2\\n'
        '  elif [ -d "$_odysseus_target" ]; then\\n'
        '    find "$_odysseus_target" -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +\\n'
        '  fi\\n'
        '  mkdir -p "$_odysseus_target"\\n'
        '  ;;\\n'
        '*)\\n'
        '  echo "[Odysseus Lite] refusing to scaffold outside workspace: $_odysseus_target" >&2\\n'
        '  exit 1\\n'
        '  ;;\\n'
        'esac'
    )


def _odysseus_lite_dotnet_scaffold_target(parts: list[str], cwd: str) -> Optional[str]:
    if len(parts) < 3 or parts[0] != "dotnet" or parts[1] != "new":
        return None
    idx = 3
    while idx < len(parts):
        part = parts[idx]
        if part in ("-o", "--output", "-n", "--name") and idx + 1 < len(parts):
            return _odysseus_lite_resolve_path(parts[idx + 1], cwd)
        if part.startswith("--output=") or part.startswith("--name="):
            return _odysseus_lite_resolve_path(part.split("=", 1)[1], cwd)
        idx += 1
    return None


def _odysseus_lite_prepare_scaffold_content(content: str, cwd: str) -> str:
    """Make small-model scaffold commands deterministic in the workspace.

    This is intentionally generic: it only acts on common project scaffold
    commands and only for targets below the configured persistent workspace.
    It protects user repositories by refusing to auto-clean directories that
    contain a .git folder.
    """
    if not _odysseus_lite_scaffold_command(content):
        return content
    lines = content.splitlines()
    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            parts = shlex.split(line)
        except ValueError:
            continue
        if not parts or parts[0] != "mkdir":
            continue
        targets = [part for part in parts[1:] if not part.startswith("-")]
        if not targets:
            continue
        target = _odysseus_lite_resolve_path(targets[-1], cwd)
        if not _odysseus_lite_path_under(target, _AGENT_WORKDIR):
            continue
        if _odysseus_lite_realpath(target) == _odysseus_lite_realpath(_AGENT_WORKDIR):
            continue
        lines[idx] = _odysseus_lite_safe_recreate_shell(target)
        return "\\n".join(lines)

    current_cwd = cwd
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            parts = shlex.split(line)
        except ValueError:
            continue
        if parts and parts[0] == "cd" and len(parts) <= 2:
            cd_target = parts[1] if len(parts) == 2 else os.path.expanduser("~")
            resolved = _odysseus_lite_resolve_path(cd_target, current_cwd)
            if os.path.isdir(resolved):
                current_cwd = resolved
            continue
        target = _odysseus_lite_dotnet_scaffold_target(parts, current_cwd)
        if not target:
            continue
        if not _odysseus_lite_path_under(target, _AGENT_WORKDIR):
            continue
        if _odysseus_lite_realpath(target) == _odysseus_lite_realpath(_AGENT_WORKDIR):
            continue
        return _odysseus_lite_safe_recreate_shell(target) + "\\n" + content

    if "--force" in content:
        current = _odysseus_lite_realpath(cwd)
        workspace = _odysseus_lite_realpath(_AGENT_WORKDIR)
        if current != workspace and _odysseus_lite_path_under(current, workspace):
            return _odysseus_lite_safe_recreate_shell(current) + "\\n" + content
    return content


def _translate_bash_pseudo_tools(content: str) -> str:
    """Recover common pseudo tool calls that small models put in Bash."""
    if not content:
        return content
    content = re.sub(r"(?m)^([ \\t]*)write_file\\s+(.+?)\\s+<<", r"\\1cat > \\2 <<", content)
    return content


def _prepare_bash_content(content: str, workspace: Optional[str] = None) -> tuple[str, Optional[Dict], str]:
    """Make separate `cd` and later command tool calls behave like a shell."""
    global _AGENT_SHELL_CWD
    content = _translate_bash_pseudo_tools(content)
    base_cwd = _AGENT_SHELL_CWD or workspace or _AGENT_WORKDIR
    if not os.path.isdir(base_cwd):
        base_cwd = workspace or _AGENT_WORKDIR
    cd_target = _bash_cd_only_target(content, base_cwd)
    if cd_target:
        _AGENT_SHELL_CWD = cd_target
        return content, {"output": f"Working directory: {cd_target}", "exit_code": 0}, cd_target
    content = _odysseus_lite_prepare_scaffold_content(content, base_cwd)
    last_cd = _odysseus_lite_last_cd_target(content, base_cwd)
    if last_cd:
        _AGENT_SHELL_CWD = last_cd
    run_cwd = _AGENT_SHELL_CWD if _AGENT_SHELL_CWD and os.path.isdir(_AGENT_SHELL_CWD) else base_cwd
    if run_cwd and os.path.isdir(run_cwd):
        return f"cd {shlex.quote(run_cwd)} &&\\n{content}", None, run_cwd
    return content, None, base_cwd

''',
        ),
    ],
)

patch_file(
    "src/tool_execution.py",
    [
        (
            '''def _translate_bash_pseudo_tools(content: str) -> str:
    """Recover common pseudo tool calls that small models put in Bash."""
    if not content:
        return content
    content = re.sub(r"(?m)^([ \\t]*)write_file\\s+(.+?)\\s+<<", r"\\1cat > \\2 <<", content)
    return content

''',
            '''def _translate_bash_pseudo_tools(content: str) -> str:
    """Recover common pseudo tool calls that small models put in Bash."""
    if not content:
        return content
    content = re.sub(r"(?m)^([ \\t]*)write_file\\s+(.+?)\\s+<<", r"\\1cat > \\2 <<", content)
    content = re.sub(r"(?m)(^|[ \\t])\\.\\\\(?=[^ \\t\\r\\n;&|]+)", r"\\1./", content)

    fixed_lines = []
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            fixed_lines.append(raw_line)
            continue
        try:
            parts = shlex.split(stripped)
        except ValueError:
            fixed_lines.append(raw_line)
            continue
        # Small models often write `dotnet new webapi MyApp` or
        # `dotnet new webapi MyApp.csproj`. The .NET CLI treats that trailing
        # token as an invalid option. Interpret it as the project name.
        if (
            len(parts) >= 4
            and parts[0] == "dotnet"
            and parts[1] == "new"
            and not parts[3].startswith("-")
        ):
            name = pathlib.Path(parts[3]).name
            if name.endswith(".csproj"):
                name = name[:-7]
            if name:
                rest = parts[4:]
                if "--force" not in rest:
                    rest = [*rest, "--force"]
                indent = raw_line[: len(raw_line) - len(raw_line.lstrip())]
                fixed = ["dotnet", "new", parts[2], "-n", name, *rest]
                fixed_lines.append(indent + " ".join(shlex.quote(p) for p in fixed))
                continue
        fixed_lines.append(raw_line)
    return "\\n".join(fixed_lines)

''',
            False,
        ),
        (
            '''    try:
        if tool == "bash":
            proc = await asyncio.create_subprocess_shell(
                content,
''',
            '''    try:
        if tool == "bash":
            content, cd_result, workspace = _prepare_bash_content(content, workspace)
            if cd_result:
                return cd_result
            proc = await asyncio.create_subprocess_shell(
                content,
''',
            False,
        ),
    ],
)

patch_file(
    "src/tool_execution.py",
    [
        (
            '''def _prepare_bash_content(content: str, workspace: Optional[str] = None) -> tuple[str, Optional[Dict], str]:
    """Make separate `cd` and later command tool calls behave like a shell."""
''',
            '''def _odysseus_lite_normalize_current_dir_scaffold(content: str, cwd: str) -> str:
    """Avoid nested projects when a model already cd'd into the target dir."""
    if not content or not cwd:
        return content
    fixed_lines = []
    nested_names = set()
    current_cwd = cwd
    changed = False
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        indent = raw_line[: len(raw_line) - len(raw_line.lstrip())]
        if not stripped or stripped.startswith("#"):
            fixed_lines.append(raw_line)
            continue
        try:
            parts = shlex.split(stripped)
        except ValueError:
            fixed_lines.append(raw_line)
            continue

        if nested_names and len(parts) == 2 and parts[0] == "cd":
            cd_path = pathlib.Path(parts[1])
            if not cd_path.is_absolute() and cd_path.name in nested_names:
                fixed_lines.append(indent + ": # Odysseus Lite: already in current scaffold directory")
                changed = True
                continue

        if parts and parts[0] == "cd" and len(parts) <= 2:
            cd_target = parts[1] if len(parts) == 2 else os.path.expanduser("~")
            resolved = _odysseus_lite_resolve_path(cd_target, current_cwd)
            if os.path.isdir(resolved):
                current_cwd = resolved
            fixed_lines.append(raw_line)
            continue

        if len(parts) >= 3 and parts[0] == "dotnet" and parts[1] == "new":
            new_parts = parts[:3]
            removed_name = None
            current_name = pathlib.Path(current_cwd).name
            i = 3
            while i < len(parts):
                part = parts[i]
                if part in ("-n", "--name", "-o", "--output") and i + 1 < len(parts):
                    value = parts[i + 1]
                    if current_name and pathlib.Path(value).name == current_name:
                        removed_name = current_name
                        i += 2
                        continue
                    new_parts.extend([part, value])
                    i += 2
                    continue
                if part.startswith("--name=") or part.startswith("--output="):
                    value = part.split("=", 1)[1]
                    if current_name and pathlib.Path(value).name == current_name:
                        removed_name = current_name
                        i += 1
                        continue
                new_parts.append(part)
                i += 1
            if removed_name:
                if "--force" not in new_parts:
                    new_parts.append("--force")
                fixed_lines.append(indent + " ".join(shlex.quote(p) for p in new_parts))
                nested_names.add(removed_name)
                changed = True
                continue

        fixed_lines.append(raw_line)

    return "\\n".join(fixed_lines) if changed else content


def _prepare_bash_content(content: str, workspace: Optional[str] = None) -> tuple[str, Optional[Dict], str]:
    """Make separate `cd` and later command tool calls behave like a shell."""
''',
            False,
        ),
        (
            '''    content = _odysseus_lite_prepare_scaffold_content(content, base_cwd)
    last_cd = _odysseus_lite_last_cd_target(content, base_cwd)
''',
            '''    content = _odysseus_lite_normalize_current_dir_scaffold(content, base_cwd)
    content = _odysseus_lite_prepare_scaffold_content(content, base_cwd)
    last_cd = _odysseus_lite_last_cd_target(content, base_cwd)
''',
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
            "  let mode = 'login'; // 'login' | 'signup' | 'setup'\n"
            "  let signupAllowed = false;\n\n"
            "  const rememberToggle = document.getElementById('rememberToggle');\n",
            "  let mode = 'login'; // 'login' | 'signup' | 'setup'\n"
            "  let signupAllowed = false;\n"
            "  let bootingAuth = true;\n\n"
            "  const rememberToggle = document.getElementById('rememberToggle');\n\n"
            "  function setFormDisabled(disabled) {\n"
            "    form.querySelectorAll('input, button').forEach((el) => { el.disabled = !!disabled; });\n"
            "  }\n\n"
            "  function sleep(ms) { return new Promise((resolve) => setTimeout(resolve, ms)); }\n\n"
            "  function noStoreUrl(path) {\n"
            "    const sep = path.includes('?') ? '&' : '?';\n"
            "    return path + sep + '_=' + Date.now();\n"
            "  }\n\n"
            "  async function fetchJsonNoStore(path, options = {}) {\n"
            "    const headers = { 'Accept': 'application/json', ...(options.headers || {}) };\n"
            "    const res = await fetch(noStoreUrl(path), {\n"
            "      ...options,\n"
            "      credentials: 'same-origin',\n"
            "      cache: 'no-store',\n"
            "      headers,\n"
            "    });\n"
            "    const data = await res.json().catch(() => ({}));\n"
            "    if (!res.ok) throw new Error(data.detail || data.error || 'Request failed');\n"
            "    return data;\n"
            "  }\n\n"
            "  async function waitForAuthenticatedSession(attempts = 5) {\n"
            "    for (let i = 0; i < attempts; i++) {\n"
            "      try {\n"
            "        const status = await fetchJsonNoStore('/api/auth/status');\n"
            "        if (status && status.authenticated) return true;\n"
            "      } catch (e) {}\n"
            "      await sleep(150 + i * 100);\n"
            "    }\n"
            "    return false;\n"
            "  }\n\n"
            "  function showAuthBoot() {\n"
            "    bootingAuth = true;\n"
            "    errEl.style.display = 'none';\n"
            "    setupNote.textContent = 'Checking sign-in status...';\n"
            "    setupNote.style.display = 'block';\n"
            "    confirmGroup.style.display = 'none';\n"
            "    toggleArea.style.display = 'none';\n"
            "    rememberToggle.style.display = 'none';\n"
            "    submitBtn.innerHTML = '<span class=\"login-spinner\" aria-hidden=\"true\"></span>';\n"
            "    setFormDisabled(true);\n"
            "    form.setAttribute('aria-busy', 'true');\n"
            "  }\n\n"
            "  showAuthBoot();\n",
        ),
        (
            "  function setMode(m) {\n"
            "    mode = m;\n"
            "    errEl.style.display = 'none';\n",
            "  function setMode(m) {\n"
            "    mode = m;\n"
            "    bootingAuth = false;\n"
            "    form.removeAttribute('aria-busy');\n"
            "    setFormDisabled(false);\n"
            "    errEl.style.display = 'none';\n",
        ),
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
            "    const data = await fetchJsonNoStore('/api/auth/status');\n"
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
        (
            "  }\n\n"
            "  // Check auth status. Be conservative: only show first-run setup when\n",
            "  }\n\n"
            "  function restoreSubmitLabel() {\n"
            "    if (form._totpMode) {\n"
            "      submitBtn.textContent = 'Verify';\n"
            "    } else if (mode === 'setup') {\n"
            "      submitBtn.textContent = 'Create Admin Account';\n"
            "    } else if (mode === 'signup') {\n"
            "      submitBtn.innerHTML = '<span style=\"position:relative;top:1px;\">Create Account</span>';\n"
            "    } else {\n"
            "      submitBtn.textContent = 'Sign In';\n"
            "    }\n"
            "  }\n\n"
            "  // Check auth status. Be conservative: only show first-run setup when\n",
            False,
        ),
        (
            "  form.addEventListener('submit', async (e) => {\n"
            "    e.preventDefault();\n"
            "    errEl.style.display = 'none';\n",
            "  form.addEventListener('submit', async (e) => {\n"
            "    e.preventDefault();\n"
            "    if (bootingAuth) return;\n"
            "    errEl.style.display = 'none';\n",
        ),
        (
            "    function finishLogin() {\n"
            "      const _rem = document.getElementById('remember').checked;\n",
            "    async function finishLogin() {\n"
            "      const _rem = document.getElementById('remember').checked;\n",
        ),
        (
            "      Promise.all([\n"
            "        fetch('/api/sessions', { credentials: 'same-origin' }).then(r => r.json()),\n"
            "        fetch('/api/auth/features', { credentials: 'same-origin' }).then(r => r.json()),\n"
            "        fetch('/api/auth/settings', { credentials: 'same-origin' }).then(r => r.json()),\n"
            "      ]).then(([sess, feat, sett]) => {\n",
            "      const sessionReady = await waitForAuthenticatedSession();\n"
            "      if (!sessionReady) {\n"
            "        throw new Error('Login cookie was not visible yet. Please try again.');\n"
            "      }\n"
            "      Promise.all([\n"
            "        fetch('/api/sessions', { credentials: 'same-origin', cache: 'no-store' }).then(r => r.json()),\n"
            "        fetch('/api/auth/features', { credentials: 'same-origin', cache: 'no-store' }).then(r => r.json()),\n"
            "        fetch('/api/auth/settings', { credentials: 'same-origin', cache: 'no-store' }).then(r => r.json()),\n"
            "      ]).then(([sess, feat, sett]) => {\n",
        ),
        (
            "        form._totpMode = false;\n"
            "        finishLogin();\n"
            "      } catch (err) {\n",
            "        form._totpMode = false;\n"
            "        await finishLogin();\n"
            "      } catch (err) {\n",
        ),
        (
            "      } catch (err) {\n"
            "        errEl.textContent = err.message;\n"
            "        errEl.style.display = 'block';\n"
            "        submitBtn.disabled = false;\n"
            "      }\n"
            "      return;\n",
            "      } catch (err) {\n"
            "        errEl.textContent = err.message;\n"
            "        errEl.style.display = 'block';\n"
            "        submitBtn.disabled = false;\n"
            "        restoreSubmitLabel();\n"
            "      }\n"
            "      return;\n",
            False,
        ),
        (
            "        errEl.textContent = 'Passwords do not match';\n"
            "        errEl.style.display = 'block';\n"
            "        submitBtn.disabled = false;\n"
            "        return;\n",
            "        errEl.textContent = 'Passwords do not match';\n"
            "        errEl.style.display = 'block';\n"
            "        submitBtn.disabled = false;\n"
            "        restoreSubmitLabel();\n"
            "        return;\n",
            False,
        ),
        (
            "        errEl.textContent = 'Password must be at least 8 characters';\n"
            "        errEl.style.display = 'block';\n"
            "        submitBtn.disabled = false;\n"
            "        return;\n",
            "        errEl.textContent = 'Password must be at least 8 characters';\n"
            "        errEl.style.display = 'block';\n"
            "        submitBtn.disabled = false;\n"
            "        restoreSubmitLabel();\n"
            "        return;\n",
            False,
        ),
        (
            "      } catch (err) {\n"
            "        errEl.textContent = err.message;\n"
            "        errEl.style.display = 'block';\n"
            "        submitBtn.disabled = false;\n"
            "        return;\n"
            "      }\n"
            "    }\n\n"
            "    // Login (auto-login after setup/signup too)\n",
            "      } catch (err) {\n"
            "        errEl.textContent = err.message;\n"
            "        errEl.style.display = 'block';\n"
            "        submitBtn.disabled = false;\n"
            "        restoreSubmitLabel();\n"
            "        return;\n"
            "      }\n"
            "    }\n\n"
            "    // Login (auto-login after setup/signup too)\n",
            False,
        ),
        (
            "      } catch (err) {\n"
            "        errEl.textContent = err.message;\n"
            "        errEl.style.display = 'block';\n"
            "        submitBtn.disabled = false;\n"
            "        restoreSubmitLabel();\n"
            "        return;\n"
            "      }\n"
            "    }\n\n"
            "    // Login (auto-login after setup/signup too)\n",
            "      } catch (err) {\n"
            "        const msg = String(err.message || 'Account creation failed');\n"
            "        if (mode === 'setup' && msg.toLowerCase().includes('already configured')) {\n"
            "          signupAllowed = false;\n"
            "          setMode('login');\n"
            "          errEl.textContent = 'Admin account already exists. Sign in with your username and password.';\n"
            "        } else {\n"
            "          errEl.textContent = msg;\n"
            "        }\n"
            "        errEl.style.display = 'block';\n"
            "        submitBtn.disabled = false;\n"
            "        restoreSubmitLabel();\n"
            "        return;\n"
            "      }\n"
            "    }\n\n"
            "    // Login (auto-login after setup/signup too)\n",
            False,
        ),
        (
            "    } catch (err) {\n"
            "      errEl.textContent = err.message;\n"
            "      errEl.style.display = 'block';\n"
            "      submitBtn.disabled = false;\n"
            "      return;\n"
            "    }\n",
            "    } catch (err) {\n"
            "      errEl.textContent = err.message;\n"
            "      errEl.style.display = 'block';\n"
            "      submitBtn.disabled = false;\n"
            "      restoreSubmitLabel();\n"
            "      return;\n"
            "    }\n",
            False,
        ),
        (
            "      finishLogin();\n"
            "    } catch (err) {\n",
            "      await finishLogin();\n"
            "    } catch (err) {\n",
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
            "    response.headers[\"Pragma\"] = \"no-cache\"\n"
            "    response.headers[\"Expires\"] = \"0\"\n"
            "    return response\n",
            False,
        ),
    ],
)

patch_file(
    "routes/auth_routes.py",
    [
        (
            "from fastapi import APIRouter, Request, Response, HTTPException\n",
            "from fastapi import APIRouter, Request, Response, HTTPException\n"
            "from fastapi.responses import JSONResponse\n",
        ),
        (
            "        return result\n\n"
            "    @router.post(\"/change-password\")\n",
            "        return JSONResponse(\n"
            "            result,\n"
            "            headers={\n"
            "                \"Cache-Control\": \"no-store, max-age=0\",\n"
            "                \"Pragma\": \"no-cache\",\n"
            "                \"Expires\": \"0\",\n"
            "            },\n"
            "        )\n\n"
            "    @router.post(\"/change-password\")\n",
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
