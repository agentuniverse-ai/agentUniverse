#!/usr/bin/env python3

"""Bounded XML sitemap ingestion for agentUniverse knowledge bases."""

from __future__ import annotations

import gzip
import json
import re
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from typing import Any
from urllib.parse import urlparse
from xml.etree import ElementTree

import httpx
from pydantic import Field

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


@dataclass(frozen=True)
class SitemapEntry:
    """One URL discovered in a sitemap URL set."""

    url: str
    sitemap_url: str
    depth: int
    lastmod: str | None = None
    changefreq: str | None = None
    priority: str | None = None


@dataclass(frozen=True)
class SitemapReference:
    """One child sitemap discovered in a sitemap index."""

    url: str
    depth: int


class SitemapReader(Reader):
    """Discover and optionally load pages declared by XML sitemaps.

    The reader understands URL sets, sitemap indexes, XML namespaces, and gzip
    payloads. All network and traversal dimensions are bounded. By default it
    returns inventory documents; set ``load_content=True`` to delegate selected
    page URLs to ``WebPageReader`` or a caller-supplied reader.
    """

    max_urls: int = Field(default=100, ge=1, le=5000)
    max_sitemaps: int = Field(default=20, ge=1, le=100)
    max_depth: int = Field(default=3, ge=0, le=10)
    max_sitemap_bytes: int = Field(
        default=5 * 1024 * 1024,
        ge=1024,
        le=50 * 1024 * 1024,
    )
    request_timeout: float = Field(default=20.0, gt=0, le=120)
    max_redirects: int = Field(default=5, ge=0, le=20)
    max_workers: int = Field(default=4, ge=1, le=16)
    same_origin_only: bool = True
    user_agent: str = Field(
        default="agentUniverse-SitemapReader/1.0",
        min_length=1,
        max_length=256,
    )

    def _load_data(
        self,
        sitemap_url: str,
        load_content: bool = False,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        modified_since: str | datetime | None = None,
        continue_on_error: bool = True,
        page_reader: Reader | None = None,
        ext_info: dict[str, Any] | None = None,
        max_urls: int | None = None,
        max_sitemaps: int | None = None,
        max_depth: int | None = None,
        max_sitemap_bytes: int | None = None,
        request_timeout: float | None = None,
        max_redirects: int | None = None,
        max_workers: int | None = None,
        same_origin_only: bool | None = None,
    ) -> list[Document]:
        """Load sitemap inventory or delegated page content.

        Args:
            sitemap_url: Absolute HTTP(S) URL of a URL set or sitemap index.
            load_content: Fetch selected page content when true; otherwise
                return one inventory document per URL.
            include_patterns: Optional regular expressions. A URL must match at
                least one when provided.
            exclude_patterns: Optional regular expressions. Any match excludes
                the URL.
            modified_since: Include entries whose valid ``lastmod`` is on or
                after this ISO-8601 date/time. Entries without a valid lastmod
                are retained to avoid silent data loss.
            continue_on_error: Continue after nested-sitemap or page failures
                and append an error-summary document. Root sitemap failures are
                always raised.
            page_reader: Reader used in content mode. Defaults to
                ``WebPageReader``.
            ext_info: Metadata merged into every returned document.
            max_urls: Per-call URL bound without mutating component defaults.
            max_sitemaps: Per-call sitemap-file bound.
            max_depth: Per-call sitemap-index recursion bound.
            max_sitemap_bytes: Per-call compressed and decompressed size bound.
            request_timeout: Per-call HTTP timeout in seconds.
            max_redirects: Per-call HTTP redirect bound.
            max_workers: Per-call page-loading worker count.
            same_origin_only: Restrict nested sitemaps and page URLs to the root
                sitemap origin.

        Returns:
            Selected inventory or page documents, followed by an optional error
            summary document.

        Raises:
            TypeError: If arguments have invalid types.
            ValueError: If configuration, URLs, patterns, dates, or XML are
                invalid, or if a configured bound is exceeded.
            RuntimeError: If the root sitemap cannot be fetched.
        """
        root_url = self._validate_url(sitemap_url, "sitemap_url")
        self._validate_request_flags(
            load_content=load_content,
            continue_on_error=continue_on_error,
            page_reader=page_reader,
            ext_info=ext_info,
        )
        options = self._resolve_options(
            max_urls=max_urls,
            max_sitemaps=max_sitemaps,
            max_depth=max_depth,
            max_sitemap_bytes=max_sitemap_bytes,
            request_timeout=request_timeout,
            max_redirects=max_redirects,
            max_workers=max_workers,
            same_origin_only=same_origin_only,
        )
        include = self._compile_patterns(include_patterns, "include_patterns")
        exclude = self._compile_patterns(exclude_patterns, "exclude_patterns")
        cutoff = self._parse_datetime(modified_since, "modified_since")

        entries, discovery_errors = self._discover(
            root_url=root_url,
            options=options,
            include=include,
            exclude=exclude,
            cutoff=cutoff,
            continue_on_error=continue_on_error,
        )

        if load_content:
            documents, page_errors = self._load_pages(
                entries=entries,
                page_reader=page_reader,
                max_workers=options["max_workers"],
                continue_on_error=continue_on_error,
                ext_info=ext_info,
            )
        else:
            documents = [self._inventory_document(entry, ext_info) for entry in entries]
            page_errors = []

        errors = [*discovery_errors, *page_errors]
        if errors:
            documents.append(self._error_summary(root_url, errors, ext_info))
        return documents

    def _resolve_options(self, **overrides: Any) -> dict[str, Any]:
        """Validate per-call overrides without mutating the reader instance."""
        limits = {
            "max_urls": (1, 5000, int),
            "max_sitemaps": (1, 100, int),
            "max_depth": (0, 10, int),
            "max_sitemap_bytes": (1024, 50 * 1024 * 1024, int),
            "request_timeout": (0, 120, (int, float)),
            "max_redirects": (0, 20, int),
            "max_workers": (1, 16, int),
        }
        resolved: dict[str, Any] = {}
        for name, (minimum, maximum, expected_type) in limits.items():
            value = getattr(self, name) if overrides.get(name) is None else overrides[name]
            if isinstance(value, bool) or not isinstance(value, expected_type):
                raise TypeError(f"{name} has an invalid type")  # noqa: TRY003
            lower_valid = value > minimum if name == "request_timeout" else value >= minimum
            if not lower_valid or value > maximum:
                comparator = "> 0" if name == "request_timeout" else f">= {minimum}"
                raise ValueError(  # noqa: TRY003
                    f"{name} must be {comparator} and <= {maximum}"
                )
            resolved[name] = value

        origin_override = overrides.get("same_origin_only")
        if origin_override is not None and not isinstance(origin_override, bool):
            raise TypeError("same_origin_only must be a boolean")  # noqa: TRY003
        resolved["same_origin_only"] = self.same_origin_only if origin_override is None else origin_override
        return resolved

    @staticmethod
    def _validate_request_flags(
        load_content: bool,
        continue_on_error: bool,
        page_reader: Reader | None,
        ext_info: dict[str, Any] | None,
    ) -> None:
        """Reject non-network request errors before fetching a sitemap."""
        if not isinstance(load_content, bool):
            raise TypeError("load_content must be a boolean")  # noqa: TRY003
        if not isinstance(continue_on_error, bool):
            raise TypeError("continue_on_error must be a boolean")  # noqa: TRY003
        if page_reader is not None and not isinstance(page_reader, Reader):
            raise TypeError("page_reader must be a Reader instance")  # noqa: TRY003
        if ext_info is not None and not isinstance(ext_info, dict):
            raise TypeError("ext_info must be a dictionary")  # noqa: TRY003

    def _discover(  # noqa: C901
        self,
        root_url: str,
        options: dict[str, Any],
        include: list[re.Pattern[str]],
        exclude: list[re.Pattern[str]],
        cutoff: datetime | None,
        continue_on_error: bool,
    ) -> tuple[list[SitemapEntry], list[dict[str, str]]]:
        """Traverse sitemap indexes and return selected, deduplicated URLs."""
        root_origin = self._origin(root_url)
        queue: deque[SitemapReference] = deque([SitemapReference(root_url, 0)])
        visited_sitemaps: set[str] = set()
        selected_urls: set[str] = set()
        entries: list[SitemapEntry] = []
        errors: list[dict[str, str]] = []

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/xml,text/xml,application/gzip,*/*;q=0.1",
        }
        timeout = httpx.Timeout(options["request_timeout"])
        with httpx.Client(
            headers=headers,
            timeout=timeout,
            follow_redirects=True,
            max_redirects=options["max_redirects"],
        ) as client:
            while queue and len(entries) < options["max_urls"]:
                reference = queue.popleft()
                if reference.url in visited_sitemaps:
                    continue
                if len(visited_sitemaps) >= options["max_sitemaps"]:
                    raise ValueError(  # noqa: TRY003
                        "max_sitemaps exceeded while traversing sitemap indexes"
                    )
                visited_sitemaps.add(reference.url)

                try:
                    payload = self._fetch_sitemap(client, reference.url, options["max_sitemap_bytes"])
                    kind, parsed_entries, children = self._parse_sitemap(payload, reference.url, reference.depth)
                except Exception as error:
                    if reference.url == root_url or not continue_on_error:
                        raise RuntimeError(  # noqa: TRY003
                            f"failed to load sitemap {reference.url}: {error}"
                        ) from error
                    errors.append(
                        {
                            "stage": "sitemap",
                            "url": reference.url,
                            "error": str(error),
                        }
                    )
                    continue

                if kind == "index":
                    for child in children:
                        if child.depth > options["max_depth"]:
                            continue
                        if options["same_origin_only"] and self._origin(child.url) != root_origin:
                            errors.append(
                                {
                                    "stage": "origin_filter",
                                    "url": child.url,
                                    "error": "child sitemap has a different origin",
                                }
                            )
                            continue
                        if child.url not in visited_sitemaps:
                            queue.append(child)
                    continue

                for entry in parsed_entries:
                    if len(entries) >= options["max_urls"]:
                        break
                    if entry.url in selected_urls:
                        continue
                    if options["same_origin_only"] and self._origin(entry.url) != root_origin:
                        continue
                    if not self._matches(entry.url, include, exclude):
                        continue
                    if cutoff and not self._passes_modified_filter(entry.lastmod, cutoff):
                        continue
                    selected_urls.add(entry.url)
                    entries.append(entry)
        return entries, errors

    def _fetch_sitemap(
        self,
        client: httpx.Client,
        url: str,
        max_bytes: int,
    ) -> bytes:
        """Fetch one sitemap with compressed and decompressed size limits."""
        with client.stream("GET", url) as response:
            response.raise_for_status()
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > max_bytes:
                raise ValueError("sitemap response exceeds max_sitemap_bytes")  # noqa: TRY003
            chunks: list[bytes] = []
            total = 0
            for chunk in response.iter_bytes():
                total += len(chunk)
                if total > max_bytes:
                    raise ValueError(  # noqa: TRY003
                        "sitemap response exceeds max_sitemap_bytes"
                    )
                chunks.append(chunk)
            payload = b"".join(chunks)
            content_type = response.headers.get("content-type", "").lower()

        has_gzip_magic = payload.startswith(bytes((0x1F, 0x8B)))
        has_gzip_hint = urlparse(url).path.lower().endswith(".gz") or "gzip" in content_type
        if has_gzip_magic:
            try:
                with gzip.GzipFile(fileobj=BytesIO(payload)) as archive:
                    payload = archive.read(max_bytes + 1)
            except (OSError, EOFError) as error:
                raise ValueError("invalid gzip sitemap payload") from error  # noqa: TRY003
            if len(payload) > max_bytes:
                raise ValueError(  # noqa: TRY003
                    "decompressed sitemap exceeds max_sitemap_bytes"
                )
        elif has_gzip_hint and not payload.lstrip().startswith(b"<"):
            # HTTP clients can transparently decode Content-Encoding: gzip. A
            # gzip hint with XML bytes is therefore valid; any other non-gzip
            # payload is malformed.
            raise ValueError("invalid gzip sitemap payload")  # noqa: TRY003
        return payload

    def _parse_sitemap(
        self,
        payload: bytes,
        sitemap_url: str,
        depth: int,
    ) -> tuple[str, list[SitemapEntry], list[SitemapReference]]:
        """Parse one URL set or sitemap index."""
        if not payload.strip():
            raise ValueError("sitemap payload is empty")  # noqa: TRY003
        upper_prefix = payload[:4096].upper()
        if b"<!DOCTYPE" in upper_prefix or b"<!ENTITY" in upper_prefix:
            raise ValueError("DTD and entity declarations are not allowed")  # noqa: TRY003
        try:
            # DTD/entity declarations are rejected above and payload size is bounded.
            root = ElementTree.fromstring(payload)  # noqa: S314
        except ElementTree.ParseError as error:
            raise ValueError(f"invalid sitemap XML: {error}") from error  # noqa: TRY003

        root_name = self._local_name(root.tag)
        if root_name == "urlset":
            entries = [
                self._parse_url_entry(element, sitemap_url, depth)
                for element in root
                if self._local_name(element.tag) == "url"
            ]
            return "urlset", entries, []
        if root_name == "sitemapindex":
            children = [
                SitemapReference(
                    self._validate_url(self._child_text(element, "loc"), "child sitemap URL"),
                    depth + 1,
                )
                for element in root
                if self._local_name(element.tag) == "sitemap"
            ]
            return "index", [], children
        raise ValueError(  # noqa: TRY003
            "sitemap root must be urlset or sitemapindex"
        )

    def _parse_url_entry(
        self,
        element: ElementTree.Element,
        sitemap_url: str,
        depth: int,
    ) -> SitemapEntry:
        """Parse and validate one ``url`` element."""
        return SitemapEntry(
            url=self._validate_url(self._child_text(element, "loc"), "sitemap URL"),
            sitemap_url=sitemap_url,
            depth=depth,
            lastmod=self._child_text(element, "lastmod", required=False),
            changefreq=self._child_text(element, "changefreq", required=False),
            priority=self._child_text(element, "priority", required=False),
        )

    def _load_pages(
        self,
        entries: list[SitemapEntry],
        page_reader: Reader | None,
        max_workers: int,
        continue_on_error: bool,
        ext_info: dict[str, Any] | None,
    ) -> tuple[list[Document], list[dict[str, str]]]:
        """Load selected pages concurrently while preserving sitemap order."""
        if page_reader is None:
            from agentuniverse.agent.action.knowledge.reader.web.web_page_reader import (
                WebPageReader,
            )

            page_reader = WebPageReader()
        if not isinstance(page_reader, Reader):
            raise TypeError("page_reader must be a Reader instance")  # noqa: TRY003

        def load(entry: SitemapEntry) -> tuple[list[Document], dict[str, str] | None]:
            try:
                page_documents = page_reader.load_data(url=entry.url)
            except Exception as error:
                if not continue_on_error:
                    raise
                return [], {"stage": "page", "url": entry.url, "error": str(error)}
            else:
                enriched = [self._enrich_page_document(document, entry, ext_info) for document in page_documents]
                return enriched, None

        documents: list[Document] = []
        errors: list[dict[str, str]] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for page_documents, error in executor.map(load, entries):
                documents.extend(page_documents)
                if error:
                    errors.append(error)
        return documents, errors

    @staticmethod
    def _enrich_page_document(
        document: Document,
        entry: SitemapEntry,
        ext_info: dict[str, Any] | None,
    ) -> Document:
        """Copy a page document and add non-destructive sitemap provenance."""
        metadata = dict(document.metadata or {})
        metadata.setdefault("url", entry.url)
        metadata.update(
            {
                "sitemap_source": entry.sitemap_url,
                "sitemap_depth": entry.depth,
                "sitemap_lastmod": entry.lastmod,
                "sitemap_changefreq": entry.changefreq,
                "sitemap_priority": entry.priority,
                "content_loaded": True,
            }
        )
        if ext_info:
            metadata.update(ext_info)
        return document.model_copy(update={"metadata": metadata})

    @staticmethod
    def _inventory_document(
        entry: SitemapEntry,
        ext_info: dict[str, Any] | None,
    ) -> Document:
        """Represent one selected sitemap URL without fetching its page."""
        metadata: dict[str, Any] = {
            "source": entry.url,
            "url": entry.url,
            "sitemap_source": entry.sitemap_url,
            "sitemap_depth": entry.depth,
            "sitemap_lastmod": entry.lastmod,
            "sitemap_changefreq": entry.changefreq,
            "sitemap_priority": entry.priority,
            "content_loaded": False,
        }
        if ext_info:
            metadata.update(ext_info)
        return Document(text=entry.url, metadata=metadata)

    @staticmethod
    def _error_summary(
        root_url: str,
        errors: list[dict[str, str]],
        ext_info: dict[str, Any] | None,
    ) -> Document:
        """Return transparent partial-failure details through the Reader API."""
        metadata: dict[str, Any] = {
            "source": root_url,
            "sitemap_error_summary": True,
            "error_count": len(errors),
            "content_loaded": False,
        }
        if ext_info:
            metadata.update(ext_info)
        return Document(
            text=json.dumps({"errors": errors}, ensure_ascii=False, sort_keys=True),
            metadata=metadata,
        )

    @staticmethod
    def _compile_patterns(
        patterns: list[str] | None,
        name: str,
    ) -> list[re.Pattern[str]]:
        """Compile URL filters and fail before any network request."""
        if patterns is None:
            return []
        if not isinstance(patterns, list) or any(not isinstance(pattern, str) for pattern in patterns):
            raise TypeError(f"{name} must be a list of strings")  # noqa: TRY003
        try:
            return [re.compile(pattern) for pattern in patterns]
        except re.error as error:
            raise ValueError(f"invalid {name} regex: {error}") from error  # noqa: TRY003

    @staticmethod
    def _matches(
        url: str,
        include: list[re.Pattern[str]],
        exclude: list[re.Pattern[str]],
    ) -> bool:
        """Apply inclusive and exclusive URL filters."""
        if include and not any(pattern.search(url) for pattern in include):
            return False
        return not any(pattern.search(url) for pattern in exclude)

    @classmethod
    def _parse_datetime(
        cls,
        value: str | datetime | None,
        name: str,
    ) -> datetime | None:
        """Parse an ISO-8601 date/time and normalize it to UTC."""
        if value is None:
            return None
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, str):
            candidate = value.strip()
            if not candidate:
                raise ValueError(f"{name} must not be empty")  # noqa: TRY003
            try:
                parsed = datetime.fromisoformat(candidate.replace("Z", "+00:00"))
            except ValueError as error:
                raise ValueError(f"{name} must be ISO-8601") from error  # noqa: TRY003
        else:
            raise TypeError(f"{name} must be a string or datetime")  # noqa: TRY003
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @classmethod
    def _passes_modified_filter(cls, lastmod: str | None, cutoff: datetime) -> bool:
        """Retain unknown dates; filter only valid dates older than cutoff."""
        if not lastmod:
            return True
        try:
            parsed = cls._parse_datetime(lastmod, "lastmod")
        except (TypeError, ValueError):
            return True
        return parsed is not None and parsed >= cutoff

    @staticmethod
    def _validate_url(value: Any, name: str) -> str:
        """Validate an absolute HTTP(S) URL without embedded credentials."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be a non-empty string")  # noqa: TRY003
        normalized = value.strip()
        parsed = urlparse(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError(f"{name} must be an absolute HTTP(S) URL")  # noqa: TRY003
        if parsed.username or parsed.password:
            raise ValueError(f"{name} must not contain credentials")  # noqa: TRY003
        return normalized

    @staticmethod
    def _origin(url: str) -> tuple[str, str, int | None]:
        """Return a normalized origin tuple."""
        parsed = urlparse(url)
        port = parsed.port
        if port is None:
            port = 443 if parsed.scheme == "https" else 80
        return parsed.scheme.lower(), (parsed.hostname or "").lower(), port

    @staticmethod
    def _local_name(tag: str) -> str:
        """Remove an XML namespace from a tag name."""
        return tag.rsplit("}", 1)[-1]

    @classmethod
    def _child_text(
        cls,
        element: ElementTree.Element,
        name: str,
        required: bool = True,
    ) -> str | None:
        """Read a direct child by namespace-independent local name."""
        for child in element:
            if cls._local_name(child.tag) == name:
                text = (child.text or "").strip()
                if text:
                    return text
                break
        if required:
            raise ValueError(f"sitemap entry is missing {name}")  # noqa: TRY003
        return None
