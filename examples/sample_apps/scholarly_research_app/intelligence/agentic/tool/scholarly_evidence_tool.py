#!/usr/bin/env python3

"""Compose built-in scholarly tools into a bounded evidence set."""

import re
import unicodedata
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from typing import Any, ClassVar
from urllib.parse import quote, urlsplit

from agentuniverse.agent.action.tool.common_tool.crossref_tool import CrossrefTool
from agentuniverse.agent.action.tool.common_tool.pubmed_tool import PubMedTool
from agentuniverse.agent.action.tool.common_tool.semantic_scholar_tool import SemanticScholarTool
from agentuniverse.agent.action.tool.tool import Tool


class ScholarlyEvidenceInputError(ValueError):
    """Raised when scholarly evidence tool input is invalid."""

    @classmethod
    def empty_query(cls) -> "ScholarlyEvidenceInputError":
        """Build an empty-query error."""
        return cls("query must not be empty")

    @classmethod
    def query_too_long(cls, maximum: int) -> "ScholarlyEvidenceInputError":
        """Build a query-length error."""
        return cls(f"query must not exceed {maximum} characters")

    @classmethod
    def integer_out_of_bounds(cls, field_name: str, maximum: int) -> "ScholarlyEvidenceInputError":
        """Build a bounded-integer error."""
        return cls(f"{field_name} must be an integer between 1 and {maximum}")


class ScholarlyEvidenceTool(Tool):
    """Search three scholarly sources and normalize their metadata."""

    SOURCE_SPECS: ClassVar[tuple[tuple[str, type[Tool], str], ...]] = (
        ("pubmed", PubMedTool, "papers"),
        ("crossref", CrossrefTool, "works"),
        ("semantic_scholar", SemanticScholarTool, "papers"),
    )
    SOURCE_LABELS: ClassVar[dict[str, str]] = {
        "pubmed": "PubMed",
        "crossref": "Crossref",
        "semantic_scholar": "Semantic Scholar",
    }
    MAX_QUERY_LENGTH: ClassVar[int] = 500
    MAX_RESULTS_PER_SOURCE: ClassVar[int] = 10
    MAX_EVIDENCE: ClassVar[int] = 15
    MAX_TITLE_LENGTH: ClassVar[int] = 500
    MAX_ABSTRACT_LENGTH: ClassVar[int] = 1600
    MAX_AUTHORS: ClassVar[int] = 10

    def execute(
        self,
        query: str,
        max_results_per_source: int = 5,
        max_evidence: int = 10,
    ) -> dict[str, Any]:
        """Search, normalize, deduplicate, and bound scholarly metadata.

        Args:
            query: Research question or search expression.
            max_results_per_source: Results requested from each source, from 1 to 10.
            max_evidence: Maximum deduplicated records returned, from 1 to 15.

        Returns:
            A source-status summary and a citation-ready evidence list. Failure of
            one source is reported without discarding successful source results.

        Raises:
            ValueError: If an input is empty, too long, or outside its bounds.
        """
        normalized_query = self._validate_inputs(query, max_results_per_source, max_evidence)
        source_results = self._collect_sources(normalized_query, max_results_per_source)

        source_status = []
        normalized_records = []
        raw_result_count = 0
        for source, _tool_class, result_key in self.SOURCE_SPECS:
            result = source_results[source]
            records = result.get(result_key, [])
            if not isinstance(records, list):
                records = []
            raw_result_count += len(records)
            status = {
                "source": source,
                "status": "error" if result.get("error") else ("ok" if records else "empty"),
                "returned_results": len(records),
            }
            if result.get("error"):
                status["error"] = self._safe_error(source, result["error"])
            source_status.append(status)
            normalized_records.extend(
                record
                for raw_record in records
                if isinstance(raw_record, dict)
                if (record := self._normalize_record(source, raw_record)) is not None
            )

        deduplicated = self._deduplicate(normalized_records)
        evidence = [self._public_record(record, index + 1) for index, record in enumerate(deduplicated[:max_evidence])]
        return {
            "query": normalized_query,
            "sources": [source for source, _tool_class, _result_key in self.SOURCE_SPECS],
            "source_status": source_status,
            "raw_result_count": raw_result_count,
            "deduplicated_result_count": len(deduplicated),
            "returned_results": len(evidence),
            "truncated": len(deduplicated) > max_evidence,
            "evidence": evidence,
            "notice": (
                "Results contain scholarly metadata and available abstracts only; "
                "they do not constitute full-text appraisal."
            ),
        }

    @classmethod
    def _validate_inputs(cls, query: str, max_results_per_source: int, max_evidence: int) -> str:
        normalized_query = query.strip() if isinstance(query, str) else ""
        if not normalized_query:
            raise ScholarlyEvidenceInputError.empty_query()
        if len(normalized_query) > cls.MAX_QUERY_LENGTH:
            raise ScholarlyEvidenceInputError.query_too_long(cls.MAX_QUERY_LENGTH)
        cls._validate_integer(
            max_results_per_source,
            "max_results_per_source",
            cls.MAX_RESULTS_PER_SOURCE,
        )
        cls._validate_integer(max_evidence, "max_evidence", cls.MAX_EVIDENCE)
        return normalized_query

    @staticmethod
    def _validate_integer(value: int, field_name: str, maximum: int) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= maximum:
            raise ScholarlyEvidenceInputError.integer_out_of_bounds(field_name, maximum)

    def _collect_sources(self, query: str, max_results: int) -> dict[str, dict[str, Any]]:
        results: dict[str, dict[str, Any]] = {}
        with ThreadPoolExecutor(max_workers=len(self.SOURCE_SPECS)) as executor:
            futures = {
                source: executor.submit(self._run_source, source, tool_class, result_key, query, max_results)
                for source, tool_class, result_key in self.SOURCE_SPECS
            }
            for source, _tool_class, _result_key in self.SOURCE_SPECS:
                results[source] = futures[source].result()
        return results

    @staticmethod
    def _run_source(
        source: str,
        tool_class: type[Tool],
        result_key: str,
        query: str,
        max_results: int,
    ) -> dict[str, Any]:
        try:
            result = tool_class().execute(query=query, max_results=max_results)
        except Exception:  # A sample orchestrator must isolate third-party failures.
            return {
                result_key: [],
                "error": {
                    "type": "source_execution_error",
                    "message": f"{source} search could not be completed.",
                },
            }
        if not isinstance(result, dict):
            return {
                result_key: [],
                "error": {
                    "type": "invalid_source_response",
                    "message": f"{source} returned an invalid response.",
                },
            }
        return result

    @classmethod
    def _normalize_record(cls, source: str, record: dict[str, Any]) -> dict[str, Any] | None:
        title = cls._bounded_text(record.get("title"), cls.MAX_TITLE_LENGTH)
        identifiers = cls._identifiers(source, record)
        if not title and not any(identifiers.values()):
            return None

        source_url = cls._source_url(source, record, identifiers)
        authors = cls._string_list(record.get("authors"), cls.MAX_AUTHORS, 120)
        abstract = cls._bounded_text(record.get("abstract"), cls.MAX_ABSTRACT_LENGTH)
        venue = cls._bounded_text(record.get("journal") or record.get("container_title") or record.get("venue"), 300)
        published = cls._bounded_text(
            record.get("published") or record.get("publication_date") or record.get("year"), 40
        )
        citation_count = record.get("citation_count")
        if isinstance(citation_count, bool) or not isinstance(citation_count, int) or citation_count < 0:
            citation_count = 0

        source_urls = {source: source_url} if source_url else {}
        return {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "venue": venue,
            "published": published,
            "citation_count": citation_count,
            "is_open_access": record.get("is_open_access") is True,
            "open_access_pdf": cls._open_access_pdf(record.get("open_access_pdf")),
            "identifiers": identifiers,
            "sources": [source],
            "source_urls": source_urls,
            "_keys": cls._identity_keys(title, identifiers),
        }

    @classmethod
    def _identifiers(cls, source: str, record: dict[str, Any]) -> dict[str, str]:
        external_ids = record.get("external_ids") if isinstance(record.get("external_ids"), dict) else {}
        external_ids_ci = {str(key).lower(): value for key, value in external_ids.items()}
        doi = cls._normalize_doi(record.get("doi") or external_ids_ci.get("doi"))
        pmid = cls._normalize_pmid(record.get("pmid") or external_ids_ci.get("pubmed") or external_ids_ci.get("pmid"))
        paper_id = cls._bounded_text(record.get("paper_id"), 80) if source == "semantic_scholar" else ""
        return {"doi": doi, "pmid": pmid, "semantic_scholar_paper_id": paper_id}

    @classmethod
    def _source_url(cls, source: str, record: dict[str, Any], identifiers: dict[str, str]) -> str:
        url = record.get("entry_url") if source == "pubmed" else record.get("url")
        normalized_url = cls._bounded_url(url)
        if normalized_url:
            return normalized_url
        if source == "pubmed" and identifiers["pmid"]:
            return f"https://pubmed.ncbi.nlm.nih.gov/{identifiers['pmid']}/"
        if identifiers["doi"]:
            return f"https://doi.org/{quote(identifiers['doi'], safe='/')}"
        return ""

    @classmethod
    def _open_access_pdf(cls, value: Any) -> dict[str, str]:
        if not isinstance(value, dict):
            return {}
        result = {}
        url = cls._bounded_url(value.get("url"))
        if url:
            result["url"] = url
        for key in ("status", "license"):
            text = cls._bounded_text(value.get(key), 100)
            if text:
                result[key] = text
        return result

    @classmethod
    def _identity_keys(cls, title: str, identifiers: dict[str, str]) -> set[str]:
        keys = set()
        if identifiers["doi"]:
            keys.add(f"doi:{identifiers['doi']}")
        if identifiers["pmid"]:
            keys.add(f"pmid:{identifiers['pmid']}")
        normalized_title = cls._normalize_title(title)
        if len(normalized_title) >= 12:
            keys.add(f"title:{normalized_title}")
        return keys

    @classmethod
    def _deduplicate(cls, records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        deduplicated: list[dict[str, Any]] = []
        for record in records:
            matches = [existing for existing in deduplicated if cls._records_match(existing, record)]
            if not matches:
                deduplicated.append(record)
                continue
            primary = matches[0]
            cls._merge_record(primary, record)
            for duplicate in matches[1:]:
                # A title-only bridge may match two mutually conflicting works.
                # Recheck after every merge as the primary gains identifiers.
                if cls._records_match(primary, duplicate):
                    cls._merge_record(primary, duplicate)
                    deduplicated.remove(duplicate)
        return deduplicated

    @staticmethod
    def _records_match(first: dict[str, Any], second: dict[str, Any]) -> bool:
        """Match shared identities unless authoritative identifiers conflict."""
        for identifier in ("doi", "pmid"):
            first_value = first["identifiers"][identifier]
            second_value = second["identifiers"][identifier]
            if first_value and second_value and first_value != second_value:
                return False
        return bool(first["_keys"] & second["_keys"])

    @classmethod
    def _merge_record(cls, target: dict[str, Any], incoming: dict[str, Any]) -> None:
        target["_keys"].update(incoming["_keys"])
        for field in ("title", "venue", "published", "open_access_pdf"):
            if not target[field] and incoming[field]:
                target[field] = incoming[field]
        if len(incoming["abstract"]) > len(target["abstract"]):
            target["abstract"] = incoming["abstract"]
        if len(incoming["authors"]) > len(target["authors"]):
            target["authors"] = incoming["authors"]
        target["citation_count"] = max(target["citation_count"], incoming["citation_count"])
        target["is_open_access"] = target["is_open_access"] or incoming["is_open_access"]
        for key, value in incoming["identifiers"].items():
            if not target["identifiers"][key] and value:
                target["identifiers"][key] = value
        for source in incoming["sources"]:
            if source not in target["sources"]:
                target["sources"].append(source)
        target["source_urls"].update(incoming["source_urls"])

    @staticmethod
    def _public_record(record: dict[str, Any], index: int) -> dict[str, Any]:
        return {"evidence_id": f"E{index}", **{key: value for key, value in record.items() if key != "_keys"}}

    @staticmethod
    def _normalize_doi(value: Any) -> str:
        if not isinstance(value, str):
            return ""
        doi = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I)
        return doi.lower() if doi.startswith("10.") and "/" in doi and not any(char.isspace() for char in doi) else ""

    @staticmethod
    def _normalize_pmid(value: Any) -> str:
        if isinstance(value, int) and not isinstance(value, bool):
            value = str(value)
        if not isinstance(value, str):
            return ""
        pmid = re.sub(r"^(?:pmid:\s*|https?://pubmed\.ncbi\.nlm\.nih\.gov/)", "", value.strip(), flags=re.I)
        pmid = pmid.rstrip("/")
        return pmid if pmid.isdigit() else ""

    @staticmethod
    def _normalize_title(value: str) -> str:
        normalized = unicodedata.normalize("NFKC", value).casefold()
        return "".join(character for character in normalized if character.isalnum())

    @staticmethod
    def _bounded_text(value: Any, maximum: int) -> str:
        if isinstance(value, int) and not isinstance(value, bool):
            value = str(value)
        return value.strip()[:maximum] if isinstance(value, str) else ""

    @classmethod
    def _bounded_url(cls, value: Any) -> str:
        url = cls._bounded_text(value, 1000)
        if not url:
            return ""
        try:
            parsed = urlsplit(url)
        except ValueError:
            return ""
        return url if parsed.scheme.lower() in {"http", "https"} and parsed.netloc else ""

    @classmethod
    def _string_list(cls, value: Any, maximum_items: int, maximum_length: int) -> list[str]:
        if not isinstance(value, list):
            return []
        result = []
        for item in value:
            text = cls._bounded_text(item, maximum_length)
            if text and text not in result:
                result.append(text)
            if len(result) >= maximum_items:
                break
        return result

    @classmethod
    def _safe_error(cls, source: str, value: Any) -> dict[str, str]:
        source_label = cls.SOURCE_LABELS.get(source, source.replace("_", " ").title())
        if not isinstance(value, dict):
            return {"type": "source_error", "message": f"{source_label} search failed."}
        error_type = cls._bounded_text(value.get("type"), 80) or "source_error"
        safe_messages = {
            "api_error": f"{source_label} returned an API error.",
            "http_error": f"{source_label} returned an HTTP error.",
            "invalid_response": f"{source_label} returned an invalid response.",
            "invalid_source_response": f"{source_label} returned an invalid response.",
            "request_error": f"{source_label} request failed.",
            "request_timeout": f"{source_label} request timed out.",
            "source_execution_error": f"{source_label} search could not be completed.",
        }
        return {
            "type": error_type,
            "message": safe_messages.get(error_type, f"{source_label} search failed."),
        }
