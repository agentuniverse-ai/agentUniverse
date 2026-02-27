# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/27
# @FileName: load_skill_tool.py

import re
import subprocess
from pathlib import Path
from typing import List

from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.logging.logging_util import LOGGER


def preprocess_instructions(instructions: str, skill_path: str) -> str:
    """Preprocess ``!`command``` syntax in SKILL.md body.

    Executes commands in the skill directory and replaces placeholders with
    stdout output.  If execution fails, retains the original placeholder with
    an error annotation.

    Example:
        Input:  "Current diff:\\n!`git diff --cached`\\nPlease review above."
        Output: "Current diff:\\n<actual git diff output>\\nPlease review above."
    """
    pattern = r'!`([^`]+)`'

    def _execute_command(match):
        cmd = match.group(1)
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=30, cwd=skill_path
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return f"[Command failed: {cmd}]\n{result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return f"[Command timeout: {cmd}]"
        except Exception as e:
            return f"[Command error: {cmd}] {str(e)}"

    return re.sub(pattern, _execute_command, instructions)


def _build_fork_system_content(skill, processed_instructions: str) -> str:
    """Build the system message content for a fork sub-agent.

    Combines the preprocessed skill instructions with a reference file index
    (if available) and the skill directory path.
    """
    content = f"Skill directory: {skill.skill_path}\n"
    content += ("Note: All relative paths mentioned in this skill are relative to the skill directory above. "
                "Always use absolute paths when reading or writing files.\n\n")
    content += processed_instructions

    # Append references/ directory file index
    references_dir = Path(skill.skill_path) / 'references'
    if references_dir.is_dir():
        ref_files = [f for f in references_dir.rglob('*') if f.is_file()]
        if ref_files:
            content += "\n\n---\nAvailable reference documents (load on demand via Read tool):\n"
            for ref in ref_files:
                content += f"- {ref.relative_to(skill.skill_path)}\n"

    return content


class LoadSkillTool(Tool):
    """Built-in tool for agents to dynamically load and invoke skills.

    Key design points:
    - Global singleton shared by all agents.
    - ``require_agent_context=True``: agent_context is automatically injected
      by ``execute_tool_call`` and excluded from the LLM-facing schema.
    - Skill list descriptions are placed in each agent's system message,
      not in this tool's description.
    """

    name: str = "load_skill"
    description: str = (
        "Load a skill to obtain specialized instructions and capabilities. "
        "skill_name must be a name from the available skills list."
    )
    tool_type: ToolTypeEnum = ToolTypeEnum.FUNC
    input_keys: List = ['skill_name']
    require_agent_context: bool = True

    def execute(self, skill_name: str, input: str = "",
                agent_context=None) -> str:
        """Load and execute a skill (sync).

        ``agent_context`` is injected automatically by ``execute_tool_call``;
        it is not exposed to the LLM.
        """
        from agentuniverse.agent.action.skill.skill_manager import SkillManager

        skill = SkillManager().get_instance_obj(skill_name)
        if skill is None:
            return f"Error: Skill '{skill_name}' not found."

        if skill.disable_model_invocation and not self._is_user_invocation(input):
            return (
                f"Skill '{skill_name}' has disable_model_invocation=true. "
                f"It can only be invoked manually by the user, not by LLM auto-invocation."
            )

        if skill.context == "fork":
            return self._execute_fork(skill, input, agent_context)
        else:
            return self._execute_inline(skill, input, agent_context)

    async def async_execute(self, skill_name: str, input: str = "",
                            agent_context=None) -> str:
        """Load and execute a skill (async).

        ``agent_context`` is injected automatically by ``async_execute_tool_call``;
        it is not exposed to the LLM.
        """
        from agentuniverse.agent.action.skill.skill_manager import SkillManager

        skill = SkillManager().get_instance_obj(skill_name)
        if skill is None:
            return f"Error: Skill '{skill_name}' not found."

        if skill.disable_model_invocation and not self._is_user_invocation(input):
            return (
                f"Skill '{skill_name}' has disable_model_invocation=true. "
                f"It can only be invoked manually by the user, not by LLM auto-invocation."
            )

        if skill.context == "fork":
            return await self._async_execute_fork(skill, input, agent_context)
        else:
            return self._execute_inline(skill, input, agent_context)

    def _is_user_invocation(self, input_text: str) -> bool:
        """Check whether invocation was triggered manually by the user."""
        return input_text.startswith("[USER_INVOCATION]") if input_text else False

    def _execute_inline(self, skill, input_text, agent_context) -> str:
        """Inline mode: preprocess instructions, add allowed_tools to context, return instructions text.

        Tool-set modification strategy:
        - Append skill's allowed_tools to agent_context's existing tool set.
        - No replacement, no restoration (inline mode changes are permanent).
        """
        # 1. Preprocess !`command` syntax
        processed_instructions = preprocess_instructions(
            skill.instructions, skill.skill_path
        )

        # 2. Append skill's allowed_tools to agent_context
        if agent_context and skill.allowed_tools:
            self._add_tools_to_context(skill, agent_context)

        # 3. Build return text
        result = f"[Skill '{skill.name}' loaded]\n\n"
        result += f"Skill directory: {skill.skill_path}\n"
        result += ("Note: All relative paths mentioned in this skill are relative to the skill directory above. "
                    "Always use absolute paths when reading or writing files.\n\n")
        result += processed_instructions

        # 4. Append references/ directory file index
        references_dir = Path(skill.skill_path) / 'references'
        if references_dir.is_dir():
            ref_files = [f for f in references_dir.rglob('*') if f.is_file()]
            if ref_files:
                result += "\n\n---\nAvailable reference documents (load on demand via Read tool):\n"
                for ref in ref_files:
                    result += f"- {ref.relative_to(skill.skill_path)}\n"

        if input_text:
            result += f"\n\n---\nUser input: {input_text}"
        return result

    def _resolve_fork_agent(self, skill):
        """Resolve the agent instance for fork mode.

        If ``skill.sub_agent`` is set, retrieves the named agent from
        AgentManager.  Otherwise, creates a default SkillForkAgentTemplate.

        Returns:
            (agent_instance, error_string_or_None)
        """
        if skill.sub_agent:
            from agentuniverse.agent.agent_manager import AgentManager
            agent = AgentManager().get_instance_obj(skill.sub_agent)
            if agent is None:
                return None, (
                    f"Error: sub_agent '{skill.sub_agent}' not found for "
                    f"skill '{skill.name}' fork mode."
                )
            return agent, None
        else:
            from agentuniverse.agent.template.skill_fork_agent_template import SkillForkAgentTemplate
            return SkillForkAgentTemplate(), None

    def _build_fork_context(self, skill, input_text, agent_context):
        """Build the isolated AgentContext and LLM for fork execution.

        Returns:
            (fork_context, llm, error_string_or_None)
        """
        from agentuniverse.agent.memory.enum import ChatMessageEnum
        from agentuniverse.agent.memory.message import Message
        from agentuniverse.ai_context.agent_context import AgentContext
        from agentuniverse.ai_context.tool_utils import build_tools_schema
        from agentuniverse.llm.llm_manager import LLMManager

        # 1. Determine LLM: skill.model overrides parent agent's LLM
        llm_name = skill.model
        if not llm_name and agent_context:
            llm_name = agent_context.llm_model.get('name')
        if not llm_name:
            return None, None, (
                f"Error: Skill '{skill.name}' fork mode requires a model. "
                f"Set 'model' in SKILL.md or ensure the parent agent has an LLM configured."
            )

        llm = LLMManager().get_instance_obj(llm_name)
        if llm is None:
            return None, None, (
                f"Error: LLM '{llm_name}' not found for skill '{skill.name}' fork mode."
            )

        # 2. Preprocess !`command` syntax
        processed_instructions = preprocess_instructions(
            skill.instructions, skill.skill_path
        )

        # 3. Build restricted tool set (only skill's allowed_tools, no load_skill)
        tool_names = skill.get_tool_names()
        tool_names = [n for n in tool_names if n != 'load_skill']
        tools_schema = build_tools_schema(tool_names)

        # 4. Build isolated AgentContext
        system_content = _build_fork_system_content(skill, processed_instructions)
        system_message = Message(type=ChatMessageEnum.SYSTEM, content=system_content)

        user_content = input_text or "Please execute the skill instructions above."
        current_messages = [Message(type=ChatMessageEnum.HUMAN, content=user_content)]

        fork_context = AgentContext(
            agent_id=f"skill_fork:{skill.name}",
            session_id=agent_context.session_id if agent_context else "",
            tool_names=tool_names,
            tools_schema=tools_schema,
            system_message=system_message,
            current_messages=current_messages,
        )

        return fork_context, llm, None

    def _execute_fork(self, skill, input_text, agent_context) -> str:
        """Fork mode: spawn an isolated sub-agent to execute the skill.

        The sub-agent has an independent AgentContext whose tool set contains
        **only** the skill's allowed_tools (hard restriction).  The main
        conversation's agent_context is unaffected.

        Core mechanism:
        1. Resolve agent: use skill.sub_agent or default SkillForkAgentTemplate
        2. Build isolated AgentContext with tools = allowed_tools only
        3. Call agent.run() with agent_context passed via InputObject
        4. Return the output text from the agent's OutputObject
        5. Sub-agent intermediate process doesn't enter main context
        """
        # 1. Resolve the fork agent
        fork_agent, err = self._resolve_fork_agent(skill)
        if err:
            return err

        # 2. Build isolated context and LLM
        fork_context, llm, err = self._build_fork_context(skill, input_text, agent_context)
        if err:
            return err

        # 3. Run via agent.run() — standard agent execution pipeline
        try:
            output_object = fork_agent.run(
                input=input_text or "",
                agent_context=fork_context,
                llm=llm,
                max_iterations=skill.max_iterations,
            )
        except Exception as e:
            LOGGER.warn(f"Skill '{skill.name}' fork execution failed: {e}")
            return f"Error: Skill '{skill.name}' fork execution failed: {e}"

        # 4. Return only the final text result
        result_text = output_object.get_data('output') if output_object else ""
        if not result_text:
            result_text = f"[Skill '{skill.name}' fork completed with no text output]"

        return f"[Skill '{skill.name}' fork result]\n\n{result_text}"

    async def _async_execute_fork(self, skill, input_text, agent_context) -> str:
        """Async fork mode: spawn an isolated sub-agent to execute the skill.

        Same as _execute_fork but uses agent.async_run().
        """
        # 1. Resolve the fork agent
        fork_agent, err = self._resolve_fork_agent(skill)
        if err:
            return err

        # 2. Build isolated context and LLM
        fork_context, llm, err = self._build_fork_context(skill, input_text, agent_context)
        if err:
            return err

        # 3. Run via agent.async_run() — standard async agent execution pipeline
        try:
            output_object = await fork_agent.async_run(
                input=input_text or "",
                agent_context=fork_context,
                llm=llm,
                max_iterations=skill.max_iterations,
            )
        except Exception as e:
            LOGGER.warn(f"Skill '{skill.name}' async fork execution failed: {e}")
            return f"Error: Skill '{skill.name}' fork execution failed: {e}"

        # 4. Return only the final text result
        result_text = output_object.get_data('output') if output_object else ""
        if not result_text:
            result_text = f"[Skill '{skill.name}' fork completed with no text output]"

        return f"[Skill '{skill.name}' fork result]\n\n{result_text}"

    def _add_tools_to_context(self, skill, agent_context) -> None:
        """Append skill's allowed_tools to agent_context's tool set.

        Extracts pure tool names from allowed_tools specs, resolves via
        ToolManager, and adds only tools not already present.
        """
        from agentuniverse.ai_context.tool_utils import build_tools_schema

        tool_names_to_add = skill.get_tool_names()
        existing_names = set(agent_context.tool_names)

        new_names = [n for n in tool_names_to_add if n not in existing_names]
        if not new_names:
            return

        new_schemas = build_tools_schema(new_names)
        agent_context.tool_names.extend(new_names)
        agent_context.tools_schema.extend(new_schemas)
