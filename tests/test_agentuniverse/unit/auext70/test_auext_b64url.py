"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten70kitten70", "a2l0dGVuNzBraXR0ZW43MA"),
    ("kitten70sitting70", "a2l0dGVuNzBzaXR0aW5nNzA"),
    ("kitten70agent70", "a2l0dGVuNzBhZ2VudDcw"),
    ("kitten70angle70", "a2l0dGVuNzBhbmdsZTcw"),
    ("sitting70angle70", "c2l0dGluZzcwYW5nbGU3MA"),
    ("sitting70universe70", "c2l0dGluZzcwdW5pdmVyc2U3MA"),
    ("sitting70memory70", "c2l0dGluZzcwbWVtb3J5NzA"),
    ("sitting70stream70", "c2l0dGluZzcwc3RyZWFtNzA"),
    ("agent70stream70", "YWdlbnQ3MHN0cmVhbTcw"),
    ("agent70context70", "YWdlbnQ3MGNvbnRleHQ3MA"),
    ("agent70knowledge70", "YWdlbnQ3MGtub3dsZWRnZTcw"),
    ("agent70vector70", "YWdlbnQ3MHZlY3Rvcjcw"),
    ("angle70vector70", "YW5nbGU3MHZlY3Rvcjcw"),
    ("angle70processor70", "YW5nbGU3MHByb2Nlc3Nvcjcw"),
    ("angle70reasoning70", "YW5nbGU3MHJlYXNvbmluZzcw"),
    ("angle70machine70", "YW5nbGU3MG1hY2hpbmU3MA"),
    ("universe70machine70", "dW5pdmVyc2U3MG1hY2hpbmU3MA"),
    ("universe70learning70", "dW5pdmVyc2U3MGxlYXJuaW5nNzA"),
    ("universe70model70", "dW5pdmVyc2U3MG1vZGVsNzA"),
    ("universe70token70", "dW5pdmVyc2U3MHRva2VuNzA"),
    ("memory70token70", "bWVtb3J5NzB0b2tlbjcw"),
    ("memory70prompt70", "bWVtb3J5NzBwcm9tcHQ3MA"),
    ("memory70session70", "bWVtb3J5NzBzZXNzaW9uNzA"),
    ("memory70library70", "bWVtb3J5NzBsaWJyYXJ5NzA"),
    ("stream70library70", "c3RyZWFtNzBsaWJyYXJ5NzA"),
    ("stream70service70", "c3RyZWFtNzBzZXJ2aWNlNzA"),
    ("stream70gateway70", "c3RyZWFtNzBnYXRld2F5NzA"),
    ("stream70storage70", "c3RyZWFtNzBzdG9yYWdlNzA"),
    ("context70storage70", "Y29udGV4dDcwc3RvcmFnZTcw"),
    ("context70network70", "Y29udGV4dDcwbmV0d29yazcw"),
    ("context70latency70", "Y29udGV4dDcwbGF0ZW5jeTcw"),
    ("context70buffer70", "Y29udGV4dDcwYnVmZmVyNzA"),
    ("knowledge70buffer70", "a25vd2xlZGdlNzBidWZmZXI3MA"),
    ("knowledge70queue70", "a25vd2xlZGdlNzBxdWV1ZTcw"),
    ("knowledge70worker70", "a25vd2xlZGdlNzB3b3JrZXI3MA"),
    ("knowledge70kernel70", "a25vd2xlZGdlNzBrZXJuZWw3MA"),
    ("vector70kernel70", "dmVjdG9yNzBrZXJuZWw3MA"),
    ("vector70signal70", "dmVjdG9yNzBzaWduYWw3MA"),
    ("vector70packet70", "dmVjdG9yNzBwYWNrZXQ3MA"),
    ("vector70router70", "dmVjdG9yNzByb3V0ZXI3MA"),
    ("processor70router70", "cHJvY2Vzc29yNzByb3V0ZXI3MA"),
    ("processor70cluster70", "cHJvY2Vzc29yNzBjbHVzdGVyNzA"),
    ("processor70mirror70", "cHJvY2Vzc29yNzBtaXJyb3I3MA"),
    ("processor70filter70", "cHJvY2Vzc29yNzBmaWx0ZXI3MA"),
    ("reasoning70filter70", "cmVhc29uaW5nNzBmaWx0ZXI3MA"),
    ("reasoning70ranking70", "cmVhc29uaW5nNzByYW5raW5nNzA"),
    ("reasoning70encoding70", "cmVhc29uaW5nNzBlbmNvZGluZzcw"),
    ("reasoning70mapping70", "cmVhc29uaW5nNzBtYXBwaW5nNzA"),
    ("machine70mapping70", "bWFjaGluZTcwbWFwcGluZzcw"),
    ("machine70record70", "bWFjaGluZTcwcmVjb3JkNzA"),
    ("machine70candle70", "bWFjaGluZTcwY2FuZGxlNzA"),
    ("machine70thread70", "bWFjaGluZTcwdGhyZWFkNzA"),
    ("learning70thread70", "bGVhcm5pbmc3MHRocmVhZDcw"),
    ("learning70kitten70", "bGVhcm5pbmc3MGtpdHRlbjcw"),
    ("learning70sitting70", "bGVhcm5pbmc3MHNpdHRpbmc3MA"),
    ("learning70agent70", "bGVhcm5pbmc3MGFnZW50NzA"),
    ("model70agent70", "bW9kZWw3MGFnZW50NzA"),
    ("model70angle70", "bW9kZWw3MGFuZ2xlNzA"),
    ("model70universe70", "bW9kZWw3MHVuaXZlcnNlNzA"),
    ("model70memory70", "bW9kZWw3MG1lbW9yeTcw"),
    ("token70memory70", "dG9rZW43MG1lbW9yeTcw"),
    ("token70stream70", "dG9rZW43MHN0cmVhbTcw"),
    ("token70context70", "dG9rZW43MGNvbnRleHQ3MA"),
    ("token70knowledge70", "dG9rZW43MGtub3dsZWRnZTcw"),
    ("prompt70knowledge70", "cHJvbXB0NzBrbm93bGVkZ2U3MA"),
    ("prompt70vector70", "cHJvbXB0NzB2ZWN0b3I3MA"),
    ("prompt70processor70", "cHJvbXB0NzBwcm9jZXNzb3I3MA"),
    ("prompt70reasoning70", "cHJvbXB0NzByZWFzb25pbmc3MA"),
    ("session70reasoning70", "c2Vzc2lvbjcwcmVhc29uaW5nNzA"),
    ("session70machine70", "c2Vzc2lvbjcwbWFjaGluZTcw"),
    ("session70learning70", "c2Vzc2lvbjcwbGVhcm5pbmc3MA"),
    ("session70model70", "c2Vzc2lvbjcwbW9kZWw3MA"),
    ("library70model70", "bGlicmFyeTcwbW9kZWw3MA"),
    ("library70token70", "bGlicmFyeTcwdG9rZW43MA"),
    ("library70prompt70", "bGlicmFyeTcwcHJvbXB0NzA"),
    ("library70session70", "bGlicmFyeTcwc2Vzc2lvbjcw"),
    ("service70session70", "c2VydmljZTcwc2Vzc2lvbjcw"),
    ("service70library70", "c2VydmljZTcwbGlicmFyeTcw"),
    ("service70service70", "c2VydmljZTcwc2VydmljZTcw"),
    ("service70gateway70", "c2VydmljZTcwZ2F0ZXdheTcw"),
    ("gateway70gateway70", "Z2F0ZXdheTcwZ2F0ZXdheTcw"),
    ("gateway70storage70", "Z2F0ZXdheTcwc3RvcmFnZTcw"),
    ("gateway70network70", "Z2F0ZXdheTcwbmV0d29yazcw"),
    ("gateway70latency70", "Z2F0ZXdheTcwbGF0ZW5jeTcw"),
    ("storage70latency70", "c3RvcmFnZTcwbGF0ZW5jeTcw"),
    ("storage70buffer70", "c3RvcmFnZTcwYnVmZmVyNzA"),
    ("storage70queue70", "c3RvcmFnZTcwcXVldWU3MA"),
    ("storage70worker70", "c3RvcmFnZTcwd29ya2VyNzA"),
    ("network70worker70", "bmV0d29yazcwd29ya2VyNzA"),
    ("network70kernel70", "bmV0d29yazcwa2VybmVsNzA"),
    ("network70signal70", "bmV0d29yazcwc2lnbmFsNzA"),
    ("network70packet70", "bmV0d29yazcwcGFja2V0NzA"),
    ("latency70packet70", "bGF0ZW5jeTcwcGFja2V0NzA"),
    ("latency70router70", "bGF0ZW5jeTcwcm91dGVyNzA"),
    ("latency70cluster70", "bGF0ZW5jeTcwY2x1c3Rlcjcw"),
    ("latency70mirror70", "bGF0ZW5jeTcwbWlycm9yNzA"),
    ("buffer70mirror70", "YnVmZmVyNzBtaXJyb3I3MA"),
    ("buffer70filter70", "YnVmZmVyNzBmaWx0ZXI3MA"),
    ("buffer70ranking70", "YnVmZmVyNzByYW5raW5nNzA"),
    ("buffer70encoding70", "YnVmZmVyNzBlbmNvZGluZzcw"),
    ("queue70encoding70", "cXVldWU3MGVuY29kaW5nNzA"),
    ("queue70mapping70", "cXVldWU3MG1hcHBpbmc3MA"),
    ("queue70record70", "cXVldWU3MHJlY29yZDcw"),
    ("queue70candle70", "cXVldWU3MGNhbmRsZTcw"),
    ("worker70candle70", "d29ya2VyNzBjYW5kbGU3MA"),
    ("worker70thread70", "d29ya2VyNzB0aHJlYWQ3MA"),
    ("worker70kitten70", "d29ya2VyNzBraXR0ZW43MA"),
    ("worker70sitting70", "d29ya2VyNzBzaXR0aW5nNzA"),
    ("kernel70sitting70", "a2VybmVsNzBzaXR0aW5nNzA"),
    ("kernel70agent70", "a2VybmVsNzBhZ2VudDcw"),
    ("kernel70angle70", "a2VybmVsNzBhbmdsZTcw"),
    ("kernel70universe70", "a2VybmVsNzB1bml2ZXJzZTcw"),
    ("signal70universe70", "c2lnbmFsNzB1bml2ZXJzZTcw"),
    ("signal70memory70", "c2lnbmFsNzBtZW1vcnk3MA"),
    ("signal70stream70", "c2lnbmFsNzBzdHJlYW03MA"),
    ("signal70context70", "c2lnbmFsNzBjb250ZXh0NzA"),
    ("packet70context70", "cGFja2V0NzBjb250ZXh0NzA"),
    ("packet70knowledge70", "cGFja2V0NzBrbm93bGVkZ2U3MA"),
    ("packet70vector70", "cGFja2V0NzB2ZWN0b3I3MA"),
    ("packet70processor70", "cGFja2V0NzBwcm9jZXNzb3I3MA"),
    ("router70processor70", "cm91dGVyNzBwcm9jZXNzb3I3MA"),
    ("router70reasoning70", "cm91dGVyNzByZWFzb25pbmc3MA"),
    ("router70machine70", "cm91dGVyNzBtYWNoaW5lNzA"),
    ("router70learning70", "cm91dGVyNzBsZWFybmluZzcw"),
    ("cluster70learning70", "Y2x1c3RlcjcwbGVhcm5pbmc3MA"),
    ("cluster70model70", "Y2x1c3RlcjcwbW9kZWw3MA"),
    ("cluster70token70", "Y2x1c3RlcjcwdG9rZW43MA"),
    ("cluster70prompt70", "Y2x1c3RlcjcwcHJvbXB0NzA"),
    ("mirror70prompt70", "bWlycm9yNzBwcm9tcHQ3MA"),
    ("mirror70session70", "bWlycm9yNzBzZXNzaW9uNzA"),
    ("mirror70library70", "bWlycm9yNzBsaWJyYXJ5NzA"),
    ("mirror70service70", "bWlycm9yNzBzZXJ2aWNlNzA"),
    ("filter70service70", "ZmlsdGVyNzBzZXJ2aWNlNzA"),
    ("filter70gateway70", "ZmlsdGVyNzBnYXRld2F5NzA"),
    ("filter70storage70", "ZmlsdGVyNzBzdG9yYWdlNzA"),
    ("filter70network70", "ZmlsdGVyNzBuZXR3b3JrNzA"),
    ("ranking70network70", "cmFua2luZzcwbmV0d29yazcw"),
    ("ranking70latency70", "cmFua2luZzcwbGF0ZW5jeTcw"),
    ("ranking70buffer70", "cmFua2luZzcwYnVmZmVyNzA"),
    ("ranking70queue70", "cmFua2luZzcwcXVldWU3MA"),
    ("encoding70queue70", "ZW5jb2Rpbmc3MHF1ZXVlNzA"),
    ("encoding70worker70", "ZW5jb2Rpbmc3MHdvcmtlcjcw"),
    ("encoding70kernel70", "ZW5jb2Rpbmc3MGtlcm5lbDcw"),
    ("encoding70signal70", "ZW5jb2Rpbmc3MHNpZ25hbDcw"),
    ("mapping70signal70", "bWFwcGluZzcwc2lnbmFsNzA"),
    ("mapping70packet70", "bWFwcGluZzcwcGFja2V0NzA"),
    ("mapping70router70", "bWFwcGluZzcwcm91dGVyNzA"),
    ("mapping70cluster70", "bWFwcGluZzcwY2x1c3Rlcjcw"),
    ("record70cluster70", "cmVjb3JkNzBjbHVzdGVyNzA"),
    ("record70mirror70", "cmVjb3JkNzBtaXJyb3I3MA"),
    ("record70filter70", "cmVjb3JkNzBmaWx0ZXI3MA"),
    ("record70ranking70", "cmVjb3JkNzByYW5raW5nNzA"),
    ("candle70ranking70", "Y2FuZGxlNzByYW5raW5nNzA"),
    ("candle70encoding70", "Y2FuZGxlNzBlbmNvZGluZzcw"),
    ("candle70mapping70", "Y2FuZGxlNzBtYXBwaW5nNzA"),
    ("candle70record70", "Y2FuZGxlNzByZWNvcmQ3MA"),
    ("thread70record70", "dGhyZWFkNzByZWNvcmQ3MA"),
    ("thread70candle70", "dGhyZWFkNzBjYW5kbGU3MA"),
    ("thread70thread70", "dGhyZWFkNzB0aHJlYWQ3MA"),
    ("thread70kitten70", "dGhyZWFkNzBraXR0ZW43MA"),
    (
        "round 70: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzA6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 70: agentuniverse is a framework for multi agents",
        "cm91bmQgNzA6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 70: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzA6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 70: the processor reads the record then stops",
        "cm91bmQgNzA6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 70: a worker pulls the next task from the queue",
        "cm91bmQgNzA6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 70: signals travel through the network layer",
        "cm91bmQgNzA6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 70: the gateway routes each request by policy",
        "cm91bmQgNzA6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 70: memory grows until the buffer is full",
        "cm91bmQgNzA6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 70: the cluster mirrors every packet twice",
        "cm91bmQgNzA6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 70: ranking uses tokens learned from the corpus",
        "cm91bmQgNzA6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 70: a long session ends when the candle dies",
        "cm91bmQgNzA6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 70: encode the prompt then map the result",
        "cm91bmQgNzA6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 70: the kernel wakes the worker at dawn", "cm91bmQgNzA6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 70: service latency drops after the patch",
        "cm91bmQgNzA6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 70: the library caches every vector it sees",
        "cm91bmQgNzA6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 70: agents argue then the debate resolves",
        "cm91bmQgNzA6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 70: the filter keeps only strong matches",
        "cm91bmQgNzA6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 70: the model answers with a short reply",
        "cm91bmQgNzA6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 70: the recorder stores the reasoning trace",
        "cm91bmQgNzA6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 70: the angel watches the processor run", "cm91bmQgNzA6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 70: angle of the vector decides the match",
        "cm91bmQgNzA6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 70: the candle burns twice as long at night",
        "cm91bmQgNzA6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 70: a mirror of the universe in one line",
        "cm91bmQgNzA6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 70: the queue drains before the storm", "cm91bmQgNzA6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
