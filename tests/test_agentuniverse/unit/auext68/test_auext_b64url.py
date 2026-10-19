"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten68kitten68", "a2l0dGVuNjhraXR0ZW42OA"),
    ("kitten68sitting68", "a2l0dGVuNjhzaXR0aW5nNjg"),
    ("kitten68agent68", "a2l0dGVuNjhhZ2VudDY4"),
    ("kitten68angle68", "a2l0dGVuNjhhbmdsZTY4"),
    ("sitting68angle68", "c2l0dGluZzY4YW5nbGU2OA"),
    ("sitting68universe68", "c2l0dGluZzY4dW5pdmVyc2U2OA"),
    ("sitting68memory68", "c2l0dGluZzY4bWVtb3J5Njg"),
    ("sitting68stream68", "c2l0dGluZzY4c3RyZWFtNjg"),
    ("agent68stream68", "YWdlbnQ2OHN0cmVhbTY4"),
    ("agent68context68", "YWdlbnQ2OGNvbnRleHQ2OA"),
    ("agent68knowledge68", "YWdlbnQ2OGtub3dsZWRnZTY4"),
    ("agent68vector68", "YWdlbnQ2OHZlY3RvcjY4"),
    ("angle68vector68", "YW5nbGU2OHZlY3RvcjY4"),
    ("angle68processor68", "YW5nbGU2OHByb2Nlc3NvcjY4"),
    ("angle68reasoning68", "YW5nbGU2OHJlYXNvbmluZzY4"),
    ("angle68machine68", "YW5nbGU2OG1hY2hpbmU2OA"),
    ("universe68machine68", "dW5pdmVyc2U2OG1hY2hpbmU2OA"),
    ("universe68learning68", "dW5pdmVyc2U2OGxlYXJuaW5nNjg"),
    ("universe68model68", "dW5pdmVyc2U2OG1vZGVsNjg"),
    ("universe68token68", "dW5pdmVyc2U2OHRva2VuNjg"),
    ("memory68token68", "bWVtb3J5Njh0b2tlbjY4"),
    ("memory68prompt68", "bWVtb3J5Njhwcm9tcHQ2OA"),
    ("memory68session68", "bWVtb3J5NjhzZXNzaW9uNjg"),
    ("memory68library68", "bWVtb3J5NjhsaWJyYXJ5Njg"),
    ("stream68library68", "c3RyZWFtNjhsaWJyYXJ5Njg"),
    ("stream68service68", "c3RyZWFtNjhzZXJ2aWNlNjg"),
    ("stream68gateway68", "c3RyZWFtNjhnYXRld2F5Njg"),
    ("stream68storage68", "c3RyZWFtNjhzdG9yYWdlNjg"),
    ("context68storage68", "Y29udGV4dDY4c3RvcmFnZTY4"),
    ("context68network68", "Y29udGV4dDY4bmV0d29yazY4"),
    ("context68latency68", "Y29udGV4dDY4bGF0ZW5jeTY4"),
    ("context68buffer68", "Y29udGV4dDY4YnVmZmVyNjg"),
    ("knowledge68buffer68", "a25vd2xlZGdlNjhidWZmZXI2OA"),
    ("knowledge68queue68", "a25vd2xlZGdlNjhxdWV1ZTY4"),
    ("knowledge68worker68", "a25vd2xlZGdlNjh3b3JrZXI2OA"),
    ("knowledge68kernel68", "a25vd2xlZGdlNjhrZXJuZWw2OA"),
    ("vector68kernel68", "dmVjdG9yNjhrZXJuZWw2OA"),
    ("vector68signal68", "dmVjdG9yNjhzaWduYWw2OA"),
    ("vector68packet68", "dmVjdG9yNjhwYWNrZXQ2OA"),
    ("vector68router68", "dmVjdG9yNjhyb3V0ZXI2OA"),
    ("processor68router68", "cHJvY2Vzc29yNjhyb3V0ZXI2OA"),
    ("processor68cluster68", "cHJvY2Vzc29yNjhjbHVzdGVyNjg"),
    ("processor68mirror68", "cHJvY2Vzc29yNjhtaXJyb3I2OA"),
    ("processor68filter68", "cHJvY2Vzc29yNjhmaWx0ZXI2OA"),
    ("reasoning68filter68", "cmVhc29uaW5nNjhmaWx0ZXI2OA"),
    ("reasoning68ranking68", "cmVhc29uaW5nNjhyYW5raW5nNjg"),
    ("reasoning68encoding68", "cmVhc29uaW5nNjhlbmNvZGluZzY4"),
    ("reasoning68mapping68", "cmVhc29uaW5nNjhtYXBwaW5nNjg"),
    ("machine68mapping68", "bWFjaGluZTY4bWFwcGluZzY4"),
    ("machine68record68", "bWFjaGluZTY4cmVjb3JkNjg"),
    ("machine68candle68", "bWFjaGluZTY4Y2FuZGxlNjg"),
    ("machine68thread68", "bWFjaGluZTY4dGhyZWFkNjg"),
    ("learning68thread68", "bGVhcm5pbmc2OHRocmVhZDY4"),
    ("learning68kitten68", "bGVhcm5pbmc2OGtpdHRlbjY4"),
    ("learning68sitting68", "bGVhcm5pbmc2OHNpdHRpbmc2OA"),
    ("learning68agent68", "bGVhcm5pbmc2OGFnZW50Njg"),
    ("model68agent68", "bW9kZWw2OGFnZW50Njg"),
    ("model68angle68", "bW9kZWw2OGFuZ2xlNjg"),
    ("model68universe68", "bW9kZWw2OHVuaXZlcnNlNjg"),
    ("model68memory68", "bW9kZWw2OG1lbW9yeTY4"),
    ("token68memory68", "dG9rZW42OG1lbW9yeTY4"),
    ("token68stream68", "dG9rZW42OHN0cmVhbTY4"),
    ("token68context68", "dG9rZW42OGNvbnRleHQ2OA"),
    ("token68knowledge68", "dG9rZW42OGtub3dsZWRnZTY4"),
    ("prompt68knowledge68", "cHJvbXB0Njhrbm93bGVkZ2U2OA"),
    ("prompt68vector68", "cHJvbXB0Njh2ZWN0b3I2OA"),
    ("prompt68processor68", "cHJvbXB0Njhwcm9jZXNzb3I2OA"),
    ("prompt68reasoning68", "cHJvbXB0NjhyZWFzb25pbmc2OA"),
    ("session68reasoning68", "c2Vzc2lvbjY4cmVhc29uaW5nNjg"),
    ("session68machine68", "c2Vzc2lvbjY4bWFjaGluZTY4"),
    ("session68learning68", "c2Vzc2lvbjY4bGVhcm5pbmc2OA"),
    ("session68model68", "c2Vzc2lvbjY4bW9kZWw2OA"),
    ("library68model68", "bGlicmFyeTY4bW9kZWw2OA"),
    ("library68token68", "bGlicmFyeTY4dG9rZW42OA"),
    ("library68prompt68", "bGlicmFyeTY4cHJvbXB0Njg"),
    ("library68session68", "bGlicmFyeTY4c2Vzc2lvbjY4"),
    ("service68session68", "c2VydmljZTY4c2Vzc2lvbjY4"),
    ("service68library68", "c2VydmljZTY4bGlicmFyeTY4"),
    ("service68service68", "c2VydmljZTY4c2VydmljZTY4"),
    ("service68gateway68", "c2VydmljZTY4Z2F0ZXdheTY4"),
    ("gateway68gateway68", "Z2F0ZXdheTY4Z2F0ZXdheTY4"),
    ("gateway68storage68", "Z2F0ZXdheTY4c3RvcmFnZTY4"),
    ("gateway68network68", "Z2F0ZXdheTY4bmV0d29yazY4"),
    ("gateway68latency68", "Z2F0ZXdheTY4bGF0ZW5jeTY4"),
    ("storage68latency68", "c3RvcmFnZTY4bGF0ZW5jeTY4"),
    ("storage68buffer68", "c3RvcmFnZTY4YnVmZmVyNjg"),
    ("storage68queue68", "c3RvcmFnZTY4cXVldWU2OA"),
    ("storage68worker68", "c3RvcmFnZTY4d29ya2VyNjg"),
    ("network68worker68", "bmV0d29yazY4d29ya2VyNjg"),
    ("network68kernel68", "bmV0d29yazY4a2VybmVsNjg"),
    ("network68signal68", "bmV0d29yazY4c2lnbmFsNjg"),
    ("network68packet68", "bmV0d29yazY4cGFja2V0Njg"),
    ("latency68packet68", "bGF0ZW5jeTY4cGFja2V0Njg"),
    ("latency68router68", "bGF0ZW5jeTY4cm91dGVyNjg"),
    ("latency68cluster68", "bGF0ZW5jeTY4Y2x1c3RlcjY4"),
    ("latency68mirror68", "bGF0ZW5jeTY4bWlycm9yNjg"),
    ("buffer68mirror68", "YnVmZmVyNjhtaXJyb3I2OA"),
    ("buffer68filter68", "YnVmZmVyNjhmaWx0ZXI2OA"),
    ("buffer68ranking68", "YnVmZmVyNjhyYW5raW5nNjg"),
    ("buffer68encoding68", "YnVmZmVyNjhlbmNvZGluZzY4"),
    ("queue68encoding68", "cXVldWU2OGVuY29kaW5nNjg"),
    ("queue68mapping68", "cXVldWU2OG1hcHBpbmc2OA"),
    ("queue68record68", "cXVldWU2OHJlY29yZDY4"),
    ("queue68candle68", "cXVldWU2OGNhbmRsZTY4"),
    ("worker68candle68", "d29ya2VyNjhjYW5kbGU2OA"),
    ("worker68thread68", "d29ya2VyNjh0aHJlYWQ2OA"),
    ("worker68kitten68", "d29ya2VyNjhraXR0ZW42OA"),
    ("worker68sitting68", "d29ya2VyNjhzaXR0aW5nNjg"),
    ("kernel68sitting68", "a2VybmVsNjhzaXR0aW5nNjg"),
    ("kernel68agent68", "a2VybmVsNjhhZ2VudDY4"),
    ("kernel68angle68", "a2VybmVsNjhhbmdsZTY4"),
    ("kernel68universe68", "a2VybmVsNjh1bml2ZXJzZTY4"),
    ("signal68universe68", "c2lnbmFsNjh1bml2ZXJzZTY4"),
    ("signal68memory68", "c2lnbmFsNjhtZW1vcnk2OA"),
    ("signal68stream68", "c2lnbmFsNjhzdHJlYW02OA"),
    ("signal68context68", "c2lnbmFsNjhjb250ZXh0Njg"),
    ("packet68context68", "cGFja2V0Njhjb250ZXh0Njg"),
    ("packet68knowledge68", "cGFja2V0Njhrbm93bGVkZ2U2OA"),
    ("packet68vector68", "cGFja2V0Njh2ZWN0b3I2OA"),
    ("packet68processor68", "cGFja2V0Njhwcm9jZXNzb3I2OA"),
    ("router68processor68", "cm91dGVyNjhwcm9jZXNzb3I2OA"),
    ("router68reasoning68", "cm91dGVyNjhyZWFzb25pbmc2OA"),
    ("router68machine68", "cm91dGVyNjhtYWNoaW5lNjg"),
    ("router68learning68", "cm91dGVyNjhsZWFybmluZzY4"),
    ("cluster68learning68", "Y2x1c3RlcjY4bGVhcm5pbmc2OA"),
    ("cluster68model68", "Y2x1c3RlcjY4bW9kZWw2OA"),
    ("cluster68token68", "Y2x1c3RlcjY4dG9rZW42OA"),
    ("cluster68prompt68", "Y2x1c3RlcjY4cHJvbXB0Njg"),
    ("mirror68prompt68", "bWlycm9yNjhwcm9tcHQ2OA"),
    ("mirror68session68", "bWlycm9yNjhzZXNzaW9uNjg"),
    ("mirror68library68", "bWlycm9yNjhsaWJyYXJ5Njg"),
    ("mirror68service68", "bWlycm9yNjhzZXJ2aWNlNjg"),
    ("filter68service68", "ZmlsdGVyNjhzZXJ2aWNlNjg"),
    ("filter68gateway68", "ZmlsdGVyNjhnYXRld2F5Njg"),
    ("filter68storage68", "ZmlsdGVyNjhzdG9yYWdlNjg"),
    ("filter68network68", "ZmlsdGVyNjhuZXR3b3JrNjg"),
    ("ranking68network68", "cmFua2luZzY4bmV0d29yazY4"),
    ("ranking68latency68", "cmFua2luZzY4bGF0ZW5jeTY4"),
    ("ranking68buffer68", "cmFua2luZzY4YnVmZmVyNjg"),
    ("ranking68queue68", "cmFua2luZzY4cXVldWU2OA"),
    ("encoding68queue68", "ZW5jb2Rpbmc2OHF1ZXVlNjg"),
    ("encoding68worker68", "ZW5jb2Rpbmc2OHdvcmtlcjY4"),
    ("encoding68kernel68", "ZW5jb2Rpbmc2OGtlcm5lbDY4"),
    ("encoding68signal68", "ZW5jb2Rpbmc2OHNpZ25hbDY4"),
    ("mapping68signal68", "bWFwcGluZzY4c2lnbmFsNjg"),
    ("mapping68packet68", "bWFwcGluZzY4cGFja2V0Njg"),
    ("mapping68router68", "bWFwcGluZzY4cm91dGVyNjg"),
    ("mapping68cluster68", "bWFwcGluZzY4Y2x1c3RlcjY4"),
    ("record68cluster68", "cmVjb3JkNjhjbHVzdGVyNjg"),
    ("record68mirror68", "cmVjb3JkNjhtaXJyb3I2OA"),
    ("record68filter68", "cmVjb3JkNjhmaWx0ZXI2OA"),
    ("record68ranking68", "cmVjb3JkNjhyYW5raW5nNjg"),
    ("candle68ranking68", "Y2FuZGxlNjhyYW5raW5nNjg"),
    ("candle68encoding68", "Y2FuZGxlNjhlbmNvZGluZzY4"),
    ("candle68mapping68", "Y2FuZGxlNjhtYXBwaW5nNjg"),
    ("candle68record68", "Y2FuZGxlNjhyZWNvcmQ2OA"),
    ("thread68record68", "dGhyZWFkNjhyZWNvcmQ2OA"),
    ("thread68candle68", "dGhyZWFkNjhjYW5kbGU2OA"),
    ("thread68thread68", "dGhyZWFkNjh0aHJlYWQ2OA"),
    ("thread68kitten68", "dGhyZWFkNjhraXR0ZW42OA"),
    (
        "round 68: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNjg6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 68: agentuniverse is a framework for multi agents",
        "cm91bmQgNjg6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 68: knowledge stored as vectors enables retrieval",
        "cm91bmQgNjg6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 68: the processor reads the record then stops",
        "cm91bmQgNjg6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 68: a worker pulls the next task from the queue",
        "cm91bmQgNjg6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 68: signals travel through the network layer",
        "cm91bmQgNjg6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 68: the gateway routes each request by policy",
        "cm91bmQgNjg6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 68: memory grows until the buffer is full",
        "cm91bmQgNjg6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 68: the cluster mirrors every packet twice",
        "cm91bmQgNjg6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 68: ranking uses tokens learned from the corpus",
        "cm91bmQgNjg6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 68: a long session ends when the candle dies",
        "cm91bmQgNjg6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 68: encode the prompt then map the result",
        "cm91bmQgNjg6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 68: the kernel wakes the worker at dawn", "cm91bmQgNjg6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 68: service latency drops after the patch",
        "cm91bmQgNjg6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 68: the library caches every vector it sees",
        "cm91bmQgNjg6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 68: agents argue then the debate resolves",
        "cm91bmQgNjg6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 68: the filter keeps only strong matches",
        "cm91bmQgNjg6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 68: the model answers with a short reply",
        "cm91bmQgNjg6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 68: the recorder stores the reasoning trace",
        "cm91bmQgNjg6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 68: the angel watches the processor run", "cm91bmQgNjg6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 68: angle of the vector decides the match",
        "cm91bmQgNjg6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 68: the candle burns twice as long at night",
        "cm91bmQgNjg6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 68: a mirror of the universe in one line",
        "cm91bmQgNjg6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 68: the queue drains before the storm", "cm91bmQgNjg6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
