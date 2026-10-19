"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten7kitten7", "a2l0dGVuN2tpdHRlbjc"),
    ("kitten7sitting7", "a2l0dGVuN3NpdHRpbmc3"),
    ("kitten7agent7", "a2l0dGVuN2FnZW50Nw"),
    ("kitten7angle7", "a2l0dGVuN2FuZ2xlNw"),
    ("sitting7angle7", "c2l0dGluZzdhbmdsZTc"),
    ("sitting7universe7", "c2l0dGluZzd1bml2ZXJzZTc"),
    ("sitting7memory7", "c2l0dGluZzdtZW1vcnk3"),
    ("sitting7stream7", "c2l0dGluZzdzdHJlYW03"),
    ("agent7stream7", "YWdlbnQ3c3RyZWFtNw"),
    ("agent7context7", "YWdlbnQ3Y29udGV4dDc"),
    ("agent7knowledge7", "YWdlbnQ3a25vd2xlZGdlNw"),
    ("agent7vector7", "YWdlbnQ3dmVjdG9yNw"),
    ("angle7vector7", "YW5nbGU3dmVjdG9yNw"),
    ("angle7processor7", "YW5nbGU3cHJvY2Vzc29yNw"),
    ("angle7reasoning7", "YW5nbGU3cmVhc29uaW5nNw"),
    ("angle7machine7", "YW5nbGU3bWFjaGluZTc"),
    ("universe7machine7", "dW5pdmVyc2U3bWFjaGluZTc"),
    ("universe7learning7", "dW5pdmVyc2U3bGVhcm5pbmc3"),
    ("universe7model7", "dW5pdmVyc2U3bW9kZWw3"),
    ("universe7token7", "dW5pdmVyc2U3dG9rZW43"),
    ("memory7token7", "bWVtb3J5N3Rva2VuNw"),
    ("memory7prompt7", "bWVtb3J5N3Byb21wdDc"),
    ("memory7session7", "bWVtb3J5N3Nlc3Npb243"),
    ("memory7library7", "bWVtb3J5N2xpYnJhcnk3"),
    ("stream7library7", "c3RyZWFtN2xpYnJhcnk3"),
    ("stream7service7", "c3RyZWFtN3NlcnZpY2U3"),
    ("stream7gateway7", "c3RyZWFtN2dhdGV3YXk3"),
    ("stream7storage7", "c3RyZWFtN3N0b3JhZ2U3"),
    ("context7storage7", "Y29udGV4dDdzdG9yYWdlNw"),
    ("context7network7", "Y29udGV4dDduZXR3b3JrNw"),
    ("context7latency7", "Y29udGV4dDdsYXRlbmN5Nw"),
    ("context7buffer7", "Y29udGV4dDdidWZmZXI3"),
    ("knowledge7buffer7", "a25vd2xlZGdlN2J1ZmZlcjc"),
    ("knowledge7queue7", "a25vd2xlZGdlN3F1ZXVlNw"),
    ("knowledge7worker7", "a25vd2xlZGdlN3dvcmtlcjc"),
    ("knowledge7kernel7", "a25vd2xlZGdlN2tlcm5lbDc"),
    ("vector7kernel7", "dmVjdG9yN2tlcm5lbDc"),
    ("vector7signal7", "dmVjdG9yN3NpZ25hbDc"),
    ("vector7packet7", "dmVjdG9yN3BhY2tldDc"),
    ("vector7router7", "dmVjdG9yN3JvdXRlcjc"),
    ("processor7router7", "cHJvY2Vzc29yN3JvdXRlcjc"),
    ("processor7cluster7", "cHJvY2Vzc29yN2NsdXN0ZXI3"),
    ("processor7mirror7", "cHJvY2Vzc29yN21pcnJvcjc"),
    ("processor7filter7", "cHJvY2Vzc29yN2ZpbHRlcjc"),
    ("reasoning7filter7", "cmVhc29uaW5nN2ZpbHRlcjc"),
    ("reasoning7ranking7", "cmVhc29uaW5nN3Jhbmtpbmc3"),
    ("reasoning7encoding7", "cmVhc29uaW5nN2VuY29kaW5nNw"),
    ("reasoning7mapping7", "cmVhc29uaW5nN21hcHBpbmc3"),
    ("machine7mapping7", "bWFjaGluZTdtYXBwaW5nNw"),
    ("machine7record7", "bWFjaGluZTdyZWNvcmQ3"),
    ("machine7candle7", "bWFjaGluZTdjYW5kbGU3"),
    ("machine7thread7", "bWFjaGluZTd0aHJlYWQ3"),
    ("learning7thread7", "bGVhcm5pbmc3dGhyZWFkNw"),
    ("learning7kitten7", "bGVhcm5pbmc3a2l0dGVuNw"),
    ("learning7sitting7", "bGVhcm5pbmc3c2l0dGluZzc"),
    ("learning7agent7", "bGVhcm5pbmc3YWdlbnQ3"),
    ("model7agent7", "bW9kZWw3YWdlbnQ3"),
    ("model7angle7", "bW9kZWw3YW5nbGU3"),
    ("model7universe7", "bW9kZWw3dW5pdmVyc2U3"),
    ("model7memory7", "bW9kZWw3bWVtb3J5Nw"),
    ("token7memory7", "dG9rZW43bWVtb3J5Nw"),
    ("token7stream7", "dG9rZW43c3RyZWFtNw"),
    ("token7context7", "dG9rZW43Y29udGV4dDc"),
    ("token7knowledge7", "dG9rZW43a25vd2xlZGdlNw"),
    ("prompt7knowledge7", "cHJvbXB0N2tub3dsZWRnZTc"),
    ("prompt7vector7", "cHJvbXB0N3ZlY3Rvcjc"),
    ("prompt7processor7", "cHJvbXB0N3Byb2Nlc3Nvcjc"),
    ("prompt7reasoning7", "cHJvbXB0N3JlYXNvbmluZzc"),
    ("session7reasoning7", "c2Vzc2lvbjdyZWFzb25pbmc3"),
    ("session7machine7", "c2Vzc2lvbjdtYWNoaW5lNw"),
    ("session7learning7", "c2Vzc2lvbjdsZWFybmluZzc"),
    ("session7model7", "c2Vzc2lvbjdtb2RlbDc"),
    ("library7model7", "bGlicmFyeTdtb2RlbDc"),
    ("library7token7", "bGlicmFyeTd0b2tlbjc"),
    ("library7prompt7", "bGlicmFyeTdwcm9tcHQ3"),
    ("library7session7", "bGlicmFyeTdzZXNzaW9uNw"),
    ("service7session7", "c2VydmljZTdzZXNzaW9uNw"),
    ("service7library7", "c2VydmljZTdsaWJyYXJ5Nw"),
    ("service7service7", "c2VydmljZTdzZXJ2aWNlNw"),
    ("service7gateway7", "c2VydmljZTdnYXRld2F5Nw"),
    ("gateway7gateway7", "Z2F0ZXdheTdnYXRld2F5Nw"),
    ("gateway7storage7", "Z2F0ZXdheTdzdG9yYWdlNw"),
    ("gateway7network7", "Z2F0ZXdheTduZXR3b3JrNw"),
    ("gateway7latency7", "Z2F0ZXdheTdsYXRlbmN5Nw"),
    ("storage7latency7", "c3RvcmFnZTdsYXRlbmN5Nw"),
    ("storage7buffer7", "c3RvcmFnZTdidWZmZXI3"),
    ("storage7queue7", "c3RvcmFnZTdxdWV1ZTc"),
    ("storage7worker7", "c3RvcmFnZTd3b3JrZXI3"),
    ("network7worker7", "bmV0d29yazd3b3JrZXI3"),
    ("network7kernel7", "bmV0d29yazdrZXJuZWw3"),
    ("network7signal7", "bmV0d29yazdzaWduYWw3"),
    ("network7packet7", "bmV0d29yazdwYWNrZXQ3"),
    ("latency7packet7", "bGF0ZW5jeTdwYWNrZXQ3"),
    ("latency7router7", "bGF0ZW5jeTdyb3V0ZXI3"),
    ("latency7cluster7", "bGF0ZW5jeTdjbHVzdGVyNw"),
    ("latency7mirror7", "bGF0ZW5jeTdtaXJyb3I3"),
    ("buffer7mirror7", "YnVmZmVyN21pcnJvcjc"),
    ("buffer7filter7", "YnVmZmVyN2ZpbHRlcjc"),
    ("buffer7ranking7", "YnVmZmVyN3Jhbmtpbmc3"),
    ("buffer7encoding7", "YnVmZmVyN2VuY29kaW5nNw"),
    ("queue7encoding7", "cXVldWU3ZW5jb2Rpbmc3"),
    ("queue7mapping7", "cXVldWU3bWFwcGluZzc"),
    ("queue7record7", "cXVldWU3cmVjb3JkNw"),
    ("queue7candle7", "cXVldWU3Y2FuZGxlNw"),
    ("worker7candle7", "d29ya2VyN2NhbmRsZTc"),
    ("worker7thread7", "d29ya2VyN3RocmVhZDc"),
    ("worker7kitten7", "d29ya2VyN2tpdHRlbjc"),
    ("worker7sitting7", "d29ya2VyN3NpdHRpbmc3"),
    ("kernel7sitting7", "a2VybmVsN3NpdHRpbmc3"),
    ("kernel7agent7", "a2VybmVsN2FnZW50Nw"),
    ("kernel7angle7", "a2VybmVsN2FuZ2xlNw"),
    ("kernel7universe7", "a2VybmVsN3VuaXZlcnNlNw"),
    ("signal7universe7", "c2lnbmFsN3VuaXZlcnNlNw"),
    ("signal7memory7", "c2lnbmFsN21lbW9yeTc"),
    ("signal7stream7", "c2lnbmFsN3N0cmVhbTc"),
    ("signal7context7", "c2lnbmFsN2NvbnRleHQ3"),
    ("packet7context7", "cGFja2V0N2NvbnRleHQ3"),
    ("packet7knowledge7", "cGFja2V0N2tub3dsZWRnZTc"),
    ("packet7vector7", "cGFja2V0N3ZlY3Rvcjc"),
    ("packet7processor7", "cGFja2V0N3Byb2Nlc3Nvcjc"),
    ("router7processor7", "cm91dGVyN3Byb2Nlc3Nvcjc"),
    ("router7reasoning7", "cm91dGVyN3JlYXNvbmluZzc"),
    ("router7machine7", "cm91dGVyN21hY2hpbmU3"),
    ("router7learning7", "cm91dGVyN2xlYXJuaW5nNw"),
    ("cluster7learning7", "Y2x1c3RlcjdsZWFybmluZzc"),
    ("cluster7model7", "Y2x1c3Rlcjdtb2RlbDc"),
    ("cluster7token7", "Y2x1c3Rlcjd0b2tlbjc"),
    ("cluster7prompt7", "Y2x1c3Rlcjdwcm9tcHQ3"),
    ("mirror7prompt7", "bWlycm9yN3Byb21wdDc"),
    ("mirror7session7", "bWlycm9yN3Nlc3Npb243"),
    ("mirror7library7", "bWlycm9yN2xpYnJhcnk3"),
    ("mirror7service7", "bWlycm9yN3NlcnZpY2U3"),
    ("filter7service7", "ZmlsdGVyN3NlcnZpY2U3"),
    ("filter7gateway7", "ZmlsdGVyN2dhdGV3YXk3"),
    ("filter7storage7", "ZmlsdGVyN3N0b3JhZ2U3"),
    ("filter7network7", "ZmlsdGVyN25ldHdvcms3"),
    ("ranking7network7", "cmFua2luZzduZXR3b3JrNw"),
    ("ranking7latency7", "cmFua2luZzdsYXRlbmN5Nw"),
    ("ranking7buffer7", "cmFua2luZzdidWZmZXI3"),
    ("ranking7queue7", "cmFua2luZzdxdWV1ZTc"),
    ("encoding7queue7", "ZW5jb2Rpbmc3cXVldWU3"),
    ("encoding7worker7", "ZW5jb2Rpbmc3d29ya2VyNw"),
    ("encoding7kernel7", "ZW5jb2Rpbmc3a2VybmVsNw"),
    ("encoding7signal7", "ZW5jb2Rpbmc3c2lnbmFsNw"),
    ("mapping7signal7", "bWFwcGluZzdzaWduYWw3"),
    ("mapping7packet7", "bWFwcGluZzdwYWNrZXQ3"),
    ("mapping7router7", "bWFwcGluZzdyb3V0ZXI3"),
    ("mapping7cluster7", "bWFwcGluZzdjbHVzdGVyNw"),
    ("record7cluster7", "cmVjb3JkN2NsdXN0ZXI3"),
    ("record7mirror7", "cmVjb3JkN21pcnJvcjc"),
    ("record7filter7", "cmVjb3JkN2ZpbHRlcjc"),
    ("record7ranking7", "cmVjb3JkN3Jhbmtpbmc3"),
    ("candle7ranking7", "Y2FuZGxlN3Jhbmtpbmc3"),
    ("candle7encoding7", "Y2FuZGxlN2VuY29kaW5nNw"),
    ("candle7mapping7", "Y2FuZGxlN21hcHBpbmc3"),
    ("candle7record7", "Y2FuZGxlN3JlY29yZDc"),
    ("thread7record7", "dGhyZWFkN3JlY29yZDc"),
    ("thread7candle7", "dGhyZWFkN2NhbmRsZTc"),
    ("thread7thread7", "dGhyZWFkN3RocmVhZDc"),
    ("thread7kitten7", "dGhyZWFkN2tpdHRlbjc"),
    (
        "round 7: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzogdGhlIHF1aWNrIGJyb3duIGZveCBqdW1wcyBvdmVyIHRoZSBsYXp5IGRvZw",
    ),
    (
        "round 7: agentuniverse is a framework for multi agents",
        "cm91bmQgNzogYWdlbnR1bml2ZXJzZSBpcyBhIGZyYW1ld29yayBmb3IgbXVsdGkgYWdlbnRz",
    ),
    (
        "round 7: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzoga25vd2xlZGdlIHN0b3JlZCBhcyB2ZWN0b3JzIGVuYWJsZXMgcmV0cmlldmFs",
    ),
    (
        "round 7: the processor reads the record then stops",
        "cm91bmQgNzogdGhlIHByb2Nlc3NvciByZWFkcyB0aGUgcmVjb3JkIHRoZW4gc3RvcHM",
    ),
    (
        "round 7: a worker pulls the next task from the queue",
        "cm91bmQgNzogYSB3b3JrZXIgcHVsbHMgdGhlIG5leHQgdGFzayBmcm9tIHRoZSBxdWV1ZQ",
    ),
    (
        "round 7: signals travel through the network layer",
        "cm91bmQgNzogc2lnbmFscyB0cmF2ZWwgdGhyb3VnaCB0aGUgbmV0d29yayBsYXllcg",
    ),
    (
        "round 7: the gateway routes each request by policy",
        "cm91bmQgNzogdGhlIGdhdGV3YXkgcm91dGVzIGVhY2ggcmVxdWVzdCBieSBwb2xpY3k",
    ),
    (
        "round 7: memory grows until the buffer is full",
        "cm91bmQgNzogbWVtb3J5IGdyb3dzIHVudGlsIHRoZSBidWZmZXIgaXMgZnVsbA",
    ),
    (
        "round 7: the cluster mirrors every packet twice",
        "cm91bmQgNzogdGhlIGNsdXN0ZXIgbWlycm9ycyBldmVyeSBwYWNrZXQgdHdpY2U",
    ),
    (
        "round 7: ranking uses tokens learned from the corpus",
        "cm91bmQgNzogcmFua2luZyB1c2VzIHRva2VucyBsZWFybmVkIGZyb20gdGhlIGNvcnB1cw",
    ),
    (
        "round 7: a long session ends when the candle dies",
        "cm91bmQgNzogYSBsb25nIHNlc3Npb24gZW5kcyB3aGVuIHRoZSBjYW5kbGUgZGllcw",
    ),
    (
        "round 7: encode the prompt then map the result",
        "cm91bmQgNzogZW5jb2RlIHRoZSBwcm9tcHQgdGhlbiBtYXAgdGhlIHJlc3VsdA",
    ),
    ("round 7: the kernel wakes the worker at dawn", "cm91bmQgNzogdGhlIGtlcm5lbCB3YWtlcyB0aGUgd29ya2VyIGF0IGRhd24"),
    (
        "round 7: service latency drops after the patch",
        "cm91bmQgNzogc2VydmljZSBsYXRlbmN5IGRyb3BzIGFmdGVyIHRoZSBwYXRjaA",
    ),
    (
        "round 7: the library caches every vector it sees",
        "cm91bmQgNzogdGhlIGxpYnJhcnkgY2FjaGVzIGV2ZXJ5IHZlY3RvciBpdCBzZWVz",
    ),
    (
        "round 7: agents argue then the debate resolves",
        "cm91bmQgNzogYWdlbnRzIGFyZ3VlIHRoZW4gdGhlIGRlYmF0ZSByZXNvbHZlcw",
    ),
    ("round 7: the filter keeps only strong matches", "cm91bmQgNzogdGhlIGZpbHRlciBrZWVwcyBvbmx5IHN0cm9uZyBtYXRjaGVz"),
    ("round 7: the model answers with a short reply", "cm91bmQgNzogdGhlIG1vZGVsIGFuc3dlcnMgd2l0aCBhIHNob3J0IHJlcGx5"),
    (
        "round 7: the recorder stores the reasoning trace",
        "cm91bmQgNzogdGhlIHJlY29yZGVyIHN0b3JlcyB0aGUgcmVhc29uaW5nIHRyYWNl",
    ),
    ("round 7: the angel watches the processor run", "cm91bmQgNzogdGhlIGFuZ2VsIHdhdGNoZXMgdGhlIHByb2Nlc3NvciBydW4"),
    (
        "round 7: angle of the vector decides the match",
        "cm91bmQgNzogYW5nbGUgb2YgdGhlIHZlY3RvciBkZWNpZGVzIHRoZSBtYXRjaA",
    ),
    (
        "round 7: the candle burns twice as long at night",
        "cm91bmQgNzogdGhlIGNhbmRsZSBidXJucyB0d2ljZSBhcyBsb25nIGF0IG5pZ2h0",
    ),
    ("round 7: a mirror of the universe in one line", "cm91bmQgNzogYSBtaXJyb3Igb2YgdGhlIHVuaXZlcnNlIGluIG9uZSBsaW5l"),
    ("round 7: the queue drains before the storm", "cm91bmQgNzogdGhlIHF1ZXVlIGRyYWlucyBiZWZvcmUgdGhlIHN0b3Jt"),
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
