# agentUniverse v0.1.0a1 — No More LangChain

> **彻底移除 LangChain 依赖，全面重构 LLM/Memory/Agent 核心链路，新增 Skill 技能系统。**

本次为架构级重构版本，涉及 **344 个文件变更，新增 20,800+ 行，删除 9,100+ 行**。

---

## Breaking Changes

### 1. 完全移除 LangChain 依赖
- 删除所有 `langchain_instance` 模块（`LangchainOpenAI`、`OpenAIStyleLangchainInstance`、`ClaudeLangchainInstance`、`OllamaLangchainInstance`、`WenxinLangchainInstance` 等）
- 删除 `LangChainTool` 工具基类及 `sql_langchain_tool`
- 删除 LLM Channel 中的 langchain 转换层（`default_channel_langchain_instance`、`ollama_channel_langchain_instance`）
- 删除 Memory 中的 `langchain_instance.py`
- LLM 的 `as_langchain()` 方法已移除，所有模型调用改为直接使用官方 SDK
- **pyproject.toml 中不再依赖 langchain 相关包，框架更轻量**

### 2. 废弃 Planner 计划组件
- 删除整个 `agent/plan/planner/` 目录，包括 ReactPlanner、PeerPlanner、RAGPlanner、WorkflowPlanner 等全部 Planner
- 删除 `planner_configer`
- **迁移方案**：使用 Agent Template（智能体模版）替代，对应关系见文档

---

## New Features

### 3. Skill 技能系统
全新的模块化能力扩展机制，将指令 + 工具打包为可复用的技能单元。
- 通过 `SKILL.md` 文件定义（YAML frontmatter + Markdown 指令）
- 支持 **inline 模式**（工具注入当前上下文）和 **fork 模式**（隔离子智能体执行）
- 支持 `allowed_tools`、`allowed_toolkits` 精细控制工具访问权限
- 内置 `LoadSkillTool` 实现运行时动态加载
- 内置 `SkillForkAgentTemplate` 支持 fork 模式下的隔离执行
- 示例：`algorithmic-art`（算法艺术生成）、`mcp-builder`（MCP 服务器开发指南）

### 4. AI Context（AgentContext）
全新的运行时状态容器，替代原有的上下文传递方式。
- 分层消息管理：system_message → few_shot → chat_history → current_messages
- 内置工具/知识/技能的自动解析与 schema 构建
- 多模态支持（图片 URL/Base64/本地文件、音频）
- 流式输出辅助方法（`stream_token` / `stream_final`）

### 5. 11 个新内置工具
| 工具 | 说明 |
|---|---|
| `WebSearchTool` | DuckDuckGo 搜索，支持域名过滤 |
| `WebFetchTool` | URL 抓取，HTML 自动转文本 |
| `DuckDuckGoSearchTool` | DuckDuckGo 搜索（支持 news backend） |
| `RunCommandTool` | Bash 命令执行（同步/异步） |
| `ViewFileTool` | 文件读取，支持行范围 |
| `WriteFileTool` | 文件写入/追加 |
| `EditTool` | 精确字符串替换 |
| `GlobTool` | Glob 模式文件搜索 |
| `GrepTool` | 正则内容搜索 |
| `SqlDatabaseTools` | SQL 查询/列表/结构查看（3 合 1） |
| `HumanInputTool` | 终端交互输入 |

### 6. HybridKnowledgeStore 混合知识存储
- 组合多个子 Store 统一管理
- CRUD 操作并行分发到所有子 Store
- 查询结果自动去重合并

### 7. HybridMemoryStorage 混合记忆存储
- 组合多个子 MemoryStorage 后端
- 写入并行分发，读取返回首个非空结果
- 适用于 向量 + KV 等多后端场景

### 8. Knowledge Tool（知识工具）
- Knowledge 组件可自动包装为 LLM function calling 工具
- 工具名以 `__knowledge_tool__` 为前缀
- 支持自定义 schema

---

## Enhancements

### 9. LLM 全面重构
- 所有内置 LLM（OpenAI、Claude、Ollama、Qwen、WenXin、Bedrock、Kimi、DeepSeek、GLM、BaiChuan、Gemini）改为直接调用官方 SDK
- 新增 `transfer_utils.py` 统一消息格式转换（au_messages_to_openai）
- LLM Channel 层重构，移除 langchain 中间层
- Bedrock LLM 大幅增强（+600 行）
- Claude LLM 大幅增强（+700 行）
- Ollama LLM 大幅增强（+300 行）

### 10. Memory 系统重构
- Memory 基类重写，不再依赖 langchain
- 新增 `RamMemoryStorage`（纯内存存储，适合开发/测试）
- `MemoryCompressor` 重构
- `Message` 类增强（+200 行），支持更丰富的消息结构
- Qdrant MemoryStorage 增强
- ES ConversationMemory 存储重构

### 11. Agent 核心重构
- Agent 基类重写（+500 行），移除 langchain 依赖
- 新增 `OpenAIProtocolTemplate` 增强
- 新增 `ContextualIterationAgentTemplate` 增强
- React Agent 模版重写，使用原生 tool calling
- React Prompt 更新（中英文）

### 12. Prompt 系统增强
- `prompt_util.py` 大幅扩展（+600 行）
- 多模态 prompt 处理支持
- `PromptModel` 增强（+200 行）
- `ChatPrompt` 增强

### 13. Tool 系统增强
- Tool 基类大幅增强（+400 行）
- MCP Tool / MCP Toolkit 改进
- MCP Session Manager 重构

### 14. Knowledge 系统增强
- Knowledge 基类重构（+450 行），支持异步操作
- DocProcessor 系列组件移除 langchain 依赖，改为原生实现
- 文本分割器（Character/Token/Recursive）全部原生重写
- Reranker（Dashscope/Jina）原生重写
- Markdown Reader 增强

---

## Bug Fixes
- 修复 MCP session 管理 bug
- 修复空参数工具调用问题
- 修复 OpenAI Style LLM api_base 配置 bug
- 修复工具结果多模态内容处理
- 修复 Instrument 追踪 bug
- 修复多个示例应用兼容性问题

---

## Docs
- 更新 30+ 文档文件，移除所有 LangChain 相关内容
- 新增 Skill 技能系统文档（中英文）
- 新增 11 个内置工具文档
- 新增 HybridKnowledgeStore / HybridMemoryStorage / KnowledgeTool 文档
- Planner 文档标记为废弃并提供迁移指南
- 更新中英文目录索引

---

## Migration Guide

**从旧版本迁移请注意：**

1. **移除 langchain 依赖**：如果你的自定义代码使用了 `as_langchain()` 方法或 langchain 相关 import，需要改为直接使用 LLM 的 `call()` / `acall()` 方法
2. **Planner → Agent Template**：将 Planner 配置迁移到对应的 Agent Template（如 `ReactPlanner` → `ReactAgentTemplate`）
3. **LangChainTool → Tool**：将 LangChain 工具迁移为原生 Tool 实现，重写 `execute` 方法
4. **pyproject.toml**：可以移除项目中的 `langchain`、`langchain-core`、`langchain-community` 等依赖
