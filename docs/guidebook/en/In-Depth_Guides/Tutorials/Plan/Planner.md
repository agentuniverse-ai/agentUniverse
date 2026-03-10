# Planner - Deprecated

> **Note:** Starting from the new version, the Planner component has been deprecated. It is recommended to use **Agent Templates** as a replacement for the original Planner functionality.

## Background

In earlier versions, Planners influenced the collaboration and execution strategies of actual agents. agentUniverse could be viewed as a Pattern Factory, and Planners were the practical carriers of the collaboration and execution philosophies of these patterns.

## Migration Guide

The original Planner functionality has now been replaced by Agent Templates. Agent Templates provide a more flexible and powerful way to define collaboration and execution strategies.

Please refer to the following documentation for Agent Templates:
- [Creating and Using Agent Templates](../../../Get_Start/5.Creating_and_Using_Agent_Templates.md)
- [Agent Template](../Agent/AgentTemplate.md)

### Mapping

| Original Planner Type | Corresponding Agent Template |
|---|---|
| ReactPlanner | ReactAgentTemplate |
| RAGPlanner | RAGAgentTemplate |
| PEERPlanner | PeerAgentTemplate |
| WorkflowPlanner | WorkflowAgentTemplate |
| ExecutingPlanner | ExecutingAgentTemplate |
| ExpressingPlanner | ExpressingAgentTemplate |
| PlanningPlanner | PlanningAgentTemplate |
| ReviewingPlanner | ReviewingAgentTemplate |
