"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten43kitten43", "a2l0dGVuNDNraXR0ZW40Mw"),
    ("kitten43sitting43", "a2l0dGVuNDNzaXR0aW5nNDM"),
    ("kitten43agent43", "a2l0dGVuNDNhZ2VudDQz"),
    ("kitten43angle43", "a2l0dGVuNDNhbmdsZTQz"),
    ("sitting43angle43", "c2l0dGluZzQzYW5nbGU0Mw"),
    ("sitting43universe43", "c2l0dGluZzQzdW5pdmVyc2U0Mw"),
    ("sitting43memory43", "c2l0dGluZzQzbWVtb3J5NDM"),
    ("sitting43stream43", "c2l0dGluZzQzc3RyZWFtNDM"),
    ("agent43stream43", "YWdlbnQ0M3N0cmVhbTQz"),
    ("agent43context43", "YWdlbnQ0M2NvbnRleHQ0Mw"),
    ("agent43knowledge43", "YWdlbnQ0M2tub3dsZWRnZTQz"),
    ("agent43vector43", "YWdlbnQ0M3ZlY3RvcjQz"),
    ("angle43vector43", "YW5nbGU0M3ZlY3RvcjQz"),
    ("angle43processor43", "YW5nbGU0M3Byb2Nlc3NvcjQz"),
    ("angle43reasoning43", "YW5nbGU0M3JlYXNvbmluZzQz"),
    ("angle43machine43", "YW5nbGU0M21hY2hpbmU0Mw"),
    ("universe43machine43", "dW5pdmVyc2U0M21hY2hpbmU0Mw"),
    ("universe43learning43", "dW5pdmVyc2U0M2xlYXJuaW5nNDM"),
    ("universe43model43", "dW5pdmVyc2U0M21vZGVsNDM"),
    ("universe43token43", "dW5pdmVyc2U0M3Rva2VuNDM"),
    ("memory43token43", "bWVtb3J5NDN0b2tlbjQz"),
    ("memory43prompt43", "bWVtb3J5NDNwcm9tcHQ0Mw"),
    ("memory43session43", "bWVtb3J5NDNzZXNzaW9uNDM"),
    ("memory43library43", "bWVtb3J5NDNsaWJyYXJ5NDM"),
    ("stream43library43", "c3RyZWFtNDNsaWJyYXJ5NDM"),
    ("stream43service43", "c3RyZWFtNDNzZXJ2aWNlNDM"),
    ("stream43gateway43", "c3RyZWFtNDNnYXRld2F5NDM"),
    ("stream43storage43", "c3RyZWFtNDNzdG9yYWdlNDM"),
    ("context43storage43", "Y29udGV4dDQzc3RvcmFnZTQz"),
    ("context43network43", "Y29udGV4dDQzbmV0d29yazQz"),
    ("context43latency43", "Y29udGV4dDQzbGF0ZW5jeTQz"),
    ("context43buffer43", "Y29udGV4dDQzYnVmZmVyNDM"),
    ("knowledge43buffer43", "a25vd2xlZGdlNDNidWZmZXI0Mw"),
    ("knowledge43queue43", "a25vd2xlZGdlNDNxdWV1ZTQz"),
    ("knowledge43worker43", "a25vd2xlZGdlNDN3b3JrZXI0Mw"),
    ("knowledge43kernel43", "a25vd2xlZGdlNDNrZXJuZWw0Mw"),
    ("vector43kernel43", "dmVjdG9yNDNrZXJuZWw0Mw"),
    ("vector43signal43", "dmVjdG9yNDNzaWduYWw0Mw"),
    ("vector43packet43", "dmVjdG9yNDNwYWNrZXQ0Mw"),
    ("vector43router43", "dmVjdG9yNDNyb3V0ZXI0Mw"),
    ("processor43router43", "cHJvY2Vzc29yNDNyb3V0ZXI0Mw"),
    ("processor43cluster43", "cHJvY2Vzc29yNDNjbHVzdGVyNDM"),
    ("processor43mirror43", "cHJvY2Vzc29yNDNtaXJyb3I0Mw"),
    ("processor43filter43", "cHJvY2Vzc29yNDNmaWx0ZXI0Mw"),
    ("reasoning43filter43", "cmVhc29uaW5nNDNmaWx0ZXI0Mw"),
    ("reasoning43ranking43", "cmVhc29uaW5nNDNyYW5raW5nNDM"),
    ("reasoning43encoding43", "cmVhc29uaW5nNDNlbmNvZGluZzQz"),
    ("reasoning43mapping43", "cmVhc29uaW5nNDNtYXBwaW5nNDM"),
    ("machine43mapping43", "bWFjaGluZTQzbWFwcGluZzQz"),
    ("machine43record43", "bWFjaGluZTQzcmVjb3JkNDM"),
    ("machine43candle43", "bWFjaGluZTQzY2FuZGxlNDM"),
    ("machine43thread43", "bWFjaGluZTQzdGhyZWFkNDM"),
    ("learning43thread43", "bGVhcm5pbmc0M3RocmVhZDQz"),
    ("learning43kitten43", "bGVhcm5pbmc0M2tpdHRlbjQz"),
    ("learning43sitting43", "bGVhcm5pbmc0M3NpdHRpbmc0Mw"),
    ("learning43agent43", "bGVhcm5pbmc0M2FnZW50NDM"),
    ("model43agent43", "bW9kZWw0M2FnZW50NDM"),
    ("model43angle43", "bW9kZWw0M2FuZ2xlNDM"),
    ("model43universe43", "bW9kZWw0M3VuaXZlcnNlNDM"),
    ("model43memory43", "bW9kZWw0M21lbW9yeTQz"),
    ("token43memory43", "dG9rZW40M21lbW9yeTQz"),
    ("token43stream43", "dG9rZW40M3N0cmVhbTQz"),
    ("token43context43", "dG9rZW40M2NvbnRleHQ0Mw"),
    ("token43knowledge43", "dG9rZW40M2tub3dsZWRnZTQz"),
    ("prompt43knowledge43", "cHJvbXB0NDNrbm93bGVkZ2U0Mw"),
    ("prompt43vector43", "cHJvbXB0NDN2ZWN0b3I0Mw"),
    ("prompt43processor43", "cHJvbXB0NDNwcm9jZXNzb3I0Mw"),
    ("prompt43reasoning43", "cHJvbXB0NDNyZWFzb25pbmc0Mw"),
    ("session43reasoning43", "c2Vzc2lvbjQzcmVhc29uaW5nNDM"),
    ("session43machine43", "c2Vzc2lvbjQzbWFjaGluZTQz"),
    ("session43learning43", "c2Vzc2lvbjQzbGVhcm5pbmc0Mw"),
    ("session43model43", "c2Vzc2lvbjQzbW9kZWw0Mw"),
    ("library43model43", "bGlicmFyeTQzbW9kZWw0Mw"),
    ("library43token43", "bGlicmFyeTQzdG9rZW40Mw"),
    ("library43prompt43", "bGlicmFyeTQzcHJvbXB0NDM"),
    ("library43session43", "bGlicmFyeTQzc2Vzc2lvbjQz"),
    ("service43session43", "c2VydmljZTQzc2Vzc2lvbjQz"),
    ("service43library43", "c2VydmljZTQzbGlicmFyeTQz"),
    ("service43service43", "c2VydmljZTQzc2VydmljZTQz"),
    ("service43gateway43", "c2VydmljZTQzZ2F0ZXdheTQz"),
    ("gateway43gateway43", "Z2F0ZXdheTQzZ2F0ZXdheTQz"),
    ("gateway43storage43", "Z2F0ZXdheTQzc3RvcmFnZTQz"),
    ("gateway43network43", "Z2F0ZXdheTQzbmV0d29yazQz"),
    ("gateway43latency43", "Z2F0ZXdheTQzbGF0ZW5jeTQz"),
    ("storage43latency43", "c3RvcmFnZTQzbGF0ZW5jeTQz"),
    ("storage43buffer43", "c3RvcmFnZTQzYnVmZmVyNDM"),
    ("storage43queue43", "c3RvcmFnZTQzcXVldWU0Mw"),
    ("storage43worker43", "c3RvcmFnZTQzd29ya2VyNDM"),
    ("network43worker43", "bmV0d29yazQzd29ya2VyNDM"),
    ("network43kernel43", "bmV0d29yazQza2VybmVsNDM"),
    ("network43signal43", "bmV0d29yazQzc2lnbmFsNDM"),
    ("network43packet43", "bmV0d29yazQzcGFja2V0NDM"),
    ("latency43packet43", "bGF0ZW5jeTQzcGFja2V0NDM"),
    ("latency43router43", "bGF0ZW5jeTQzcm91dGVyNDM"),
    ("latency43cluster43", "bGF0ZW5jeTQzY2x1c3RlcjQz"),
    ("latency43mirror43", "bGF0ZW5jeTQzbWlycm9yNDM"),
    ("buffer43mirror43", "YnVmZmVyNDNtaXJyb3I0Mw"),
    ("buffer43filter43", "YnVmZmVyNDNmaWx0ZXI0Mw"),
    ("buffer43ranking43", "YnVmZmVyNDNyYW5raW5nNDM"),
    ("buffer43encoding43", "YnVmZmVyNDNlbmNvZGluZzQz"),
    ("queue43encoding43", "cXVldWU0M2VuY29kaW5nNDM"),
    ("queue43mapping43", "cXVldWU0M21hcHBpbmc0Mw"),
    ("queue43record43", "cXVldWU0M3JlY29yZDQz"),
    ("queue43candle43", "cXVldWU0M2NhbmRsZTQz"),
    ("worker43candle43", "d29ya2VyNDNjYW5kbGU0Mw"),
    ("worker43thread43", "d29ya2VyNDN0aHJlYWQ0Mw"),
    ("worker43kitten43", "d29ya2VyNDNraXR0ZW40Mw"),
    ("worker43sitting43", "d29ya2VyNDNzaXR0aW5nNDM"),
    ("kernel43sitting43", "a2VybmVsNDNzaXR0aW5nNDM"),
    ("kernel43agent43", "a2VybmVsNDNhZ2VudDQz"),
    ("kernel43angle43", "a2VybmVsNDNhbmdsZTQz"),
    ("kernel43universe43", "a2VybmVsNDN1bml2ZXJzZTQz"),
    ("signal43universe43", "c2lnbmFsNDN1bml2ZXJzZTQz"),
    ("signal43memory43", "c2lnbmFsNDNtZW1vcnk0Mw"),
    ("signal43stream43", "c2lnbmFsNDNzdHJlYW00Mw"),
    ("signal43context43", "c2lnbmFsNDNjb250ZXh0NDM"),
    ("packet43context43", "cGFja2V0NDNjb250ZXh0NDM"),
    ("packet43knowledge43", "cGFja2V0NDNrbm93bGVkZ2U0Mw"),
    ("packet43vector43", "cGFja2V0NDN2ZWN0b3I0Mw"),
    ("packet43processor43", "cGFja2V0NDNwcm9jZXNzb3I0Mw"),
    ("router43processor43", "cm91dGVyNDNwcm9jZXNzb3I0Mw"),
    ("router43reasoning43", "cm91dGVyNDNyZWFzb25pbmc0Mw"),
    ("router43machine43", "cm91dGVyNDNtYWNoaW5lNDM"),
    ("router43learning43", "cm91dGVyNDNsZWFybmluZzQz"),
    ("cluster43learning43", "Y2x1c3RlcjQzbGVhcm5pbmc0Mw"),
    ("cluster43model43", "Y2x1c3RlcjQzbW9kZWw0Mw"),
    ("cluster43token43", "Y2x1c3RlcjQzdG9rZW40Mw"),
    ("cluster43prompt43", "Y2x1c3RlcjQzcHJvbXB0NDM"),
    ("mirror43prompt43", "bWlycm9yNDNwcm9tcHQ0Mw"),
    ("mirror43session43", "bWlycm9yNDNzZXNzaW9uNDM"),
    ("mirror43library43", "bWlycm9yNDNsaWJyYXJ5NDM"),
    ("mirror43service43", "bWlycm9yNDNzZXJ2aWNlNDM"),
    ("filter43service43", "ZmlsdGVyNDNzZXJ2aWNlNDM"),
    ("filter43gateway43", "ZmlsdGVyNDNnYXRld2F5NDM"),
    ("filter43storage43", "ZmlsdGVyNDNzdG9yYWdlNDM"),
    ("filter43network43", "ZmlsdGVyNDNuZXR3b3JrNDM"),
    ("ranking43network43", "cmFua2luZzQzbmV0d29yazQz"),
    ("ranking43latency43", "cmFua2luZzQzbGF0ZW5jeTQz"),
    ("ranking43buffer43", "cmFua2luZzQzYnVmZmVyNDM"),
    ("ranking43queue43", "cmFua2luZzQzcXVldWU0Mw"),
    ("encoding43queue43", "ZW5jb2Rpbmc0M3F1ZXVlNDM"),
    ("encoding43worker43", "ZW5jb2Rpbmc0M3dvcmtlcjQz"),
    ("encoding43kernel43", "ZW5jb2Rpbmc0M2tlcm5lbDQz"),
    ("encoding43signal43", "ZW5jb2Rpbmc0M3NpZ25hbDQz"),
    ("mapping43signal43", "bWFwcGluZzQzc2lnbmFsNDM"),
    ("mapping43packet43", "bWFwcGluZzQzcGFja2V0NDM"),
    ("mapping43router43", "bWFwcGluZzQzcm91dGVyNDM"),
    ("mapping43cluster43", "bWFwcGluZzQzY2x1c3RlcjQz"),
    ("record43cluster43", "cmVjb3JkNDNjbHVzdGVyNDM"),
    ("record43mirror43", "cmVjb3JkNDNtaXJyb3I0Mw"),
    ("record43filter43", "cmVjb3JkNDNmaWx0ZXI0Mw"),
    ("record43ranking43", "cmVjb3JkNDNyYW5raW5nNDM"),
    ("candle43ranking43", "Y2FuZGxlNDNyYW5raW5nNDM"),
    ("candle43encoding43", "Y2FuZGxlNDNlbmNvZGluZzQz"),
    ("candle43mapping43", "Y2FuZGxlNDNtYXBwaW5nNDM"),
    ("candle43record43", "Y2FuZGxlNDNyZWNvcmQ0Mw"),
    ("thread43record43", "dGhyZWFkNDNyZWNvcmQ0Mw"),
    ("thread43candle43", "dGhyZWFkNDNjYW5kbGU0Mw"),
    ("thread43thread43", "dGhyZWFkNDN0aHJlYWQ0Mw"),
    ("thread43kitten43", "dGhyZWFkNDNraXR0ZW40Mw"),
    (
        "round 43: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNDM6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 43: agentuniverse is a framework for multi agents",
        "cm91bmQgNDM6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 43: knowledge stored as vectors enables retrieval",
        "cm91bmQgNDM6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 43: the processor reads the record then stops",
        "cm91bmQgNDM6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 43: a worker pulls the next task from the queue",
        "cm91bmQgNDM6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 43: signals travel through the network layer",
        "cm91bmQgNDM6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 43: the gateway routes each request by policy",
        "cm91bmQgNDM6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 43: memory grows until the buffer is full",
        "cm91bmQgNDM6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 43: the cluster mirrors every packet twice",
        "cm91bmQgNDM6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 43: ranking uses tokens learned from the corpus",
        "cm91bmQgNDM6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 43: a long session ends when the candle dies",
        "cm91bmQgNDM6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 43: encode the prompt then map the result",
        "cm91bmQgNDM6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 43: the kernel wakes the worker at dawn", "cm91bmQgNDM6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 43: service latency drops after the patch",
        "cm91bmQgNDM6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 43: the library caches every vector it sees",
        "cm91bmQgNDM6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 43: agents argue then the debate resolves",
        "cm91bmQgNDM6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 43: the filter keeps only strong matches",
        "cm91bmQgNDM6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 43: the model answers with a short reply",
        "cm91bmQgNDM6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 43: the recorder stores the reasoning trace",
        "cm91bmQgNDM6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 43: the angel watches the processor run", "cm91bmQgNDM6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 43: angle of the vector decides the match",
        "cm91bmQgNDM6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 43: the candle burns twice as long at night",
        "cm91bmQgNDM6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 43: a mirror of the universe in one line",
        "cm91bmQgNDM6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 43: the queue drains before the storm", "cm91bmQgNDM6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
