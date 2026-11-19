"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten88kitten88", "a2l0dGVuODhraXR0ZW44OA"),
    ("kitten88sitting88", "a2l0dGVuODhzaXR0aW5nODg"),
    ("kitten88agent88", "a2l0dGVuODhhZ2VudDg4"),
    ("kitten88angle88", "a2l0dGVuODhhbmdsZTg4"),
    ("sitting88angle88", "c2l0dGluZzg4YW5nbGU4OA"),
    ("sitting88universe88", "c2l0dGluZzg4dW5pdmVyc2U4OA"),
    ("sitting88memory88", "c2l0dGluZzg4bWVtb3J5ODg"),
    ("sitting88stream88", "c2l0dGluZzg4c3RyZWFtODg"),
    ("agent88stream88", "YWdlbnQ4OHN0cmVhbTg4"),
    ("agent88context88", "YWdlbnQ4OGNvbnRleHQ4OA"),
    ("agent88knowledge88", "YWdlbnQ4OGtub3dsZWRnZTg4"),
    ("agent88vector88", "YWdlbnQ4OHZlY3Rvcjg4"),
    ("angle88vector88", "YW5nbGU4OHZlY3Rvcjg4"),
    ("angle88processor88", "YW5nbGU4OHByb2Nlc3Nvcjg4"),
    ("angle88reasoning88", "YW5nbGU4OHJlYXNvbmluZzg4"),
    ("angle88machine88", "YW5nbGU4OG1hY2hpbmU4OA"),
    ("universe88machine88", "dW5pdmVyc2U4OG1hY2hpbmU4OA"),
    ("universe88learning88", "dW5pdmVyc2U4OGxlYXJuaW5nODg"),
    ("universe88model88", "dW5pdmVyc2U4OG1vZGVsODg"),
    ("universe88token88", "dW5pdmVyc2U4OHRva2VuODg"),
    ("memory88token88", "bWVtb3J5ODh0b2tlbjg4"),
    ("memory88prompt88", "bWVtb3J5ODhwcm9tcHQ4OA"),
    ("memory88session88", "bWVtb3J5ODhzZXNzaW9uODg"),
    ("memory88library88", "bWVtb3J5ODhsaWJyYXJ5ODg"),
    ("stream88library88", "c3RyZWFtODhsaWJyYXJ5ODg"),
    ("stream88service88", "c3RyZWFtODhzZXJ2aWNlODg"),
    ("stream88gateway88", "c3RyZWFtODhnYXRld2F5ODg"),
    ("stream88storage88", "c3RyZWFtODhzdG9yYWdlODg"),
    ("context88storage88", "Y29udGV4dDg4c3RvcmFnZTg4"),
    ("context88network88", "Y29udGV4dDg4bmV0d29yazg4"),
    ("context88latency88", "Y29udGV4dDg4bGF0ZW5jeTg4"),
    ("context88buffer88", "Y29udGV4dDg4YnVmZmVyODg"),
    ("knowledge88buffer88", "a25vd2xlZGdlODhidWZmZXI4OA"),
    ("knowledge88queue88", "a25vd2xlZGdlODhxdWV1ZTg4"),
    ("knowledge88worker88", "a25vd2xlZGdlODh3b3JrZXI4OA"),
    ("knowledge88kernel88", "a25vd2xlZGdlODhrZXJuZWw4OA"),
    ("vector88kernel88", "dmVjdG9yODhrZXJuZWw4OA"),
    ("vector88signal88", "dmVjdG9yODhzaWduYWw4OA"),
    ("vector88packet88", "dmVjdG9yODhwYWNrZXQ4OA"),
    ("vector88router88", "dmVjdG9yODhyb3V0ZXI4OA"),
    ("processor88router88", "cHJvY2Vzc29yODhyb3V0ZXI4OA"),
    ("processor88cluster88", "cHJvY2Vzc29yODhjbHVzdGVyODg"),
    ("processor88mirror88", "cHJvY2Vzc29yODhtaXJyb3I4OA"),
    ("processor88filter88", "cHJvY2Vzc29yODhmaWx0ZXI4OA"),
    ("reasoning88filter88", "cmVhc29uaW5nODhmaWx0ZXI4OA"),
    ("reasoning88ranking88", "cmVhc29uaW5nODhyYW5raW5nODg"),
    ("reasoning88encoding88", "cmVhc29uaW5nODhlbmNvZGluZzg4"),
    ("reasoning88mapping88", "cmVhc29uaW5nODhtYXBwaW5nODg"),
    ("machine88mapping88", "bWFjaGluZTg4bWFwcGluZzg4"),
    ("machine88record88", "bWFjaGluZTg4cmVjb3JkODg"),
    ("machine88candle88", "bWFjaGluZTg4Y2FuZGxlODg"),
    ("machine88thread88", "bWFjaGluZTg4dGhyZWFkODg"),
    ("learning88thread88", "bGVhcm5pbmc4OHRocmVhZDg4"),
    ("learning88kitten88", "bGVhcm5pbmc4OGtpdHRlbjg4"),
    ("learning88sitting88", "bGVhcm5pbmc4OHNpdHRpbmc4OA"),
    ("learning88agent88", "bGVhcm5pbmc4OGFnZW50ODg"),
    ("model88agent88", "bW9kZWw4OGFnZW50ODg"),
    ("model88angle88", "bW9kZWw4OGFuZ2xlODg"),
    ("model88universe88", "bW9kZWw4OHVuaXZlcnNlODg"),
    ("model88memory88", "bW9kZWw4OG1lbW9yeTg4"),
    ("token88memory88", "dG9rZW44OG1lbW9yeTg4"),
    ("token88stream88", "dG9rZW44OHN0cmVhbTg4"),
    ("token88context88", "dG9rZW44OGNvbnRleHQ4OA"),
    ("token88knowledge88", "dG9rZW44OGtub3dsZWRnZTg4"),
    ("prompt88knowledge88", "cHJvbXB0ODhrbm93bGVkZ2U4OA"),
    ("prompt88vector88", "cHJvbXB0ODh2ZWN0b3I4OA"),
    ("prompt88processor88", "cHJvbXB0ODhwcm9jZXNzb3I4OA"),
    ("prompt88reasoning88", "cHJvbXB0ODhyZWFzb25pbmc4OA"),
    ("session88reasoning88", "c2Vzc2lvbjg4cmVhc29uaW5nODg"),
    ("session88machine88", "c2Vzc2lvbjg4bWFjaGluZTg4"),
    ("session88learning88", "c2Vzc2lvbjg4bGVhcm5pbmc4OA"),
    ("session88model88", "c2Vzc2lvbjg4bW9kZWw4OA"),
    ("library88model88", "bGlicmFyeTg4bW9kZWw4OA"),
    ("library88token88", "bGlicmFyeTg4dG9rZW44OA"),
    ("library88prompt88", "bGlicmFyeTg4cHJvbXB0ODg"),
    ("library88session88", "bGlicmFyeTg4c2Vzc2lvbjg4"),
    ("service88session88", "c2VydmljZTg4c2Vzc2lvbjg4"),
    ("service88library88", "c2VydmljZTg4bGlicmFyeTg4"),
    ("service88service88", "c2VydmljZTg4c2VydmljZTg4"),
    ("service88gateway88", "c2VydmljZTg4Z2F0ZXdheTg4"),
    ("gateway88gateway88", "Z2F0ZXdheTg4Z2F0ZXdheTg4"),
    ("gateway88storage88", "Z2F0ZXdheTg4c3RvcmFnZTg4"),
    ("gateway88network88", "Z2F0ZXdheTg4bmV0d29yazg4"),
    ("gateway88latency88", "Z2F0ZXdheTg4bGF0ZW5jeTg4"),
    ("storage88latency88", "c3RvcmFnZTg4bGF0ZW5jeTg4"),
    ("storage88buffer88", "c3RvcmFnZTg4YnVmZmVyODg"),
    ("storage88queue88", "c3RvcmFnZTg4cXVldWU4OA"),
    ("storage88worker88", "c3RvcmFnZTg4d29ya2VyODg"),
    ("network88worker88", "bmV0d29yazg4d29ya2VyODg"),
    ("network88kernel88", "bmV0d29yazg4a2VybmVsODg"),
    ("network88signal88", "bmV0d29yazg4c2lnbmFsODg"),
    ("network88packet88", "bmV0d29yazg4cGFja2V0ODg"),
    ("latency88packet88", "bGF0ZW5jeTg4cGFja2V0ODg"),
    ("latency88router88", "bGF0ZW5jeTg4cm91dGVyODg"),
    ("latency88cluster88", "bGF0ZW5jeTg4Y2x1c3Rlcjg4"),
    ("latency88mirror88", "bGF0ZW5jeTg4bWlycm9yODg"),
    ("buffer88mirror88", "YnVmZmVyODhtaXJyb3I4OA"),
    ("buffer88filter88", "YnVmZmVyODhmaWx0ZXI4OA"),
    ("buffer88ranking88", "YnVmZmVyODhyYW5raW5nODg"),
    ("buffer88encoding88", "YnVmZmVyODhlbmNvZGluZzg4"),
    ("queue88encoding88", "cXVldWU4OGVuY29kaW5nODg"),
    ("queue88mapping88", "cXVldWU4OG1hcHBpbmc4OA"),
    ("queue88record88", "cXVldWU4OHJlY29yZDg4"),
    ("queue88candle88", "cXVldWU4OGNhbmRsZTg4"),
    ("worker88candle88", "d29ya2VyODhjYW5kbGU4OA"),
    ("worker88thread88", "d29ya2VyODh0aHJlYWQ4OA"),
    ("worker88kitten88", "d29ya2VyODhraXR0ZW44OA"),
    ("worker88sitting88", "d29ya2VyODhzaXR0aW5nODg"),
    ("kernel88sitting88", "a2VybmVsODhzaXR0aW5nODg"),
    ("kernel88agent88", "a2VybmVsODhhZ2VudDg4"),
    ("kernel88angle88", "a2VybmVsODhhbmdsZTg4"),
    ("kernel88universe88", "a2VybmVsODh1bml2ZXJzZTg4"),
    ("signal88universe88", "c2lnbmFsODh1bml2ZXJzZTg4"),
    ("signal88memory88", "c2lnbmFsODhtZW1vcnk4OA"),
    ("signal88stream88", "c2lnbmFsODhzdHJlYW04OA"),
    ("signal88context88", "c2lnbmFsODhjb250ZXh0ODg"),
    ("packet88context88", "cGFja2V0ODhjb250ZXh0ODg"),
    ("packet88knowledge88", "cGFja2V0ODhrbm93bGVkZ2U4OA"),
    ("packet88vector88", "cGFja2V0ODh2ZWN0b3I4OA"),
    ("packet88processor88", "cGFja2V0ODhwcm9jZXNzb3I4OA"),
    ("router88processor88", "cm91dGVyODhwcm9jZXNzb3I4OA"),
    ("router88reasoning88", "cm91dGVyODhyZWFzb25pbmc4OA"),
    ("router88machine88", "cm91dGVyODhtYWNoaW5lODg"),
    ("router88learning88", "cm91dGVyODhsZWFybmluZzg4"),
    ("cluster88learning88", "Y2x1c3Rlcjg4bGVhcm5pbmc4OA"),
    ("cluster88model88", "Y2x1c3Rlcjg4bW9kZWw4OA"),
    ("cluster88token88", "Y2x1c3Rlcjg4dG9rZW44OA"),
    ("cluster88prompt88", "Y2x1c3Rlcjg4cHJvbXB0ODg"),
    ("mirror88prompt88", "bWlycm9yODhwcm9tcHQ4OA"),
    ("mirror88session88", "bWlycm9yODhzZXNzaW9uODg"),
    ("mirror88library88", "bWlycm9yODhsaWJyYXJ5ODg"),
    ("mirror88service88", "bWlycm9yODhzZXJ2aWNlODg"),
    ("filter88service88", "ZmlsdGVyODhzZXJ2aWNlODg"),
    ("filter88gateway88", "ZmlsdGVyODhnYXRld2F5ODg"),
    ("filter88storage88", "ZmlsdGVyODhzdG9yYWdlODg"),
    ("filter88network88", "ZmlsdGVyODhuZXR3b3JrODg"),
    ("ranking88network88", "cmFua2luZzg4bmV0d29yazg4"),
    ("ranking88latency88", "cmFua2luZzg4bGF0ZW5jeTg4"),
    ("ranking88buffer88", "cmFua2luZzg4YnVmZmVyODg"),
    ("ranking88queue88", "cmFua2luZzg4cXVldWU4OA"),
    ("encoding88queue88", "ZW5jb2Rpbmc4OHF1ZXVlODg"),
    ("encoding88worker88", "ZW5jb2Rpbmc4OHdvcmtlcjg4"),
    ("encoding88kernel88", "ZW5jb2Rpbmc4OGtlcm5lbDg4"),
    ("encoding88signal88", "ZW5jb2Rpbmc4OHNpZ25hbDg4"),
    ("mapping88signal88", "bWFwcGluZzg4c2lnbmFsODg"),
    ("mapping88packet88", "bWFwcGluZzg4cGFja2V0ODg"),
    ("mapping88router88", "bWFwcGluZzg4cm91dGVyODg"),
    ("mapping88cluster88", "bWFwcGluZzg4Y2x1c3Rlcjg4"),
    ("record88cluster88", "cmVjb3JkODhjbHVzdGVyODg"),
    ("record88mirror88", "cmVjb3JkODhtaXJyb3I4OA"),
    ("record88filter88", "cmVjb3JkODhmaWx0ZXI4OA"),
    ("record88ranking88", "cmVjb3JkODhyYW5raW5nODg"),
    ("candle88ranking88", "Y2FuZGxlODhyYW5raW5nODg"),
    ("candle88encoding88", "Y2FuZGxlODhlbmNvZGluZzg4"),
    ("candle88mapping88", "Y2FuZGxlODhtYXBwaW5nODg"),
    ("candle88record88", "Y2FuZGxlODhyZWNvcmQ4OA"),
    ("thread88record88", "dGhyZWFkODhyZWNvcmQ4OA"),
    ("thread88candle88", "dGhyZWFkODhjYW5kbGU4OA"),
    ("thread88thread88", "dGhyZWFkODh0aHJlYWQ4OA"),
    ("thread88kitten88", "dGhyZWFkODhraXR0ZW44OA"),
    (
        "round 88: the quick brown fox jumps over the lazy dog",
        "cm91bmQgODg6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 88: agentuniverse is a framework for multi agents",
        "cm91bmQgODg6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 88: knowledge stored as vectors enables retrieval",
        "cm91bmQgODg6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 88: the processor reads the record then stops",
        "cm91bmQgODg6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 88: a worker pulls the next task from the queue",
        "cm91bmQgODg6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 88: signals travel through the network layer",
        "cm91bmQgODg6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 88: the gateway routes each request by policy",
        "cm91bmQgODg6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 88: memory grows until the buffer is full",
        "cm91bmQgODg6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 88: the cluster mirrors every packet twice",
        "cm91bmQgODg6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 88: ranking uses tokens learned from the corpus",
        "cm91bmQgODg6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 88: a long session ends when the candle dies",
        "cm91bmQgODg6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 88: encode the prompt then map the result",
        "cm91bmQgODg6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 88: the kernel wakes the worker at dawn", "cm91bmQgODg6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 88: service latency drops after the patch",
        "cm91bmQgODg6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 88: the library caches every vector it sees",
        "cm91bmQgODg6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 88: agents argue then the debate resolves",
        "cm91bmQgODg6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 88: the filter keeps only strong matches",
        "cm91bmQgODg6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 88: the model answers with a short reply",
        "cm91bmQgODg6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 88: the recorder stores the reasoning trace",
        "cm91bmQgODg6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 88: the angel watches the processor run", "cm91bmQgODg6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 88: angle of the vector decides the match",
        "cm91bmQgODg6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 88: the candle burns twice as long at night",
        "cm91bmQgODg6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 88: a mirror of the universe in one line",
        "cm91bmQgODg6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 88: the queue drains before the storm", "cm91bmQgODg6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
