"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten91kitten91", "a2l0dGVuOTFraXR0ZW45MQ"),
    ("kitten91sitting91", "a2l0dGVuOTFzaXR0aW5nOTE"),
    ("kitten91agent91", "a2l0dGVuOTFhZ2VudDkx"),
    ("kitten91angle91", "a2l0dGVuOTFhbmdsZTkx"),
    ("sitting91angle91", "c2l0dGluZzkxYW5nbGU5MQ"),
    ("sitting91universe91", "c2l0dGluZzkxdW5pdmVyc2U5MQ"),
    ("sitting91memory91", "c2l0dGluZzkxbWVtb3J5OTE"),
    ("sitting91stream91", "c2l0dGluZzkxc3RyZWFtOTE"),
    ("agent91stream91", "YWdlbnQ5MXN0cmVhbTkx"),
    ("agent91context91", "YWdlbnQ5MWNvbnRleHQ5MQ"),
    ("agent91knowledge91", "YWdlbnQ5MWtub3dsZWRnZTkx"),
    ("agent91vector91", "YWdlbnQ5MXZlY3Rvcjkx"),
    ("angle91vector91", "YW5nbGU5MXZlY3Rvcjkx"),
    ("angle91processor91", "YW5nbGU5MXByb2Nlc3Nvcjkx"),
    ("angle91reasoning91", "YW5nbGU5MXJlYXNvbmluZzkx"),
    ("angle91machine91", "YW5nbGU5MW1hY2hpbmU5MQ"),
    ("universe91machine91", "dW5pdmVyc2U5MW1hY2hpbmU5MQ"),
    ("universe91learning91", "dW5pdmVyc2U5MWxlYXJuaW5nOTE"),
    ("universe91model91", "dW5pdmVyc2U5MW1vZGVsOTE"),
    ("universe91token91", "dW5pdmVyc2U5MXRva2VuOTE"),
    ("memory91token91", "bWVtb3J5OTF0b2tlbjkx"),
    ("memory91prompt91", "bWVtb3J5OTFwcm9tcHQ5MQ"),
    ("memory91session91", "bWVtb3J5OTFzZXNzaW9uOTE"),
    ("memory91library91", "bWVtb3J5OTFsaWJyYXJ5OTE"),
    ("stream91library91", "c3RyZWFtOTFsaWJyYXJ5OTE"),
    ("stream91service91", "c3RyZWFtOTFzZXJ2aWNlOTE"),
    ("stream91gateway91", "c3RyZWFtOTFnYXRld2F5OTE"),
    ("stream91storage91", "c3RyZWFtOTFzdG9yYWdlOTE"),
    ("context91storage91", "Y29udGV4dDkxc3RvcmFnZTkx"),
    ("context91network91", "Y29udGV4dDkxbmV0d29yazkx"),
    ("context91latency91", "Y29udGV4dDkxbGF0ZW5jeTkx"),
    ("context91buffer91", "Y29udGV4dDkxYnVmZmVyOTE"),
    ("knowledge91buffer91", "a25vd2xlZGdlOTFidWZmZXI5MQ"),
    ("knowledge91queue91", "a25vd2xlZGdlOTFxdWV1ZTkx"),
    ("knowledge91worker91", "a25vd2xlZGdlOTF3b3JrZXI5MQ"),
    ("knowledge91kernel91", "a25vd2xlZGdlOTFrZXJuZWw5MQ"),
    ("vector91kernel91", "dmVjdG9yOTFrZXJuZWw5MQ"),
    ("vector91signal91", "dmVjdG9yOTFzaWduYWw5MQ"),
    ("vector91packet91", "dmVjdG9yOTFwYWNrZXQ5MQ"),
    ("vector91router91", "dmVjdG9yOTFyb3V0ZXI5MQ"),
    ("processor91router91", "cHJvY2Vzc29yOTFyb3V0ZXI5MQ"),
    ("processor91cluster91", "cHJvY2Vzc29yOTFjbHVzdGVyOTE"),
    ("processor91mirror91", "cHJvY2Vzc29yOTFtaXJyb3I5MQ"),
    ("processor91filter91", "cHJvY2Vzc29yOTFmaWx0ZXI5MQ"),
    ("reasoning91filter91", "cmVhc29uaW5nOTFmaWx0ZXI5MQ"),
    ("reasoning91ranking91", "cmVhc29uaW5nOTFyYW5raW5nOTE"),
    ("reasoning91encoding91", "cmVhc29uaW5nOTFlbmNvZGluZzkx"),
    ("reasoning91mapping91", "cmVhc29uaW5nOTFtYXBwaW5nOTE"),
    ("machine91mapping91", "bWFjaGluZTkxbWFwcGluZzkx"),
    ("machine91record91", "bWFjaGluZTkxcmVjb3JkOTE"),
    ("machine91candle91", "bWFjaGluZTkxY2FuZGxlOTE"),
    ("machine91thread91", "bWFjaGluZTkxdGhyZWFkOTE"),
    ("learning91thread91", "bGVhcm5pbmc5MXRocmVhZDkx"),
    ("learning91kitten91", "bGVhcm5pbmc5MWtpdHRlbjkx"),
    ("learning91sitting91", "bGVhcm5pbmc5MXNpdHRpbmc5MQ"),
    ("learning91agent91", "bGVhcm5pbmc5MWFnZW50OTE"),
    ("model91agent91", "bW9kZWw5MWFnZW50OTE"),
    ("model91angle91", "bW9kZWw5MWFuZ2xlOTE"),
    ("model91universe91", "bW9kZWw5MXVuaXZlcnNlOTE"),
    ("model91memory91", "bW9kZWw5MW1lbW9yeTkx"),
    ("token91memory91", "dG9rZW45MW1lbW9yeTkx"),
    ("token91stream91", "dG9rZW45MXN0cmVhbTkx"),
    ("token91context91", "dG9rZW45MWNvbnRleHQ5MQ"),
    ("token91knowledge91", "dG9rZW45MWtub3dsZWRnZTkx"),
    ("prompt91knowledge91", "cHJvbXB0OTFrbm93bGVkZ2U5MQ"),
    ("prompt91vector91", "cHJvbXB0OTF2ZWN0b3I5MQ"),
    ("prompt91processor91", "cHJvbXB0OTFwcm9jZXNzb3I5MQ"),
    ("prompt91reasoning91", "cHJvbXB0OTFyZWFzb25pbmc5MQ"),
    ("session91reasoning91", "c2Vzc2lvbjkxcmVhc29uaW5nOTE"),
    ("session91machine91", "c2Vzc2lvbjkxbWFjaGluZTkx"),
    ("session91learning91", "c2Vzc2lvbjkxbGVhcm5pbmc5MQ"),
    ("session91model91", "c2Vzc2lvbjkxbW9kZWw5MQ"),
    ("library91model91", "bGlicmFyeTkxbW9kZWw5MQ"),
    ("library91token91", "bGlicmFyeTkxdG9rZW45MQ"),
    ("library91prompt91", "bGlicmFyeTkxcHJvbXB0OTE"),
    ("library91session91", "bGlicmFyeTkxc2Vzc2lvbjkx"),
    ("service91session91", "c2VydmljZTkxc2Vzc2lvbjkx"),
    ("service91library91", "c2VydmljZTkxbGlicmFyeTkx"),
    ("service91service91", "c2VydmljZTkxc2VydmljZTkx"),
    ("service91gateway91", "c2VydmljZTkxZ2F0ZXdheTkx"),
    ("gateway91gateway91", "Z2F0ZXdheTkxZ2F0ZXdheTkx"),
    ("gateway91storage91", "Z2F0ZXdheTkxc3RvcmFnZTkx"),
    ("gateway91network91", "Z2F0ZXdheTkxbmV0d29yazkx"),
    ("gateway91latency91", "Z2F0ZXdheTkxbGF0ZW5jeTkx"),
    ("storage91latency91", "c3RvcmFnZTkxbGF0ZW5jeTkx"),
    ("storage91buffer91", "c3RvcmFnZTkxYnVmZmVyOTE"),
    ("storage91queue91", "c3RvcmFnZTkxcXVldWU5MQ"),
    ("storage91worker91", "c3RvcmFnZTkxd29ya2VyOTE"),
    ("network91worker91", "bmV0d29yazkxd29ya2VyOTE"),
    ("network91kernel91", "bmV0d29yazkxa2VybmVsOTE"),
    ("network91signal91", "bmV0d29yazkxc2lnbmFsOTE"),
    ("network91packet91", "bmV0d29yazkxcGFja2V0OTE"),
    ("latency91packet91", "bGF0ZW5jeTkxcGFja2V0OTE"),
    ("latency91router91", "bGF0ZW5jeTkxcm91dGVyOTE"),
    ("latency91cluster91", "bGF0ZW5jeTkxY2x1c3Rlcjkx"),
    ("latency91mirror91", "bGF0ZW5jeTkxbWlycm9yOTE"),
    ("buffer91mirror91", "YnVmZmVyOTFtaXJyb3I5MQ"),
    ("buffer91filter91", "YnVmZmVyOTFmaWx0ZXI5MQ"),
    ("buffer91ranking91", "YnVmZmVyOTFyYW5raW5nOTE"),
    ("buffer91encoding91", "YnVmZmVyOTFlbmNvZGluZzkx"),
    ("queue91encoding91", "cXVldWU5MWVuY29kaW5nOTE"),
    ("queue91mapping91", "cXVldWU5MW1hcHBpbmc5MQ"),
    ("queue91record91", "cXVldWU5MXJlY29yZDkx"),
    ("queue91candle91", "cXVldWU5MWNhbmRsZTkx"),
    ("worker91candle91", "d29ya2VyOTFjYW5kbGU5MQ"),
    ("worker91thread91", "d29ya2VyOTF0aHJlYWQ5MQ"),
    ("worker91kitten91", "d29ya2VyOTFraXR0ZW45MQ"),
    ("worker91sitting91", "d29ya2VyOTFzaXR0aW5nOTE"),
    ("kernel91sitting91", "a2VybmVsOTFzaXR0aW5nOTE"),
    ("kernel91agent91", "a2VybmVsOTFhZ2VudDkx"),
    ("kernel91angle91", "a2VybmVsOTFhbmdsZTkx"),
    ("kernel91universe91", "a2VybmVsOTF1bml2ZXJzZTkx"),
    ("signal91universe91", "c2lnbmFsOTF1bml2ZXJzZTkx"),
    ("signal91memory91", "c2lnbmFsOTFtZW1vcnk5MQ"),
    ("signal91stream91", "c2lnbmFsOTFzdHJlYW05MQ"),
    ("signal91context91", "c2lnbmFsOTFjb250ZXh0OTE"),
    ("packet91context91", "cGFja2V0OTFjb250ZXh0OTE"),
    ("packet91knowledge91", "cGFja2V0OTFrbm93bGVkZ2U5MQ"),
    ("packet91vector91", "cGFja2V0OTF2ZWN0b3I5MQ"),
    ("packet91processor91", "cGFja2V0OTFwcm9jZXNzb3I5MQ"),
    ("router91processor91", "cm91dGVyOTFwcm9jZXNzb3I5MQ"),
    ("router91reasoning91", "cm91dGVyOTFyZWFzb25pbmc5MQ"),
    ("router91machine91", "cm91dGVyOTFtYWNoaW5lOTE"),
    ("router91learning91", "cm91dGVyOTFsZWFybmluZzkx"),
    ("cluster91learning91", "Y2x1c3RlcjkxbGVhcm5pbmc5MQ"),
    ("cluster91model91", "Y2x1c3RlcjkxbW9kZWw5MQ"),
    ("cluster91token91", "Y2x1c3RlcjkxdG9rZW45MQ"),
    ("cluster91prompt91", "Y2x1c3RlcjkxcHJvbXB0OTE"),
    ("mirror91prompt91", "bWlycm9yOTFwcm9tcHQ5MQ"),
    ("mirror91session91", "bWlycm9yOTFzZXNzaW9uOTE"),
    ("mirror91library91", "bWlycm9yOTFsaWJyYXJ5OTE"),
    ("mirror91service91", "bWlycm9yOTFzZXJ2aWNlOTE"),
    ("filter91service91", "ZmlsdGVyOTFzZXJ2aWNlOTE"),
    ("filter91gateway91", "ZmlsdGVyOTFnYXRld2F5OTE"),
    ("filter91storage91", "ZmlsdGVyOTFzdG9yYWdlOTE"),
    ("filter91network91", "ZmlsdGVyOTFuZXR3b3JrOTE"),
    ("ranking91network91", "cmFua2luZzkxbmV0d29yazkx"),
    ("ranking91latency91", "cmFua2luZzkxbGF0ZW5jeTkx"),
    ("ranking91buffer91", "cmFua2luZzkxYnVmZmVyOTE"),
    ("ranking91queue91", "cmFua2luZzkxcXVldWU5MQ"),
    ("encoding91queue91", "ZW5jb2Rpbmc5MXF1ZXVlOTE"),
    ("encoding91worker91", "ZW5jb2Rpbmc5MXdvcmtlcjkx"),
    ("encoding91kernel91", "ZW5jb2Rpbmc5MWtlcm5lbDkx"),
    ("encoding91signal91", "ZW5jb2Rpbmc5MXNpZ25hbDkx"),
    ("mapping91signal91", "bWFwcGluZzkxc2lnbmFsOTE"),
    ("mapping91packet91", "bWFwcGluZzkxcGFja2V0OTE"),
    ("mapping91router91", "bWFwcGluZzkxcm91dGVyOTE"),
    ("mapping91cluster91", "bWFwcGluZzkxY2x1c3Rlcjkx"),
    ("record91cluster91", "cmVjb3JkOTFjbHVzdGVyOTE"),
    ("record91mirror91", "cmVjb3JkOTFtaXJyb3I5MQ"),
    ("record91filter91", "cmVjb3JkOTFmaWx0ZXI5MQ"),
    ("record91ranking91", "cmVjb3JkOTFyYW5raW5nOTE"),
    ("candle91ranking91", "Y2FuZGxlOTFyYW5raW5nOTE"),
    ("candle91encoding91", "Y2FuZGxlOTFlbmNvZGluZzkx"),
    ("candle91mapping91", "Y2FuZGxlOTFtYXBwaW5nOTE"),
    ("candle91record91", "Y2FuZGxlOTFyZWNvcmQ5MQ"),
    ("thread91record91", "dGhyZWFkOTFyZWNvcmQ5MQ"),
    ("thread91candle91", "dGhyZWFkOTFjYW5kbGU5MQ"),
    ("thread91thread91", "dGhyZWFkOTF0aHJlYWQ5MQ"),
    ("thread91kitten91", "dGhyZWFkOTFraXR0ZW45MQ"),
    (
        "round 91: the quick brown fox jumps over the lazy dog",
        "cm91bmQgOTE6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 91: agentuniverse is a framework for multi agents",
        "cm91bmQgOTE6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 91: knowledge stored as vectors enables retrieval",
        "cm91bmQgOTE6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 91: the processor reads the record then stops",
        "cm91bmQgOTE6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 91: a worker pulls the next task from the queue",
        "cm91bmQgOTE6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 91: signals travel through the network layer",
        "cm91bmQgOTE6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 91: the gateway routes each request by policy",
        "cm91bmQgOTE6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 91: memory grows until the buffer is full",
        "cm91bmQgOTE6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 91: the cluster mirrors every packet twice",
        "cm91bmQgOTE6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 91: ranking uses tokens learned from the corpus",
        "cm91bmQgOTE6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 91: a long session ends when the candle dies",
        "cm91bmQgOTE6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 91: encode the prompt then map the result",
        "cm91bmQgOTE6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 91: the kernel wakes the worker at dawn", "cm91bmQgOTE6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 91: service latency drops after the patch",
        "cm91bmQgOTE6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 91: the library caches every vector it sees",
        "cm91bmQgOTE6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 91: agents argue then the debate resolves",
        "cm91bmQgOTE6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 91: the filter keeps only strong matches",
        "cm91bmQgOTE6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 91: the model answers with a short reply",
        "cm91bmQgOTE6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 91: the recorder stores the reasoning trace",
        "cm91bmQgOTE6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 91: the angel watches the processor run", "cm91bmQgOTE6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 91: angle of the vector decides the match",
        "cm91bmQgOTE6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 91: the candle burns twice as long at night",
        "cm91bmQgOTE6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 91: a mirror of the universe in one line",
        "cm91bmQgOTE6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 91: the queue drains before the storm", "cm91bmQgOTE6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
