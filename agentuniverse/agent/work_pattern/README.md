# 安全闭环 RAG 工作模式 / Secure RAG Work Pattern

## 简介

安全闭环 RAG 工作模式（Secure RAG Loop）是 agentUniverse 的智能体工作模式贡献，专为**知识服务场景下的内容安全管控**设计（如 RAG 知识问答、天理裁决式安全技能）。

模式由四个 Agent 角色按顺序串联，每轮可重试：

| 角色 | 职责 | 关键产出 |
|------|------|----------|
| planning（检索规划） | 根据用户问题规划检索策略（关键词/向量/混合、数据源选择） | 检索策略 |
| executing（检索与生成） | 检索相关知识片段，基于知识生成候选回答 | 候选答案 + 上下文 |
| reviewing（安全审查） | 敏感词过滤、合规知识库校验、数据脱敏；输出安全得分与处置动作 | pass / mask / block + 得分 |
| expressing（表达输出） | 审查通过输出最终答案；否则输出脱敏答案或拦截提示 | 最终答案 |

配置参数（`work_pattern_input`）：
- `retry_count`：最大重试轮数，默认 1
- `eval_threshold`：审查通过分数阈值，默认 0.6
- `security_threshold`：安全审查阈值，默认 0.8
- `jump_step`：跳过至指定步骤继续执行

## 快速开始

在你的应用中引用此模式（参考 `peer_workflow.yaml`）：

```yaml
info:
  name: 'secure_rag_workflow'
  description: 'secure RAG closed-loop workflow'
metadata:
  type: 'WORK_PATTERN'
  module: 'agentuniverse.agent.work_pattern.secure_rag_work_pattern'
  class: 'SecureRagWorkPattern'
```

并在 agent 实例中注入四个角色模板：
- `planning`: PlanningAgentTemplate 实现
- `executing`: ExecutingAgentTemplate 实现（RAG 检索+生成）
- `reviewing`: ReviewingAgentTemplate 实现（敏感词/合规/脱敏）
- `expressing`: ExpressingAgentTemplate 实现

## 贡献说明

本模式对应 agentUniverse 直通乌镇2026 专场赛任务：**智能体工作模式贡献**（复杂型任务，issue #183 “Working Pattern Contribution Solicitation”）。

## License

Apache-2.0
