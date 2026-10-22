# QueryParaphraser

QueryParaphraser负责对原始的Query进行加工处理，包括改写、拆分、提取关键词等，使得Query在Store中能召回更丰富且精准的内容。QueryParaphraser的输入和输出均为Query，因此query能经过多个QueryParaphraser叠加处理。

Query定义如下：
```python
from PIL.Image import Image
from typing import Optional, List, Set

from pydantic import BaseModel, Field


class Query(BaseModel):
    query_str: Optional[str] = None
    query_text_bundles: Optional[List[str]] = Field(default_factory=list)
    query_image_bundles: Optional[List[Image]] = Field(default_factory=list)
    keywords: Optional[Set[str]] = Field(default_factory=set)
    embeddings: List[List[float]] = Field(default_factory=list)
    ext_info: dict = {}
    similarity_top_k: Optional[int] = None
```
- query_str: 一个可选的字符串字段，用于存储原始查询的文本内容。
- query_text_bundles: 一个可选的字符串列表字段，用于存储多个改写后的查询文本片段。
- query_image_bundles: 一个可选的图像列表字段，用于存储多个查询图像。
- keywords: 一个可选的集合字段，用于存储查询的关键词。
- embeddings: 一个嵌入向量列表字段，用于存储查询的嵌入表示，用于相似度匹配。
- ext_info: 一个字典字段，用于存储与查询相关的额外信息，支持任意扩展。
- similarity_top_k: 一个可选的整数字段，用于指定相似度搜索中返回的最相似结果的数量。

QueryParaphraser定义如下：
```python
from abc import abstractmethod
from typing import Optional

from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.component.component_base import ComponentEnum
from agentuniverse.base.component.component_base import ComponentBase


class QueryParaphraser(ComponentBase):

    component_type: ComponentEnum = ComponentEnum.QUERY_PARAPHRASER
    name: Optional[str] = None
    description: Optional[str] = None

    @abstractmethod
    def query_paraphrase(self, origin_query: Query) -> Query:
        """Paraphrase the origin query string to different style."""
```
用户在自定义的QueryParaphraser子类中，需要重写`query_paraphrase`函数，函数的出入参均为Query形式。

在编写完对应代码后，可以参考下面的yaml将QueryParaphraser注册为aU组件：
```yaml
name: 'query_keyword_extractor'
description: 'extract keywords from query origin str'
metadata:
  type: 'QUERY_PARAPHRASER'
  module: 'agentuniverse.agent.action.knowledge.query_paraphraser.query_keyword_extractor'
  class: 'QueryKeywordExtractor'
```
其中metadata的type必须为QUERY_PARAPHRASER。
### 关注您定义的QueryParaphraser所在的包路径
在agentUniverse项目的config.toml中需要配置QueryParaphraser配置对应的package, 请再次确认您创建的文件所在的包路径是否在`CORE_PACKAGE`中`query_paraphraser`路径或其子路径下。

以示例工程中的配置为例，如下：
```yaml
[CORE_PACKAGE]
query_paraphraser = ['sample_standard_app.intelligence.agentic.knowledge.query_paraphraser']
```

## agentUniverse目前内置有以下QueryParaphraser:
### [query_keyword_extractor](../../../../../../agentuniverse/agent/action/knowledge/query_paraphraser/query_keyword_extractor.yaml)
该组件会根据Query中的原始文本提取关键词，并保存至Query的keywords字段
组件定义文件如下：
```yaml
name: 'query_keyword_extractor'
description: 'extract keywords from query origin str'
metadata:
  type: 'QUERY_PARAPHRASER'
  module: 'agentuniverse.agent.action.knowledge.query_paraphraser.query_keyword_extractor'
  class: 'QueryKeywordExtractor'
```

### [hyde_query_paraphraser](../../../../../../agentuniverse/agent/action/knowledge/query_paraphraser/hyde_query_paraphraser.yaml)
该组件实现 HyDE（Hypothetical Document Embeddings，假设性文档嵌入）查询改写：请一个已注册的 LLM 组件针对用户查询撰写一段或多段简短的*假设性段落*，并用它们改写 Query，使稠密检索去匹配"答案形态"的文本而非裸问题（弥合查询与文档之间的形态不对称）。

改写遵循框架的 Query 契约：`query_str` 被改写（`append` 模式 = 原始查询 + 假设段落，默认混合形态；`replace` 模式 = 仅保留假设段落，即经典 HyDE 形态）；每个段落同时追加进 `query_text_bundles`；未改动的原始查询与生成的段落分别记录在 `ext_info` 的 `hyde_origin_query_str` / `hyde_documents` 键下，供后续环节（融合、重排、日志）使用。

扩展按设计是"尽力而为"：查询为空、未配置 `llm_model`、LLM 调用失败或生成内容为空时，一律退化为原样透传并记录告警——检索绝不会因为*增强*失败而中断。配置错误则相反，会在组件加载时快速失败（未知 `mode`、`num_docs` 超出 [1, 5]、非正的 `max_doc_chars`、自定义 `prompt_template` 缺少字面量 `{query}` 占位符）。

生成是有界的：`num_docs`（1-5）个段落、每段一次 LLM 调用（单次失败不影响其余段落）、每段按 `max_doc_chars` 硬截断、重复段落自动去除。LLM 输出只被当作检索文本——不会被执行，也不会被解析为结构化数据。

组件定义文件如下：
```yaml
name: 'hyde_query_paraphraser'
description: '使用 LLM 生成假设性段落的 HyDE 查询改写'
llm_model: ''            # 已注册的 LLM 组件名，如 'default_openai_llm'
num_docs: 1              # 生成段落数，取值 [1, 5]
mode: 'append'           # append（原始查询+段落）| replace（经典 HyDE）
max_doc_chars: 2000      # 每段硬截断上限
origin_query_key: 'hyde_origin_query_str'
documents_key: 'hyde_documents'
metadata:
  type: 'QUERY_PARAPHRASER'
  module: 'agentuniverse.agent.action.knowledge.query_paraphraser.hyde_query_paraphraser'
  class: 'HyDEQueryParaphraser'
```
- llm_model: 用于生成假设性段落的已注册 LLM 组件名。为空时查询原样透传（并告警），因此内置定义无需任何模型凭据即可加载。
- num_docs: 生成的假设段落数量，取值 [1, 5]；每段一次 LLM 调用，重复段落自动去除。
- mode: `append`（默认）把 `query_str` 改写为"原始查询 + 假设段落"；`replace` 只保留假设段落（经典 HyDE 形态）。
- max_doc_chars: 每个段落在进入查询或嵌入模型前的硬截断上限。
- prompt_template: 自定义用户提示模板；必须包含字面量 `{query}` 占位符（通过 `str.replace` 替换，模板中其它花括号不受影响）。默认使用"以查询语言作答"的内置指令。
- origin_query_key / documents_key: 记录未改动原始查询与生成段落列表的 `ext_info` 键名。
