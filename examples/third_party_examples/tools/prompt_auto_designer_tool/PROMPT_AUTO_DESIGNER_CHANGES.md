# Prompt Auto Designer 改动说明

- 新增 `PromptAutoDesigner` 服务，封装 prompt 生成/优化的核心流程，并通过定制的异常、数据模型和 LLM 调用链路提高易用性。
- 引入 `generator_cn.yaml`、`optimizer_cn.yaml` 两个模板，分别用于从场景输入生成新 prompt 以及对既有 prompt 做迭代优化。
- 扩展 `agentuniverse/prompt/__init__.py` 以便直接从 `agentuniverse.prompt` 导入新服务，同时补充了针对成功/失败路径的单元测试。
- 当前文档部分暂未调整，保留上游版本；如需接入，可在后续 PR 中扩展使用指南。

## 测试命令

```bash
PYTHONPATH=$PWD poetry run pytest tests/test_agentuniverse/unit/prompt/test_prompt_auto_designer.py -q
```
