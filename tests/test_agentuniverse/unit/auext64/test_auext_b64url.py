"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten64kitten64", "a2l0dGVuNjRraXR0ZW42NA"),
    ("kitten64sitting64", "a2l0dGVuNjRzaXR0aW5nNjQ"),
    ("kitten64agent64", "a2l0dGVuNjRhZ2VudDY0"),
    ("kitten64angle64", "a2l0dGVuNjRhbmdsZTY0"),
    ("sitting64angle64", "c2l0dGluZzY0YW5nbGU2NA"),
    ("sitting64universe64", "c2l0dGluZzY0dW5pdmVyc2U2NA"),
    ("sitting64memory64", "c2l0dGluZzY0bWVtb3J5NjQ"),
    ("sitting64stream64", "c2l0dGluZzY0c3RyZWFtNjQ"),
    ("agent64stream64", "YWdlbnQ2NHN0cmVhbTY0"),
    ("agent64context64", "YWdlbnQ2NGNvbnRleHQ2NA"),
    ("agent64knowledge64", "YWdlbnQ2NGtub3dsZWRnZTY0"),
    ("agent64vector64", "YWdlbnQ2NHZlY3RvcjY0"),
    ("angle64vector64", "YW5nbGU2NHZlY3RvcjY0"),
    ("angle64processor64", "YW5nbGU2NHByb2Nlc3NvcjY0"),
    ("angle64reasoning64", "YW5nbGU2NHJlYXNvbmluZzY0"),
    ("angle64machine64", "YW5nbGU2NG1hY2hpbmU2NA"),
    ("universe64machine64", "dW5pdmVyc2U2NG1hY2hpbmU2NA"),
    ("universe64learning64", "dW5pdmVyc2U2NGxlYXJuaW5nNjQ"),
    ("universe64model64", "dW5pdmVyc2U2NG1vZGVsNjQ"),
    ("universe64token64", "dW5pdmVyc2U2NHRva2VuNjQ"),
    ("memory64token64", "bWVtb3J5NjR0b2tlbjY0"),
    ("memory64prompt64", "bWVtb3J5NjRwcm9tcHQ2NA"),
    ("memory64session64", "bWVtb3J5NjRzZXNzaW9uNjQ"),
    ("memory64library64", "bWVtb3J5NjRsaWJyYXJ5NjQ"),
    ("stream64library64", "c3RyZWFtNjRsaWJyYXJ5NjQ"),
    ("stream64service64", "c3RyZWFtNjRzZXJ2aWNlNjQ"),
    ("stream64gateway64", "c3RyZWFtNjRnYXRld2F5NjQ"),
    ("stream64storage64", "c3RyZWFtNjRzdG9yYWdlNjQ"),
    ("context64storage64", "Y29udGV4dDY0c3RvcmFnZTY0"),
    ("context64network64", "Y29udGV4dDY0bmV0d29yazY0"),
    ("context64latency64", "Y29udGV4dDY0bGF0ZW5jeTY0"),
    ("context64buffer64", "Y29udGV4dDY0YnVmZmVyNjQ"),
    ("knowledge64buffer64", "a25vd2xlZGdlNjRidWZmZXI2NA"),
    ("knowledge64queue64", "a25vd2xlZGdlNjRxdWV1ZTY0"),
    ("knowledge64worker64", "a25vd2xlZGdlNjR3b3JrZXI2NA"),
    ("knowledge64kernel64", "a25vd2xlZGdlNjRrZXJuZWw2NA"),
    ("vector64kernel64", "dmVjdG9yNjRrZXJuZWw2NA"),
    ("vector64signal64", "dmVjdG9yNjRzaWduYWw2NA"),
    ("vector64packet64", "dmVjdG9yNjRwYWNrZXQ2NA"),
    ("vector64router64", "dmVjdG9yNjRyb3V0ZXI2NA"),
    ("processor64router64", "cHJvY2Vzc29yNjRyb3V0ZXI2NA"),
    ("processor64cluster64", "cHJvY2Vzc29yNjRjbHVzdGVyNjQ"),
    ("processor64mirror64", "cHJvY2Vzc29yNjRtaXJyb3I2NA"),
    ("processor64filter64", "cHJvY2Vzc29yNjRmaWx0ZXI2NA"),
    ("reasoning64filter64", "cmVhc29uaW5nNjRmaWx0ZXI2NA"),
    ("reasoning64ranking64", "cmVhc29uaW5nNjRyYW5raW5nNjQ"),
    ("reasoning64encoding64", "cmVhc29uaW5nNjRlbmNvZGluZzY0"),
    ("reasoning64mapping64", "cmVhc29uaW5nNjRtYXBwaW5nNjQ"),
    ("machine64mapping64", "bWFjaGluZTY0bWFwcGluZzY0"),
    ("machine64record64", "bWFjaGluZTY0cmVjb3JkNjQ"),
    ("machine64candle64", "bWFjaGluZTY0Y2FuZGxlNjQ"),
    ("machine64thread64", "bWFjaGluZTY0dGhyZWFkNjQ"),
    ("learning64thread64", "bGVhcm5pbmc2NHRocmVhZDY0"),
    ("learning64kitten64", "bGVhcm5pbmc2NGtpdHRlbjY0"),
    ("learning64sitting64", "bGVhcm5pbmc2NHNpdHRpbmc2NA"),
    ("learning64agent64", "bGVhcm5pbmc2NGFnZW50NjQ"),
    ("model64agent64", "bW9kZWw2NGFnZW50NjQ"),
    ("model64angle64", "bW9kZWw2NGFuZ2xlNjQ"),
    ("model64universe64", "bW9kZWw2NHVuaXZlcnNlNjQ"),
    ("model64memory64", "bW9kZWw2NG1lbW9yeTY0"),
    ("token64memory64", "dG9rZW42NG1lbW9yeTY0"),
    ("token64stream64", "dG9rZW42NHN0cmVhbTY0"),
    ("token64context64", "dG9rZW42NGNvbnRleHQ2NA"),
    ("token64knowledge64", "dG9rZW42NGtub3dsZWRnZTY0"),
    ("prompt64knowledge64", "cHJvbXB0NjRrbm93bGVkZ2U2NA"),
    ("prompt64vector64", "cHJvbXB0NjR2ZWN0b3I2NA"),
    ("prompt64processor64", "cHJvbXB0NjRwcm9jZXNzb3I2NA"),
    ("prompt64reasoning64", "cHJvbXB0NjRyZWFzb25pbmc2NA"),
    ("session64reasoning64", "c2Vzc2lvbjY0cmVhc29uaW5nNjQ"),
    ("session64machine64", "c2Vzc2lvbjY0bWFjaGluZTY0"),
    ("session64learning64", "c2Vzc2lvbjY0bGVhcm5pbmc2NA"),
    ("session64model64", "c2Vzc2lvbjY0bW9kZWw2NA"),
    ("library64model64", "bGlicmFyeTY0bW9kZWw2NA"),
    ("library64token64", "bGlicmFyeTY0dG9rZW42NA"),
    ("library64prompt64", "bGlicmFyeTY0cHJvbXB0NjQ"),
    ("library64session64", "bGlicmFyeTY0c2Vzc2lvbjY0"),
    ("service64session64", "c2VydmljZTY0c2Vzc2lvbjY0"),
    ("service64library64", "c2VydmljZTY0bGlicmFyeTY0"),
    ("service64service64", "c2VydmljZTY0c2VydmljZTY0"),
    ("service64gateway64", "c2VydmljZTY0Z2F0ZXdheTY0"),
    ("gateway64gateway64", "Z2F0ZXdheTY0Z2F0ZXdheTY0"),
    ("gateway64storage64", "Z2F0ZXdheTY0c3RvcmFnZTY0"),
    ("gateway64network64", "Z2F0ZXdheTY0bmV0d29yazY0"),
    ("gateway64latency64", "Z2F0ZXdheTY0bGF0ZW5jeTY0"),
    ("storage64latency64", "c3RvcmFnZTY0bGF0ZW5jeTY0"),
    ("storage64buffer64", "c3RvcmFnZTY0YnVmZmVyNjQ"),
    ("storage64queue64", "c3RvcmFnZTY0cXVldWU2NA"),
    ("storage64worker64", "c3RvcmFnZTY0d29ya2VyNjQ"),
    ("network64worker64", "bmV0d29yazY0d29ya2VyNjQ"),
    ("network64kernel64", "bmV0d29yazY0a2VybmVsNjQ"),
    ("network64signal64", "bmV0d29yazY0c2lnbmFsNjQ"),
    ("network64packet64", "bmV0d29yazY0cGFja2V0NjQ"),
    ("latency64packet64", "bGF0ZW5jeTY0cGFja2V0NjQ"),
    ("latency64router64", "bGF0ZW5jeTY0cm91dGVyNjQ"),
    ("latency64cluster64", "bGF0ZW5jeTY0Y2x1c3RlcjY0"),
    ("latency64mirror64", "bGF0ZW5jeTY0bWlycm9yNjQ"),
    ("buffer64mirror64", "YnVmZmVyNjRtaXJyb3I2NA"),
    ("buffer64filter64", "YnVmZmVyNjRmaWx0ZXI2NA"),
    ("buffer64ranking64", "YnVmZmVyNjRyYW5raW5nNjQ"),
    ("buffer64encoding64", "YnVmZmVyNjRlbmNvZGluZzY0"),
    ("queue64encoding64", "cXVldWU2NGVuY29kaW5nNjQ"),
    ("queue64mapping64", "cXVldWU2NG1hcHBpbmc2NA"),
    ("queue64record64", "cXVldWU2NHJlY29yZDY0"),
    ("queue64candle64", "cXVldWU2NGNhbmRsZTY0"),
    ("worker64candle64", "d29ya2VyNjRjYW5kbGU2NA"),
    ("worker64thread64", "d29ya2VyNjR0aHJlYWQ2NA"),
    ("worker64kitten64", "d29ya2VyNjRraXR0ZW42NA"),
    ("worker64sitting64", "d29ya2VyNjRzaXR0aW5nNjQ"),
    ("kernel64sitting64", "a2VybmVsNjRzaXR0aW5nNjQ"),
    ("kernel64agent64", "a2VybmVsNjRhZ2VudDY0"),
    ("kernel64angle64", "a2VybmVsNjRhbmdsZTY0"),
    ("kernel64universe64", "a2VybmVsNjR1bml2ZXJzZTY0"),
    ("signal64universe64", "c2lnbmFsNjR1bml2ZXJzZTY0"),
    ("signal64memory64", "c2lnbmFsNjRtZW1vcnk2NA"),
    ("signal64stream64", "c2lnbmFsNjRzdHJlYW02NA"),
    ("signal64context64", "c2lnbmFsNjRjb250ZXh0NjQ"),
    ("packet64context64", "cGFja2V0NjRjb250ZXh0NjQ"),
    ("packet64knowledge64", "cGFja2V0NjRrbm93bGVkZ2U2NA"),
    ("packet64vector64", "cGFja2V0NjR2ZWN0b3I2NA"),
    ("packet64processor64", "cGFja2V0NjRwcm9jZXNzb3I2NA"),
    ("router64processor64", "cm91dGVyNjRwcm9jZXNzb3I2NA"),
    ("router64reasoning64", "cm91dGVyNjRyZWFzb25pbmc2NA"),
    ("router64machine64", "cm91dGVyNjRtYWNoaW5lNjQ"),
    ("router64learning64", "cm91dGVyNjRsZWFybmluZzY0"),
    ("cluster64learning64", "Y2x1c3RlcjY0bGVhcm5pbmc2NA"),
    ("cluster64model64", "Y2x1c3RlcjY0bW9kZWw2NA"),
    ("cluster64token64", "Y2x1c3RlcjY0dG9rZW42NA"),
    ("cluster64prompt64", "Y2x1c3RlcjY0cHJvbXB0NjQ"),
    ("mirror64prompt64", "bWlycm9yNjRwcm9tcHQ2NA"),
    ("mirror64session64", "bWlycm9yNjRzZXNzaW9uNjQ"),
    ("mirror64library64", "bWlycm9yNjRsaWJyYXJ5NjQ"),
    ("mirror64service64", "bWlycm9yNjRzZXJ2aWNlNjQ"),
    ("filter64service64", "ZmlsdGVyNjRzZXJ2aWNlNjQ"),
    ("filter64gateway64", "ZmlsdGVyNjRnYXRld2F5NjQ"),
    ("filter64storage64", "ZmlsdGVyNjRzdG9yYWdlNjQ"),
    ("filter64network64", "ZmlsdGVyNjRuZXR3b3JrNjQ"),
    ("ranking64network64", "cmFua2luZzY0bmV0d29yazY0"),
    ("ranking64latency64", "cmFua2luZzY0bGF0ZW5jeTY0"),
    ("ranking64buffer64", "cmFua2luZzY0YnVmZmVyNjQ"),
    ("ranking64queue64", "cmFua2luZzY0cXVldWU2NA"),
    ("encoding64queue64", "ZW5jb2Rpbmc2NHF1ZXVlNjQ"),
    ("encoding64worker64", "ZW5jb2Rpbmc2NHdvcmtlcjY0"),
    ("encoding64kernel64", "ZW5jb2Rpbmc2NGtlcm5lbDY0"),
    ("encoding64signal64", "ZW5jb2Rpbmc2NHNpZ25hbDY0"),
    ("mapping64signal64", "bWFwcGluZzY0c2lnbmFsNjQ"),
    ("mapping64packet64", "bWFwcGluZzY0cGFja2V0NjQ"),
    ("mapping64router64", "bWFwcGluZzY0cm91dGVyNjQ"),
    ("mapping64cluster64", "bWFwcGluZzY0Y2x1c3RlcjY0"),
    ("record64cluster64", "cmVjb3JkNjRjbHVzdGVyNjQ"),
    ("record64mirror64", "cmVjb3JkNjRtaXJyb3I2NA"),
    ("record64filter64", "cmVjb3JkNjRmaWx0ZXI2NA"),
    ("record64ranking64", "cmVjb3JkNjRyYW5raW5nNjQ"),
    ("candle64ranking64", "Y2FuZGxlNjRyYW5raW5nNjQ"),
    ("candle64encoding64", "Y2FuZGxlNjRlbmNvZGluZzY0"),
    ("candle64mapping64", "Y2FuZGxlNjRtYXBwaW5nNjQ"),
    ("candle64record64", "Y2FuZGxlNjRyZWNvcmQ2NA"),
    ("thread64record64", "dGhyZWFkNjRyZWNvcmQ2NA"),
    ("thread64candle64", "dGhyZWFkNjRjYW5kbGU2NA"),
    ("thread64thread64", "dGhyZWFkNjR0aHJlYWQ2NA"),
    ("thread64kitten64", "dGhyZWFkNjRraXR0ZW42NA"),
    (
        "round 64: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNjQ6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 64: agentuniverse is a framework for multi agents",
        "cm91bmQgNjQ6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 64: knowledge stored as vectors enables retrieval",
        "cm91bmQgNjQ6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 64: the processor reads the record then stops",
        "cm91bmQgNjQ6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 64: a worker pulls the next task from the queue",
        "cm91bmQgNjQ6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 64: signals travel through the network layer",
        "cm91bmQgNjQ6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 64: the gateway routes each request by policy",
        "cm91bmQgNjQ6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 64: memory grows until the buffer is full",
        "cm91bmQgNjQ6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 64: the cluster mirrors every packet twice",
        "cm91bmQgNjQ6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 64: ranking uses tokens learned from the corpus",
        "cm91bmQgNjQ6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 64: a long session ends when the candle dies",
        "cm91bmQgNjQ6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 64: encode the prompt then map the result",
        "cm91bmQgNjQ6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 64: the kernel wakes the worker at dawn", "cm91bmQgNjQ6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 64: service latency drops after the patch",
        "cm91bmQgNjQ6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 64: the library caches every vector it sees",
        "cm91bmQgNjQ6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 64: agents argue then the debate resolves",
        "cm91bmQgNjQ6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 64: the filter keeps only strong matches",
        "cm91bmQgNjQ6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 64: the model answers with a short reply",
        "cm91bmQgNjQ6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 64: the recorder stores the reasoning trace",
        "cm91bmQgNjQ6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 64: the angel watches the processor run", "cm91bmQgNjQ6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 64: angle of the vector decides the match",
        "cm91bmQgNjQ6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 64: the candle burns twice as long at night",
        "cm91bmQgNjQ6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 64: a mirror of the universe in one line",
        "cm91bmQgNjQ6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 64: the queue drains before the storm", "cm91bmQgNjQ6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
