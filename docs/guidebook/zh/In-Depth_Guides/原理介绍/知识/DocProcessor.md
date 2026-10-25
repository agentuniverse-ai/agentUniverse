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

标题层级由 `hierarchical_index` 的顺序决定。新标题会结束之前同级或更深层级的分支。
中间层级缺失时，标题挂到当前最近的较浅层标题下；不存在较浅层标题时，父节点为 `root`。
例如“第一章 → 第一节 → 第二章 → 子条款”中的子条款属于第二章，不会关联到第一章的第一节。
正文只累加到当前祖先节点及其摘要输入中，不会为缺失层级创建虚拟节点。

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
- truncate: 为真时，第一个会超出预算的文档被截断到不超过剩余预算并作为最后一个结果保留；为假时遇到该文档即停止。使用 `word` 时，截断保留已选词前方和词间的原始空白。使用 `tiktoken` 时，截断结果保持为原文前缀并重新校验 token 数；若剩余预算放不下完整字符，则不保留该文档。
- tiktoken_encoding: 当 `counter` 为 `tiktoken` 时使用的 tiktoken 编码。

### [CodeBlockDetector](../../../../../../agentuniverse/agent/action/knowledge/doc_processor/code_block_detector.yaml)

该组件定位围栏代码块并把行跨度与语言写入文档 metadata，对应 issue #258 的*预处理/分析*方向。以 Markdown 为主的语料——README 集合、设计文档、issue 归档、聊天记录——携带大量围栏代码块，而下游组件大多将其视为噪声：嵌入模型在其上耗费 token，关键词提取器会索引标识符，切分器则把代码块切成无意义的碎片。现有流水线组件只是自保（`OutlineExtractor` 与 `HeadingConsistencyChecker` 解析标题时跳过围栏内的行），没有一个真正编目代码的位置。本处理器为每篇文档按 CommonMark 规则扫描围栏代码块，把每个块的语言、行跨度、规模、缩进与闭合状态记录进 `metadata[code_blocks]`，后续阶段因此可以按块、按精确坐标决定在嵌入前遮蔽、绕开或丢弃哪些内容。

围栏识别遵循 CommonMark：起始行是最多缩进 3 个空格、其余部分以 3 个及以上连续反引号或波浪线开头的行，行内剩余部分是 info 字符串，取其第一个词（小写化）作为语言（缺省为空串；词仅以 ASCII 空格、制表符与回车分隔，其他 Unicode 空白属于词的一部分），反引号围栏的 info 字符串中不得再出现反引号。结束围栏必须是最多缩进 3 个空格、仅由同种围栏字符重复至少起始长度构成（围栏字符之后只允许空格、制表符与回车残留，不允许其他 Unicode 空白，也不允许 info 文本）的行——因此 3 个反引号不能闭合 4 个反引号的块，波浪线围栏永远不会闭合反引号围栏，形似嵌套的围栏只是外围块的内容。未闭合的围栏一直延伸到文档末尾，并以 `unclosed: true` 上报。一个有意的偏差：不执行 CommonMark 对 info 字符串的行内规范化（反斜杠转义与实体引用解析），直接上报原始第一个词。

写入 `metadata[code_blocks]` 的摘要包含：`blocks`（每块明细——`language`、覆盖围栏本身的 1 基闭区间 `span` `[首行, 末行]`、含围栏行的 `line_count`、`unclosed`、`indent`——最多保留 `max_blocks` 条），以及对*全部*检测块（含超出上限的部分）的聚合：`block_count`、`total_code_lines`、按计数降序再按语言名排序的 `languages` 直方图、`longest_block_lines` 与 `code_ratio`（代码行数除以总行数；行数按 `\n` 切分统计，因此末尾换行会产生一个空行）。`mask: true` 时每个块（含超出上限的）还会在文档文本中被替换为单行占位符 `⟦code:python:12⟧`（语言在前、行数在后）。占位符不含围栏字符，因此遮蔽是幂等的：第二遍扫描找不到任何围栏，文本保持不变。整个流程纯 Python、确定性和离线。

组件定义文件如下：
```yaml
name: 'code_block_detector'
description: 'locate fenced code blocks and stamp spans plus languages into document metadata'
mask: false                  # 同时把代码块替换为 ⟦code:<lang>:<lines>⟧ 占位符
max_blocks: 50               # 每块明细上限；聚合始终统计全部块
metadata_key: 'code_blocks'  # 摘要写入的 metadata 键；'' 表示不写入
metadata:
  type: 'DOC_PROCESSOR'
  module: 'agentuniverse.agent.action.knowledge.doc_processor.code_block_detector'
  class: 'CodeBlockDetector'
```
- mask：为真时，把每个检测到的块在文档文本中替换为 `⟦code:<lang>:<lines>⟧` 占位符行，下游嵌入或切分只看到正文。默认 false（仅检测，不改文本）。
- max_blocks：写入 metadata 的 `blocks` 明细列表最多保留的条目数，必须 >= 1。超出上限的块仍计入所有聚合统计。默认 50。
- metadata_key：摘要映射写入的 metadata 键；为空则不写入（适合只做遮蔽的流水线）。默认 `code_blocks`。
