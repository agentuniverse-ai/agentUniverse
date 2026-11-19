"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten66kitten66", "a2l0dGVuNjZraXR0ZW42Ng"),
    ("kitten66sitting66", "a2l0dGVuNjZzaXR0aW5nNjY"),
    ("kitten66agent66", "a2l0dGVuNjZhZ2VudDY2"),
    ("kitten66angle66", "a2l0dGVuNjZhbmdsZTY2"),
    ("sitting66angle66", "c2l0dGluZzY2YW5nbGU2Ng"),
    ("sitting66universe66", "c2l0dGluZzY2dW5pdmVyc2U2Ng"),
    ("sitting66memory66", "c2l0dGluZzY2bWVtb3J5NjY"),
    ("sitting66stream66", "c2l0dGluZzY2c3RyZWFtNjY"),
    ("agent66stream66", "YWdlbnQ2NnN0cmVhbTY2"),
    ("agent66context66", "YWdlbnQ2NmNvbnRleHQ2Ng"),
    ("agent66knowledge66", "YWdlbnQ2Nmtub3dsZWRnZTY2"),
    ("agent66vector66", "YWdlbnQ2NnZlY3RvcjY2"),
    ("angle66vector66", "YW5nbGU2NnZlY3RvcjY2"),
    ("angle66processor66", "YW5nbGU2NnByb2Nlc3NvcjY2"),
    ("angle66reasoning66", "YW5nbGU2NnJlYXNvbmluZzY2"),
    ("angle66machine66", "YW5nbGU2Nm1hY2hpbmU2Ng"),
    ("universe66machine66", "dW5pdmVyc2U2Nm1hY2hpbmU2Ng"),
    ("universe66learning66", "dW5pdmVyc2U2NmxlYXJuaW5nNjY"),
    ("universe66model66", "dW5pdmVyc2U2Nm1vZGVsNjY"),
    ("universe66token66", "dW5pdmVyc2U2NnRva2VuNjY"),
    ("memory66token66", "bWVtb3J5NjZ0b2tlbjY2"),
    ("memory66prompt66", "bWVtb3J5NjZwcm9tcHQ2Ng"),
    ("memory66session66", "bWVtb3J5NjZzZXNzaW9uNjY"),
    ("memory66library66", "bWVtb3J5NjZsaWJyYXJ5NjY"),
    ("stream66library66", "c3RyZWFtNjZsaWJyYXJ5NjY"),
    ("stream66service66", "c3RyZWFtNjZzZXJ2aWNlNjY"),
    ("stream66gateway66", "c3RyZWFtNjZnYXRld2F5NjY"),
    ("stream66storage66", "c3RyZWFtNjZzdG9yYWdlNjY"),
    ("context66storage66", "Y29udGV4dDY2c3RvcmFnZTY2"),
    ("context66network66", "Y29udGV4dDY2bmV0d29yazY2"),
    ("context66latency66", "Y29udGV4dDY2bGF0ZW5jeTY2"),
    ("context66buffer66", "Y29udGV4dDY2YnVmZmVyNjY"),
    ("knowledge66buffer66", "a25vd2xlZGdlNjZidWZmZXI2Ng"),
    ("knowledge66queue66", "a25vd2xlZGdlNjZxdWV1ZTY2"),
    ("knowledge66worker66", "a25vd2xlZGdlNjZ3b3JrZXI2Ng"),
    ("knowledge66kernel66", "a25vd2xlZGdlNjZrZXJuZWw2Ng"),
    ("vector66kernel66", "dmVjdG9yNjZrZXJuZWw2Ng"),
    ("vector66signal66", "dmVjdG9yNjZzaWduYWw2Ng"),
    ("vector66packet66", "dmVjdG9yNjZwYWNrZXQ2Ng"),
    ("vector66router66", "dmVjdG9yNjZyb3V0ZXI2Ng"),
    ("processor66router66", "cHJvY2Vzc29yNjZyb3V0ZXI2Ng"),
    ("processor66cluster66", "cHJvY2Vzc29yNjZjbHVzdGVyNjY"),
    ("processor66mirror66", "cHJvY2Vzc29yNjZtaXJyb3I2Ng"),
    ("processor66filter66", "cHJvY2Vzc29yNjZmaWx0ZXI2Ng"),
    ("reasoning66filter66", "cmVhc29uaW5nNjZmaWx0ZXI2Ng"),
    ("reasoning66ranking66", "cmVhc29uaW5nNjZyYW5raW5nNjY"),
    ("reasoning66encoding66", "cmVhc29uaW5nNjZlbmNvZGluZzY2"),
    ("reasoning66mapping66", "cmVhc29uaW5nNjZtYXBwaW5nNjY"),
    ("machine66mapping66", "bWFjaGluZTY2bWFwcGluZzY2"),
    ("machine66record66", "bWFjaGluZTY2cmVjb3JkNjY"),
    ("machine66candle66", "bWFjaGluZTY2Y2FuZGxlNjY"),
    ("machine66thread66", "bWFjaGluZTY2dGhyZWFkNjY"),
    ("learning66thread66", "bGVhcm5pbmc2NnRocmVhZDY2"),
    ("learning66kitten66", "bGVhcm5pbmc2NmtpdHRlbjY2"),
    ("learning66sitting66", "bGVhcm5pbmc2NnNpdHRpbmc2Ng"),
    ("learning66agent66", "bGVhcm5pbmc2NmFnZW50NjY"),
    ("model66agent66", "bW9kZWw2NmFnZW50NjY"),
    ("model66angle66", "bW9kZWw2NmFuZ2xlNjY"),
    ("model66universe66", "bW9kZWw2NnVuaXZlcnNlNjY"),
    ("model66memory66", "bW9kZWw2Nm1lbW9yeTY2"),
    ("token66memory66", "dG9rZW42Nm1lbW9yeTY2"),
    ("token66stream66", "dG9rZW42NnN0cmVhbTY2"),
    ("token66context66", "dG9rZW42NmNvbnRleHQ2Ng"),
    ("token66knowledge66", "dG9rZW42Nmtub3dsZWRnZTY2"),
    ("prompt66knowledge66", "cHJvbXB0NjZrbm93bGVkZ2U2Ng"),
    ("prompt66vector66", "cHJvbXB0NjZ2ZWN0b3I2Ng"),
    ("prompt66processor66", "cHJvbXB0NjZwcm9jZXNzb3I2Ng"),
    ("prompt66reasoning66", "cHJvbXB0NjZyZWFzb25pbmc2Ng"),
    ("session66reasoning66", "c2Vzc2lvbjY2cmVhc29uaW5nNjY"),
    ("session66machine66", "c2Vzc2lvbjY2bWFjaGluZTY2"),
    ("session66learning66", "c2Vzc2lvbjY2bGVhcm5pbmc2Ng"),
    ("session66model66", "c2Vzc2lvbjY2bW9kZWw2Ng"),
    ("library66model66", "bGlicmFyeTY2bW9kZWw2Ng"),
    ("library66token66", "bGlicmFyeTY2dG9rZW42Ng"),
    ("library66prompt66", "bGlicmFyeTY2cHJvbXB0NjY"),
    ("library66session66", "bGlicmFyeTY2c2Vzc2lvbjY2"),
    ("service66session66", "c2VydmljZTY2c2Vzc2lvbjY2"),
    ("service66library66", "c2VydmljZTY2bGlicmFyeTY2"),
    ("service66service66", "c2VydmljZTY2c2VydmljZTY2"),
    ("service66gateway66", "c2VydmljZTY2Z2F0ZXdheTY2"),
    ("gateway66gateway66", "Z2F0ZXdheTY2Z2F0ZXdheTY2"),
    ("gateway66storage66", "Z2F0ZXdheTY2c3RvcmFnZTY2"),
    ("gateway66network66", "Z2F0ZXdheTY2bmV0d29yazY2"),
    ("gateway66latency66", "Z2F0ZXdheTY2bGF0ZW5jeTY2"),
    ("storage66latency66", "c3RvcmFnZTY2bGF0ZW5jeTY2"),
    ("storage66buffer66", "c3RvcmFnZTY2YnVmZmVyNjY"),
    ("storage66queue66", "c3RvcmFnZTY2cXVldWU2Ng"),
    ("storage66worker66", "c3RvcmFnZTY2d29ya2VyNjY"),
    ("network66worker66", "bmV0d29yazY2d29ya2VyNjY"),
    ("network66kernel66", "bmV0d29yazY2a2VybmVsNjY"),
    ("network66signal66", "bmV0d29yazY2c2lnbmFsNjY"),
    ("network66packet66", "bmV0d29yazY2cGFja2V0NjY"),
    ("latency66packet66", "bGF0ZW5jeTY2cGFja2V0NjY"),
    ("latency66router66", "bGF0ZW5jeTY2cm91dGVyNjY"),
    ("latency66cluster66", "bGF0ZW5jeTY2Y2x1c3RlcjY2"),
    ("latency66mirror66", "bGF0ZW5jeTY2bWlycm9yNjY"),
    ("buffer66mirror66", "YnVmZmVyNjZtaXJyb3I2Ng"),
    ("buffer66filter66", "YnVmZmVyNjZmaWx0ZXI2Ng"),
    ("buffer66ranking66", "YnVmZmVyNjZyYW5raW5nNjY"),
    ("buffer66encoding66", "YnVmZmVyNjZlbmNvZGluZzY2"),
    ("queue66encoding66", "cXVldWU2NmVuY29kaW5nNjY"),
    ("queue66mapping66", "cXVldWU2Nm1hcHBpbmc2Ng"),
    ("queue66record66", "cXVldWU2NnJlY29yZDY2"),
    ("queue66candle66", "cXVldWU2NmNhbmRsZTY2"),
    ("worker66candle66", "d29ya2VyNjZjYW5kbGU2Ng"),
    ("worker66thread66", "d29ya2VyNjZ0aHJlYWQ2Ng"),
    ("worker66kitten66", "d29ya2VyNjZraXR0ZW42Ng"),
    ("worker66sitting66", "d29ya2VyNjZzaXR0aW5nNjY"),
    ("kernel66sitting66", "a2VybmVsNjZzaXR0aW5nNjY"),
    ("kernel66agent66", "a2VybmVsNjZhZ2VudDY2"),
    ("kernel66angle66", "a2VybmVsNjZhbmdsZTY2"),
    ("kernel66universe66", "a2VybmVsNjZ1bml2ZXJzZTY2"),
    ("signal66universe66", "c2lnbmFsNjZ1bml2ZXJzZTY2"),
    ("signal66memory66", "c2lnbmFsNjZtZW1vcnk2Ng"),
    ("signal66stream66", "c2lnbmFsNjZzdHJlYW02Ng"),
    ("signal66context66", "c2lnbmFsNjZjb250ZXh0NjY"),
    ("packet66context66", "cGFja2V0NjZjb250ZXh0NjY"),
    ("packet66knowledge66", "cGFja2V0NjZrbm93bGVkZ2U2Ng"),
    ("packet66vector66", "cGFja2V0NjZ2ZWN0b3I2Ng"),
    ("packet66processor66", "cGFja2V0NjZwcm9jZXNzb3I2Ng"),
    ("router66processor66", "cm91dGVyNjZwcm9jZXNzb3I2Ng"),
    ("router66reasoning66", "cm91dGVyNjZyZWFzb25pbmc2Ng"),
    ("router66machine66", "cm91dGVyNjZtYWNoaW5lNjY"),
    ("router66learning66", "cm91dGVyNjZsZWFybmluZzY2"),
    ("cluster66learning66", "Y2x1c3RlcjY2bGVhcm5pbmc2Ng"),
    ("cluster66model66", "Y2x1c3RlcjY2bW9kZWw2Ng"),
    ("cluster66token66", "Y2x1c3RlcjY2dG9rZW42Ng"),
    ("cluster66prompt66", "Y2x1c3RlcjY2cHJvbXB0NjY"),
    ("mirror66prompt66", "bWlycm9yNjZwcm9tcHQ2Ng"),
    ("mirror66session66", "bWlycm9yNjZzZXNzaW9uNjY"),
    ("mirror66library66", "bWlycm9yNjZsaWJyYXJ5NjY"),
    ("mirror66service66", "bWlycm9yNjZzZXJ2aWNlNjY"),
    ("filter66service66", "ZmlsdGVyNjZzZXJ2aWNlNjY"),
    ("filter66gateway66", "ZmlsdGVyNjZnYXRld2F5NjY"),
    ("filter66storage66", "ZmlsdGVyNjZzdG9yYWdlNjY"),
    ("filter66network66", "ZmlsdGVyNjZuZXR3b3JrNjY"),
    ("ranking66network66", "cmFua2luZzY2bmV0d29yazY2"),
    ("ranking66latency66", "cmFua2luZzY2bGF0ZW5jeTY2"),
    ("ranking66buffer66", "cmFua2luZzY2YnVmZmVyNjY"),
    ("ranking66queue66", "cmFua2luZzY2cXVldWU2Ng"),
    ("encoding66queue66", "ZW5jb2Rpbmc2NnF1ZXVlNjY"),
    ("encoding66worker66", "ZW5jb2Rpbmc2NndvcmtlcjY2"),
    ("encoding66kernel66", "ZW5jb2Rpbmc2Nmtlcm5lbDY2"),
    ("encoding66signal66", "ZW5jb2Rpbmc2NnNpZ25hbDY2"),
    ("mapping66signal66", "bWFwcGluZzY2c2lnbmFsNjY"),
    ("mapping66packet66", "bWFwcGluZzY2cGFja2V0NjY"),
    ("mapping66router66", "bWFwcGluZzY2cm91dGVyNjY"),
    ("mapping66cluster66", "bWFwcGluZzY2Y2x1c3RlcjY2"),
    ("record66cluster66", "cmVjb3JkNjZjbHVzdGVyNjY"),
    ("record66mirror66", "cmVjb3JkNjZtaXJyb3I2Ng"),
    ("record66filter66", "cmVjb3JkNjZmaWx0ZXI2Ng"),
    ("record66ranking66", "cmVjb3JkNjZyYW5raW5nNjY"),
    ("candle66ranking66", "Y2FuZGxlNjZyYW5raW5nNjY"),
    ("candle66encoding66", "Y2FuZGxlNjZlbmNvZGluZzY2"),
    ("candle66mapping66", "Y2FuZGxlNjZtYXBwaW5nNjY"),
    ("candle66record66", "Y2FuZGxlNjZyZWNvcmQ2Ng"),
    ("thread66record66", "dGhyZWFkNjZyZWNvcmQ2Ng"),
    ("thread66candle66", "dGhyZWFkNjZjYW5kbGU2Ng"),
    ("thread66thread66", "dGhyZWFkNjZ0aHJlYWQ2Ng"),
    ("thread66kitten66", "dGhyZWFkNjZraXR0ZW42Ng"),
    (
        "round 66: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNjY6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 66: agentuniverse is a framework for multi agents",
        "cm91bmQgNjY6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 66: knowledge stored as vectors enables retrieval",
        "cm91bmQgNjY6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 66: the processor reads the record then stops",
        "cm91bmQgNjY6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 66: a worker pulls the next task from the queue",
        "cm91bmQgNjY6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 66: signals travel through the network layer",
        "cm91bmQgNjY6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 66: the gateway routes each request by policy",
        "cm91bmQgNjY6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 66: memory grows until the buffer is full",
        "cm91bmQgNjY6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 66: the cluster mirrors every packet twice",
        "cm91bmQgNjY6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 66: ranking uses tokens learned from the corpus",
        "cm91bmQgNjY6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 66: a long session ends when the candle dies",
        "cm91bmQgNjY6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 66: encode the prompt then map the result",
        "cm91bmQgNjY6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 66: the kernel wakes the worker at dawn", "cm91bmQgNjY6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 66: service latency drops after the patch",
        "cm91bmQgNjY6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 66: the library caches every vector it sees",
        "cm91bmQgNjY6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 66: agents argue then the debate resolves",
        "cm91bmQgNjY6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 66: the filter keeps only strong matches",
        "cm91bmQgNjY6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 66: the model answers with a short reply",
        "cm91bmQgNjY6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 66: the recorder stores the reasoning trace",
        "cm91bmQgNjY6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 66: the angel watches the processor run", "cm91bmQgNjY6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 66: angle of the vector decides the match",
        "cm91bmQgNjY6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 66: the candle burns twice as long at night",
        "cm91bmQgNjY6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 66: a mirror of the universe in one line",
        "cm91bmQgNjY6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 66: the queue drains before the storm", "cm91bmQgNjY6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
