# Secure RAG Agent App (示例应用)

基于 `secure_rag_work_pattern` 的安全闭环 RAG 智能体示例：
检索规划 → 检索与生成 → 安全审查（敏感词/合规/脱敏） → 表达输出。

适用于知识服务场景下的内容安全管控（如 RAG 知识问答）。

## 目录结构

```
secure_rag_agent_app/
├── config/
│   └── config.toml             # 应用配置（LLM、向量库、安全审查阈值等）
├── intelligence/
│   └── agentic/
│       ├── agent/
│       │   ├── agent_template/        # 四个角色模板示例
│       │   │   ├── demo_retrieval_planner.yaml
│       │   │   ├── demo_rag_executor.yaml
│       │   │   ├── demo_security_reviewer.yaml
│       │   │   └── demo_secure_expressor.yaml
│       │   ├── agent_instance/
│       │   │   └── secure_rag_case/
│       │   │       └── demo_*.yaml      # 四个角色实例
│       │   └── work_pattern/
│       │           └── secure_rag_workflow.yaml   # 引用 secure_rag_work_pattern
│       ├── knowledge/
│       ├── llm/
│       ├── memory/
│       ├── prompt/
│       └── tool/
│       └── test/                    # 示例用例与断言
├── bootstrap/
├── db/
├── platform/
├── pyproject.toml
├── poetry.toml
├── README.md
└── README_zh.md
```

## 使用

1. 在 `config/config.toml` 中配置 LLM（qwen_llm 等）与向量数据库。
2. 参照 `peer_agent_app` 的 `peer_workflow.yaml` 编写 `secure_rag_workflow.yaml`，元数据指向：
   `agentuniverse.agent.work_pattern.secure_rag_work_pattern.SecureRagWorkPattern`。
3. 在 `intelligence/agentic/agent/agent_instance/secure_rag_case/` 下配置四个角色实例（planning/executing/reviewing/expressing）。
4. 运行示例：需要 LLM API Key 与可运行的向量库（chromadb），请参阅 `rag_app` 的启动方式。

## 贡献出处

该示例配套 agentUniverse 工作模式贡献 `secure_rag_work_pattern`（对应直通乌镇2026 专场赛任务：智能体工作模式贡献，issue #183）。
