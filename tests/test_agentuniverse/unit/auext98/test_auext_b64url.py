"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten98kitten98", "a2l0dGVuOThraXR0ZW45OA"),
    ("kitten98sitting98", "a2l0dGVuOThzaXR0aW5nOTg"),
    ("kitten98agent98", "a2l0dGVuOThhZ2VudDk4"),
    ("kitten98angle98", "a2l0dGVuOThhbmdsZTk4"),
    ("sitting98angle98", "c2l0dGluZzk4YW5nbGU5OA"),
    ("sitting98universe98", "c2l0dGluZzk4dW5pdmVyc2U5OA"),
    ("sitting98memory98", "c2l0dGluZzk4bWVtb3J5OTg"),
    ("sitting98stream98", "c2l0dGluZzk4c3RyZWFtOTg"),
    ("agent98stream98", "YWdlbnQ5OHN0cmVhbTk4"),
    ("agent98context98", "YWdlbnQ5OGNvbnRleHQ5OA"),
    ("agent98knowledge98", "YWdlbnQ5OGtub3dsZWRnZTk4"),
    ("agent98vector98", "YWdlbnQ5OHZlY3Rvcjk4"),
    ("angle98vector98", "YW5nbGU5OHZlY3Rvcjk4"),
    ("angle98processor98", "YW5nbGU5OHByb2Nlc3Nvcjk4"),
    ("angle98reasoning98", "YW5nbGU5OHJlYXNvbmluZzk4"),
    ("angle98machine98", "YW5nbGU5OG1hY2hpbmU5OA"),
    ("universe98machine98", "dW5pdmVyc2U5OG1hY2hpbmU5OA"),
    ("universe98learning98", "dW5pdmVyc2U5OGxlYXJuaW5nOTg"),
    ("universe98model98", "dW5pdmVyc2U5OG1vZGVsOTg"),
    ("universe98token98", "dW5pdmVyc2U5OHRva2VuOTg"),
    ("memory98token98", "bWVtb3J5OTh0b2tlbjk4"),
    ("memory98prompt98", "bWVtb3J5OThwcm9tcHQ5OA"),
    ("memory98session98", "bWVtb3J5OThzZXNzaW9uOTg"),
    ("memory98library98", "bWVtb3J5OThsaWJyYXJ5OTg"),
    ("stream98library98", "c3RyZWFtOThsaWJyYXJ5OTg"),
    ("stream98service98", "c3RyZWFtOThzZXJ2aWNlOTg"),
    ("stream98gateway98", "c3RyZWFtOThnYXRld2F5OTg"),
    ("stream98storage98", "c3RyZWFtOThzdG9yYWdlOTg"),
    ("context98storage98", "Y29udGV4dDk4c3RvcmFnZTk4"),
    ("context98network98", "Y29udGV4dDk4bmV0d29yazk4"),
    ("context98latency98", "Y29udGV4dDk4bGF0ZW5jeTk4"),
    ("context98buffer98", "Y29udGV4dDk4YnVmZmVyOTg"),
    ("knowledge98buffer98", "a25vd2xlZGdlOThidWZmZXI5OA"),
    ("knowledge98queue98", "a25vd2xlZGdlOThxdWV1ZTk4"),
    ("knowledge98worker98", "a25vd2xlZGdlOTh3b3JrZXI5OA"),
    ("knowledge98kernel98", "a25vd2xlZGdlOThrZXJuZWw5OA"),
    ("vector98kernel98", "dmVjdG9yOThrZXJuZWw5OA"),
    ("vector98signal98", "dmVjdG9yOThzaWduYWw5OA"),
    ("vector98packet98", "dmVjdG9yOThwYWNrZXQ5OA"),
    ("vector98router98", "dmVjdG9yOThyb3V0ZXI5OA"),
    ("processor98router98", "cHJvY2Vzc29yOThyb3V0ZXI5OA"),
    ("processor98cluster98", "cHJvY2Vzc29yOThjbHVzdGVyOTg"),
    ("processor98mirror98", "cHJvY2Vzc29yOThtaXJyb3I5OA"),
    ("processor98filter98", "cHJvY2Vzc29yOThmaWx0ZXI5OA"),
    ("reasoning98filter98", "cmVhc29uaW5nOThmaWx0ZXI5OA"),
    ("reasoning98ranking98", "cmVhc29uaW5nOThyYW5raW5nOTg"),
    ("reasoning98encoding98", "cmVhc29uaW5nOThlbmNvZGluZzk4"),
    ("reasoning98mapping98", "cmVhc29uaW5nOThtYXBwaW5nOTg"),
    ("machine98mapping98", "bWFjaGluZTk4bWFwcGluZzk4"),
    ("machine98record98", "bWFjaGluZTk4cmVjb3JkOTg"),
    ("machine98candle98", "bWFjaGluZTk4Y2FuZGxlOTg"),
    ("machine98thread98", "bWFjaGluZTk4dGhyZWFkOTg"),
    ("learning98thread98", "bGVhcm5pbmc5OHRocmVhZDk4"),
    ("learning98kitten98", "bGVhcm5pbmc5OGtpdHRlbjk4"),
    ("learning98sitting98", "bGVhcm5pbmc5OHNpdHRpbmc5OA"),
    ("learning98agent98", "bGVhcm5pbmc5OGFnZW50OTg"),
    ("model98agent98", "bW9kZWw5OGFnZW50OTg"),
    ("model98angle98", "bW9kZWw5OGFuZ2xlOTg"),
    ("model98universe98", "bW9kZWw5OHVuaXZlcnNlOTg"),
    ("model98memory98", "bW9kZWw5OG1lbW9yeTk4"),
    ("token98memory98", "dG9rZW45OG1lbW9yeTk4"),
    ("token98stream98", "dG9rZW45OHN0cmVhbTk4"),
    ("token98context98", "dG9rZW45OGNvbnRleHQ5OA"),
    ("token98knowledge98", "dG9rZW45OGtub3dsZWRnZTk4"),
    ("prompt98knowledge98", "cHJvbXB0OThrbm93bGVkZ2U5OA"),
    ("prompt98vector98", "cHJvbXB0OTh2ZWN0b3I5OA"),
    ("prompt98processor98", "cHJvbXB0OThwcm9jZXNzb3I5OA"),
    ("prompt98reasoning98", "cHJvbXB0OThyZWFzb25pbmc5OA"),
    ("session98reasoning98", "c2Vzc2lvbjk4cmVhc29uaW5nOTg"),
    ("session98machine98", "c2Vzc2lvbjk4bWFjaGluZTk4"),
    ("session98learning98", "c2Vzc2lvbjk4bGVhcm5pbmc5OA"),
    ("session98model98", "c2Vzc2lvbjk4bW9kZWw5OA"),
    ("library98model98", "bGlicmFyeTk4bW9kZWw5OA"),
    ("library98token98", "bGlicmFyeTk4dG9rZW45OA"),
    ("library98prompt98", "bGlicmFyeTk4cHJvbXB0OTg"),
    ("library98session98", "bGlicmFyeTk4c2Vzc2lvbjk4"),
    ("service98session98", "c2VydmljZTk4c2Vzc2lvbjk4"),
    ("service98library98", "c2VydmljZTk4bGlicmFyeTk4"),
    ("service98service98", "c2VydmljZTk4c2VydmljZTk4"),
    ("service98gateway98", "c2VydmljZTk4Z2F0ZXdheTk4"),
    ("gateway98gateway98", "Z2F0ZXdheTk4Z2F0ZXdheTk4"),
    ("gateway98storage98", "Z2F0ZXdheTk4c3RvcmFnZTk4"),
    ("gateway98network98", "Z2F0ZXdheTk4bmV0d29yazk4"),
    ("gateway98latency98", "Z2F0ZXdheTk4bGF0ZW5jeTk4"),
    ("storage98latency98", "c3RvcmFnZTk4bGF0ZW5jeTk4"),
    ("storage98buffer98", "c3RvcmFnZTk4YnVmZmVyOTg"),
    ("storage98queue98", "c3RvcmFnZTk4cXVldWU5OA"),
    ("storage98worker98", "c3RvcmFnZTk4d29ya2VyOTg"),
    ("network98worker98", "bmV0d29yazk4d29ya2VyOTg"),
    ("network98kernel98", "bmV0d29yazk4a2VybmVsOTg"),
    ("network98signal98", "bmV0d29yazk4c2lnbmFsOTg"),
    ("network98packet98", "bmV0d29yazk4cGFja2V0OTg"),
    ("latency98packet98", "bGF0ZW5jeTk4cGFja2V0OTg"),
    ("latency98router98", "bGF0ZW5jeTk4cm91dGVyOTg"),
    ("latency98cluster98", "bGF0ZW5jeTk4Y2x1c3Rlcjk4"),
    ("latency98mirror98", "bGF0ZW5jeTk4bWlycm9yOTg"),
    ("buffer98mirror98", "YnVmZmVyOThtaXJyb3I5OA"),
    ("buffer98filter98", "YnVmZmVyOThmaWx0ZXI5OA"),
    ("buffer98ranking98", "YnVmZmVyOThyYW5raW5nOTg"),
    ("buffer98encoding98", "YnVmZmVyOThlbmNvZGluZzk4"),
    ("queue98encoding98", "cXVldWU5OGVuY29kaW5nOTg"),
    ("queue98mapping98", "cXVldWU5OG1hcHBpbmc5OA"),
    ("queue98record98", "cXVldWU5OHJlY29yZDk4"),
    ("queue98candle98", "cXVldWU5OGNhbmRsZTk4"),
    ("worker98candle98", "d29ya2VyOThjYW5kbGU5OA"),
    ("worker98thread98", "d29ya2VyOTh0aHJlYWQ5OA"),
    ("worker98kitten98", "d29ya2VyOThraXR0ZW45OA"),
    ("worker98sitting98", "d29ya2VyOThzaXR0aW5nOTg"),
    ("kernel98sitting98", "a2VybmVsOThzaXR0aW5nOTg"),
    ("kernel98agent98", "a2VybmVsOThhZ2VudDk4"),
    ("kernel98angle98", "a2VybmVsOThhbmdsZTk4"),
    ("kernel98universe98", "a2VybmVsOTh1bml2ZXJzZTk4"),
    ("signal98universe98", "c2lnbmFsOTh1bml2ZXJzZTk4"),
    ("signal98memory98", "c2lnbmFsOThtZW1vcnk5OA"),
    ("signal98stream98", "c2lnbmFsOThzdHJlYW05OA"),
    ("signal98context98", "c2lnbmFsOThjb250ZXh0OTg"),
    ("packet98context98", "cGFja2V0OThjb250ZXh0OTg"),
    ("packet98knowledge98", "cGFja2V0OThrbm93bGVkZ2U5OA"),
    ("packet98vector98", "cGFja2V0OTh2ZWN0b3I5OA"),
    ("packet98processor98", "cGFja2V0OThwcm9jZXNzb3I5OA"),
    ("router98processor98", "cm91dGVyOThwcm9jZXNzb3I5OA"),
    ("router98reasoning98", "cm91dGVyOThyZWFzb25pbmc5OA"),
    ("router98machine98", "cm91dGVyOThtYWNoaW5lOTg"),
    ("router98learning98", "cm91dGVyOThsZWFybmluZzk4"),
    ("cluster98learning98", "Y2x1c3Rlcjk4bGVhcm5pbmc5OA"),
    ("cluster98model98", "Y2x1c3Rlcjk4bW9kZWw5OA"),
    ("cluster98token98", "Y2x1c3Rlcjk4dG9rZW45OA"),
    ("cluster98prompt98", "Y2x1c3Rlcjk4cHJvbXB0OTg"),
    ("mirror98prompt98", "bWlycm9yOThwcm9tcHQ5OA"),
    ("mirror98session98", "bWlycm9yOThzZXNzaW9uOTg"),
    ("mirror98library98", "bWlycm9yOThsaWJyYXJ5OTg"),
    ("mirror98service98", "bWlycm9yOThzZXJ2aWNlOTg"),
    ("filter98service98", "ZmlsdGVyOThzZXJ2aWNlOTg"),
    ("filter98gateway98", "ZmlsdGVyOThnYXRld2F5OTg"),
    ("filter98storage98", "ZmlsdGVyOThzdG9yYWdlOTg"),
    ("filter98network98", "ZmlsdGVyOThuZXR3b3JrOTg"),
    ("ranking98network98", "cmFua2luZzk4bmV0d29yazk4"),
    ("ranking98latency98", "cmFua2luZzk4bGF0ZW5jeTk4"),
    ("ranking98buffer98", "cmFua2luZzk4YnVmZmVyOTg"),
    ("ranking98queue98", "cmFua2luZzk4cXVldWU5OA"),
    ("encoding98queue98", "ZW5jb2Rpbmc5OHF1ZXVlOTg"),
    ("encoding98worker98", "ZW5jb2Rpbmc5OHdvcmtlcjk4"),
    ("encoding98kernel98", "ZW5jb2Rpbmc5OGtlcm5lbDk4"),
    ("encoding98signal98", "ZW5jb2Rpbmc5OHNpZ25hbDk4"),
    ("mapping98signal98", "bWFwcGluZzk4c2lnbmFsOTg"),
    ("mapping98packet98", "bWFwcGluZzk4cGFja2V0OTg"),
    ("mapping98router98", "bWFwcGluZzk4cm91dGVyOTg"),
    ("mapping98cluster98", "bWFwcGluZzk4Y2x1c3Rlcjk4"),
    ("record98cluster98", "cmVjb3JkOThjbHVzdGVyOTg"),
    ("record98mirror98", "cmVjb3JkOThtaXJyb3I5OA"),
    ("record98filter98", "cmVjb3JkOThmaWx0ZXI5OA"),
    ("record98ranking98", "cmVjb3JkOThyYW5raW5nOTg"),
    ("candle98ranking98", "Y2FuZGxlOThyYW5raW5nOTg"),
    ("candle98encoding98", "Y2FuZGxlOThlbmNvZGluZzk4"),
    ("candle98mapping98", "Y2FuZGxlOThtYXBwaW5nOTg"),
    ("candle98record98", "Y2FuZGxlOThyZWNvcmQ5OA"),
    ("thread98record98", "dGhyZWFkOThyZWNvcmQ5OA"),
    ("thread98candle98", "dGhyZWFkOThjYW5kbGU5OA"),
    ("thread98thread98", "dGhyZWFkOTh0aHJlYWQ5OA"),
    ("thread98kitten98", "dGhyZWFkOThraXR0ZW45OA"),
    (
        "round 98: the quick brown fox jumps over the lazy dog",
        "cm91bmQgOTg6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 98: agentuniverse is a framework for multi agents",
        "cm91bmQgOTg6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 98: knowledge stored as vectors enables retrieval",
        "cm91bmQgOTg6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 98: the processor reads the record then stops",
        "cm91bmQgOTg6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 98: a worker pulls the next task from the queue",
        "cm91bmQgOTg6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 98: signals travel through the network layer",
        "cm91bmQgOTg6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 98: the gateway routes each request by policy",
        "cm91bmQgOTg6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 98: memory grows until the buffer is full",
        "cm91bmQgOTg6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 98: the cluster mirrors every packet twice",
        "cm91bmQgOTg6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 98: ranking uses tokens learned from the corpus",
        "cm91bmQgOTg6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 98: a long session ends when the candle dies",
        "cm91bmQgOTg6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 98: encode the prompt then map the result",
        "cm91bmQgOTg6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 98: the kernel wakes the worker at dawn", "cm91bmQgOTg6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 98: service latency drops after the patch",
        "cm91bmQgOTg6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 98: the library caches every vector it sees",
        "cm91bmQgOTg6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 98: agents argue then the debate resolves",
        "cm91bmQgOTg6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 98: the filter keeps only strong matches",
        "cm91bmQgOTg6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 98: the model answers with a short reply",
        "cm91bmQgOTg6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 98: the recorder stores the reasoning trace",
        "cm91bmQgOTg6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 98: the angel watches the processor run", "cm91bmQgOTg6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 98: angle of the vector decides the match",
        "cm91bmQgOTg6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 98: the candle burns twice as long at night",
        "cm91bmQgOTg6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 98: a mirror of the universe in one line",
        "cm91bmQgOTg6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 98: the queue drains before the storm", "cm91bmQgOTg6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
