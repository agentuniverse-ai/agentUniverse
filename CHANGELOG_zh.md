# 版本说明
**************************************
语言版本: [简体中文](CHANGELOG_zh.md) | [English](CHANGELOG.md)

本文件用于记录项目的版本更新历史。

## 版本号格式
版本号格式为 `主版本号.次版本号.修订号`，版本号递增规则如下：
- 主版本号：当你做了不兼容的 API 修改时，递增主版本号。
- 次版本号：当你做了向下兼容的功能性新增时，递增次版本号。
- 修订号：当你做了向下兼容的问题修正时，递增修订号。
- 详细说明请参考 [语义化版本 2.0.0](https://semver.org)

## 记录类型
Init - 项目初始化。
Added - 新增的功能。
Changed - 对现有功能的更改。
Deprecated - 即将废弃的功能。
Removed - 现版本中移除的功能。
Fixed - 任何错误修复。
Security - 补丁与安全改进。
Note - 对于版本的额外说明。

***************************************************

# 版本更新记录
## [0.0.18] - 2025-07-10
### Added
- 新增基于OTel协议的智能体应用可观测能力
制定aU智能体应用的观测标准，基于OTel(OpenTelemetry)协议，对智能体、模型、工具等关键组件的token消耗、耗时、成功率等核心指标以及调用链（trace）进行全面采集与观测，并适配 SigNoz、Jaeger、Prometheus 等主流观测框架，从而实现对智能体全生命周期的可观测性支持。

- 新增异步SLS日志Sink、Sender组件

### Fixed
- MCP服务调用Stdio模式下env参数支持用户配置透传

### Note
- 第三方包依赖变更（格式：原版本->新版本，只包含一个版本号为新引入）
  - openai ("1.13.3" -> "1.55.3")
  - opentelemetry-api ("^1.25.0")
  - opentelemetry-sdk ("^1.25.0")
  - opentelemetry-semantic-conventions (">=0.48b0")
  - opentelemetry-exporter-otlp-proto-http ("^1.25.0")
  - httpx ("0.27.2" -> ">=0.27.2")
  - jsonlines ("^4.0.0")
- 其他代码优化与文档更新

## [0.0.17] - 2025-05-22
### Added
- 新增MCP接入与发布能力
  - 通过该功能可快速接入MCPServer供智能体使用，亦可将aU中的工具/工具集合发布成为MCPServer对外服务
- 新增工具包ToolKit能力
  - 可对于一系列工具进行分类管理并供智能体配置使用
- 新增知识Reader与加工组件
  - 新增语雀文档加载组件
- 工具基类中新增async_execute方法，开放工具异步调用能力
- trace模块新增自定义插件扩展，支持自定义处理trace采集内容
- 新增千问3系列模型配置

### Changed
- Request上下文优化

### Deprecated
- ToolInput对象废弃  
工具入参ToolInput对象写法已不推荐(将在3个版本后废弃),可关注agentuniverse.agent.action.tool.common_tool最新推荐写法

### Note
- 新增第三方包依赖
  - mcp ("~=1.9.0")
  - opentracing (">=2.4.0,<3.0.0")
- 其他代码优化与文档更新

## [0.0.16] - 2025-04-17
### Added
- 新增工具插件
  - 新增基于opencv图像OCR能力的图片文字提取工具
  - 新增shell命令状态查询与执行工具
  - 新增通用文件读写工具
  - 新增Tavily智能搜索工具
- 新增知识Reader与加工组件
  - 新增飞书云文档加载组件
  - 新增通用代码加载组件
  - 新增基于AST(Abstract Syntax Tree)代码处理组件
- 新增llm模型通道配置能力，支持模型基于不同通道平台提供方进行切换,详情可见[文档](https://github.com/agentuniverse-ai/agentUniverse/blob/master/docs/guidebook/zh/In-Depth_Guides/%E5%8E%9F%E7%90%86%E4%BB%8B%E7%BB%8D/%E6%A8%A1%E5%9E%8B/%E6%A8%A1%E5%9E%8B%E9%80%9A%E9%81%93.md)
- 新增Google gemini 2.5 pro模型配置
- 支持aU智能体配置接入chatbox、CherryStudio客户端,详情可见[文档](https://github.com/agentuniverse-ai/agentUniverse/blob/master/docs/guidebook/zh/How-to/%E4%BD%BF%E7%94%A8chatbox%E7%AD%89%E5%B7%A5%E5%85%B7%E8%BF%9E%E6%8E%A5aU/%E5%A6%82%E4%BD%95%E4%BD%BF%E7%94%A8chatbox%E7%AD%89%E5%B7%A5%E5%85%B7%E8%BF%9E%E6%8E%A5agentUniverse.md)

### Note
- 部分依赖第三方包版本限制放开
  - tiktoken ('0.5.2' -> '<1.0.0')
  - pydantic ('~2.6.4' -> '^2.6.4')
- 基于Python3.10、3.11与3.12版本的主干回归通过
- 其他代码优化与文档更新

## [0.0.15] - 2025-03-03
### Added
- embedding组件新增  
  - 新增azure-openai embedding组件  
  - 新增gemini embedding组件  
  - 新增豆包embedding标准组件 
- 知识加载reader组件新增  
  - 新增基于bs4的网页读取组件
  - 新增基于OCR技术的图像加载组件
  - 新增csv格式表格加载组件
- 工具插件新增  
  - 新增Arxiv文献检索查询工具插件
  - 新增Jina AI智能搜索工具插件
- 新增reasoning类模型标准LLM输出解析器
- 新增agent、llm、tool相关日志采集标准logger
- 新增retry函数注解

### Changed  
- 项目配置体验优化，主要优化点如下
  - 项目配置支持全局PACKAGE路径替换，详情见样例工程config.toml文件PACKAGE_PATH_INFO参数部分
  - 支持用户自定义配置扩展与yaml函数扩展，详情见样例工程config.toml文件EXTENSION_MODULES参数部分
  - custom_key.toml.sample更新，提供更详细与全面的参数内容
  - 内置一批常用模型配置yaml，详情见样例工程llm目录
  - yaml配置支持用户使用环境变量与扩展函数自定义加载对应属性，详情见样例工程llm样例中api_key注释说明部分
  - llm配置简化，默认读取全局default_llm配置，详情见样例工程llm样例default_llm.toml配置内容
  - 组件扩展配置简化，组件metadata中module部分可不填写，默认寻找同层级同名py扩展文件
- 项目启动流程优化，主要优化点如下
  - LLM组件启动注册优化，只启动用户在agent、tool等组件中依赖启动的LLM实例
  - 项目启动报错提示优化
- 其他变更
  - 内存记忆存储对象LocalMemoryStorage更名RamMemoryStorage

### Note 
- 新增应用工程image_build镜像打包文件与教程文档
- 新增项目贡献者开发文档
- 规范项目PR与ISSUE模版
- 新增基于模型多模态能力的agent样例实践，详情见项目examples/multimodal_app
- 项目于2月收录于deepseek发布的awesome-deepseek-integration榜单

## [0.0.14] - 2025-01-26
### Added
- aU记忆机制全面改版升级  
新版aU记忆通过全局记忆模块为多智能体应用提供全面的记忆管理和使用能力，它能够自动采集、记录和处理多智能体之间的对话、模型调用、工具调用、知识检索等记忆过程。同时，还为单智能体与多智能体提供记忆新增、记忆检索、记忆修改、记忆压缩、记忆裁剪、记忆提取以及记忆多源持久化等功能。

- 新增智能体模版(AgentTemplate)与工作模式(WorkPattern)组件    
智能体模板(AgentTemplate)组件帮助用户快速根据已经沉淀的模版搭建智能体，工作模式组件帮助智能体组快速选择复用特定的智能体协作方式。在V0.0.13之前的版本中，计划（Planner）组件承载了智能体的定制逻辑与工作模式，智能体的定制逻辑经常会因为实际任务需求被修改，而工作模式是验证有效稳定的，用户往往需要复写Planner并关注工作模式的代码逻辑，这大大增加了用户的使用与研发成本。通过本次改版我们将智能体构建中的定制逻辑与工作模式分层，这将使协同模式研究与智能体构建过程更加聚焦与高效。原有的计划（Planner）组件仍将会保留，但不再被推荐。

- 部分知识组件新增与优化   
新增组件：markdown格式知识加载组件、文档章节段落切分组件、图谱知识存储组件(beta版)

### Changed
- 标准脚手架工程结构改版  
脚手架工程结构规范化，您可阅读 [「标准应用工程结构说明」](./docs/guidebook/zh/开始使用/1.标准应用工程结构说明.md) 了解详情。对于旧版本的用户我们为这次改版提供了一些指南说明与工具，详情可阅读 [「aU新老工程迁移指南」](./docs/guidebook/zh/开始使用/6.aU新老工程迁移指南.md)。

### Note 
- 新增aU新版记忆机制文档介绍   
通过[「aU记忆机制介绍」](./docs/guidebook/zh/开始使用/1.标准应用工程结构说明.md)与[「新版记忆使用说明」](./docs/guidebook/zh/How-to/定义与使用全局记忆/如何使用全局记忆.md)文档了解本次版本更新内容。
- 官方文档与实践案例优化改版
- 高优feature公布与征集

## [0.0.13] - 2024-09-12
### Added
- RAG检索增强能力组件版本更新  
本版本提供知识库构建、RAG检索召回环节标准作业流程，组件覆盖数据加载、数据处理、索引构建、知识入库、意图改写、检索重排等一系列RAG原子能力，帮助用户在开源场景下快速构建通用RAG智能体方案。

- 智能体产品化平台更新  
本版本新增支持智能体画布编排、私有知识库构建、自定义插件等能力，通过低代码、可视化的方式帮助用户快速构建与编排智能体。

- 新增智谱GLM默认模型组件
- 新增SQLiteStore存储组件
- 新增flow编排执行引擎

### Note 
- system_db_uri默认路径优化  
默认路径已兼容windows平台，详情见[issue142](https://github.com/agentuniverse-ai/agentUniverse/issues/142)
- ReactAgent支持链停止词配置化  
ReactAgent yaml配置目前已经支持stop_sequence关键词，用户可以自行配置链停止词,详情见[issue127](https://github.com/agentuniverse-ai/agentUniverse/issues/127)
- 新增RAG原理介绍与RAG快速构建指导文档，请关注README与用户指南相应部分。
- 新增智能体产品化平台高阶指导文档，请关注README与用户指南相应部分。
- 部分代码优化与文档更新

## [0.0.12] - 2024-08-14
### Added
- agentUniverse产品化版本提供
  - 当前版本提供智能体构建、修改、调试等基础能力，由difizen项目联合推出，更多详情请见文档产品化平台部分。
- monitor组件新增对于知识、工具实例采集，支持全链路trace时序串联并提供token消耗监控
- 新增web会话模块，提供session与message持久化管理能力

### Note
- 优化知识组件，可由用户配置指定任意召回结果数量（similarity_top_k）
- 修复chroma组件未指定embedding模块出现异常
- 其他部分代码优化与文档更新

## [0.0.11] - 2024-07-11
### Added
- DataAgent数据自治智能体MVP版本发布
  - Minimum Viable Product版本，DataAgent旨在使用智能体能力让您的Agent拥有自我评价与演进的能力，详细内容请查阅用户文档。
- 增加PEER、ReAct模式中间信息流式输出能力

### Note
- PEER最新研究成果发布
  - 该文献详细介绍了PEER多智能体框架的机制原理，同时在实验部分通过验证证明了PEER模式的先进性，详细内容请查阅用户文档。
- 新增使用案例
  - 吴恩达反思工作流翻译智能体复刻
- 部分代码优化与文档更新

## [0.0.10] - 2024-06-28
### Added
- LLM组件新增DeepSeek模型标准接入
- 新增OpenAI通用协议包装类OpenAIStyleLLM
  - openai协议类模型接入可直接配置
- 新增LangChain工具包装类LangChainTool，新增搜索类、执行类示例工具若干
  - LangChain工具接入可直接配置
- monitor模块新增Agent纬度信息采集能力

### Note
- 新增使用案例
  - PEER协同模式的金融事件分析案例文档补充
- 新增若干LLM组件、工具组件、Monitor模块文档
- 新版README更新
- 部分代码优化与文档更新

## [0.0.9] - 2024-06-14
### Added
- LLM组件新增claude、ollama标准接入
- 新增qwen embedding模块
- 新增ReAct、nl2api默认agent

### Note
- 新增使用案例
  - RAG类Agent案例-法律咨询Agent
  - ReAct类Agent案例-Python代码生成与执行Agent
  - 多智能体案例-基于多轮多Agent的讨论小组

  详情请看用户文档案例部分。
- 部分代码优化与文档更新

## [0.0.8] - 2024-06-06
### Added
- 新增monitor模块
  - 任何agentUniverse运行时的数据可以被采集与观测
- 新增webserver post_fork功能
  - 开放agentUniverse中webserver启动后的多节点流程干预功能
- 新增SQLDB_WRAPPER包装类，提供典型数据库连接方式
  - 通过SQLDB_WRAPPER包装类您可以非常方便的连接如SQLServer、MySQL、Oracle、PostgreSQL、SQLite等几十种数据库与存储技术组件。
- 新增milvus向量数据库组件连接

上述功能更多用法请关注agentUniverse指导手册部分。

### Changed
- 全平台以flask作为默认webserver启动方式，gunicorn与GRPC能力置为默认关闭
  - 我们在上个版本中发现不同的操作系统对于gunicorn与GRPC的兼容性会有略微差异，我们将flask作为全平台的第一启动方式，您可以按需在配置中开启gunicorn与GRPC。

### Security
- 部分aU依赖第三方包识别到安全漏洞，出于安全考虑我们对其进行版本升级，主要包含如下变动：
  - requests (^2.31.0 -> ^2.32.0)
  - flask (^2.2 -> ^2.3.2)
  - werkzeug (^2.2.2 -> ^3.0.3)
  - langchain (0.0.352 -> 0.1.20)
  - langchain-core (0.1.3 -> 0.1.52)
  - langchain-community (no version lock -> 0.0.38)
  - gunicorn (21.2.0 -> ^22.0.0)
  - Jinja2 (no version lock -> ^3.1.4)
  - tqdm (no version lock -> ^4.66.3)
若您的系统存在外部访问，强烈建议您安装v0.0.8版本的aU以规避这些三方包的安全风险，更详细的说明您可以关注https://security.snyk.io。

### Note
- 部分代码优化与文档更新

## [0.0.7] - 2024-05-29
### Added
- LLM组件支持多模态参数调用
- 新增通义千问、文心一言、Kimi、百川等常用LLM接入方式

### Note 
- 添加多模态样例agent调用详情见`sample_standard_app.intelligence.test.test_multimodal_agent.MultimodalAgentTest`
- 部分代码优化与文档更新

## [0.0.6] - 2024-05-15
### Added
- 支持gpt-4o模型, 并更新相关样例
- 支持RPC组件gGpc，并提供标准服务启动方法

### Note 
- 提供标准的aU Docker镜像与K8S部署方案，详情见指导手册
- 部分代码优化与文档更新

## [0.0.5] - 2024-05-08
### Added
- LLM组件支持流式调用
- 知识组件添加update定义

### Fixed
- 修复peer planner中可能存在的并发安全性隐患
- 修复0.0.4版本中pypi package打包方式导致启动强制要求用户填写AK问题

### Note 
- 追加部分代码优化与文档更新

## [0.0.4] - 2024-04-26
### Added
- 新增prompt版本管理能力

### Fixed
- Windows版本下的兼容问题修复
  * 由于Gunicore对于windows系统的兼容问题，自动识别内核版本自动选择web启动方式
  * yaml读取指定为utf-8 encode方式
### Note 
- [2024-05-08] 注意，0.0.4的pypi package版本中默认包含了sample_standard_app示例工程, 这将会在启动时引用sample_standard_app中的额外组件,并要求用户填写AK, 若您没有使用对应组件可以通过mock ak跳过这一限制, 这已经在0.0.5版本中修复。

## [0.0.3] - 2024-04-19
### Init
- agentUniverse正式外发版本初始化,祝您使用愉快！

## [0.0.2] - 2024-04-17
### Fixed
- 修复安装包版本时无法自动安装关联依赖包问题。 

## [0.0.1] - 2024-04-09
### Init
- 项目初始化提交,本框架是一个大模型多智能体框架,祝您使用愉快！