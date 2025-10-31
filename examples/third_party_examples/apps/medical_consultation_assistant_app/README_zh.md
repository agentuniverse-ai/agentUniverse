# 医疗咨询助手

本案例基于RagAgentTemplate，搭建了一个简单的医疗咨询智能体，通过检索《常见疾病药物推荐》《常见疾病自然疗法介绍》《常见疾病及症状汇总》中的相关信息并结合用户提供的身体症状的描述合理推断用户的疾病类型并给出相应的自然治疗方案和药物治疗方案。

该案例基于Deepseek大模型和DashScope的embedding和rerank功能，使用前需要您在环境变量中配置DASHSCOPE_API_KEY。

## 快速开始
### 配置API密钥
比如在agentUniverse管理私有密钥配置的文件custom_key.toml中配置密钥信息（讨论组默认使用deepseek作为基座模型，serper作为google search工具，下文讲述其他模型或工具使用方法）
```toml
[KEY_LIST]
# serper google search key
SERPER_API_KEY='xxx'
# deepseek api key
DEEPSEEK_API_KEY='xxx'
```
### 构建疾病知识库
疾病知识库基于agentUniverse中的知识组件，通过将常见疾病的症状及治疗方案存储至ChromaDB和Sqlite中，构建方便智能体查阅检索的知识库。

常见疾病的症状及治疗方案资料：
- 常见疾病及症状汇总.docx
- 常见疾病自然疗法介绍.docx
- 常见疾病药物推荐.docx

disease_knowledge定义如下:
```python
name: "disease_knowledge"
description: "常见疾病症状与治疗方法相关的知识库"
stores:
    - "disease_symptoms_chroma_store"
    - "disease_therapy_one_chroma_store"
    - "disease_therapy_two_chroma_store"
    - "disease_symptoms_sqlite_store"
    - "disease_therapy_one_sqlite_store"
    - "disease_therapy_two_sqlite_store"
query_paraphrasers:
    - "custom_query_keyword_extractor"
insert_processors:
    - "recursive_character_text_splitter"
rag_router: "nlu_rag_router"
post_processors:
    - "dashscope_reranker"
readers:
    docx: "default_docx_reader"
metadata:
  type: 'KNOWLEDGE'
  module: 'medical_consultation_assistant_app.intelligence.agentic.knowledge.disease_knowledge'
  class: 'DiseaseKnowledge'
```

### 运行代码
在agentUniverse的examples/sample_apps/sample_rag_app示例工程中，找到intelligence/test目录下的legal_advice_rag_agent.py文件，chat方法中输入想要解答的问题，运行即可。

例如，输入问题"小明最近出现了发热表现，伴有畏寒现象，精神状态萎靡，注意力难以集中，时常感到头晕目眩，整个人呈现出明显的虚弱状态，请推测小明的疾病类型，并为其推荐治疗方法和药物推荐"
```python
from agentuniverse.agent.output_object import OutputObject
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('disease_rag_agent')
    output_object: OutputObject = instance.run(input=question)

    question = f"\nYour event is :\n"
    question += output_object.get_data('input')
    print(question)

    background_info = f"\nRetrieved background is :\n"
    background_info += output_object.get_data('background').replace("\n","")
    print(background_info)

    res_info = f"\nRag chat bot execution result is :\n"
    res_info += output_object.get_data('output')
    print(res_info)


if name == '__main__':
    chat("小明最近出现了发热表现，伴有畏寒现象，精神状态萎靡，注意力难以集中，时常感到头晕目眩，"
         "整个人呈现出明显的虚弱状态，请推测小明的疾病类型，并为其推荐治疗方法和药物推荐")
```
### 效果演示
问题"小明最近出现了发热表现，伴有畏寒现象，精神状态萎靡，注意力难以集中，时常感到头晕目眩，整个人呈现出明显的虚弱状态，请推测小明的疾病类型，并为其推荐治疗方法和药物推荐":

![演示图片](../../_picture/result_show.png)

## 更多细节
### Reader组件
- [default_docx_reader](../../../../agentuniverse/agent/action/knowledge/reader/file/docx_reader.yaml)

### DocProcessor组件
- [custom_query_keyword_extractor](../../../../examples/sample_apps/rag_app/intelligence/agentic/knowledge/doc_processor/query_keyword_extractor.yaml)
- [recursive_character_text_splitter](../../../../agentuniverse/agent/action/knowledge/doc_processor/recursive_character_text_splitter.yaml)

### QueryParaphraser组件
- [custom_query_keyword_extractor](../../../../examples/sample_apps/rag_app/intelligence/agentic/knowledge/query_paraphraser/custom_query_keyword_extractor.yaml)

### RagRouter组件
- [nlu_rag_router](../../../../examples/sample_apps/rag_app/intelligence/agentic/knowledge/rag_router/nlu_rag_router.yaml)

### Store组件
- [disease_symptoms_chroma_store](../../../../examples/sample_apps/rag_app/intelligence/agentic/knowledge/store/disease_symptoms_chroma_store.yaml)
- [disease_therapy_one_chroma_store](../../../../examples/sample_apps/rag_app/intelligence/agentic/knowledge/store/disease_therapy_one_chroma_store.yaml)
- [disease_therapy_two_chroma_store](../../../../examples/sample_apps/rag_app/intelligence/agentic/knowledge/store/disease_therapy_two_chroma_store.yaml)
- [disease_symptoms_sqlite_store](../../../../examples/sample_apps/rag_app/intelligence/agentic/knowledge/store/disease_symptoms_sqlite_store.yaml)
- [disease_therapy_one_sqlite_store](../../../../examples/sample_apps/rag_app/intelligence/agentic/knowledge/store/disease_therapy_one_sqlite_store.yaml)
- [disease_therapy_two_sqlite_store](../../../../examples/sample_apps/rag_app/intelligence/agentic/knowledge/store/disease_therapy_two_sqlite_store.yaml)

为了方便您使用，我们已经将存储有相关信息的数据库文件存储如下图：
![演示图片](../../_picture/db_structure.png)

如果您想从头构建知识库的话，您可以运行test文件夹下的__init__.py文件，代码如下：
![演示图片](../../_picture/init_code.png)