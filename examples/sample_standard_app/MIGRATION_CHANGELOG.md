# sample_standard_app 迁移变更记录 (No More LangChain)

本文档记录了 `sample_standard_app` 脚手架工程从旧版（依赖 LangChain）迁移到新版（移除 LangChain）的所有变更，可供其他 LLM 参照修改旧工程。

---

## 一、总体变更概述

`No_more_langchain` 分支移除了框架中所有 LangChain 依赖。核心变化：

| 维度 | 旧版（LangChain） | 新版（原生实现） |
|------|-------------------|-----------------|
| **LLM 调用** | `llm.as_langchain_runnable(params)` | `llm.call(messages=...)` 返回 `LLMOutput` |
| **Prompt 渲染** | `prompt.as_langchain()` | `ChatPrompt.render(**kwargs)` 返回 `List[Message]` |
| **链式调用** | `prompt \| llm \| StrOutputParser()` + `invoke_chain()` | `invoke_llm(llm, messages, input_object)` 直接调用 |
| **Planner 系统** | `agent/plan/planner/` 整个子系统 | 已删除，不再存在 |
| **Memory** | LangChain Memory 封装 | 原生实现 |
| **Tool 实现** | 部分依赖 `langchain_community` 工具包装 | 使用 `httpx`/`subprocess` 等原生 Python 实现 |
| **输出解析** | `StrOutputParser` / `ReasoningOutputParser` | 直接使用 `llm_output.text` |

---

## 二、sample_standard_app 中具体变更的文件

### 2.1 `intelligence/agentic/agent/agent_instance/demo_agent.py`

**变更类型：** 重写（移除 LangChain 链式调用模式）

#### 删除的 import

```python
# 以下全部删除
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.prompt_util import process_llm_token
from agentuniverse.base.util.reasoning_output_parse import ReasoningOutputParser
from agentuniverse.prompt.prompt import Prompt
from langchain_core.output_parsers import StrOutputParser
```

#### 新增的 import

```python
from agentuniverse.prompt.chat_prompt import ChatPrompt
```

#### 关键代码变更

**旧代码 — execute() 方法：**
```python
def execute(self, input_object, agent_input):
    memory = self.process_memory(agent_input)
    llm = self.process_llm()
    prompt: Prompt = self.process_prompt(agent_input)
    tool_res = self.invoke_tools(input_object)
    knowledge_res = self.invoke_knowledge(agent_input.get('input'), input_object)
    agent_input['background'] = agent_input['background'] + f"tool_res: {tool_res} \n\n knowledge_res: {knowledge_res}"
    return self.customized_execute(input_object, agent_input, memory, llm, prompt)
```

**旧代码 — customized_execute() 方法：**
```python
def customized_execute(self, input_object, agent_input, memory, llm, prompt, **kwargs):
    assemble_memory_input(memory, agent_input)
    process_llm_token(llm, prompt.as_langchain(), self.agent_model.profile, agent_input)
    chain = prompt.as_langchain() | llm.as_langchain_runnable(
        self.agent_model.llm_params()) | ReasoningOutputParser()
    res = self.invoke_chain(chain, agent_input, input_object, **kwargs)
    assemble_memory_output(memory=memory, agent_input=agent_input,
                           content=f"Human: {agent_input.get('input')}, AI: {res}")
    return {**agent_input, 'output': res}
```

**新代码 — execute() 方法（合并了原 customized_execute 的逻辑）：**
```python
def execute(self, input_object, agent_input):
    memory = self.process_memory(agent_input)
    llm = self.process_llm()
    prompt: ChatPrompt = self.process_prompt(agent_input)  # 类型改为 ChatPrompt
    agent_context = self._create_agent_context(input_object, agent_input, memory)  # 创建 AgentContext
    tool_res = self.invoke_tools(input_object)
    knowledge_res = self.invoke_knowledge(agent_input.get('input'), input_object)
    agent_input['background'] = agent_input['background'] + f"tool_res: {tool_res} \n\n knowledge_res: {knowledge_res}"

    assemble_memory_input(memory, agent_input)

    messages = prompt.render(**agent_input)                 # 替代 prompt.as_langchain()
    llm_output = self.invoke_llm(llm, messages, input_object, agent_context=agent_context)  # 必须传 agent_context
    res = llm_output.text                                   # 替代 StrOutputParser / ReasoningOutputParser

    assemble_memory_output(memory=memory, agent_input=agent_input,
                           content=f"Human: {agent_input.get('input')}, AI: {res}")
    return {**agent_input, 'output': res}
```

**变更要点总结：**

1. `Prompt` → `ChatPrompt`
2. `prompt.as_langchain()` → `prompt.render(**agent_input)` — 返回 `List[Message]`
3. `llm.as_langchain_runnable()` → 不再需要
4. `chain = prompt | llm | Parser()` + `invoke_chain()` → `self.invoke_llm(llm, messages, input_object, agent_context=agent_context)`
5. `ReasoningOutputParser()` / `StrOutputParser()` → `llm_output.text`
6. `process_llm_token()` → 删除该调用（新版 LLM 层自行处理 token 限制）
7. 删除了 `customized_execute()` 方法，逻辑合并到 `execute()` 中
8. **必须创建 `agent_context`** — 调用 `self._create_agent_context(input_object, agent_input, memory)`，并传给 `invoke_llm()`，否则 LLM 开启 streaming 时会因 `agent_context` 为 None 导致 `AttributeError`

---

### 2.2 `intelligence/agentic/tool/custom/demo_search_tool.py`

**变更类型：** 重写（用原生 HTTP 调用替代 LangChain 工具封装）

#### 删除的 import

```python
from agentuniverse.agent.action.tool.tool import Tool, ToolInput  # ToolInput 不再引用
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
```

#### 新增的 import

```python
import httpx
from agentuniverse.agent.action.tool.tool import Tool  # 仅引入 Tool
```

#### 关键代码变更

**旧代码：**
```python
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper

class DemoSearchTool(Tool):
    serper_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SERPER_API_KEY"))

    def execute(self, input: str):
        search_api = GoogleSerperAPIWrapper(serper_api_key=self.serper_api_key, k=10, gl="us", hl="en", type="search")
        res = search_api.run(query=input)
        return res
```

**新代码：**
```python
import httpx

SERPER_API_URL = "https://google.serper.dev/search"

class DemoSearchTool(Tool):
    serper_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SERPER_API_KEY"))

    def _build_request(self, query: str) -> tuple:
        headers = {"X-API-KEY": self.serper_api_key, "Content-Type": "application/json"}
        payload = {"q": query, "num": 10, "gl": "us", "hl": "en"}
        return headers, payload

    def _parse_results(self, response_json: dict) -> str:
        snippets = []
        if "answerBox" in response_json:
            box = response_json["answerBox"]
            answer = box.get("answer") or box.get("snippet") or box.get("snippetHighlighted")
            if answer:
                snippets.append(str(answer))
        if "knowledgeGraph" in response_json:
            kg = response_json["knowledgeGraph"]
            title = kg.get("title", "")
            description = kg.get("description", "")
            if title:
                snippets.append(f"{title}: {description}")
        for result in response_json.get("organic", []):
            snippet = result.get("snippet")
            if snippet:
                snippets.append(snippet)
        if not snippets:
            return "No good Google Search Result was found"
        return "\n\n".join(snippets)

    def execute(self, input: str):
        headers, payload = self._build_request(input)
        response = httpx.post(SERPER_API_URL, headers=headers, json=payload, timeout=20)
        response.raise_for_status()
        return self._parse_results(response.json())
```

**变更要点总结：**

1. `GoogleSerperAPIWrapper` → 使用 `httpx.post()` 直接调用 Google Serper REST API
2. 新增 `_build_request()` 方法构建请求头和 payload
3. 新增 `_parse_results()` 方法解析 API 返回的 JSON（支持 answerBox、knowledgeGraph、organic 三种结果类型）
4. `ToolInput` 不再需要引入

---

### 2.3 内置工具 YAML 文件变更（已在之前的提交中完成）

以下 5 个 buildin 工具 YAML 文件已在分支早期提交中更新，module/class 指向了新的原生实现：

| YAML 文件 | 旧 module | 新 module |
|-----------|-----------|-----------|
| `duckduckgo_search.yaml` | `langchain_community...` | `agentuniverse.agent.action.tool.common_tool.duckduckgo_search_tool.DuckDuckGoSearchTool` |
| `human_input_run.yaml` | `langchain...` | `agentuniverse.agent.action.tool.common_tool.human_input_tool.HumanInputTool` |
| `info_sql_database_tool.yaml` | `langchain...sql_langchain_tool` | `agentuniverse.agent.action.tool.common_tool.sql_database_tool.InfoSqlDbTool` |
| `list_sql_database_tool.yaml` | `langchain...sql_langchain_tool` | `agentuniverse.agent.action.tool.common_tool.sql_database_tool.ListSqlDbTool` |
| `query_sql_database_tool.yaml` | `langchain...sql_langchain_tool` | `agentuniverse.agent.action.tool.common_tool.sql_database_tool.QuerySqlDbTool` |

以下 buildin 工具 YAML **无需变更**（它们引用的 module 原本就是 agentUniverse 自有实现）：

- `google_search_tool.yaml` → `agentuniverse.agent.action.tool.common_tool.google_search_tool.GoogleSearchTool`
- `python_repl_tool.yaml` → `agentuniverse.agent.action.tool.common_tool.python_repl.PythonREPLTool`
- `wikipedia_query.yaml` → `agentuniverse.agent.action.tool.common_tool.wikipedia_query.WikipediaTool`
- `arxiv_tool.yaml` → `agentuniverse.agent.action.tool.common_tool.arxiv_tool.ArxivTool`
- `youtube_tool.yaml` → `agentuniverse.agent.action.tool.common_tool.youtube_tool.YouTubeTool`
- `request_get_tool.yaml` / `request_post_tool.yaml` → `agentuniverse.agent.action.tool.common_tool.request_tool.RequestTool`
- `jina_ai_tool.yaml` → `agentuniverse.agent.action.tool.common_tool.jina_ai_tool.JinaAITool`
- `add/sub/mul/div_simple_tool.yaml` → `agentuniverse.agent.action.tool.common_tool.simple_math_tool.*`

---

## 三、框架层面的关键 API 变更参考

以下是其他旧工程迁移时需要对照的框架 API 变更：

### 3.1 Import 替换速查表

| 旧 import | 新 import / 处理方式 |
|-----------|---------------------|
| `from langchain_core.output_parsers import StrOutputParser` | **删除** — 用 `llm_output.text` 替代 |
| `from langchain_core.utils.json import parse_json_markdown` | `from agentuniverse.base.util.common_util import parse_json_markdown` |
| `from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper` | **删除** — 用 `httpx` 直接调 Serper API |
| `from langchain_community.utilities import PythonREPL` | **删除** — 用 `subprocess` 原生执行 |
| `from langchain_text_splitters import RecursiveCharacterTextSplitter` | **删除** — 自行实现文本切分 |
| `from langchain_core.runnables import RunnableSerializable` | **删除** |
| `from agentuniverse.base.util.prompt_util import process_llm_token` | **删除调用**（函数仍存在但需要 langchain 参数） |
| `from agentuniverse.base.util.reasoning_output_parse import ReasoningOutputParser` | **删除** — 文件已删除 |
| `from agentuniverse.prompt.prompt import Prompt` | `from agentuniverse.prompt.chat_prompt import ChatPrompt` |

### 3.2 核心 API 调用方式对照

| 旧 API | 新 API |
|--------|--------|
| `prompt.as_langchain()` | `prompt.render(**kwargs)` → 返回 `List[Message]` |
| `llm.as_langchain_runnable(params)` | `llm.call(messages=messages)` → 返回 `LLMOutput` |
| `chain = prompt \| llm \| StrOutputParser()` | 不再需要链式构造 |
| `self.invoke_chain(chain, agent_input, input_object)` | `self.invoke_llm(llm, messages, input_object)` |
| `res = chain_result` (字符串) | `res = llm_output.text` |
| `process_llm_token(llm, prompt.as_langchain(), ...)` | 删除该调用 |

### 3.3 Agent 模板方法签名变更

**旧签名：**
```python
def customized_execute(self, input_object, agent_input, memory, llm, prompt, **kwargs):
```

**新签名（如果使用 AgentTemplate 基类）：**
```python
def customized_execute(self, input_object, agent_input, memory, llm, agent_context=None, **kwargs):
```

关键变化：`prompt: Prompt` 参数被 `agent_context: AgentContext` 替代。

### 3.4 Agent 执行新模式

**模式 A — 简单 Agent（无需自定义逻辑）：**
不重写 `customized_execute()`，默认 `AgentTemplate` 通过 `AgentContext` 自动处理一切。
只需重写：`input_keys()` / `output_keys()` / `parse_input()` / `parse_result()`

**模式 B — 自定义 Prompt 逻辑的 Agent：**
```python
def customized_execute(self, input_object, agent_input, memory, llm, agent_context=None, **kwargs):
    prompt: ChatPrompt = self.process_prompt(agent_input)
    messages = prompt.render(**agent_input)
    llm_output = self.invoke_llm(llm, messages, input_object, agent_context=agent_context)
    return {'output': llm_output.text}
```

**模式 C — 直接在 execute() 中处理（如本工程 demo_agent.py）：**

### 3.5 工具迁移模式

**模式 A — LangChain 工具包装 → httpx 原生 HTTP 调用：**
适用于 Google Search、Bing Search 等 API 工具。用 `httpx.post()` / `httpx.get()` 直接请求 API。

**模式 B — LangChain PythonREPL → subprocess 原生执行：**
```python
import subprocess, sys, tempfile

def _run_code(code: str) -> str:
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=True) as f:
        f.write(code)
        f.flush()
        result = subprocess.run([sys.executable, f.name], capture_output=True, text=True, timeout=30)
        output = result.stdout
        if result.returncode != 0:
            output += result.stderr
        return output.strip()
```

**模式 C — LangChain SQL 工具 → SQLAlchemy 原生实现：**
新的 `sql_database_tool.py` 提供了 `QuerySqlDbTool`、`ListSqlDbTool`、`InfoSqlDbTool`，直接使用 SQLAlchemy。

---

## 四、框架层面已删除的模块

以下模块在新版中已**完全删除**，旧工程中如有引用需要清理：

| 已删除模块 | 说明 |
|-----------|------|
| `agentuniverse/agent/plan/` | 整个 planner 子系统（含 peer_planner, react_planner, rag_planner 等） |
| `agentuniverse/llm/langchain_instance.py` | LangChain LLM 实例封装 |
| `agentuniverse/llm/openai_style_langchain_instance.py` | OpenAI 风格 LangChain 实例 |
| `agentuniverse/llm/claude_langchain_instance.py` | Claude LangChain 实例 |
| `agentuniverse/llm/ollama_langchain_instance.py` | Ollama LangChain 实例 |
| `agentuniverse/llm/wenxin_langchain_instance.py` | 文心 LangChain 实例 |
| `agentuniverse/llm/llm_channel/langchain_instance/` | LLM Channel 的 LangChain 实例目录 |
| `agentuniverse/agent/memory/langchain_instance.py` | Memory 的 LangChain 实例 |
| `agentuniverse/agent/action/tool/common_tool/langchain_tool.py` | LangChain 工具封装 |
| `agentuniverse/agent/action/tool/common_tool/sql_langchain_tool.py` | SQL LangChain 工具 |
| `agentuniverse/base/util/reasoning_output_parse.py` | ReasoningOutputParser（基于 LangChain） |
| `agentuniverse/base/config/component_configer/configers/planner_configer.py` | Planner 配置器 |
| `agentuniverse/agent/template/slave_rag_agent_template.py` | Slave RAG Agent 模板 |

---

## 五、框架层面新增的模块

| 新增模块 | 说明 |
|---------|------|
| `agentuniverse/ai_context/agent_context.py` | Agent 运行时上下文容器，管理消息构建和 LLM 配置 |
| `agentuniverse/ai_context/tool_utils.py` | 工具调用相关辅助函数 |
| `agentuniverse/ai_context/utils.py` | 通用辅助函数 |
| `agentuniverse/llm/transfer_utils.py` | LLM 转换工具函数 |
| `agentuniverse/agent/action/tool/common_tool/duckduckgo_search_tool.py` | DuckDuckGo 搜索原生实现 |
| `agentuniverse/agent/action/tool/common_tool/human_input_tool.py` | 人工输入工具原生实现 |
| `agentuniverse/agent/action/tool/common_tool/sql_database_tool.py` | SQL 数据库工具原生实现 |
| `agentuniverse/agent/action/knowledge/store/hybrid_store.py` | 混合知识存储 |
| `agentuniverse/agent/memory/memory_storage/hybrid_memory_storage.py` | 混合记忆存储 |
| `agentuniverse/agent/memory/memory_storage/legacy_hybrid_memory_storage.py` | 兼容旧版混合记忆存储 |
| `agentuniverse/agent/memory/memory_storage/ram_memory_storage.py` | 内存记忆存储 |

---

## 六、config.toml 变更说明

`config.toml` 中的 `planner = [...]` 配置项现在会被忽略（planner 系统已删除），保留或删除均可，不影响运行。

---

## 七、YAML 配置无需变更的部分

以下类型的 YAML 配置文件在此次迁移中 **不需要修改**：

- Agent YAML 配置（`demo_agent.yaml` 等）
- LLM YAML 配置（所有 buildin LLM 配置）
- Memory YAML 配置（`demo_memory.yaml`、存储配置等）
- Prompt YAML 配置（`cn_v1.yaml`、`cn_v2.yaml` 等）
- Knowledge YAML 配置
- Service YAML 配置
- Toolkit YAML 配置

---

## 八、迁移检查清单

对旧工程进行迁移时，按以下步骤逐一检查：

- [ ] 全局搜索 `langchain` 关键字，清理所有 langchain 相关 import
- [ ] 将 `prompt.as_langchain()` 替换为 `prompt.render(**kwargs)`
- [ ] 将 `Prompt` 类型标注替换为 `ChatPrompt`
- [ ] 将 `llm.as_langchain_runnable()` 替换为 `llm.call(messages=...)`
- [ ] 将 `invoke_chain(chain, ...)` 替换为 `invoke_llm(llm, messages, input_object)`
- [ ] 将 `StrOutputParser()` / `ReasoningOutputParser()` 替换为 `llm_output.text`
- [ ] 删除 `process_llm_token()` 调用
- [ ] 检查自定义 Tool 是否使用了 `GoogleSerperAPIWrapper` 等 LangChain 工具，替换为 `httpx` 原生调用
- [ ] 检查 buildin 工具 YAML 的 module/class 是否指向了新的原生实现
- [ ] 检查是否引用了已删除的模块（见第四节）
- [ ] 验证 `config.toml` 中是否有 planner 相关配置（可选清理）
