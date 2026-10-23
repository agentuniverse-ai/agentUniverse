# Email attachment boundaries / 邮件附件边界

`EmailDocumentTool` treats attached messages and named multipart attachments as
separate documents. Their text and HTML are not appended to the containing
email's body or counted against its `max_body_chars` budget. Nested filenames
remain inside their attachment, so two forwarded messages may each contain
an `inside.bin` without a false duplicate-filename error in the outer email.

Named `message/rfc822` and `message/global` attachments are extracted as the
inner email serialized by Python's standard `email` package. Named multipart
attachments are serialized with their MIME container headers and structure.
Ordinary text and binary attachment payloads retain their decoded bytes.
Attachment sizes and the individual/aggregate byte limits use the same bytes
that extraction writes, rather than treating structured payloads as empty.
Base64 and quoted-printable message attachments are transfer-decoded before
extraction, including messages whose encoded headers contain soft line breaks.

Read/info/extract result fields and safe-filename checks are unchanged.
Extraction lists and writes named attachments at the current email level; it
does not unpack the documents attached within a forwarded email. Attachments
without filenames are excluded from body text and retain the existing policy
of not being listed or extracted automatically.

Structured email extraction preserves message content and MIME structure; it
does not promise a byte-for-byte copy of the original wire representation.
The standard serializer may normalize header folding and line endings.

`EmailDocumentTool` 将附件邮件和带文件名的多部分 MIME 附件作为独立文档处理。
它们的正文、HTML 不再混入主邮件，也不占用主邮件的 `max_body_chars` 预算。
内部文件名保留在附件内部；两封转发邮件各有一个 `inside.bin`，不再被误判为
主邮件中的重名附件。

带文件名的 `message/rfc822`、`message/global` 附件使用 Python 标准 `email`
库将内部邮件重新序列化后提取。带文件名的 multipart 附件连同 MIME 容器头部
和结构保存。普通文字、二进制附件保留解码后的原始字节。附件大小以及单个、
总附件字节限制按照实际写出的同一份字节计算，结构化附件不再被视为空文件。

read/info/extract 返回字段和安全文件名校验保持原有格式。提取只列出和写出
当前邮件层级的有名附件，不继续拆出转发邮件内部的附件。没有文件名的附件不
进入主邮件正文，并维持原先不自动列出、提取或命名的处理方式。

结构化附件的提取保留邮件内容与 MIME 结构，不保证与原始传输字节逐字节一致；
标准序列化过程可能规范化头部折行和换行符。

Base64 和 quoted-printable 编码的附件邮件先进行传输解码后再提取；编码头部
含软换行的邮件也按实际解码内容处理。
