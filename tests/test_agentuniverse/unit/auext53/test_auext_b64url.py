"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten53kitten53", "a2l0dGVuNTNraXR0ZW41Mw"),
    ("kitten53sitting53", "a2l0dGVuNTNzaXR0aW5nNTM"),
    ("kitten53agent53", "a2l0dGVuNTNhZ2VudDUz"),
    ("kitten53angle53", "a2l0dGVuNTNhbmdsZTUz"),
    ("sitting53angle53", "c2l0dGluZzUzYW5nbGU1Mw"),
    ("sitting53universe53", "c2l0dGluZzUzdW5pdmVyc2U1Mw"),
    ("sitting53memory53", "c2l0dGluZzUzbWVtb3J5NTM"),
    ("sitting53stream53", "c2l0dGluZzUzc3RyZWFtNTM"),
    ("agent53stream53", "YWdlbnQ1M3N0cmVhbTUz"),
    ("agent53context53", "YWdlbnQ1M2NvbnRleHQ1Mw"),
    ("agent53knowledge53", "YWdlbnQ1M2tub3dsZWRnZTUz"),
    ("agent53vector53", "YWdlbnQ1M3ZlY3RvcjUz"),
    ("angle53vector53", "YW5nbGU1M3ZlY3RvcjUz"),
    ("angle53processor53", "YW5nbGU1M3Byb2Nlc3NvcjUz"),
    ("angle53reasoning53", "YW5nbGU1M3JlYXNvbmluZzUz"),
    ("angle53machine53", "YW5nbGU1M21hY2hpbmU1Mw"),
    ("universe53machine53", "dW5pdmVyc2U1M21hY2hpbmU1Mw"),
    ("universe53learning53", "dW5pdmVyc2U1M2xlYXJuaW5nNTM"),
    ("universe53model53", "dW5pdmVyc2U1M21vZGVsNTM"),
    ("universe53token53", "dW5pdmVyc2U1M3Rva2VuNTM"),
    ("memory53token53", "bWVtb3J5NTN0b2tlbjUz"),
    ("memory53prompt53", "bWVtb3J5NTNwcm9tcHQ1Mw"),
    ("memory53session53", "bWVtb3J5NTNzZXNzaW9uNTM"),
    ("memory53library53", "bWVtb3J5NTNsaWJyYXJ5NTM"),
    ("stream53library53", "c3RyZWFtNTNsaWJyYXJ5NTM"),
    ("stream53service53", "c3RyZWFtNTNzZXJ2aWNlNTM"),
    ("stream53gateway53", "c3RyZWFtNTNnYXRld2F5NTM"),
    ("stream53storage53", "c3RyZWFtNTNzdG9yYWdlNTM"),
    ("context53storage53", "Y29udGV4dDUzc3RvcmFnZTUz"),
    ("context53network53", "Y29udGV4dDUzbmV0d29yazUz"),
    ("context53latency53", "Y29udGV4dDUzbGF0ZW5jeTUz"),
    ("context53buffer53", "Y29udGV4dDUzYnVmZmVyNTM"),
    ("knowledge53buffer53", "a25vd2xlZGdlNTNidWZmZXI1Mw"),
    ("knowledge53queue53", "a25vd2xlZGdlNTNxdWV1ZTUz"),
    ("knowledge53worker53", "a25vd2xlZGdlNTN3b3JrZXI1Mw"),
    ("knowledge53kernel53", "a25vd2xlZGdlNTNrZXJuZWw1Mw"),
    ("vector53kernel53", "dmVjdG9yNTNrZXJuZWw1Mw"),
    ("vector53signal53", "dmVjdG9yNTNzaWduYWw1Mw"),
    ("vector53packet53", "dmVjdG9yNTNwYWNrZXQ1Mw"),
    ("vector53router53", "dmVjdG9yNTNyb3V0ZXI1Mw"),
    ("processor53router53", "cHJvY2Vzc29yNTNyb3V0ZXI1Mw"),
    ("processor53cluster53", "cHJvY2Vzc29yNTNjbHVzdGVyNTM"),
    ("processor53mirror53", "cHJvY2Vzc29yNTNtaXJyb3I1Mw"),
    ("processor53filter53", "cHJvY2Vzc29yNTNmaWx0ZXI1Mw"),
    ("reasoning53filter53", "cmVhc29uaW5nNTNmaWx0ZXI1Mw"),
    ("reasoning53ranking53", "cmVhc29uaW5nNTNyYW5raW5nNTM"),
    ("reasoning53encoding53", "cmVhc29uaW5nNTNlbmNvZGluZzUz"),
    ("reasoning53mapping53", "cmVhc29uaW5nNTNtYXBwaW5nNTM"),
    ("machine53mapping53", "bWFjaGluZTUzbWFwcGluZzUz"),
    ("machine53record53", "bWFjaGluZTUzcmVjb3JkNTM"),
    ("machine53candle53", "bWFjaGluZTUzY2FuZGxlNTM"),
    ("machine53thread53", "bWFjaGluZTUzdGhyZWFkNTM"),
    ("learning53thread53", "bGVhcm5pbmc1M3RocmVhZDUz"),
    ("learning53kitten53", "bGVhcm5pbmc1M2tpdHRlbjUz"),
    ("learning53sitting53", "bGVhcm5pbmc1M3NpdHRpbmc1Mw"),
    ("learning53agent53", "bGVhcm5pbmc1M2FnZW50NTM"),
    ("model53agent53", "bW9kZWw1M2FnZW50NTM"),
    ("model53angle53", "bW9kZWw1M2FuZ2xlNTM"),
    ("model53universe53", "bW9kZWw1M3VuaXZlcnNlNTM"),
    ("model53memory53", "bW9kZWw1M21lbW9yeTUz"),
    ("token53memory53", "dG9rZW41M21lbW9yeTUz"),
    ("token53stream53", "dG9rZW41M3N0cmVhbTUz"),
    ("token53context53", "dG9rZW41M2NvbnRleHQ1Mw"),
    ("token53knowledge53", "dG9rZW41M2tub3dsZWRnZTUz"),
    ("prompt53knowledge53", "cHJvbXB0NTNrbm93bGVkZ2U1Mw"),
    ("prompt53vector53", "cHJvbXB0NTN2ZWN0b3I1Mw"),
    ("prompt53processor53", "cHJvbXB0NTNwcm9jZXNzb3I1Mw"),
    ("prompt53reasoning53", "cHJvbXB0NTNyZWFzb25pbmc1Mw"),
    ("session53reasoning53", "c2Vzc2lvbjUzcmVhc29uaW5nNTM"),
    ("session53machine53", "c2Vzc2lvbjUzbWFjaGluZTUz"),
    ("session53learning53", "c2Vzc2lvbjUzbGVhcm5pbmc1Mw"),
    ("session53model53", "c2Vzc2lvbjUzbW9kZWw1Mw"),
    ("library53model53", "bGlicmFyeTUzbW9kZWw1Mw"),
    ("library53token53", "bGlicmFyeTUzdG9rZW41Mw"),
    ("library53prompt53", "bGlicmFyeTUzcHJvbXB0NTM"),
    ("library53session53", "bGlicmFyeTUzc2Vzc2lvbjUz"),
    ("service53session53", "c2VydmljZTUzc2Vzc2lvbjUz"),
    ("service53library53", "c2VydmljZTUzbGlicmFyeTUz"),
    ("service53service53", "c2VydmljZTUzc2VydmljZTUz"),
    ("service53gateway53", "c2VydmljZTUzZ2F0ZXdheTUz"),
    ("gateway53gateway53", "Z2F0ZXdheTUzZ2F0ZXdheTUz"),
    ("gateway53storage53", "Z2F0ZXdheTUzc3RvcmFnZTUz"),
    ("gateway53network53", "Z2F0ZXdheTUzbmV0d29yazUz"),
    ("gateway53latency53", "Z2F0ZXdheTUzbGF0ZW5jeTUz"),
    ("storage53latency53", "c3RvcmFnZTUzbGF0ZW5jeTUz"),
    ("storage53buffer53", "c3RvcmFnZTUzYnVmZmVyNTM"),
    ("storage53queue53", "c3RvcmFnZTUzcXVldWU1Mw"),
    ("storage53worker53", "c3RvcmFnZTUzd29ya2VyNTM"),
    ("network53worker53", "bmV0d29yazUzd29ya2VyNTM"),
    ("network53kernel53", "bmV0d29yazUza2VybmVsNTM"),
    ("network53signal53", "bmV0d29yazUzc2lnbmFsNTM"),
    ("network53packet53", "bmV0d29yazUzcGFja2V0NTM"),
    ("latency53packet53", "bGF0ZW5jeTUzcGFja2V0NTM"),
    ("latency53router53", "bGF0ZW5jeTUzcm91dGVyNTM"),
    ("latency53cluster53", "bGF0ZW5jeTUzY2x1c3RlcjUz"),
    ("latency53mirror53", "bGF0ZW5jeTUzbWlycm9yNTM"),
    ("buffer53mirror53", "YnVmZmVyNTNtaXJyb3I1Mw"),
    ("buffer53filter53", "YnVmZmVyNTNmaWx0ZXI1Mw"),
    ("buffer53ranking53", "YnVmZmVyNTNyYW5raW5nNTM"),
    ("buffer53encoding53", "YnVmZmVyNTNlbmNvZGluZzUz"),
    ("queue53encoding53", "cXVldWU1M2VuY29kaW5nNTM"),
    ("queue53mapping53", "cXVldWU1M21hcHBpbmc1Mw"),
    ("queue53record53", "cXVldWU1M3JlY29yZDUz"),
    ("queue53candle53", "cXVldWU1M2NhbmRsZTUz"),
    ("worker53candle53", "d29ya2VyNTNjYW5kbGU1Mw"),
    ("worker53thread53", "d29ya2VyNTN0aHJlYWQ1Mw"),
    ("worker53kitten53", "d29ya2VyNTNraXR0ZW41Mw"),
    ("worker53sitting53", "d29ya2VyNTNzaXR0aW5nNTM"),
    ("kernel53sitting53", "a2VybmVsNTNzaXR0aW5nNTM"),
    ("kernel53agent53", "a2VybmVsNTNhZ2VudDUz"),
    ("kernel53angle53", "a2VybmVsNTNhbmdsZTUz"),
    ("kernel53universe53", "a2VybmVsNTN1bml2ZXJzZTUz"),
    ("signal53universe53", "c2lnbmFsNTN1bml2ZXJzZTUz"),
    ("signal53memory53", "c2lnbmFsNTNtZW1vcnk1Mw"),
    ("signal53stream53", "c2lnbmFsNTNzdHJlYW01Mw"),
    ("signal53context53", "c2lnbmFsNTNjb250ZXh0NTM"),
    ("packet53context53", "cGFja2V0NTNjb250ZXh0NTM"),
    ("packet53knowledge53", "cGFja2V0NTNrbm93bGVkZ2U1Mw"),
    ("packet53vector53", "cGFja2V0NTN2ZWN0b3I1Mw"),
    ("packet53processor53", "cGFja2V0NTNwcm9jZXNzb3I1Mw"),
    ("router53processor53", "cm91dGVyNTNwcm9jZXNzb3I1Mw"),
    ("router53reasoning53", "cm91dGVyNTNyZWFzb25pbmc1Mw"),
    ("router53machine53", "cm91dGVyNTNtYWNoaW5lNTM"),
    ("router53learning53", "cm91dGVyNTNsZWFybmluZzUz"),
    ("cluster53learning53", "Y2x1c3RlcjUzbGVhcm5pbmc1Mw"),
    ("cluster53model53", "Y2x1c3RlcjUzbW9kZWw1Mw"),
    ("cluster53token53", "Y2x1c3RlcjUzdG9rZW41Mw"),
    ("cluster53prompt53", "Y2x1c3RlcjUzcHJvbXB0NTM"),
    ("mirror53prompt53", "bWlycm9yNTNwcm9tcHQ1Mw"),
    ("mirror53session53", "bWlycm9yNTNzZXNzaW9uNTM"),
    ("mirror53library53", "bWlycm9yNTNsaWJyYXJ5NTM"),
    ("mirror53service53", "bWlycm9yNTNzZXJ2aWNlNTM"),
    ("filter53service53", "ZmlsdGVyNTNzZXJ2aWNlNTM"),
    ("filter53gateway53", "ZmlsdGVyNTNnYXRld2F5NTM"),
    ("filter53storage53", "ZmlsdGVyNTNzdG9yYWdlNTM"),
    ("filter53network53", "ZmlsdGVyNTNuZXR3b3JrNTM"),
    ("ranking53network53", "cmFua2luZzUzbmV0d29yazUz"),
    ("ranking53latency53", "cmFua2luZzUzbGF0ZW5jeTUz"),
    ("ranking53buffer53", "cmFua2luZzUzYnVmZmVyNTM"),
    ("ranking53queue53", "cmFua2luZzUzcXVldWU1Mw"),
    ("encoding53queue53", "ZW5jb2Rpbmc1M3F1ZXVlNTM"),
    ("encoding53worker53", "ZW5jb2Rpbmc1M3dvcmtlcjUz"),
    ("encoding53kernel53", "ZW5jb2Rpbmc1M2tlcm5lbDUz"),
    ("encoding53signal53", "ZW5jb2Rpbmc1M3NpZ25hbDUz"),
    ("mapping53signal53", "bWFwcGluZzUzc2lnbmFsNTM"),
    ("mapping53packet53", "bWFwcGluZzUzcGFja2V0NTM"),
    ("mapping53router53", "bWFwcGluZzUzcm91dGVyNTM"),
    ("mapping53cluster53", "bWFwcGluZzUzY2x1c3RlcjUz"),
    ("record53cluster53", "cmVjb3JkNTNjbHVzdGVyNTM"),
    ("record53mirror53", "cmVjb3JkNTNtaXJyb3I1Mw"),
    ("record53filter53", "cmVjb3JkNTNmaWx0ZXI1Mw"),
    ("record53ranking53", "cmVjb3JkNTNyYW5raW5nNTM"),
    ("candle53ranking53", "Y2FuZGxlNTNyYW5raW5nNTM"),
    ("candle53encoding53", "Y2FuZGxlNTNlbmNvZGluZzUz"),
    ("candle53mapping53", "Y2FuZGxlNTNtYXBwaW5nNTM"),
    ("candle53record53", "Y2FuZGxlNTNyZWNvcmQ1Mw"),
    ("thread53record53", "dGhyZWFkNTNyZWNvcmQ1Mw"),
    ("thread53candle53", "dGhyZWFkNTNjYW5kbGU1Mw"),
    ("thread53thread53", "dGhyZWFkNTN0aHJlYWQ1Mw"),
    ("thread53kitten53", "dGhyZWFkNTNraXR0ZW41Mw"),
    (
        "round 53: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNTM6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 53: agentuniverse is a framework for multi agents",
        "cm91bmQgNTM6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 53: knowledge stored as vectors enables retrieval",
        "cm91bmQgNTM6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 53: the processor reads the record then stops",
        "cm91bmQgNTM6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 53: a worker pulls the next task from the queue",
        "cm91bmQgNTM6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 53: signals travel through the network layer",
        "cm91bmQgNTM6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 53: the gateway routes each request by policy",
        "cm91bmQgNTM6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 53: memory grows until the buffer is full",
        "cm91bmQgNTM6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 53: the cluster mirrors every packet twice",
        "cm91bmQgNTM6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 53: ranking uses tokens learned from the corpus",
        "cm91bmQgNTM6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 53: a long session ends when the candle dies",
        "cm91bmQgNTM6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 53: encode the prompt then map the result",
        "cm91bmQgNTM6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 53: the kernel wakes the worker at dawn", "cm91bmQgNTM6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 53: service latency drops after the patch",
        "cm91bmQgNTM6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 53: the library caches every vector it sees",
        "cm91bmQgNTM6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 53: agents argue then the debate resolves",
        "cm91bmQgNTM6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 53: the filter keeps only strong matches",
        "cm91bmQgNTM6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 53: the model answers with a short reply",
        "cm91bmQgNTM6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 53: the recorder stores the reasoning trace",
        "cm91bmQgNTM6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 53: the angel watches the processor run", "cm91bmQgNTM6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 53: angle of the vector decides the match",
        "cm91bmQgNTM6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 53: the candle burns twice as long at night",
        "cm91bmQgNTM6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 53: a mirror of the universe in one line",
        "cm91bmQgNTM6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 53: the queue drains before the storm", "cm91bmQgNTM6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
