"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten62kitten62", "a2l0dGVuNjJraXR0ZW42Mg"),
    ("kitten62sitting62", "a2l0dGVuNjJzaXR0aW5nNjI"),
    ("kitten62agent62", "a2l0dGVuNjJhZ2VudDYy"),
    ("kitten62angle62", "a2l0dGVuNjJhbmdsZTYy"),
    ("sitting62angle62", "c2l0dGluZzYyYW5nbGU2Mg"),
    ("sitting62universe62", "c2l0dGluZzYydW5pdmVyc2U2Mg"),
    ("sitting62memory62", "c2l0dGluZzYybWVtb3J5NjI"),
    ("sitting62stream62", "c2l0dGluZzYyc3RyZWFtNjI"),
    ("agent62stream62", "YWdlbnQ2MnN0cmVhbTYy"),
    ("agent62context62", "YWdlbnQ2MmNvbnRleHQ2Mg"),
    ("agent62knowledge62", "YWdlbnQ2Mmtub3dsZWRnZTYy"),
    ("agent62vector62", "YWdlbnQ2MnZlY3RvcjYy"),
    ("angle62vector62", "YW5nbGU2MnZlY3RvcjYy"),
    ("angle62processor62", "YW5nbGU2MnByb2Nlc3NvcjYy"),
    ("angle62reasoning62", "YW5nbGU2MnJlYXNvbmluZzYy"),
    ("angle62machine62", "YW5nbGU2Mm1hY2hpbmU2Mg"),
    ("universe62machine62", "dW5pdmVyc2U2Mm1hY2hpbmU2Mg"),
    ("universe62learning62", "dW5pdmVyc2U2MmxlYXJuaW5nNjI"),
    ("universe62model62", "dW5pdmVyc2U2Mm1vZGVsNjI"),
    ("universe62token62", "dW5pdmVyc2U2MnRva2VuNjI"),
    ("memory62token62", "bWVtb3J5NjJ0b2tlbjYy"),
    ("memory62prompt62", "bWVtb3J5NjJwcm9tcHQ2Mg"),
    ("memory62session62", "bWVtb3J5NjJzZXNzaW9uNjI"),
    ("memory62library62", "bWVtb3J5NjJsaWJyYXJ5NjI"),
    ("stream62library62", "c3RyZWFtNjJsaWJyYXJ5NjI"),
    ("stream62service62", "c3RyZWFtNjJzZXJ2aWNlNjI"),
    ("stream62gateway62", "c3RyZWFtNjJnYXRld2F5NjI"),
    ("stream62storage62", "c3RyZWFtNjJzdG9yYWdlNjI"),
    ("context62storage62", "Y29udGV4dDYyc3RvcmFnZTYy"),
    ("context62network62", "Y29udGV4dDYybmV0d29yazYy"),
    ("context62latency62", "Y29udGV4dDYybGF0ZW5jeTYy"),
    ("context62buffer62", "Y29udGV4dDYyYnVmZmVyNjI"),
    ("knowledge62buffer62", "a25vd2xlZGdlNjJidWZmZXI2Mg"),
    ("knowledge62queue62", "a25vd2xlZGdlNjJxdWV1ZTYy"),
    ("knowledge62worker62", "a25vd2xlZGdlNjJ3b3JrZXI2Mg"),
    ("knowledge62kernel62", "a25vd2xlZGdlNjJrZXJuZWw2Mg"),
    ("vector62kernel62", "dmVjdG9yNjJrZXJuZWw2Mg"),
    ("vector62signal62", "dmVjdG9yNjJzaWduYWw2Mg"),
    ("vector62packet62", "dmVjdG9yNjJwYWNrZXQ2Mg"),
    ("vector62router62", "dmVjdG9yNjJyb3V0ZXI2Mg"),
    ("processor62router62", "cHJvY2Vzc29yNjJyb3V0ZXI2Mg"),
    ("processor62cluster62", "cHJvY2Vzc29yNjJjbHVzdGVyNjI"),
    ("processor62mirror62", "cHJvY2Vzc29yNjJtaXJyb3I2Mg"),
    ("processor62filter62", "cHJvY2Vzc29yNjJmaWx0ZXI2Mg"),
    ("reasoning62filter62", "cmVhc29uaW5nNjJmaWx0ZXI2Mg"),
    ("reasoning62ranking62", "cmVhc29uaW5nNjJyYW5raW5nNjI"),
    ("reasoning62encoding62", "cmVhc29uaW5nNjJlbmNvZGluZzYy"),
    ("reasoning62mapping62", "cmVhc29uaW5nNjJtYXBwaW5nNjI"),
    ("machine62mapping62", "bWFjaGluZTYybWFwcGluZzYy"),
    ("machine62record62", "bWFjaGluZTYycmVjb3JkNjI"),
    ("machine62candle62", "bWFjaGluZTYyY2FuZGxlNjI"),
    ("machine62thread62", "bWFjaGluZTYydGhyZWFkNjI"),
    ("learning62thread62", "bGVhcm5pbmc2MnRocmVhZDYy"),
    ("learning62kitten62", "bGVhcm5pbmc2MmtpdHRlbjYy"),
    ("learning62sitting62", "bGVhcm5pbmc2MnNpdHRpbmc2Mg"),
    ("learning62agent62", "bGVhcm5pbmc2MmFnZW50NjI"),
    ("model62agent62", "bW9kZWw2MmFnZW50NjI"),
    ("model62angle62", "bW9kZWw2MmFuZ2xlNjI"),
    ("model62universe62", "bW9kZWw2MnVuaXZlcnNlNjI"),
    ("model62memory62", "bW9kZWw2Mm1lbW9yeTYy"),
    ("token62memory62", "dG9rZW42Mm1lbW9yeTYy"),
    ("token62stream62", "dG9rZW42MnN0cmVhbTYy"),
    ("token62context62", "dG9rZW42MmNvbnRleHQ2Mg"),
    ("token62knowledge62", "dG9rZW42Mmtub3dsZWRnZTYy"),
    ("prompt62knowledge62", "cHJvbXB0NjJrbm93bGVkZ2U2Mg"),
    ("prompt62vector62", "cHJvbXB0NjJ2ZWN0b3I2Mg"),
    ("prompt62processor62", "cHJvbXB0NjJwcm9jZXNzb3I2Mg"),
    ("prompt62reasoning62", "cHJvbXB0NjJyZWFzb25pbmc2Mg"),
    ("session62reasoning62", "c2Vzc2lvbjYycmVhc29uaW5nNjI"),
    ("session62machine62", "c2Vzc2lvbjYybWFjaGluZTYy"),
    ("session62learning62", "c2Vzc2lvbjYybGVhcm5pbmc2Mg"),
    ("session62model62", "c2Vzc2lvbjYybW9kZWw2Mg"),
    ("library62model62", "bGlicmFyeTYybW9kZWw2Mg"),
    ("library62token62", "bGlicmFyeTYydG9rZW42Mg"),
    ("library62prompt62", "bGlicmFyeTYycHJvbXB0NjI"),
    ("library62session62", "bGlicmFyeTYyc2Vzc2lvbjYy"),
    ("service62session62", "c2VydmljZTYyc2Vzc2lvbjYy"),
    ("service62library62", "c2VydmljZTYybGlicmFyeTYy"),
    ("service62service62", "c2VydmljZTYyc2VydmljZTYy"),
    ("service62gateway62", "c2VydmljZTYyZ2F0ZXdheTYy"),
    ("gateway62gateway62", "Z2F0ZXdheTYyZ2F0ZXdheTYy"),
    ("gateway62storage62", "Z2F0ZXdheTYyc3RvcmFnZTYy"),
    ("gateway62network62", "Z2F0ZXdheTYybmV0d29yazYy"),
    ("gateway62latency62", "Z2F0ZXdheTYybGF0ZW5jeTYy"),
    ("storage62latency62", "c3RvcmFnZTYybGF0ZW5jeTYy"),
    ("storage62buffer62", "c3RvcmFnZTYyYnVmZmVyNjI"),
    ("storage62queue62", "c3RvcmFnZTYycXVldWU2Mg"),
    ("storage62worker62", "c3RvcmFnZTYyd29ya2VyNjI"),
    ("network62worker62", "bmV0d29yazYyd29ya2VyNjI"),
    ("network62kernel62", "bmV0d29yazYya2VybmVsNjI"),
    ("network62signal62", "bmV0d29yazYyc2lnbmFsNjI"),
    ("network62packet62", "bmV0d29yazYycGFja2V0NjI"),
    ("latency62packet62", "bGF0ZW5jeTYycGFja2V0NjI"),
    ("latency62router62", "bGF0ZW5jeTYycm91dGVyNjI"),
    ("latency62cluster62", "bGF0ZW5jeTYyY2x1c3RlcjYy"),
    ("latency62mirror62", "bGF0ZW5jeTYybWlycm9yNjI"),
    ("buffer62mirror62", "YnVmZmVyNjJtaXJyb3I2Mg"),
    ("buffer62filter62", "YnVmZmVyNjJmaWx0ZXI2Mg"),
    ("buffer62ranking62", "YnVmZmVyNjJyYW5raW5nNjI"),
    ("buffer62encoding62", "YnVmZmVyNjJlbmNvZGluZzYy"),
    ("queue62encoding62", "cXVldWU2MmVuY29kaW5nNjI"),
    ("queue62mapping62", "cXVldWU2Mm1hcHBpbmc2Mg"),
    ("queue62record62", "cXVldWU2MnJlY29yZDYy"),
    ("queue62candle62", "cXVldWU2MmNhbmRsZTYy"),
    ("worker62candle62", "d29ya2VyNjJjYW5kbGU2Mg"),
    ("worker62thread62", "d29ya2VyNjJ0aHJlYWQ2Mg"),
    ("worker62kitten62", "d29ya2VyNjJraXR0ZW42Mg"),
    ("worker62sitting62", "d29ya2VyNjJzaXR0aW5nNjI"),
    ("kernel62sitting62", "a2VybmVsNjJzaXR0aW5nNjI"),
    ("kernel62agent62", "a2VybmVsNjJhZ2VudDYy"),
    ("kernel62angle62", "a2VybmVsNjJhbmdsZTYy"),
    ("kernel62universe62", "a2VybmVsNjJ1bml2ZXJzZTYy"),
    ("signal62universe62", "c2lnbmFsNjJ1bml2ZXJzZTYy"),
    ("signal62memory62", "c2lnbmFsNjJtZW1vcnk2Mg"),
    ("signal62stream62", "c2lnbmFsNjJzdHJlYW02Mg"),
    ("signal62context62", "c2lnbmFsNjJjb250ZXh0NjI"),
    ("packet62context62", "cGFja2V0NjJjb250ZXh0NjI"),
    ("packet62knowledge62", "cGFja2V0NjJrbm93bGVkZ2U2Mg"),
    ("packet62vector62", "cGFja2V0NjJ2ZWN0b3I2Mg"),
    ("packet62processor62", "cGFja2V0NjJwcm9jZXNzb3I2Mg"),
    ("router62processor62", "cm91dGVyNjJwcm9jZXNzb3I2Mg"),
    ("router62reasoning62", "cm91dGVyNjJyZWFzb25pbmc2Mg"),
    ("router62machine62", "cm91dGVyNjJtYWNoaW5lNjI"),
    ("router62learning62", "cm91dGVyNjJsZWFybmluZzYy"),
    ("cluster62learning62", "Y2x1c3RlcjYybGVhcm5pbmc2Mg"),
    ("cluster62model62", "Y2x1c3RlcjYybW9kZWw2Mg"),
    ("cluster62token62", "Y2x1c3RlcjYydG9rZW42Mg"),
    ("cluster62prompt62", "Y2x1c3RlcjYycHJvbXB0NjI"),
    ("mirror62prompt62", "bWlycm9yNjJwcm9tcHQ2Mg"),
    ("mirror62session62", "bWlycm9yNjJzZXNzaW9uNjI"),
    ("mirror62library62", "bWlycm9yNjJsaWJyYXJ5NjI"),
    ("mirror62service62", "bWlycm9yNjJzZXJ2aWNlNjI"),
    ("filter62service62", "ZmlsdGVyNjJzZXJ2aWNlNjI"),
    ("filter62gateway62", "ZmlsdGVyNjJnYXRld2F5NjI"),
    ("filter62storage62", "ZmlsdGVyNjJzdG9yYWdlNjI"),
    ("filter62network62", "ZmlsdGVyNjJuZXR3b3JrNjI"),
    ("ranking62network62", "cmFua2luZzYybmV0d29yazYy"),
    ("ranking62latency62", "cmFua2luZzYybGF0ZW5jeTYy"),
    ("ranking62buffer62", "cmFua2luZzYyYnVmZmVyNjI"),
    ("ranking62queue62", "cmFua2luZzYycXVldWU2Mg"),
    ("encoding62queue62", "ZW5jb2Rpbmc2MnF1ZXVlNjI"),
    ("encoding62worker62", "ZW5jb2Rpbmc2MndvcmtlcjYy"),
    ("encoding62kernel62", "ZW5jb2Rpbmc2Mmtlcm5lbDYy"),
    ("encoding62signal62", "ZW5jb2Rpbmc2MnNpZ25hbDYy"),
    ("mapping62signal62", "bWFwcGluZzYyc2lnbmFsNjI"),
    ("mapping62packet62", "bWFwcGluZzYycGFja2V0NjI"),
    ("mapping62router62", "bWFwcGluZzYycm91dGVyNjI"),
    ("mapping62cluster62", "bWFwcGluZzYyY2x1c3RlcjYy"),
    ("record62cluster62", "cmVjb3JkNjJjbHVzdGVyNjI"),
    ("record62mirror62", "cmVjb3JkNjJtaXJyb3I2Mg"),
    ("record62filter62", "cmVjb3JkNjJmaWx0ZXI2Mg"),
    ("record62ranking62", "cmVjb3JkNjJyYW5raW5nNjI"),
    ("candle62ranking62", "Y2FuZGxlNjJyYW5raW5nNjI"),
    ("candle62encoding62", "Y2FuZGxlNjJlbmNvZGluZzYy"),
    ("candle62mapping62", "Y2FuZGxlNjJtYXBwaW5nNjI"),
    ("candle62record62", "Y2FuZGxlNjJyZWNvcmQ2Mg"),
    ("thread62record62", "dGhyZWFkNjJyZWNvcmQ2Mg"),
    ("thread62candle62", "dGhyZWFkNjJjYW5kbGU2Mg"),
    ("thread62thread62", "dGhyZWFkNjJ0aHJlYWQ2Mg"),
    ("thread62kitten62", "dGhyZWFkNjJraXR0ZW42Mg"),
    (
        "round 62: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNjI6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 62: agentuniverse is a framework for multi agents",
        "cm91bmQgNjI6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 62: knowledge stored as vectors enables retrieval",
        "cm91bmQgNjI6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 62: the processor reads the record then stops",
        "cm91bmQgNjI6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 62: a worker pulls the next task from the queue",
        "cm91bmQgNjI6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 62: signals travel through the network layer",
        "cm91bmQgNjI6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 62: the gateway routes each request by policy",
        "cm91bmQgNjI6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 62: memory grows until the buffer is full",
        "cm91bmQgNjI6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 62: the cluster mirrors every packet twice",
        "cm91bmQgNjI6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 62: ranking uses tokens learned from the corpus",
        "cm91bmQgNjI6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 62: a long session ends when the candle dies",
        "cm91bmQgNjI6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 62: encode the prompt then map the result",
        "cm91bmQgNjI6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 62: the kernel wakes the worker at dawn", "cm91bmQgNjI6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 62: service latency drops after the patch",
        "cm91bmQgNjI6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 62: the library caches every vector it sees",
        "cm91bmQgNjI6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 62: agents argue then the debate resolves",
        "cm91bmQgNjI6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 62: the filter keeps only strong matches",
        "cm91bmQgNjI6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 62: the model answers with a short reply",
        "cm91bmQgNjI6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 62: the recorder stores the reasoning trace",
        "cm91bmQgNjI6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 62: the angel watches the processor run", "cm91bmQgNjI6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 62: angle of the vector decides the match",
        "cm91bmQgNjI6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 62: the candle burns twice as long at night",
        "cm91bmQgNjI6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 62: a mirror of the universe in one line",
        "cm91bmQgNjI6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 62: the queue drains before the storm", "cm91bmQgNjI6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
