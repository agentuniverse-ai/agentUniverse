# 隐私保护知识问答智能体（privacy_guard_app）

一个"知识库先脱敏、再检索、后作答"的客服工单问答示例。知识库中包含虚构的邮箱、手机号、银行卡、身份证号与工号等敏感信息，经过 agentUniverse 的 DocProcessor 管道在**入库前**完成脱敏，召回时再做一次兜底清洗，保证敏感原文不会进入大模型上下文。

## 特性

- 双重脱敏管道：入库 `ticket_redactor`（含自定义工号/订单号正则），召回 `recall_redactor` 兜底（`log_key: null`，不覆盖入库统计）
- 每篇文档携带 `redaction_summary` 统计元数据，回答时可说明"脱敏了什么"
- 基于 SQLiteStore + jieba 的 BM25 检索，**检索链路零 API Key、可完全离线运行**
- 样例数据中的卡号/身份证号为结构合法的虚构号码（组件仅脱敏通过 Luhn/GB11643 校验的号码，避免误伤）

## 快速开始

```bash
# 1. 安装 agentUniverse（仓库根目录）
pip install agentUniverse

# 2. 进入应用目录
cd examples/sample_apps/privacy_guard_app

# 3. 离线验证脱敏检索管道（无需任何密钥）
export PYTHONPATH=$(pwd)/../../..:$(cd ../.. && pwd)
python intelligence/test/privacy_pipeline_test.py
# 预期输出: OK: N documents retrieved, all PII redacted.

# 4. （可选）在线问答：配置 DeepSeek 密钥后
cp config/custom_key.toml.sample config/custom_key.toml  # 填入 DEEPSEEK_API_KEY
python bootstrap/intelligence/server_application.py       # http://localhost:8888
```

## 目录结构

```
privacy_guard_app/
├── config/                                 # 应用配置与密钥模板
├── bootstrap/intelligence/server_application.py
└── intelligence/agentic/
    ├── agent/agent_instance/privacy_guard_agent.yaml   # RAG 智能体
    ├── llm/deepseek_llm.yaml                           # 在线问答所用 LLM
    └── knowledge/
        ├── privacy_knowledge.yaml                      # 脱敏管道编排
        ├── privacy_knowledge.py                        # 携带脱敏统计的 Knowledge
        ├── doc_processor/ticket_redactor.yaml          # 入库脱敏（含自定义正则）
        ├── doc_processor/recall_redactor.yaml          # 召回兜底脱敏
        ├── store/privacy_sqlite_store.yaml             # BM25 SQLite 存储
        └── raw_knowledge_file/support_tickets.txt      # 虚构工单样例
```

## 扩展建议

- 换向量检索：新增一个 ChromaStore/FAISS yaml 并加入 `stores`，配置 `embedding_model` 即可（参考 `rag_app`）
- 增加敏感实体：在 `ticket_redactor.yaml` 的 `custom_patterns` 中补充业务正则（如合同编号、车牌号）
- 合规审计：以 `redaction_summary` 为基础接入日志或审计服务

英文简介见 [README.md](README.md)，完整案例文档见 [隐私保护知识问答案例](../../../docs/guidebook/zh/实践应用/隐私保护知识问答案例.md)。
