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

### [multi_query_paraphraser](../../../../../../agentuniverse/agent/action/knowledge/query_paraphraser/multi_query_paraphraser.yaml)
该组件实现多查询扩展（multi-query expansion）：单次 LLM 调用为原始问题生成多个*同义改写*（意图不变、措辞多样），并用它们改写 Query，使稠密检索也能覆盖语料中用不同措辞表达同一意图的段落。它是 HyDE 类扩展（生成"答案形态"段落）在提问侧的对应物，两者可以在 `query_paraphrasers` 链中自然叠加。

改写遵循框架的 Query 契约：所有改写变体追加进 `query_text_bundles`；`query_str` 被改写（`append` 模式 = 原始查询 + 变体，默认；`replace` 模式 = 仅保留变体）；未改动的原始查询与最终变体列表分别记录在 `ext_info` 的 `multi_query_origin_query_str` / `multi_query_variants` 键下，供后续环节（融合、重排、日志）使用。

输出解析容忍常见的 LLM 装饰（`1.` / `1)` / `1、` 编号、`-`/`*`/`•` 项目符号、成对包裹引号），会跳过空行、与原始查询相同的变体（空白折叠后大小写不敏感比较）以及重复项，并把结果截断到 `num_queries` 个、每个变体截断到 `max_query_chars` 字符。

扩展按设计是"尽力而为"：查询为空、未配置 `llm_model`、LLM 调用失败或输出中没有任何可用变体时，一律退化为原样透传并记录告警——检索绝不会因为增强失败而中断。配置错误则相反，会在组件加载时快速失败（未知 `mode`、`num_queries` 超出 [1, 10]、非正的 `max_query_chars`、自定义 `prompt_template` 缺少字面量 `{query}` 占位符）。

组件定义文件如下：
```yaml
name: 'multi_query_paraphraser'
description: '使用 LLM 生成的同义改写扩展查询'
llm_model: ''            # 已注册的 LLM 组件名，如 'default_openai_llm'
num_queries: 3           # 保留的变体数，取值 [1, 10]；单次 LLM 调用
mode: 'append'           # append（原始查询+变体）| replace（仅变体）
max_query_chars: 512     # 每个变体的硬截断上限
origin_query_key: 'multi_query_origin_query_str'
variants_key: 'multi_query_variants'
metadata:
  type: 'QUERY_PARAPHRASER'
  module: 'agentuniverse.agent.action.knowledge.query_paraphraser.multi_query_paraphraser'
  class: 'MultiQueryParaphraser'
```
- llm_model: 用于生成改写变体的已注册 LLM 组件名。为空时查询原样透传（并告警），因此内置定义无需任何模型凭据即可加载。
- num_queries: 保留的变体数量上限，取值 [1, 10]；单次调用即向 LLM 请求该数量。
- mode: `append`（默认）把 `query_str` 改写为"原始查询 + 变体"；`replace` 只保留变体。
- max_query_chars: 每个变体的硬截断上限。
- prompt_template: 自定义用户提示模板；必须包含字面量 `{query}` 占位符，可包含 `{num}`（先替换 `{num}`，其它花括号不受影响）。默认使用"以查询语言作答"的内置指令。
- origin_query_key / variants_key: 记录未改动原始查询与最终变体列表的 `ext_info` 键名。