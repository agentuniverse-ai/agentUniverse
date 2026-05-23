# Phase 3 Guardrail 诊断 API（后台管理模块 MVP）

本文档描述 LPP 安全雷达所需的 Guardrail 诊断接口。

## 接口前缀

`/api/v1/admin/guardrail`

## 接口清单

- `GET /sessions/<session_id>`：返回会话级 Guardrail 诊断分数与告警

Trace 接口 `GET /api/v1/admin/trace/sessions/<session_id>` 也会在 `diagnostics` 字段中附带相同结构，便于前端一次联调。

## 响应示例

```json
{
  "success": true,
  "result": {
    "guardrail_enabled": true,
    "risk_level": "medium",
    "scores": {
      "logic_consistency": 75.0,
      "info_entropy": 62.5,
      "diversity_ttr": 58.0,
      "lpp_feature": 48.0,
      "safety_score": 66.2
    },
    "warnings": [
      {
        "level": "warning",
        "message": "Low lexical diversity detected. Output may be homogenized."
      }
    ]
  }
}
```

## 评分说明（MVP）

- 基于 Session 消息内容的轻量启发式分析
- 维度：逻辑一致性、信息熵、词汇多样性、结构相似度、综合安全分
- 后续可替换为真实 LPP/Guardrail 模型输出，前端 DTO 保持不变

## 测试

```bash
pytest tests/test_agentuniverse/unit/agent_serve/test_admin_guardrail_service.py -q
```
