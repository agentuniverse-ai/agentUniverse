"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten46kitten46", "a2l0dGVuNDZraXR0ZW40Ng"),
    ("kitten46sitting46", "a2l0dGVuNDZzaXR0aW5nNDY"),
    ("kitten46agent46", "a2l0dGVuNDZhZ2VudDQ2"),
    ("kitten46angle46", "a2l0dGVuNDZhbmdsZTQ2"),
    ("sitting46angle46", "c2l0dGluZzQ2YW5nbGU0Ng"),
    ("sitting46universe46", "c2l0dGluZzQ2dW5pdmVyc2U0Ng"),
    ("sitting46memory46", "c2l0dGluZzQ2bWVtb3J5NDY"),
    ("sitting46stream46", "c2l0dGluZzQ2c3RyZWFtNDY"),
    ("agent46stream46", "YWdlbnQ0NnN0cmVhbTQ2"),
    ("agent46context46", "YWdlbnQ0NmNvbnRleHQ0Ng"),
    ("agent46knowledge46", "YWdlbnQ0Nmtub3dsZWRnZTQ2"),
    ("agent46vector46", "YWdlbnQ0NnZlY3RvcjQ2"),
    ("angle46vector46", "YW5nbGU0NnZlY3RvcjQ2"),
    ("angle46processor46", "YW5nbGU0NnByb2Nlc3NvcjQ2"),
    ("angle46reasoning46", "YW5nbGU0NnJlYXNvbmluZzQ2"),
    ("angle46machine46", "YW5nbGU0Nm1hY2hpbmU0Ng"),
    ("universe46machine46", "dW5pdmVyc2U0Nm1hY2hpbmU0Ng"),
    ("universe46learning46", "dW5pdmVyc2U0NmxlYXJuaW5nNDY"),
    ("universe46model46", "dW5pdmVyc2U0Nm1vZGVsNDY"),
    ("universe46token46", "dW5pdmVyc2U0NnRva2VuNDY"),
    ("memory46token46", "bWVtb3J5NDZ0b2tlbjQ2"),
    ("memory46prompt46", "bWVtb3J5NDZwcm9tcHQ0Ng"),
    ("memory46session46", "bWVtb3J5NDZzZXNzaW9uNDY"),
    ("memory46library46", "bWVtb3J5NDZsaWJyYXJ5NDY"),
    ("stream46library46", "c3RyZWFtNDZsaWJyYXJ5NDY"),
    ("stream46service46", "c3RyZWFtNDZzZXJ2aWNlNDY"),
    ("stream46gateway46", "c3RyZWFtNDZnYXRld2F5NDY"),
    ("stream46storage46", "c3RyZWFtNDZzdG9yYWdlNDY"),
    ("context46storage46", "Y29udGV4dDQ2c3RvcmFnZTQ2"),
    ("context46network46", "Y29udGV4dDQ2bmV0d29yazQ2"),
    ("context46latency46", "Y29udGV4dDQ2bGF0ZW5jeTQ2"),
    ("context46buffer46", "Y29udGV4dDQ2YnVmZmVyNDY"),
    ("knowledge46buffer46", "a25vd2xlZGdlNDZidWZmZXI0Ng"),
    ("knowledge46queue46", "a25vd2xlZGdlNDZxdWV1ZTQ2"),
    ("knowledge46worker46", "a25vd2xlZGdlNDZ3b3JrZXI0Ng"),
    ("knowledge46kernel46", "a25vd2xlZGdlNDZrZXJuZWw0Ng"),
    ("vector46kernel46", "dmVjdG9yNDZrZXJuZWw0Ng"),
    ("vector46signal46", "dmVjdG9yNDZzaWduYWw0Ng"),
    ("vector46packet46", "dmVjdG9yNDZwYWNrZXQ0Ng"),
    ("vector46router46", "dmVjdG9yNDZyb3V0ZXI0Ng"),
    ("processor46router46", "cHJvY2Vzc29yNDZyb3V0ZXI0Ng"),
    ("processor46cluster46", "cHJvY2Vzc29yNDZjbHVzdGVyNDY"),
    ("processor46mirror46", "cHJvY2Vzc29yNDZtaXJyb3I0Ng"),
    ("processor46filter46", "cHJvY2Vzc29yNDZmaWx0ZXI0Ng"),
    ("reasoning46filter46", "cmVhc29uaW5nNDZmaWx0ZXI0Ng"),
    ("reasoning46ranking46", "cmVhc29uaW5nNDZyYW5raW5nNDY"),
    ("reasoning46encoding46", "cmVhc29uaW5nNDZlbmNvZGluZzQ2"),
    ("reasoning46mapping46", "cmVhc29uaW5nNDZtYXBwaW5nNDY"),
    ("machine46mapping46", "bWFjaGluZTQ2bWFwcGluZzQ2"),
    ("machine46record46", "bWFjaGluZTQ2cmVjb3JkNDY"),
    ("machine46candle46", "bWFjaGluZTQ2Y2FuZGxlNDY"),
    ("machine46thread46", "bWFjaGluZTQ2dGhyZWFkNDY"),
    ("learning46thread46", "bGVhcm5pbmc0NnRocmVhZDQ2"),
    ("learning46kitten46", "bGVhcm5pbmc0NmtpdHRlbjQ2"),
    ("learning46sitting46", "bGVhcm5pbmc0NnNpdHRpbmc0Ng"),
    ("learning46agent46", "bGVhcm5pbmc0NmFnZW50NDY"),
    ("model46agent46", "bW9kZWw0NmFnZW50NDY"),
    ("model46angle46", "bW9kZWw0NmFuZ2xlNDY"),
    ("model46universe46", "bW9kZWw0NnVuaXZlcnNlNDY"),
    ("model46memory46", "bW9kZWw0Nm1lbW9yeTQ2"),
    ("token46memory46", "dG9rZW40Nm1lbW9yeTQ2"),
    ("token46stream46", "dG9rZW40NnN0cmVhbTQ2"),
    ("token46context46", "dG9rZW40NmNvbnRleHQ0Ng"),
    ("token46knowledge46", "dG9rZW40Nmtub3dsZWRnZTQ2"),
    ("prompt46knowledge46", "cHJvbXB0NDZrbm93bGVkZ2U0Ng"),
    ("prompt46vector46", "cHJvbXB0NDZ2ZWN0b3I0Ng"),
    ("prompt46processor46", "cHJvbXB0NDZwcm9jZXNzb3I0Ng"),
    ("prompt46reasoning46", "cHJvbXB0NDZyZWFzb25pbmc0Ng"),
    ("session46reasoning46", "c2Vzc2lvbjQ2cmVhc29uaW5nNDY"),
    ("session46machine46", "c2Vzc2lvbjQ2bWFjaGluZTQ2"),
    ("session46learning46", "c2Vzc2lvbjQ2bGVhcm5pbmc0Ng"),
    ("session46model46", "c2Vzc2lvbjQ2bW9kZWw0Ng"),
    ("library46model46", "bGlicmFyeTQ2bW9kZWw0Ng"),
    ("library46token46", "bGlicmFyeTQ2dG9rZW40Ng"),
    ("library46prompt46", "bGlicmFyeTQ2cHJvbXB0NDY"),
    ("library46session46", "bGlicmFyeTQ2c2Vzc2lvbjQ2"),
    ("service46session46", "c2VydmljZTQ2c2Vzc2lvbjQ2"),
    ("service46library46", "c2VydmljZTQ2bGlicmFyeTQ2"),
    ("service46service46", "c2VydmljZTQ2c2VydmljZTQ2"),
    ("service46gateway46", "c2VydmljZTQ2Z2F0ZXdheTQ2"),
    ("gateway46gateway46", "Z2F0ZXdheTQ2Z2F0ZXdheTQ2"),
    ("gateway46storage46", "Z2F0ZXdheTQ2c3RvcmFnZTQ2"),
    ("gateway46network46", "Z2F0ZXdheTQ2bmV0d29yazQ2"),
    ("gateway46latency46", "Z2F0ZXdheTQ2bGF0ZW5jeTQ2"),
    ("storage46latency46", "c3RvcmFnZTQ2bGF0ZW5jeTQ2"),
    ("storage46buffer46", "c3RvcmFnZTQ2YnVmZmVyNDY"),
    ("storage46queue46", "c3RvcmFnZTQ2cXVldWU0Ng"),
    ("storage46worker46", "c3RvcmFnZTQ2d29ya2VyNDY"),
    ("network46worker46", "bmV0d29yazQ2d29ya2VyNDY"),
    ("network46kernel46", "bmV0d29yazQ2a2VybmVsNDY"),
    ("network46signal46", "bmV0d29yazQ2c2lnbmFsNDY"),
    ("network46packet46", "bmV0d29yazQ2cGFja2V0NDY"),
    ("latency46packet46", "bGF0ZW5jeTQ2cGFja2V0NDY"),
    ("latency46router46", "bGF0ZW5jeTQ2cm91dGVyNDY"),
    ("latency46cluster46", "bGF0ZW5jeTQ2Y2x1c3RlcjQ2"),
    ("latency46mirror46", "bGF0ZW5jeTQ2bWlycm9yNDY"),
    ("buffer46mirror46", "YnVmZmVyNDZtaXJyb3I0Ng"),
    ("buffer46filter46", "YnVmZmVyNDZmaWx0ZXI0Ng"),
    ("buffer46ranking46", "YnVmZmVyNDZyYW5raW5nNDY"),
    ("buffer46encoding46", "YnVmZmVyNDZlbmNvZGluZzQ2"),
    ("queue46encoding46", "cXVldWU0NmVuY29kaW5nNDY"),
    ("queue46mapping46", "cXVldWU0Nm1hcHBpbmc0Ng"),
    ("queue46record46", "cXVldWU0NnJlY29yZDQ2"),
    ("queue46candle46", "cXVldWU0NmNhbmRsZTQ2"),
    ("worker46candle46", "d29ya2VyNDZjYW5kbGU0Ng"),
    ("worker46thread46", "d29ya2VyNDZ0aHJlYWQ0Ng"),
    ("worker46kitten46", "d29ya2VyNDZraXR0ZW40Ng"),
    ("worker46sitting46", "d29ya2VyNDZzaXR0aW5nNDY"),
    ("kernel46sitting46", "a2VybmVsNDZzaXR0aW5nNDY"),
    ("kernel46agent46", "a2VybmVsNDZhZ2VudDQ2"),
    ("kernel46angle46", "a2VybmVsNDZhbmdsZTQ2"),
    ("kernel46universe46", "a2VybmVsNDZ1bml2ZXJzZTQ2"),
    ("signal46universe46", "c2lnbmFsNDZ1bml2ZXJzZTQ2"),
    ("signal46memory46", "c2lnbmFsNDZtZW1vcnk0Ng"),
    ("signal46stream46", "c2lnbmFsNDZzdHJlYW00Ng"),
    ("signal46context46", "c2lnbmFsNDZjb250ZXh0NDY"),
    ("packet46context46", "cGFja2V0NDZjb250ZXh0NDY"),
    ("packet46knowledge46", "cGFja2V0NDZrbm93bGVkZ2U0Ng"),
    ("packet46vector46", "cGFja2V0NDZ2ZWN0b3I0Ng"),
    ("packet46processor46", "cGFja2V0NDZwcm9jZXNzb3I0Ng"),
    ("router46processor46", "cm91dGVyNDZwcm9jZXNzb3I0Ng"),
    ("router46reasoning46", "cm91dGVyNDZyZWFzb25pbmc0Ng"),
    ("router46machine46", "cm91dGVyNDZtYWNoaW5lNDY"),
    ("router46learning46", "cm91dGVyNDZsZWFybmluZzQ2"),
    ("cluster46learning46", "Y2x1c3RlcjQ2bGVhcm5pbmc0Ng"),
    ("cluster46model46", "Y2x1c3RlcjQ2bW9kZWw0Ng"),
    ("cluster46token46", "Y2x1c3RlcjQ2dG9rZW40Ng"),
    ("cluster46prompt46", "Y2x1c3RlcjQ2cHJvbXB0NDY"),
    ("mirror46prompt46", "bWlycm9yNDZwcm9tcHQ0Ng"),
    ("mirror46session46", "bWlycm9yNDZzZXNzaW9uNDY"),
    ("mirror46library46", "bWlycm9yNDZsaWJyYXJ5NDY"),
    ("mirror46service46", "bWlycm9yNDZzZXJ2aWNlNDY"),
    ("filter46service46", "ZmlsdGVyNDZzZXJ2aWNlNDY"),
    ("filter46gateway46", "ZmlsdGVyNDZnYXRld2F5NDY"),
    ("filter46storage46", "ZmlsdGVyNDZzdG9yYWdlNDY"),
    ("filter46network46", "ZmlsdGVyNDZuZXR3b3JrNDY"),
    ("ranking46network46", "cmFua2luZzQ2bmV0d29yazQ2"),
    ("ranking46latency46", "cmFua2luZzQ2bGF0ZW5jeTQ2"),
    ("ranking46buffer46", "cmFua2luZzQ2YnVmZmVyNDY"),
    ("ranking46queue46", "cmFua2luZzQ2cXVldWU0Ng"),
    ("encoding46queue46", "ZW5jb2Rpbmc0NnF1ZXVlNDY"),
    ("encoding46worker46", "ZW5jb2Rpbmc0NndvcmtlcjQ2"),
    ("encoding46kernel46", "ZW5jb2Rpbmc0Nmtlcm5lbDQ2"),
    ("encoding46signal46", "ZW5jb2Rpbmc0NnNpZ25hbDQ2"),
    ("mapping46signal46", "bWFwcGluZzQ2c2lnbmFsNDY"),
    ("mapping46packet46", "bWFwcGluZzQ2cGFja2V0NDY"),
    ("mapping46router46", "bWFwcGluZzQ2cm91dGVyNDY"),
    ("mapping46cluster46", "bWFwcGluZzQ2Y2x1c3RlcjQ2"),
    ("record46cluster46", "cmVjb3JkNDZjbHVzdGVyNDY"),
    ("record46mirror46", "cmVjb3JkNDZtaXJyb3I0Ng"),
    ("record46filter46", "cmVjb3JkNDZmaWx0ZXI0Ng"),
    ("record46ranking46", "cmVjb3JkNDZyYW5raW5nNDY"),
    ("candle46ranking46", "Y2FuZGxlNDZyYW5raW5nNDY"),
    ("candle46encoding46", "Y2FuZGxlNDZlbmNvZGluZzQ2"),
    ("candle46mapping46", "Y2FuZGxlNDZtYXBwaW5nNDY"),
    ("candle46record46", "Y2FuZGxlNDZyZWNvcmQ0Ng"),
    ("thread46record46", "dGhyZWFkNDZyZWNvcmQ0Ng"),
    ("thread46candle46", "dGhyZWFkNDZjYW5kbGU0Ng"),
    ("thread46thread46", "dGhyZWFkNDZ0aHJlYWQ0Ng"),
    ("thread46kitten46", "dGhyZWFkNDZraXR0ZW40Ng"),
    (
        "round 46: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNDY6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 46: agentuniverse is a framework for multi agents",
        "cm91bmQgNDY6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 46: knowledge stored as vectors enables retrieval",
        "cm91bmQgNDY6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 46: the processor reads the record then stops",
        "cm91bmQgNDY6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 46: a worker pulls the next task from the queue",
        "cm91bmQgNDY6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 46: signals travel through the network layer",
        "cm91bmQgNDY6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 46: the gateway routes each request by policy",
        "cm91bmQgNDY6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 46: memory grows until the buffer is full",
        "cm91bmQgNDY6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 46: the cluster mirrors every packet twice",
        "cm91bmQgNDY6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 46: ranking uses tokens learned from the corpus",
        "cm91bmQgNDY6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 46: a long session ends when the candle dies",
        "cm91bmQgNDY6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 46: encode the prompt then map the result",
        "cm91bmQgNDY6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 46: the kernel wakes the worker at dawn", "cm91bmQgNDY6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 46: service latency drops after the patch",
        "cm91bmQgNDY6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 46: the library caches every vector it sees",
        "cm91bmQgNDY6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 46: agents argue then the debate resolves",
        "cm91bmQgNDY6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 46: the filter keeps only strong matches",
        "cm91bmQgNDY6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 46: the model answers with a short reply",
        "cm91bmQgNDY6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 46: the recorder stores the reasoning trace",
        "cm91bmQgNDY6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 46: the angel watches the processor run", "cm91bmQgNDY6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 46: angle of the vector decides the match",
        "cm91bmQgNDY6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 46: the candle burns twice as long at night",
        "cm91bmQgNDY6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 46: a mirror of the universe in one line",
        "cm91bmQgNDY6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 46: the queue drains before the storm", "cm91bmQgNDY6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
