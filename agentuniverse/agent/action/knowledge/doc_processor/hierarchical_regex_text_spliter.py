# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/28 16:54
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: hierarchical_text_spliter.py
import re
import uuid
from typing import List, Optional

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.action.knowledge.doc_processor.doc_processor import \
    DocProcessor
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger


class HierarchicalRegexTextSplitter(DocProcessor):
    """Splits text into hierarchical structure based on regex patterns."""
    merge_first: bool = False
    hierarchical_index: List[dict] = [
        {
            "reg_exp": "第[零一二三四五六七八九十百千]+章",
            "need_summary": True
        },
        {
            "reg_exp": "第[零一二三四五六七八九十百千]+节",
            "need_summary": False
        }
    ]
    summary_agent: str = "simple_summary_agent"
    llm: Optional[dict] = None

    def _hierarchical_split_single_doc(self, doc: Document) -> List[Document]:
        """Splits a single document into hierarchical structure using regex patterns.
        
        Args:
            doc: Document to be split hierarchically.
            
        Returns:
            List of hierarchically structured documents.
        """
        hierarchy = {}
        levels = [(f"item_{i}", re.compile(index['reg_exp'])) for i, index in enumerate(self.hierarchical_index)]
        current_level = {level[0]: None for level in levels}
        current_level['root'] = None
        root = Document(
            text='',
            metadata={
                'hierarchical_parent': 'root'
            }
        )
        hierarchy['root'] = root

        last_inserted_id = 'root'

        # build hierarchical doc tree
        for line in doc.text.splitlines():
            line = line.strip()
            if not line:
                continue
            for level_name, pattern in levels:
                match = pattern.match(line)
                if match:
                    _ptr = levels.index((level_name, pattern))
                    parent_level = \
                        levels[_ptr - 1][0] if _ptr > 0 else 'root'
                    parent_id = current_level[parent_level].id if \
                        current_level[parent_level] else 'root'
                    # use uuid4 to generate a random id, because chapter name can always duplicate
                    node = Document(
                        id=str(uuid.uuid4()),
                        text=line,
                        metadata={
                            'hierarchical_parent': parent_id,
                            'hierarchical_info': match.group(0) if match else '',
                            'hierarchical_level': _ptr
                        }
                    )
                    hierarchy[node.id] = node
                    current_level[level_name] = node
                    last_inserted_id = node.id
                    break
            else:
                hierarchy[last_inserted_id].text += "\n" + line
            # Append text to the last inserted node's text and all its parent
            _inserted_id = hierarchy[last_inserted_id].metadata['hierarchical_parent']
            while _inserted_id != 'root':
                hierarchy[_inserted_id].text += "\n" + line
                _inserted_id = hierarchy[_inserted_id].metadata['hierarchical_parent']
        hierarchy.pop("root")
        hierarchical_docs = []

        # summary the text if docs hierarchical_level need summary
        for k, v in hierarchy.items():
            hierarchical_level = v.metadata['hierarchical_level']
            if self.hierarchical_index[hierarchical_level]['need_summary']:
                agent = AgentManager().get_instance_obj(self.summary_agent)
                if self.llm:
                    agent.agent_model.profile['llm_model'] = self.llm
                else:
                    agent.agent_model.profile['llm_model'] = {
                        "name": "__default_instance__"}
                agent_result = agent.run(input=v.text)
                v.text = agent_result.output
            hierarchical_docs.append(v)

        return hierarchical_docs

    def _process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        """Processes documents by splitting them into hierarchical structure.
        
        Args:
            origin_docs: List of documents to be processed.
            query: Optional query object (not used in this processor).
            
        Returns:
            List of hierarchically structured documents.
        """
        # merge all documents first
        merged_docs = origin_docs
        if self.merge_first and len(origin_docs) > 0:
            for _doc in origin_docs[1:]:
                origin_docs[0].text += "\n" + _doc.text
            merged_docs = [origin_docs[0]]
        hierarchical_docs = []
        for _doc in merged_docs:
            hierarchical_docs.extend(self._hierarchical_split_single_doc(_doc))
        return hierarchical_docs

    def _initialize_by_component_configer(self,
                                         doc_processor_configer: ComponentConfiger) -> 'DocProcessor':
        """Initializes the splitter with configuration parameters.
        
        Args:
            doc_processor_configer: Configuration object containing splitter parameters.
            
        Returns:
            Initialized document processor instance.
        """
        super()._initialize_by_component_configer(doc_processor_configer)
        if hasattr(doc_processor_configer, "hierarchical_index"):
            self.hierarchical_index = doc_processor_configer.hierarchical_index
        if hasattr(doc_processor_configer, "merge_first"):
            self.merge_first = doc_processor_configer.merge_first
        if hasattr(doc_processor_configer, "llm"):
            self.llm = doc_processor_configer.llm
        if hasattr(doc_processor_configer, "summary_agent"):
            self.summary_agent = doc_processor_configer.summary_agent
        return self

