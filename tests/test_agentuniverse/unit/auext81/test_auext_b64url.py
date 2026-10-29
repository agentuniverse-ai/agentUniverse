"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten81kitten81", "a2l0dGVuODFraXR0ZW44MQ"),
    ("kitten81sitting81", "a2l0dGVuODFzaXR0aW5nODE"),
    ("kitten81agent81", "a2l0dGVuODFhZ2VudDgx"),
    ("kitten81angle81", "a2l0dGVuODFhbmdsZTgx"),
    ("sitting81angle81", "c2l0dGluZzgxYW5nbGU4MQ"),
    ("sitting81universe81", "c2l0dGluZzgxdW5pdmVyc2U4MQ"),
    ("sitting81memory81", "c2l0dGluZzgxbWVtb3J5ODE"),
    ("sitting81stream81", "c2l0dGluZzgxc3RyZWFtODE"),
    ("agent81stream81", "YWdlbnQ4MXN0cmVhbTgx"),
    ("agent81context81", "YWdlbnQ4MWNvbnRleHQ4MQ"),
    ("agent81knowledge81", "YWdlbnQ4MWtub3dsZWRnZTgx"),
    ("agent81vector81", "YWdlbnQ4MXZlY3Rvcjgx"),
    ("angle81vector81", "YW5nbGU4MXZlY3Rvcjgx"),
    ("angle81processor81", "YW5nbGU4MXByb2Nlc3Nvcjgx"),
    ("angle81reasoning81", "YW5nbGU4MXJlYXNvbmluZzgx"),
    ("angle81machine81", "YW5nbGU4MW1hY2hpbmU4MQ"),
    ("universe81machine81", "dW5pdmVyc2U4MW1hY2hpbmU4MQ"),
    ("universe81learning81", "dW5pdmVyc2U4MWxlYXJuaW5nODE"),
    ("universe81model81", "dW5pdmVyc2U4MW1vZGVsODE"),
    ("universe81token81", "dW5pdmVyc2U4MXRva2VuODE"),
    ("memory81token81", "bWVtb3J5ODF0b2tlbjgx"),
    ("memory81prompt81", "bWVtb3J5ODFwcm9tcHQ4MQ"),
    ("memory81session81", "bWVtb3J5ODFzZXNzaW9uODE"),
    ("memory81library81", "bWVtb3J5ODFsaWJyYXJ5ODE"),
    ("stream81library81", "c3RyZWFtODFsaWJyYXJ5ODE"),
    ("stream81service81", "c3RyZWFtODFzZXJ2aWNlODE"),
    ("stream81gateway81", "c3RyZWFtODFnYXRld2F5ODE"),
    ("stream81storage81", "c3RyZWFtODFzdG9yYWdlODE"),
    ("context81storage81", "Y29udGV4dDgxc3RvcmFnZTgx"),
    ("context81network81", "Y29udGV4dDgxbmV0d29yazgx"),
    ("context81latency81", "Y29udGV4dDgxbGF0ZW5jeTgx"),
    ("context81buffer81", "Y29udGV4dDgxYnVmZmVyODE"),
    ("knowledge81buffer81", "a25vd2xlZGdlODFidWZmZXI4MQ"),
    ("knowledge81queue81", "a25vd2xlZGdlODFxdWV1ZTgx"),
    ("knowledge81worker81", "a25vd2xlZGdlODF3b3JrZXI4MQ"),
    ("knowledge81kernel81", "a25vd2xlZGdlODFrZXJuZWw4MQ"),
    ("vector81kernel81", "dmVjdG9yODFrZXJuZWw4MQ"),
    ("vector81signal81", "dmVjdG9yODFzaWduYWw4MQ"),
    ("vector81packet81", "dmVjdG9yODFwYWNrZXQ4MQ"),
    ("vector81router81", "dmVjdG9yODFyb3V0ZXI4MQ"),
    ("processor81router81", "cHJvY2Vzc29yODFyb3V0ZXI4MQ"),
    ("processor81cluster81", "cHJvY2Vzc29yODFjbHVzdGVyODE"),
    ("processor81mirror81", "cHJvY2Vzc29yODFtaXJyb3I4MQ"),
    ("processor81filter81", "cHJvY2Vzc29yODFmaWx0ZXI4MQ"),
    ("reasoning81filter81", "cmVhc29uaW5nODFmaWx0ZXI4MQ"),
    ("reasoning81ranking81", "cmVhc29uaW5nODFyYW5raW5nODE"),
    ("reasoning81encoding81", "cmVhc29uaW5nODFlbmNvZGluZzgx"),
    ("reasoning81mapping81", "cmVhc29uaW5nODFtYXBwaW5nODE"),
    ("machine81mapping81", "bWFjaGluZTgxbWFwcGluZzgx"),
    ("machine81record81", "bWFjaGluZTgxcmVjb3JkODE"),
    ("machine81candle81", "bWFjaGluZTgxY2FuZGxlODE"),
    ("machine81thread81", "bWFjaGluZTgxdGhyZWFkODE"),
    ("learning81thread81", "bGVhcm5pbmc4MXRocmVhZDgx"),
    ("learning81kitten81", "bGVhcm5pbmc4MWtpdHRlbjgx"),
    ("learning81sitting81", "bGVhcm5pbmc4MXNpdHRpbmc4MQ"),
    ("learning81agent81", "bGVhcm5pbmc4MWFnZW50ODE"),
    ("model81agent81", "bW9kZWw4MWFnZW50ODE"),
    ("model81angle81", "bW9kZWw4MWFuZ2xlODE"),
    ("model81universe81", "bW9kZWw4MXVuaXZlcnNlODE"),
    ("model81memory81", "bW9kZWw4MW1lbW9yeTgx"),
    ("token81memory81", "dG9rZW44MW1lbW9yeTgx"),
    ("token81stream81", "dG9rZW44MXN0cmVhbTgx"),
    ("token81context81", "dG9rZW44MWNvbnRleHQ4MQ"),
    ("token81knowledge81", "dG9rZW44MWtub3dsZWRnZTgx"),
    ("prompt81knowledge81", "cHJvbXB0ODFrbm93bGVkZ2U4MQ"),
    ("prompt81vector81", "cHJvbXB0ODF2ZWN0b3I4MQ"),
    ("prompt81processor81", "cHJvbXB0ODFwcm9jZXNzb3I4MQ"),
    ("prompt81reasoning81", "cHJvbXB0ODFyZWFzb25pbmc4MQ"),
    ("session81reasoning81", "c2Vzc2lvbjgxcmVhc29uaW5nODE"),
    ("session81machine81", "c2Vzc2lvbjgxbWFjaGluZTgx"),
    ("session81learning81", "c2Vzc2lvbjgxbGVhcm5pbmc4MQ"),
    ("session81model81", "c2Vzc2lvbjgxbW9kZWw4MQ"),
    ("library81model81", "bGlicmFyeTgxbW9kZWw4MQ"),
    ("library81token81", "bGlicmFyeTgxdG9rZW44MQ"),
    ("library81prompt81", "bGlicmFyeTgxcHJvbXB0ODE"),
    ("library81session81", "bGlicmFyeTgxc2Vzc2lvbjgx"),
    ("service81session81", "c2VydmljZTgxc2Vzc2lvbjgx"),
    ("service81library81", "c2VydmljZTgxbGlicmFyeTgx"),
    ("service81service81", "c2VydmljZTgxc2VydmljZTgx"),
    ("service81gateway81", "c2VydmljZTgxZ2F0ZXdheTgx"),
    ("gateway81gateway81", "Z2F0ZXdheTgxZ2F0ZXdheTgx"),
    ("gateway81storage81", "Z2F0ZXdheTgxc3RvcmFnZTgx"),
    ("gateway81network81", "Z2F0ZXdheTgxbmV0d29yazgx"),
    ("gateway81latency81", "Z2F0ZXdheTgxbGF0ZW5jeTgx"),
    ("storage81latency81", "c3RvcmFnZTgxbGF0ZW5jeTgx"),
    ("storage81buffer81", "c3RvcmFnZTgxYnVmZmVyODE"),
    ("storage81queue81", "c3RvcmFnZTgxcXVldWU4MQ"),
    ("storage81worker81", "c3RvcmFnZTgxd29ya2VyODE"),
    ("network81worker81", "bmV0d29yazgxd29ya2VyODE"),
    ("network81kernel81", "bmV0d29yazgxa2VybmVsODE"),
    ("network81signal81", "bmV0d29yazgxc2lnbmFsODE"),
    ("network81packet81", "bmV0d29yazgxcGFja2V0ODE"),
    ("latency81packet81", "bGF0ZW5jeTgxcGFja2V0ODE"),
    ("latency81router81", "bGF0ZW5jeTgxcm91dGVyODE"),
    ("latency81cluster81", "bGF0ZW5jeTgxY2x1c3Rlcjgx"),
    ("latency81mirror81", "bGF0ZW5jeTgxbWlycm9yODE"),
    ("buffer81mirror81", "YnVmZmVyODFtaXJyb3I4MQ"),
    ("buffer81filter81", "YnVmZmVyODFmaWx0ZXI4MQ"),
    ("buffer81ranking81", "YnVmZmVyODFyYW5raW5nODE"),
    ("buffer81encoding81", "YnVmZmVyODFlbmNvZGluZzgx"),
    ("queue81encoding81", "cXVldWU4MWVuY29kaW5nODE"),
    ("queue81mapping81", "cXVldWU4MW1hcHBpbmc4MQ"),
    ("queue81record81", "cXVldWU4MXJlY29yZDgx"),
    ("queue81candle81", "cXVldWU4MWNhbmRsZTgx"),
    ("worker81candle81", "d29ya2VyODFjYW5kbGU4MQ"),
    ("worker81thread81", "d29ya2VyODF0aHJlYWQ4MQ"),
    ("worker81kitten81", "d29ya2VyODFraXR0ZW44MQ"),
    ("worker81sitting81", "d29ya2VyODFzaXR0aW5nODE"),
    ("kernel81sitting81", "a2VybmVsODFzaXR0aW5nODE"),
    ("kernel81agent81", "a2VybmVsODFhZ2VudDgx"),
    ("kernel81angle81", "a2VybmVsODFhbmdsZTgx"),
    ("kernel81universe81", "a2VybmVsODF1bml2ZXJzZTgx"),
    ("signal81universe81", "c2lnbmFsODF1bml2ZXJzZTgx"),
    ("signal81memory81", "c2lnbmFsODFtZW1vcnk4MQ"),
    ("signal81stream81", "c2lnbmFsODFzdHJlYW04MQ"),
    ("signal81context81", "c2lnbmFsODFjb250ZXh0ODE"),
    ("packet81context81", "cGFja2V0ODFjb250ZXh0ODE"),
    ("packet81knowledge81", "cGFja2V0ODFrbm93bGVkZ2U4MQ"),
    ("packet81vector81", "cGFja2V0ODF2ZWN0b3I4MQ"),
    ("packet81processor81", "cGFja2V0ODFwcm9jZXNzb3I4MQ"),
    ("router81processor81", "cm91dGVyODFwcm9jZXNzb3I4MQ"),
    ("router81reasoning81", "cm91dGVyODFyZWFzb25pbmc4MQ"),
    ("router81machine81", "cm91dGVyODFtYWNoaW5lODE"),
    ("router81learning81", "cm91dGVyODFsZWFybmluZzgx"),
    ("cluster81learning81", "Y2x1c3RlcjgxbGVhcm5pbmc4MQ"),
    ("cluster81model81", "Y2x1c3RlcjgxbW9kZWw4MQ"),
    ("cluster81token81", "Y2x1c3RlcjgxdG9rZW44MQ"),
    ("cluster81prompt81", "Y2x1c3RlcjgxcHJvbXB0ODE"),
    ("mirror81prompt81", "bWlycm9yODFwcm9tcHQ4MQ"),
    ("mirror81session81", "bWlycm9yODFzZXNzaW9uODE"),
    ("mirror81library81", "bWlycm9yODFsaWJyYXJ5ODE"),
    ("mirror81service81", "bWlycm9yODFzZXJ2aWNlODE"),
    ("filter81service81", "ZmlsdGVyODFzZXJ2aWNlODE"),
    ("filter81gateway81", "ZmlsdGVyODFnYXRld2F5ODE"),
    ("filter81storage81", "ZmlsdGVyODFzdG9yYWdlODE"),
    ("filter81network81", "ZmlsdGVyODFuZXR3b3JrODE"),
    ("ranking81network81", "cmFua2luZzgxbmV0d29yazgx"),
    ("ranking81latency81", "cmFua2luZzgxbGF0ZW5jeTgx"),
    ("ranking81buffer81", "cmFua2luZzgxYnVmZmVyODE"),
    ("ranking81queue81", "cmFua2luZzgxcXVldWU4MQ"),
    ("encoding81queue81", "ZW5jb2Rpbmc4MXF1ZXVlODE"),
    ("encoding81worker81", "ZW5jb2Rpbmc4MXdvcmtlcjgx"),
    ("encoding81kernel81", "ZW5jb2Rpbmc4MWtlcm5lbDgx"),
    ("encoding81signal81", "ZW5jb2Rpbmc4MXNpZ25hbDgx"),
    ("mapping81signal81", "bWFwcGluZzgxc2lnbmFsODE"),
    ("mapping81packet81", "bWFwcGluZzgxcGFja2V0ODE"),
    ("mapping81router81", "bWFwcGluZzgxcm91dGVyODE"),
    ("mapping81cluster81", "bWFwcGluZzgxY2x1c3Rlcjgx"),
    ("record81cluster81", "cmVjb3JkODFjbHVzdGVyODE"),
    ("record81mirror81", "cmVjb3JkODFtaXJyb3I4MQ"),
    ("record81filter81", "cmVjb3JkODFmaWx0ZXI4MQ"),
    ("record81ranking81", "cmVjb3JkODFyYW5raW5nODE"),
    ("candle81ranking81", "Y2FuZGxlODFyYW5raW5nODE"),
    ("candle81encoding81", "Y2FuZGxlODFlbmNvZGluZzgx"),
    ("candle81mapping81", "Y2FuZGxlODFtYXBwaW5nODE"),
    ("candle81record81", "Y2FuZGxlODFyZWNvcmQ4MQ"),
    ("thread81record81", "dGhyZWFkODFyZWNvcmQ4MQ"),
    ("thread81candle81", "dGhyZWFkODFjYW5kbGU4MQ"),
    ("thread81thread81", "dGhyZWFkODF0aHJlYWQ4MQ"),
    ("thread81kitten81", "dGhyZWFkODFraXR0ZW44MQ"),
    (
        "round 81: the quick brown fox jumps over the lazy dog",
        "cm91bmQgODE6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 81: agentuniverse is a framework for multi agents",
        "cm91bmQgODE6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 81: knowledge stored as vectors enables retrieval",
        "cm91bmQgODE6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 81: the processor reads the record then stops",
        "cm91bmQgODE6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 81: a worker pulls the next task from the queue",
        "cm91bmQgODE6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 81: signals travel through the network layer",
        "cm91bmQgODE6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 81: the gateway routes each request by policy",
        "cm91bmQgODE6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 81: memory grows until the buffer is full",
        "cm91bmQgODE6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 81: the cluster mirrors every packet twice",
        "cm91bmQgODE6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 81: ranking uses tokens learned from the corpus",
        "cm91bmQgODE6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 81: a long session ends when the candle dies",
        "cm91bmQgODE6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 81: encode the prompt then map the result",
        "cm91bmQgODE6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 81: the kernel wakes the worker at dawn", "cm91bmQgODE6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 81: service latency drops after the patch",
        "cm91bmQgODE6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 81: the library caches every vector it sees",
        "cm91bmQgODE6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 81: agents argue then the debate resolves",
        "cm91bmQgODE6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 81: the filter keeps only strong matches",
        "cm91bmQgODE6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 81: the model answers with a short reply",
        "cm91bmQgODE6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 81: the recorder stores the reasoning trace",
        "cm91bmQgODE6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 81: the angel watches the processor run", "cm91bmQgODE6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 81: angle of the vector decides the match",
        "cm91bmQgODE6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 81: the candle burns twice as long at night",
        "cm91bmQgODE6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 81: a mirror of the universe in one line",
        "cm91bmQgODE6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 81: the queue drains before the storm", "cm91bmQgODE6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
