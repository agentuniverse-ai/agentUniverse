"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten83kitten83", "a2l0dGVuODNraXR0ZW44Mw"),
    ("kitten83sitting83", "a2l0dGVuODNzaXR0aW5nODM"),
    ("kitten83agent83", "a2l0dGVuODNhZ2VudDgz"),
    ("kitten83angle83", "a2l0dGVuODNhbmdsZTgz"),
    ("sitting83angle83", "c2l0dGluZzgzYW5nbGU4Mw"),
    ("sitting83universe83", "c2l0dGluZzgzdW5pdmVyc2U4Mw"),
    ("sitting83memory83", "c2l0dGluZzgzbWVtb3J5ODM"),
    ("sitting83stream83", "c2l0dGluZzgzc3RyZWFtODM"),
    ("agent83stream83", "YWdlbnQ4M3N0cmVhbTgz"),
    ("agent83context83", "YWdlbnQ4M2NvbnRleHQ4Mw"),
    ("agent83knowledge83", "YWdlbnQ4M2tub3dsZWRnZTgz"),
    ("agent83vector83", "YWdlbnQ4M3ZlY3Rvcjgz"),
    ("angle83vector83", "YW5nbGU4M3ZlY3Rvcjgz"),
    ("angle83processor83", "YW5nbGU4M3Byb2Nlc3Nvcjgz"),
    ("angle83reasoning83", "YW5nbGU4M3JlYXNvbmluZzgz"),
    ("angle83machine83", "YW5nbGU4M21hY2hpbmU4Mw"),
    ("universe83machine83", "dW5pdmVyc2U4M21hY2hpbmU4Mw"),
    ("universe83learning83", "dW5pdmVyc2U4M2xlYXJuaW5nODM"),
    ("universe83model83", "dW5pdmVyc2U4M21vZGVsODM"),
    ("universe83token83", "dW5pdmVyc2U4M3Rva2VuODM"),
    ("memory83token83", "bWVtb3J5ODN0b2tlbjgz"),
    ("memory83prompt83", "bWVtb3J5ODNwcm9tcHQ4Mw"),
    ("memory83session83", "bWVtb3J5ODNzZXNzaW9uODM"),
    ("memory83library83", "bWVtb3J5ODNsaWJyYXJ5ODM"),
    ("stream83library83", "c3RyZWFtODNsaWJyYXJ5ODM"),
    ("stream83service83", "c3RyZWFtODNzZXJ2aWNlODM"),
    ("stream83gateway83", "c3RyZWFtODNnYXRld2F5ODM"),
    ("stream83storage83", "c3RyZWFtODNzdG9yYWdlODM"),
    ("context83storage83", "Y29udGV4dDgzc3RvcmFnZTgz"),
    ("context83network83", "Y29udGV4dDgzbmV0d29yazgz"),
    ("context83latency83", "Y29udGV4dDgzbGF0ZW5jeTgz"),
    ("context83buffer83", "Y29udGV4dDgzYnVmZmVyODM"),
    ("knowledge83buffer83", "a25vd2xlZGdlODNidWZmZXI4Mw"),
    ("knowledge83queue83", "a25vd2xlZGdlODNxdWV1ZTgz"),
    ("knowledge83worker83", "a25vd2xlZGdlODN3b3JrZXI4Mw"),
    ("knowledge83kernel83", "a25vd2xlZGdlODNrZXJuZWw4Mw"),
    ("vector83kernel83", "dmVjdG9yODNrZXJuZWw4Mw"),
    ("vector83signal83", "dmVjdG9yODNzaWduYWw4Mw"),
    ("vector83packet83", "dmVjdG9yODNwYWNrZXQ4Mw"),
    ("vector83router83", "dmVjdG9yODNyb3V0ZXI4Mw"),
    ("processor83router83", "cHJvY2Vzc29yODNyb3V0ZXI4Mw"),
    ("processor83cluster83", "cHJvY2Vzc29yODNjbHVzdGVyODM"),
    ("processor83mirror83", "cHJvY2Vzc29yODNtaXJyb3I4Mw"),
    ("processor83filter83", "cHJvY2Vzc29yODNmaWx0ZXI4Mw"),
    ("reasoning83filter83", "cmVhc29uaW5nODNmaWx0ZXI4Mw"),
    ("reasoning83ranking83", "cmVhc29uaW5nODNyYW5raW5nODM"),
    ("reasoning83encoding83", "cmVhc29uaW5nODNlbmNvZGluZzgz"),
    ("reasoning83mapping83", "cmVhc29uaW5nODNtYXBwaW5nODM"),
    ("machine83mapping83", "bWFjaGluZTgzbWFwcGluZzgz"),
    ("machine83record83", "bWFjaGluZTgzcmVjb3JkODM"),
    ("machine83candle83", "bWFjaGluZTgzY2FuZGxlODM"),
    ("machine83thread83", "bWFjaGluZTgzdGhyZWFkODM"),
    ("learning83thread83", "bGVhcm5pbmc4M3RocmVhZDgz"),
    ("learning83kitten83", "bGVhcm5pbmc4M2tpdHRlbjgz"),
    ("learning83sitting83", "bGVhcm5pbmc4M3NpdHRpbmc4Mw"),
    ("learning83agent83", "bGVhcm5pbmc4M2FnZW50ODM"),
    ("model83agent83", "bW9kZWw4M2FnZW50ODM"),
    ("model83angle83", "bW9kZWw4M2FuZ2xlODM"),
    ("model83universe83", "bW9kZWw4M3VuaXZlcnNlODM"),
    ("model83memory83", "bW9kZWw4M21lbW9yeTgz"),
    ("token83memory83", "dG9rZW44M21lbW9yeTgz"),
    ("token83stream83", "dG9rZW44M3N0cmVhbTgz"),
    ("token83context83", "dG9rZW44M2NvbnRleHQ4Mw"),
    ("token83knowledge83", "dG9rZW44M2tub3dsZWRnZTgz"),
    ("prompt83knowledge83", "cHJvbXB0ODNrbm93bGVkZ2U4Mw"),
    ("prompt83vector83", "cHJvbXB0ODN2ZWN0b3I4Mw"),
    ("prompt83processor83", "cHJvbXB0ODNwcm9jZXNzb3I4Mw"),
    ("prompt83reasoning83", "cHJvbXB0ODNyZWFzb25pbmc4Mw"),
    ("session83reasoning83", "c2Vzc2lvbjgzcmVhc29uaW5nODM"),
    ("session83machine83", "c2Vzc2lvbjgzbWFjaGluZTgz"),
    ("session83learning83", "c2Vzc2lvbjgzbGVhcm5pbmc4Mw"),
    ("session83model83", "c2Vzc2lvbjgzbW9kZWw4Mw"),
    ("library83model83", "bGlicmFyeTgzbW9kZWw4Mw"),
    ("library83token83", "bGlicmFyeTgzdG9rZW44Mw"),
    ("library83prompt83", "bGlicmFyeTgzcHJvbXB0ODM"),
    ("library83session83", "bGlicmFyeTgzc2Vzc2lvbjgz"),
    ("service83session83", "c2VydmljZTgzc2Vzc2lvbjgz"),
    ("service83library83", "c2VydmljZTgzbGlicmFyeTgz"),
    ("service83service83", "c2VydmljZTgzc2VydmljZTgz"),
    ("service83gateway83", "c2VydmljZTgzZ2F0ZXdheTgz"),
    ("gateway83gateway83", "Z2F0ZXdheTgzZ2F0ZXdheTgz"),
    ("gateway83storage83", "Z2F0ZXdheTgzc3RvcmFnZTgz"),
    ("gateway83network83", "Z2F0ZXdheTgzbmV0d29yazgz"),
    ("gateway83latency83", "Z2F0ZXdheTgzbGF0ZW5jeTgz"),
    ("storage83latency83", "c3RvcmFnZTgzbGF0ZW5jeTgz"),
    ("storage83buffer83", "c3RvcmFnZTgzYnVmZmVyODM"),
    ("storage83queue83", "c3RvcmFnZTgzcXVldWU4Mw"),
    ("storage83worker83", "c3RvcmFnZTgzd29ya2VyODM"),
    ("network83worker83", "bmV0d29yazgzd29ya2VyODM"),
    ("network83kernel83", "bmV0d29yazgza2VybmVsODM"),
    ("network83signal83", "bmV0d29yazgzc2lnbmFsODM"),
    ("network83packet83", "bmV0d29yazgzcGFja2V0ODM"),
    ("latency83packet83", "bGF0ZW5jeTgzcGFja2V0ODM"),
    ("latency83router83", "bGF0ZW5jeTgzcm91dGVyODM"),
    ("latency83cluster83", "bGF0ZW5jeTgzY2x1c3Rlcjgz"),
    ("latency83mirror83", "bGF0ZW5jeTgzbWlycm9yODM"),
    ("buffer83mirror83", "YnVmZmVyODNtaXJyb3I4Mw"),
    ("buffer83filter83", "YnVmZmVyODNmaWx0ZXI4Mw"),
    ("buffer83ranking83", "YnVmZmVyODNyYW5raW5nODM"),
    ("buffer83encoding83", "YnVmZmVyODNlbmNvZGluZzgz"),
    ("queue83encoding83", "cXVldWU4M2VuY29kaW5nODM"),
    ("queue83mapping83", "cXVldWU4M21hcHBpbmc4Mw"),
    ("queue83record83", "cXVldWU4M3JlY29yZDgz"),
    ("queue83candle83", "cXVldWU4M2NhbmRsZTgz"),
    ("worker83candle83", "d29ya2VyODNjYW5kbGU4Mw"),
    ("worker83thread83", "d29ya2VyODN0aHJlYWQ4Mw"),
    ("worker83kitten83", "d29ya2VyODNraXR0ZW44Mw"),
    ("worker83sitting83", "d29ya2VyODNzaXR0aW5nODM"),
    ("kernel83sitting83", "a2VybmVsODNzaXR0aW5nODM"),
    ("kernel83agent83", "a2VybmVsODNhZ2VudDgz"),
    ("kernel83angle83", "a2VybmVsODNhbmdsZTgz"),
    ("kernel83universe83", "a2VybmVsODN1bml2ZXJzZTgz"),
    ("signal83universe83", "c2lnbmFsODN1bml2ZXJzZTgz"),
    ("signal83memory83", "c2lnbmFsODNtZW1vcnk4Mw"),
    ("signal83stream83", "c2lnbmFsODNzdHJlYW04Mw"),
    ("signal83context83", "c2lnbmFsODNjb250ZXh0ODM"),
    ("packet83context83", "cGFja2V0ODNjb250ZXh0ODM"),
    ("packet83knowledge83", "cGFja2V0ODNrbm93bGVkZ2U4Mw"),
    ("packet83vector83", "cGFja2V0ODN2ZWN0b3I4Mw"),
    ("packet83processor83", "cGFja2V0ODNwcm9jZXNzb3I4Mw"),
    ("router83processor83", "cm91dGVyODNwcm9jZXNzb3I4Mw"),
    ("router83reasoning83", "cm91dGVyODNyZWFzb25pbmc4Mw"),
    ("router83machine83", "cm91dGVyODNtYWNoaW5lODM"),
    ("router83learning83", "cm91dGVyODNsZWFybmluZzgz"),
    ("cluster83learning83", "Y2x1c3RlcjgzbGVhcm5pbmc4Mw"),
    ("cluster83model83", "Y2x1c3RlcjgzbW9kZWw4Mw"),
    ("cluster83token83", "Y2x1c3RlcjgzdG9rZW44Mw"),
    ("cluster83prompt83", "Y2x1c3RlcjgzcHJvbXB0ODM"),
    ("mirror83prompt83", "bWlycm9yODNwcm9tcHQ4Mw"),
    ("mirror83session83", "bWlycm9yODNzZXNzaW9uODM"),
    ("mirror83library83", "bWlycm9yODNsaWJyYXJ5ODM"),
    ("mirror83service83", "bWlycm9yODNzZXJ2aWNlODM"),
    ("filter83service83", "ZmlsdGVyODNzZXJ2aWNlODM"),
    ("filter83gateway83", "ZmlsdGVyODNnYXRld2F5ODM"),
    ("filter83storage83", "ZmlsdGVyODNzdG9yYWdlODM"),
    ("filter83network83", "ZmlsdGVyODNuZXR3b3JrODM"),
    ("ranking83network83", "cmFua2luZzgzbmV0d29yazgz"),
    ("ranking83latency83", "cmFua2luZzgzbGF0ZW5jeTgz"),
    ("ranking83buffer83", "cmFua2luZzgzYnVmZmVyODM"),
    ("ranking83queue83", "cmFua2luZzgzcXVldWU4Mw"),
    ("encoding83queue83", "ZW5jb2Rpbmc4M3F1ZXVlODM"),
    ("encoding83worker83", "ZW5jb2Rpbmc4M3dvcmtlcjgz"),
    ("encoding83kernel83", "ZW5jb2Rpbmc4M2tlcm5lbDgz"),
    ("encoding83signal83", "ZW5jb2Rpbmc4M3NpZ25hbDgz"),
    ("mapping83signal83", "bWFwcGluZzgzc2lnbmFsODM"),
    ("mapping83packet83", "bWFwcGluZzgzcGFja2V0ODM"),
    ("mapping83router83", "bWFwcGluZzgzcm91dGVyODM"),
    ("mapping83cluster83", "bWFwcGluZzgzY2x1c3Rlcjgz"),
    ("record83cluster83", "cmVjb3JkODNjbHVzdGVyODM"),
    ("record83mirror83", "cmVjb3JkODNtaXJyb3I4Mw"),
    ("record83filter83", "cmVjb3JkODNmaWx0ZXI4Mw"),
    ("record83ranking83", "cmVjb3JkODNyYW5raW5nODM"),
    ("candle83ranking83", "Y2FuZGxlODNyYW5raW5nODM"),
    ("candle83encoding83", "Y2FuZGxlODNlbmNvZGluZzgz"),
    ("candle83mapping83", "Y2FuZGxlODNtYXBwaW5nODM"),
    ("candle83record83", "Y2FuZGxlODNyZWNvcmQ4Mw"),
    ("thread83record83", "dGhyZWFkODNyZWNvcmQ4Mw"),
    ("thread83candle83", "dGhyZWFkODNjYW5kbGU4Mw"),
    ("thread83thread83", "dGhyZWFkODN0aHJlYWQ4Mw"),
    ("thread83kitten83", "dGhyZWFkODNraXR0ZW44Mw"),
    (
        "round 83: the quick brown fox jumps over the lazy dog",
        "cm91bmQgODM6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 83: agentuniverse is a framework for multi agents",
        "cm91bmQgODM6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 83: knowledge stored as vectors enables retrieval",
        "cm91bmQgODM6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 83: the processor reads the record then stops",
        "cm91bmQgODM6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 83: a worker pulls the next task from the queue",
        "cm91bmQgODM6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 83: signals travel through the network layer",
        "cm91bmQgODM6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 83: the gateway routes each request by policy",
        "cm91bmQgODM6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 83: memory grows until the buffer is full",
        "cm91bmQgODM6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 83: the cluster mirrors every packet twice",
        "cm91bmQgODM6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 83: ranking uses tokens learned from the corpus",
        "cm91bmQgODM6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 83: a long session ends when the candle dies",
        "cm91bmQgODM6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 83: encode the prompt then map the result",
        "cm91bmQgODM6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 83: the kernel wakes the worker at dawn", "cm91bmQgODM6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 83: service latency drops after the patch",
        "cm91bmQgODM6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 83: the library caches every vector it sees",
        "cm91bmQgODM6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 83: agents argue then the debate resolves",
        "cm91bmQgODM6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 83: the filter keeps only strong matches",
        "cm91bmQgODM6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 83: the model answers with a short reply",
        "cm91bmQgODM6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 83: the recorder stores the reasoning trace",
        "cm91bmQgODM6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 83: the angel watches the processor run", "cm91bmQgODM6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 83: angle of the vector decides the match",
        "cm91bmQgODM6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 83: the candle burns twice as long at night",
        "cm91bmQgODM6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 83: a mirror of the universe in one line",
        "cm91bmQgODM6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 83: the queue drains before the storm", "cm91bmQgODM6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
