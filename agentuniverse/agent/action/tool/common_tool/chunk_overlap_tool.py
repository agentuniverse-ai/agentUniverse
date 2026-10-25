#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/21
# @Author  : agentUniverse contributors
# @FileName: chunk_overlap_tool.py

"""Chunking QA tool — analyze and validate chunking RESULTS (stdlib only).

Addresses the *other tools* item of issue #252 (tool plug-in
integration). Where ``TextChunkerTool`` (#3503) and the upstream
splitter components (``RecursiveCharacterTextSplitter`` etc., issue
#258) CREATE chunks from text, this tool goes the other way: it takes
an EXISTING chunk list — the output of any splitter, ours or a foreign
pipeline — and reports whether that chunking is any good. It is the QA
layer for RAG pipelines debugging their chunking: retrieval misses are
often caused not by the retriever but by chunks that leave source
regions uncovered, overlap too little (split facts) or too much
(duplicated embedding cost), or drift out of source order.

Four modes:

* ``analyze`` — a chunk list (plus an optional ``source_text``) to a
  one-shot report: ``count``; ``sizes`` ``{min, mean, median, max,
  total}``; ``overlap_stats`` between CONSECUTIVE chunks via exact
  suffix/prefix matching (``pairs_with_overlap``, ``max_overlap_chars``,
  ``mean_overlap_chars``); positional ``adjacency`` of consecutive
  chunks (contiguous vs overlapping vs gapped, from located char
  offsets) — requires the source; and ``coverage`` when the source is
  given: ``covered_ratio`` (union of located chunk spans over the
  source), ``missing_spans`` (source regions no chunk covers, capped
  at 20) and ``duplicated_regions`` (regions covered by two or more
  chunks, capped at 20) — every listed span carries its offsets, its
  length and the span text capped at 50 characters as ``preview``.
* ``coverage`` — chunks plus ``source_text`` (required) to the detail
  view: per-chunk ``{found, positions, span, chars}`` (all exact
  occurrence starts, capped at 100) and a source heatmap per 100-char
  bucket (per-bucket covered ratio plus fully / partially / uncovered
  counts; the bucket list is capped at 1,000 buckets with aggregate
  counts always covering the whole source).
* ``overlap_matrix`` — pairwise consecutive-window overlap: for every
  chunk pair ``(i, j)`` with ``i < j <= i + window`` (``window``
  default 1 = consecutive only, capped at 100 and 200,000 checked
  pairs) the exact suffix/prefix overlap length, reported for the
  pairs with a non-zero overlap (capped at 2,000 entries) with the
  shared text preview.
* ``validate`` — chunks plus a ``policy`` against chunking invariants:
  ``min_chars`` / ``max_chars`` (per-chunk size bounds, offending chunk
  indices), ``max_overlap`` (consecutive suffix/prefix overlap,
  offending pairs) and ``min_coverage`` (located-span coverage of the
  source, requires ``source_text``); every rule reports an independent
  pass/fail and the result carries an ``all_pass`` flag. Every bound is
  inclusive: a chunk of exactly ``min_chars`` / ``max_chars``
  characters passes, a consecutive overlap of exactly ``max_overlap``
  characters passes and coverage exactly equal to ``min_coverage``
  passes (only strictly worse values fail), with ``min_coverage``
  compared at full precision before any display rounding.

Conventions, pinned for determinism:

* Offsets are Python ``str`` code-point indices — one CJK ideograph
  (or astral character) is exactly one character. Offsets are never
  byte or UTF-16 offsets.
* Chunk location is exact-substring and greedy-sequential: chunk i is
  located at the first occurrence at or after ``previous start + 1``,
  so chunks are assumed to appear in source order. A chunk occurring
  more often than it is listed (or not at all) stays ``unlocated`` —
  reported, never guessed. Empty chunk strings are trivially found
  but contribute no span and no coverage (documented vacuous case).
* Two different overlaps are reported and never conflated: the
  TEXTUAL overlap (a suffix of chunk i equals a prefix of chunk i+1)
  and the POSITIONAL overlap (located spans intersect). For located
  chunks an overlapping span region is the same substring on both
  sides, so positional overlap always implies an equal textual
  overlap; textual overlap with contiguous spans (or beyond the
  positional one) is the signal of repeated content.
* Exact overlap search scans suffix/prefix matches up to
  ``MAX_OVERLAP_SCAN`` (10,000) characters; for longer chunk pairs the
  result is flagged ``scan_cap_reached`` (overlaps beyond 10,000
  characters are pathological for chunking).
* Zero-denominator ratios are ``0.0`` (an empty source is covered
  0.0); ratios are reported at 4 decimal places; the median of an odd
  count is the middle size (int), of an even count the mean of the two
  middle sizes (float). An empty chunk list is valid input and reports
  ``count 0`` with null size statistics and (with a source) a single
  missing span covering everything.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode, a non-list chunk list, a non-string
member, over 10,000 chunks, over 10 MB of chunk text, a non-string or
over 10 MB source, a bad ``window``, an empty / unknown-key / bad-value
policy, the ``min_coverage`` rule without a source, or a parameter that
does not belong to the selected mode) raise a ``ValueError``, mirroring
the other common tools.
"""

from typing import Any, ClassVar, Dict, List, Optional, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool


class ChunkOverlapTool(Tool):
    """Chunking QA tool — inspect and validate an existing chunk list.

    The tool never splits text itself; it measures a chunk list that
    some splitter produced. Input bounds (rejected before any
    computation): at most :obj:`MAX_CHUNKS` chunks, at most
    :obj:`MAX_TOTAL_CHUNK_CHARS` characters of chunk text in total and
    a source of at most :obj:`MAX_SOURCE_CHARS` characters. An empty
    chunk list is accepted with the documented null conventions.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "chunk_overlap_tool"
    description: str = (
        "Chunking QA tool — pure Python stdlib, no network required. "
        "Analyzes and validates the RESULT of any text splitter: given "
        "an existing chunk list (and optionally the source text it came "
        "from) it reports chunk size statistics (min/mean/median/max/"
        "total), textual overlap between consecutive chunks (exact "
        "suffix/prefix matching), positional adjacency (contiguous vs "
        "overlapping vs gapped char offsets), source coverage "
        "(covered_ratio, missing_spans, duplicated_regions via exact "
        "substring location, greedy in source order), a per-100-char-"
        "bucket coverage heatmap, a pairwise consecutive-window overlap "
        "matrix and policy validation (min_chars / max_chars / "
        "max_overlap / min_coverage, each rule with an independent "
        "pass/fail and offending indices). Offsets are code-point "
        "indices (CJK-safe). The companion of TextChunkerTool and the "
        "upstream splitters: those CREATE chunks, this tool checks them."
    )

    MODES: ClassVar[tuple] = (
        "analyze",
        "coverage",
        "overlap_matrix",
        "validate",
    )

    POLICY_KEYS: ClassVar[tuple] = (
        "min_chars",
        "max_chars",
        "max_overlap",
        "min_coverage",
    )

    # Input bounds (see the class docstring).
    MAX_CHUNKS: ClassVar[int] = 10_000
    MAX_TOTAL_CHUNK_CHARS: ClassVar[int] = 10_000_000
    MAX_SOURCE_CHARS: ClassVar[int] = 10_000_000
    # Overlap search bound (see the module docstring).
    MAX_OVERLAP_SCAN: ClassVar[int] = 10_000
    # overlap_matrix bounds.
    MAX_WINDOW: ClassVar[int] = 100
    MAX_PAIRS: ClassVar[int] = 200_000
    MAX_MATRIX_ENTRIES: ClassVar[int] = 2_000
    # Reporting caps (the full counts are always reported alongside).
    MAX_MISSING_SPANS: ClassVar[int] = 20
    MAX_DUPLICATED_REGIONS: ClassVar[int] = 20
    MAX_POSITIONS: ClassVar[int] = 100
    MAX_OFFENDERS: ClassVar[int] = 100
    MAX_PAIR_DETAIL: ClassVar[int] = 100
    BUCKET_CHARS: ClassVar[int] = 100
    MAX_HEATMAP_BUCKETS: ClassVar[int] = 1_000
    MAX_SPAN_PREVIEW: ClassVar[int] = 50
    MAX_OVERLAP_PREVIEW: ClassVar[int] = 40
    # Ratios are reported at this precision.
    RATIO_DECIMALS: ClassVar[int] = 4

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: Any = None,
        chunks: Any = None,
        source_text: Any = None,
        window: Any = None,
        policy: Any = None,
    ) -> Dict[str, Any]:
        """Run one chunking QA query.

        Args:
            mode (str): One of ``analyze`` / ``coverage`` /
                ``overlap_matrix`` / ``validate``.
            chunks (list[str]): The chunk list to inspect — the output
                of any splitter. An empty list is valid (documented
                null conventions); at most 10,000 strings and 10 MB of
                text in total. Individual chunks may be empty strings.
            source_text (str): The source the chunks came from.
                Optional in ``analyze`` (enables adjacency + coverage),
                required in ``coverage``, rejected in ``overlap_matrix``
                and required in ``validate`` when the policy has a
                ``min_coverage`` rule. Capped at 10 MB.
            window (int): ``overlap_matrix`` only — compare chunk ``i``
                with chunks ``i+1 .. i+window`` (default 1 =
                consecutive pairs only; 1 to 100, at most 200,000
                checked pairs).
            policy (dict): ``validate`` only — a non-empty dict with
                any of ``min_chars`` (int >= 0), ``max_chars``
                (int >= 1, >= ``min_chars`` when both present),
                ``max_overlap`` (int >= 0, consecutive textual overlap)
                and ``min_coverage`` (number 0..1, needs
                ``source_text``). All bounds are inclusive: a value
                exactly at a bound passes, only strictly worse values
                fail.

        Returns:
            Dict[str, Any]: The mode result as described in the module
            docstring.

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_chunks = self._validate_chunks(chunks)
        clean_source = self._validate_source(source_text)

        if mode == "analyze":
            if window is not None:
                self._invalid("analyze mode does not take a window")
            if policy is not None:
                self._invalid(
                    "analyze mode does not take a policy (use validate)"
                )
            return self._run_analyze(clean_chunks, clean_source)

        if mode == "coverage":
            if clean_source is None:
                self._invalid("coverage mode requires source_text")
            if window is not None:
                self._invalid("coverage mode does not take a window")
            if policy is not None:
                self._invalid("coverage mode does not take a policy")
            return self._run_coverage(clean_chunks, clean_source)

        if mode == "overlap_matrix":
            if clean_source is not None:
                self._invalid(
                    "overlap_matrix mode measures chunk-to-chunk overlap "
                    "and does not take a source_text"
                )
            if policy is not None:
                self._invalid("overlap_matrix mode does not take a policy")
            clean_window = self._validate_window(window, len(clean_chunks))
            return self._run_overlap_matrix(clean_chunks, clean_window)

        # validate mode
        if window is not None:
            self._invalid("validate mode does not take a window")
        clean_policy = self._validate_policy(policy)
        if "min_coverage" in clean_policy and clean_source is None:
            self._invalid(
                "the min_coverage rule requires source_text (the source "
                "the chunks came from)"
            )
        return self._run_validate(clean_chunks, clean_policy, clean_source)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"chunk_overlap_tool: {message}")

    @classmethod
    def _validate_chunks(cls, value: Any) -> List[str]:
        """Validate the chunk list (a list of strings, capped).

        An EMPTY list is valid — it is a chunking result worth
        reporting on (count 0, null sizes, everything uncovered).
        Empty chunk strings are valid too (they are surfaced by the
        size statistics and the min_chars rule).
        """
        if isinstance(value, bool) or not isinstance(value, list):
            cls._invalid(
                f"chunks must be a list of strings (got {value!r})"
            )
        if len(value) > cls.MAX_CHUNKS:
            cls._invalid(
                f"chunks exceeds the {cls.MAX_CHUNKS:,}-item limit "
                f"(got {len(value):,} items)"
            )
        total = 0
        for index, item in enumerate(value):
            bad = (
                item is None
                or isinstance(item, bool)
                or not isinstance(item, str)
            )
            if bad:
                cls._invalid(
                    f"chunks[{index}] must be a string (got {item!r})"
                )
            total += len(item)
            if total > cls.MAX_TOTAL_CHUNK_CHARS:
                cls._invalid(
                    "chunks exceeds the "
                    f"{cls.MAX_TOTAL_CHUNK_CHARS:,}-character total "
                    f"limit (over {total:,} characters)"
                )
        return value

    @classmethod
    def _validate_source(cls, value: Any) -> Optional[str]:
        """Validate the optional source text (capped at 10 MB)."""
        if value is None:
            return None
        if isinstance(value, bool) or not isinstance(value, str):
            cls._invalid(f"source_text must be a string (got {value!r})")
        if len(value) > cls.MAX_SOURCE_CHARS:
            cls._invalid(
                f"source_text exceeds the {cls.MAX_SOURCE_CHARS:,}-"
                f"character limit (got {len(value):,} characters)"
            )
        return value

    @classmethod
    def _validate_window(cls, value: Any, chunk_count: int) -> int:
        """Validate the overlap_matrix window and its pair budget."""
        if value is None:
            value = 1
        if isinstance(value, bool) or not isinstance(value, int):
            cls._invalid(f"window must be an integer (got {value!r})")
        if value < 1 or value > cls.MAX_WINDOW:
            cls._invalid(
                f"window must be between 1 and {cls.MAX_WINDOW} "
                f"(got {value!r})"
            )
        if chunk_count > 1:
            if value >= chunk_count:
                pairs = chunk_count * (chunk_count - 1) // 2
            else:
                # sum over i of min(window, chunk_count - 1 - i)
                pairs = (
                    (chunk_count - value) * value
                    + value * (value - 1) // 2
                )
            if pairs > cls.MAX_PAIRS:
                cls._invalid(
                    f"window {value} over {chunk_count:,} chunks checks "
                    f"{pairs:,} pairs — over the {cls.MAX_PAIRS:,}-pair "
                    "limit (narrow the window)"
                )
        return value

    @classmethod
    def _validate_policy(cls, value: Any) -> Dict[str, Any]:
        """Validate the validate-mode policy (non-empty, known keys)."""
        if isinstance(value, bool) or not isinstance(value, dict):
            cls._invalid(
                "policy must be a dict with any of: "
                f"{', '.join(cls.POLICY_KEYS)} (got {value!r})"
            )
        unknown = [key for key in value if key not in cls.POLICY_KEYS]
        if unknown:
            cls._invalid(
                f"policy has unknown key(s): {', '.join(sorted(unknown))} "
                f"(allowed: {', '.join(cls.POLICY_KEYS)})"
            )
        if not value:
            cls._invalid(
                "policy must contain at least one rule: "
                f"{', '.join(cls.POLICY_KEYS)}"
            )
        for key in ("min_chars", "max_chars", "max_overlap"):
            if key in value:
                bound = value[key]
                if (
                    isinstance(bound, bool)
                    or not isinstance(bound, int)
                    or bound < 0
                ):
                    cls._invalid(
                        f"policy[{key!r}] must be an integer >= 0 "
                        f"(got {bound!r})"
                    )
        if "max_chars" in value and value["max_chars"] < 1:
            cls._invalid(
                "policy['max_chars'] must be >= 1 (got "
                f"{value['max_chars']!r})"
            )
        if (
            "min_chars" in value
            and "max_chars" in value
            and value["min_chars"] > value["max_chars"]
        ):
            cls._invalid(
                "policy['min_chars'] must not exceed policy['max_chars'] "
                f"(got {value['min_chars']!r} > {value['max_chars']!r})"
            )
        if "min_coverage" in value:
            bound = value["min_coverage"]
            if isinstance(bound, bool) or not isinstance(bound, (int, float)):
                cls._invalid(
                    f"policy['min_coverage'] must be a number between 0 "
                    f"and 1 (got {bound!r})"
                )
            number = float(bound)
            if not 0.0 <= number <= 1.0:
                cls._invalid(
                    f"policy['min_coverage'] must be a number between 0 "
                    f"and 1 (got {bound!r})"
                )
        return value

    # ------------------------------------------------------------------ #
    # Core primitives (pure, shared by every mode)
    # ------------------------------------------------------------------ #

    @classmethod
    def _pair_overlap(cls, first: str, second: str) -> Tuple[int, bool]:
        """Exact textual overlap of two chunks (suffix of first == prefix
        of second).

        Returns ``(overlap_chars, scan_capped)`` where ``scan_capped``
        is True when the pair is longer than :obj:`MAX_OVERLAP_SCAN`
        on both sides — the exact search then starts (and the result is
        reliable only) up to that cap.
        """
        limit = min(len(first), len(second), cls.MAX_OVERLAP_SCAN)
        capped = min(len(first), len(second)) > cls.MAX_OVERLAP_SCAN
        for k in range(limit, 0, -1):
            if first[len(first) - k:] == second[:k]:
                return k, capped
        return 0, capped

    @classmethod
    def _locate_spans(
        cls, chunks: List[str], source: str
    ) -> List[Optional[Tuple[int, int]]]:
        """Locate every chunk in the source — greedy and sequential.

        Chunk ``i`` is placed at the first occurrence at or after
        ``previous start + 1`` (so chunks are assumed to appear in
        source order; overlapping windows step back, duplicates step
        forward). A chunk that occurs no earlier — or not at all —
        stays ``None`` (reported as unlocated, never guessed). An
        empty chunk string is never located (it contributes no span).
        """
        spans: List[Optional[Tuple[int, int]]] = []
        cursor = 0
        for chunk in chunks:
            if not chunk:
                spans.append(None)
                continue
            pos = source.find(chunk, cursor)
            if pos == -1:
                spans.append(None)
            else:
                spans.append((pos, pos + len(chunk)))
                cursor = pos + 1
        return spans

    @classmethod
    def _all_positions(cls, chunk: str, source: str) -> Tuple[int, List[int]]:
        """All exact occurrence starts of ``chunk`` in ``source``.

        Returns ``(count, positions)`` — the true total and at most
        :obj:`MAX_POSITIONS` stored starts (in ascending order).
        """
        positions: List[int] = []
        count = 0
        start = 0
        while True:
            pos = source.find(chunk, start)
            if pos == -1:
                break
            count += 1
            if len(positions) < cls.MAX_POSITIONS:
                positions.append(pos)
            start = pos + 1
        return count, positions

    @classmethod
    def _merge_spans(
        cls, spans: List[Optional[Tuple[int, int]]]
    ) -> List[List[int]]:
        """Merge the located spans into a sorted disjoint union."""
        present = sorted(span for span in spans if span is not None)
        merged: List[List[int]] = []
        for start, end in present:
            if merged and start <= merged[-1][1]:
                if end > merged[-1][1]:
                    merged[-1][1] = end
            else:
                merged.append([start, end])
        return merged

    @classmethod
    def _missing_spans(
        cls, merged: List[List[int]], source: str
    ) -> Tuple[List[Dict[str, Any]], int, bool]:
        """Source regions no located chunk covers.

        Returns ``(details, total_count, truncated)`` — the details are
        capped at :obj:`MAX_MISSING_SPANS`; the total count is exact.
        """
        missing: List[Dict[str, Any]] = []
        total = 0
        truncated = False
        cursor = 0
        source_len = len(source)
        for start, end in merged + [[source_len, source_len]]:
            if start > cursor:
                total += 1
                if len(missing) >= cls.MAX_MISSING_SPANS:
                    truncated = True
                else:
                    missing.append(
                        {
                            "start": cursor,
                            "end": start,
                            "chars": start - cursor,
                            "preview": source[
                                cursor : min(
                                    start, cursor + cls.MAX_SPAN_PREVIEW
                                )
                            ],
                        }
                    )
            if end > cursor:
                cursor = end
        return missing, total, truncated

    @classmethod
    def _duplicated_regions(
        cls, spans: List[Optional[Tuple[int, int]]], source: str
    ) -> Dict[str, Any]:
        """Source regions covered by two or more located chunk spans.

        Classic sweep over the span boundaries (a run is closed before
        the next delta is applied, so touching spans are NOT
        duplicated); adjacent runs are merged, regions capped at 20.
        """
        events: List[Tuple[int, int]] = []
        for span in spans:
            if span is not None:
                events.append((span[0], 1))
                events.append((span[1], -1))
        events.sort()
        regions: List[List[int]] = []
        depth = 0
        prev: Optional[int] = None
        for pos, delta in events:
            if depth >= 2 and prev is not None and pos > prev:
                if regions and regions[-1][1] == prev:
                    regions[-1][1] = pos
                else:
                    regions.append([prev, pos])
            depth += delta
            prev = pos
        region_details: List[Dict[str, Any]] = []
        truncated = False
        for start, end in regions:
            if len(region_details) >= cls.MAX_DUPLICATED_REGIONS:
                truncated = True
            else:
                region_details.append(
                    {
                        "start": start,
                        "end": end,
                        "chars": end - start,
                        "preview": source[
                            start : min(end, start + cls.MAX_SPAN_PREVIEW)
                        ],
                    }
                )
        return {
            "region_count": len(regions),
            "total_chars": sum(end - start for start, end in regions),
            "regions": region_details,
            "truncated": truncated,
        }

    @classmethod
    def _coverage_summary(
        cls, spans: List[Optional[Tuple[int, int]]], source: str
    ) -> Dict[str, Any]:
        """Coverage block shared by analyze and coverage modes."""
        merged = cls._merge_spans(spans)
        covered_chars = sum(end - start for start, end in merged)
        source_len = len(source)
        covered_ratio = (
            round(covered_chars / source_len, cls.RATIO_DECIMALS)
            if source_len
            else 0.0
        )
        missing, missing_total, missing_truncated = cls._missing_spans(
            merged, source
        )
        return {
            "source_chars": source_len,
            "covered_chars": covered_chars,
            "covered_ratio": covered_ratio,
            "missing_span_count": missing_total,
            "missing_spans": missing,
            "missing_spans_truncated": missing_truncated,
            "duplicated_regions": cls._duplicated_regions(spans, source),
        }

    # ------------------------------------------------------------------ #
    # analyze mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _size_stats(cls, chunks: List[str]) -> Dict[str, Any]:
        """Chunk size statistics (count > 0 assumed handled by caller)."""
        lengths = [len(chunk) for chunk in chunks]
        if not lengths:
            return {
                "min": None,
                "mean": None,
                "median": None,
                "max": None,
                "total": 0,
            }
        ordered = sorted(lengths)
        middle = len(ordered) // 2
        if len(ordered) % 2:
            median: Any = ordered[middle]
        else:
            median = round(
                (ordered[middle - 1] + ordered[middle]) / 2, cls.RATIO_DECIMALS
            )
        return {
            "min": ordered[0],
            "mean": round(sum(ordered) / len(ordered), cls.RATIO_DECIMALS),
            "median": median,
            "max": ordered[-1],
            "total": sum(ordered),
        }

    @classmethod
    def _consecutive_overlaps(cls, chunks: List[str]) -> Dict[str, Any]:
        """Textual overlap stats between consecutive chunks."""
        pairs = len(chunks) - 1 if len(chunks) >= 2 else 0
        if pairs <= 0:
            return {
                "pairs": 0,
                "pairs_with_overlap": 0,
                "max_overlap_chars": 0,
                "mean_overlap_chars": 0.0,
                "scan_cap": cls.MAX_OVERLAP_SCAN,
                "scan_cap_reached": False,
            }
        overlap_sum = 0
        max_overlap = 0
        with_overlap = 0
        capped = False
        for index in range(len(chunks) - 1):
            chars, scan_capped = cls._pair_overlap(
                chunks[index], chunks[index + 1]
            )
            capped = capped or scan_capped
            overlap_sum += chars
            if chars > 0:
                with_overlap += 1
            if chars > max_overlap:
                max_overlap = chars
        return {
            "pairs": pairs,
            "pairs_with_overlap": with_overlap,
            "max_overlap_chars": max_overlap,
            "mean_overlap_chars": round(
                overlap_sum / pairs, cls.RATIO_DECIMALS
            ),
            "scan_cap": cls.MAX_OVERLAP_SCAN,
            "scan_cap_reached": capped,
        }

    @classmethod
    def _adjacency(
        cls, spans: List[Optional[Tuple[int, int]]]
    ) -> Dict[str, Any]:
        """Positional adjacency of consecutive located chunks."""
        result = {
            "pairs": len(spans) - 1 if len(spans) >= 2 else 0,
            "contiguous_pairs": 0,
            "overlapping_pairs": 0,
            "gapped_pairs": 0,
            "unlocated_pairs": 0,
            "max_gap_chars": 0,
            "max_overlap_chars": 0,
            "pairs_detail": [],
            "detail_truncated": False,
        }
        for index in range(len(spans) - 1):
            first, second = spans[index], spans[index + 1]
            entry: Dict[str, Any] = {"pair": [index, index + 1]}
            if first is None or second is None:
                kind = "unlocated"
                entry["type"] = kind
                if first is not None:
                    entry["first"] = [first[0], first[1]]
                if second is not None:
                    entry["second"] = [second[0], second[1]]
            else:
                entry["first"] = [first[0], first[1]]
                entry["second"] = [second[0], second[1]]
                if second[0] == first[1]:
                    kind = "contiguous"
                elif second[0] < first[1]:
                    kind = "overlapping"
                    chars = first[1] - second[0]
                    entry["chars"] = chars
                    if chars > result["max_overlap_chars"]:
                        result["max_overlap_chars"] = chars
                else:
                    kind = "gapped"
                    chars = second[0] - first[1]
                    entry["chars"] = chars
                    if chars > result["max_gap_chars"]:
                        result["max_gap_chars"] = chars
                entry["type"] = kind
            result[f"{kind}_pairs"] += 1
            if len(result["pairs_detail"]) < cls.MAX_PAIR_DETAIL:
                result["pairs_detail"].append(entry)
            else:
                result["detail_truncated"] = True
        return result

    def _run_analyze(
        self, chunks: List[str], source: Optional[str]
    ) -> Dict[str, Any]:
        """The one-shot chunking report."""
        result: Dict[str, Any] = {
            "mode": "analyze",
            "count": len(chunks),
            "sizes": self._size_stats(chunks),
            "overlap_stats": self._consecutive_overlaps(chunks),
            "adjacency": None,
            "coverage": None,
        }
        if source is not None:
            result["source_chars"] = len(source)
            spans = self._locate_spans(chunks, source)
            result["adjacency"] = self._adjacency(spans)
            result["coverage"] = self._coverage_summary(spans, source)
        return result

    # ------------------------------------------------------------------ #
    # coverage mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _heatmap(
        cls, merged: List[List[int]], source: str
    ) -> Dict[str, Any]:
        """Per-100-char-bucket covered ratio plus aggregate counts."""
        bucket_chars = cls.BUCKET_CHARS
        source_len = len(source)
        bucket_count = (
            (source_len + bucket_chars - 1) // bucket_chars
            if source_len
            else 0
        )
        covered = [0] * bucket_count
        for start, end in merged:
            first = start // bucket_chars
            last = (end - 1) // bucket_chars
            for bucket in range(first, last + 1):
                bucket_start = bucket * bucket_chars
                bucket_end = min(bucket_start + bucket_chars, source_len)
                amount = min(end, bucket_end) - max(start, bucket_start)
                if amount > 0:
                    covered[bucket] += amount
        fully = 0
        partial = 0
        uncovered = 0
        buckets: List[Dict[str, Any]] = []
        truncated = False
        for bucket in range(bucket_count):
            bucket_start = bucket * bucket_chars
            bucket_end = min(bucket_start + bucket_chars, source_len)
            ratio = round(
                covered[bucket] / (bucket_end - bucket_start),
                cls.RATIO_DECIMALS,
            )
            if ratio >= 1.0:
                fully += 1
            elif ratio > 0.0:
                partial += 1
            else:
                uncovered += 1
            if len(buckets) < cls.MAX_HEATMAP_BUCKETS:
                buckets.append(
                    {
                        "start": bucket_start,
                        "end": bucket_end,
                        "covered_ratio": ratio,
                    }
                )
            else:
                truncated = True
        return {
            "bucket_chars": bucket_chars,
            "bucket_count": bucket_count,
            "fully_covered_buckets": fully,
            "partially_covered_buckets": partial,
            "uncovered_buckets": uncovered,
            "buckets": buckets,
            "truncated": truncated,
        }

    def _run_coverage(self, chunks: List[str], source: str) -> Dict[str, Any]:
        """The per-chunk location detail plus the source heatmap."""
        spans = self._locate_spans(chunks, source)
        per_chunk: List[Dict[str, Any]] = []
        for index, chunk in enumerate(chunks):
            if not chunk:
                per_chunk.append(
                    {
                        "index": index,
                        "chars": 0,
                        "found": True,
                        "positions": [],
                        "position_count": 0,
                        "positions_truncated": False,
                        "span": None,
                    }
                )
                continue
            count, positions = self._all_positions(chunk, source)
            per_chunk.append(
                {
                    "index": index,
                    "chars": len(chunk),
                    "found": count > 0,
                    "positions": positions,
                    "position_count": count,
                    "positions_truncated": count > len(positions),
                    "span": (
                        [spans[index][0], spans[index][1]]
                        if spans[index] is not None
                        else None
                    ),
                }
            )
        merged = self._merge_spans(spans)
        return {
            "mode": "coverage",
            "chunk_count": len(chunks),
            "source_chars": len(source),
            "per_chunk": per_chunk,
            "coverage": self._coverage_summary(spans, source),
            "heatmap": self._heatmap(merged, source),
        }

    # ------------------------------------------------------------------ #
    # overlap_matrix mode
    # ------------------------------------------------------------------ #

    def _run_overlap_matrix(
        self, chunks: List[str], window: int
    ) -> Dict[str, Any]:
        """Pairwise consecutive-window textual overlaps."""
        count = len(chunks)
        pairs_checked = 0
        pairs_with_overlap = 0
        max_overlap = 0
        overlap_sum = 0
        capped = False
        entries: List[Dict[str, Any]] = []
        entries_truncated = False
        for i in range(count):
            for j in range(i + 1, min(i + 1 + window, count)):
                pairs_checked += 1
                chars, scan_capped = self._pair_overlap(chunks[i], chunks[j])
                capped = capped or scan_capped
                overlap_sum += chars
                if chars > 0:
                    pairs_with_overlap += 1
                    if chars > max_overlap:
                        max_overlap = chars
                    if len(entries) < self.MAX_MATRIX_ENTRIES:
                        entries.append(
                            {
                                "i": i,
                                "j": j,
                                "chars": chars,
                                "overlap_text": chunks[i][
                                    len(chunks[i]) - chars:
                                ][: self.MAX_OVERLAP_PREVIEW],
                            }
                        )
                    else:
                        entries_truncated = True
        return {
            "mode": "overlap_matrix",
            "chunk_count": count,
            "window": window,
            "pairs_checked": pairs_checked,
            "pairs_with_overlap": pairs_with_overlap,
            "max_overlap_chars": max_overlap,
            "mean_overlap_chars": (
                round(overlap_sum / pairs_checked, self.RATIO_DECIMALS)
                if pairs_checked
                else 0.0
            ),
            "overlaps": entries,
            "entries_truncated": entries_truncated,
            "scan_cap": self.MAX_OVERLAP_SCAN,
            "scan_cap_reached": capped,
        }

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    @classmethod
    def _offending_indices(
        cls, offenders: List[int]
    ) -> Tuple[List[int], bool]:
        """Cap an offending-index list (full count reported by caller)."""
        return (
            offenders[: cls.MAX_OFFENDERS],
            len(offenders) > cls.MAX_OFFENDERS,
        )

    def _run_validate(
        self,
        chunks: List[str],
        policy: Dict[str, Any],
        source: Optional[str],
    ) -> Dict[str, Any]:
        """Policy validation — one independent result per rule."""
        rules: List[Dict[str, Any]] = []

        if "min_chars" in policy:
            offenders = [
                index
                for index, chunk in enumerate(chunks)
                if len(chunk) < policy["min_chars"]
            ]
            listed, truncated = self._offending_indices(offenders)
            rules.append(
                {
                    "rule": "min_chars",
                    "threshold": policy["min_chars"],
                    "pass": not offenders,
                    "violations": len(offenders),
                    "offending_indices": listed,
                    "offending_truncated": truncated,
                }
            )

        if "max_chars" in policy:
            offenders = [
                index
                for index, chunk in enumerate(chunks)
                if len(chunk) > policy["max_chars"]
            ]
            listed, truncated = self._offending_indices(offenders)
            rules.append(
                {
                    "rule": "max_chars",
                    "threshold": policy["max_chars"],
                    "pass": not offenders,
                    "violations": len(offenders),
                    "offending_indices": listed,
                    "offending_truncated": truncated,
                }
            )

        if "max_overlap" in policy:
            offending_pairs: List[List[int]] = []
            for index in range(len(chunks) - 1):
                chars, _ = self._pair_overlap(
                    chunks[index], chunks[index + 1]
                )
                if chars > policy["max_overlap"]:
                    offending_pairs.append([index, index + 1])
            listed_pairs = offending_pairs[: self.MAX_OFFENDERS]
            rules.append(
                {
                    "rule": "max_overlap",
                    "threshold": policy["max_overlap"],
                    "pass": not offending_pairs,
                    "violations": len(offending_pairs),
                    "offending_pairs": listed_pairs,
                    "offending_truncated": len(offending_pairs)
                    > self.MAX_OFFENDERS,
                }
            )

        if "min_coverage" in policy:
            spans = self._locate_spans(chunks, source or "")
            merged = self._merge_spans(spans)
            covered_chars = sum(end - start for start, end in merged)
            source_len = len(source or "")
            exact_ratio = (
                covered_chars / source_len if source_len else 0.0
            )
            rules.append(
                {
                    "rule": "min_coverage",
                    "threshold": float(policy["min_coverage"]),
                    "pass": exact_ratio >= float(policy["min_coverage"]),
                    "covered_ratio": round(
                        exact_ratio, self.RATIO_DECIMALS
                    ),
                }
            )

        return {
            "mode": "validate",
            "chunk_count": len(chunks),
            "policy": policy,
            "rules": rules,
            "all_pass": all(rule["pass"] for rule in rules),
        }
