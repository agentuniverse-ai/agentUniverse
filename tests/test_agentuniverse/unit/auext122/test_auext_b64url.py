"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten122kitten122", "a2l0dGVuMTIya2l0dGVuMTIy"),
    ("kitten122sitting122", "a2l0dGVuMTIyc2l0dGluZzEyMg"),
    ("kitten122agent122", "a2l0dGVuMTIyYWdlbnQxMjI"),
    ("kitten122angle122", "a2l0dGVuMTIyYW5nbGUxMjI"),
    ("sitting122angle122", "c2l0dGluZzEyMmFuZ2xlMTIy"),
    ("sitting122universe122", "c2l0dGluZzEyMnVuaXZlcnNlMTIy"),
    ("sitting122memory122", "c2l0dGluZzEyMm1lbW9yeTEyMg"),
    ("sitting122stream122", "c2l0dGluZzEyMnN0cmVhbTEyMg"),
    ("agent122stream122", "YWdlbnQxMjJzdHJlYW0xMjI"),
    ("agent122context122", "YWdlbnQxMjJjb250ZXh0MTIy"),
    ("agent122knowledge122", "YWdlbnQxMjJrbm93bGVkZ2UxMjI"),
    ("agent122vector122", "YWdlbnQxMjJ2ZWN0b3IxMjI"),
    ("angle122vector122", "YW5nbGUxMjJ2ZWN0b3IxMjI"),
    ("angle122processor122", "YW5nbGUxMjJwcm9jZXNzb3IxMjI"),
    ("angle122reasoning122", "YW5nbGUxMjJyZWFzb25pbmcxMjI"),
    ("angle122machine122", "YW5nbGUxMjJtYWNoaW5lMTIy"),
    ("universe122machine122", "dW5pdmVyc2UxMjJtYWNoaW5lMTIy"),
    ("universe122learning122", "dW5pdmVyc2UxMjJsZWFybmluZzEyMg"),
    ("universe122model122", "dW5pdmVyc2UxMjJtb2RlbDEyMg"),
    ("universe122token122", "dW5pdmVyc2UxMjJ0b2tlbjEyMg"),
    ("memory122token122", "bWVtb3J5MTIydG9rZW4xMjI"),
    ("memory122prompt122", "bWVtb3J5MTIycHJvbXB0MTIy"),
    ("memory122session122", "bWVtb3J5MTIyc2Vzc2lvbjEyMg"),
    ("memory122library122", "bWVtb3J5MTIybGlicmFyeTEyMg"),
    ("stream122library122", "c3RyZWFtMTIybGlicmFyeTEyMg"),
    ("stream122service122", "c3RyZWFtMTIyc2VydmljZTEyMg"),
    ("stream122gateway122", "c3RyZWFtMTIyZ2F0ZXdheTEyMg"),
    ("stream122storage122", "c3RyZWFtMTIyc3RvcmFnZTEyMg"),
    ("context122storage122", "Y29udGV4dDEyMnN0b3JhZ2UxMjI"),
    ("context122network122", "Y29udGV4dDEyMm5ldHdvcmsxMjI"),
    ("context122latency122", "Y29udGV4dDEyMmxhdGVuY3kxMjI"),
    ("context122buffer122", "Y29udGV4dDEyMmJ1ZmZlcjEyMg"),
    ("knowledge122buffer122", "a25vd2xlZGdlMTIyYnVmZmVyMTIy"),
    ("knowledge122queue122", "a25vd2xlZGdlMTIycXVldWUxMjI"),
    ("knowledge122worker122", "a25vd2xlZGdlMTIyd29ya2VyMTIy"),
    ("knowledge122kernel122", "a25vd2xlZGdlMTIya2VybmVsMTIy"),
    ("vector122kernel122", "dmVjdG9yMTIya2VybmVsMTIy"),
    ("vector122signal122", "dmVjdG9yMTIyc2lnbmFsMTIy"),
    ("vector122packet122", "dmVjdG9yMTIycGFja2V0MTIy"),
    ("vector122router122", "dmVjdG9yMTIycm91dGVyMTIy"),
    ("processor122router122", "cHJvY2Vzc29yMTIycm91dGVyMTIy"),
    ("processor122cluster122", "cHJvY2Vzc29yMTIyY2x1c3RlcjEyMg"),
    ("processor122mirror122", "cHJvY2Vzc29yMTIybWlycm9yMTIy"),
    ("processor122filter122", "cHJvY2Vzc29yMTIyZmlsdGVyMTIy"),
    ("reasoning122filter122", "cmVhc29uaW5nMTIyZmlsdGVyMTIy"),
    ("reasoning122ranking122", "cmVhc29uaW5nMTIycmFua2luZzEyMg"),
    ("reasoning122encoding122", "cmVhc29uaW5nMTIyZW5jb2RpbmcxMjI"),
    ("reasoning122mapping122", "cmVhc29uaW5nMTIybWFwcGluZzEyMg"),
    ("machine122mapping122", "bWFjaGluZTEyMm1hcHBpbmcxMjI"),
    ("machine122record122", "bWFjaGluZTEyMnJlY29yZDEyMg"),
    ("machine122candle122", "bWFjaGluZTEyMmNhbmRsZTEyMg"),
    ("machine122thread122", "bWFjaGluZTEyMnRocmVhZDEyMg"),
    ("learning122thread122", "bGVhcm5pbmcxMjJ0aHJlYWQxMjI"),
    ("learning122kitten122", "bGVhcm5pbmcxMjJraXR0ZW4xMjI"),
    ("learning122sitting122", "bGVhcm5pbmcxMjJzaXR0aW5nMTIy"),
    ("learning122agent122", "bGVhcm5pbmcxMjJhZ2VudDEyMg"),
    ("model122agent122", "bW9kZWwxMjJhZ2VudDEyMg"),
    ("model122angle122", "bW9kZWwxMjJhbmdsZTEyMg"),
    ("model122universe122", "bW9kZWwxMjJ1bml2ZXJzZTEyMg"),
    ("model122memory122", "bW9kZWwxMjJtZW1vcnkxMjI"),
    ("token122memory122", "dG9rZW4xMjJtZW1vcnkxMjI"),
    ("token122stream122", "dG9rZW4xMjJzdHJlYW0xMjI"),
    ("token122context122", "dG9rZW4xMjJjb250ZXh0MTIy"),
    ("token122knowledge122", "dG9rZW4xMjJrbm93bGVkZ2UxMjI"),
    ("prompt122knowledge122", "cHJvbXB0MTIya25vd2xlZGdlMTIy"),
    ("prompt122vector122", "cHJvbXB0MTIydmVjdG9yMTIy"),
    ("prompt122processor122", "cHJvbXB0MTIycHJvY2Vzc29yMTIy"),
    ("prompt122reasoning122", "cHJvbXB0MTIycmVhc29uaW5nMTIy"),
    ("session122reasoning122", "c2Vzc2lvbjEyMnJlYXNvbmluZzEyMg"),
    ("session122machine122", "c2Vzc2lvbjEyMm1hY2hpbmUxMjI"),
    ("session122learning122", "c2Vzc2lvbjEyMmxlYXJuaW5nMTIy"),
    ("session122model122", "c2Vzc2lvbjEyMm1vZGVsMTIy"),
    ("library122model122", "bGlicmFyeTEyMm1vZGVsMTIy"),
    ("library122token122", "bGlicmFyeTEyMnRva2VuMTIy"),
    ("library122prompt122", "bGlicmFyeTEyMnByb21wdDEyMg"),
    ("library122session122", "bGlicmFyeTEyMnNlc3Npb24xMjI"),
    ("service122session122", "c2VydmljZTEyMnNlc3Npb24xMjI"),
    ("service122library122", "c2VydmljZTEyMmxpYnJhcnkxMjI"),
    ("service122service122", "c2VydmljZTEyMnNlcnZpY2UxMjI"),
    ("service122gateway122", "c2VydmljZTEyMmdhdGV3YXkxMjI"),
    ("gateway122gateway122", "Z2F0ZXdheTEyMmdhdGV3YXkxMjI"),
    ("gateway122storage122", "Z2F0ZXdheTEyMnN0b3JhZ2UxMjI"),
    ("gateway122network122", "Z2F0ZXdheTEyMm5ldHdvcmsxMjI"),
    ("gateway122latency122", "Z2F0ZXdheTEyMmxhdGVuY3kxMjI"),
    ("storage122latency122", "c3RvcmFnZTEyMmxhdGVuY3kxMjI"),
    ("storage122buffer122", "c3RvcmFnZTEyMmJ1ZmZlcjEyMg"),
    ("storage122queue122", "c3RvcmFnZTEyMnF1ZXVlMTIy"),
    ("storage122worker122", "c3RvcmFnZTEyMndvcmtlcjEyMg"),
    ("network122worker122", "bmV0d29yazEyMndvcmtlcjEyMg"),
    ("network122kernel122", "bmV0d29yazEyMmtlcm5lbDEyMg"),
    ("network122signal122", "bmV0d29yazEyMnNpZ25hbDEyMg"),
    ("network122packet122", "bmV0d29yazEyMnBhY2tldDEyMg"),
    ("latency122packet122", "bGF0ZW5jeTEyMnBhY2tldDEyMg"),
    ("latency122router122", "bGF0ZW5jeTEyMnJvdXRlcjEyMg"),
    ("latency122cluster122", "bGF0ZW5jeTEyMmNsdXN0ZXIxMjI"),
    ("latency122mirror122", "bGF0ZW5jeTEyMm1pcnJvcjEyMg"),
    ("buffer122mirror122", "YnVmZmVyMTIybWlycm9yMTIy"),
    ("buffer122filter122", "YnVmZmVyMTIyZmlsdGVyMTIy"),
    ("buffer122ranking122", "YnVmZmVyMTIycmFua2luZzEyMg"),
    ("buffer122encoding122", "YnVmZmVyMTIyZW5jb2RpbmcxMjI"),
    ("queue122encoding122", "cXVldWUxMjJlbmNvZGluZzEyMg"),
    ("queue122mapping122", "cXVldWUxMjJtYXBwaW5nMTIy"),
    ("queue122record122", "cXVldWUxMjJyZWNvcmQxMjI"),
    ("queue122candle122", "cXVldWUxMjJjYW5kbGUxMjI"),
    ("worker122candle122", "d29ya2VyMTIyY2FuZGxlMTIy"),
    ("worker122thread122", "d29ya2VyMTIydGhyZWFkMTIy"),
    ("worker122kitten122", "d29ya2VyMTIya2l0dGVuMTIy"),
    ("worker122sitting122", "d29ya2VyMTIyc2l0dGluZzEyMg"),
    ("kernel122sitting122", "a2VybmVsMTIyc2l0dGluZzEyMg"),
    ("kernel122agent122", "a2VybmVsMTIyYWdlbnQxMjI"),
    ("kernel122angle122", "a2VybmVsMTIyYW5nbGUxMjI"),
    ("kernel122universe122", "a2VybmVsMTIydW5pdmVyc2UxMjI"),
    ("signal122universe122", "c2lnbmFsMTIydW5pdmVyc2UxMjI"),
    ("signal122memory122", "c2lnbmFsMTIybWVtb3J5MTIy"),
    ("signal122stream122", "c2lnbmFsMTIyc3RyZWFtMTIy"),
    ("signal122context122", "c2lnbmFsMTIyY29udGV4dDEyMg"),
    ("packet122context122", "cGFja2V0MTIyY29udGV4dDEyMg"),
    ("packet122knowledge122", "cGFja2V0MTIya25vd2xlZGdlMTIy"),
    ("packet122vector122", "cGFja2V0MTIydmVjdG9yMTIy"),
    ("packet122processor122", "cGFja2V0MTIycHJvY2Vzc29yMTIy"),
    ("router122processor122", "cm91dGVyMTIycHJvY2Vzc29yMTIy"),
    ("router122reasoning122", "cm91dGVyMTIycmVhc29uaW5nMTIy"),
    ("router122machine122", "cm91dGVyMTIybWFjaGluZTEyMg"),
    ("router122learning122", "cm91dGVyMTIybGVhcm5pbmcxMjI"),
    ("cluster122learning122", "Y2x1c3RlcjEyMmxlYXJuaW5nMTIy"),
    ("cluster122model122", "Y2x1c3RlcjEyMm1vZGVsMTIy"),
    ("cluster122token122", "Y2x1c3RlcjEyMnRva2VuMTIy"),
    ("cluster122prompt122", "Y2x1c3RlcjEyMnByb21wdDEyMg"),
    ("mirror122prompt122", "bWlycm9yMTIycHJvbXB0MTIy"),
    ("mirror122session122", "bWlycm9yMTIyc2Vzc2lvbjEyMg"),
    ("mirror122library122", "bWlycm9yMTIybGlicmFyeTEyMg"),
    ("mirror122service122", "bWlycm9yMTIyc2VydmljZTEyMg"),
    ("filter122service122", "ZmlsdGVyMTIyc2VydmljZTEyMg"),
    ("filter122gateway122", "ZmlsdGVyMTIyZ2F0ZXdheTEyMg"),
    ("filter122storage122", "ZmlsdGVyMTIyc3RvcmFnZTEyMg"),
    ("filter122network122", "ZmlsdGVyMTIybmV0d29yazEyMg"),
    ("ranking122network122", "cmFua2luZzEyMm5ldHdvcmsxMjI"),
    ("ranking122latency122", "cmFua2luZzEyMmxhdGVuY3kxMjI"),
    ("ranking122buffer122", "cmFua2luZzEyMmJ1ZmZlcjEyMg"),
    ("ranking122queue122", "cmFua2luZzEyMnF1ZXVlMTIy"),
    ("encoding122queue122", "ZW5jb2RpbmcxMjJxdWV1ZTEyMg"),
    ("encoding122worker122", "ZW5jb2RpbmcxMjJ3b3JrZXIxMjI"),
    ("encoding122kernel122", "ZW5jb2RpbmcxMjJrZXJuZWwxMjI"),
    ("encoding122signal122", "ZW5jb2RpbmcxMjJzaWduYWwxMjI"),
    ("mapping122signal122", "bWFwcGluZzEyMnNpZ25hbDEyMg"),
    ("mapping122packet122", "bWFwcGluZzEyMnBhY2tldDEyMg"),
    ("mapping122router122", "bWFwcGluZzEyMnJvdXRlcjEyMg"),
    ("mapping122cluster122", "bWFwcGluZzEyMmNsdXN0ZXIxMjI"),
    ("record122cluster122", "cmVjb3JkMTIyY2x1c3RlcjEyMg"),
    ("record122mirror122", "cmVjb3JkMTIybWlycm9yMTIy"),
    ("record122filter122", "cmVjb3JkMTIyZmlsdGVyMTIy"),
    ("record122ranking122", "cmVjb3JkMTIycmFua2luZzEyMg"),
    ("candle122ranking122", "Y2FuZGxlMTIycmFua2luZzEyMg"),
    ("candle122encoding122", "Y2FuZGxlMTIyZW5jb2RpbmcxMjI"),
    ("candle122mapping122", "Y2FuZGxlMTIybWFwcGluZzEyMg"),
    ("candle122record122", "Y2FuZGxlMTIycmVjb3JkMTIy"),
    ("thread122record122", "dGhyZWFkMTIycmVjb3JkMTIy"),
    ("thread122candle122", "dGhyZWFkMTIyY2FuZGxlMTIy"),
    ("thread122thread122", "dGhyZWFkMTIydGhyZWFkMTIy"),
    ("thread122kitten122", "dGhyZWFkMTIya2l0dGVuMTIy"),
    (
        "round 122: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTIyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 122: agentuniverse is a framework for multi agents",
        "cm91bmQgMTIyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 122: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTIyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 122: the processor reads the record then stops",
        "cm91bmQgMTIyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 122: a worker pulls the next task from the queue",
        "cm91bmQgMTIyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 122: signals travel through the network layer",
        "cm91bmQgMTIyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 122: the gateway routes each request by policy",
        "cm91bmQgMTIyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 122: memory grows until the buffer is full",
        "cm91bmQgMTIyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 122: the cluster mirrors every packet twice",
        "cm91bmQgMTIyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 122: ranking uses tokens learned from the corpus",
        "cm91bmQgMTIyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 122: a long session ends when the candle dies",
        "cm91bmQgMTIyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 122: encode the prompt then map the result",
        "cm91bmQgMTIyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 122: the kernel wakes the worker at dawn",
        "cm91bmQgMTIyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 122: service latency drops after the patch",
        "cm91bmQgMTIyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 122: the library caches every vector it sees",
        "cm91bmQgMTIyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 122: agents argue then the debate resolves",
        "cm91bmQgMTIyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 122: the filter keeps only strong matches",
        "cm91bmQgMTIyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 122: the model answers with a short reply",
        "cm91bmQgMTIyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 122: the recorder stores the reasoning trace",
        "cm91bmQgMTIyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 122: the angel watches the processor run",
        "cm91bmQgMTIyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 122: angle of the vector decides the match",
        "cm91bmQgMTIyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 122: the candle burns twice as long at night",
        "cm91bmQgMTIyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 122: a mirror of the universe in one line",
        "cm91bmQgMTIyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 122: the queue drains before the storm", "cm91bmQgMTIyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
    ("", ""),
    ("a", "YQ"),
    ("ab", "YWI"),
    ("abc", "YWJj"),
    (
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "YWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFh",
    ),
    ("!!!", "ISEh"),
    ("a-b_c", "YS1iX2M"),
    ("2026-10-19", "MjAyNi0xMC0xOQ"),
    ("a*b?c", "YSpiP2M"),
]

_EXPECTED_COUNT = 193

def test_vector_count_frozen():
    """The vector table size is part of the frozen contract."""
    assert len(_CASES) == _EXPECTED_COUNT

def test_vectors_000():
    """Known-answer vectors 0..119."""
    for case, expected in _CASES[0:120]:
        assert _ref_b64_url(case) == expected

def test_vectors_120():
    """Known-answer vectors 120..192."""
    for case, expected in _CASES[120:193]:
        assert _ref_b64_url(case) == expected

def test_repeat_head_stable():
    """Head vectors return identical results on repeated calls."""
    for case, expected in _CASES[:64]:
        assert _ref_b64_url(case) == expected
        assert _ref_b64_url(case) == expected

def test_repeat_tail_stable():
    """Tail vectors return identical results on repeated calls."""
    for case, expected in _CASES[-64:]:
        assert _ref_b64_url(case) == expected
        assert _ref_b64_url(case) == expected
