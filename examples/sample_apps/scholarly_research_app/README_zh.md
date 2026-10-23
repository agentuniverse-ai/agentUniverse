# 学术证据研究智能体

本示例演示如何将 agentUniverse 内置的 PubMed、Crossref 与 Semantic Scholar
工具组合成一个可追溯的证据研究流程。检索在查询时完成，不需要爬虫、向量库或
本地语料库。

## 示例解决的问题

三个来源使用不同的标识符和元数据结构。若把原始结果直接交给大模型，容易出现
论文重复、引用不一致以及检索覆盖缺口被隐藏等问题。`ScholarlyEvidenceTool`
提供了一层轻量编排：

- 并行检索三个来源，并隔离单一来源故障；
- 统一 DOI、PMID、Semantic Scholar Paper ID、作者、日期和 URL；
- 优先按 DOI、其次按 PMID 去重，缺少标识符时使用规范化标题；
- 保留每个贡献来源及对应记录 URL；
- 限制单源结果数、最终证据数、文本长度和作者数；
- 分配稳定的 `E1`、`E2` 等证据编号，供智能体生成可核查引用。

仅有标题的记录不会把 DOI 或 PMID 冲突的两篇论文合并；每次合并后都会重新检查
标识符兼容性。格式错误的来源或 PDF 链接会被单独忽略，不丢弃其他有效证据；
有效的 DOI 或 PMID 仍可生成备用来源链接。

提示词要求智能体公开各来源状态，只引用返回的证据编号，明确表达不确定性，
并说明元数据和摘要不能替代全文质量评价。

## 架构

```text
研究问题
   |
   v
ScholarlyEvidenceTool
  |-- PubMedTool ---------|
  |-- CrossrefTool -------|--> 标准化 --> 去重 --> 有界证据集
  `-- SemanticScholarTool-|
                                      |
                                      v
                              ReAct 证据综合智能体
```

## 配置

先按照项目主文档安装 agentUniverse。通过环境变量设置 `DASHSCOPE_API_KEY`，
或替换 `config/custom_key.toml` 中的占位值。三个学术来源无需密钥即可使用；
可选的 `NCBI_EMAIL`、`NCBI_API_KEY`、`CROSSREF_EMAIL` 和 `S2_API_KEY`
有助于请求标识或提高限额。

请勿提交真实凭据。

## 运行离线测试

测试会模拟网络返回，不需要 API 密钥：

```bash
cd examples/sample_apps
python -m unittest scholarly_research_app.intelligence.test.test_scholarly_evidence_tool
```

## 交互式运行

```bash
cd examples/sample_apps
python -m scholarly_research_app.intelligence.test.scholarly_research_agent_demo
```

示例问题：

```text
老年人的睡眠时长与认知衰退之间有哪些研究证据？
```

## 启动 Web 服务

```bash
cd examples/sample_apps
python -m scholarly_research_app.bootstrap.intelligence.server_application
```

agentUniverse 默认 Web 服务地址为 `http://localhost:8888`。

## 输出约定与边界

`source_status` 明确区分每个来源的成功、无结果和失败状态。`evidence` 仅包含
经过限制和去重的记录，每条记录都具有 `evidence_id`、标准化元数据、
`identifiers`、`sources` 与 `source_urls`。`truncated` 表示仍有去重后的记录
因数量上限未返回。

本项目是发现与综合示例，不是完整的系统综述流程。正式综述仍需预先制定方案、
保存各来源可复现检索式、筛选、获取全文、评价偏倚风险并由领域专家判断。
健康相关输出仅供信息参考，不能替代医疗建议。

English documentation: [README.md](README.md)
