"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten73kitten73", "a2l0dGVuNzNraXR0ZW43Mw"),
    ("kitten73sitting73", "a2l0dGVuNzNzaXR0aW5nNzM"),
    ("kitten73agent73", "a2l0dGVuNzNhZ2VudDcz"),
    ("kitten73angle73", "a2l0dGVuNzNhbmdsZTcz"),
    ("sitting73angle73", "c2l0dGluZzczYW5nbGU3Mw"),
    ("sitting73universe73", "c2l0dGluZzczdW5pdmVyc2U3Mw"),
    ("sitting73memory73", "c2l0dGluZzczbWVtb3J5NzM"),
    ("sitting73stream73", "c2l0dGluZzczc3RyZWFtNzM"),
    ("agent73stream73", "YWdlbnQ3M3N0cmVhbTcz"),
    ("agent73context73", "YWdlbnQ3M2NvbnRleHQ3Mw"),
    ("agent73knowledge73", "YWdlbnQ3M2tub3dsZWRnZTcz"),
    ("agent73vector73", "YWdlbnQ3M3ZlY3Rvcjcz"),
    ("angle73vector73", "YW5nbGU3M3ZlY3Rvcjcz"),
    ("angle73processor73", "YW5nbGU3M3Byb2Nlc3Nvcjcz"),
    ("angle73reasoning73", "YW5nbGU3M3JlYXNvbmluZzcz"),
    ("angle73machine73", "YW5nbGU3M21hY2hpbmU3Mw"),
    ("universe73machine73", "dW5pdmVyc2U3M21hY2hpbmU3Mw"),
    ("universe73learning73", "dW5pdmVyc2U3M2xlYXJuaW5nNzM"),
    ("universe73model73", "dW5pdmVyc2U3M21vZGVsNzM"),
    ("universe73token73", "dW5pdmVyc2U3M3Rva2VuNzM"),
    ("memory73token73", "bWVtb3J5NzN0b2tlbjcz"),
    ("memory73prompt73", "bWVtb3J5NzNwcm9tcHQ3Mw"),
    ("memory73session73", "bWVtb3J5NzNzZXNzaW9uNzM"),
    ("memory73library73", "bWVtb3J5NzNsaWJyYXJ5NzM"),
    ("stream73library73", "c3RyZWFtNzNsaWJyYXJ5NzM"),
    ("stream73service73", "c3RyZWFtNzNzZXJ2aWNlNzM"),
    ("stream73gateway73", "c3RyZWFtNzNnYXRld2F5NzM"),
    ("stream73storage73", "c3RyZWFtNzNzdG9yYWdlNzM"),
    ("context73storage73", "Y29udGV4dDczc3RvcmFnZTcz"),
    ("context73network73", "Y29udGV4dDczbmV0d29yazcz"),
    ("context73latency73", "Y29udGV4dDczbGF0ZW5jeTcz"),
    ("context73buffer73", "Y29udGV4dDczYnVmZmVyNzM"),
    ("knowledge73buffer73", "a25vd2xlZGdlNzNidWZmZXI3Mw"),
    ("knowledge73queue73", "a25vd2xlZGdlNzNxdWV1ZTcz"),
    ("knowledge73worker73", "a25vd2xlZGdlNzN3b3JrZXI3Mw"),
    ("knowledge73kernel73", "a25vd2xlZGdlNzNrZXJuZWw3Mw"),
    ("vector73kernel73", "dmVjdG9yNzNrZXJuZWw3Mw"),
    ("vector73signal73", "dmVjdG9yNzNzaWduYWw3Mw"),
    ("vector73packet73", "dmVjdG9yNzNwYWNrZXQ3Mw"),
    ("vector73router73", "dmVjdG9yNzNyb3V0ZXI3Mw"),
    ("processor73router73", "cHJvY2Vzc29yNzNyb3V0ZXI3Mw"),
    ("processor73cluster73", "cHJvY2Vzc29yNzNjbHVzdGVyNzM"),
    ("processor73mirror73", "cHJvY2Vzc29yNzNtaXJyb3I3Mw"),
    ("processor73filter73", "cHJvY2Vzc29yNzNmaWx0ZXI3Mw"),
    ("reasoning73filter73", "cmVhc29uaW5nNzNmaWx0ZXI3Mw"),
    ("reasoning73ranking73", "cmVhc29uaW5nNzNyYW5raW5nNzM"),
    ("reasoning73encoding73", "cmVhc29uaW5nNzNlbmNvZGluZzcz"),
    ("reasoning73mapping73", "cmVhc29uaW5nNzNtYXBwaW5nNzM"),
    ("machine73mapping73", "bWFjaGluZTczbWFwcGluZzcz"),
    ("machine73record73", "bWFjaGluZTczcmVjb3JkNzM"),
    ("machine73candle73", "bWFjaGluZTczY2FuZGxlNzM"),
    ("machine73thread73", "bWFjaGluZTczdGhyZWFkNzM"),
    ("learning73thread73", "bGVhcm5pbmc3M3RocmVhZDcz"),
    ("learning73kitten73", "bGVhcm5pbmc3M2tpdHRlbjcz"),
    ("learning73sitting73", "bGVhcm5pbmc3M3NpdHRpbmc3Mw"),
    ("learning73agent73", "bGVhcm5pbmc3M2FnZW50NzM"),
    ("model73agent73", "bW9kZWw3M2FnZW50NzM"),
    ("model73angle73", "bW9kZWw3M2FuZ2xlNzM"),
    ("model73universe73", "bW9kZWw3M3VuaXZlcnNlNzM"),
    ("model73memory73", "bW9kZWw3M21lbW9yeTcz"),
    ("token73memory73", "dG9rZW43M21lbW9yeTcz"),
    ("token73stream73", "dG9rZW43M3N0cmVhbTcz"),
    ("token73context73", "dG9rZW43M2NvbnRleHQ3Mw"),
    ("token73knowledge73", "dG9rZW43M2tub3dsZWRnZTcz"),
    ("prompt73knowledge73", "cHJvbXB0NzNrbm93bGVkZ2U3Mw"),
    ("prompt73vector73", "cHJvbXB0NzN2ZWN0b3I3Mw"),
    ("prompt73processor73", "cHJvbXB0NzNwcm9jZXNzb3I3Mw"),
    ("prompt73reasoning73", "cHJvbXB0NzNyZWFzb25pbmc3Mw"),
    ("session73reasoning73", "c2Vzc2lvbjczcmVhc29uaW5nNzM"),
    ("session73machine73", "c2Vzc2lvbjczbWFjaGluZTcz"),
    ("session73learning73", "c2Vzc2lvbjczbGVhcm5pbmc3Mw"),
    ("session73model73", "c2Vzc2lvbjczbW9kZWw3Mw"),
    ("library73model73", "bGlicmFyeTczbW9kZWw3Mw"),
    ("library73token73", "bGlicmFyeTczdG9rZW43Mw"),
    ("library73prompt73", "bGlicmFyeTczcHJvbXB0NzM"),
    ("library73session73", "bGlicmFyeTczc2Vzc2lvbjcz"),
    ("service73session73", "c2VydmljZTczc2Vzc2lvbjcz"),
    ("service73library73", "c2VydmljZTczbGlicmFyeTcz"),
    ("service73service73", "c2VydmljZTczc2VydmljZTcz"),
    ("service73gateway73", "c2VydmljZTczZ2F0ZXdheTcz"),
    ("gateway73gateway73", "Z2F0ZXdheTczZ2F0ZXdheTcz"),
    ("gateway73storage73", "Z2F0ZXdheTczc3RvcmFnZTcz"),
    ("gateway73network73", "Z2F0ZXdheTczbmV0d29yazcz"),
    ("gateway73latency73", "Z2F0ZXdheTczbGF0ZW5jeTcz"),
    ("storage73latency73", "c3RvcmFnZTczbGF0ZW5jeTcz"),
    ("storage73buffer73", "c3RvcmFnZTczYnVmZmVyNzM"),
    ("storage73queue73", "c3RvcmFnZTczcXVldWU3Mw"),
    ("storage73worker73", "c3RvcmFnZTczd29ya2VyNzM"),
    ("network73worker73", "bmV0d29yazczd29ya2VyNzM"),
    ("network73kernel73", "bmV0d29yazcza2VybmVsNzM"),
    ("network73signal73", "bmV0d29yazczc2lnbmFsNzM"),
    ("network73packet73", "bmV0d29yazczcGFja2V0NzM"),
    ("latency73packet73", "bGF0ZW5jeTczcGFja2V0NzM"),
    ("latency73router73", "bGF0ZW5jeTczcm91dGVyNzM"),
    ("latency73cluster73", "bGF0ZW5jeTczY2x1c3Rlcjcz"),
    ("latency73mirror73", "bGF0ZW5jeTczbWlycm9yNzM"),
    ("buffer73mirror73", "YnVmZmVyNzNtaXJyb3I3Mw"),
    ("buffer73filter73", "YnVmZmVyNzNmaWx0ZXI3Mw"),
    ("buffer73ranking73", "YnVmZmVyNzNyYW5raW5nNzM"),
    ("buffer73encoding73", "YnVmZmVyNzNlbmNvZGluZzcz"),
    ("queue73encoding73", "cXVldWU3M2VuY29kaW5nNzM"),
    ("queue73mapping73", "cXVldWU3M21hcHBpbmc3Mw"),
    ("queue73record73", "cXVldWU3M3JlY29yZDcz"),
    ("queue73candle73", "cXVldWU3M2NhbmRsZTcz"),
    ("worker73candle73", "d29ya2VyNzNjYW5kbGU3Mw"),
    ("worker73thread73", "d29ya2VyNzN0aHJlYWQ3Mw"),
    ("worker73kitten73", "d29ya2VyNzNraXR0ZW43Mw"),
    ("worker73sitting73", "d29ya2VyNzNzaXR0aW5nNzM"),
    ("kernel73sitting73", "a2VybmVsNzNzaXR0aW5nNzM"),
    ("kernel73agent73", "a2VybmVsNzNhZ2VudDcz"),
    ("kernel73angle73", "a2VybmVsNzNhbmdsZTcz"),
    ("kernel73universe73", "a2VybmVsNzN1bml2ZXJzZTcz"),
    ("signal73universe73", "c2lnbmFsNzN1bml2ZXJzZTcz"),
    ("signal73memory73", "c2lnbmFsNzNtZW1vcnk3Mw"),
    ("signal73stream73", "c2lnbmFsNzNzdHJlYW03Mw"),
    ("signal73context73", "c2lnbmFsNzNjb250ZXh0NzM"),
    ("packet73context73", "cGFja2V0NzNjb250ZXh0NzM"),
    ("packet73knowledge73", "cGFja2V0NzNrbm93bGVkZ2U3Mw"),
    ("packet73vector73", "cGFja2V0NzN2ZWN0b3I3Mw"),
    ("packet73processor73", "cGFja2V0NzNwcm9jZXNzb3I3Mw"),
    ("router73processor73", "cm91dGVyNzNwcm9jZXNzb3I3Mw"),
    ("router73reasoning73", "cm91dGVyNzNyZWFzb25pbmc3Mw"),
    ("router73machine73", "cm91dGVyNzNtYWNoaW5lNzM"),
    ("router73learning73", "cm91dGVyNzNsZWFybmluZzcz"),
    ("cluster73learning73", "Y2x1c3RlcjczbGVhcm5pbmc3Mw"),
    ("cluster73model73", "Y2x1c3RlcjczbW9kZWw3Mw"),
    ("cluster73token73", "Y2x1c3RlcjczdG9rZW43Mw"),
    ("cluster73prompt73", "Y2x1c3RlcjczcHJvbXB0NzM"),
    ("mirror73prompt73", "bWlycm9yNzNwcm9tcHQ3Mw"),
    ("mirror73session73", "bWlycm9yNzNzZXNzaW9uNzM"),
    ("mirror73library73", "bWlycm9yNzNsaWJyYXJ5NzM"),
    ("mirror73service73", "bWlycm9yNzNzZXJ2aWNlNzM"),
    ("filter73service73", "ZmlsdGVyNzNzZXJ2aWNlNzM"),
    ("filter73gateway73", "ZmlsdGVyNzNnYXRld2F5NzM"),
    ("filter73storage73", "ZmlsdGVyNzNzdG9yYWdlNzM"),
    ("filter73network73", "ZmlsdGVyNzNuZXR3b3JrNzM"),
    ("ranking73network73", "cmFua2luZzczbmV0d29yazcz"),
    ("ranking73latency73", "cmFua2luZzczbGF0ZW5jeTcz"),
    ("ranking73buffer73", "cmFua2luZzczYnVmZmVyNzM"),
    ("ranking73queue73", "cmFua2luZzczcXVldWU3Mw"),
    ("encoding73queue73", "ZW5jb2Rpbmc3M3F1ZXVlNzM"),
    ("encoding73worker73", "ZW5jb2Rpbmc3M3dvcmtlcjcz"),
    ("encoding73kernel73", "ZW5jb2Rpbmc3M2tlcm5lbDcz"),
    ("encoding73signal73", "ZW5jb2Rpbmc3M3NpZ25hbDcz"),
    ("mapping73signal73", "bWFwcGluZzczc2lnbmFsNzM"),
    ("mapping73packet73", "bWFwcGluZzczcGFja2V0NzM"),
    ("mapping73router73", "bWFwcGluZzczcm91dGVyNzM"),
    ("mapping73cluster73", "bWFwcGluZzczY2x1c3Rlcjcz"),
    ("record73cluster73", "cmVjb3JkNzNjbHVzdGVyNzM"),
    ("record73mirror73", "cmVjb3JkNzNtaXJyb3I3Mw"),
    ("record73filter73", "cmVjb3JkNzNmaWx0ZXI3Mw"),
    ("record73ranking73", "cmVjb3JkNzNyYW5raW5nNzM"),
    ("candle73ranking73", "Y2FuZGxlNzNyYW5raW5nNzM"),
    ("candle73encoding73", "Y2FuZGxlNzNlbmNvZGluZzcz"),
    ("candle73mapping73", "Y2FuZGxlNzNtYXBwaW5nNzM"),
    ("candle73record73", "Y2FuZGxlNzNyZWNvcmQ3Mw"),
    ("thread73record73", "dGhyZWFkNzNyZWNvcmQ3Mw"),
    ("thread73candle73", "dGhyZWFkNzNjYW5kbGU3Mw"),
    ("thread73thread73", "dGhyZWFkNzN0aHJlYWQ3Mw"),
    ("thread73kitten73", "dGhyZWFkNzNraXR0ZW43Mw"),
    (
        "round 73: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzM6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 73: agentuniverse is a framework for multi agents",
        "cm91bmQgNzM6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 73: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzM6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 73: the processor reads the record then stops",
        "cm91bmQgNzM6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 73: a worker pulls the next task from the queue",
        "cm91bmQgNzM6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 73: signals travel through the network layer",
        "cm91bmQgNzM6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 73: the gateway routes each request by policy",
        "cm91bmQgNzM6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 73: memory grows until the buffer is full",
        "cm91bmQgNzM6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 73: the cluster mirrors every packet twice",
        "cm91bmQgNzM6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 73: ranking uses tokens learned from the corpus",
        "cm91bmQgNzM6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 73: a long session ends when the candle dies",
        "cm91bmQgNzM6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 73: encode the prompt then map the result",
        "cm91bmQgNzM6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 73: the kernel wakes the worker at dawn", "cm91bmQgNzM6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 73: service latency drops after the patch",
        "cm91bmQgNzM6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 73: the library caches every vector it sees",
        "cm91bmQgNzM6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 73: agents argue then the debate resolves",
        "cm91bmQgNzM6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 73: the filter keeps only strong matches",
        "cm91bmQgNzM6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 73: the model answers with a short reply",
        "cm91bmQgNzM6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 73: the recorder stores the reasoning trace",
        "cm91bmQgNzM6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 73: the angel watches the processor run", "cm91bmQgNzM6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 73: angle of the vector decides the match",
        "cm91bmQgNzM6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 73: the candle burns twice as long at night",
        "cm91bmQgNzM6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 73: a mirror of the universe in one line",
        "cm91bmQgNzM6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 73: the queue drains before the storm", "cm91bmQgNzM6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
