# GitHub工具使用示例

## 概述

GitHub工具提供了强大的GitHub API集成功能，支持搜索仓库、用户、问题和代码，以及获取特定仓库的详细信息。

## 功能特性

- **仓库搜索**: 根据关键词搜索GitHub仓库，支持按星标、分叉、更新时间等排序
- **用户搜索**: 搜索GitHub用户，支持按关注者、仓库数量等排序
- **问题搜索**: 搜索GitHub问题，支持按创建时间、更新时间、评论数等排序
- **代码搜索**: 搜索GitHub代码片段
- **仓库信息**: 获取特定仓库的详细信息

## 配置

### 环境变量

```bash
# 设置GitHub API密钥（可选，但推荐设置以提高API限制）
export GITHUB_API_KEY="your_github_token_here"
```

### 工具配置

```yaml
name: github_tool
description: GitHub仓库、用户、问题和代码搜索工具
class_path: agentuniverse.agent.action.tool.common_tool.github_tool.GitHubTool
```

## 使用示例

### 1. 搜索仓库

```python
# 搜索Python相关的仓库
result = github_tool.execute(
    mode="repository",
    query="python machine learning",
    sort="stars",
    order="desc"
)
```

### 2. 搜索用户

```python
# 搜索GitHub用户
result = github_tool.execute(
    mode="user",
    query="torvalds",
    sort="followers",
    order="desc"
)
```

### 3. 搜索问题

```python
# 搜索特定仓库的问题
result = github_tool.execute(
    mode="issue",
    query="bug repo:facebook/react",
    sort="created",
    order="desc"
)
```

### 4. 搜索代码

```python
# 搜索代码片段
result = github_tool.execute(
    mode="code",
    query="def hello_world language:python",
    sort="indexed",
    order="desc"
)
```

### 5. 获取仓库信息

```python
# 获取特定仓库的详细信息
result = github_tool.execute(
    mode="repo_info",
    owner="facebook",
    repo="react"
)
```

## 返回数据格式

### 仓库搜索结果

```json
{
  "name": "tensorflow",
  "full_name": "tensorflow/tensorflow",
  "description": "An Open Source Machine Learning Framework",
  "html_url": "https://github.com/tensorflow/tensorflow",
  "stars": 180000,
  "forks": 88000,
  "language": "C++",
  "created_at": "2015-11-07T01:08:11Z",
  "updated_at": "2024-01-20T10:30:00Z",
  "owner": {
    "login": "tensorflow",
    "avatar_url": "https://avatars.githubusercontent.com/u/15658638?v=4",
    "html_url": "https://github.com/tensorflow"
  },
  "topics": ["machine-learning", "deep-learning", "neural-networks"]
}
```

### 用户搜索结果

```json
{
  "login": "torvalds",
  "id": 1024025,
  "avatar_url": "https://avatars.githubusercontent.com/u/1024025?v=4",
  "html_url": "https://github.com/torvalds",
  "type": "User",
  "site_admin": false
}
```

### 问题搜索结果

```json
{
  "title": "Bug: Component not rendering correctly",
  "number": 12345,
  "html_url": "https://github.com/facebook/react/issues/12345",
  "state": "open",
  "created_at": "2024-01-15T09:00:00Z",
  "updated_at": "2024-01-20T15:30:00Z",
  "comments": 5,
  "user": {
    "login": "username",
    "avatar_url": "https://avatars.githubusercontent.com/u/12345?v=4"
  },
  "labels": ["bug", "priority-high"],
  "repository": {
    "name": "react",
    "full_name": "facebook/react"
  }
}
```

## 错误处理

工具会自动处理以下错误情况：

- **API限制**: 当API调用次数超过限制时，会返回相应的错误信息
- **网络超时**: 请求超时时会返回超时错误
- **资源不存在**: 当搜索的资源不存在时，会返回404错误
- **参数错误**: 当必需参数缺失时，会返回参数错误信息

## 注意事项

1. **API限制**: GitHub API有速率限制，建议设置API密钥以提高限制
2. **搜索语法**: 可以使用GitHub的搜索语法来精确搜索
3. **结果数量**: 默认最多返回10个结果，可以通过配置调整
4. **认证**: 虽然API密钥是可选的，但建议设置以获得更高的API限制

## 依赖

- `requests`: 用于HTTP请求
- `pydantic`: 用于数据验证
- `agentuniverse`: AgentUniverse框架

## 许可证

本工具遵循AgentUniverse项目的许可证。
