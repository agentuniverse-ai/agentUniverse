# agentUniverse - PERP Sample Project
## Introduction
This project is a sample project built using the PERP work pattern in agentUniverse.
You can refer to the code in this project to understand how to use the PERP work pattern.
This example integrates executors such as `Google Search Tool`, `Analysis Agent`, and `Reporter Agent` to implement a simple search analysis report generation process.

## About PERP
PERP (Plan-Execute-RePlan) is an improved version of the classic Plan&Execute pattern.   
By introducing the RePlan mechanism, it allows Agents to self-correct during execution based on execution results, thereby improving Agent execution efficiency and accuracy, especially suitable for long-range tasks.

Its advantages are:
1. Through the Planner's mandatory planning, Agents can break away from conditioned reflex-style tool calls and consider tasks from a global perspective
2. Solves context problems through sub-Agents. At the same time, it can reuse existing agents in the project, improving agent reusability/modularization
3. Aligns Tools with Agents for unified planning

Its workflow is as follows:
![PERP](img/perp.jpg)

## Quick Start
You can run this project based on the [Quick Start](https://github.com/agentuniverse-ai/agentUniverse/blob/master/docs/guidebook/en/Get_Start/Quick_Start.md).

## Guidebook
For more detailed information, please refer to the [Guidebook](https://github.com/agentuniverse-ai/agentUniverse/blob/master/docs/guidebook/en/Contents.md).

