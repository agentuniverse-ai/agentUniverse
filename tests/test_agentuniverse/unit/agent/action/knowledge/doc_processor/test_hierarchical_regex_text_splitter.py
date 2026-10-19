# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/08/02 10:00
# @Author  : Yue Wang
# @FileName: test_hierarchical_regex_text_splitter.py
"""Unit tests for HierarchicalRegexTextSplitter."""

from types import SimpleNamespace

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.\
    hierarchical_regex_text_splitter import HierarchicalRegexTextSplitter
import agentuniverse.agent.action.knowledge.doc_processor.\
    hierarchical_regex_text_splitter as splitter_module
from agentuniverse.agent.action.knowledge.store.document import Document

_NO_SUMMARY_INDEX = [
    {"reg_exp": "第[零一二三四五六七八九十百千]+章", "need_summary": False},
    {"reg_exp": "第[零一二三四五六七八九十百千]+节", "need_summary": False},
]

_SAMPLE = ("第一章 引言\n这是引言内容。\n第二章 方法\n第一节 数据\n数据内容\n"
           "第二节 处理\n处理内容\n")


class TestHierarchicalRegexTextSplitter:
    """Pure splitting logic, exercised without agents or app config."""

    @pytest.fixture
    def splitter(self):
        return HierarchicalRegexTextSplitter(
            hierarchical_index=_NO_SUMMARY_INDEX)

    def test_splits_chapters_and_sections(self, splitter):
        docs = splitter.process_docs([Document(text=_SAMPLE)])
        assert len(docs) == 4
        assert docs[0].text == "第一章 引言\n这是引言内容。"
        assert docs[1].text.startswith("第二章 方法")
        assert docs[2].text == "第一节 数据\n数据内容"
        assert docs[3].text == "第二节 处理\n处理内容"

    def test_metadata_links_sections_to_parent_chapter(self, splitter):
        docs = splitter.process_docs([Document(text=_SAMPLE)])
        chapter_ids = {d.id for d in docs
                       if d.metadata["hierarchical_level"] == 0}
        assert len(chapter_ids) == 2
        chapter2 = docs[1]
        assert chapter2.text.startswith("第二章 方法")
        assert "数据内容" in chapter2.text
        for doc in docs:
            if doc.metadata["hierarchical_level"] == 0:
                assert doc.metadata["hierarchical_parent"] == "root"
            else:
                assert doc.metadata["hierarchical_parent"] in chapter_ids
                assert doc.metadata["hierarchical_info"] in ("第一节", "第二节")

    def test_content_without_headers_yields_no_docs(self, splitter):
        for text in ("", "普通正文\n没有标题"):
            assert splitter.process_docs([Document(text=text)]) == []

    def test_merge_first_merges_documents_before_split(self):
        splitter = HierarchicalRegexTextSplitter(
            hierarchical_index=_NO_SUMMARY_INDEX, merge_first=True)
        docs = splitter.process_docs([Document(text="第一章 A\n内容a"),
                                      Document(text="第一章 B\n内容b")])
        assert [d.metadata["hierarchical_info"] for d in docs] == \
            ["第一章", "第一章"]
        assert docs[0].text == "第一章 A\n内容a"
        assert docs[1].text == "第一章 B\n内容b"

    def test_summary_level_replaces_text_via_agent(self, splitter, monkeypatch):
        agent_inputs = []

        class _FakeAgent:
            agent_model = SimpleNamespace(profile={})

            def run(self, input=None):
                agent_inputs.append(input)
                return SimpleNamespace(output="摘要结果")

        fake_agent = _FakeAgent()

        class _FakeAgentManager:
            def get_instance_obj(self, _name):
                return fake_agent

        monkeypatch.setattr(splitter_module, "AgentManager", _FakeAgentManager)
        splitter.hierarchical_index = [{"reg_exp": "第[零一二三四五六七八九十百千]+章",
                                        "need_summary": True}]
        docs = splitter.process_docs([Document(text=_SAMPLE)])
        assert [d.text for d in docs] == ["摘要结果", "摘要结果"]
        assert agent_inputs[0].startswith("第一章 引言")
        assert agent_inputs[1].startswith("第二章 方法")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
