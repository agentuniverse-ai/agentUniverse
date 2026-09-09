#!/usr/bin/env python3
# ruff: noqa: TRY003, TRY004

"""GitLab project and issue discovery through the GitLab REST API."""

from typing import Any, ClassVar

import requests
from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.env_util import get_from_env


class GitLabTool(Tool):
    """Search GitLab projects, inspect a project, or search project issues."""

    MODES: ClassVar[set[str]] = {"projects", "project", "issues"}
    PROJECT_SORTS: ClassVar[set[str]] = {
        "created_at",
        "id",
        "last_activity_at",
        "name",
        "path",
        "star_count",
        "updated_at",
    }
    ISSUE_SORTS: ClassVar[set[str]] = {"created_at", "updated_at"}
    ORDERS: ClassVar[set[str]] = {"asc", "desc"}
    STATES: ClassVar[set[str]] = {"opened", "closed", "all"}
    MAX_OFFSET: ClassVar[int] = 9999

    base_url: str = "https://gitlab.com/api/v4"
    timeout: float = Field(default=15.0, description="HTTP request timeout in seconds")
    access_token: str | None = Field(default_factory=lambda: get_from_env("GITLAB_TOKEN"))
    user_agent: str = "agentUniverse-GitLab-Tool/1.0"

    def execute(
        self,
        query: str,
        mode: str = "projects",
        max_results: int = 5,
        page: int = 1,
        sort: str = "created_at",
        order: str = "desc",
        state: str = "opened",
        labels: str | None = None,
        issue_search: str | None = None,
    ) -> dict[str, Any]:
        """Search GitLab projects/issues or retrieve one project.

        Args:
            query: Search text, or a project path/ID for project and issues modes.
            mode: projects, project, or issues.
            max_results: Results per page, from 1 to 20.
            page: One-based result page.
            sort: Server-side sort field.
            order: asc or desc.
            state: Issue state opened, closed, or all.
            labels: Optional comma-separated issue labels.
            issue_search: Optional text to search within issue title and description.
        """
        normalized_mode = self._normalize_mode(mode)
        normalized_query = query.strip() if isinstance(query, str) else ""
        if not normalized_query:
            raise ValueError("query must not be empty")
        if normalized_mode == "project":
            max_results, page = 1, 1
        else:
            self._validate_pagination(max_results, page)
        normalized_order = self._normalize_order(order)
        normalized_state = (
            self._normalize_state(state)
            if normalized_mode == "issues"
            else (state.strip().lower() if isinstance(state, str) else "")
        )
        normalized_sort = self._normalize_sort(normalized_mode, sort)
        offset = (page - 1) * max_results
        context = {
            "mode": normalized_mode,
            "query": normalized_query,
            "max_results": max_results,
            "page": page,
            "offset": offset,
            "sort": normalized_sort,
            "order": normalized_order,
            "state": normalized_state,
            "labels": labels.strip() if isinstance(labels, str) else "",
            "issue_search": issue_search.strip() if isinstance(issue_search, str) else "",
        }
        try:
            if normalized_mode == "projects":
                data, total_results = self._get_json(
                    "/projects",
                    {
                        "search": normalized_query,
                        "page": page,
                        "per_page": max_results,
                        "order_by": normalized_sort,
                        "sort": normalized_order,
                    },
                )
                projects = [self._parse_project(item) for item in self._list_data(data)]
                return {
                    **context,
                    "total_results": total_results,
                    "returned_results": len(projects),
                    "projects": projects,
                    "issues": [],
                }
            if normalized_mode == "project":
                data, _ = self._get_json(f"/projects/{self._encode_project(normalized_query)}")
                project = self._parse_project(data)
                return {**context, "total_results": 1, "returned_results": 1, "projects": [project], "issues": []}
            data, total_results = self._get_json(
                f"/projects/{self._encode_project(normalized_query)}/issues",
                {
                    "page": page,
                    "per_page": max_results,
                    "order_by": normalized_sort,
                    "sort": normalized_order,
                    "state": normalized_state,
                    **({"labels": context["labels"]} if context["labels"] else {}),
                    **({"search": context["issue_search"]} if context["issue_search"] else {}),
                },
            )
            issues = [self._parse_issue(item) for item in self._list_data(data)]
            return {
                **context,
                "total_results": total_results,
                "returned_results": len(issues),
                "projects": [],
                "issues": issues,
            }
        except requests.Timeout:
            return self._error_result(**context, error_type="request_timeout", message="GitLab request timed out.")
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else None
            return self._error_result(
                **context,
                error_type="http_error",
                message=f"GitLab returned HTTP status {status}." if status else "GitLab HTTP request failed.",
            )
        except requests.RequestException:
            return self._error_result(**context, error_type="request_error", message="GitLab request failed.")
        except (KeyError, TypeError, ValueError) as exc:
            return self._error_result(
                **context, error_type="invalid_response", message=f"Unable to parse GitLab response: {exc}"
            )

    def _get_json(self, path: str, params: dict[str, Any] | None = None) -> tuple[Any, int | None]:
        response = requests.get(f"{self.base_url}{path}", params=params, headers=self._headers(), timeout=self.timeout)
        response.raise_for_status()
        try:
            data = response.json()
        except requests.JSONDecodeError as exc:
            raise ValueError("invalid GitLab JSON response") from exc
        total_header = response.headers.get("X-Total") if hasattr(response, "headers") else None
        try:
            total = int(total_header) if total_header is not None else None
        except (TypeError, ValueError):
            total = None
        return data, total

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json", "User-Agent": self.user_agent}
        if self.access_token:
            headers["PRIVATE-TOKEN"] = self.access_token
        return headers

    @staticmethod
    def _encode_project(value: str) -> str:
        from urllib.parse import quote

        return quote(value, safe="%")

    @classmethod
    def _normalize_mode(cls, value: str) -> str:
        normalized = value.strip().lower() if isinstance(value, str) else ""
        if normalized not in cls.MODES:
            raise ValueError(f"mode must be one of: {', '.join(sorted(cls.MODES))}")
        return normalized

    @classmethod
    def _normalize_sort(cls, mode: str, value: str) -> str:
        normalized = value.strip().lower() if isinstance(value, str) else ""
        valid = cls.PROJECT_SORTS if mode == "projects" else cls.ISSUE_SORTS
        if mode == "project":
            return "created_at"
        if normalized not in valid:
            raise ValueError(f"sort must be one of: {', '.join(sorted(valid))}")
        return normalized

    @classmethod
    def _normalize_order(cls, value: str) -> str:
        normalized = value.strip().lower() if isinstance(value, str) else ""
        if normalized not in cls.ORDERS:
            raise ValueError("order must be one of: asc, desc")
        return normalized

    @classmethod
    def _normalize_state(cls, value: str) -> str:
        normalized = value.strip().lower() if isinstance(value, str) else ""
        if normalized not in cls.STATES:
            raise ValueError("state must be one of: opened, closed, all")
        return normalized

    @classmethod
    def _validate_pagination(cls, max_results: int, page: int) -> None:
        if isinstance(max_results, bool) or not isinstance(max_results, int) or not 1 <= max_results <= 20:
            raise ValueError("max_results must be an integer between 1 and 20")
        if isinstance(page, bool) or not isinstance(page, int) or page < 1:
            raise ValueError("page must be a positive integer")
        if (page - 1) * max_results > cls.MAX_OFFSET:
            raise ValueError("page and max_results must produce an offset below 10000")

    @staticmethod
    def _list_data(data: Any) -> list[dict[str, Any]]:
        if not isinstance(data, list):
            raise ValueError("invalid GitLab list response")
        if any(not isinstance(item, dict) for item in data):
            raise ValueError("invalid GitLab list item")
        return data

    @staticmethod
    def _parse_project(item: dict[str, Any]) -> dict[str, Any]:
        namespace = item.get("namespace")
        if namespace is not None and not isinstance(namespace, dict):
            raise ValueError("invalid project namespace")
        return {
            "id": item.get("id", 0),
            "name": item.get("name", ""),
            "path": item.get("path", ""),
            "path_with_namespace": item.get("path_with_namespace", ""),
            "description": item.get("description", ""),
            "web_url": item.get("web_url", ""),
            "namespace": (item.get("namespace") or {}).get("full_path", ""),
            "visibility": item.get("visibility", ""),
            "star_count": item.get("star_count", 0),
            "forks_count": item.get("forks_count", 0),
            "open_issues_count": item.get("open_issues_count", 0),
            "default_branch": item.get("default_branch", ""),
            "created_at": item.get("created_at", ""),
            "last_activity_at": item.get("last_activity_at", ""),
            "topics": item.get("topics", []),
        }

    @staticmethod
    def _parse_issue(item: dict[str, Any]) -> dict[str, Any]:
        author = item.get("author") or {}
        milestone = item.get("milestone")
        if not isinstance(author, dict) or not isinstance(milestone, (dict, type(None))):
            raise ValueError("invalid issue nested metadata")
        return {
            "id": item.get("id", 0),
            "iid": item.get("iid", 0),
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "state": item.get("state", ""),
            "web_url": item.get("web_url", ""),
            "project_id": item.get("project_id", 0),
            "author": {"username": author.get("username", ""), "name": author.get("name", "")},
            "labels": item.get("labels", []),
            "milestone": (milestone or {}).get("title", ""),
            "created_at": item.get("created_at", ""),
            "updated_at": item.get("updated_at", ""),
            "closed_at": item.get("closed_at", ""),
            "upvotes": item.get("upvotes", 0),
            "downvotes": item.get("downvotes", 0),
        }

    @staticmethod
    def _error_result(**context: Any) -> dict[str, Any]:
        error_type, message = context.pop("error_type"), context.pop("message")
        return {
            **context,
            "total_results": None,
            "returned_results": 0,
            "projects": [],
            "issues": [],
            "error": {"type": error_type, "message": message},
        }
