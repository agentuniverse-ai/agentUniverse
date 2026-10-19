"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten33kitten33", "a2l0dGVuMzNraXR0ZW4zMw"),
    ("kitten33sitting33", "a2l0dGVuMzNzaXR0aW5nMzM"),
    ("kitten33agent33", "a2l0dGVuMzNhZ2VudDMz"),
    ("kitten33angle33", "a2l0dGVuMzNhbmdsZTMz"),
    ("sitting33angle33", "c2l0dGluZzMzYW5nbGUzMw"),
    ("sitting33universe33", "c2l0dGluZzMzdW5pdmVyc2UzMw"),
    ("sitting33memory33", "c2l0dGluZzMzbWVtb3J5MzM"),
    ("sitting33stream33", "c2l0dGluZzMzc3RyZWFtMzM"),
    ("agent33stream33", "YWdlbnQzM3N0cmVhbTMz"),
    ("agent33context33", "YWdlbnQzM2NvbnRleHQzMw"),
    ("agent33knowledge33", "YWdlbnQzM2tub3dsZWRnZTMz"),
    ("agent33vector33", "YWdlbnQzM3ZlY3RvcjMz"),
    ("angle33vector33", "YW5nbGUzM3ZlY3RvcjMz"),
    ("angle33processor33", "YW5nbGUzM3Byb2Nlc3NvcjMz"),
    ("angle33reasoning33", "YW5nbGUzM3JlYXNvbmluZzMz"),
    ("angle33machine33", "YW5nbGUzM21hY2hpbmUzMw"),
    ("universe33machine33", "dW5pdmVyc2UzM21hY2hpbmUzMw"),
    ("universe33learning33", "dW5pdmVyc2UzM2xlYXJuaW5nMzM"),
    ("universe33model33", "dW5pdmVyc2UzM21vZGVsMzM"),
    ("universe33token33", "dW5pdmVyc2UzM3Rva2VuMzM"),
    ("memory33token33", "bWVtb3J5MzN0b2tlbjMz"),
    ("memory33prompt33", "bWVtb3J5MzNwcm9tcHQzMw"),
    ("memory33session33", "bWVtb3J5MzNzZXNzaW9uMzM"),
    ("memory33library33", "bWVtb3J5MzNsaWJyYXJ5MzM"),
    ("stream33library33", "c3RyZWFtMzNsaWJyYXJ5MzM"),
    ("stream33service33", "c3RyZWFtMzNzZXJ2aWNlMzM"),
    ("stream33gateway33", "c3RyZWFtMzNnYXRld2F5MzM"),
    ("stream33storage33", "c3RyZWFtMzNzdG9yYWdlMzM"),
    ("context33storage33", "Y29udGV4dDMzc3RvcmFnZTMz"),
    ("context33network33", "Y29udGV4dDMzbmV0d29yazMz"),
    ("context33latency33", "Y29udGV4dDMzbGF0ZW5jeTMz"),
    ("context33buffer33", "Y29udGV4dDMzYnVmZmVyMzM"),
    ("knowledge33buffer33", "a25vd2xlZGdlMzNidWZmZXIzMw"),
    ("knowledge33queue33", "a25vd2xlZGdlMzNxdWV1ZTMz"),
    ("knowledge33worker33", "a25vd2xlZGdlMzN3b3JrZXIzMw"),
    ("knowledge33kernel33", "a25vd2xlZGdlMzNrZXJuZWwzMw"),
    ("vector33kernel33", "dmVjdG9yMzNrZXJuZWwzMw"),
    ("vector33signal33", "dmVjdG9yMzNzaWduYWwzMw"),
    ("vector33packet33", "dmVjdG9yMzNwYWNrZXQzMw"),
    ("vector33router33", "dmVjdG9yMzNyb3V0ZXIzMw"),
    ("processor33router33", "cHJvY2Vzc29yMzNyb3V0ZXIzMw"),
    ("processor33cluster33", "cHJvY2Vzc29yMzNjbHVzdGVyMzM"),
    ("processor33mirror33", "cHJvY2Vzc29yMzNtaXJyb3IzMw"),
    ("processor33filter33", "cHJvY2Vzc29yMzNmaWx0ZXIzMw"),
    ("reasoning33filter33", "cmVhc29uaW5nMzNmaWx0ZXIzMw"),
    ("reasoning33ranking33", "cmVhc29uaW5nMzNyYW5raW5nMzM"),
    ("reasoning33encoding33", "cmVhc29uaW5nMzNlbmNvZGluZzMz"),
    ("reasoning33mapping33", "cmVhc29uaW5nMzNtYXBwaW5nMzM"),
    ("machine33mapping33", "bWFjaGluZTMzbWFwcGluZzMz"),
    ("machine33record33", "bWFjaGluZTMzcmVjb3JkMzM"),
    ("machine33candle33", "bWFjaGluZTMzY2FuZGxlMzM"),
    ("machine33thread33", "bWFjaGluZTMzdGhyZWFkMzM"),
    ("learning33thread33", "bGVhcm5pbmczM3RocmVhZDMz"),
    ("learning33kitten33", "bGVhcm5pbmczM2tpdHRlbjMz"),
    ("learning33sitting33", "bGVhcm5pbmczM3NpdHRpbmczMw"),
    ("learning33agent33", "bGVhcm5pbmczM2FnZW50MzM"),
    ("model33agent33", "bW9kZWwzM2FnZW50MzM"),
    ("model33angle33", "bW9kZWwzM2FuZ2xlMzM"),
    ("model33universe33", "bW9kZWwzM3VuaXZlcnNlMzM"),
    ("model33memory33", "bW9kZWwzM21lbW9yeTMz"),
    ("token33memory33", "dG9rZW4zM21lbW9yeTMz"),
    ("token33stream33", "dG9rZW4zM3N0cmVhbTMz"),
    ("token33context33", "dG9rZW4zM2NvbnRleHQzMw"),
    ("token33knowledge33", "dG9rZW4zM2tub3dsZWRnZTMz"),
    ("prompt33knowledge33", "cHJvbXB0MzNrbm93bGVkZ2UzMw"),
    ("prompt33vector33", "cHJvbXB0MzN2ZWN0b3IzMw"),
    ("prompt33processor33", "cHJvbXB0MzNwcm9jZXNzb3IzMw"),
    ("prompt33reasoning33", "cHJvbXB0MzNyZWFzb25pbmczMw"),
    ("session33reasoning33", "c2Vzc2lvbjMzcmVhc29uaW5nMzM"),
    ("session33machine33", "c2Vzc2lvbjMzbWFjaGluZTMz"),
    ("session33learning33", "c2Vzc2lvbjMzbGVhcm5pbmczMw"),
    ("session33model33", "c2Vzc2lvbjMzbW9kZWwzMw"),
    ("library33model33", "bGlicmFyeTMzbW9kZWwzMw"),
    ("library33token33", "bGlicmFyeTMzdG9rZW4zMw"),
    ("library33prompt33", "bGlicmFyeTMzcHJvbXB0MzM"),
    ("library33session33", "bGlicmFyeTMzc2Vzc2lvbjMz"),
    ("service33session33", "c2VydmljZTMzc2Vzc2lvbjMz"),
    ("service33library33", "c2VydmljZTMzbGlicmFyeTMz"),
    ("service33service33", "c2VydmljZTMzc2VydmljZTMz"),
    ("service33gateway33", "c2VydmljZTMzZ2F0ZXdheTMz"),
    ("gateway33gateway33", "Z2F0ZXdheTMzZ2F0ZXdheTMz"),
    ("gateway33storage33", "Z2F0ZXdheTMzc3RvcmFnZTMz"),
    ("gateway33network33", "Z2F0ZXdheTMzbmV0d29yazMz"),
    ("gateway33latency33", "Z2F0ZXdheTMzbGF0ZW5jeTMz"),
    ("storage33latency33", "c3RvcmFnZTMzbGF0ZW5jeTMz"),
    ("storage33buffer33", "c3RvcmFnZTMzYnVmZmVyMzM"),
    ("storage33queue33", "c3RvcmFnZTMzcXVldWUzMw"),
    ("storage33worker33", "c3RvcmFnZTMzd29ya2VyMzM"),
    ("network33worker33", "bmV0d29yazMzd29ya2VyMzM"),
    ("network33kernel33", "bmV0d29yazMza2VybmVsMzM"),
    ("network33signal33", "bmV0d29yazMzc2lnbmFsMzM"),
    ("network33packet33", "bmV0d29yazMzcGFja2V0MzM"),
    ("latency33packet33", "bGF0ZW5jeTMzcGFja2V0MzM"),
    ("latency33router33", "bGF0ZW5jeTMzcm91dGVyMzM"),
    ("latency33cluster33", "bGF0ZW5jeTMzY2x1c3RlcjMz"),
    ("latency33mirror33", "bGF0ZW5jeTMzbWlycm9yMzM"),
    ("buffer33mirror33", "YnVmZmVyMzNtaXJyb3IzMw"),
    ("buffer33filter33", "YnVmZmVyMzNmaWx0ZXIzMw"),
    ("buffer33ranking33", "YnVmZmVyMzNyYW5raW5nMzM"),
    ("buffer33encoding33", "YnVmZmVyMzNlbmNvZGluZzMz"),
    ("queue33encoding33", "cXVldWUzM2VuY29kaW5nMzM"),
    ("queue33mapping33", "cXVldWUzM21hcHBpbmczMw"),
    ("queue33record33", "cXVldWUzM3JlY29yZDMz"),
    ("queue33candle33", "cXVldWUzM2NhbmRsZTMz"),
    ("worker33candle33", "d29ya2VyMzNjYW5kbGUzMw"),
    ("worker33thread33", "d29ya2VyMzN0aHJlYWQzMw"),
    ("worker33kitten33", "d29ya2VyMzNraXR0ZW4zMw"),
    ("worker33sitting33", "d29ya2VyMzNzaXR0aW5nMzM"),
    ("kernel33sitting33", "a2VybmVsMzNzaXR0aW5nMzM"),
    ("kernel33agent33", "a2VybmVsMzNhZ2VudDMz"),
    ("kernel33angle33", "a2VybmVsMzNhbmdsZTMz"),
    ("kernel33universe33", "a2VybmVsMzN1bml2ZXJzZTMz"),
    ("signal33universe33", "c2lnbmFsMzN1bml2ZXJzZTMz"),
    ("signal33memory33", "c2lnbmFsMzNtZW1vcnkzMw"),
    ("signal33stream33", "c2lnbmFsMzNzdHJlYW0zMw"),
    ("signal33context33", "c2lnbmFsMzNjb250ZXh0MzM"),
    ("packet33context33", "cGFja2V0MzNjb250ZXh0MzM"),
    ("packet33knowledge33", "cGFja2V0MzNrbm93bGVkZ2UzMw"),
    ("packet33vector33", "cGFja2V0MzN2ZWN0b3IzMw"),
    ("packet33processor33", "cGFja2V0MzNwcm9jZXNzb3IzMw"),
    ("router33processor33", "cm91dGVyMzNwcm9jZXNzb3IzMw"),
    ("router33reasoning33", "cm91dGVyMzNyZWFzb25pbmczMw"),
    ("router33machine33", "cm91dGVyMzNtYWNoaW5lMzM"),
    ("router33learning33", "cm91dGVyMzNsZWFybmluZzMz"),
    ("cluster33learning33", "Y2x1c3RlcjMzbGVhcm5pbmczMw"),
    ("cluster33model33", "Y2x1c3RlcjMzbW9kZWwzMw"),
    ("cluster33token33", "Y2x1c3RlcjMzdG9rZW4zMw"),
    ("cluster33prompt33", "Y2x1c3RlcjMzcHJvbXB0MzM"),
    ("mirror33prompt33", "bWlycm9yMzNwcm9tcHQzMw"),
    ("mirror33session33", "bWlycm9yMzNzZXNzaW9uMzM"),
    ("mirror33library33", "bWlycm9yMzNsaWJyYXJ5MzM"),
    ("mirror33service33", "bWlycm9yMzNzZXJ2aWNlMzM"),
    ("filter33service33", "ZmlsdGVyMzNzZXJ2aWNlMzM"),
    ("filter33gateway33", "ZmlsdGVyMzNnYXRld2F5MzM"),
    ("filter33storage33", "ZmlsdGVyMzNzdG9yYWdlMzM"),
    ("filter33network33", "ZmlsdGVyMzNuZXR3b3JrMzM"),
    ("ranking33network33", "cmFua2luZzMzbmV0d29yazMz"),
    ("ranking33latency33", "cmFua2luZzMzbGF0ZW5jeTMz"),
    ("ranking33buffer33", "cmFua2luZzMzYnVmZmVyMzM"),
    ("ranking33queue33", "cmFua2luZzMzcXVldWUzMw"),
    ("encoding33queue33", "ZW5jb2RpbmczM3F1ZXVlMzM"),
    ("encoding33worker33", "ZW5jb2RpbmczM3dvcmtlcjMz"),
    ("encoding33kernel33", "ZW5jb2RpbmczM2tlcm5lbDMz"),
    ("encoding33signal33", "ZW5jb2RpbmczM3NpZ25hbDMz"),
    ("mapping33signal33", "bWFwcGluZzMzc2lnbmFsMzM"),
    ("mapping33packet33", "bWFwcGluZzMzcGFja2V0MzM"),
    ("mapping33router33", "bWFwcGluZzMzcm91dGVyMzM"),
    ("mapping33cluster33", "bWFwcGluZzMzY2x1c3RlcjMz"),
    ("record33cluster33", "cmVjb3JkMzNjbHVzdGVyMzM"),
    ("record33mirror33", "cmVjb3JkMzNtaXJyb3IzMw"),
    ("record33filter33", "cmVjb3JkMzNmaWx0ZXIzMw"),
    ("record33ranking33", "cmVjb3JkMzNyYW5raW5nMzM"),
    ("candle33ranking33", "Y2FuZGxlMzNyYW5raW5nMzM"),
    ("candle33encoding33", "Y2FuZGxlMzNlbmNvZGluZzMz"),
    ("candle33mapping33", "Y2FuZGxlMzNtYXBwaW5nMzM"),
    ("candle33record33", "Y2FuZGxlMzNyZWNvcmQzMw"),
    ("thread33record33", "dGhyZWFkMzNyZWNvcmQzMw"),
    ("thread33candle33", "dGhyZWFkMzNjYW5kbGUzMw"),
    ("thread33thread33", "dGhyZWFkMzN0aHJlYWQzMw"),
    ("thread33kitten33", "dGhyZWFkMzNraXR0ZW4zMw"),
    (
        "round 33: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMzM6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 33: agentuniverse is a framework for multi agents",
        "cm91bmQgMzM6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 33: knowledge stored as vectors enables retrieval",
        "cm91bmQgMzM6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 33: the processor reads the record then stops",
        "cm91bmQgMzM6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 33: a worker pulls the next task from the queue",
        "cm91bmQgMzM6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 33: signals travel through the network layer",
        "cm91bmQgMzM6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 33: the gateway routes each request by policy",
        "cm91bmQgMzM6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 33: memory grows until the buffer is full",
        "cm91bmQgMzM6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 33: the cluster mirrors every packet twice",
        "cm91bmQgMzM6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 33: ranking uses tokens learned from the corpus",
        "cm91bmQgMzM6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 33: a long session ends when the candle dies",
        "cm91bmQgMzM6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 33: encode the prompt then map the result",
        "cm91bmQgMzM6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 33: the kernel wakes the worker at dawn", "cm91bmQgMzM6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 33: service latency drops after the patch",
        "cm91bmQgMzM6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 33: the library caches every vector it sees",
        "cm91bmQgMzM6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 33: agents argue then the debate resolves",
        "cm91bmQgMzM6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 33: the filter keeps only strong matches",
        "cm91bmQgMzM6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 33: the model answers with a short reply",
        "cm91bmQgMzM6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 33: the recorder stores the reasoning trace",
        "cm91bmQgMzM6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 33: the angel watches the processor run", "cm91bmQgMzM6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 33: angle of the vector decides the match",
        "cm91bmQgMzM6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 33: the candle burns twice as long at night",
        "cm91bmQgMzM6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 33: a mirror of the universe in one line",
        "cm91bmQgMzM6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 33: the queue drains before the storm", "cm91bmQgMzM6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
