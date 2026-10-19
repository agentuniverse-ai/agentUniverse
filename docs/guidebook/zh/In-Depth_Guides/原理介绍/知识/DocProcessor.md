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

### [SummarizationProcessor](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/summarization_processor.yaml)

该组件将召回的文档汇总压缩为一份摘要文档，减少多路召回后的冗余与噪声，对应 issue #248 中"摘要、总结"方向。

支持两种工作模式：

- **LLM 模式**：配置 `llm_name` 时，由指定的 agentUniverse LLM 组件生成抽象式摘要，质量最高，推荐生产环境使用。
- **抽取式模式**：`llm_name` 为空时，使用无依赖的纯算法兜底——对拼接后的文档按词频对句子打分（开启 query_aware 时还会用查询词加权），保留得分最高的若干句并保持原顺序。该模式确定性、可离线运行。

该组件定义文件如下：
```yaml
name: 'summarization_processor'
description: 'summarize recalled documents'
llm_name: ''              # 填入 LLM 组件名即启用 LLM 模式
max_input_docs: 10
max_sentences: 5
query_aware: true
summary_instruction: 'Summarize the following retrieved documents into a concise, coherent summary.'
language: ''              # 可选输出语言提示，如 'Chinese'
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.summarization_processor'
  class: 'SummarizationProcessor'
```
- llm_name: 用于抽象式摘要的 LLM 组件名。为空时使用确定性抽取式兜底。
- max_input_docs: 参与摘要的召回文档最大数量。
- max_sentences: 抽取式摘要保留的句子数量（LLM 模式下忽略）。
- query_aware: 是否让摘要向查询倾斜。抽取式模式下会提升含查询词句子的得分，LLM 模式下会让模型聚焦于查询。
- summary_instruction: 追加到 LLM 提示前的自定义指令（抽取式模式下忽略）。
- language: LLM 摘要的可选输出语言提示，如 `Chinese`（抽取式模式下忽略）。

该组件始终返回单个 Document，其 `text` 为摘要内容。其 `metadata` 记录工作模式（`summarization_mode`：`llm` 或 `extractive`）、参与摘要的源文档数（`source_doc_count`）以及使用的 `llm_name`。

### [MMRProcessor](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/mmr_processor.yaml)

该组件使用最大边际相关性（Maximal Marginal Relevance，MMR）对召回文档重排，在"与查询相关"和"彼此不重复"之间取得平衡，使结果既切题又无冗余。对应 issue #248 的*重排 / 多样性*方向。

MMR 每一步选择使 `lambda * sim(d, query) - (1 - lambda) * max_{已选} sim(d, 已选)` 最大的文档。`lambda_coef` 设为 `1.0` 即纯相关性排序、`0.0` 即最大化多样性、`0.5`（默认）为二者折中。它与 `SemanticDeduplicator`（按硬阈值删除近似重复）和 `ReciprocalRankFusionProcessor`（融合多路召回的排序列表）不同：MMR 是对单个召回集做"兼顾多样性的选择 / 重排"。

未设置 `embedding_name` 时，查询与文档向量取自 `Query.embeddings` 和 `Document.embedding`，且必须具有一致维度。设置 `embedding_name` 后，所有文档和查询向量都会用同一模型重新计算；查询必须提供 `query_str`，因为预计算查询向量的模型来源无法验证。若无法建立同一向量空间，则按输入顺序返回。

组件定义文件如下：
```yaml
name: 'mmr_processor'
description: '对召回文档做最大边际相关性重排'
lambda_coef: 0.5          # 1.0 = 仅相关性，0.0 = 最大化多样性
top_n: null               # 重排后保留的文档数量
embedding_name: ''        # 用于按需计算向量的注册 embedding 组件
score_key: ''             # 写入余弦相关性的 metadata 键，'' 表示不写入
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.mmr_processor'
  class: 'MMRProcessor'
```
- lambda_coef: 相关性/多样性权衡，取值 [0.0, 1.0]。
- top_n: 重排后保留的文档数量；`null` 表示保留全部，仅重排顺序。
- embedding_name: 用同一注册 embedding 组件重新计算所有文档和查询向量。为空时只使用查询/文档已携带的向量。
- score_key: 写入每个保留文档与查询余弦相关性的 metadata 键；为空则不写入（从而保留前置处理器如 RRF 写入的分数）。

### [SensitiveDataRedactor](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/sensitive_data_redactor.yaml)

该组件在召回文档**送入 LLM 之前**，对其中的常见个人敏感信息（PII）/敏感标识符进行脱敏，避免个人数据与密钥泄漏进模型上下文。对应 issue #248 的*隐私 / 合规*方向，且与其它文档处理器都不同（没有任何组件会出于隐私目的改写文本）。

检测过程确定、无额外依赖。内置实体先匹配结构化格式，并在仅靠格式不足时执行语义校验：信用卡号必须通过 Luhn 校验，IPv4 各段必须在合法范围内，中国居民身份证必须通过校验码，美国 SSN 必须满足 area/group/serial 规则。`email` 和常见 API Key 前缀采用格式校验；`phone` 可用但默认不开启（手机号匹配更模糊）。领域专属标识符可通过 `custom_patterns` 补充。

配置会在加载时严格校验。未知实体、格式错误的自定义项或非法正则会直接导致组件初始化失败，不会静默跳过而使脱敏失效。

每个匹配被替换为 `replacement`（默认 `[REDACTED]`）；每篇文档的 `redaction_summary` 会记录各类实体被脱敏的数量。

组件定义文件如下：
```yaml
name: 'sensitive_data_redactor'
description: '对召回文档做 PII 脱敏'
entities: [email, credit_card, id_card, ssn, ip_address, api_key]
replacement: '[REDACTED]'
custom_patterns: []      # 如 [{name: employee_id, pattern: '\bEMP-\d{6}\b'}]
log_key: 'redaction_summary'
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.sensitive_data_redactor'
  class: 'SensitiveDataRedactor'
```
- entities: 要脱敏的内置实体类型。加入 `phone` 可开启手机号脱敏。
- replacement: 替换每个匹配的文本。
- custom_patterns: 额外的 `{"name","pattern"}` 正则项，用于领域专属标识符；非法配置会导致组件初始化失败。
- log_key: 记录每篇文档 `{实体: 数量}` 汇总的 metadata 键；设为 null 则不写入。

### [ContextBudgetCompressor](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/context_budget_compressor.yaml)

该组件把召回文档装进一个固定的累积大小预算（通常是 LLM 上下文窗口）。它沿召回列表——已由 store 或前置 reranker / 融合处理器排好序——按顺序保留文档，只要累计大小不超过 `budget`；对那个会超出预算的边界文档，可选择截断，使结果在不超预算的前提下尽可能用满预算。对应 issue #248 的*上下文窗口管理*方向。

它与 `ThresholdFilter` 关注的维度不同：`ThresholdFilter` 做的是 per-document 谓词（分数/长度范围）或固定 top-k，而本组件管理的是保留集合的**累计**大小，并能把最后一个文档切分开来以恰好装下。

大小由 `counter` 计量：`estimate`（默认，`max(1, len(text)//4)`，无依赖的 token 近似）、`tiktoken`（经 tiktoken 的真实 BPE token）、`char` 或 `word`。预算始终以所选 counter 的单位解释，不会出现"名义上是 token、实际按词数算"的误导。

组件定义文件如下：
```yaml
name: 'context_budget_compressor'
description: '把召回文档装进累计大小预算'
budget: 4096                 # 最大累计大小，单位同 counter
counter: 'estimate'          # estimate | tiktoken | char | word
truncate: true               # 截断边界文档以装满预算
tiktoken_encoding: 'cl100k_base'
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.context_budget_compressor'
  class: 'ContextBudgetCompressor'
```
- budget: 保留文档的最大累计大小，单位同 `counter`。
- counter: 计量每个文档大小的方式：`estimate`（字符数/4，默认）、`tiktoken`（BPE token）、`char`、`word`。
- truncate: 为真时，第一个会超出预算的文档被截断到不超过剩余预算并作为最后一个结果保留；为假时遇到该文档即停止。使用 `tiktoken` 时，截断结果保持为原文前缀并重新校验 token 数；若剩余预算放不下完整字符，则不保留该文档。
- tiktoken_encoding: 当 `counter` 为 `tiktoken` 时使用的 tiktoken 编码。

### [QuoteAttributionAnalyzer](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/quote_attribution_analyzer.yaml)

该组件将直接引语与被归属的发言人配对，对应 issue #258 的*知识抽取*方向。新闻稿、访谈记录、电话会议与委员会报告中最可引用的知识都承载在引号里——但对知识库而言，原始引语只是事实的一半：`"We will not rest until every customer is refunded," said Alice Chen` 的价值恰恰在于承诺者是 *Alice Chen*。基于向量检索会抹平这层结构，本组件在入库前将其还原，把每对“引语/发言人”写入元数据，将 `CitationExtractor` 的扁平 `quote` 类型扩展为结构化的“谁说了什么”记录。组件为直通型：文档原样返回，不做过滤，text/id 不变，元数据先复制再写入。

引语识别支持四种样式——ASCII 双引号 `"..."`、弯双引号 `“...”`、CJK 直角引号 `「...」`、德语低高引号 `„...“`——均在单行内配对，引语不会跨段落泄漏；撇号与单引号刻意不作为界定符。文本被切分为句子（中文句末标点无需后随空格；`Dr.`/`Mr.`/首字母缩写点不切分），每条引语内部先被抹除以免引语自身触发模式，然后在包含该引语的句子中检索归属模式。多个模式命中时取距引语最近者；当引语位于句末且句内无命中时，检索延伸到下一句（模式须起始于下一句前 48 个字符内），从而恢复 `"We are disappointed." Alice Weber said in a note.` 这类写法。

归属模式：

| 语言 | 模式 | 示例 |
|---|---|---|
| 英文 | 动词（said/says/told/added/noted/claimed/stated）前的姓名串，保留 Dr./Mr./President 等头衔，小写虚词（`of`、`van`）粘合多词姓名，姓名与动词之间的逗号同位语被跳过 | `Alice Weber, the finance director, said "..."` → `Alice Weber` |
| 英文 | 动词后置 | `"..." said Alice Chen.` → `Alice Chen` |
| 英文 | `according to NAME` | `According to Bob Martinez, "..."` → `Bob Martinez` |
| 中/英 | 动词前代词（he/she/they；他/她/它/他们/她们） | `"..." she added` → 代词回溯 |
| 中文 | 表示/称/说/指出/认为 之前的汉字串（≤4 字，剥离前导虚字）；单字动词后须紧跟标点，故 称为/说明 不会误触 | `李娜表示：“……”` → `李娜` |
| 中文 | `据X报道` | `据新华社报道，“……”` → `新华社` |

代词回溯是文档化的启发式：he/she/they 本身不含姓名，组件在同一文档最近的 `speaker_lookback` 次归属事件（默认 2）中回溯并复用最近的具名发言人——即新闻写作中先行词通常满足的“发言人追踪”近似。回溯范围内没有具名先行词，或引语完全无模式命中，则 `speaker_resolved: unknown`。已知局限（如实说明）：归属是词法层面的而非句法层面的，重度改写的句子可能绕过全部模式；中文姓名串无分词，动词前的长修饰可能残留在姓名中；代词回溯不做性别与单复数校验。

每条记录形如 `{quote, speaker, speaker_resolved, attribution_text, span}`——`quote` 含引号标记，`speaker_resolved` 取 `'name'`、`'pronoun'`（经回溯解析）或 `'unknown'`，`attribution_text` 为命中的模式原文，`span` 为精确复现引语的 `(start, end)` 字符区间。记录按文档位置排序并截断至 `max_quotes` 条；`metadata['quote_count']` 始终记录真实总数以便察觉截断，`metadata['speakers']` 为按首次出现顺序排列的 `{speaker: 引语数}` 统计。整体流程纯标准库 `re` 实现，确定性、离线、无依赖。

组件定义文件如下：
```yaml
name: 'quote_attribution_analyzer'
description: 'pair direct quotes with their attributed speakers and stamp them into document metadata'
max_quotes: 50              # 保留的引语记录数；总数仍记录于 quote_count
speaker_lookback: 2         # 代词回溯检索的归属事件数
quotes_key: 'quotes'        # 记录列表的元数据键；'' 表示不写入
count_key: 'quote_count'    # 未截断总数的元数据键；'' 表示不写入
speakers_key: 'speakers'    # {发言人: 数量} 统计的元数据键；'' 表示不写入
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.quote_attribution_analyzer'
  class: 'QuoteAttributionAnalyzer'
```
- max_quotes: 写入 `metadata[quotes_key]` 的引语记录数上限；必须 >= 1。默认 50，限制引语密集文本的元数据膨胀。
- speaker_lookback: 解析 he/she/they 时向前检索（由近及远）的归属事件数；必须 >= 1。
- quotes_key: 引语记录列表的元数据键；空字符串表示不写入。
- count_key: 引语真实总数（未截断）的元数据键；空字符串表示不写入。
- speakers_key: 去重后 `{发言人: 引语数}` 统计的元数据键；空字符串表示不写入。
