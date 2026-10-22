# 可审计金融研究工作区

这是一个基于 agentUniverse 原生 `Tool`、`DocProcessor`、`Document`、`Query` 和
`WorkPattern` 接口的离线优先金融研究应用，包含：

- SQLite 租户隔离的数据摄取和任务；
- 有上限的确定性检索、稳定引用 ID 和来源哈希；
- 持久化检索检查点，中断恢复时不会悄悄更换证据；
- 内置 `FinancialIndicatorExtractor` 与 `MMRProcessor`；
- 可选的已注册 `WorkPattern`（包括项目配置好的 PEER）；
- 引用 precision/recall 评估和完全离线的测试数据。

## 离线运行

```bash
python -m examples.sample_apps.financial_research_app.cli \
  --db /tmp/financial-research.db --tenant demo \
  --ingest examples/sample_apps/financial_research_app/data/sample_company_report.txt \
  --question 'How did revenue and margin change?'
```

无需模型密钥和网络。输出同时保留原始引用/来源信息，以及经过 agentUniverse 金融指标处理器
和 MMR 重排后的分析文档。

## 组件注册模式

```bash
python -m examples.sample_apps.financial_research_app.cli \
  --config examples/sample_apps/financial_research_app/config/config.toml \
  --db /tmp/financial-research.db --tenant demo \
  --ingest examples/sample_apps/financial_research_app/data/sample_company_report.txt \
  --question 'How did revenue and margin change?'
```

此模式通过 agentUniverse Manager 获取处理器。项目若已经配置 PEER 的 planning、executing、
expressing、reviewing 智能体，可再传 `--work-pattern`；证据和稳定引用会放进其 `InputObject`。

## 测试

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q \
  examples/sample_apps/financial_research_app/intelligence/test/test_workspace.py
```

测试覆盖租户隔离、输入上限、检查点恢复、金融指标提取、MMR、WorkPattern 输入、YAML 组件
配置和 `FinancialEvidenceTool`，不会访问托管模型或行情服务。生产环境可将本地检索替换为
agentUniverse `Store`，并接入认证服务、配置完整 PEER 和批准的行情工具。
