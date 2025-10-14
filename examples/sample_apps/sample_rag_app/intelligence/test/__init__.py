# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/10/06 22:14
# @Author  : zhangxi
# @Email   : 1724585800@qq.com
# @FileName: __init__.py

from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.action.knowledge.knowledge_manager import KnowledgeManager


if __name__ == '__main__':
    AgentUniverse().start(config_path="../../config/config.toml", core_mode=True)
    disease_symptoms_store_list = ["disease_symptoms_sqlite_store", "disease_symptoms_chroma_store"]
    disease_therapy_one_store_list = ["disease_therapy_one_sqlite_store", "disease_therapy_one_chroma_store"]
    disease_therapy_two_store_list = ["disease_therapy_two_sqlite_store", "disease_therapy_two_chroma_store"]
    disease_knowledge = KnowledgeManager().get_instance_obj("disease_knowledge")
    disease_knowledge.insert_knowledge(
        source_path="../resources/常见疾病自然疗法介绍.docx",
        stores=disease_therapy_one_store_list
    )
    disease_knowledge.insert_knowledge(
        source_path="../resources/常见疾病及症状汇总.docx",
        stores=disease_symptoms_store_list
    )
    disease_knowledge.insert_knowledge(
        source_path="../resources/常见疾病药物推荐.docx",
        stores=disease_therapy_two_store_list
    )