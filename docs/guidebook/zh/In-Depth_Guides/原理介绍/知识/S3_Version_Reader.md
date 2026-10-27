# S3 固定版本知识导入

`S3VersionReader` 将“捕获对象身份清单”与“下载解析”分开：清单记录 bucket/key/VersionId/ETag/长度，Document 再记录实际 SHA-256、来源命名空间和委托 Reader。它不会自动改读最新对象，不修改现有 Reader，也不重写文件解析器。完整示例、清单结构与复现命令见[英文文档](../../../../en/In-Depth_Guides/Tutorials/Knowledge/S3_Version_Reader.md)。

## 使用

安装 `agentuniverse[s3_reader_ext]`；已测 boto3 1.35.99。将 `s3_version_reader.yaml.example` 复制到应用 Reader 扫描目录，设置已授权 bucket、稳定且区分不同服务/账号的 `source_name`、后缀→已注册本地 Reader 映射。凭证走正常 AWS 凭证机制，不能写进清单或文档 metadata。`client_args` 不出现在普通模型 dump/repr 中，但这不等于替其他组件的日志或用户正文脱敏。

应用启动后，用 `capture_prefix('manuals/')` 获得 JSON 清单并保存为 `.s3manifest`，然后调用 `load_data`。Knowledge 中配置 `readers: {s3manifest: s3_version_reader}`，按普通 `source_path` 入库。捕获是显式前置步骤，读取不会重新遍历最新对象。空 prefix 明确表示整个配置 bucket。

组件只做 list/HEAD/GET，不创建或修改 S3 数据。普通 `load_data` 导入完成或失败都会关闭 SDK 客户端；直接使用 capture/partial API 时调用方负责 `close()`。注册组件的副本不会共享客户端或可变配置。

## 一致性与限制

- 默认要求非 null 不可变 VersionId。读取指定版本并发送 `IfMatch`，检查响应版本、ETag、长度与流实际字节数，计算 SHA-256；清单可附加预期 SHA-256。ETag 是不透明条件值，不一概当 MD5。
- `allow_unversioned: true` 才允许缺版本或字符串 `"null"`。此模式明确标为 `conditional-etag`，可以发现 ETag 变化，但不保证不可变身份，也不能发现同内容/同 ETag 替换或纯 metadata 修改。兼容服务可以省略 null 版本响应头。
- 分页列举＋逐对象 HEAD 不是 bucket 级原子快照；期间新增/删除对象不保证一致可见。旧版本也可能因生命周期清理或权限改变而不可用。分页重复 token、数量/字节预算超出时抛错，不返回伪完整清单。
- 输出保留 `s3_source` 来源信息，`file_name` 为对象 key。稳定 ID 来自来源、解析序号和文本；不代表 Store 自动去重或完整解析环境指纹。调用方不能用 `ext_info` 覆盖保留的来源字段。
- `load_data` 任一对象失败就抛 `S3ImportError`，不返回部分列表。`error.report` 提供对象 key、失败阶段、异常类型和经过限定的服务错误码，不包含可能带凭证的原始异常文本。只有显式调用 `read_manifest_with_report` 才取得部分结果，由调用方检查 `complete` 再决定入库。
- 数量、清单大小、对象/总字节、输出文档数/文本字符设上限。对象保存到系统临时目录的固定生成文件名，不从 key 构建本地路径，完成后删除。委托解析器仍在进程内运行，输出限制不是 CPU/内存沙箱；必须选择适合内容、具有自身边界的可信 Reader。
- 超时是连接/读取 socket 超时，不是整个导入任务截止时间。SDK 总尝试数为 1，无应用层重试、异步、恢复日志或跨 Store 事务承诺。普通 bucket/path-style 请求之外的目录桶、Access Point ARN、requester-pays、SSE-C 不支持。

## 验证范围

真实兼容服务由 MinIO 官方固定提交 `9e49d5e7a648f00e26f2246f4dc28e6b07f8c84a`、Go 1.27.1 本地构建，版本字符串是 DEVELOPMENT.GOGET，不冒称官方发行镜像。测试包含真实分页、覆盖/删除标记后的旧版本读取、可变对象条件拒绝、缺失版本、哈希与输出预算、错误报告、组件复制和注册 Reader→MinIO→SQLite→公开 Knowledge 检索的版本溯源。

未使用 AWS 账号，不能声称已覆盖真实 AWS IAM/KMS/Object Lock、所有 multipart 情况或所有兼容厂商。测试服务仅回环开放，使用公开测试凭证和每例唯一 bucket，测试结束只清理该 bucket；不可把测试配置用于生产。
