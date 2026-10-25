"""Verify quoted spans against caller-supplied source snapshots, offline."""
import hashlib
import re

from pydantic import StrictInt

from agentuniverse.agent.action.tool.tool import Tool


class CitationVerifierTool(Tool):
    """Check provenance consistency, never truth, entailment or source credibility.

    Source IDs map to exact text. Each citation supplies source_id, start, end,
    quote and optionally source_sha256. Offsets are Python Unicode-codepoint
    indices, zero-based and end-exclusive, not UTF-8 bytes or UTF-16 offsets.
    """
    max_source_chars: StrictInt = 2000000
    max_sources: StrictInt = 100
    max_citations: StrictInt = 200
    max_quote_chars: StrictInt = 10000

    def _validate_options(self):
        for name in ("max_source_chars", "max_sources", "max_citations", "max_quote_chars"):
            if type(getattr(self, name)) is not int or getattr(self, name) <= 0:
                raise ValueError(f"{name} must be a positive integer")

    def execute(self, sources: dict, citations: list) -> dict:
        """Return ordered status codes without echoing quotes or source contents.

        Invalid top-level data/configuration raises ValueError. Malformed
        individual citation records yield invalid_citation and do not disappear.
        Empty citation input has all_verified=False (not vacuous success).
        """
        self._validate_options()
        if not isinstance(sources, dict) or len(sources) > self.max_sources:
            raise ValueError("sources must be a bounded mapping")
        if any(not isinstance(key, str) or not key or len(key) > 256 or not isinstance(value, str)
               for key, value in sources.items()):
            raise ValueError("sources require nonempty short string IDs and text values")
        if sum(len(value) for value in sources.values()) > self.max_source_chars:
            raise ValueError("source texts exceed max_source_chars")
        if not isinstance(citations, list) or len(citations) > self.max_citations:
            raise ValueError("citations must be a bounded list")
        hashes = {}
        results = []
        for index, citation in enumerate(citations):
            status = self._check(sources, hashes, citation)
            results.append({"index": index, "status": status, "verified": status == "verified"})
        count = sum(row["verified"] for row in results)
        return {"results": results, "verified_count": count, "citation_count": len(results),
                "all_verified": bool(results) and count == len(results),
                "verification_scope": "exact_quote_and_optional_source_hash_only"}

    def _check(self, sources, hashes, citation):
        required = {"source_id", "start", "end", "quote"}
        if (not isinstance(citation, dict) or not required <= citation.keys() or
                set(citation) - required - {"source_sha256"}):
            return "invalid_citation"
        identity, start, end, quote = (citation[key] for key in ("source_id", "start", "end", "quote"))
        if (not isinstance(identity, str) or not identity or len(identity) > 256 or
                type(start) is not int or type(end) is not int or
                not isinstance(quote, str) or not quote or len(quote) > self.max_quote_chars):
            return "invalid_citation"
        expected_hash = citation.get("source_sha256")
        if "source_sha256" in citation and (not isinstance(expected_hash, str) or
                not re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash)):
            return "invalid_citation"
        if identity not in sources:
            return "source_missing"
        text = sources[identity]
        if expected_hash is not None:
            if identity not in hashes:
                hashes[identity] = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if hashes[identity] != expected_hash.lower():
                return "source_changed"
        if not 0 <= start < end <= len(text):
            return "span_out_of_bounds"
        if text[start:end] != quote:
            return "quote_mismatch"
        return "verified"

    def initialize_by_component_configer(self, config):
        """Validate limits before Tool's public initializer mutates this instance."""
        names = ("max_source_chars", "max_sources", "max_citations", "max_quote_chars")
        validated = CitationVerifierTool(**{name: getattr(config, name, getattr(self, name)) for name in names})
        validated._validate_options()
        super().initialize_by_component_configer(config)
        for name in names:
            setattr(self, name, getattr(validated, name))
        return self
