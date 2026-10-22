# 大型 Tool 结果制品引用

`ArtifactResultTool` 包装已有 Tool，默认 `enabled=False`。显式开启后，超过阈值的完整文本/JSON结果保存到指定私有目录，返回包含ID、SHA-256、字节数、媒体类型、过期时间和存储说明的小引用；不是语义摘要。小结果保持原值。

```python
from agentuniverse.agent.action.tool.result_artifacts import LocalToolArtifactStore, ArtifactResultTool, ArtifactReadTool
store = LocalToolArtifactStore("./private-session-artifacts")
wrapped = ArtifactResultTool(target=my_existing_tool, artifact_store=store,
                             enabled=True, threshold_bytes=65536,
                             input_keys=my_existing_tool.input_keys)
reader = ArtifactReadTool(artifact_store=store)
```

使用真实 `run/async_run`，或将两个配置好的实例注册到 ToolManager、通过 `as_langchain()` 供规划器调用。目标Tool仍走公开调用与参数/旧ToolInput校验。仅程序式配置，无自动启用的YAML。异步目标完成后的本地序列化/发布仍是有界同步磁盘操作。

`reader.run(artifact_id=ref["id"], expected_sha256=ref["sha256"], offset=0, limit=4096)` 返回有界字符页、下一偏移和结束状态。偏移按Unicode字符计数。JSON页可能截断token，应拼接完整文本后再解析。每次读取校验完整有界制品，不是流式随机访问。

使用临时文件flush和硬链接原子发布，禁止覆盖，包括强制ID碰撞。普通失败清理临时文件；不支持硬链接的文件系统明确失败。损坏、过期、缺文件、越界、超预算均失败，不悄悄截断结果。存储失败前目标可能已有副作用，不能盲目重试。

开启持久化意味着保留结果内容。私有目录与reader的访问范围由应用负责；不提供加密、多租户授权、自动脱敏或对本地文件篡改者的保护。原目标tracing/会话钩子仍可能记录完整输出，本功能只缩小选定Tool返回给规划器的直接观察值，不保证所有上下文路径都缩小。

TTL只拒绝过期读取，不自动删除。保留结束后显式调用 `store.remove(id)` 或外部管理专用目录。只限制单制品大小，没有总磁盘配额/后台清理/安全擦除。完整使用方法、边界和测试说明见英文 Tool_Result_Artifacts.md。
