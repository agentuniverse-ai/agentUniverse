# agentUniverse
****************************************
语言版本: [English](./README.md) | [中文](./README_zh.md) | [日本語](./README_jp.md)

![](https://img.shields.io/badge/framework-agentUniverse-pink)
![](https://img.shields.io/badge/python-3.10%2B-blue?logo=Python)
[![](https://img.shields.io/badge/%20license-Apache--2.0-yellow)](LICENSE)
[![Static Badge](https://img.shields.io/badge/pypi-v0.0.18-blue?logo=pypi)](https://pypi.org/project/agentUniverse/)

![](docs/guidebook/_picture/logo_bar.jpg)
****************************************

## agentUniverse是什么？

**agentUniverse 是一个基于大型语言模型的多智能体框架。** agentUniverse为您提供灵活易拓展的单智能体构建能力；agentUniverse核心拥有丰富的多智能体协同模式组件（可视为一个协同模式工厂Pattern Factory），它能让智能体们各司其职在解决不同领域问题时发挥最大的能力；同时agentUniverse专注于领域经验的融合，帮助您轻松将领域经验融入到智能体的工作中。🎉🎉🎉

**🌈🌈🌈agentUniverse源自于蚂蚁集团(https://github.com/antgroup) 的真实金融业务实践，致力于帮助开发者、企业轻松构建出领域专家级别的强大智能体，协同完成工作。**

![](docs/guidebook/_picture/agent_universe_framework_resize.jpg)

我们期待您通过社区对不同领域的Pattern进行实践与交流共享，框架也预置有若干已在真实产业中验证有效的多智能体协作模式组件，并在未来持续丰富。目前即将开放的模式组件包括：
* PEER 模式组件： 该pattern通过计划（Plan）、执行（Execute）、表达（Express）、评价（Review）四个不同职责的智能体，实现对复杂问题的多步拆解、分步执行，并基于评价反馈进行自主迭代，最终提升推理分析类任务表现。典型适用场景：事件解读、行业分析
* DOE 模式组件： 该pattern通过数据精制（Data-fining）、观点注入（Opinion-inject）、表达（Express）三个智能体，实现对数据密集、高计算精度、融合专家观点的生成任务的效果提升。典型适用场景：财报生成

更多模式组件持续推出中...

The LLM model integration can be accomplished with simple configuration, currently agentUniverse supported models include:

|-|供应商|                                                      模型                                                      |
|:-----:|:--------:|:------------------------------------------------------------------------------------------------------------:|
|<img src="https://github.com/user-attachments/assets/b7b0f2ce-3250-4008-b6d7-4712a983deb9" height="25">|Qwen| qwen3 Series（qwen3-235b-a22b、qwen3-32b、qwen3-30b-a3b, etc.） 、qwen2.5-72b-instruct、qwq-32b-preview、qwen-max、… |
|<img src="https://github.com/user-attachments/assets/5a997feb-bef4-4e53-ac3e-d38221e5399c" height="25">|Deepseek|                            deepseek-r1、deepseek-v3、deepseek-r1-distill-qwen-32b、…                            |
|<img src="https://github.com/user-attachments/assets/0b50e555-65e8-49b2-b725-f3f71ee7daed" height="25">|OpenAI|                                GPT-4o、GPT-4o mini、OpenAI o1、OpenAI o3-mini、…                                 |
|<img src="https://github.com/user-attachments/assets/60fe0a70-0b47-4ac7-9bc9-8e860732ace9" height="25">|Claude|                             claude 3.7 sonnet 、Claude 3.5 Sonnet、Claude 3 Opus、…                             |
|<img src="https://github.com/user-attachments/assets/334c7f09-7eae-4a65-a70f-2e6531964224" height="25">|Gemini|                  Gemini 2.5 Pro、Gemini 2.0 Flash、Gemini 2.0 Flash Thinking、Gemini 1.5 Pro、…                  |
|<img src="https://github.com/user-attachments/assets/8e41c73f-3103-4305-ad1f-56116ea55523" height="25">|Llama|                      llama3.3-70b-instruct、llama3.2-3b-instruct、llama3.2-1b-instruct、…                       |
|<img src="https://github.com/user-attachments/assets/19d264c6-e499-4913-9d6d-314d392f2246" height="25">|KIMI|                              moonshot-v1-128k、moonshot-v1-32k、moonshot-v1-8k、…                               |
|<img src="https://github.com/user-attachments/assets/79572d9a-29d5-4c0e-a336-ce3f8018fb05" height="25">|WenXin|                                     ERNIE 4.5 Turbo、ERNIE 4.5、ERNIE 4.0 Turbo、ERNIE 4.0、ERNIE 3.5、…                                     |
|<img src="https://github.com/user-attachments/assets/abb5311e-4d70-4e9c-8fca-e5129ae912fc" height="25">|chatglm|                                         chatglm3-6b、chatglm-6b-v2、…                                          |
|<img src="https://github.com/user-attachments/assets/fe265f24-4ea6-4ff2-9b50-58ab6706a5f5" height="25">|BaiChuan|                                   baichuan2-turbo、baichuan2-13b-chat-v1、…                                    |
|<img src="https://github.com/user-attachments/assets/41ffe268-392f-4ab9-b42d-e30dbd70d66b" height="25">|Doubao|                              Doubao-pro-128k、Doubao-pro-32k、Doubao-lite-128k、…                               |

****************************************

## 目录
* [快速开始](#快速开始)  
|  &nbsp; [快速安装](#快速安装) &nbsp; |
&nbsp; [运行案例](#运行第一个教程案例) &nbsp; |
* [如何搭建一个智能体应用](#如何搭建一个智能体应用)  
| &nbsp; [标准工程脚手架搭建](#标准工程脚手架) &nbsp; |
&nbsp; [画布式研发平台搭建](#画布式研发平台搭建) &nbsp; |
* [为什么使用agentUniverse](#为什么使用agentUniverse)  
| &nbsp; [设计思路](#设计思路) &nbsp; | 
&nbsp; [协同机制](#多智能体协同机制) &nbsp; | 
&nbsp; [研究文献](#文献) &nbsp; | 
&nbsp; [核心特性](#核心特性) &nbsp; |
* [应用实践](#应用实践)  
| &nbsp; [应用实践案例](#应用实践案例) &nbsp; |
&nbsp; [典型产品](#使用aU构建的典型产品) &nbsp; |
* [用户指南手册](#用户指南手册)
* [更多](#更多)  
| &nbsp; Roadmap &nbsp; | 
&nbsp; [API说明](#API参考) &nbsp; | 
&nbsp; [项目支持](#支持) &nbsp; |
&nbsp;&nbsp; [鸣谢](#鸣谢)  &nbsp;&nbsp; |

****************************************

## 快速开始
### 快速安装
使用pip：
```shell
pip install agentUniverse
```

### 运行第一个教程案例

运行您的第一个案例，您可以通过教程快速体验agentUniverse构建出的智能体(组)运行效果。 

详细步骤请阅读文档: [运行第一个教程案例](./docs/guidebook/zh/开始使用/2.运行第一个教程案例.md) 。

****************************************

## 如何搭建一个智能体应用

### 标准工程脚手架
⌨️ 标准工程脚手架：[agentUniverse Standard Project](examples/sample_standard_app)

#### 快速构建单体智能体
您可以通过 [快速构建单体智能体](./docs/guidebook/zh/开始使用/3.快速构建单体智能体.md) 章节的阅读与体验了解如何快速构建单个智能体，并掌握如何通过工具、知识库、RAG技术等能力增强您的智能体能力，同时掌握智能体配置、测试、调优、服务化、效果评估等一系列基本的智能体应用研发流程。 

#### 构建典型的多智能体应用
您可以通过 [构建典型的多智能体应用](./docs/guidebook/zh/开始使用/4.构建典型的多智能体应用.md) 章节进一步了解在复杂的任务场景，如何将智能体能力拆分成多个智能体，并让其通过协同进一步提升您的任务表现。

#### 沉淀与使用智能体模版
您可以通过 [沉淀与使用智能体模版](./docs/guidebook/zh/开始使用/5.沉淀与使用智能体模版.md) 章节了解如何将有效的智能体模式沉淀成模版，这将大大提升后续智能体的构建效率并便于传播。

#### 使用与发布MCP服务
您可以通过 [如何使用MCP服务](./docs/guidebook/zh/How-to/使用与发布MCP服务/如何使用MCP服务.md)、[如何发布MCP服务](./docs/guidebook/zh/How-to/使用与发布MCP服务/如何发布MCP服务.md) 章节掌握如何快速在智能体框架中使用或发布MCP服务。

#### 智能体应用观测
agentUniverse拥有标准的智能体应用观测标准，并基于OpenTelemetry协议对于智能体、模型、工具等重要组件进行全方位采集与观测，方便用户追踪智能体全生命周期，您可以在 [智能体应用可观测](./docs/guidebook/zh/In-Depth_Guides/技术组件/可观测/基于OTEL的可观测能力.md) 章节掌握如何使用观测能力。

#### 常用使用技巧
您可以通过 [开始章节](./docs/guidebook/zh/开始使用) 下的其他文档了解智能体应用构建过程中的其他进阶技巧，例如如何在智能体过程中加入记忆模块、如何有效的管理项目中的prompt等。

### 画布式研发平台搭建

agentUniverse提供基于本地的画布式研发平台能力，请按照如下步骤快速启动。

**通过pip安装**
```shell
pip install magent-ui ruamel.yaml
```

**一键运行**

运行sample_apps/workflow_agent_app/bootstrap/platform下的[product_application.py](examples/sample_apps/workflow_agent_app/bootstrap/platform/product_application.py)文件，一键启动。

更多详情参考 [产品化平台快速开始](./docs/guidebook/zh/How-to/画布式研发平台使用/画布式研发平台快速开始.md)
与 [产品化平台进阶指南](./docs/guidebook/zh/How-to/画布式研发平台使用/画布式研发平台进阶指南.md) 。本功能由 🔗[difizen](https://github.com/difizen/magent) 项目组 X agentUniverse 项目组联合推出。

****************************************

## 为什么使用agentUniverse
### 设计思路

![](docs/guidebook/_picture/agentuniverse_structure.png)

agentUniverse核心提供了搭建单一智能体的全部关键组件、多智能体之间的协作机制、以及专家经验的注入机制，可以帮助开发者轻松构建具备专业KnowHow的智能应用。

### 多智能体协同机制

agentUniverse提供了若干已在真实产业中验证有效的多智能体协作模式组件，其中，“PEER”是最具特色的模式之一。

PEER模式通过计划（Planning）、执行（Executing）、表达（Expressing）、评价（Reviewing）四个不同职责的智能体，实现对复杂问题的多步拆解、分步执行，并基于评价反馈进行自主迭代，最终提升推理分析类任务表现。这一模式显著适用于需要多步拆解、深度分析的场景，比如对于事件的解读、宏中观经济分析、商业方案的可行性分析等。

PEER模式取得了令人兴奋的效果，最新的研究成果与实验结果我们可以在下列文献中阅读。

### 文献

BibTeX formatted
```text
@misc{wang2024peerexpertizingdomainspecifictasks,
      title={PEER: Expertizing Domain-Specific Tasks with a Multi-Agent Framework and Tuning Methods}, 
      author={Yiying Wang and Xiaojing Li and Binzhu Wang and Yueyang Zhou and Han Ji and Hong Chen and Jinshi Zhang and Fei Yu and Zewei Zhao and Song Jin and Renji Gong and Wanqing Xu},
      year={2024},
      eprint={2407.06985},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2407.06985}, 
}
```
文献简介：该文献详细介绍了介绍了PEER多智能体框架的机制原理，同时在实验部分分别从**完整性、相关性、紧凑性、事实性、逻辑性、结构性和全面性七个维度进行打分（各纬度满分为5分）**，PEER模式在每个测评维度的平均分数均高于BabyAGI，且在**完整性、相关性、逻辑性、结构性和全面性五个纬度有显著优势**；同时PEER模式在 GPT-3.5 turbo (16k) 模型下相较于 BabyAGI 的择优胜率达到 83%，在 GPT-4o 模型下择优胜率达到 81%，更多详情请阅读文献。
🔗https://arxiv.org/pdf/2407.06985

### 核心特性
通过上述的介绍我们将其归纳总结，agentUniverse包含如下主要特点：

灵活易拓的智能体构建能力： 提供智能体构建所必须的全部关键组件，所有组件均可支持定制供用户增强专属智能体；

丰富有效的多智能体协同模式： 提供PEER（Plan/Execute/Express/Review）、DOE（Data-fining/Opinion-inject/Express）等产业中验证有效的协同模式，支持用户自定义编排新模式，让多个智能体有机合作；

轻松融入领域经验： 提供领域prompt、知识构建与管理的能力，支持领域级SOP编排与注入，将智能体对齐至领域专家级别；

💡 更多特点见[agentUniverse核心特性](./docs/guidebook/zh/设计理念/核心特性.md)部分。

****************************************

## 应用实践
### 应用实践案例
🚩 [法律咨询Agent_v2](docs/guidebook/zh/实践应用/法律咨询案例.md)

🚩 [Python代码生成与执行Agent](docs/guidebook/zh/实践应用/Python自动执行案例.md)

🚩 [基于多轮多Agent的讨论小组](docs/guidebook/zh/实践应用/讨论组.md)

🚩 [基于PEER协同模式的金融事件分析](docs/guidebook/zh/实践应用/金融事件分析案例.md)

🚩 [吴恩达反思工作流翻译智能体复刻](docs/guidebook/zh/实践应用/翻译案例.md)

### 使用aU构建的典型产品
🔗[支小助-金融从业专家AI助手](https://zhu.alipay.com/?from=au)

**投研支小助：助推大模型落地严谨产业，提升投研专家效率**

投研支小助是大模型落地严谨产业的高效解决方案，基于专注严谨应用的凤凰大模型和善于专业定制的agentUniverse智能体框架，主要面向投研、ESG、财经、财报等投研相关细分领域的一系列专业AI业务助手，已在蚂蚁大规模场景充分验证，提升专家效率。


https://private-user-images.githubusercontent.com/39180831/355437700-192f712d-1b03-46a6-8422-1ca10aa94331.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3MjI5NDk4NTAsIm5iZiI6MTcyMjk0OTU1MCwicGF0aCI6Ii8zOTE4MDgzMS8zNTU0Mzc3MDAtMTkyZjcxMmQtMWIwMy00NmE2LTg0MjItMWNhMTBhYTk0MzMxLm1wND9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNDA4MDYlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjQwODA2VDEzMDU1MFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTU4NWMzNzVjOGZjZDNjMDMzMTE4YjQzOTk0ZWQwZGZkNWNmNWQxNWMzYWIzMTk4MzY1MjA5NWRhMjU2NGNiNzUmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0JmFjdG9yX2lkPTAma2V5X2lkPTAmcmVwb19pZD0wIn0.q1vdSg_Ghxr-DHLXfmQ_fVVRVSFn7H8VMHMi-_2QrjA


****************************************

## 用户指南手册
💡 更多详细信息，请阅读[用户指南手册](docs/guidebook/zh/目录.md) 。

****************************************

## 更多

### API参考
💡 请阅读[readthedocs](https://agentuniverse.readthedocs.io/en/latest/) 。

### 支持
#### 通过github issue提交疑问
😊 我们建议您使用[github issue](https://github.com/agentuniverse-ai/agentUniverse/issues) 提交您的疑问, 我们通常会在2日内回复。

#### 通过Discord联系我们
😊 加入我们的 [Discord频道](https://discord.gg/DHFcdkWAhn) 与我们进行交流。

#### 通过钉钉群联系我们
😊 加入我们的钉钉答疑群与我们联系。
![](./docs/guidebook/_picture/dingtalk_util20250429.png)

#### 通过管理员Email联系我们
😊 Email: 

* [jihan.hanji@antgroup.com](mailto:jihan.hanji@antgroup.com)
* [jerry.zzw@antgroup.com](mailto:jerry.zzw@antgroup.com)
* [jinshi.zjs@antgroup.com](mailto:jinshi.zjs@antgroup.com)

#### 微信公众号

😊 公众号ID：**agentUniverse智多星**

![](./docs/guidebook/_picture/wechat_official.png)

更多相关的文章与资讯你可以在微信公众号中获取。

#### twitter
ID: [@agentuniverse_](https://x.com/agentuniverse_)

### 鸣谢
本项目部分基于langchain、pydantic、gunicorn、flask、SQLAlchemy、chromadb等（详细依赖列表可见pyproject.toml）优秀开源项目实现，在此特别感谢相关项目与关联方。 🙏🙏🙏
