# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/13
# @Author  : au-bot
# @FileName: summarize_processor.py

from typing import List, Optional

from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.prompt_util import (
    summarize_by_stuff,
    summarize_by_map_reduce,
)
from agentuniverse.llm.llm_manager import LLMManager
from agentuniverse.prompt.prompt_manager import PromptManager


class SummarizeDocs(DocProcessor):
    """对召回文档进行摘要/总结合成。

    支持两种模式：
    - stuff: 直接将文本喂入 LLM 摘要，适合文档较短的情况；
    - map_reduce: 先对分块做小结再合并，适合较长文本。
    """

    name: Optional[str] = "summarize_docs"
    description: Optional[str] = "Summarize retrieved documents"

    llm: str = "__default_instance__"
    mode: str = "stuff"  # "stuff" | "map_reduce"
    summary_prompt_version: str = "prompt_processor.summary_cn"
    combine_prompt_version: str = "prompt_processor.combine_cn"
    return_only_summary: bool = True
    summary_metadata_key: str = "is_summary"

    def _process_docs(self, origin_docs: List[Document], query: Query | None = None) -> List[Document]:
        if not origin_docs:
            return origin_docs

        llm = LLMManager().get_instance_obj(self.llm)
        texts = [d.text or "" for d in origin_docs if d.text]

        summary_prompt = PromptManager().get_instance_obj(self.summary_prompt_version)
        if self.mode == "map_reduce":
            combine_prompt = PromptManager().get_instance_obj(self.combine_prompt_version)
            summary_text = summarize_by_map_reduce(texts=texts, llm=llm, summary_prompt=summary_prompt,
                                                  combine_prompt=combine_prompt)
        else:
            summary_text = summarize_by_stuff(texts=texts, llm=llm, summary_prompt=summary_prompt)

        summary_doc = Document(text=str(summary_text), metadata={self.summary_metadata_key: True})
        if self.return_only_summary:
            return [summary_doc]
        return [summary_doc] + origin_docs

    def _initialize_by_component_configer(self, doc_processor_configer: ComponentConfiger) -> "DocProcessor":
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "llm"):
            self.llm = str(doc_processor_configer.llm)
        if hasattr(doc_processor_configer, "mode"):
            self.mode = str(doc_processor_configer.mode)
        if hasattr(doc_processor_configer, "summary_prompt_version"):
            self.summary_prompt_version = str(doc_processor_configer.summary_prompt_version)
        if hasattr(doc_processor_configer, "combine_prompt_version"):
            self.combine_prompt_version = str(doc_processor_configer.combine_prompt_version)
        if hasattr(doc_processor_configer, "return_only_summary"):
            self.return_only_summary = bool(doc_processor_configer.return_only_summary)
        if hasattr(doc_processor_configer, "summary_metadata_key"):
            self.summary_metadata_key = str(doc_processor_configer.summary_metadata_key)
        return self


