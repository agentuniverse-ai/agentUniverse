# Integrated Tools

In the current agentUniverse's sample project, the following tools are integrated.

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
## TabularDataTool

`TabularDataTool` provides bounded, deterministic workflows for CSV, TSV, and JSONL datasets. It can create or read datasets, calculate per-column profiles, and transform rows with structured filters, projection, numeric-aware sorting, deduplication, limits, and format conversion.

```python
from agentuniverse.agent.action.tool.common_tool.tabular_data_tool import TabularDataTool

tool = TabularDataTool(base_dir="/srv/agent-files")
tool.execute(
    mode="transform",
    file_path="sales.csv",
    output_path="large-orders.jsonl",
    filters=[{"column": "amount", "operator": "gte", "value": 1000}],
    select_columns=["customer", "amount"],
    sort_by="amount",
    descending=True,
)
```

The tool does not evaluate code or expressions. Paths, file size, generated size, rows, columns, cells, output context, profiling cardinality, and `in`-filter values are bounded, and writes are atomic. Profiles count every occurrence of retained values; when distinct cardinality exceeds the configured map, `distinct_count` becomes `null`, a truthful lower bound is returned, and top values are marked approximate. The entire serialized profile is constrained by `max_output_chars`.
