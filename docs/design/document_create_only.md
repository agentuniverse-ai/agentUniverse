# Concurrent document output publication

`WordDocumentTool` and `PowerPointTool` create mode, `PDFTool` merge/split/rotate,
and `EmailDocumentTool` create/extract default to `overwrite=false`. A destination
created by another caller while an output is being prepared is preserved: the
later publication returns a structured error. A temporary file is fully written
and the existing size/format validations finish before publication.

An explicit `overwrite=true` still permits replacement. Append retains its
existing update behavior; this change does not serialize concurrent appends.
File-size/archive limits, template handling and temporary-file cleanup remain
in effect.

The guarantee applies to each individual output file. Splitting a PDF or
extracting several email attachments is not an all-or-nothing transaction:
a concurrent conflict on a later destination can leave earlier outputs written.

Publication uses no-replace rename on Windows and a same-filesystem hard link
on POSIX. A POSIX filesystem that cannot create hard links reports an error
instead of weakening the create-only guarantee. Temporary files already live
beside the destination, so publication does not cross filesystems.

## 中文说明

Word/PPT 创建模式、PDF 合并/拆分/旋转、邮件创建/附件提取默认
`overwrite=false`。如果另一个调用在输出准备期间先创建了同名文件，后到的
保存会返回结构化错误，并保留先创建的文件。临时文件先写完并完成原有的大小、
格式校验，再发布到目标路径。

显式设置 `overwrite=true` 时仍可替换；追加模式保持原有更新行为，此修改不对
多个并发追加操作进行串行化。大小限制、模板处理和临时文件清理仍然有效。

此保证针对单个输出文件。拆分 PDF 或提取多个附件不属于整体原子事务；如果后面
某个目标出现并发冲突，前面已经写出的文件可能保留。

Windows 使用不覆盖目标的重命名，POSIX 使用同一文件系统上的硬链接。POSIX
文件系统不支持硬链接时会报错，不会降级成可能覆盖文件的操作。
