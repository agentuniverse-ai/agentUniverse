#!/usr/bin/env python3

"""Offline tests for the scholarly evidence composition tool."""

import unittest
from unittest.mock import patch

from scholarly_research_app.intelligence.agentic.tool.scholarly_evidence_tool import ScholarlyEvidenceTool


class _SensitiveUpstreamError(RuntimeError):
    """Represent an exception whose text must not be exposed."""

    def __init__(self) -> None:
        super().__init__("secret upstream details")


class ScholarlyEvidenceToolTest(unittest.TestCase):
    """Verify normalization, provenance, bounds, and graceful degradation."""

    def setUp(self) -> None:
        self.tool = ScholarlyEvidenceTool()

    def test_merges_duplicate_records_and_preserves_provenance(self) -> None:
        source_results = {
            "pubmed": {
                "papers": [
                    {
                        "pmid": "12345",
                        "doi": "10.1000/Example",
                        "title": "A Trial of Evidence Synthesis",
                        "authors": ["A. Author"],
                        "abstract": "Short abstract.",
                        "journal": "Example Medicine",
                        "published": "2025",
                        "entry_url": "https://pubmed.ncbi.nlm.nih.gov/12345/",
                    }
                ]
            },
            "crossref": {
                "works": [
                    {
                        "doi": "https://doi.org/10.1000/example",
                        "title": "A Trial of Evidence Synthesis",
                        "authors": ["A. Author", "B. Author"],
                        "abstract": "A longer abstract from Crossref metadata.",
                        "container_title": "Example Medicine",
                        "published": "2025-01-02",
                        "url": "https://doi.org/10.1000/example",
                        "citation_count": 7,
                    }
                ]
            },
            "semantic_scholar": {
                "papers": [
                    {
                        "paper_id": "abc123",
                        "external_ids": {"DOI": "10.1000/EXAMPLE", "PubMed": "12345"},
                        "title": "A Trial of Evidence Synthesis",
                        "authors": ["A. Author", "B. Author"],
                        "venue": "Example Medicine",
                        "year": 2025,
                        "citation_count": 9,
                        "is_open_access": True,
                        "open_access_pdf": {"url": "https://example.org/paper.pdf", "status": "GREEN"},
                        "url": "https://www.semanticscholar.org/paper/abc123",
                    }
                ]
            },
        }

        with patch.object(self.tool, "_collect_sources", return_value=source_results):
            result = self.tool.execute("evidence synthesis")

        self.assertEqual(result["raw_result_count"], 3)
        self.assertEqual(result["deduplicated_result_count"], 1)
        evidence = result["evidence"][0]
        self.assertEqual(evidence["evidence_id"], "E1")
        self.assertEqual(evidence["identifiers"]["doi"], "10.1000/example")
        self.assertEqual(evidence["identifiers"]["pmid"], "12345")
        self.assertEqual(evidence["identifiers"]["semantic_scholar_paper_id"], "abc123")
        self.assertEqual(evidence["sources"], ["pubmed", "crossref", "semantic_scholar"])
        self.assertEqual(evidence["citation_count"], 9)
        self.assertTrue(evidence["is_open_access"])
        self.assertEqual(set(evidence["source_urls"]), {"pubmed", "crossref", "semantic_scholar"})

    def test_deduplicates_by_normalized_title_without_identifiers(self) -> None:
        source_results = {
            "pubmed": {"papers": [{"title": "Evidence-based Medicine: An Overview"}]},
            "crossref": {"works": [{"title": "Evidence Based Medicine — An Overview"}]},
            "semantic_scholar": {"papers": []},
        }
        with patch.object(self.tool, "_collect_sources", return_value=source_results):
            result = self.tool.execute("evidence based medicine")
        self.assertEqual(result["deduplicated_result_count"], 1)
        self.assertEqual(result["evidence"][0]["sources"], ["pubmed", "crossref"])

    def test_does_not_merge_same_title_when_dois_conflict(self) -> None:
        source_results = {
            "pubmed": {
                "papers": [
                    {"doi": "10.1000/first", "title": "A deliberately shared title"},
                ]
            },
            "crossref": {
                "works": [
                    {"doi": "10.1000/second", "title": "A deliberately shared title"},
                ]
            },
            "semantic_scholar": {"papers": []},
        }
        with patch.object(self.tool, "_collect_sources", return_value=source_results):
            result = self.tool.execute("shared title")
        self.assertEqual(result["deduplicated_result_count"], 2)

    def test_rejects_unsafe_source_urls_and_builds_encoded_doi_url(self) -> None:
        source_results = {
            "pubmed": {"papers": []},
            "crossref": {
                "works": [
                    {
                        "doi": "10.1000/example(1)",
                        "title": "A work with an unsafe metadata URL",
                        "url": "javascript:alert(1)",
                    }
                ]
            },
            "semantic_scholar": {"papers": []},
        }
        with patch.object(self.tool, "_collect_sources", return_value=source_results):
            result = self.tool.execute("unsafe URL")
        self.assertEqual(
            result["evidence"][0]["source_urls"]["crossref"],
            "https://doi.org/10.1000/example%281%29",
        )

    def test_reports_partial_failure_and_keeps_successful_records(self) -> None:
        source_results = {
            "pubmed": {
                "papers": [],
                "error": {
                    "type": "request_timeout",
                    "message": "https://example.test/?api_key=secret",
                },
            },
            "crossref": {"works": [{"doi": "10.1000/one", "title": "One useful work"}]},
            "semantic_scholar": {"papers": []},
        }
        with patch.object(self.tool, "_collect_sources", return_value=source_results):
            result = self.tool.execute("useful work")
        self.assertEqual(result["returned_results"], 1)
        self.assertEqual(result["source_status"][0]["status"], "error")
        self.assertEqual(result["source_status"][0]["error"]["message"], "PubMed request timed out.")
        self.assertNotIn("secret", result["source_status"][0]["error"]["message"])
        self.assertEqual(result["source_status"][1]["status"], "ok")
        self.assertEqual(result["source_status"][2]["status"], "empty")

    def test_bounds_output_and_assigns_stable_evidence_ids(self) -> None:
        source_results = {
            "pubmed": {
                "papers": [{"pmid": str(index), "title": f"Unique paper number {index}"} for index in range(1, 5)]
            },
            "crossref": {"works": []},
            "semantic_scholar": {"papers": []},
        }
        with patch.object(self.tool, "_collect_sources", return_value=source_results):
            result = self.tool.execute("bounded results", max_evidence=2)
        self.assertTrue(result["truncated"])
        self.assertEqual([item["evidence_id"] for item in result["evidence"]], ["E1", "E2"])

    def test_rejects_invalid_inputs(self) -> None:
        invalid_calls = (
            {"query": ""},
            {"query": "x" * 501},
            {"query": "valid", "max_results_per_source": 0},
            {"query": "valid", "max_results_per_source": True},
            {"query": "valid", "max_evidence": 16},
        )
        for arguments in invalid_calls:
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                self.tool.execute(**arguments)

    def test_source_exception_is_sanitized(self) -> None:
        class BrokenTool:
            def execute(self, **_kwargs):
                raise _SensitiveUpstreamError

        result = self.tool._run_source("broken", BrokenTool, "papers", "query", 1)
        self.assertEqual(result["error"]["type"], "source_execution_error")
        self.assertNotIn("secret", result["error"]["message"])

    def test_invalid_source_response_is_structured(self) -> None:
        class InvalidTool:
            def execute(self, **_kwargs):
                return ["not", "a", "mapping"]

        result = self.tool._run_source("invalid", InvalidTool, "papers", "query", 1)
        self.assertEqual(result["papers"], [])
        self.assertEqual(result["error"]["type"], "invalid_source_response")


if __name__ == "__main__":
    unittest.main()
