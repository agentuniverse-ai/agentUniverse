# 固定 Git 提交快照 Reader

`GitSnapshotReader` 从明确指定的**本地仓库完整 commit ID**读取 UTF-8 原文，生成
带仓库标签、commit、blob、路径和行范围的 Document。它不读取当前工作目录内容，
不 checkout、不修改暂存区，也不自动 clone/fetch。与读取当前单个文件的 CodeReader、
解析日志的 GitLogTool 范围不同，不改变默认 Reader 路由。

## 配置与使用

需要可信 Git（支持 `--no-lazy-fetch`）和 Python >=3.10；本地验证版本为
Git 2.54.0.windows.1、Python 3.10/3.12。不增加 Python 依赖，不绕过仓库所有权检查。
旧 Git 不支持必要参数时失败，不悄悄退回可能联网的读取方式。

复制 `agentuniverse/agent/action/knowledge/reader/file/git_snapshot_reader.yaml.example`
到应用扫描目录并改为 `.yaml`，配置 include/exclude、分块及资源限制。
创建 `manuals.gitsnapshot` JSON：

```json
{
  "repository_path": "./local-checkout",
  "commit": "替换为完整commit对象ID",
  "repository_id": "team/project"
}
```

占位符不能直接运行。先在所选仓库 `git rev-parse HEAD` 获取并确认完整 ID；
不接受分支、缩写哈希或 annotated tag 对象。相对路径按清单所在目录解析。
清单最多 8,192 字节，仅允许上述三个字符串字段，拒绝重复/未知键。
清单会选择本地文件访问范围，应作为可信应用配置管理。

Knowledge 设置 `readers={"gitsnapshot": "git_snapshot_reader"}` 和已注册 Store，
即可 `insert_knowledge(source_path="/absolute/path/manuals.gitsnapshot")`，再正常查询。
SQLiteStore 仍需按原有要求配置 keyword extractor。测试贯通真实 YAML 注册、Git、
JiebaKeywordExtractor、SQLite 和公开 Knowledge 接口，仅隔离 tracing。
Knowledge 既有的异常日志行为不变；读入新 commit 不会自动删除旧快照，需独立索引或
明确的来源同步策略，不能把本 Reader 当增量同步事务。

需要完整排除报告时：

```python
reader = GitSnapshotReader(include=["docs/*.md", "src/*.py"], lines_per_document=100)
report = reader.read_snapshot("/local/repo", full_commit_id, "team/project")
documents, skipped = report.documents, report.skipped
```

普通 `load_data(manifest_path)` 只返回 Document 列表。每条的 `metadata.git_snapshot`
包含仓库标签、commit/blob、相对路径、起止行号、编码、排除计数；完整排除原因见 report。
标签由用户保证跨仓库唯一且不含秘密，不保存远端凭证或本机绝对路径。
稳定 ID 由标签、commit、路径、blob 和行范围生成；目录搬迁不影响，同一内容改名或
换 commit 会产生不同 ID。blob 哈希核验代表内容完整性，不代表签名或作者身份验证。

## 范围和失败处理

- 行号按 LF 分隔计算，保留 CRLF/LF 和结尾换行；Unicode 分隔符不额外算一行。
  后续处理器若改写文本，应负责修正来源行范围。
- include 默认 `*.md/*.txt/*.py`（三个独立模式），使用整条相对路径的大小写敏感
  fnmatch；`*` 可跨 `/`，exclude 优先。这不是 Gitignore 语义。
- 默认排除常见 `.env`/密钥路径，但**不是秘密扫描器**；外部入库前自行审核内容。
- 符号链接、子模块不跟随；NUL 二进制、非 UTF-8 内容/路径、空文件、LFS 指针
  显式列入排除报告，不下载 LFS。只用 UTF-8/NUL 规则不能识别所有非文本格式，
  因此应收窄 include。全部排除时返回空列表，不算已经完整收录。
- 默认 200 行/块、5,000 块、2,000 个树条目（含被排除条目）、树输出 2 MB、
  单 blob 2 MB、所选原始内容总计 20 MB；超限整次失败，不返回不完整语料。
- 单命令 10 秒、总预算 60 秒，读取时限制 stdout，超时终止并回收子进程。
  这不是操作系统级隔离或精确内存上限。每个 blob 启动一次 Git，大仓库应先基准测试，
  不能仅因为窄 include 就忽略树大小限制。

使用 `rev-parse`、`ls-tree -z`、`cat-file blob`，不使用 textconv/smudge、不运行源码或
仓库钩子，忽略 replacement refs；隔离继承的 Git 环境和全局/系统配置，禁止协议与
懒加载获取。缺对象时失败，请在 Reader 外自行获取。仓库本地配置和对象库仍被视为
可信输入；本功能不是运行不可信仓库的安全沙箱。

测试命令和详细契约见[英文说明](../../../../en/In-Depth_Guides/Tutorials/Knowledge/GitSnapshotReader.md)。
覆盖真实多提交、重命名、脏工作区、bare clone、符号链接/gitlink、SHA-256、换行、缺对象、
确定性和资源限制，以及 Knowledge 查询返回精确来源。超时进程清理使用受控测试替身。
