# Concurrent create-only Word and PowerPoint saves

`WordDocumentTool` and `PowerPointTool` create mode defaults to
`overwrite=false`. A destination created by another caller while a document
is being prepared is preserved: the later publication returns a structured
error. The temporary archive is fully written and validated before it becomes
visible as the destination.

An explicit `overwrite=true` still permits replacement. Append retains its
existing update behavior; this change does not serialize concurrent appends.
File-size/archive limits, template handling and temporary-file cleanup remain
in effect.

Publication uses no-replace rename on Windows and a same-filesystem hard link
on POSIX. A POSIX filesystem that cannot create hard links reports an error
instead of weakening the create-only guarantee. Temporary files already live
beside the destination, so publication does not cross filesystems.

## 中文说明

Word/PPT 工具的创建模式默认 `overwrite=false`。如果另一个调用在文档准备期间
先创建了同名文件，后到的保存会返回结构化错误，并保留先创建的文件。临时文档会
先完成写入及压缩包校验，再发布到目标路径。

显式设置 `overwrite=true` 时仍可替换；追加模式保持原有更新行为，此修改不对
多个并发追加操作进行串行化。大小限制、模板处理和临时文件清理仍然有效。

Windows 使用不覆盖目标的重命名，POSIX 使用同一文件系统上的硬链接。POSIX
文件系统不支持硬链接时会报错，不会降级成可能覆盖文件的操作。
