# 保留协议的字面历史桥接

`ProtocolHistory` 是显式启用的历史转换接口，不改变原有 `Message.as_langchain()` 的模板语义。
它通过 `au_protocol_history` v1 元数据保留 assistant 的 function tool_calls、tool 结果的
tool_call_id、原始 JSON 参数和可选消息 ID；已有 SQL 存储无需建新表或迁移。

使用顺序：`ProtocolHistory.from_wire(observed)` → 已配置的 MemoryStorage.add → 重启后 get →
`prompt.as_langchain_with_history(history, history_index=1)` → `llm.as_langchain()`。
对于 `[system_template, user_template]`，位置 1 在系统模板和当前问题之间插入历史。
原模板变量正常替换，历史中的 `{customer_id}` 保持原文；可同步 invoke 或异步 ainvoke。
也可将 `ProtocolHistory.to_wire(history)` 交给现有 OpenAILLM.call/acall。
完整代码见 [英文指南](../../../../en/In-Depth_Guides/Tutorials/Memory/Protocol_History.md)。

支持 system/user/assistant/tool、存储 human/ai 别名、用户 text/image_url 内容块。
不支持的字段、角色、旧 function_call、音频或供应商私有块会明确报错，不静默降级。
保存响应片段时允许工具结果尚未产生；发给模型前必须已配齐每个工具结果，拒绝孤立结果、
重复调用 ID、未完成调用及被普通消息打断的工具组。调用者必须读取完整、按时间排序的历史，
本功能不修复其他存储排序/分页问题、不自动补回遗漏回合。

默认上限为 256 条、序列化 UTF-8 大小 2,000,000 字节；超限报错，不截断，不等同 token 预算。
数据深拷贝，原对象不变。可通过 `message_ids` 保存原消息 ID，与数据库行 ID 分离。
元数据保留不代表来源可信；丢弃元数据的外部导出不保证协议保真。不会执行工具或读取图片 URL。
LangChain 0.1.20 会把带 tool_calls 的空字符串 assistant 内容转为 null；直接 to_wire 仍保留原值。

复现入口在 `tests/reproduction/protocol-history-bridge/`。测试使用真实 SQLite 重启读取和
本地 HTTP 服务捕获真实 SDK 同步/异步请求，没有付费模型调用。它不是 JSONL 归档、自动回放、
上下文压缩或 SQL 类型过滤功能。测试通过不代表上游 CI、合并或比赛得分。
