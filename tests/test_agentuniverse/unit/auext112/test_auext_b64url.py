"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten112kitten112", "a2l0dGVuMTEya2l0dGVuMTEy"),
    ("kitten112sitting112", "a2l0dGVuMTEyc2l0dGluZzExMg"),
    ("kitten112agent112", "a2l0dGVuMTEyYWdlbnQxMTI"),
    ("kitten112angle112", "a2l0dGVuMTEyYW5nbGUxMTI"),
    ("sitting112angle112", "c2l0dGluZzExMmFuZ2xlMTEy"),
    ("sitting112universe112", "c2l0dGluZzExMnVuaXZlcnNlMTEy"),
    ("sitting112memory112", "c2l0dGluZzExMm1lbW9yeTExMg"),
    ("sitting112stream112", "c2l0dGluZzExMnN0cmVhbTExMg"),
    ("agent112stream112", "YWdlbnQxMTJzdHJlYW0xMTI"),
    ("agent112context112", "YWdlbnQxMTJjb250ZXh0MTEy"),
    ("agent112knowledge112", "YWdlbnQxMTJrbm93bGVkZ2UxMTI"),
    ("agent112vector112", "YWdlbnQxMTJ2ZWN0b3IxMTI"),
    ("angle112vector112", "YW5nbGUxMTJ2ZWN0b3IxMTI"),
    ("angle112processor112", "YW5nbGUxMTJwcm9jZXNzb3IxMTI"),
    ("angle112reasoning112", "YW5nbGUxMTJyZWFzb25pbmcxMTI"),
    ("angle112machine112", "YW5nbGUxMTJtYWNoaW5lMTEy"),
    ("universe112machine112", "dW5pdmVyc2UxMTJtYWNoaW5lMTEy"),
    ("universe112learning112", "dW5pdmVyc2UxMTJsZWFybmluZzExMg"),
    ("universe112model112", "dW5pdmVyc2UxMTJtb2RlbDExMg"),
    ("universe112token112", "dW5pdmVyc2UxMTJ0b2tlbjExMg"),
    ("memory112token112", "bWVtb3J5MTEydG9rZW4xMTI"),
    ("memory112prompt112", "bWVtb3J5MTEycHJvbXB0MTEy"),
    ("memory112session112", "bWVtb3J5MTEyc2Vzc2lvbjExMg"),
    ("memory112library112", "bWVtb3J5MTEybGlicmFyeTExMg"),
    ("stream112library112", "c3RyZWFtMTEybGlicmFyeTExMg"),
    ("stream112service112", "c3RyZWFtMTEyc2VydmljZTExMg"),
    ("stream112gateway112", "c3RyZWFtMTEyZ2F0ZXdheTExMg"),
    ("stream112storage112", "c3RyZWFtMTEyc3RvcmFnZTExMg"),
    ("context112storage112", "Y29udGV4dDExMnN0b3JhZ2UxMTI"),
    ("context112network112", "Y29udGV4dDExMm5ldHdvcmsxMTI"),
    ("context112latency112", "Y29udGV4dDExMmxhdGVuY3kxMTI"),
    ("context112buffer112", "Y29udGV4dDExMmJ1ZmZlcjExMg"),
    ("knowledge112buffer112", "a25vd2xlZGdlMTEyYnVmZmVyMTEy"),
    ("knowledge112queue112", "a25vd2xlZGdlMTEycXVldWUxMTI"),
    ("knowledge112worker112", "a25vd2xlZGdlMTEyd29ya2VyMTEy"),
    ("knowledge112kernel112", "a25vd2xlZGdlMTEya2VybmVsMTEy"),
    ("vector112kernel112", "dmVjdG9yMTEya2VybmVsMTEy"),
    ("vector112signal112", "dmVjdG9yMTEyc2lnbmFsMTEy"),
    ("vector112packet112", "dmVjdG9yMTEycGFja2V0MTEy"),
    ("vector112router112", "dmVjdG9yMTEycm91dGVyMTEy"),
    ("processor112router112", "cHJvY2Vzc29yMTEycm91dGVyMTEy"),
    ("processor112cluster112", "cHJvY2Vzc29yMTEyY2x1c3RlcjExMg"),
    ("processor112mirror112", "cHJvY2Vzc29yMTEybWlycm9yMTEy"),
    ("processor112filter112", "cHJvY2Vzc29yMTEyZmlsdGVyMTEy"),
    ("reasoning112filter112", "cmVhc29uaW5nMTEyZmlsdGVyMTEy"),
    ("reasoning112ranking112", "cmVhc29uaW5nMTEycmFua2luZzExMg"),
    ("reasoning112encoding112", "cmVhc29uaW5nMTEyZW5jb2RpbmcxMTI"),
    ("reasoning112mapping112", "cmVhc29uaW5nMTEybWFwcGluZzExMg"),
    ("machine112mapping112", "bWFjaGluZTExMm1hcHBpbmcxMTI"),
    ("machine112record112", "bWFjaGluZTExMnJlY29yZDExMg"),
    ("machine112candle112", "bWFjaGluZTExMmNhbmRsZTExMg"),
    ("machine112thread112", "bWFjaGluZTExMnRocmVhZDExMg"),
    ("learning112thread112", "bGVhcm5pbmcxMTJ0aHJlYWQxMTI"),
    ("learning112kitten112", "bGVhcm5pbmcxMTJraXR0ZW4xMTI"),
    ("learning112sitting112", "bGVhcm5pbmcxMTJzaXR0aW5nMTEy"),
    ("learning112agent112", "bGVhcm5pbmcxMTJhZ2VudDExMg"),
    ("model112agent112", "bW9kZWwxMTJhZ2VudDExMg"),
    ("model112angle112", "bW9kZWwxMTJhbmdsZTExMg"),
    ("model112universe112", "bW9kZWwxMTJ1bml2ZXJzZTExMg"),
    ("model112memory112", "bW9kZWwxMTJtZW1vcnkxMTI"),
    ("token112memory112", "dG9rZW4xMTJtZW1vcnkxMTI"),
    ("token112stream112", "dG9rZW4xMTJzdHJlYW0xMTI"),
    ("token112context112", "dG9rZW4xMTJjb250ZXh0MTEy"),
    ("token112knowledge112", "dG9rZW4xMTJrbm93bGVkZ2UxMTI"),
    ("prompt112knowledge112", "cHJvbXB0MTEya25vd2xlZGdlMTEy"),
    ("prompt112vector112", "cHJvbXB0MTEydmVjdG9yMTEy"),
    ("prompt112processor112", "cHJvbXB0MTEycHJvY2Vzc29yMTEy"),
    ("prompt112reasoning112", "cHJvbXB0MTEycmVhc29uaW5nMTEy"),
    ("session112reasoning112", "c2Vzc2lvbjExMnJlYXNvbmluZzExMg"),
    ("session112machine112", "c2Vzc2lvbjExMm1hY2hpbmUxMTI"),
    ("session112learning112", "c2Vzc2lvbjExMmxlYXJuaW5nMTEy"),
    ("session112model112", "c2Vzc2lvbjExMm1vZGVsMTEy"),
    ("library112model112", "bGlicmFyeTExMm1vZGVsMTEy"),
    ("library112token112", "bGlicmFyeTExMnRva2VuMTEy"),
    ("library112prompt112", "bGlicmFyeTExMnByb21wdDExMg"),
    ("library112session112", "bGlicmFyeTExMnNlc3Npb24xMTI"),
    ("service112session112", "c2VydmljZTExMnNlc3Npb24xMTI"),
    ("service112library112", "c2VydmljZTExMmxpYnJhcnkxMTI"),
    ("service112service112", "c2VydmljZTExMnNlcnZpY2UxMTI"),
    ("service112gateway112", "c2VydmljZTExMmdhdGV3YXkxMTI"),
    ("gateway112gateway112", "Z2F0ZXdheTExMmdhdGV3YXkxMTI"),
    ("gateway112storage112", "Z2F0ZXdheTExMnN0b3JhZ2UxMTI"),
    ("gateway112network112", "Z2F0ZXdheTExMm5ldHdvcmsxMTI"),
    ("gateway112latency112", "Z2F0ZXdheTExMmxhdGVuY3kxMTI"),
    ("storage112latency112", "c3RvcmFnZTExMmxhdGVuY3kxMTI"),
    ("storage112buffer112", "c3RvcmFnZTExMmJ1ZmZlcjExMg"),
    ("storage112queue112", "c3RvcmFnZTExMnF1ZXVlMTEy"),
    ("storage112worker112", "c3RvcmFnZTExMndvcmtlcjExMg"),
    ("network112worker112", "bmV0d29yazExMndvcmtlcjExMg"),
    ("network112kernel112", "bmV0d29yazExMmtlcm5lbDExMg"),
    ("network112signal112", "bmV0d29yazExMnNpZ25hbDExMg"),
    ("network112packet112", "bmV0d29yazExMnBhY2tldDExMg"),
    ("latency112packet112", "bGF0ZW5jeTExMnBhY2tldDExMg"),
    ("latency112router112", "bGF0ZW5jeTExMnJvdXRlcjExMg"),
    ("latency112cluster112", "bGF0ZW5jeTExMmNsdXN0ZXIxMTI"),
    ("latency112mirror112", "bGF0ZW5jeTExMm1pcnJvcjExMg"),
    ("buffer112mirror112", "YnVmZmVyMTEybWlycm9yMTEy"),
    ("buffer112filter112", "YnVmZmVyMTEyZmlsdGVyMTEy"),
    ("buffer112ranking112", "YnVmZmVyMTEycmFua2luZzExMg"),
    ("buffer112encoding112", "YnVmZmVyMTEyZW5jb2RpbmcxMTI"),
    ("queue112encoding112", "cXVldWUxMTJlbmNvZGluZzExMg"),
    ("queue112mapping112", "cXVldWUxMTJtYXBwaW5nMTEy"),
    ("queue112record112", "cXVldWUxMTJyZWNvcmQxMTI"),
    ("queue112candle112", "cXVldWUxMTJjYW5kbGUxMTI"),
    ("worker112candle112", "d29ya2VyMTEyY2FuZGxlMTEy"),
    ("worker112thread112", "d29ya2VyMTEydGhyZWFkMTEy"),
    ("worker112kitten112", "d29ya2VyMTEya2l0dGVuMTEy"),
    ("worker112sitting112", "d29ya2VyMTEyc2l0dGluZzExMg"),
    ("kernel112sitting112", "a2VybmVsMTEyc2l0dGluZzExMg"),
    ("kernel112agent112", "a2VybmVsMTEyYWdlbnQxMTI"),
    ("kernel112angle112", "a2VybmVsMTEyYW5nbGUxMTI"),
    ("kernel112universe112", "a2VybmVsMTEydW5pdmVyc2UxMTI"),
    ("signal112universe112", "c2lnbmFsMTEydW5pdmVyc2UxMTI"),
    ("signal112memory112", "c2lnbmFsMTEybWVtb3J5MTEy"),
    ("signal112stream112", "c2lnbmFsMTEyc3RyZWFtMTEy"),
    ("signal112context112", "c2lnbmFsMTEyY29udGV4dDExMg"),
    ("packet112context112", "cGFja2V0MTEyY29udGV4dDExMg"),
    ("packet112knowledge112", "cGFja2V0MTEya25vd2xlZGdlMTEy"),
    ("packet112vector112", "cGFja2V0MTEydmVjdG9yMTEy"),
    ("packet112processor112", "cGFja2V0MTEycHJvY2Vzc29yMTEy"),
    ("router112processor112", "cm91dGVyMTEycHJvY2Vzc29yMTEy"),
    ("router112reasoning112", "cm91dGVyMTEycmVhc29uaW5nMTEy"),
    ("router112machine112", "cm91dGVyMTEybWFjaGluZTExMg"),
    ("router112learning112", "cm91dGVyMTEybGVhcm5pbmcxMTI"),
    ("cluster112learning112", "Y2x1c3RlcjExMmxlYXJuaW5nMTEy"),
    ("cluster112model112", "Y2x1c3RlcjExMm1vZGVsMTEy"),
    ("cluster112token112", "Y2x1c3RlcjExMnRva2VuMTEy"),
    ("cluster112prompt112", "Y2x1c3RlcjExMnByb21wdDExMg"),
    ("mirror112prompt112", "bWlycm9yMTEycHJvbXB0MTEy"),
    ("mirror112session112", "bWlycm9yMTEyc2Vzc2lvbjExMg"),
    ("mirror112library112", "bWlycm9yMTEybGlicmFyeTExMg"),
    ("mirror112service112", "bWlycm9yMTEyc2VydmljZTExMg"),
    ("filter112service112", "ZmlsdGVyMTEyc2VydmljZTExMg"),
    ("filter112gateway112", "ZmlsdGVyMTEyZ2F0ZXdheTExMg"),
    ("filter112storage112", "ZmlsdGVyMTEyc3RvcmFnZTExMg"),
    ("filter112network112", "ZmlsdGVyMTEybmV0d29yazExMg"),
    ("ranking112network112", "cmFua2luZzExMm5ldHdvcmsxMTI"),
    ("ranking112latency112", "cmFua2luZzExMmxhdGVuY3kxMTI"),
    ("ranking112buffer112", "cmFua2luZzExMmJ1ZmZlcjExMg"),
    ("ranking112queue112", "cmFua2luZzExMnF1ZXVlMTEy"),
    ("encoding112queue112", "ZW5jb2RpbmcxMTJxdWV1ZTExMg"),
    ("encoding112worker112", "ZW5jb2RpbmcxMTJ3b3JrZXIxMTI"),
    ("encoding112kernel112", "ZW5jb2RpbmcxMTJrZXJuZWwxMTI"),
    ("encoding112signal112", "ZW5jb2RpbmcxMTJzaWduYWwxMTI"),
    ("mapping112signal112", "bWFwcGluZzExMnNpZ25hbDExMg"),
    ("mapping112packet112", "bWFwcGluZzExMnBhY2tldDExMg"),
    ("mapping112router112", "bWFwcGluZzExMnJvdXRlcjExMg"),
    ("mapping112cluster112", "bWFwcGluZzExMmNsdXN0ZXIxMTI"),
    ("record112cluster112", "cmVjb3JkMTEyY2x1c3RlcjExMg"),
    ("record112mirror112", "cmVjb3JkMTEybWlycm9yMTEy"),
    ("record112filter112", "cmVjb3JkMTEyZmlsdGVyMTEy"),
    ("record112ranking112", "cmVjb3JkMTEycmFua2luZzExMg"),
    ("candle112ranking112", "Y2FuZGxlMTEycmFua2luZzExMg"),
    ("candle112encoding112", "Y2FuZGxlMTEyZW5jb2RpbmcxMTI"),
    ("candle112mapping112", "Y2FuZGxlMTEybWFwcGluZzExMg"),
    ("candle112record112", "Y2FuZGxlMTEycmVjb3JkMTEy"),
    ("thread112record112", "dGhyZWFkMTEycmVjb3JkMTEy"),
    ("thread112candle112", "dGhyZWFkMTEyY2FuZGxlMTEy"),
    ("thread112thread112", "dGhyZWFkMTEydGhyZWFkMTEy"),
    ("thread112kitten112", "dGhyZWFkMTEya2l0dGVuMTEy"),
    (
        "round 112: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTEyOiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 112: agentuniverse is a framework for multi agents",
        "cm91bmQgMTEyOiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 112: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTEyOiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 112: the processor reads the record then stops",
        "cm91bmQgMTEyOiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 112: a worker pulls the next task from the queue",
        "cm91bmQgMTEyOiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 112: signals travel through the network layer",
        "cm91bmQgMTEyOiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 112: the gateway routes each request by policy",
        "cm91bmQgMTEyOiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 112: memory grows until the buffer is full",
        "cm91bmQgMTEyOiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 112: the cluster mirrors every packet twice",
        "cm91bmQgMTEyOiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 112: ranking uses tokens learned from the corpus",
        "cm91bmQgMTEyOiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 112: a long session ends when the candle dies",
        "cm91bmQgMTEyOiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 112: encode the prompt then map the result",
        "cm91bmQgMTEyOiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 112: the kernel wakes the worker at dawn",
        "cm91bmQgMTEyOiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 112: service latency drops after the patch",
        "cm91bmQgMTEyOiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 112: the library caches every vector it sees",
        "cm91bmQgMTEyOiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 112: agents argue then the debate resolves",
        "cm91bmQgMTEyOiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 112: the filter keeps only strong matches",
        "cm91bmQgMTEyOiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 112: the model answers with a short reply",
        "cm91bmQgMTEyOiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 112: the recorder stores the reasoning trace",
        "cm91bmQgMTEyOiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 112: the angel watches the processor run",
        "cm91bmQgMTEyOiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 112: angle of the vector decides the match",
        "cm91bmQgMTEyOiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 112: the candle burns twice as long at night",
        "cm91bmQgMTEyOiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 112: a mirror of the universe in one line",
        "cm91bmQgMTEyOiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 112: the queue drains before the storm", "cm91bmQgMTEyOiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
