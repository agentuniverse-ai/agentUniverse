"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten41kitten41", "a2l0dGVuNDFraXR0ZW40MQ"),
    ("kitten41sitting41", "a2l0dGVuNDFzaXR0aW5nNDE"),
    ("kitten41agent41", "a2l0dGVuNDFhZ2VudDQx"),
    ("kitten41angle41", "a2l0dGVuNDFhbmdsZTQx"),
    ("sitting41angle41", "c2l0dGluZzQxYW5nbGU0MQ"),
    ("sitting41universe41", "c2l0dGluZzQxdW5pdmVyc2U0MQ"),
    ("sitting41memory41", "c2l0dGluZzQxbWVtb3J5NDE"),
    ("sitting41stream41", "c2l0dGluZzQxc3RyZWFtNDE"),
    ("agent41stream41", "YWdlbnQ0MXN0cmVhbTQx"),
    ("agent41context41", "YWdlbnQ0MWNvbnRleHQ0MQ"),
    ("agent41knowledge41", "YWdlbnQ0MWtub3dsZWRnZTQx"),
    ("agent41vector41", "YWdlbnQ0MXZlY3RvcjQx"),
    ("angle41vector41", "YW5nbGU0MXZlY3RvcjQx"),
    ("angle41processor41", "YW5nbGU0MXByb2Nlc3NvcjQx"),
    ("angle41reasoning41", "YW5nbGU0MXJlYXNvbmluZzQx"),
    ("angle41machine41", "YW5nbGU0MW1hY2hpbmU0MQ"),
    ("universe41machine41", "dW5pdmVyc2U0MW1hY2hpbmU0MQ"),
    ("universe41learning41", "dW5pdmVyc2U0MWxlYXJuaW5nNDE"),
    ("universe41model41", "dW5pdmVyc2U0MW1vZGVsNDE"),
    ("universe41token41", "dW5pdmVyc2U0MXRva2VuNDE"),
    ("memory41token41", "bWVtb3J5NDF0b2tlbjQx"),
    ("memory41prompt41", "bWVtb3J5NDFwcm9tcHQ0MQ"),
    ("memory41session41", "bWVtb3J5NDFzZXNzaW9uNDE"),
    ("memory41library41", "bWVtb3J5NDFsaWJyYXJ5NDE"),
    ("stream41library41", "c3RyZWFtNDFsaWJyYXJ5NDE"),
    ("stream41service41", "c3RyZWFtNDFzZXJ2aWNlNDE"),
    ("stream41gateway41", "c3RyZWFtNDFnYXRld2F5NDE"),
    ("stream41storage41", "c3RyZWFtNDFzdG9yYWdlNDE"),
    ("context41storage41", "Y29udGV4dDQxc3RvcmFnZTQx"),
    ("context41network41", "Y29udGV4dDQxbmV0d29yazQx"),
    ("context41latency41", "Y29udGV4dDQxbGF0ZW5jeTQx"),
    ("context41buffer41", "Y29udGV4dDQxYnVmZmVyNDE"),
    ("knowledge41buffer41", "a25vd2xlZGdlNDFidWZmZXI0MQ"),
    ("knowledge41queue41", "a25vd2xlZGdlNDFxdWV1ZTQx"),
    ("knowledge41worker41", "a25vd2xlZGdlNDF3b3JrZXI0MQ"),
    ("knowledge41kernel41", "a25vd2xlZGdlNDFrZXJuZWw0MQ"),
    ("vector41kernel41", "dmVjdG9yNDFrZXJuZWw0MQ"),
    ("vector41signal41", "dmVjdG9yNDFzaWduYWw0MQ"),
    ("vector41packet41", "dmVjdG9yNDFwYWNrZXQ0MQ"),
    ("vector41router41", "dmVjdG9yNDFyb3V0ZXI0MQ"),
    ("processor41router41", "cHJvY2Vzc29yNDFyb3V0ZXI0MQ"),
    ("processor41cluster41", "cHJvY2Vzc29yNDFjbHVzdGVyNDE"),
    ("processor41mirror41", "cHJvY2Vzc29yNDFtaXJyb3I0MQ"),
    ("processor41filter41", "cHJvY2Vzc29yNDFmaWx0ZXI0MQ"),
    ("reasoning41filter41", "cmVhc29uaW5nNDFmaWx0ZXI0MQ"),
    ("reasoning41ranking41", "cmVhc29uaW5nNDFyYW5raW5nNDE"),
    ("reasoning41encoding41", "cmVhc29uaW5nNDFlbmNvZGluZzQx"),
    ("reasoning41mapping41", "cmVhc29uaW5nNDFtYXBwaW5nNDE"),
    ("machine41mapping41", "bWFjaGluZTQxbWFwcGluZzQx"),
    ("machine41record41", "bWFjaGluZTQxcmVjb3JkNDE"),
    ("machine41candle41", "bWFjaGluZTQxY2FuZGxlNDE"),
    ("machine41thread41", "bWFjaGluZTQxdGhyZWFkNDE"),
    ("learning41thread41", "bGVhcm5pbmc0MXRocmVhZDQx"),
    ("learning41kitten41", "bGVhcm5pbmc0MWtpdHRlbjQx"),
    ("learning41sitting41", "bGVhcm5pbmc0MXNpdHRpbmc0MQ"),
    ("learning41agent41", "bGVhcm5pbmc0MWFnZW50NDE"),
    ("model41agent41", "bW9kZWw0MWFnZW50NDE"),
    ("model41angle41", "bW9kZWw0MWFuZ2xlNDE"),
    ("model41universe41", "bW9kZWw0MXVuaXZlcnNlNDE"),
    ("model41memory41", "bW9kZWw0MW1lbW9yeTQx"),
    ("token41memory41", "dG9rZW40MW1lbW9yeTQx"),
    ("token41stream41", "dG9rZW40MXN0cmVhbTQx"),
    ("token41context41", "dG9rZW40MWNvbnRleHQ0MQ"),
    ("token41knowledge41", "dG9rZW40MWtub3dsZWRnZTQx"),
    ("prompt41knowledge41", "cHJvbXB0NDFrbm93bGVkZ2U0MQ"),
    ("prompt41vector41", "cHJvbXB0NDF2ZWN0b3I0MQ"),
    ("prompt41processor41", "cHJvbXB0NDFwcm9jZXNzb3I0MQ"),
    ("prompt41reasoning41", "cHJvbXB0NDFyZWFzb25pbmc0MQ"),
    ("session41reasoning41", "c2Vzc2lvbjQxcmVhc29uaW5nNDE"),
    ("session41machine41", "c2Vzc2lvbjQxbWFjaGluZTQx"),
    ("session41learning41", "c2Vzc2lvbjQxbGVhcm5pbmc0MQ"),
    ("session41model41", "c2Vzc2lvbjQxbW9kZWw0MQ"),
    ("library41model41", "bGlicmFyeTQxbW9kZWw0MQ"),
    ("library41token41", "bGlicmFyeTQxdG9rZW40MQ"),
    ("library41prompt41", "bGlicmFyeTQxcHJvbXB0NDE"),
    ("library41session41", "bGlicmFyeTQxc2Vzc2lvbjQx"),
    ("service41session41", "c2VydmljZTQxc2Vzc2lvbjQx"),
    ("service41library41", "c2VydmljZTQxbGlicmFyeTQx"),
    ("service41service41", "c2VydmljZTQxc2VydmljZTQx"),
    ("service41gateway41", "c2VydmljZTQxZ2F0ZXdheTQx"),
    ("gateway41gateway41", "Z2F0ZXdheTQxZ2F0ZXdheTQx"),
    ("gateway41storage41", "Z2F0ZXdheTQxc3RvcmFnZTQx"),
    ("gateway41network41", "Z2F0ZXdheTQxbmV0d29yazQx"),
    ("gateway41latency41", "Z2F0ZXdheTQxbGF0ZW5jeTQx"),
    ("storage41latency41", "c3RvcmFnZTQxbGF0ZW5jeTQx"),
    ("storage41buffer41", "c3RvcmFnZTQxYnVmZmVyNDE"),
    ("storage41queue41", "c3RvcmFnZTQxcXVldWU0MQ"),
    ("storage41worker41", "c3RvcmFnZTQxd29ya2VyNDE"),
    ("network41worker41", "bmV0d29yazQxd29ya2VyNDE"),
    ("network41kernel41", "bmV0d29yazQxa2VybmVsNDE"),
    ("network41signal41", "bmV0d29yazQxc2lnbmFsNDE"),
    ("network41packet41", "bmV0d29yazQxcGFja2V0NDE"),
    ("latency41packet41", "bGF0ZW5jeTQxcGFja2V0NDE"),
    ("latency41router41", "bGF0ZW5jeTQxcm91dGVyNDE"),
    ("latency41cluster41", "bGF0ZW5jeTQxY2x1c3RlcjQx"),
    ("latency41mirror41", "bGF0ZW5jeTQxbWlycm9yNDE"),
    ("buffer41mirror41", "YnVmZmVyNDFtaXJyb3I0MQ"),
    ("buffer41filter41", "YnVmZmVyNDFmaWx0ZXI0MQ"),
    ("buffer41ranking41", "YnVmZmVyNDFyYW5raW5nNDE"),
    ("buffer41encoding41", "YnVmZmVyNDFlbmNvZGluZzQx"),
    ("queue41encoding41", "cXVldWU0MWVuY29kaW5nNDE"),
    ("queue41mapping41", "cXVldWU0MW1hcHBpbmc0MQ"),
    ("queue41record41", "cXVldWU0MXJlY29yZDQx"),
    ("queue41candle41", "cXVldWU0MWNhbmRsZTQx"),
    ("worker41candle41", "d29ya2VyNDFjYW5kbGU0MQ"),
    ("worker41thread41", "d29ya2VyNDF0aHJlYWQ0MQ"),
    ("worker41kitten41", "d29ya2VyNDFraXR0ZW40MQ"),
    ("worker41sitting41", "d29ya2VyNDFzaXR0aW5nNDE"),
    ("kernel41sitting41", "a2VybmVsNDFzaXR0aW5nNDE"),
    ("kernel41agent41", "a2VybmVsNDFhZ2VudDQx"),
    ("kernel41angle41", "a2VybmVsNDFhbmdsZTQx"),
    ("kernel41universe41", "a2VybmVsNDF1bml2ZXJzZTQx"),
    ("signal41universe41", "c2lnbmFsNDF1bml2ZXJzZTQx"),
    ("signal41memory41", "c2lnbmFsNDFtZW1vcnk0MQ"),
    ("signal41stream41", "c2lnbmFsNDFzdHJlYW00MQ"),
    ("signal41context41", "c2lnbmFsNDFjb250ZXh0NDE"),
    ("packet41context41", "cGFja2V0NDFjb250ZXh0NDE"),
    ("packet41knowledge41", "cGFja2V0NDFrbm93bGVkZ2U0MQ"),
    ("packet41vector41", "cGFja2V0NDF2ZWN0b3I0MQ"),
    ("packet41processor41", "cGFja2V0NDFwcm9jZXNzb3I0MQ"),
    ("router41processor41", "cm91dGVyNDFwcm9jZXNzb3I0MQ"),
    ("router41reasoning41", "cm91dGVyNDFyZWFzb25pbmc0MQ"),
    ("router41machine41", "cm91dGVyNDFtYWNoaW5lNDE"),
    ("router41learning41", "cm91dGVyNDFsZWFybmluZzQx"),
    ("cluster41learning41", "Y2x1c3RlcjQxbGVhcm5pbmc0MQ"),
    ("cluster41model41", "Y2x1c3RlcjQxbW9kZWw0MQ"),
    ("cluster41token41", "Y2x1c3RlcjQxdG9rZW40MQ"),
    ("cluster41prompt41", "Y2x1c3RlcjQxcHJvbXB0NDE"),
    ("mirror41prompt41", "bWlycm9yNDFwcm9tcHQ0MQ"),
    ("mirror41session41", "bWlycm9yNDFzZXNzaW9uNDE"),
    ("mirror41library41", "bWlycm9yNDFsaWJyYXJ5NDE"),
    ("mirror41service41", "bWlycm9yNDFzZXJ2aWNlNDE"),
    ("filter41service41", "ZmlsdGVyNDFzZXJ2aWNlNDE"),
    ("filter41gateway41", "ZmlsdGVyNDFnYXRld2F5NDE"),
    ("filter41storage41", "ZmlsdGVyNDFzdG9yYWdlNDE"),
    ("filter41network41", "ZmlsdGVyNDFuZXR3b3JrNDE"),
    ("ranking41network41", "cmFua2luZzQxbmV0d29yazQx"),
    ("ranking41latency41", "cmFua2luZzQxbGF0ZW5jeTQx"),
    ("ranking41buffer41", "cmFua2luZzQxYnVmZmVyNDE"),
    ("ranking41queue41", "cmFua2luZzQxcXVldWU0MQ"),
    ("encoding41queue41", "ZW5jb2Rpbmc0MXF1ZXVlNDE"),
    ("encoding41worker41", "ZW5jb2Rpbmc0MXdvcmtlcjQx"),
    ("encoding41kernel41", "ZW5jb2Rpbmc0MWtlcm5lbDQx"),
    ("encoding41signal41", "ZW5jb2Rpbmc0MXNpZ25hbDQx"),
    ("mapping41signal41", "bWFwcGluZzQxc2lnbmFsNDE"),
    ("mapping41packet41", "bWFwcGluZzQxcGFja2V0NDE"),
    ("mapping41router41", "bWFwcGluZzQxcm91dGVyNDE"),
    ("mapping41cluster41", "bWFwcGluZzQxY2x1c3RlcjQx"),
    ("record41cluster41", "cmVjb3JkNDFjbHVzdGVyNDE"),
    ("record41mirror41", "cmVjb3JkNDFtaXJyb3I0MQ"),
    ("record41filter41", "cmVjb3JkNDFmaWx0ZXI0MQ"),
    ("record41ranking41", "cmVjb3JkNDFyYW5raW5nNDE"),
    ("candle41ranking41", "Y2FuZGxlNDFyYW5raW5nNDE"),
    ("candle41encoding41", "Y2FuZGxlNDFlbmNvZGluZzQx"),
    ("candle41mapping41", "Y2FuZGxlNDFtYXBwaW5nNDE"),
    ("candle41record41", "Y2FuZGxlNDFyZWNvcmQ0MQ"),
    ("thread41record41", "dGhyZWFkNDFyZWNvcmQ0MQ"),
    ("thread41candle41", "dGhyZWFkNDFjYW5kbGU0MQ"),
    ("thread41thread41", "dGhyZWFkNDF0aHJlYWQ0MQ"),
    ("thread41kitten41", "dGhyZWFkNDFraXR0ZW40MQ"),
    (
        "round 41: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNDE6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 41: agentuniverse is a framework for multi agents",
        "cm91bmQgNDE6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 41: knowledge stored as vectors enables retrieval",
        "cm91bmQgNDE6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 41: the processor reads the record then stops",
        "cm91bmQgNDE6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 41: a worker pulls the next task from the queue",
        "cm91bmQgNDE6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 41: signals travel through the network layer",
        "cm91bmQgNDE6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 41: the gateway routes each request by policy",
        "cm91bmQgNDE6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 41: memory grows until the buffer is full",
        "cm91bmQgNDE6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 41: the cluster mirrors every packet twice",
        "cm91bmQgNDE6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 41: ranking uses tokens learned from the corpus",
        "cm91bmQgNDE6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 41: a long session ends when the candle dies",
        "cm91bmQgNDE6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 41: encode the prompt then map the result",
        "cm91bmQgNDE6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 41: the kernel wakes the worker at dawn", "cm91bmQgNDE6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 41: service latency drops after the patch",
        "cm91bmQgNDE6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 41: the library caches every vector it sees",
        "cm91bmQgNDE6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 41: agents argue then the debate resolves",
        "cm91bmQgNDE6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 41: the filter keeps only strong matches",
        "cm91bmQgNDE6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 41: the model answers with a short reply",
        "cm91bmQgNDE6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 41: the recorder stores the reasoning trace",
        "cm91bmQgNDE6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 41: the angel watches the processor run", "cm91bmQgNDE6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 41: angle of the vector decides the match",
        "cm91bmQgNDE6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 41: the candle burns twice as long at night",
        "cm91bmQgNDE6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 41: a mirror of the universe in one line",
        "cm91bmQgNDE6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 41: the queue drains before the storm", "cm91bmQgNDE6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
