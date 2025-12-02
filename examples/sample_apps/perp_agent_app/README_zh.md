# agentUniverse - PERP Sample Project
## 介绍
本项目是使用agentUniverse中的PERP模式构建的示例项目。
您可以参考本项目中的代码，了解如何使用PERP模式。
该示例通过整合`Google Search Tool`、`Analysis Agent`、`Reporter Agent`等Executor，实现了一个简单的搜索分析报告生成流程。

## 关于 PERP
PERP(Plan-Execute-RePlan)为经典 Plan&Execute 的一种改进方案，通过引入 RePlan 机制，使得 Agent 在执行过程中能够根据执行结果进行自我修正，从而提高 Agent 的执行效率和准确性，尤其适用于长程任务。
其优势在于：
1.通过Planner的强制plan，让Agent摆脱条件反射式的工具调用，从全局视角考虑任务
2.通过子Agent的方式，解决上下文的问题。同时可复用项目中已有的Agent，提升Agent的复用性/模块化
3.将Tool跟Agent拉齐，进行统一的规划


其工作流程如下：
![PERP](img/perp.jpg)

## 快速开始
您可以基于 [快速开始](https://github.com/agentuniverse-ai/agentUniverse/blob/master/docs/guidebook/zh/%E5%BC%80%E5%A7%8B%E4%BD%BF%E7%94%A8/%E5%BF%AB%E9%80%9F%E5%BC%80%E5%A7%8B.md) 运行第一个案例。

## 用户指南
更多详细信息，请参阅 [用户指南](https://github.com/agentuniverse-ai/agentUniverse/blob/master/docs/guidebook/zh/%E7%9B%AE%E5%BD%95.md) 。