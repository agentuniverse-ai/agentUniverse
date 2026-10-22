# SitemapReader

`SitemapReader` 将网站声明的 XML Sitemap URL 清单转换为 agentUniverse 的
`Document`。它支持标准 `urlset`、嵌套 `sitemapindex`，以及 gzip 压缩的
Sitemap 文件。

为文档站、帮助中心或公共知识门户构建知识库时，Sitemap 通常比普通链接爬取更
可靠：它提供站点发布者声明的规范 URL 清单和更新时间等元数据；本 Reader 则为
网络请求、递归和页面数量增加明确上限。

## 组件注册

内置组件配置如下：

```yaml
name: default_sitemap_reader
description: Bounded XML sitemap and sitemap-index reader for knowledge ingestion
max_urls: 100
max_sitemaps: 20
max_depth: 3
max_sitemap_bytes: 5242880
request_timeout: 20
max_redirects: 5
max_workers: 4
same_origin_only: true
metadata:
  type: READER
  module: agentuniverse.agent.action.knowledge.reader.web.sitemap_reader
  class: SitemapReader
```

## 清单模式

默认使用清单模式，只请求 Sitemap 文件，不请求每个页面：

```python
from agentuniverse.agent.action.knowledge.reader.web.sitemap_reader import (
    SitemapReader,
)

reader = SitemapReader(max_urls=500)
documents = reader.load_data(
    sitemap_url="https://docs.example.com/sitemap.xml",
    include_patterns=[r"/guide/", r"/reference/"],
    exclude_patterns=[r"/archive/"],
    modified_since="2026-01-01",
)
```

每个 URL 对应一个轻量 `Document`，其元数据包含 `sitemap_source`、
`sitemap_depth`、`sitemap_lastmod`、`sitemap_changefreq`、
`sitemap_priority` 和 `content_loaded: false`。使用 `modified_since` 时，
没有合法 `lastmod` 的条目仍会保留，避免因站点元数据不完整而静默漏掉页面。

## 内容模式

设置 `load_content=True` 后，选中的页面会交给现有 `WebPageReader`：

```python
documents = reader.load_data(
    sitemap_url="https://docs.example.com/sitemap.xml",
    load_content=True,
    max_urls=100,
    max_workers=4,
    continue_on_error=True,
    ext_info={"collection": "product-docs"},
)
```

Reader 会保留页面 Reader 原有元数据，并附加 Sitemap 来源信息。动态页面或特定
领域页面也可以注入自定义 Reader：

```python
documents = reader.load_data(
    sitemap_url="https://app.example.com/sitemap.xml",
    load_content=True,
    page_reader=my_rendered_reader,
)
```

即使并行加载，结果仍按 Sitemap 原始顺序返回。`continue_on_error=True` 时不会
隐藏局部失败：最后一个 `Document` 会带有 `sitemap_error_summary: true`，正文
是失败 Sitemap 或页面的 JSON 列表。设置为 `False` 可遇错立即停止。根 Sitemap
失败始终抛出异常。

## 参数

| 参数 | 默认值 | 上限或行为 |
|---|---:|---|
| `load_content` | `false` | 只返回清单，或继续加载页面正文。 |
| `include_patterns` | 无 | 提供后，URL 至少匹配一个正则。 |
| `exclude_patterns` | 无 | 匹配任意正则即排除。 |
| `modified_since` | 无 | 按合法 `lastmod` 应用 ISO-8601 时间过滤。 |
| `continue_on_error` | `true` | 汇总子 Sitemap/页面错误，或立即失败。 |
| `max_urls` | `100` | 1-5,000 个最终页面 URL。 |
| `max_sitemaps` | `20` | 1-100 个 Sitemap 文件。 |
| `max_depth` | `3` | 0-10 层 Sitemap 索引递归。 |
| `max_sitemap_bytes` | 5 MiB | 1 KiB-50 MiB，同时约束压缩前后。 |
| `request_timeout` | 20 秒 | 大于 0 且不超过 120 秒。 |
| `max_redirects` | `5` | 每个 Sitemap 请求允许 0-20 次 HTTP 重定向。 |
| `max_workers` | `4` | 1-16 个页面加载线程。 |
| `same_origin_only` | `true` | 子 Sitemap 和页面限于根 Sitemap 同源。 |
| `page_reader` | `WebPageReader` | 任意 agentUniverse `Reader`。 |
| `ext_info` | 无 | 合并到返回文档的元数据。 |

调用参数只覆盖当前调用，不修改 Reader 实例的默认配置。

## 安全与协议处理

- 只接受不含内嵌账号密码的绝对 HTTP(S) URL；
- Sitemap 索引具备循环检测，页面 URL 按原顺序去重；
- 同时支持带 XML 命名空间和不带命名空间的 Sitemap；
- 通过 gzip 魔数、Content-Type 或 `.gz` 后缀识别压缩内容；
- 压缩响应和解压后内容均受同一个大小上限约束；
- HTTP 重定向受显式配置的次数上限约束；
- XML 解析前拒绝 DTD 和实体声明；
- 默认将跨域子 Sitemap 记录到错误摘要，并过滤跨域页面；
- 不绕过 robots 规则、不调度周期刷新、不渲染 JavaScript，也不作为无界爬虫。

Sitemap 协议本身允许远大于默认值的文件。本 Reader 故意采用较小默认上限，避免
一个误传 URL 触发全站导入。只有在信任并控制目标站点时，才应显式提高上限。
