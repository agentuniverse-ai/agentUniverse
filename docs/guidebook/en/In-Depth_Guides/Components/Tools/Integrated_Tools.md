# Integrated Tools

In the current agentUniverse's sample project, the following tools are integrated.

HTTP-based API tools use the SSRF proxy helper for outbound requests. See [SSRF proxy environment variables](./SSRF_Proxy.md) for `SSRF_PROXY_*` configuration.

## 1. Search Tools

### 1.1 Google Search
[Tool Path](../../../../../../examples/sample_standard_app/intelligence/agentic/tool/google_search_tool.yaml)  
Detailed Configuration Information:

```yaml
name: 'google_search_tool'
description: |
  This tool can be used to perform Google searches. The tool's input is the content you want to search for.
  Example inputs for the tool:
    Example 1: If you want to search for the weather in Shanghai, the tool's input should be: "Shanghai weather today"
    Example 2: If you want to search for the weather in Japan, the tool's input should be: "Japan weather"
tool_type: 'api'
input_keys: ['input']
metadata:
  type: 'TOOL'
  module: 'sample_standard_app.intelligence.agentic.tool.google_search_tool'
  class: 'GoogleSearchTool'
```
To use this API, you must apply for a BING_SUBSCRIPTION_KEY at https://serper.dev and configure it in your environment variables. 
Configuration method:
1. Configure via Python code You must configure: SERPER_API_KEY

```python
import os
os.environ['SERPER_API_KEY'] = 'xxxx'
```
2. Configure via configuration file In the custom_key.toml file located in the config directory of the project, add the configuration:
```toml
SERPER_API_KEY="xxxx"
```


### 1.2 Bing Search 
Currently, it integrates with the official Bing search.
[Tool Path](../../../../../../examples/sample_standard_app/intelligence/agentic/tool/samples/bing_search_tool.yaml)  
Tool configuration:
```yaml
name: 'bing_search_tool'
description: 'demo bing search tool'
tool_type: 'api'
input_keys: ['input']
metadata:
  type: 'TOOL'
  module: 'sample_standard_app.intelligence.agentic.tool.bing_search_tool'
  class: 'BingSearchTool'
```
To use this API, you must apply for BING_SUBSCRIPTION_KEY and configure it in environment variables. 
Configuration method:
1. Configure through Python code
Mandatory configuration: BING_SUBSCRIPTION_KEY
```python
import os
os.environ['BING_SUBSCRIPTION_KEY'] = 'xxxx'
```
2. Configure through configuration file
In custom_key.toml under config directory of the project, add configuration:
```toml
BING_SUBSCRIPTION_KEY="xxxx"
```



### 1.3 Search API
Supports multiple search tools, such as: 
- [Baidu search](../../../../../../examples/sample_standard_app/intelligence/agentic/tool/samples/search_api_baidu_tool.yaml)
- [Bing search](../../../../../../examples/sample_standard_app/intelligence/agentic/tool/samples/search_api_bing_tool.yaml)  
Other search engines also include: Google search, Amazon search, YouTube search, etc. For more information, please refer to: https://www.searchapi.io/
Tool configuration:
```yaml
name: 'search_api_baidu_tool'
description: 'Baidu (Bing) search tool, input is a string of content to be searched, e.g.: input="What is the price of gold?"'
tool_type: 'api'
input_keys: ['input']
engine: 'baidu'
search_type: 'json'
search_params:
  num: 10
metadata:
  type: 'TOOL'
  module: 'sample_standard_app.intelligence.agentic.tool.search_api_tool'
  class: 'SearchAPITool'
```
Parameter description:

search_type: Represents the format of the expected search results, where json represents the expectation for JSON format and common represents the expectation for string format.
search_params: Represents additional parameters that need to be passed to the search engine, such as in Baidu search, num represents the number of returned search results, detailed parameters need to be referenced at [https://www.searchapi.io/].
engine: The search engine you expect to use, including baidu, google, bing, amazon, youtube, ... To use this API, you must apply for SEARCH_API_KEY from the official website ([https://www.searchapi.io/]) and configure it in environment variables.
Configuration method:
You must configure：SEARCHAPI_API_KEY
1. Configure via Python code :
```python
import os
os.environ['SEARCHAPI_API_KEY'] = 'xxxxxx'
```
2. Configure through configuration file
Add configuration in custom_key.toml under the config directory of the project:
```toml
SEARCHAPI_API_KEY="xxxxxx"
```


### 1.4 PubMed Paper Search

The paper list follows the PMID order returned by ESearch for the requested sort and page, even if EFetch returns records in a different order. Missing fetched records are omitted; unrequested or unidentified records are not added to the page. Repeated PMIDs appear once (the first fetched record is used). `total_results` remains the search total, while `returned_results` counts the matched records actually returned. This does not add support for additional EFetch record types.

The PubMed tool uses [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) to search biomedical and life-sciences literature. Basic searches do not require an API key.

[Tool configuration](../../../../../../examples/sample_standard_app/intelligence/agentic/tool/buildin/pubmed_tool.yaml)

Tool configuration:

```yaml
name: 'pubmed_tool'
description: |
  Search PubMed for biomedical and life-sciences papers and return structured metadata.
tool_type: 'api'
input_keys: ['query']
metadata:
  type: 'TOOL'
  module: 'agentuniverse.agent.action.tool.common_tool.pubmed_tool'
  class: 'PubMedTool'
```

Usage example:

```python
from agentuniverse.agent.action.tool.tool_manager import ToolManager

tool = ToolManager().get_instance_obj('pubmed_tool')
result = tool.run(
    query='large language models in medicine',
    max_results=5,
    page=2,
    sort='pub_date',
    mindate='2024-01-01',
    maxdate='2024-12-31',
    datetype='pdat',
)
```

Parameters:

- `query`: Required PubMed keywords or search expression.
- `max_results`: Optional number of papers per page, from 1 to 20. The default is 5.
- `page`: Optional one-based page number. The default is 1. The combination of `page` and `max_results` can address only PubMed's first 9,999 results; the tool rejects larger ranges before sending a request.
- `sort`: Optional result order: `relevance`, `pub_date`, `author`, or `journal`. The default is `relevance`.
- `mindate`, `maxdate`: Optional date-range bounds in `YYYY`, `YYYY-MM`, or `YYYY-MM-DD` format. Supply both values together; the tool rejects an incomplete range because NCBI would not apply the expected filter.
- `datetype`: Optional PubMed date field: `pdat` (publication), `edat` (Entrez), `mdat` (modification), or `crdt` (creation). The default is `pdat`.

The response contains query, paging, and result-count context plus a normalized paper list. A paper can include its PMID, title, authors, abstract, journal and ISSN, publication date and types, keywords, MeSH terms, languages, DOI, and PubMed URL. MeSH entries preserve descriptors, qualifiers, unique identifiers, and major-topic flags. Missing scalar and collection fields use empty values. The tool returns metadata only; it does not download or summarize full text.

Network, HTTP, and parsing failures use a structured `error` field. Errors explicitly reported by NCBI in ESearch JSON or EFetch XML use the `api_error` type and retain NCBI's message so callers can distinguish an empty result from a failed request. You may set `NCBI_EMAIL` and `NCBI_API_KEY`; basic searches continue to work without an API key.

### 1.5 Crossref Scholarly Metadata

The Crossref tool uses the [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) to search scholarly works across disciplines or retrieve publication metadata by DOI. The public API can be used without registration.

[Tool configuration](../../../../../../examples/sample_standard_app/intelligence/agentic/tool/buildin/crossref_tool.yaml)

Tool configuration:

```yaml
name: 'crossref_tool'
description: |
  Search Crossref for scholarly works or retrieve one work by DOI.
tool_type: 'api'
input_keys: ['query']
metadata:
  type: 'TOOL'
  module: 'agentuniverse.agent.action.tool.common_tool.crossref_tool'
  class: 'CrossrefTool'
```

Search example:

```python
from agentuniverse.agent.action.tool.tool_manager import ToolManager

tool = ToolManager().get_instance_obj('crossref_tool')
result = tool.run(
    query='large language models in medicine',
    mode='search',
    max_results=5,
    page=2,
    sort='citation_count',
    order='desc',
    from_pub_date='2020-01-01',
    until_pub_date='2025-12-31',
)
```

DOI lookup example:

```python
result = tool.run(
    query='https://doi.org/10.1128/mbio.01735-25',
    mode='doi',
)
```

Parameters:

- `query`: Required search text in `search` mode, or a DOI, `doi:` identifier, or DOI URL in `doi` mode.
- `mode`: Optional operation mode, either `search` or `doi`. The default is `search`.
- `max_results`: Optional search result count from 1 to 20. The default is 5. DOI mode returns at most one record.
- `page`: Optional one-based search page. The default is 1. The calculated Crossref offset must remain below 10,000.
- `cursor`: Optional deep-paging cursor. Use `*` for the first cursor request, then pass the returned `next_cursor`. Cursor requests require `page` to remain 1, and Crossref cursors expire after five minutes of inactivity.
- `sort`: Optional search sort field. Supported fields are `created`, `deposited`, `indexed`, `is-referenced-by-count`, `issued`, `published`, `published-online`, `published-print`, `references-count`, `relevance`, `score`, and `updated`. Underscores may replace hyphens; `citation_count`, `publication_date`, and `reference_count` are accepted aliases. The default is `relevance`.
- `order`: Optional search order, either `asc` or `desc`. The default is `desc`.
- `from_pub_date`, `until_pub_date`: Optional inclusive publication-date bounds in `YYYY`, `YYYY-MM`, or `YYYY-MM-DD` format. Either bound can be used independently; when both are present, the lower bound cannot be later than the upper bound.

The response preserves operation, query, paging, sorting, date-filter, and result-count context and returns a normalized `works` list. Cursor searches also return `next_cursor`. A work can include DOI, title and subtitle, authors, abstract, journal or conference, publication date, publisher, type, URL, ISSN, ISBN, subjects, language, volume, issue, pages, citation and reference counts, funders, and licenses. Crossref metadata is deposited by publishers and completeness varies by record; missing values use empty strings, empty lists, or zero counts. The tool returns metadata only.

Timeouts, HTTP errors, connection failures, invalid JSON, and Crossref API failures use a structured `error` field. Set the optional `CROSSREF_EMAIL` environment variable to identify requests and use the Crossref polite pool.

### 1.6 Semantic Scholar Discovery and Citation Graphs

The Semantic Scholar tool uses the [Semantic Scholar Academic Graph API](https://api.semanticscholar.org/api-docs/graph) to search papers, retrieve one paper, explore citation and reference relationships, or look up several identifiers in one request. Most endpoints support basic anonymous use. If Semantic Scholar has issued an API key to you, configure it with `S2_API_KEY`.

[Tool configuration](../../../../../../examples/sample_standard_app/intelligence/agentic/tool/buildin/semantic_scholar_tool.yaml)

Tool configuration:

```yaml
name: 'semantic_scholar_tool'
description: |
  Search Semantic Scholar, retrieve paper metadata, explore citation relationships,
  or look up multiple papers in one request.
tool_type: 'api'
input_keys: ['query']
metadata:
  type: 'TOOL'
  module: 'agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool'
  class: 'SemanticScholarTool'
```

Filtered search example:

```python
from agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool import SemanticScholarTool

tool = SemanticScholarTool()
result = tool.execute(
    query='large language models in medicine',
    mode='search',
    max_results=5,
    page=1,
    year='2020-',
    fields_of_study=['Medicine', 'Computer Science'],
    min_citation_count=10,
    open_access_only=True,
)
```

Citation example:

```python
result = tool.execute(
    query='DOI:10.18653/v1/2020.acl-main.447',
    mode='citations',
    max_results=5,
    page=1,
    publication_date_or_year='2020:',
)
```

Batch example:

```python
result = tool.execute(
    query=[
        'DOI:10.18653/v1/2020.acl-main.447',
        'PMID:19872477',
    ],
    mode='batch',
)
```

Parameters:

- `query`: Required search text in `search` mode; one paper identifier in `paper`, `citations`, or `references` mode; or an identifier list in `batch` mode. Supported identifiers include DOI, PMID, PMCID, ArXiv, CorpusId, MAG, ACL, `URL:`, and Semantic Scholar paper IDs. DOI, ArXiv, and Semantic Scholar URLs are accepted.
- `mode`: Optional operation mode: `search`, `paper`, `citations`, `references`, or `batch`. The default is `search`. Citations are papers that cite the target; references are papers cited by the target. Batch mode accepts 1 to 20 unique identifiers and enforces a 32 KiB serialized output limit.
- `max_results`: Optional page size from 1 to 20 for search and relationship modes. The default is 5. Paper mode returns one record; batch size is determined by its identifier list.
- `page`: Optional one-based page for search and relationship modes. Relevance search exposes only the first 1,000 results.
- `year`: Optional search-only filter in `YYYY`, `YYYY-YYYY`, `YYYY-`, or `-YYYY` form.
- `publication_date_or_year`: Optional search and citation filter. Accepts `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, or an inclusive colon-delimited range such as `2020-01:2024-06-30`, `2020:`, or `:2024-06`. Do not combine it with `year` in search mode. Citation mode applies it to citing papers; the references endpoint does not support this filter.
- `publication_types`: Optional search-only publication type or list, such as `Review`, `JournalArticle`, `ClinicalTrial`, `Conference`, or `Dataset`.
- `fields_of_study`: Optional search-only field or list, such as `Medicine`, `Computer Science`, `Biology`, or `Physics`.
- `venue`: Optional search-only venue name or list.
- `min_citation_count`: Optional non-negative search-only citation threshold.
- `open_access_only`: Optional search-only flag. Set it to `true` to require a public PDF.

Every mode returns a normalized `papers` list. Full paper metadata can include Semantic Scholar paper ID, CorpusId, external identifiers, title, authors, abstract, venue, publication date and year, publication types, fields of study, citation and reference counts, open-access status and PDF, and URL. Citation and reference entries also include relationship `contexts`, `intents`, and `is_influential` metadata.

Search and relationship modes return `page`, `offset`, and `next_offset`. Citation endpoints do not report a total, so relationship-mode `total_results` is `null`. Batch mode returns `requested_results`, `not_found_ids`, and compact paper fields; titles are capped at 500 characters and venues at 200 characters. Use `paper` mode when full metadata is required. Missing fields use empty values, and the tool never downloads or summarizes full text.

Semantic Scholar relevance search does not expose server-side sorting, so the tool does not misleadingly reorder a single local page. For large offline workloads, use the bulk search or dataset APIs instead of increasing an agent tool's response size. Network and API failures use a structured `error` field and preserve operation context. Anonymous users share a rate limit and may receive HTTP 429; retry later when limited.

## 2. Code Tool

### 2.1 PythonRepl
[Tool Path](../../../../../../examples/sample_standard_app/intelligence/agentic/tool/buildin/python_repl_tool.yaml)  
This tool can execute a piece of Python code, the configuration information of the tool:  
```yaml
name: 'python_runner'
description: 'The tool can execute Python code, which can be directly run in PyCharm. The input to the tool must be valid Python code. If you want to view the execution result of the tool, you must use print(...) to print the content you want to view in the Python code.
  Example of tool input:
    When you want to calculate what 1 + 3 equals, the input to the tool should be:
        ```py 
        print(1+3)
        ```
      When you want to get information about the Baidu page, the input to the tool should be:
        ```py 
        import requests
        resp=requests.get("https://www.baidu.com")
        print(resp.content)
        ```'
tool_type: 'api'
input_keys: ['input']
# SECURITY: see the note below.
allow_code_execution: true
metadata:
  type: 'TOOL'
  module: 'agentuniverse.agent.action.tool.common_tool.python_repl'
  class: 'PythonREPLTool'
```

> **Security warning – opt-in code execution**  
> `PythonREPLTool` runs the code an agent produces **directly on the host** through
> Python's `exec`. There is **no** sandboxing, subprocess isolation, or resource
> limiting, so a prompt injection that reaches this tool escalates to arbitrary
> code execution. The tool is therefore **disabled by default**: until you set
> `allow_code_execution: true`, `execute()` refuses to run code and returns an
> instructive error instead.
>
> Only opt in (`allow_code_execution: true`) in a fully trusted, isolated
> environment, and never equip an agent that ingests untrusted input (documents,
> web pages, chat messages) with this tool. Do not enable it in production.

This tool can be used directly without any key.


## 3.HTTP Tool

### 3.1 HTTP GET
[Tool Path](../../../../../../examples/sample_standard_app/intelligence/agentic/tool/request_get_tool.yaml)
The tool can send a GET request, with its configuration information being:
```yaml
name: 'requests_get'
description: 'A portal to the internet. Use this when you need to get specific
    content from a website. Input should be a  url (i.e. https://www.google.com).
    The output will be the text response of the GET request.
        ```'
headers:
  content-type: 'application/json'
method: 'GET'
json_parser: false
response_content_type: json
tool_type: 'api'
input_keys: ['input']
metadata:
  type: 'TOOL'
  module: 'sample_standard_app.intelligence.agentic.tool.request_tool'
  class: 'RequestTool'
```
Configuration to Refer to When Sending a POST Request：
```yaml
name: 'requests_post'
# description copy from langchain RequestPOSTTool
description: 'Use this when you want to POST to a website.
    Input should be a json string with two keys: "url" and "data".
    The value of "url" should be a string, and the value of "data" should be a dictionary of 
    key-value pairs you want to POST to the url.
    Be careful to always use double quotes for strings in the json string
    The output will be the text response of the POST request.
        ```'
headers:
  content-type: 'application/json'
method: 'POST'
json_parser: true
response_content_type: json
tool_type: 'api'
input_keys: ['input']
metadata:
  type: 'TOOL'
  module: 'sample_standard_app.intelligence.agentic.tool.request_tool'
  class: 'RequestTool'
```
Parameter Description:
    method: the method of the request, such as GET, POST, PUT, etc.
    headers: the HTTP headers necessary for sending the request.
    json_parse: indicates whether the input parameters should be serialized as JSON and sent in the request body (True for POST requests) or not (False for GET requests, where parameters are typically sent as a query string).
    response_content_type: the output format for the HTTP request result. If set to 'json', the result will be returned in JSON format; if set to 'text', it will be returned as plain text.
This tool can be used directly without  requiring any keys.


## 4. Office Tools

### 4.1 PowerPoint

`PowerPointTool` creates, appends to, reads, and inspects `.pptx` files from
structured data. Install the optional Office dependency before using it:

```bash
pip install "agentUniverse[office_ext]"
# source checkout alternative: pip install python-pptx
```

The built-in component configuration is
[`powerpoint_tool.yaml`](../../../../../../agentuniverse/agent/action/tool/common_tool/powerpoint_tool.yaml):

```yaml
name: powerpoint_tool
description: Create, append to, read, or inspect PowerPoint PPTX presentations from structured slide data.
tool_type: api
metadata:
  type: TOOL
  module: agentuniverse.agent.action.tool.common_tool.powerpoint_tool
  class: PowerPointTool
input_keys: [mode, file_path]
base_dir: .
max_read_bytes: 20971520
max_write_bytes: 20971520
max_uncompressed_bytes: 104857600
max_archive_entries: 5000
max_slides: 100
max_text_chars: 50000
```

Create a presentation:

```python
from agentuniverse.agent.action.tool.tool_manager import ToolManager

tool = ToolManager().get_instance_obj("powerpoint_tool")
result = tool.run(
    mode="create",
    file_path="reports/q2-review.pptx",
    overwrite=False,
    metadata={"title": "Q2 Review", "author": "Finance Agent"},
    slides=[
        {
            "title": "Q2 Review",
            "subtitle": "Revenue and regional performance",
            "notes": "Open with the consolidated revenue result.",
        },
        {
            "title": "Highlights",
            "bullets": [
                "Revenue grew 20% year over year",
                {"text": "APAC led growth", "level": 1},
            ],
            "table": [
                ["Metric", "Q2", "YoY"],
                ["Revenue", "$123M", "+20%"],
            ],
        },
    ],
)
```

Use `mode="append"` with another `slides` list to add slides to an existing
deck. `mode="read"` returns bounded slide text, tables, and speaker notes;
`mode="info"` returns file metadata and per-slide shape/table information.
Create mode can also receive a `template_path` underneath `base_dir`; existing
template slides are retained and the generated slides are appended.

Supported slide fields are:

- `title`, `subtitle`, and `notes`: strings.
- `bullets`: strings or `{ "text": "...", "level": 0 }` objects. Levels are
  restricted to 0–8.
- `table`: a two-dimensional array of scalar cell values.
- `layout`: `auto`, `title`, `title_content`, `section`, `title_only`, or
  `blank`.

The tool confines `file_path` and `template_path` to `base_dir`, including
resolved symlinks. It rejects oversized files, slide/table/text limits, unknown
input fields, and implicit overwrites. Writes are atomic: the new presentation
is saved and size-checked in the destination directory before it replaces the
target, so a failed write does not corrupt an existing deck. The `read` result
is capped by the configured slide, shape, table-row, table-column, and shared
text budgets, and reports `truncated: true` when traversal stops early.

### 4.2 WordDocumentTool

`WordDocumentTool` creates, appends to, reads, and inspects DOCX files with structured `heading`, `paragraph`, `bullet`, `table`, and `page_break` blocks. Install `agentUniverse[office_ext]` or `python-docx`, then resolve the built-in `word_document_tool` component. Paths and templates are confined to `base_dir`; archive expansion, file, block, table, and text limits are enforced, and writes are atomic. The existing `WriteWordDocumentTool` remains available for backward compatibility.

## EmailDocumentTool

`EmailDocumentTool` provides offline RFC 5322 `.eml` workflows with `create`, `read`, `info`, and `extract` modes. It can build multipart text/HTML messages, attach files, inspect headers and bodies, and extract selected attachments.

```python
from agentuniverse.agent.action.tool.common_tool.email_document_tool import EmailDocumentTool

tool = EmailDocumentTool(base_dir="/srv/agent-files")
tool.execute(
    mode="create",
    file_path="report.eml",
    headers={"from": "agent@example.com", "to": "user@example.com", "subject": "Report"},
    text_body="The report is attached.",
    attachments=["report.pdf"],
)
```

The tool performs no network or mailbox access. It confines paths to `base_dir`, rejects header injection and unsafe/duplicate attachment names, bounds headers, bodies, attachment counts and bytes, preflights extraction destinations, and uses atomic writes.

## SecureArchiveTool

`SecureArchiveTool` provides bounded archive operations for agent workflows without external dependencies. It supports ZIP, TAR, TAR.GZ, and TGZ files with four modes: `create`, `list`, `extract`, and `info`.

```python
from agentuniverse.agent.action.tool.common_tool.secure_archive_tool import SecureArchiveTool

tool = SecureArchiveTool(base_dir="/srv/agent-files")
tool.execute(mode="create", file_path="reports.zip", input_paths=["reports"])
tool.execute(mode="extract", file_path="reports.zip", output_dir="restored", members=["reports/q2.txt"])
```

All paths are confined to `base_dir`. Extraction rejects absolute/traversal paths, links, special TAR files, encrypted ZIPs, duplicate members, excessive compression ratios, and configured size/count limits. Destinations are preflighted before extraction and files are written through same-directory temporary files.

## 4. PDF Tool

The built-in `PDFTool` supports bounded `merge`, `split`, `rotate`, `extract`, and `info` operations. Install `agentUniverse[pdf_ext]` or `pypdf`. All source and destination paths are confined to `base_dir`; page, input-file, read/write-size, and extracted-text budgets are enforced. Writes are atomic and never replace an existing file unless `overwrite=true` is explicit.

## NVD CVE Tool

`NvdCveTool` queries the official National Vulnerability Database CVE API 2.0. A
`CVE-YYYY-NNNN` query performs an exact identifier lookup; any other query searches
vulnerability descriptions. Keyword calls support a bounded `max_results`, a
zero-based `start_index`, and optional exact-phrase matching.

```python
from agentuniverse.agent.action.tool.common_tool.nvd_cve_tool import NvdCveTool

tool = NvdCveTool()
record = tool.execute(query="CVE-2021-44228")
results = tool.execute(
    query="Apache HTTP Server",
    max_results=5,
    exact_match=True,
)
```

Results normalize the highest available CVSS v4/v3/v2 metric, CWE weaknesses,
references, affected CPE criteria, CVE tags, CISA KEV fields, record status, and
the NVD detail URL. Descriptions and nested collections have explicit limits.
Each execution makes one request; the tool is not a bulk dataset downloader.

Anonymous use follows NVD's public rate limit. Set `NVD_API_KEY` to send a key in
the `apiKey` header for the higher authenticated limit. Timeouts, HTTP failures,
rate limits, malformed JSON, and invalid response shapes return a structured
`error` without exposing the key. Every response includes the NVD source link and
the attribution notice required by NVD API guidance.

## deps.dev Package Intelligence Tool

`DepsDevPackageTool` uses the official deps.dev Open Source Insights API to
inspect one exact package version. It supports Go, RubyGems, npm, Cargo, Maven,
PyPI, and NuGet package coordinates.

```python
from agentuniverse.agent.action.tool.common_tool.deps_dev_package_tool import DepsDevPackageTool

tool = DepsDevPackageTool()
metadata = tool.execute(
    name="jinja2",
    system="PYPI",
    version="2.4.1",
)
graph = tool.execute(
    name="react",
    system="NPM",
    version="18.2.0",
    mode="dependencies",
    max_nodes=100,
    max_edges=200,
)
```

The default `version` mode returns the canonical package key, publication and
deprecation state, licenses, directly affecting OSV advisory IDs, safe external
links, SLSA provenance, attestations, registries, related projects, and project
status. The `dependencies` mode returns a resolved graph for npm, Cargo, Maven,
and PyPI. Node indices are preserved, and edges whose endpoints are not in the
bounded node result are omitted so the returned graph cannot contain dangling
references.

The tool uses fixed endpoints, percent-encodes package coordinates, makes one
request per call, and needs no API key. Inputs, scalar text, URLs, collections,
nodes, edges, and node errors are bounded; collection counts and truncation
metadata expose omitted data. Timeout, connection, HTTP, not-found, rate-limit,
JSON, and response-shape failures are structured. Package metadata and graph
text are untrusted external data rather than agent instructions, and non-HTTP(S)
links are omitted.

## OpenSSF Scorecard Tool

`OpenSsfScorecardTool` retrieves a published repository security-posture result
from the official OpenSSF Scorecard API. It accepts `owner/repo`,
`github.com/owner/repo`, or an HTTPS GitHub repository URL. An exact 40-character
commit SHA can optionally select a specific published analysis.

```python
from agentuniverse.agent.action.tool.common_tool.openssf_scorecard_tool import OpenSsfScorecardTool

tool = OpenSsfScorecardTool()
result = tool.execute(
    repository="ossf/scorecard",
    max_checks=30,
    max_details_per_check=10,
)
```

The normalized result contains the analysis date, analyzed repository and
commit, Scorecard version, aggregate score, and individual checks with their
scores, reasons, evidence details, and safe documentation links. Check counts,
evidence counts, text truncation, and omitted links remain visible in the
returned metadata.

Repository coordinates are validated and percent-encoded before one request to
a fixed endpoint. The tool rejects credentials, non-GitHub URLs, extra path
segments, dot path segments, malformed commits, non-finite scores, and invalid
response shapes. Inputs, checks, evidence, metadata, text, and URLs are bounded;
non-HTTP(S) links are omitted. Timeout, connection, HTTP, not-found, rate-limit,
and JSON failures return structured errors.

A Scorecard result measures repository security practices at a point in time;
it does not prove that the repository is vulnerability-free. Upstream reasons,
evidence, metadata, and links are untrusted data rather than agent instructions.

## Command Result Lookup

`RunCommandTool` returns an integer `thread_id` for each invocation. Treat this
legacy field as an opaque command handle, and pass it unchanged to
`CommandStatusTool.execute(thread_id)` to retrieve that invocation's status and
output. It is not an operating-system thread ID. Later commands, including
commands run on the same worker thread or another tool instance, receive their
own handles and do not replace earlier results.

Handles and results are local to the current Python process and do not survive
restarts or transfer between server processes. Command execution requires the
existing `allow_command_execution=True` opt-in.

## ConsoleAnsiTool

`ConsoleAnsiTool` analyzes terminal output that contains ANSI escape
sequences. It implements the ECMA-48 §5.4 control-function grammar plus the
xterm ctlseqs extensions with a hand-rolled state machine (per-state
character-class runs, linear scanning, stdlib only), so agents can understand,
clean, or safely relay colored CLI output, progress bars, prompts with OSC 8
hyperlinks, and window titles.

```python
from agentuniverse.agent.action.tool.common_tool.console_ansi_tool import ConsoleAnsiTool

tool = ConsoleAnsiTool()
result = tool.execute(mode="strip", text="\x1b[1;31mERR\x1b[0m: timeout")
# -> {"clean": "ERR: timeout", "removed_count": 2, "classes_removed": {"sgr": 2}, ...}
inventory = tool.execute(mode="classify", text=terminal_dump)
safe = tool.execute(mode="sanitize", text=terminal_dump, keep="safe")
note = tool.execute(mode="explain", sequence="\x1b[?25l")
```

`strip` returns the plain text with every escape run removed (visible
characters preserved; bare C0 controls such as `\r` belong to the text layer
and are kept), the removed count, per-category counts, and flags for
incomplete trailing sequences (`truncated_at_eof` plus the bounded pending
bytes) and 8-bit C1 detection. `classify` returns an inventory of
`{category, code, human, occurrences, span_samples}` entries over the
categories `sgr | cursor | erase | scroll | mode | osc-link | osc-title |
other`, with an embedded SGR table (30-37/40-47, 90-97/100-107 bright,
`38;5;n` and `38;2;r;g;b` extended colors named through the xterm palette
arithmetic, resets and style clears), cursor operations, ED/EL/ECH erase
semantics, SM/RM and DEC private modes (`?25` cursor visibility, `?1049`
alternate screen, mouse and bracketed-paste modes), OSC 8 hyperlinks with the
URL and visible label extracted, and OSC 0/1/2 titles. `sanitize` re-emits
kept sequences as their original bytes (`keep: none | sgr-only | safe`, where
safe keeps SGR plus hyperlinks), so kept output is canonical passthrough with
no rewriting. `explain` decomposes a single sequence into introducer, private
marker, parameters, intermediates, and final byte, and states where xterm and
ECMA-48 differ (SGR 21, ECH, DEC private modes, OSC BEL termination, 8-bit C1
in UTF-8 streams).

Documented deterministic rules: an OSC run without BEL/ST is consumed to the
end of input and flagged; DCS/APC/PM/SOS data is consumed to ST; runs
abandoned by an out-of-grammar byte are dropped and scanning resumes at that
byte; a C1 introducer that cannot complete a sequence is kept as literal text
and reported via `c1_8bit_detected` because C1 bytes cannot occur in valid
UTF-8. All results are deterministic; input size, inventory codes, span
samples, and pending bytes are capped by tunables. Terminal output is
untrusted external data, not agent instructions; the tool never executes
sequences, it only parses them.
