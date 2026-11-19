"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten77kitten77", "a2l0dGVuNzdraXR0ZW43Nw"),
    ("kitten77sitting77", "a2l0dGVuNzdzaXR0aW5nNzc"),
    ("kitten77agent77", "a2l0dGVuNzdhZ2VudDc3"),
    ("kitten77angle77", "a2l0dGVuNzdhbmdsZTc3"),
    ("sitting77angle77", "c2l0dGluZzc3YW5nbGU3Nw"),
    ("sitting77universe77", "c2l0dGluZzc3dW5pdmVyc2U3Nw"),
    ("sitting77memory77", "c2l0dGluZzc3bWVtb3J5Nzc"),
    ("sitting77stream77", "c2l0dGluZzc3c3RyZWFtNzc"),
    ("agent77stream77", "YWdlbnQ3N3N0cmVhbTc3"),
    ("agent77context77", "YWdlbnQ3N2NvbnRleHQ3Nw"),
    ("agent77knowledge77", "YWdlbnQ3N2tub3dsZWRnZTc3"),
    ("agent77vector77", "YWdlbnQ3N3ZlY3Rvcjc3"),
    ("angle77vector77", "YW5nbGU3N3ZlY3Rvcjc3"),
    ("angle77processor77", "YW5nbGU3N3Byb2Nlc3Nvcjc3"),
    ("angle77reasoning77", "YW5nbGU3N3JlYXNvbmluZzc3"),
    ("angle77machine77", "YW5nbGU3N21hY2hpbmU3Nw"),
    ("universe77machine77", "dW5pdmVyc2U3N21hY2hpbmU3Nw"),
    ("universe77learning77", "dW5pdmVyc2U3N2xlYXJuaW5nNzc"),
    ("universe77model77", "dW5pdmVyc2U3N21vZGVsNzc"),
    ("universe77token77", "dW5pdmVyc2U3N3Rva2VuNzc"),
    ("memory77token77", "bWVtb3J5Nzd0b2tlbjc3"),
    ("memory77prompt77", "bWVtb3J5Nzdwcm9tcHQ3Nw"),
    ("memory77session77", "bWVtb3J5NzdzZXNzaW9uNzc"),
    ("memory77library77", "bWVtb3J5NzdsaWJyYXJ5Nzc"),
    ("stream77library77", "c3RyZWFtNzdsaWJyYXJ5Nzc"),
    ("stream77service77", "c3RyZWFtNzdzZXJ2aWNlNzc"),
    ("stream77gateway77", "c3RyZWFtNzdnYXRld2F5Nzc"),
    ("stream77storage77", "c3RyZWFtNzdzdG9yYWdlNzc"),
    ("context77storage77", "Y29udGV4dDc3c3RvcmFnZTc3"),
    ("context77network77", "Y29udGV4dDc3bmV0d29yazc3"),
    ("context77latency77", "Y29udGV4dDc3bGF0ZW5jeTc3"),
    ("context77buffer77", "Y29udGV4dDc3YnVmZmVyNzc"),
    ("knowledge77buffer77", "a25vd2xlZGdlNzdidWZmZXI3Nw"),
    ("knowledge77queue77", "a25vd2xlZGdlNzdxdWV1ZTc3"),
    ("knowledge77worker77", "a25vd2xlZGdlNzd3b3JrZXI3Nw"),
    ("knowledge77kernel77", "a25vd2xlZGdlNzdrZXJuZWw3Nw"),
    ("vector77kernel77", "dmVjdG9yNzdrZXJuZWw3Nw"),
    ("vector77signal77", "dmVjdG9yNzdzaWduYWw3Nw"),
    ("vector77packet77", "dmVjdG9yNzdwYWNrZXQ3Nw"),
    ("vector77router77", "dmVjdG9yNzdyb3V0ZXI3Nw"),
    ("processor77router77", "cHJvY2Vzc29yNzdyb3V0ZXI3Nw"),
    ("processor77cluster77", "cHJvY2Vzc29yNzdjbHVzdGVyNzc"),
    ("processor77mirror77", "cHJvY2Vzc29yNzdtaXJyb3I3Nw"),
    ("processor77filter77", "cHJvY2Vzc29yNzdmaWx0ZXI3Nw"),
    ("reasoning77filter77", "cmVhc29uaW5nNzdmaWx0ZXI3Nw"),
    ("reasoning77ranking77", "cmVhc29uaW5nNzdyYW5raW5nNzc"),
    ("reasoning77encoding77", "cmVhc29uaW5nNzdlbmNvZGluZzc3"),
    ("reasoning77mapping77", "cmVhc29uaW5nNzdtYXBwaW5nNzc"),
    ("machine77mapping77", "bWFjaGluZTc3bWFwcGluZzc3"),
    ("machine77record77", "bWFjaGluZTc3cmVjb3JkNzc"),
    ("machine77candle77", "bWFjaGluZTc3Y2FuZGxlNzc"),
    ("machine77thread77", "bWFjaGluZTc3dGhyZWFkNzc"),
    ("learning77thread77", "bGVhcm5pbmc3N3RocmVhZDc3"),
    ("learning77kitten77", "bGVhcm5pbmc3N2tpdHRlbjc3"),
    ("learning77sitting77", "bGVhcm5pbmc3N3NpdHRpbmc3Nw"),
    ("learning77agent77", "bGVhcm5pbmc3N2FnZW50Nzc"),
    ("model77agent77", "bW9kZWw3N2FnZW50Nzc"),
    ("model77angle77", "bW9kZWw3N2FuZ2xlNzc"),
    ("model77universe77", "bW9kZWw3N3VuaXZlcnNlNzc"),
    ("model77memory77", "bW9kZWw3N21lbW9yeTc3"),
    ("token77memory77", "dG9rZW43N21lbW9yeTc3"),
    ("token77stream77", "dG9rZW43N3N0cmVhbTc3"),
    ("token77context77", "dG9rZW43N2NvbnRleHQ3Nw"),
    ("token77knowledge77", "dG9rZW43N2tub3dsZWRnZTc3"),
    ("prompt77knowledge77", "cHJvbXB0Nzdrbm93bGVkZ2U3Nw"),
    ("prompt77vector77", "cHJvbXB0Nzd2ZWN0b3I3Nw"),
    ("prompt77processor77", "cHJvbXB0Nzdwcm9jZXNzb3I3Nw"),
    ("prompt77reasoning77", "cHJvbXB0NzdyZWFzb25pbmc3Nw"),
    ("session77reasoning77", "c2Vzc2lvbjc3cmVhc29uaW5nNzc"),
    ("session77machine77", "c2Vzc2lvbjc3bWFjaGluZTc3"),
    ("session77learning77", "c2Vzc2lvbjc3bGVhcm5pbmc3Nw"),
    ("session77model77", "c2Vzc2lvbjc3bW9kZWw3Nw"),
    ("library77model77", "bGlicmFyeTc3bW9kZWw3Nw"),
    ("library77token77", "bGlicmFyeTc3dG9rZW43Nw"),
    ("library77prompt77", "bGlicmFyeTc3cHJvbXB0Nzc"),
    ("library77session77", "bGlicmFyeTc3c2Vzc2lvbjc3"),
    ("service77session77", "c2VydmljZTc3c2Vzc2lvbjc3"),
    ("service77library77", "c2VydmljZTc3bGlicmFyeTc3"),
    ("service77service77", "c2VydmljZTc3c2VydmljZTc3"),
    ("service77gateway77", "c2VydmljZTc3Z2F0ZXdheTc3"),
    ("gateway77gateway77", "Z2F0ZXdheTc3Z2F0ZXdheTc3"),
    ("gateway77storage77", "Z2F0ZXdheTc3c3RvcmFnZTc3"),
    ("gateway77network77", "Z2F0ZXdheTc3bmV0d29yazc3"),
    ("gateway77latency77", "Z2F0ZXdheTc3bGF0ZW5jeTc3"),
    ("storage77latency77", "c3RvcmFnZTc3bGF0ZW5jeTc3"),
    ("storage77buffer77", "c3RvcmFnZTc3YnVmZmVyNzc"),
    ("storage77queue77", "c3RvcmFnZTc3cXVldWU3Nw"),
    ("storage77worker77", "c3RvcmFnZTc3d29ya2VyNzc"),
    ("network77worker77", "bmV0d29yazc3d29ya2VyNzc"),
    ("network77kernel77", "bmV0d29yazc3a2VybmVsNzc"),
    ("network77signal77", "bmV0d29yazc3c2lnbmFsNzc"),
    ("network77packet77", "bmV0d29yazc3cGFja2V0Nzc"),
    ("latency77packet77", "bGF0ZW5jeTc3cGFja2V0Nzc"),
    ("latency77router77", "bGF0ZW5jeTc3cm91dGVyNzc"),
    ("latency77cluster77", "bGF0ZW5jeTc3Y2x1c3Rlcjc3"),
    ("latency77mirror77", "bGF0ZW5jeTc3bWlycm9yNzc"),
    ("buffer77mirror77", "YnVmZmVyNzdtaXJyb3I3Nw"),
    ("buffer77filter77", "YnVmZmVyNzdmaWx0ZXI3Nw"),
    ("buffer77ranking77", "YnVmZmVyNzdyYW5raW5nNzc"),
    ("buffer77encoding77", "YnVmZmVyNzdlbmNvZGluZzc3"),
    ("queue77encoding77", "cXVldWU3N2VuY29kaW5nNzc"),
    ("queue77mapping77", "cXVldWU3N21hcHBpbmc3Nw"),
    ("queue77record77", "cXVldWU3N3JlY29yZDc3"),
    ("queue77candle77", "cXVldWU3N2NhbmRsZTc3"),
    ("worker77candle77", "d29ya2VyNzdjYW5kbGU3Nw"),
    ("worker77thread77", "d29ya2VyNzd0aHJlYWQ3Nw"),
    ("worker77kitten77", "d29ya2VyNzdraXR0ZW43Nw"),
    ("worker77sitting77", "d29ya2VyNzdzaXR0aW5nNzc"),
    ("kernel77sitting77", "a2VybmVsNzdzaXR0aW5nNzc"),
    ("kernel77agent77", "a2VybmVsNzdhZ2VudDc3"),
    ("kernel77angle77", "a2VybmVsNzdhbmdsZTc3"),
    ("kernel77universe77", "a2VybmVsNzd1bml2ZXJzZTc3"),
    ("signal77universe77", "c2lnbmFsNzd1bml2ZXJzZTc3"),
    ("signal77memory77", "c2lnbmFsNzdtZW1vcnk3Nw"),
    ("signal77stream77", "c2lnbmFsNzdzdHJlYW03Nw"),
    ("signal77context77", "c2lnbmFsNzdjb250ZXh0Nzc"),
    ("packet77context77", "cGFja2V0Nzdjb250ZXh0Nzc"),
    ("packet77knowledge77", "cGFja2V0Nzdrbm93bGVkZ2U3Nw"),
    ("packet77vector77", "cGFja2V0Nzd2ZWN0b3I3Nw"),
    ("packet77processor77", "cGFja2V0Nzdwcm9jZXNzb3I3Nw"),
    ("router77processor77", "cm91dGVyNzdwcm9jZXNzb3I3Nw"),
    ("router77reasoning77", "cm91dGVyNzdyZWFzb25pbmc3Nw"),
    ("router77machine77", "cm91dGVyNzdtYWNoaW5lNzc"),
    ("router77learning77", "cm91dGVyNzdsZWFybmluZzc3"),
    ("cluster77learning77", "Y2x1c3Rlcjc3bGVhcm5pbmc3Nw"),
    ("cluster77model77", "Y2x1c3Rlcjc3bW9kZWw3Nw"),
    ("cluster77token77", "Y2x1c3Rlcjc3dG9rZW43Nw"),
    ("cluster77prompt77", "Y2x1c3Rlcjc3cHJvbXB0Nzc"),
    ("mirror77prompt77", "bWlycm9yNzdwcm9tcHQ3Nw"),
    ("mirror77session77", "bWlycm9yNzdzZXNzaW9uNzc"),
    ("mirror77library77", "bWlycm9yNzdsaWJyYXJ5Nzc"),
    ("mirror77service77", "bWlycm9yNzdzZXJ2aWNlNzc"),
    ("filter77service77", "ZmlsdGVyNzdzZXJ2aWNlNzc"),
    ("filter77gateway77", "ZmlsdGVyNzdnYXRld2F5Nzc"),
    ("filter77storage77", "ZmlsdGVyNzdzdG9yYWdlNzc"),
    ("filter77network77", "ZmlsdGVyNzduZXR3b3JrNzc"),
    ("ranking77network77", "cmFua2luZzc3bmV0d29yazc3"),
    ("ranking77latency77", "cmFua2luZzc3bGF0ZW5jeTc3"),
    ("ranking77buffer77", "cmFua2luZzc3YnVmZmVyNzc"),
    ("ranking77queue77", "cmFua2luZzc3cXVldWU3Nw"),
    ("encoding77queue77", "ZW5jb2Rpbmc3N3F1ZXVlNzc"),
    ("encoding77worker77", "ZW5jb2Rpbmc3N3dvcmtlcjc3"),
    ("encoding77kernel77", "ZW5jb2Rpbmc3N2tlcm5lbDc3"),
    ("encoding77signal77", "ZW5jb2Rpbmc3N3NpZ25hbDc3"),
    ("mapping77signal77", "bWFwcGluZzc3c2lnbmFsNzc"),
    ("mapping77packet77", "bWFwcGluZzc3cGFja2V0Nzc"),
    ("mapping77router77", "bWFwcGluZzc3cm91dGVyNzc"),
    ("mapping77cluster77", "bWFwcGluZzc3Y2x1c3Rlcjc3"),
    ("record77cluster77", "cmVjb3JkNzdjbHVzdGVyNzc"),
    ("record77mirror77", "cmVjb3JkNzdtaXJyb3I3Nw"),
    ("record77filter77", "cmVjb3JkNzdmaWx0ZXI3Nw"),
    ("record77ranking77", "cmVjb3JkNzdyYW5raW5nNzc"),
    ("candle77ranking77", "Y2FuZGxlNzdyYW5raW5nNzc"),
    ("candle77encoding77", "Y2FuZGxlNzdlbmNvZGluZzc3"),
    ("candle77mapping77", "Y2FuZGxlNzdtYXBwaW5nNzc"),
    ("candle77record77", "Y2FuZGxlNzdyZWNvcmQ3Nw"),
    ("thread77record77", "dGhyZWFkNzdyZWNvcmQ3Nw"),
    ("thread77candle77", "dGhyZWFkNzdjYW5kbGU3Nw"),
    ("thread77thread77", "dGhyZWFkNzd0aHJlYWQ3Nw"),
    ("thread77kitten77", "dGhyZWFkNzdraXR0ZW43Nw"),
    (
        "round 77: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzc6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 77: agentuniverse is a framework for multi agents",
        "cm91bmQgNzc6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 77: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzc6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 77: the processor reads the record then stops",
        "cm91bmQgNzc6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 77: a worker pulls the next task from the queue",
        "cm91bmQgNzc6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 77: signals travel through the network layer",
        "cm91bmQgNzc6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 77: the gateway routes each request by policy",
        "cm91bmQgNzc6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 77: memory grows until the buffer is full",
        "cm91bmQgNzc6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 77: the cluster mirrors every packet twice",
        "cm91bmQgNzc6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 77: ranking uses tokens learned from the corpus",
        "cm91bmQgNzc6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 77: a long session ends when the candle dies",
        "cm91bmQgNzc6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 77: encode the prompt then map the result",
        "cm91bmQgNzc6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 77: the kernel wakes the worker at dawn", "cm91bmQgNzc6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 77: service latency drops after the patch",
        "cm91bmQgNzc6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 77: the library caches every vector it sees",
        "cm91bmQgNzc6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 77: agents argue then the debate resolves",
        "cm91bmQgNzc6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 77: the filter keeps only strong matches",
        "cm91bmQgNzc6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 77: the model answers with a short reply",
        "cm91bmQgNzc6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 77: the recorder stores the reasoning trace",
        "cm91bmQgNzc6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 77: the angel watches the processor run", "cm91bmQgNzc6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 77: angle of the vector decides the match",
        "cm91bmQgNzc6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 77: the candle burns twice as long at night",
        "cm91bmQgNzc6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 77: a mirror of the universe in one line",
        "cm91bmQgNzc6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 77: the queue drains before the storm", "cm91bmQgNzc6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
