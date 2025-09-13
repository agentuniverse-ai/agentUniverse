# DocProcessor

DocProcessor负责对Document进行各种处理，如文本拆分、关键词提取等等。DocProcessor的输入输出均为List[Document]，这保证了多个DocProcessor可以叠加形成对Document的一个加工流。

Document定义如下：
```python
import uuid
from typing import Dict, Any, Optional, List, Set

from pydantic import BaseModel, Field, model_validator


class Document(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: str = None
    text: Optional[str] = ""
    metadata: Optional[Dict[str, Any]] = None
    embedding: List[float] = Field(default_factory=list)
    keywords: Set[str] = Field(default_factory=set)

    @model_validator(mode='before')
    def create_id(cls, values):
        text: str = values.get('text', '')
        if not values.get('id'):
            values['id'] = str(uuid.uuid5(uuid.NAMESPACE_URL, text))
        return values
```
- id：用于标识一段特定文档的唯一标识，默认通过uuid生成。
- text：文档中的文本内容
- metadata：文档的元数据信息，通常包含原始文件名、原始文件中的位置等。
- embedding：文档向量化后的形式，可以是文本向量，在Document的子类ImageDocument中，也可以是图像向量化后的结果。
- keywords：文档中的关键词，也可以是这段文本的tag。

DocProcessor定义如下：
```python
from abc import abstractmethod
from typing import List, Optional

from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase

class DocProcessor(ComponentBase):
    component_type: ComponentEnum = ComponentEnum.DOC_PROCESSOR
    name: Optional[str] = None
    description: Optional[str] = None

    def process_docs(self, origin_docs: List[Document], query: Query = None) -> \
            List[Document]:
        return self._process_docs(origin_docs, query)

    @abstractmethod
    def _process_docs(self, origin_docs: List[Document],
                      query: Query = None) -> \
            List[Document]:
        pass
```
用户在自定义的DocProcessor中主要完成对`_process_docs`函数的重写，实现具体的Document处理逻辑。

在编写完对应代码后，可以参考下面的yaml将你的DocProcessor注册为aU组件：
```yaml
name: 'dashscope_reranker'
description: 'reranker use dashscope api'
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.dashscope_reranker'
  class: 'DashscopeReranker'
```
其中metadata的type必须为DOC_PROCESSOR。

### 关注您定义的DocProcessor所在的包路径
在agentUniverse项目的config.toml中需要配置DocProcessor配置对应的package, 请再次确认您创建的文件所在的包路径是否在`CORE_PACKAGE`中`doc_processor`路径或其子路径下。

以示例工程中的配置为例，如下：
```yaml
[CORE_PACKAGE]
doc_processor = ['sample_standard_app.intelligence.agentic.knowledge.doc_processor']
```


## agentUniverse内置有以下DocProcessor:
### [CharacterTextSplitter](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/character_text_splitter.yaml)
该组件根据字符数对原始文本进行拆分。  
组件定义文件如下：
```yaml
name: 'character_text_splitter'
description: 'langchain character text splitter'
chunk_size: 200
chunk_overlap: 20
separators: "/n/n"
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.character_text_splitter'
  class: 'CharacterTextSplitter'
```
- chunk_size: 切分后文本长度大小。
- chunk_overlap: 相邻切分文本重合部分的长度。
- separators: 指定的分隔符

### [TokenTextSplitter](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/character_text_splitter.yaml)
该组件根据指定的 tokenizer 对文本进行切分，按照设定的 chunk_size 和 chunk_overlap 将文本拆分为多个片段，每个片段包含指定数量的tokens。

组件定义文件如下：

```yaml
name: 'token_text_splitter'
description: 'langchain token text splitter'
chunk_size: 200
chunk_overlap: 20
tokenizer: 'default_tokenizer'
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.token_text_splitter'
  class: 'TokenTextSplitter'
```
- chunk_size: 切分后文本的token数量。
- chunk_overlap: 相邻切分文本重合部分的token数量。
- tokenizer: 指定的tokenizer，用于将文本切分为tokens

### [RecursiveCharacterTextSplitter](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/recursive_character_text_splitter.yaml)

该组件根据指定的分隔符递归地对原始文本进行切分。它首先尝试使用优先级最高的分隔符进行切分，如果无法满足 chunk_size 的要求，则会递归地使用下一个分隔符进行切分，直到文本被成功分割。

组件定义文件如下：
```yaml
name: 'recursive_character_text_splitter'
description: 'langchain recursive character text splitter'
chunk_size: 200
chunk_overlap: 20
separators:
  - "\n\n"
  - "\n"
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.recursive_character_text_splitter'
  class: 'RecursiveCharacterTextSplitter'
```
- chunk_size: 切分后文本长度大小。
- chunk_overlap: 相邻切分文本重合部分的长度。
- separators: 指定的分隔符列表，按顺序尝试使用分隔符进行切分。如果第一个分隔符不能满足条件，则递归地使用下一个分隔符。

### [JiebaKeywordExtractor](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/jieba_keyword_extractor.yaml)
该组件使用结巴（Jieba）分词库从文本中提取关键词。它可以根据设定的 top_k 参数提取出最重要的几个关键词，用于后续作为倒排索引。  
组件定义文件如下：
```yaml
name: 'jieba_keyword_extractor'
description: 'extract keywords from text'
top_k: 3
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.jieba_keyword_extractor'
  class: 'JiebaKeywordExtractor'
```
- top_k: 从文本中提取的关键词数量，即排名前 top_k 的关键词会被提取。

### [DashscopeReranker](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/dashscope_reranker.yaml)

该组件使用 DashScope API 对文本进行重新排序（rerank），对Store召回的内容按照Query内容进行相关性排序。

组件定义文件如下：
```yaml
name: 'dashscope_reranker'
description: 'reranker use dashscope api'
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.dashscope_reranker'
  class: 'DashscopeReranker'
```
该组件需要在环境变量中配置`DASHSCOPE_API_KEY`。

### [HierarchicalRegexTextSplitter](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/hierarchical_regex_text_splitter.py)

该组件使用通过指定的正则规则对原始文本进行多层级的拆分，形成树状的文档结构。
该组件需要用户自行创建定义文件，一个示例定义文件如下：
```yaml
name: 'hierarchical_regex_text_splitter'
description: 'extract keywords from query'
merge_first: True
hierarchical_index:
  - "reg_exp": "第[零一二三四五六七八九十百千]+章"
    "need_summary": True
  - "reg_exp": "第[零一二三四五六七八九十百千]+条"
    "need_summary": False
summary_agent: "simple_summary_agent"
llm:
  name: qwen_llm
  model_name: qwen-plus
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.hierarchical_regex_text_splitter'
  class: 'HierarchicalRegexTextSplitter'
```
- merge_first: 设置为True的话会将输入的List[Document]合并为一份文档后再进行拆分
- hierarchical_index: 表示不同层级的拆分规则，`reg_exp`为正则表达式，`need_summary`为True的话则表示该层级会使用总结文本取代原始文本
- summary_agent: `hierarchical_index`中设置`need_summary`为True的时候生成总结文本的Agent， 默认为`simple_summary_agent`
- llm: 如指定的话，则会用指定的llm取代原本`summary_agent`中的llm。
