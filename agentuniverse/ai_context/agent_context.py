# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/2/13
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: agent_context.py

from __future__ import annotations

import string
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from agentuniverse.agent.agent_model import AgentModel
from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.ai_context.tool_utils import build_tools_schema


__all__ = ["AgentContext"]


class AgentContext(BaseModel):
    """Runtime state container for a single Agent run.

    Lifecycle: created at ``agent.run()`` start, discarded after the run
    returns.  Each run gets its own independent instance — even within the
    same session or trace.

    The agent's internal functions read configuration and messages from the
    context, and write intermediate results back into it.  Configuration
    comes from the existing ``AgentModel`` (which mirrors the agent YAML);
    this class does **not** redefine the config schema.
    """

    # ── Identity ──────────────────────────────────────────────────────
    agent_id: str = ""
    session_id: str = ""

    # ── Agent configuration (from YAML via AgentModel) ────────────────
    agent_model: Optional[AgentModel] = None
    """The full agent configuration loaded from YAML.  profile / action /
    memory / plan / info are all accessible via this object's dict fields."""

    # ── Tool configuration (mutable during run) ───────────────────────
    tool_names: List[str] = Field(default_factory=list)
    tools_schema: List[Dict[str, Any]] = Field(default_factory=list)

    # ── Messages (layered) ────────────────────────────────────────────
    system_message: Optional[Message] = None
    few_shot_messages: List[Message] = Field(default_factory=list)
    chat_history: List[Message] = Field(default_factory=list)
    current_messages: List[Message] = Field(default_factory=list)

    # ── Runtime references ────────────────────────────────────────────
    memory: Any = None
    """Memory instance. Typed as Any to avoid circular imports."""
    output_stream: Any = None
    """Streaming output channel."""

    # ── Extension ─────────────────────────────────────────────────────
    extra: Dict[str, Any] = Field(default_factory=dict)
    """Free-form extension dict for business-specific data."""

    # ------------------------------------------------------------------
    # Convenience accessors into agent_model
    # ------------------------------------------------------------------

    @property
    def profile(self) -> dict:
        """Shortcut to ``agent_model.profile``."""
        return self.agent_model.profile if self.agent_model else {}

    @property
    def action(self) -> dict:
        """Shortcut to ``agent_model.action``."""
        return self.agent_model.action if self.agent_model else {}

    @property
    def llm_model(self) -> dict:
        """Shortcut to ``profile['llm_model']``."""
        return self.profile.get('llm_model', {})

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    def create(
        cls,
        *,
        agent_model: AgentModel,
        session_id: str = "",
        input_dict: Optional[Dict[str, Any]] = None,
        memory: Any = None,
        output_stream: Any = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> "AgentContext":
        """High-level factory that performs full initialisation.

        Derives everything from the existing ``AgentModel`` configuration:
        - agent_id from ``agent_model.info['name']``
        - system_message from profile introduction + target
        - user message from profile instruction
        - tool_names / tools_schema from action.tool + action.toolkit
        - chat_history from the provided *memory* instance

        Args:
            agent_model: The agent's full configuration (from YAML).
            session_id: Session identifier for this run.
            input_dict: Variables for template rendering (e.g. ``{query}``).
            memory: Optional Memory instance to load chat history from.
            output_stream: Optional streaming output channel.
            extra: Optional free-form extension data.
        """
        input_dict = input_dict or {}
        profile = _resolve_profile(agent_model.profile or {})
        action = agent_model.action or {}
        agent_id = (agent_model.info or {}).get('name', '')

        # -- System message (introduction + target) --
        system_message = _build_system_message(profile, input_dict)

        # -- Few-shot messages --
        few_shot_messages = _build_few_shot_messages(profile)

        # -- Initial user message (instruction) --
        current_messages: List[Message] = []
        user_msg = _build_user_message(profile, input_dict)
        if user_msg is not None:
            current_messages.append(user_msg)

        # -- Chat history from memory --
        chat_history: List[Message] = []
        if memory is not None:
            memory_config = agent_model.memory or {}
            chat_history = memory.get(
                session_id=session_id,
                agent_id=agent_id,
                prune=memory_config.get('prune', False),
                top_k=memory_config.get('top_k', 20),
            )

        # -- Tools (from action.tool + action.toolkit) --
        tool_name_list: List[str] = list(action.get('tool', []) or [])
        toolkit_names: List[str] = action.get('toolkit', []) or []
        if toolkit_names:
            from agentuniverse.agent.action.toolkit.toolkit_manager import \
                ToolkitManager
            for toolkit_name in toolkit_names:
                toolkit = ToolkitManager().get_instance_obj(toolkit_name)
                if toolkit:
                    tool_name_list.extend(toolkit.tool_names)
        tools_schema = build_tools_schema(tool_name_list)

        return cls(
            agent_id=agent_id,
            session_id=session_id,
            agent_model=agent_model,
            tool_names=tool_name_list,
            tools_schema=tools_schema,
            system_message=system_message,
            few_shot_messages=few_shot_messages,
            chat_history=chat_history,
            current_messages=current_messages,
            memory=memory,
            output_stream=output_stream,
            extra=extra or {},
        )

    # ------------------------------------------------------------------
    # Message helpers
    # ------------------------------------------------------------------

    def build_messages(self) -> List[Message]:
        """Assemble the full message list for LLM submission.

        Concatenation order: system -> few_shot -> chat_history -> current.
        This is the **only** exit point for messages going to the LLM.

        Returns Message objects (not dicts) so that downstream converters
        like ``au_messages_to_openai`` can read attributes via ``getattr``.
        """
        result: List[Message] = []
        if self.system_message is not None:
            result.append(self.system_message)
        result.extend(self.few_shot_messages)
        result.extend(self.chat_history)
        result.extend(self.current_messages)
        return result

    def append_message(self, msg: Message) -> None:
        """Append a message to *current_messages*."""
        self.current_messages.append(msg)

    def update_user_message(self, input_dict: Dict[str, Any]) -> None:
        """Rebuild the user message from the instruction template.

        Useful in retry scenarios where the input changes between attempts.
        If a human message already exists at the end of *current_messages*
        it is replaced; otherwise a new one is appended.
        """
        new_msg = _build_user_message(self.profile, input_dict)
        if new_msg is None:
            return

        if (
            self.current_messages
            and self.current_messages[-1].type == ChatMessageEnum.HUMAN
        ):
            self.current_messages[-1] = new_msg
        else:
            self.current_messages.append(new_msg)

    # ------------------------------------------------------------------
    # Tool helpers
    # ------------------------------------------------------------------

    def set_tools(self, tool_names: List[str]) -> None:
        """Update the tool set and automatically rebuild schemas."""
        self.tool_names = tool_names
        self.tools_schema = build_tools_schema(tool_names)

    # ------------------------------------------------------------------
    # LLM helpers
    # ------------------------------------------------------------------

    def set_llm(self, **kwargs: Any) -> None:
        """Update LLM parameters in ``profile['llm_model']`` in-place.

        Example::

            ctx.set_llm(name="qwen_turbo_llm", temperature=0.8)
        """
        llm_model = self.profile.setdefault('llm_model', {})
        llm_model.update(kwargs)

    # ------------------------------------------------------------------
    # LLM builder
    # ------------------------------------------------------------------

    def build_llm(self) -> Any:
        """Build and configure an LLM instance from *agent_model* config.

        Returns a fully configured LLM ready for ``call()`` / ``acall()``.
        """
        from agentuniverse.llm.llm_manager import LLMManager
        llm_name = self.llm_model.get('name')
        llm = LLMManager().get_instance_obj(llm_name)
        if llm is not None and self.agent_model:
            llm = llm.set_by_agent_model(**self.agent_model.llm_params())
        return llm

    # ------------------------------------------------------------------
    # Streaming helpers
    # ------------------------------------------------------------------

    def stream_token(self, chunk: str, agent_info: dict = None) -> None:
        """Push an incremental token to *output_stream*."""
        if self.output_stream is None:
            return
        from agentuniverse.base.util.common_util import stream_output
        stream_output(self.output_stream, {
            'type': 'token',
            'data': {
                'chunk': chunk,
                'agent_info': agent_info or {},
            }
        })

    def stream_final(self, output: str, agent_info: dict = None) -> None:
        """Push a final result to *output_stream*.

        Base implementation is a no-op; subclasses may override to customise
        the final-output format.
        """
        pass

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def llm_params(self) -> dict:
        """LLM parameters derived from *agent_model*."""
        if self.agent_model:
            return self.agent_model.llm_params()
        return {}

    @property
    def max_iterations(self) -> int:
        """Maximum tool-calling iterations from profile config."""
        return self.profile.get('max_iterations', 10)


# ======================================================================
# Private helpers for message construction
# ======================================================================

def _resolve_profile(profile: dict) -> dict:
    """Merge prompt_version content into profile; inline values take priority.

    If ``profile['prompt_version']`` is set, load the corresponding Prompt
    object via PromptManager.  Uses the Prompt's ``prompt_model``
    (AgentPromptModel) to pull structured fields — introduction, target,
    instruction, output_format, few_shot_examples, and custom sections.
    """
    prompt_version = profile.get('prompt_version')
    if not prompt_version:
        return profile

    from agentuniverse.prompt.prompt_manager import PromptManager
    version_prompt = PromptManager().get_instance_obj(prompt_version)
    if version_prompt is None:
        return profile

    pm = getattr(version_prompt, 'prompt_model', None)
    if pm is None:
        return profile

    resolved = dict(profile)

    # Named str fields: introduction, target, output_format, instruction
    for field in ('introduction', 'target', 'output_format', 'instruction'):
        if not resolved.get(field):
            value = getattr(pm, field, None)
            if value:
                resolved[field] = value

    # few_shot_examples → few_shot (convert to Message-compatible dicts)
    if not resolved.get('few_shot') and pm.few_shot_examples:
        few_shot_msgs = []
        for ex in pm.few_shot_examples:
            few_shot_msgs.append({'type': 'human', 'content': ex.input})
            few_shot_msgs.append({'type': 'ai', 'content': ex.output})
        resolved['few_shot'] = few_shot_msgs

    # Custom sections
    named = set(pm._NAMED_STR_FIELDS) | {'few_shot_examples'}
    for k, v in pm.sections.items():
        if k not in named and v and not resolved.get(k):
            resolved[k] = v

    return resolved


def _render_template(template: str, variables: Dict[str, Any]) -> str:
    """Best-effort ``str.format_map`` that leaves unresolved placeholders."""
    try:
        return template.format_map(variables)
    except KeyError:
        fmt = string.Formatter()
        parts: List[str] = []
        for literal_text, field_name, format_spec, conversion in fmt.parse(template):
            parts.append(literal_text)
            if field_name is not None:
                value = variables.get(field_name)
                if value is not None:
                    parts.append(str(value))
                else:
                    parts.append("{" + field_name + "}")
        return "".join(parts)


def _build_system_message(
    profile: dict,
    input_dict: Dict[str, Any],
) -> Optional[Message]:
    """Build the system message from profile introduction + target."""
    parts: List[str] = []
    if profile.get('introduction'):
        parts.append(_render_template(profile['introduction'], input_dict))
    if profile.get('target'):
        parts.append(_render_template(profile['target'], input_dict))
    if not parts:
        return None
    return Message(type=ChatMessageEnum.SYSTEM, content="\n".join(parts))


def _build_few_shot_messages(profile: dict) -> List[Message]:
    """Convert profile few_shot dicts into Message objects."""
    few_shot = profile.get('few_shot')
    if not few_shot:
        return []
    return [Message.from_dict(item) for item in few_shot]


def _build_user_message(
    profile: dict,
    input_dict: Dict[str, Any],
) -> Optional[Message]:
    """Build the initial user message from the instruction template."""
    instruction = profile.get('instruction')
    if not instruction:
        return None
    content = _render_template(instruction, input_dict)
    return Message(type=ChatMessageEnum.HUMAN, content=content)
