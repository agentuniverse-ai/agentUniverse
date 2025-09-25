# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/20 10:00
# @Author  : Assistant
# @Email   : assistant@example.com
# @FileName: github_tool.py

from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import Field
import requests
import time
from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.annotation.retry import retry
from agentuniverse.base.util.env_util import get_from_env


class GitHubSearchMode(Enum):
    """GitHub搜索模式枚举"""
    REPOSITORY = "repository"  # 搜索仓库
    USER = "user"  # 搜索用户
    ISSUE = "issue"  # 搜索问题
    CODE = "code"  # 搜索代码


class GitHubTool(Tool):
    """GitHub工具类
    
    提供GitHub仓库、用户、问题和代码的搜索功能
    支持通过GitHub API获取仓库信息、用户信息、问题列表和代码片段
    
    Attributes:
        api_key: GitHub API密钥，从环境变量GITHUB_API_KEY获取
        base_url: GitHub API基础URL
        timeout: 请求超时时间（秒）
        max_results: 最大返回结果数量
    """

    name: str = "github_tool"
    description: str = "GitHub仓库、用户、问题和代码搜索工具"
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("GITHUB_API_KEY"))
    base_url: str = "https://api.github.com"
    timeout: int = Field(30, description="请求超时时间（秒）")
    max_results: int = Field(10, description="最大返回结果数量")

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AgentUniverse-GitHub-Tool/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"token {self.api_key}"
        return headers

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """发送HTTP请求"""
        try:
            response = requests.get(
                url, 
                headers=self._get_headers(), 
                params=params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                return {"error": "API rate limit exceeded. Please check your API key or try again later."}
            elif e.response.status_code == 404:
                return {"error": "Resource not found."}
            else:
                return {"error": f"HTTP Error {e.response.status_code}: {e.response.text}"}
        except requests.Timeout:
            return {"error": "Request timeout. Please try again."}
        except Exception as e:
            return {"error": f"Request failed: {str(e)}"}

    @retry(3, 1.0)
    def search_repositories(self, query: str, sort: str = "stars", order: str = "desc") -> List[Dict[str, Any]]:
        """搜索GitHub仓库
        
        Args:
            query: 搜索查询字符串
            sort: 排序方式 (stars, forks, help-wanted-issues, updated)
            order: 排序顺序 (desc, asc)
            
        Returns:
            仓库信息列表
        """
        url = f"{self.base_url}/search/repositories"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": min(self.max_results, 100)
        }
        
        result = self._make_request(url, params)
        if "error" in result:
            return [result]
        
        repositories = []
        for item in result.get("items", []):
            repo_info = {
                "name": item["name"],
                "full_name": item["full_name"],
                "description": item.get("description", ""),
                "html_url": item["html_url"],
                "stars": item["stargazers_count"],
                "forks": item["forks_count"],
                "language": item.get("language", ""),
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
                "owner": {
                    "login": item["owner"]["login"],
                    "avatar_url": item["owner"]["avatar_url"],
                    "html_url": item["owner"]["html_url"]
                },
                "topics": item.get("topics", [])
            }
            repositories.append(repo_info)
        
        return repositories

    @retry(3, 1.0)
    def search_users(self, query: str, sort: str = "followers", order: str = "desc") -> List[Dict[str, Any]]:
        """搜索GitHub用户
        
        Args:
            query: 搜索查询字符串
            sort: 排序方式 (followers, repositories, joined)
            order: 排序顺序 (desc, asc)
            
        Returns:
            用户信息列表
        """
        url = f"{self.base_url}/search/users"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": min(self.max_results, 100)
        }
        
        result = self._make_request(url, params)
        if "error" in result:
            return [result]
        
        users = []
        for item in result.get("items", []):
            user_info = {
                "login": item["login"],
                "id": item["id"],
                "avatar_url": item["avatar_url"],
                "html_url": item["html_url"],
                "type": item["type"],
                "site_admin": item["site_admin"]
            }
            users.append(user_info)
        
        return users

    @retry(3, 1.0)
    def search_issues(self, query: str, sort: str = "created", order: str = "desc") -> List[Dict[str, Any]]:
        """搜索GitHub问题
        
        Args:
            query: 搜索查询字符串
            sort: 排序方式 (created, updated, comments)
            order: 排序顺序 (desc, asc)
            
        Returns:
            问题信息列表
        """
        url = f"{self.base_url}/search/issues"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": min(self.max_results, 100)
        }
        
        result = self._make_request(url, params)
        if "error" in result:
            return [result]
        
        issues = []
        for item in result.get("items", []):
            issue_info = {
                "title": item["title"],
                "number": item["number"],
                "html_url": item["html_url"],
                "state": item["state"],
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
                "comments": item["comments"],
                "user": {
                    "login": item["user"]["login"],
                    "avatar_url": item["user"]["avatar_url"]
                },
                "labels": [label["name"] for label in item.get("labels", [])],
                "repository": {
                    "name": item["repository_url"].split("/")[-1],
                    "full_name": item["repository_url"].split("/")[-2] + "/" + item["repository_url"].split("/")[-1]
                }
            }
            issues.append(issue_info)
        
        return issues

    @retry(3, 1.0)
    def search_code(self, query: str, sort: str = "indexed", order: str = "desc") -> List[Dict[str, Any]]:
        """搜索GitHub代码
        
        Args:
            query: 搜索查询字符串
            sort: 排序方式 (indexed)
            order: 排序顺序 (desc, asc)
            
        Returns:
            代码片段列表
        """
        url = f"{self.base_url}/search/code"
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": min(self.max_results, 100)
        }
        
        result = self._make_request(url, params)
        if "error" in result:
            return [result]
        
        code_results = []
        for item in result.get("items", []):
            code_info = {
                "name": item["name"],
                "path": item["path"],
                "html_url": item["html_url"],
                "repository": {
                    "name": item["repository"]["name"],
                    "full_name": item["repository"]["full_name"],
                    "html_url": item["repository"]["html_url"]
                },
                "score": item["score"]
            }
            code_results.append(code_info)
        
        return code_results

    def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取特定仓库的详细信息
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            
        Returns:
            仓库详细信息
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        result = self._make_request(url)
        
        if "error" in result:
            return result
        
        return {
            "name": result["name"],
            "full_name": result["full_name"],
            "description": result.get("description", ""),
            "html_url": result["html_url"],
            "stars": result["stargazers_count"],
            "forks": result["forks_count"],
            "watchers": result["watchers_count"],
            "language": result.get("language", ""),
            "created_at": result["created_at"],
            "updated_at": result["updated_at"],
            "pushed_at": result["pushed_at"],
            "size": result["size"],
            "open_issues": result["open_issues_count"],
            "license": result.get("license", {}).get("name", "") if result.get("license") else "",
            "topics": result.get("topics", []),
            "owner": {
                "login": result["owner"]["login"],
                "avatar_url": result["owner"]["avatar_url"],
                "html_url": result["owner"]["html_url"]
            }
        }

    def execute(self, 
                mode: str, 
                query: str = None, 
                owner: str = None, 
                repo: str = None,
                sort: str = None,
                order: str = "desc") -> List[Dict[str, Any]] | Dict[str, Any]:
        """执行GitHub搜索
        
        Args:
            mode: 搜索模式 (repository, user, issue, code, repo_info)
            query: 搜索查询字符串
            owner: 仓库所有者（用于repo_info模式）
            repo: 仓库名称（用于repo_info模式）
            sort: 排序方式
            order: 排序顺序
            
        Returns:
            搜索结果或错误信息
        """
        if mode == GitHubSearchMode.REPOSITORY.value:
            if not query:
                return [{"error": "Query parameter is required for repository search"}]
            return self.search_repositories(query, sort or "stars", order)
        
        elif mode == GitHubSearchMode.USER.value:
            if not query:
                return [{"error": "Query parameter is required for user search"}]
            return self.search_users(query, sort or "followers", order)
        
        elif mode == GitHubSearchMode.ISSUE.value:
            if not query:
                return [{"error": "Query parameter is required for issue search"}]
            return self.search_issues(query, sort or "created", order)
        
        elif mode == GitHubSearchMode.CODE.value:
            if not query:
                return [{"error": "Query parameter is required for code search"}]
            return self.search_code(query, sort or "indexed", order)
        
        elif mode == "repo_info":
            if not owner or not repo:
                return {"error": "Owner and repo parameters are required for repository info"}
            return self.get_repository_info(owner, repo)
        
        else:
            return [{"error": f"Invalid mode: {mode}. Must be one of {[m.value for m in GitHubSearchMode]} or 'repo_info'"}]
