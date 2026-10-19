"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten95kitten95", "a2l0dGVuOTVraXR0ZW45NQ"),
    ("kitten95sitting95", "a2l0dGVuOTVzaXR0aW5nOTU"),
    ("kitten95agent95", "a2l0dGVuOTVhZ2VudDk1"),
    ("kitten95angle95", "a2l0dGVuOTVhbmdsZTk1"),
    ("sitting95angle95", "c2l0dGluZzk1YW5nbGU5NQ"),
    ("sitting95universe95", "c2l0dGluZzk1dW5pdmVyc2U5NQ"),
    ("sitting95memory95", "c2l0dGluZzk1bWVtb3J5OTU"),
    ("sitting95stream95", "c2l0dGluZzk1c3RyZWFtOTU"),
    ("agent95stream95", "YWdlbnQ5NXN0cmVhbTk1"),
    ("agent95context95", "YWdlbnQ5NWNvbnRleHQ5NQ"),
    ("agent95knowledge95", "YWdlbnQ5NWtub3dsZWRnZTk1"),
    ("agent95vector95", "YWdlbnQ5NXZlY3Rvcjk1"),
    ("angle95vector95", "YW5nbGU5NXZlY3Rvcjk1"),
    ("angle95processor95", "YW5nbGU5NXByb2Nlc3Nvcjk1"),
    ("angle95reasoning95", "YW5nbGU5NXJlYXNvbmluZzk1"),
    ("angle95machine95", "YW5nbGU5NW1hY2hpbmU5NQ"),
    ("universe95machine95", "dW5pdmVyc2U5NW1hY2hpbmU5NQ"),
    ("universe95learning95", "dW5pdmVyc2U5NWxlYXJuaW5nOTU"),
    ("universe95model95", "dW5pdmVyc2U5NW1vZGVsOTU"),
    ("universe95token95", "dW5pdmVyc2U5NXRva2VuOTU"),
    ("memory95token95", "bWVtb3J5OTV0b2tlbjk1"),
    ("memory95prompt95", "bWVtb3J5OTVwcm9tcHQ5NQ"),
    ("memory95session95", "bWVtb3J5OTVzZXNzaW9uOTU"),
    ("memory95library95", "bWVtb3J5OTVsaWJyYXJ5OTU"),
    ("stream95library95", "c3RyZWFtOTVsaWJyYXJ5OTU"),
    ("stream95service95", "c3RyZWFtOTVzZXJ2aWNlOTU"),
    ("stream95gateway95", "c3RyZWFtOTVnYXRld2F5OTU"),
    ("stream95storage95", "c3RyZWFtOTVzdG9yYWdlOTU"),
    ("context95storage95", "Y29udGV4dDk1c3RvcmFnZTk1"),
    ("context95network95", "Y29udGV4dDk1bmV0d29yazk1"),
    ("context95latency95", "Y29udGV4dDk1bGF0ZW5jeTk1"),
    ("context95buffer95", "Y29udGV4dDk1YnVmZmVyOTU"),
    ("knowledge95buffer95", "a25vd2xlZGdlOTVidWZmZXI5NQ"),
    ("knowledge95queue95", "a25vd2xlZGdlOTVxdWV1ZTk1"),
    ("knowledge95worker95", "a25vd2xlZGdlOTV3b3JrZXI5NQ"),
    ("knowledge95kernel95", "a25vd2xlZGdlOTVrZXJuZWw5NQ"),
    ("vector95kernel95", "dmVjdG9yOTVrZXJuZWw5NQ"),
    ("vector95signal95", "dmVjdG9yOTVzaWduYWw5NQ"),
    ("vector95packet95", "dmVjdG9yOTVwYWNrZXQ5NQ"),
    ("vector95router95", "dmVjdG9yOTVyb3V0ZXI5NQ"),
    ("processor95router95", "cHJvY2Vzc29yOTVyb3V0ZXI5NQ"),
    ("processor95cluster95", "cHJvY2Vzc29yOTVjbHVzdGVyOTU"),
    ("processor95mirror95", "cHJvY2Vzc29yOTVtaXJyb3I5NQ"),
    ("processor95filter95", "cHJvY2Vzc29yOTVmaWx0ZXI5NQ"),
    ("reasoning95filter95", "cmVhc29uaW5nOTVmaWx0ZXI5NQ"),
    ("reasoning95ranking95", "cmVhc29uaW5nOTVyYW5raW5nOTU"),
    ("reasoning95encoding95", "cmVhc29uaW5nOTVlbmNvZGluZzk1"),
    ("reasoning95mapping95", "cmVhc29uaW5nOTVtYXBwaW5nOTU"),
    ("machine95mapping95", "bWFjaGluZTk1bWFwcGluZzk1"),
    ("machine95record95", "bWFjaGluZTk1cmVjb3JkOTU"),
    ("machine95candle95", "bWFjaGluZTk1Y2FuZGxlOTU"),
    ("machine95thread95", "bWFjaGluZTk1dGhyZWFkOTU"),
    ("learning95thread95", "bGVhcm5pbmc5NXRocmVhZDk1"),
    ("learning95kitten95", "bGVhcm5pbmc5NWtpdHRlbjk1"),
    ("learning95sitting95", "bGVhcm5pbmc5NXNpdHRpbmc5NQ"),
    ("learning95agent95", "bGVhcm5pbmc5NWFnZW50OTU"),
    ("model95agent95", "bW9kZWw5NWFnZW50OTU"),
    ("model95angle95", "bW9kZWw5NWFuZ2xlOTU"),
    ("model95universe95", "bW9kZWw5NXVuaXZlcnNlOTU"),
    ("model95memory95", "bW9kZWw5NW1lbW9yeTk1"),
    ("token95memory95", "dG9rZW45NW1lbW9yeTk1"),
    ("token95stream95", "dG9rZW45NXN0cmVhbTk1"),
    ("token95context95", "dG9rZW45NWNvbnRleHQ5NQ"),
    ("token95knowledge95", "dG9rZW45NWtub3dsZWRnZTk1"),
    ("prompt95knowledge95", "cHJvbXB0OTVrbm93bGVkZ2U5NQ"),
    ("prompt95vector95", "cHJvbXB0OTV2ZWN0b3I5NQ"),
    ("prompt95processor95", "cHJvbXB0OTVwcm9jZXNzb3I5NQ"),
    ("prompt95reasoning95", "cHJvbXB0OTVyZWFzb25pbmc5NQ"),
    ("session95reasoning95", "c2Vzc2lvbjk1cmVhc29uaW5nOTU"),
    ("session95machine95", "c2Vzc2lvbjk1bWFjaGluZTk1"),
    ("session95learning95", "c2Vzc2lvbjk1bGVhcm5pbmc5NQ"),
    ("session95model95", "c2Vzc2lvbjk1bW9kZWw5NQ"),
    ("library95model95", "bGlicmFyeTk1bW9kZWw5NQ"),
    ("library95token95", "bGlicmFyeTk1dG9rZW45NQ"),
    ("library95prompt95", "bGlicmFyeTk1cHJvbXB0OTU"),
    ("library95session95", "bGlicmFyeTk1c2Vzc2lvbjk1"),
    ("service95session95", "c2VydmljZTk1c2Vzc2lvbjk1"),
    ("service95library95", "c2VydmljZTk1bGlicmFyeTk1"),
    ("service95service95", "c2VydmljZTk1c2VydmljZTk1"),
    ("service95gateway95", "c2VydmljZTk1Z2F0ZXdheTk1"),
    ("gateway95gateway95", "Z2F0ZXdheTk1Z2F0ZXdheTk1"),
    ("gateway95storage95", "Z2F0ZXdheTk1c3RvcmFnZTk1"),
    ("gateway95network95", "Z2F0ZXdheTk1bmV0d29yazk1"),
    ("gateway95latency95", "Z2F0ZXdheTk1bGF0ZW5jeTk1"),
    ("storage95latency95", "c3RvcmFnZTk1bGF0ZW5jeTk1"),
    ("storage95buffer95", "c3RvcmFnZTk1YnVmZmVyOTU"),
    ("storage95queue95", "c3RvcmFnZTk1cXVldWU5NQ"),
    ("storage95worker95", "c3RvcmFnZTk1d29ya2VyOTU"),
    ("network95worker95", "bmV0d29yazk1d29ya2VyOTU"),
    ("network95kernel95", "bmV0d29yazk1a2VybmVsOTU"),
    ("network95signal95", "bmV0d29yazk1c2lnbmFsOTU"),
    ("network95packet95", "bmV0d29yazk1cGFja2V0OTU"),
    ("latency95packet95", "bGF0ZW5jeTk1cGFja2V0OTU"),
    ("latency95router95", "bGF0ZW5jeTk1cm91dGVyOTU"),
    ("latency95cluster95", "bGF0ZW5jeTk1Y2x1c3Rlcjk1"),
    ("latency95mirror95", "bGF0ZW5jeTk1bWlycm9yOTU"),
    ("buffer95mirror95", "YnVmZmVyOTVtaXJyb3I5NQ"),
    ("buffer95filter95", "YnVmZmVyOTVmaWx0ZXI5NQ"),
    ("buffer95ranking95", "YnVmZmVyOTVyYW5raW5nOTU"),
    ("buffer95encoding95", "YnVmZmVyOTVlbmNvZGluZzk1"),
    ("queue95encoding95", "cXVldWU5NWVuY29kaW5nOTU"),
    ("queue95mapping95", "cXVldWU5NW1hcHBpbmc5NQ"),
    ("queue95record95", "cXVldWU5NXJlY29yZDk1"),
    ("queue95candle95", "cXVldWU5NWNhbmRsZTk1"),
    ("worker95candle95", "d29ya2VyOTVjYW5kbGU5NQ"),
    ("worker95thread95", "d29ya2VyOTV0aHJlYWQ5NQ"),
    ("worker95kitten95", "d29ya2VyOTVraXR0ZW45NQ"),
    ("worker95sitting95", "d29ya2VyOTVzaXR0aW5nOTU"),
    ("kernel95sitting95", "a2VybmVsOTVzaXR0aW5nOTU"),
    ("kernel95agent95", "a2VybmVsOTVhZ2VudDk1"),
    ("kernel95angle95", "a2VybmVsOTVhbmdsZTk1"),
    ("kernel95universe95", "a2VybmVsOTV1bml2ZXJzZTk1"),
    ("signal95universe95", "c2lnbmFsOTV1bml2ZXJzZTk1"),
    ("signal95memory95", "c2lnbmFsOTVtZW1vcnk5NQ"),
    ("signal95stream95", "c2lnbmFsOTVzdHJlYW05NQ"),
    ("signal95context95", "c2lnbmFsOTVjb250ZXh0OTU"),
    ("packet95context95", "cGFja2V0OTVjb250ZXh0OTU"),
    ("packet95knowledge95", "cGFja2V0OTVrbm93bGVkZ2U5NQ"),
    ("packet95vector95", "cGFja2V0OTV2ZWN0b3I5NQ"),
    ("packet95processor95", "cGFja2V0OTVwcm9jZXNzb3I5NQ"),
    ("router95processor95", "cm91dGVyOTVwcm9jZXNzb3I5NQ"),
    ("router95reasoning95", "cm91dGVyOTVyZWFzb25pbmc5NQ"),
    ("router95machine95", "cm91dGVyOTVtYWNoaW5lOTU"),
    ("router95learning95", "cm91dGVyOTVsZWFybmluZzk1"),
    ("cluster95learning95", "Y2x1c3Rlcjk1bGVhcm5pbmc5NQ"),
    ("cluster95model95", "Y2x1c3Rlcjk1bW9kZWw5NQ"),
    ("cluster95token95", "Y2x1c3Rlcjk1dG9rZW45NQ"),
    ("cluster95prompt95", "Y2x1c3Rlcjk1cHJvbXB0OTU"),
    ("mirror95prompt95", "bWlycm9yOTVwcm9tcHQ5NQ"),
    ("mirror95session95", "bWlycm9yOTVzZXNzaW9uOTU"),
    ("mirror95library95", "bWlycm9yOTVsaWJyYXJ5OTU"),
    ("mirror95service95", "bWlycm9yOTVzZXJ2aWNlOTU"),
    ("filter95service95", "ZmlsdGVyOTVzZXJ2aWNlOTU"),
    ("filter95gateway95", "ZmlsdGVyOTVnYXRld2F5OTU"),
    ("filter95storage95", "ZmlsdGVyOTVzdG9yYWdlOTU"),
    ("filter95network95", "ZmlsdGVyOTVuZXR3b3JrOTU"),
    ("ranking95network95", "cmFua2luZzk1bmV0d29yazk1"),
    ("ranking95latency95", "cmFua2luZzk1bGF0ZW5jeTk1"),
    ("ranking95buffer95", "cmFua2luZzk1YnVmZmVyOTU"),
    ("ranking95queue95", "cmFua2luZzk1cXVldWU5NQ"),
    ("encoding95queue95", "ZW5jb2Rpbmc5NXF1ZXVlOTU"),
    ("encoding95worker95", "ZW5jb2Rpbmc5NXdvcmtlcjk1"),
    ("encoding95kernel95", "ZW5jb2Rpbmc5NWtlcm5lbDk1"),
    ("encoding95signal95", "ZW5jb2Rpbmc5NXNpZ25hbDk1"),
    ("mapping95signal95", "bWFwcGluZzk1c2lnbmFsOTU"),
    ("mapping95packet95", "bWFwcGluZzk1cGFja2V0OTU"),
    ("mapping95router95", "bWFwcGluZzk1cm91dGVyOTU"),
    ("mapping95cluster95", "bWFwcGluZzk1Y2x1c3Rlcjk1"),
    ("record95cluster95", "cmVjb3JkOTVjbHVzdGVyOTU"),
    ("record95mirror95", "cmVjb3JkOTVtaXJyb3I5NQ"),
    ("record95filter95", "cmVjb3JkOTVmaWx0ZXI5NQ"),
    ("record95ranking95", "cmVjb3JkOTVyYW5raW5nOTU"),
    ("candle95ranking95", "Y2FuZGxlOTVyYW5raW5nOTU"),
    ("candle95encoding95", "Y2FuZGxlOTVlbmNvZGluZzk1"),
    ("candle95mapping95", "Y2FuZGxlOTVtYXBwaW5nOTU"),
    ("candle95record95", "Y2FuZGxlOTVyZWNvcmQ5NQ"),
    ("thread95record95", "dGhyZWFkOTVyZWNvcmQ5NQ"),
    ("thread95candle95", "dGhyZWFkOTVjYW5kbGU5NQ"),
    ("thread95thread95", "dGhyZWFkOTV0aHJlYWQ5NQ"),
    ("thread95kitten95", "dGhyZWFkOTVraXR0ZW45NQ"),
    (
        "round 95: the quick brown fox jumps over the lazy dog",
        "cm91bmQgOTU6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 95: agentuniverse is a framework for multi agents",
        "cm91bmQgOTU6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 95: knowledge stored as vectors enables retrieval",
        "cm91bmQgOTU6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 95: the processor reads the record then stops",
        "cm91bmQgOTU6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 95: a worker pulls the next task from the queue",
        "cm91bmQgOTU6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 95: signals travel through the network layer",
        "cm91bmQgOTU6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 95: the gateway routes each request by policy",
        "cm91bmQgOTU6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 95: memory grows until the buffer is full",
        "cm91bmQgOTU6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 95: the cluster mirrors every packet twice",
        "cm91bmQgOTU6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 95: ranking uses tokens learned from the corpus",
        "cm91bmQgOTU6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 95: a long session ends when the candle dies",
        "cm91bmQgOTU6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 95: encode the prompt then map the result",
        "cm91bmQgOTU6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 95: the kernel wakes the worker at dawn", "cm91bmQgOTU6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 95: service latency drops after the patch",
        "cm91bmQgOTU6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 95: the library caches every vector it sees",
        "cm91bmQgOTU6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 95: agents argue then the debate resolves",
        "cm91bmQgOTU6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 95: the filter keeps only strong matches",
        "cm91bmQgOTU6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 95: the model answers with a short reply",
        "cm91bmQgOTU6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 95: the recorder stores the reasoning trace",
        "cm91bmQgOTU6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 95: the angel watches the processor run", "cm91bmQgOTU6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 95: angle of the vector decides the match",
        "cm91bmQgOTU6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 95: the candle burns twice as long at night",
        "cm91bmQgOTU6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 95: a mirror of the universe in one line",
        "cm91bmQgOTU6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 95: the queue drains before the storm", "cm91bmQgOTU6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
