# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import copy
import json
import math
import re
# @Time    : 2024/4/16 14:42
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: prompt_util.py
from typing import Any, Union
from typing import Dict
from typing import List

import tiktoken

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.enum import PromptProcessEnum
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel

__all__ = [
    "summarize_messages", "summarize_by_map_reduce", "summarize_by_stuff",
    "split_text_on_tokens", "split_texts", "truncate_content", "generate_template",
    "generate_chat_template", "check_missing", "render_content", "render_str",
    "process_llm_token"
]


DEFAULT_SUMMARIZE_INSTRUCTION = (
    "请对上述对话进行简要总结。对于其中的任何图片或非文本内容，请描述其内容以及与对话的相关性。"
    "总结中请务必保留关键决策、事实信息、数据点以及尚未解决的问题。"
)


def summarize_messages(
    messages: List[Message],
    llm: LLM,
    instruction: str = None,
    token_max: int = 80000,
    chunk_size: int = 10,
    previous_summary: str = None,
) -> str:
    """
    Summarize a list of Messages, preserving multimodal context.

    Strategy:
      - If messages fit within token_max → single-pass (stuff)
      - If not → chunk into groups, summarize each, then combine

    Args:
        messages:         Conversation messages to summarize (may contain images/audio).
        llm:              LLM instance (ideally supports vision for multimodal).
        instruction:      Custom summarize instruction; uses default if None.
        token_max:        Max tokens for a single LLM call context. None = no limit (stuff).
        chunk_size:       Max number of messages per chunk for map phase.
        previous_summary: Rolling summary from earlier rounds, injected as context.

    Returns:
        Summary text string.
    """
    instruction = instruction or DEFAULT_SUMMARIZE_INSTRUCTION

    if not messages:
        return ""

    # 尝试 stuff，放不下再 map-reduce
    if token_max is None or _estimate_messages_tokens(llm, messages) <= token_max:
        return _summarize_single_pass(messages, llm, instruction, previous_summary)
    else:
        return _summarize_chunked(messages, llm, instruction, token_max, chunk_size, previous_summary)


def _summarize_single_pass(
    messages: List[Message],
    llm: LLM,
    instruction: str,
    previous_summary: str = None,
) -> str:
    """
    Stuff 模式：把完整对话 + 摘要指令一次性发给 LLM。
    多模态内容原样保留，LLM 自己看图/听音频。
    """
    prompt_messages = _build_summarize_prompt(messages, instruction, previous_summary)
    return _call_llm_extract_text(llm, prompt_messages)


def _summarize_chunked(
    messages: List[Message],
    llm: LLM,
    instruction: str,
    token_max: int,
    chunk_size: int,
    previous_summary: str = None,
) -> str:
    """
    分块模式：按 chunk_size 分组 → 每组摘要 → 递归合并直到放得下。
    """
    # Phase 1: 按消息条数分块（保证不拆开单条多模态消息）
    chunks = _chunk_messages(messages, llm, token_max, chunk_size)

    # Phase 2: Map — 每个 chunk 独立摘要（多模态内容原样传入）
    summaries = []
    for i, chunk in enumerate(chunks):
        # 第一个 chunk 带上 previous_summary 作为上文
        prev = previous_summary if i == 0 else None
        summary = _summarize_single_pass(chunk, llm, instruction, prev)
        summaries.append(summary)

    # Phase 3: 递归 reduce — 把文本摘要合并到放得下为止
    while len(summaries) > 1:
        combined = "\n\n---\n\n".join(summaries)
        if llm.get_num_tokens(combined) <= token_max:
            break
        # 还是太长，再分组合并一轮
        groups = _group_texts_by_token_limit(summaries, llm, token_max)
        summaries = [
            _reduce_texts(group, llm, instruction)
            for group in groups
        ]

    # 最终 reduce
    if len(summaries) == 1:
        return summaries[0]

    return _reduce_texts(summaries, llm, instruction)


# ─── Building blocks ───────────────────────────────────────────

def _build_summarize_prompt(
    messages: List[Message],
    instruction: str,
    previous_summary: str = None,
) -> List[Message]:
    """
    构造摘要用的 prompt:
      [system] 你是摘要助手 (+ 上一轮摘要)
      [原始对话 messages 原样保留]
      [user] 请总结以上对话
    """
    prompt = []

    # System message with optional rolling summary
    system_text = "你是一个对话总结助理"
    if previous_summary:
        system_text += (
            f"\n\nHere is the summary of earlier conversation for context:\n"
            f"{previous_summary}"
        )
    prompt.append(Message(type=ChatMessageEnum.SYSTEM, content=system_text))

    # 原始对话消息 — 多模态内容(图片/音频)原样传入
    prompt.extend(messages)

    # 摘要指令
    prompt.append(Message(type=ChatMessageEnum.USER, content=instruction))

    return prompt


def _reduce_texts(texts: List[str], llm: LLM, instruction: str) -> str:
    """将多段文本摘要合并为一段。"""
    combined = "\n\n---\n\n".join(texts)
    messages = [
        Message(type=ChatMessageEnum.SYSTEM, content="You are a conversation summarizer."),
        Message(type=ChatMessageEnum.USER, content=(
            f"The following are partial summaries of a conversation. "
            f"Combine them into a single coherent summary.\n\n"
            f"{combined}\n\n{instruction}"
        )),
    ]
    return _call_llm_extract_text(llm, messages)


def _chunk_messages(messages, llm, token_max, chunk_size):
    chunks = []
    current = []
    current_tokens = 3  # reply prime overhead

    for msg in messages:
        msg_tokens = _estimate_messages_tokens(llm, [msg])

        if current and (
            len(current) >= chunk_size
            or current_tokens + msg_tokens > token_max
        ):
            chunks.append(current)
            current = [msg]
            current_tokens = 3 + msg_tokens
        else:
            current.append(msg)
            current_tokens += msg_tokens

    if current:
        chunks.append(current)
    return chunks


def _group_texts_by_token_limit(
    texts: List[str],
    llm: LLM,
    token_limit: int,
) -> List[List[str]]:
    """将文本列表按 token 限制分组。"""
    groups, current = [], []
    current_tokens = 0

    for text in texts:
        text_tokens = llm.get_num_tokens(text)
        if current and current_tokens + text_tokens > token_limit:
            groups.append(current)
            current = [text]
            current_tokens = text_tokens
        else:
            current.append(text)
            current_tokens += text_tokens

    if current:
        groups.append(current)
    return groups


# ─── estimate token Utilities ──────────────────────────────────────────────────
def estimate_tools_tokens(tools: list, model_name: str = "gpt-4-turbo") -> int:
    """
    估算工具列表的 Token 消耗。

    Args:
        tools: 你的 Tool 实例列表
        model_name: 用于选择 tokenizer
    """
    if not tools:
        return 0

    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    total_tokens = 0

    # 1. 遍历所有工具
    for tool in tools:
        # 调用你代码里的 get_function_schema()
        schema_dict = tool.get_function_schema()

        schema_str = json.dumps(schema_dict, ensure_ascii=False,
                                separators=(",", ":"))

        # 3. 累加 Token
        total_tokens += len(encoding.encode(schema_str))

    # 4. 加上 Overhead (基础开销)
    total_tokens += 15

    return total_tokens


def calculate_image_tokens(width: int=1000, height: int=1000, detail: str = "auto") -> int:
    """
    根据 OpenAI 规则估算图片 Token。。
    """
    if detail == "low":
        return 85

    # High detail 逻辑 (简化版模拟 OpenAI 缩放逻辑)
    # 1. 缩放到 2048x2048 内
    if width > 2048 or height > 2048:
        ratio = min(2048 / width, 2048 / height)
        width = int(width * ratio)
        height = int(height * ratio)

    # 2. 缩放到最短边 768
    if width >= height and height > 768:
        width = int(width * (768 / height))
        height = 768
    elif height > width and width > 768:
        height = int(height * (768 / width))
        width = 768

    # 3. 计算 512x512 tiles
    tiles_width = math.ceil(width / 512)
    tiles_height = math.ceil(height / 512)
    total_tiles = tiles_width * tiles_height

    return 170 * total_tiles + 85


def _extract_text_from_content(content) -> str:
    """从 ContentT 提取纯文本（用于 token 估算）。"""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if text := item.get("text", ""):
                    parts.append(text)
                elif "image_url" in item:
                    parts.append("[image]")  # 图片给个固定 token 估算
                elif "input_audio" in item:
                    parts.append("[audio]")
        return "\n".join(parts)
    return str(content)


def _estimate_messages_tokens(llm, messages: list) -> int:
    """更精准的 Token 估算"""
    total_tokens = 0
    try:
        encoding = tiktoken.encoding_for_model(llm.model_name)
    except:
        encoding = tiktoken.get_encoding("cl100k_base")

    # 1. 累加消息内容
    for m in messages:
        total_tokens += 4

        total_tokens += len(encoding.encode(m.role))

        if isinstance(m.content, str):
            total_tokens += len(encoding.encode(m.content))

        elif isinstance(m.content, list):
            for item in m.content:
                if item.get("type") == "text":
                    total_tokens += len(encoding.encode(item["text"]))
                elif item.get("type") == "image_url":
                    total_tokens += calculate_image_tokens(detail="high")
                elif item.get("type") == "input_audio":
                    total_tokens += 200 # default estimate

        # 2. 处理 Tool Call
        if hasattr(m, "tool_calls") and m.tool_calls:
            for tool in m.tool_calls:
                total_tokens += len(encoding.encode(str(tool.function)))

    return total_tokens + 3  # Reply prime overhead


def calculate_total_context(llm, messages: list, tools: list = None) -> int:
    # 1. 消息体 Token
    msg_tokens = _estimate_messages_tokens(llm, messages)

    # 2. 工具定义 Token
    tool_tokens = estimate_tools_tokens(tools, llm.model_name) if tools else 0

    return msg_tokens + tool_tokens


def _call_llm_extract_text(llm: LLM, messages: List[Message]) -> str:
    """调用 LLM 并提取文本结果。"""
    result = llm.call(messages=messages)
    return str(result.text)


# -----------deprecated summarize method-----
def summarize_by_stuff(texts: List[str], llm: LLM, summary_prompt):
    """
    Stuff summarization method - combines all texts and summarizes in one go.

    Algorithm principle (same as langchain's StuffDocumentsChain):
    1. Combine all text chunks into a single text
    2. Format the prompt with the combined text
    3. Send to LLM for summarization in a single call
    4. Return the summary result

    This is the simplest approach but may fail if combined text exceeds LLM's context window.
    """
    # Combine all texts into one
    combined_text = "\n\n".join(texts)

    # Format the prompt with the combined text
    prompt_variables = {}
    if hasattr(summary_prompt, 'input_variables') and summary_prompt.input_variables:
        # Use 'text' variable if available, otherwise use first variable
        if 'text' in summary_prompt.input_variables:
            prompt_variables['text'] = combined_text
        else:
            prompt_variables[summary_prompt.input_variables[0]] = combined_text

    # Format the prompt template
    if hasattr(summary_prompt, 'prompt_template'):
        formatted_prompt = summary_prompt.prompt_template.render(**prompt_variables)
    else:
        formatted_prompt = combined_text

    # Create messages for LLM
    messages = [
        Message(type=ChatMessageEnum.USER, content=formatted_prompt)
    ]

    # Call LLM
    result = llm.call(messages=messages)

    # Extract text from result
    if hasattr(result, 'text'):
        return result.text
    elif hasattr(result, 'message') and hasattr(result.message, 'content'):
        return result.message.content_text
    else:
        return str(result)


def summarize_by_map_reduce(texts: List[str], llm: LLM, summary_prompt, combine_prompt,
                           token_max: int = 3000, collapse_max_retries: int = None):
    """
    Map-reduce summarization method - handles large documents by hierarchical summarization.

    Algorithm principle (same as langchain's MapReduceDocumentsChain + ReduceDocumentsChain):
    1. Map phase: Summarize each text chunk individually using summary_prompt
    2. Collapse phase: If map results exceed token_max, recursively group and collapse them
    3. Reduce phase: Combine final summaries using combine_prompt to produce final summary

    Args:
        texts: List of text chunks to summarize
        llm: LLM instance for generating summaries
        summary_prompt: Prompt for map phase (summarizing individual chunks)
        combine_prompt: Prompt for reduce phase (combining summaries)
        token_max: Maximum tokens for collapse phase (default: 3000)
        collapse_max_retries: Max retries for collapse, None means unlimited

    The key difference from naive map-reduce is the collapse phase that prevents
    exceeding context window when combining many summaries.
    """

    def _format_prompt_with_text(prompt, text: str) -> str:
        """Helper to format a prompt template with text."""
        prompt_variables = {}
        if hasattr(prompt, 'input_variables') and prompt.input_variables:
            if 'text' in prompt.input_variables:
                prompt_variables['text'] = text
            else:
                prompt_variables[prompt.input_variables[0]] = text

        if hasattr(prompt, 'prompt_template'):
            return prompt.prompt_template.render(**prompt_variables)
        else:
            return text

    def _call_llm_with_prompt(prompt_text: str) -> str:
        """Helper to call LLM and extract result text."""
        messages = [Message(type=ChatMessageEnum.USER, content=prompt_text)]
        result = llm.call(messages=messages)

        if hasattr(result, 'text'):
            return result.text
        elif hasattr(result, 'message') and hasattr(result.message, 'content'):
            return result.message.content
        else:
            return str(result)

    def _get_token_count(text: str) -> int:
        """Get token count for a text."""
        return llm.get_num_tokens(text)

    def _get_texts_token_count(text_list: List[str]) -> int:
        """Get total token count for a list of texts including prompt overhead."""
        # Combine texts to estimate full prompt size
        combined = "\n\n".join(text_list)
        # Add prompt template overhead (approximate)
        formatted = _format_prompt_with_text(combine_prompt, combined)
        return _get_token_count(formatted)

    def _split_texts_by_token_limit(text_list: List[str], token_limit: int) -> List[List[str]]:
        """
        Split texts into groups where each group's token count doesn't exceed token_limit.
        Same logic as langchain's split_list_of_docs.
        """
        result_groups = []
        current_group = []

        for text in text_list:
            current_group.append(text)
            # Check if current group exceeds limit
            num_tokens = _get_texts_token_count(current_group)

            if num_tokens > token_limit:
                if len(current_group) == 1:
                    # Single text is longer than limit, cannot split further
                    raise ValueError(
                        f"A single document was longer than the token limit ({token_limit}). "
                        f"Cannot handle this. Document token count: {num_tokens}"
                    )
                # Remove last text and save current group
                result_groups.append(current_group[:-1])
                current_group = [current_group[-1]]

        # Add remaining texts
        if current_group:
            result_groups.append(current_group)

        return result_groups

    def _collapse_texts(text_list: List[str]) -> str:
        """Collapse a list of texts into one by combining them with combine_prompt."""
        combined_text = "\n\n".join(text_list)
        formatted_prompt = _format_prompt_with_text(combine_prompt, combined_text)
        return _call_llm_with_prompt(formatted_prompt)

    # Phase 1: Map - summarize each text chunk individually
    summaries = []
    for text in texts:
        formatted_prompt = _format_prompt_with_text(summary_prompt, text)
        summary = _call_llm_with_prompt(formatted_prompt)
        summaries.append(summary)

    # Phase 2: Collapse - recursively reduce summaries if they exceed token_max
    # This is the key logic from ReduceDocumentsChain._collapse
    result_texts = summaries
    num_tokens = _get_texts_token_count(result_texts)
    retries = 0

    while num_tokens > token_max:
        # Split into groups that each fit within token_max
        text_groups = _split_texts_by_token_limit(result_texts, token_max)

        # Collapse each group into a single text
        result_texts = []
        for group in text_groups:
            collapsed = _collapse_texts(group)
            result_texts.append(collapsed)

        # Check if we've reduced enough
        num_tokens = _get_texts_token_count(result_texts)
        retries += 1

        if collapse_max_retries is not None and retries >= collapse_max_retries:
            raise ValueError(
                f"Exceeded {collapse_max_retries} retries trying to collapse "
                f"documents to {token_max} tokens. Current tokens: {num_tokens}"
            )

    # Phase 3: Reduce - final combination of all collapsed summaries
    final_combined_text = "\n\n".join(result_texts)
    final_formatted_prompt = _format_prompt_with_text(combine_prompt, final_combined_text)
    final_summary = _call_llm_with_prompt(final_formatted_prompt)

    return final_summary


def split_text_on_tokens(text: str, text_token: int, chunk_size=800, chunk_overlap=100) -> List[str]:
    """Split incoming text and return chunks using tokenizer."""
    # calculate the number of characters represented by each token.
    char_per_token = len(text) / text_token
    chunk_char_size = int(chunk_size * char_per_token)
    chunk_char_overlap = int(chunk_overlap * char_per_token)

    result = []
    current_position = 0

    while current_position + chunk_char_overlap < len(text):
        if current_position + chunk_char_size >= len(text):
            chunk = text[current_position:]
        else:
            chunk = text[current_position:current_position + chunk_char_size]

        result.append(chunk)
        current_position += chunk_char_size - chunk_char_overlap

    if len(result) == 0:
        result.append(text[current_position:])

    return result


def split_texts(texts: list[str], llm: LLM, chunk_size=800, chunk_overlap=100, retry=True) -> list[str]:
    """
    split texts into chunks with the fixed token length -- general method
    """
    try:
        split_texts_res = []
        for text in texts:
            text_token = llm.get_num_tokens(text)
            split_texts_res.extend(
                split_text_on_tokens(text=text, text_token=text_token, chunk_size=chunk_size,
                                     chunk_overlap=chunk_overlap))
        return split_texts_res
    except Exception as e:
        if retry:
            return split_texts(texts=texts, llm=llm, retry=False)
        raise ValueError("split text failed, exception=" + str(e))


def truncate_content(content: str, token_length: int, llm: LLM) -> str:
    """
    truncate the content based on the llm token limit
    """
    return str(split_texts(texts=[content], chunk_size=token_length, llm=llm)[0])


def generate_template(agent_prompt_model: AgentPromptModel,
                      prompt_assemble_order: list[str]) -> str:
    """Convert the agent prompt model to an ordered plain-text template string.

    Changes vs. old version:
    - Uses ``get_section()`` / ``sections`` instead of raw ``getattr`` so that
      both classic named fields *and* custom sections are covered.
    - ``few_shot_examples`` (now ``List[FewShotExample]``) is serialised into
      readable ``User: ... / Assistant: ...`` pairs.

    Args:
        agent_prompt_model: The agent prompt model.
        prompt_assemble_order: The prompt assemble ordered list.

    Returns:
        A single string with sections joined by ``\\n``.
    """
    values: list[str] = []
    for attr in prompt_assemble_order:
        # few_shot_examples 特殊处理：展开为文本对
        if attr == "few_shot_examples":
            if agent_prompt_model.few_shot_examples:
                for ex in agent_prompt_model.few_shot_examples:
                    values.append(f"User: {ex.input}\nAssistant: {ex.output}")
            continue

            # 优先从 get_section 获取（覆盖经典字段 + 自定义 sections）
        content = agent_prompt_model.get_section(attr)
        if content is not None:
            values.append(content)

    return "\n".join(values)


def generate_chat_template(agent_prompt_model: AgentPromptModel, prompt_assemble_order: list[str]) -> list[Message]:
    """Convert the agent prompt model to the agentUniverse message list.

    Args:
        agent_prompt_model (AgentPromptModel): The agent prompt model.
        prompt_assemble_order (list[str]): The prompt assemble ordered list.
    Returns:
        list: The agentUniverse message list.
    """
    # 利用 AgentPromptModel.to_messages 生成初始 message list
    message_list = agent_prompt_model.to_messages(
        assemble_order=prompt_assemble_order)

    if not message_list:
        return message_list

    # use_enum_values=True 使 msg.type 存储的是字符串值，因此用 .value 比较
    system_value = ChatMessageEnum.SYSTEM.value

    # 收集所有 SYSTEM 消息的 *文本* 内容并合并
    system_parts: list[str] = []
    for msg in message_list:
        if msg.type == system_value and isinstance(msg.content, str):
            system_parts.append(msg.content)

    if system_parts:
        merged_system = "\n".join(system_parts)
        # 过滤掉原来的 SYSTEM 消息，把合并后的放在最前面
        message_list = [
            msg for msg in message_list if msg.type != system_value
        ]
        message_list.insert(
            0, Message(type=ChatMessageEnum.SYSTEM, content=merged_system)
        )

    return message_list

def process_llm_token(agent_llm: LLM, lc_prompt_template, profile: dict, planner_input: dict,
                      var_to_process: str = 'background'):
    """Process the prompt template based on the prompt processor.

    Args:
        agent_llm (LLM): The agent llm.
        lc_prompt_template: The langchain prompt template.
        profile (dict): The profile.
        planner_input (dict): The planner input.
        var_to_process (str): The variable needs to be processed in the prompt, the default is 'background'
    """
    llm_model: dict = profile.get('llm_model')

    # get the prompt processor configuration
    prompt_processor: dict = llm_model.get('prompt_processor') or dict()
    prompt_processor_type: str = prompt_processor.get('type') or PromptProcessEnum.TRUNCATE.value
    prompt_processor_llm: str = prompt_processor.get('llm')

    # get the summary and combine prompt versions
    summary_prompt_version: str = prompt_processor.get('summary_prompt_version') or 'prompt_processor.summary_cn'
    combine_prompt_version: str = prompt_processor.get('combine_prompt_version') or 'prompt_processor.combine_cn'

    prompt_input_dict = {key: planner_input[key] for key in lc_prompt_template.input_variables if key in planner_input}

    # get the llm instance for prompt compression
    prompt_llm: LLM = LLMManager().get_instance_obj(prompt_processor_llm)

    if prompt_llm is None:
        prompt_llm = agent_llm

    prompt = lc_prompt_template.render(**prompt_input_dict)
    # get the number of tokens in the prompt
    prompt_tokens: int = agent_llm.get_num_tokens(prompt)

    input_tokens = agent_llm.max_context_length() - llm_model.get('max_tokens', agent_llm.max_tokens)
    if input_tokens <= 0:
        raise Exception("The current output max tokens limit is greater than the context length of the LLM model, "
                        "please adjust it by editing the `max_tokens` parameter in the llm yaml.")

    if prompt_tokens <= input_tokens:
        return

    process_prompt_type_enum = PromptProcessEnum.from_value(prompt_processor_type)

    # process the specific variable in the prompt
    content = planner_input.get(var_to_process)

    if content:
        if process_prompt_type_enum == PromptProcessEnum.TRUNCATE:
            planner_input[var_to_process] = truncate_content(content, input_tokens, agent_llm)
        elif process_prompt_type_enum == PromptProcessEnum.STUFF:
            planner_input[var_to_process] = summarize_by_stuff(texts=[content], llm=prompt_llm,
                                                               summary_prompt=PromptManager().get_instance_obj(
                                                                   summary_prompt_version))
        elif process_prompt_type_enum == PromptProcessEnum.MAP_REDUCE:
            planner_input[var_to_process] = summarize_by_map_reduce(texts=split_texts([content], agent_llm),
                                                                    llm=prompt_llm,
                                                                    summary_prompt=PromptManager().get_instance_obj(summary_prompt_version),
                                                                    combine_prompt=PromptManager().get_instance_obj(
                                                                        combine_prompt_version))


# ---------Template Render Utilities---------------
_PLACEHOLDER_RE = re.compile(r"\{(.*?)\}")
_ESCAPED_OPEN = "\x00__LBRACE__\x00"
_ESCAPED_CLOSE = "\x00__RBRACE__\x00"


def _strip_escaped_braces(template: str) -> str:
    """将 {{ 和 }} 替换为内部占位符，避免被当作模板变量解析。"""
    return template.replace("{{", _ESCAPED_OPEN).replace("}}", _ESCAPED_CLOSE)


def _restore_escaped_braces(text: str) -> str:
    """将内部占位符还原为字面量 { 和 }，与 Python str.format() 的 {{ / }} 转义行为一致。"""
    return text.replace(_ESCAPED_OPEN, "{").replace(_ESCAPED_CLOSE, "}")


def check_missing(template: str, kwargs: Dict[str, Any]) -> None:
    """检查模板中所有占位符是否都能被填充。"""
    stripped = _strip_escaped_braces(template)
    placeholders = set(_PLACEHOLDER_RE.findall(stripped))
    missing = placeholders - set(kwargs.keys())
    if missing:
        raise ValueError(
            f"Missing prompt variables: {missing}. "
            f"Required: {placeholders}, provided: {set(kwargs.keys())}"
        )


def render_str(template: str, kwargs: Dict[str, Any]) -> str:
    """渲染单个字符串，缺变量则报错。支持 {{ / }} 转义为字面量花括号。"""
    check_missing(template, kwargs)
    result = _strip_escaped_braces(template)
    for key, value in kwargs.items():
        result = result.replace("{" + key + "}", str(value))
    return _restore_escaped_braces(result)


def render_content(
        content: Union[str, List[Union[str, Dict[str, Any]]], None],
        kwargs: Dict[str, Any],
) -> Union[str, List[Union[str, Dict[str, Any]]], None]:
    """渲染 ContentT，缺少变量时抛出 ValueError。"""
    if content is None:
        return None

    if isinstance(content, str):
        return render_str(content, kwargs)

    if isinstance(content, list):
        rendered: List[Union[str, Dict[str, Any]]] = []
        for item in content:
            if isinstance(item, str):
                rendered.append(render_str(item, kwargs))
            elif isinstance(item, dict):
                new_item = copy.deepcopy(item)
                if "text" in new_item and isinstance(new_item["text"], str):
                    new_item["text"] = render_str(new_item["text"], kwargs)
                rendered.append(new_item)
            else:
                rendered.append(item)
        return rendered

    return content
