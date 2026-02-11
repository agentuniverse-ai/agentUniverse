# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/16 14:42
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: prompt_util.py
from typing import List

from agentuniverse.agent.memory.enum import ChatMessageEnum
from agentuniverse.agent.memory.message import Message
from agentuniverse.llm.llm import LLM
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt_manager import PromptManager
from agentuniverse.prompt.prompt_model import AgentPromptModel
from agentuniverse.prompt.enum import PromptProcessEnum


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
        formatted_prompt = summary_prompt.prompt_template.format(**prompt_variables)
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
        return result.message.content
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
            return prompt.prompt_template.format(**prompt_variables)
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


def generate_template(agent_prompt_model: AgentPromptModel, prompt_assemble_order: list[str]) -> str:
    """Convert the agent prompt model to an ordered list.

    Args:
        agent_prompt_model (AgentPromptModel): The agent prompt model.
        prompt_assemble_order (list[str]): The prompt assemble ordered list.
    Returns:
        list: The ordered list.
    """
    values = []
    for attr in prompt_assemble_order:
        value = getattr(agent_prompt_model, attr, None)
        if value is not None:
            values.append(value)

    return "\n".join(values)


def generate_chat_template(agent_prompt_model: AgentPromptModel, prompt_assemble_order: list[str]) -> list[Message]:
    """Convert the agent prompt model to the agentUniverse message list.

    Args:
        agent_prompt_model (AgentPromptModel): The agent prompt model.
        prompt_assemble_order (list[str]): The prompt assemble ordered list.
    Returns:
        list: The agentUniverse message list.
    """
    message_list = []
    for attr in prompt_assemble_order:
        value = getattr(agent_prompt_model, attr, None)
        if value is not None:
            message_list.append(
                Message(type=agent_prompt_model.get_message_type(attr), content=value))
    if message_list:
        # Integrate the system messages and put them in the first of the message list.
        system_messages = '\n'.join(msg.content for msg in message_list if msg.type == ChatMessageEnum.SYSTEM.value)
        if system_messages:
            message_list = list(filter(lambda msg: msg.type != ChatMessageEnum.SYSTEM.value, message_list))
            message_list.insert(0, Message(type=ChatMessageEnum.SYSTEM.value, content=system_messages))
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

    prompt = lc_prompt_template.format(**prompt_input_dict)
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
                                                                    summary_prompt=PromptManager().get_instance_obj(
                                                                        summary_prompt_version),
                                                                    combine_prompt=PromptManager().get_instance_obj(
                                                                        combine_prompt_version))
