# Changelog
**************************************
Language Version: [简体中文](CHANGELOG_zh.md) | [English](CHANGELOG.md)

This document records the version update history of the project.

## Version Number Format
The format of the version number is MAJOR.MINOR.PATCH, and the version number increment rule is as follows:
- MAJOR version when you make incompatible API changes,
- MINOR version when you add functionality in a backwards compatible manner,
- PATCH version when you make backwards compatible bug fixes.
- For more details, please refer to [Semantic Versioning 2.0.0](https://semver.org)

## Record Types
Init - Project initialization.
Added - Newly added features.
Changed - Changes to existing functionalities.
Deprecated - Soon to be deprecated features.
Removed - Features removed in this version.
Fixed - Any bug fixes.
Security - Patches and security improvements.
Note - Additional remarks regarding the version.

***************************************************

# Version Update History
## [0.0.19] - 2025-11-17
### Added
- Added AWS Bedrock model support
- Added ollama embedding component support
- Added jina rerank component support
- Added vector database component support
  - Faiss vector database support
  - Qdrant vector database support
- Added a batch of new Reader data loading components
  - Added Notion, GoogleDoc, Confluence cloud document loading components
  - Added file format support for epub, rar, sevenzip, zip, xlsx
  - Added text extraction components for images and PDF files based on PaddleOCR
  - Added web page loading components based on playwright and bs4
- Added GitHub and YouTube retrieval tools
- Added async safe exit method for McpSessionManager
- Added model Token consumption recording in the Otel-llm-instrumentor module

### Fixed
- Fixed parameter naming error in the RecursiveCharacterTextSplitter component's splitter method
- Fixed missing connection_kwargs parameter propagation in MCPToolkit
- Fixed abnormal queue release issue when tasks exited exceptionally in RequestTask

### Note
- Improved security for the SlsSender module's put method
- Enhanced robustness of loop event handling in logging_util
- Optimized reliability of the add_invocation_chain method in the Monitor module
- Included some third-party community examples and tools
- Performed additional code optimizations and documentation updates

## [0.0.18] - 2025-07-10
### Added
- Added observability capabilities for agent applications based on the OTel protocol
Established observation standards for aU agent applications based on OTel (OpenTelemetry) protocol. Comprehensive metrics and traces (including token consumption, latency, success rate, etc.) are collected across key components such as agents, LLMs, and tools. The implementation supports integration with mainstream observability frameworks including SigNoz, Jaeger, and Prometheus, enabling full lifecycle observability for agents.

- Added async Sink and Sender components for SLS Logger

### Fixed
- MCP service in Stdio mode now supports user-configurable environment parameter

### Note
- Third-party package dependency changes (Format: old version -> new version; single version means new)
  - openai ("1.13.3" -> "1.55.3")
  - opentelemetry-api ("^1.25.0")
  - opentelemetry-sdk ("^1.25.0")
  - opentelemetry-semantic-conventions (">=0.48b0")
  - opentelemetry-exporter-otlp-proto-http ("^1.25.0")
  - httpx ("0.27.2" -> ">=0.27.2")
  - jsonlines ("^4.0.0")
- Other code optimizations and documentation updates

## [0.0.17] - 2025-05-22
### Added
- MCP Integration & Publishing Capabilities   
Enables rapid integration with MCPServer for agent, and allows publishing tools/toolkits from aU as MCPServer services
- Toolkit Capabilities   
Supports categorized management of tools and configuration for agent
- Knowledge Reader Components  
  - Added Yuque document loading component
- Added async_execute method to base tool class, enabling asynchronous tool invocation
- Added custom plugin extensions for trace collection processing
- Added configurations for the complete Qwen3 series model

### Changed
- Request Context Optimizations

### Deprecated
- ToolInput Object  
The use of ToolInput object for tool parameters is deprecated (will be removed in 3 versions). See agentuniverse.agent.action.tool.common_tool for updated recommendations

### Note
- New Third-Party Dependencies
  - mcp ("~=1.9.0")
  - opentracing (">=2.4.0,<3.0.0")
- Other code optimizations and documentation updates

## [0.0.16] - 2025-04-17
### Added
- New Tool Plugins
  - Added image text extraction tool based on OpenCV's OCR capabilities
  - Added Shell command status query and execution tool
  - Added universal file read/write tool
  - Added Tavily intelligent search tool
- Knowledge Reader and Processing Components
  - Added Feishu cloud document loader component
  - Added universal code loader component
  - Added code processing component based on AST (Abstract Syntax Tree)
- Support LLM model channel configuration, supporting model switching across different channel platform providers.
- Added Google Gemini 2.5 Pro model configuration.
- aU Agent supports integration with chatbox and CherryStudio clients. For details, refer to the [documentation](https://github.com/agentuniverse-ai/agentUniverse/blob/master/docs/guidebook/en/In-Depth_Guides/Tutorials/LLM/LLM_Channel.md).

### Note
- Change version constraints for third-party dependencies:
  - tiktoken ('0.5.2' -> '<1.0.0')
  - pydantic ('~2.6.4' -> '^2.6.4')
- Main branch regression tests passed for Python 3.10, 3.11, and 3.12
- Other code optimizations and documentation updates

## [0.0.15] - 2025-03-03
### Added
- New embedding components  
  - Azure-OpenAI embedding component
  - Gemini embedding component
  - Doubao embedding component
- New knowledge loading reader components
  - Web page reader component based on BeautifulSoup (bs4)
  - Image reader component based on OCR technology
  - CSV format reader component
- New tool plugins
  - Arxiv paper retrieval and query tool plugin
  - Jina AI intelligent search tool plugin
- Added standard LLM output parser for reasoning-type models
- Added standard logger sink for agents, LLMs, and tools
- Added retry function annotation

### Changed  
- Improved project configuration experience, with the following key optimizations:
  - Project configuration now supports global PACKAGE path replacement. For details, see the PACKAGE_PATH_INFO parameter in the sample project's config.toml file.
  - Supports user-defined configuration extensions and YAML function extensions. For details, see the EXTENSION_MODULES parameter in the sample project's config.toml file.
  - Updated custom_key.toml.sample with more detailed parameter content.
  - Submit a set of commonly used model configuration YAML files. For details, see the llm directory in the sample project.
  - YAML configuration now supports user-defined loading of attributes using environment variables and extension functions. For details, see the api_key comments in the llm sample of the sample project.
  - Simplified LLM configuration. By default, it reads the global default_llm configuration. For details, see the default_llm.toml configuration in the llm sample of the sample project.
  - Simplified component extension configuration. The module part in the component metadata can be left blank, and it will default to searching for a Python extension file with the same name in the same directory.
- Optimized project startup process, with the following key improvements:
  - Improved LLM component startup registration. Only LLM instances that are dependent on by components like agents and tools are started.
  - Enhanced error info during project startup.
- Other changes:
  - Renamed LocalMemoryStorage to RamMemoryStorage for memory storage objects.

### Note 
- Added image_build image packaging files and tutorial documents for application projects.
- Added CONTRIBUTING.md documentation for the project.
- Standardized PR and ISSUE templates for the project.
- Added a sample practice for agents based on multimodal capabilities. For details, see the examples/multimodal_app directory in the project.
- Our project was included in the awesome-deepseek-integration list released by DeepSeek in February.

## [0.0.14] - 2025-01-26
### Added
- aU Memory Component Version Update   
The new version provides comprehensive memory management and utilization capabilities for multi-agent applications through a global memory module. It can automatically collect, record, and process memory interactions among multiple agents, including conversations, model calls, tool calls, and knowledge retrieval. Additionally, it offers functionalities such as memory addition, memory retrieval, memory modification, memory compression, memory pruning, memory extraction, and multi-source persistence for both single-agent and multi-agent.

- Add AgentTemplate Component and WorkPattern Component    
The AgentTemplate component helps users rapidly create agents according to pre-defined templates, while the WorkPattern component assists agent teams in selecting specific collaboration methods. In versions prior to V0.0.13, the Planner component offered both the customization logic of intelligent agents and their work patterns. The customization logic for agents was often modified due to the task, whereas work patterns were validated and stability. Consequently, users frequently needed to rewrite the Planner and focus on the code logic related to work patterns, which significantly increased their usage and development costs. With the new version, we have layered the customization logic and work patterns in the agent-building process. It will make the research on collaboration modes and the construction of intelligent agents more focused and efficient. The original Planner component will still be retained, but it will no longer be recommended.

- Knowledge Components Update   
Add: Markdown format knowledge loading component, document chapter and paragraph segmentation component, knowledge graph storage component (beta version).

### Changed
- Standard Project Scaffolding Update   
The scaffolding Project Scaffolding has been standardized. You can read the [「Application Project Structure and Explanation」](./docs/guidebook/en/Get_Start/1.Application_Project_Structure_and_Explanation.md)  for more details. For users of older versions, we have provided some guidelines and tools for this update, detailed information can be found in [「aU Old and New Project Migration Guide」](./docs/guidebook/en/Get_Start/6.aU_Old_and_New_Project_Migration_Guide.md).

### Note 
- Update docs for new memory version
- Optimization official docs and examples project
- Ask for high-priority features

# [0.0.13] - 2024-09-12
### Added
- RAG(Retrieval-Augmented Generation) Component Version Update  
This version provides a standard operating procedure for knowledge base construction and the RAG retrieval recall stage. The component covers a series of RAG atomic capabilities, including data loading, data processing, index construction, knowledge storage, intent rewriting, and retrieval re-ranking, helping users to quickly build a general RAG intelligent agent solution in open-source scenarios.

- Intelligent Agent Product Platform Update  
This version introduces new capabilities such as intelligent agent canvas orchestration, private knowledge base construction, and custom plugin support, enabling users to quickly build and orchestrate intelligent agents through a low-code, visual approach.

- Added GLM Default Model Component for Zhipu
- Added SQLiteStore Storage Component
- Added Flow Orchestration Execution Engine

### Note 
- Default path optimization for system_db_uri
The default path is already compatible with the Windows platform, for more details, please refer to [issue142](https://github.com/antgroup/agentUniverse/issues/142)
- Support for configurable chain stop words in ReactAgent
The ReactAgent YAML configuration now supports the stop_sequence keyword, allowing users to customize chain stop words. For more details, please refer to [issue127](https://github.com/antgroup/agentUniverse/issues/127)
- Added an introduction to RAG principles and a quick guide for building RAG, please pay attention to the corresponding parts in the README and user guide.
- Added advanced guidance documents for the intelligent agent productization platform, please pay attention to the corresponding parts in the README and user guide.
- Various code optimizations and documentation updates.

## [0.0.12] - 2024-08-14
### Added
- agentUniverse Product Version Offering
  - The current version provides basic capabilities for agent construction, modification, and debugging, jointly launched by the difizen project. For more details, please refer to the documentation in the product platform section.
- Monitor Component: Added knowledge and tool instance collection, supporting full-link trace sequence concatenation and providing token consumption monitoring.
- New Web Session Module: Provides session and message persistence management capabilities.

### Note
- Optimized Knowledge Component: Users can configure and specify any number of recall results (similarity_top_k).
- Fixed Chroma Component: Resolved issues where the embedding module was not specified.
- Various code optimizations and documentation updates.

## [0.0.11] - 2024-07-11
### Added
- DataAgent Autonomous Data Agent MVP Version Released
  - Minimum Viable Product version, DataAgent aims to empower your agent with the capability of self-assessment and evolution through intelligent agent abilities. For detailed information, please refer to the user documentation.
- Added intermediate information streaming output capabilities in PEER and ReAct modes

### Note
- Latest PEER research findings released
  - This paper provides a detailed introduction to the mechanisms and principles of the PEER multi-agent framework. Experimental validation proves the advancement of the PEER model. For detailed information, please refer to the user documentation.
- Added use cases
  - Andrew Ng's Reflexive Workflow Translation Agent Replication
- Some code optimizations and documentation updates.

## [0.0.10] - 2024-06-28
### Added
- Added standard integration for the DeepSeek model in the LLM module.
- Added a new OpenAI general protocol wrapper class, OpenAIStyleLLM.
  - Models using the OpenAI protocol can be configured directly.
- Added a new LangChain tool wrapper class, LangChainTool, with several example tools for search and execution.
  - LangChain tools can be configured directly.
- Added Agent information collection capability in the monitor module.

### Note
- Added use cases.
  - Supplemented documentation with a financial event analysis case study using PEER collaborative mode.
- Added several new documents for LLM components, tool components, and the Monitor module.
- Updated the new README.
- Some code optimizations and documentation updates.

## [0.0.9] - 2024-06-14
### Added
- Added standard integration for Claude and Ollama LLM components
- Added new Qwen embedding module
- Added default agents for ReAct-Type and NL2API-Type

### Note
- Added new use cases
  - RAG-Type Agent Examples: Legal Consultation Agent
  - ReAct-Type Agent Examples: Python Code Generation and Execution Agent
  - Multi-Agent: Discussion Group Based on Multi-Turn Multi-Agent Mode

  For more details, please refer to the use case section in the user documentation.
- Some code optimizations and documentation updates.

## [0.0.8] - 2024-06-06
### Added
- Introduced a new monitor module
  - Data running in any agentUniverse can be collected and observed
- Added webserver post_fork functionality
  - Provides multi-node process intervention capabilities after starting the webserver in agentUniverse
- Introduced SQLDB_WRAPPER wrapper class, offering typical database connection methods
  - Through the SQLDB_WRAPPER wrapper class, you can conveniently connect to various databases and storage technologies including SQLServer, MySQL, Oracle, PostgreSQL, SQLite and others
- Added connection support for Milvus vector database component

For more usage of the above features, please pay attention to the agentUniverse guidebook.

### Changed
- Flask is set as the default webserver startup method across all platforms, with gunicorn and gRPC capabilities disabled by default
  - In the previous version, we found slight compatibility differences with gunicorn and gRPC across different operating systems. Thus, we have made Flask the primary startup method for all platforms. You can enable gunicorn and gRPC in the configuration as needed.

### Security
- Some aU dependencies were identified to have security vulnerabilities in third-party packages. For security reasons, we have upgraded their versions, with the main changes including:
  - requests (^2.31.0 -> ^2.32.0)
  - flask (^2.2 -> ^2.3.2)
  - werkzeug (^2.2.2 -> ^3.0.3)
  - langchain (0.0.352 -> 0.1.20)
  - langchain-core (0.1.3 -> 0.1.52)
  - langchain-community (no version lock -> 0.0.38)
  - gunicorn (21.2.0 -> ^22.0.0)
  - Jinja2 (no version lock -> ^3.1.4)
  - tqdm (no version lock -> ^4.66.3)
If your system has external access, we strongly recommend installing version v0.0.8 of agentUniverse to mitigate the security risks posed by these third-party packages. For more detailed information, you can visit https://security.snyk.io.

### Note
- Some code optimizations and documentation updates.

## [0.0.7] - 2024-05-29
### Added
- LLM component supports multimodal parameter invocation.
- Added LLM integration methods for Qwen, WenXin, Kimi, Baichuan, etc.

### Note
- Added a multimodal example agent, see the invocation details in `sample_standard_app.intelligence.test.test_multimodal_agent.MultimodalAgentTest`.
- Some code optimizations and documentation updates.

## [0.0.6] - 2024-05-15
### Added
- Support for the GPT-4o model, with updates to related examples.
- Support for the RPC component gRPC, providing a standard method for service startup.

### Note 
- Provide standard Docker images and K8S deployment solutions.
- Some code optimizations and documentation updates.

## [0.0.5] - 2024-05-08
### Added
- The LLM component supports streaming calls.
- The Knowledge component adds an update definition.

### Fixed
- Fixed potential concurrency safety issues in the peer planner.
- Fixed the issue in version 0.0.4 of the PyPI package where the packaging method forced users to enter an AK upon startup.

### Note 
- Some code optimizations and documentation updates.

## [0.0.4] - 2024-04-26
### Added
- Add version management capability to the prompt.

### Fixed
- Fixed compatibility issues on Windows
  * Due to compatibility issues of Gunicorn with Windows systems, automatically identify the kernel version to select the web startup method.
  * Specified YAML reading as UTF-8 encoding method.

### Note
- [2024-05-08] Please be aware that the PyPI package version 0.0.4 includes the sample_standard_app example project by default. This will reference additional components from sample_standard_app at startup and require users to input an AK. If you are not using the corresponding components, you can bypass this restriction by using a mock AK. This issue has been fixed in version 0.0.5.

## [0.0.3] - 2024-04-19
### Init
- The official release version of agentUniverse has been initialized. Enjoy using it!

## [0.0.2] - 2024-04-17
### Fixed
- Fixed an issue where associated dependencies were not being automatically installed when installing package versions.

## [0.0.1] - 2024-04-09
### Init
- Project initialization commit. This framework is a large model multi-agent framework. Enjoy using it!