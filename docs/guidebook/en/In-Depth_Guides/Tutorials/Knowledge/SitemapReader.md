# SitemapReader

`SitemapReader` turns a site's declared XML sitemap inventory into
agentUniverse `Document` objects. It supports both standard URL sets and nested
sitemap indexes, including gzip-compressed sitemap files.

This is preferable to generic link crawling when building a knowledge base from
a documentation site or help center: the sitemap provides the publisher's
canonical URL inventory and optional update metadata, while the reader adds
strict application-level bounds.

## Component registration

The built-in component is registered by:

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

## Inventory mode

Inventory mode is the default and fetches only sitemap files. It returns one
lightweight `Document` per selected page URL:

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

Each document contains the URL as text and records `sitemap_source`,
`sitemap_depth`, `sitemap_lastmod`, `sitemap_changefreq`,
`sitemap_priority`, and `content_loaded: false` in metadata. Entries without a
valid `lastmod` remain included when `modified_since` is used, preventing an
incremental import from silently losing pages with incomplete metadata.

## Content mode

Set `load_content=True` to load every selected page through the existing
`WebPageReader`:

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

The reader preserves page-reader metadata and adds sitemap provenance. A custom
`Reader` can be injected for dynamic pages or domain-specific extraction:

```python
documents = reader.load_data(
    sitemap_url="https://app.example.com/sitemap.xml",
    load_content=True,
    page_reader=my_rendered_reader,
)
```

Page results are returned in sitemap order even when multiple workers are used.
When `continue_on_error=True`, partial failures are not hidden: the final
`Document` has `sitemap_error_summary: true` and a JSON list of failed sitemap
or page URLs. Set it to `False` for fail-fast ingestion. Root sitemap failures
always raise.

## Parameters

| Parameter | Default | Bound / behavior |
|---|---:|---|
| `load_content` | `false` | Inventory-only or delegated page loading. |
| `include_patterns` | none | URL must match at least one regex when provided. |
| `exclude_patterns` | none | Any matching regex excludes the URL. |
| `modified_since` | none | ISO-8601 date/time filter using valid `lastmod`. |
| `continue_on_error` | `true` | Summarize nested/page failures or fail fast. |
| `max_urls` | `100` | 1-5,000 selected page URLs. |
| `max_sitemaps` | `20` | 1-100 fetched sitemap files. |
| `max_depth` | `3` | 0-10 sitemap-index recursion depth. |
| `max_sitemap_bytes` | 5 MiB | 1 KiB-50 MiB, compressed and decompressed. |
| `request_timeout` | 20 s | Greater than 0 and at most 120 seconds. |
| `max_redirects` | `5` | 0-20 HTTP redirects per sitemap request. |
| `max_workers` | `4` | 1-16 page-loading workers. |
| `same_origin_only` | `true` | Restrict child sitemaps and pages to root origin. |
| `page_reader` | `WebPageReader` | Any agentUniverse `Reader`. |
| `ext_info` | none | Metadata merged into returned documents. |

Per-call bounds override component defaults only for that call; the reader
instance is not mutated.

## Safety and protocol behavior

- Only absolute HTTP(S) URLs without embedded credentials are accepted.
- Sitemap indexes are cycle-safe and page URLs are deduplicated in source order.
- Both namespace-qualified and namespace-free XML are accepted.
- Gzip is detected by magic bytes, content type, or `.gz` suffix.
- Compressed responses and decompressed payloads use the same configured size
  bound.
- HTTP redirects are followed only up to the configured explicit bound.
- DTD and entity declarations are rejected before XML parsing.
- Cross-origin child sitemaps are reported in the error summary by default;
  cross-origin page entries are filtered.
- `SitemapReader` does not bypass robots rules, schedule refresh jobs, render
  JavaScript, or act as an unbounded crawler.

The Sitemap protocol itself permits much larger files. The reader intentionally
uses smaller defaults so an accidental URL cannot trigger a site-wide import.
Raise the limits explicitly only for a site you trust and control.
