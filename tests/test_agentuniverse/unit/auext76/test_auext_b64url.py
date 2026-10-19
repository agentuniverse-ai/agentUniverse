"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten76kitten76", "a2l0dGVuNzZraXR0ZW43Ng"),
    ("kitten76sitting76", "a2l0dGVuNzZzaXR0aW5nNzY"),
    ("kitten76agent76", "a2l0dGVuNzZhZ2VudDc2"),
    ("kitten76angle76", "a2l0dGVuNzZhbmdsZTc2"),
    ("sitting76angle76", "c2l0dGluZzc2YW5nbGU3Ng"),
    ("sitting76universe76", "c2l0dGluZzc2dW5pdmVyc2U3Ng"),
    ("sitting76memory76", "c2l0dGluZzc2bWVtb3J5NzY"),
    ("sitting76stream76", "c2l0dGluZzc2c3RyZWFtNzY"),
    ("agent76stream76", "YWdlbnQ3NnN0cmVhbTc2"),
    ("agent76context76", "YWdlbnQ3NmNvbnRleHQ3Ng"),
    ("agent76knowledge76", "YWdlbnQ3Nmtub3dsZWRnZTc2"),
    ("agent76vector76", "YWdlbnQ3NnZlY3Rvcjc2"),
    ("angle76vector76", "YW5nbGU3NnZlY3Rvcjc2"),
    ("angle76processor76", "YW5nbGU3NnByb2Nlc3Nvcjc2"),
    ("angle76reasoning76", "YW5nbGU3NnJlYXNvbmluZzc2"),
    ("angle76machine76", "YW5nbGU3Nm1hY2hpbmU3Ng"),
    ("universe76machine76", "dW5pdmVyc2U3Nm1hY2hpbmU3Ng"),
    ("universe76learning76", "dW5pdmVyc2U3NmxlYXJuaW5nNzY"),
    ("universe76model76", "dW5pdmVyc2U3Nm1vZGVsNzY"),
    ("universe76token76", "dW5pdmVyc2U3NnRva2VuNzY"),
    ("memory76token76", "bWVtb3J5NzZ0b2tlbjc2"),
    ("memory76prompt76", "bWVtb3J5NzZwcm9tcHQ3Ng"),
    ("memory76session76", "bWVtb3J5NzZzZXNzaW9uNzY"),
    ("memory76library76", "bWVtb3J5NzZsaWJyYXJ5NzY"),
    ("stream76library76", "c3RyZWFtNzZsaWJyYXJ5NzY"),
    ("stream76service76", "c3RyZWFtNzZzZXJ2aWNlNzY"),
    ("stream76gateway76", "c3RyZWFtNzZnYXRld2F5NzY"),
    ("stream76storage76", "c3RyZWFtNzZzdG9yYWdlNzY"),
    ("context76storage76", "Y29udGV4dDc2c3RvcmFnZTc2"),
    ("context76network76", "Y29udGV4dDc2bmV0d29yazc2"),
    ("context76latency76", "Y29udGV4dDc2bGF0ZW5jeTc2"),
    ("context76buffer76", "Y29udGV4dDc2YnVmZmVyNzY"),
    ("knowledge76buffer76", "a25vd2xlZGdlNzZidWZmZXI3Ng"),
    ("knowledge76queue76", "a25vd2xlZGdlNzZxdWV1ZTc2"),
    ("knowledge76worker76", "a25vd2xlZGdlNzZ3b3JrZXI3Ng"),
    ("knowledge76kernel76", "a25vd2xlZGdlNzZrZXJuZWw3Ng"),
    ("vector76kernel76", "dmVjdG9yNzZrZXJuZWw3Ng"),
    ("vector76signal76", "dmVjdG9yNzZzaWduYWw3Ng"),
    ("vector76packet76", "dmVjdG9yNzZwYWNrZXQ3Ng"),
    ("vector76router76", "dmVjdG9yNzZyb3V0ZXI3Ng"),
    ("processor76router76", "cHJvY2Vzc29yNzZyb3V0ZXI3Ng"),
    ("processor76cluster76", "cHJvY2Vzc29yNzZjbHVzdGVyNzY"),
    ("processor76mirror76", "cHJvY2Vzc29yNzZtaXJyb3I3Ng"),
    ("processor76filter76", "cHJvY2Vzc29yNzZmaWx0ZXI3Ng"),
    ("reasoning76filter76", "cmVhc29uaW5nNzZmaWx0ZXI3Ng"),
    ("reasoning76ranking76", "cmVhc29uaW5nNzZyYW5raW5nNzY"),
    ("reasoning76encoding76", "cmVhc29uaW5nNzZlbmNvZGluZzc2"),
    ("reasoning76mapping76", "cmVhc29uaW5nNzZtYXBwaW5nNzY"),
    ("machine76mapping76", "bWFjaGluZTc2bWFwcGluZzc2"),
    ("machine76record76", "bWFjaGluZTc2cmVjb3JkNzY"),
    ("machine76candle76", "bWFjaGluZTc2Y2FuZGxlNzY"),
    ("machine76thread76", "bWFjaGluZTc2dGhyZWFkNzY"),
    ("learning76thread76", "bGVhcm5pbmc3NnRocmVhZDc2"),
    ("learning76kitten76", "bGVhcm5pbmc3NmtpdHRlbjc2"),
    ("learning76sitting76", "bGVhcm5pbmc3NnNpdHRpbmc3Ng"),
    ("learning76agent76", "bGVhcm5pbmc3NmFnZW50NzY"),
    ("model76agent76", "bW9kZWw3NmFnZW50NzY"),
    ("model76angle76", "bW9kZWw3NmFuZ2xlNzY"),
    ("model76universe76", "bW9kZWw3NnVuaXZlcnNlNzY"),
    ("model76memory76", "bW9kZWw3Nm1lbW9yeTc2"),
    ("token76memory76", "dG9rZW43Nm1lbW9yeTc2"),
    ("token76stream76", "dG9rZW43NnN0cmVhbTc2"),
    ("token76context76", "dG9rZW43NmNvbnRleHQ3Ng"),
    ("token76knowledge76", "dG9rZW43Nmtub3dsZWRnZTc2"),
    ("prompt76knowledge76", "cHJvbXB0NzZrbm93bGVkZ2U3Ng"),
    ("prompt76vector76", "cHJvbXB0NzZ2ZWN0b3I3Ng"),
    ("prompt76processor76", "cHJvbXB0NzZwcm9jZXNzb3I3Ng"),
    ("prompt76reasoning76", "cHJvbXB0NzZyZWFzb25pbmc3Ng"),
    ("session76reasoning76", "c2Vzc2lvbjc2cmVhc29uaW5nNzY"),
    ("session76machine76", "c2Vzc2lvbjc2bWFjaGluZTc2"),
    ("session76learning76", "c2Vzc2lvbjc2bGVhcm5pbmc3Ng"),
    ("session76model76", "c2Vzc2lvbjc2bW9kZWw3Ng"),
    ("library76model76", "bGlicmFyeTc2bW9kZWw3Ng"),
    ("library76token76", "bGlicmFyeTc2dG9rZW43Ng"),
    ("library76prompt76", "bGlicmFyeTc2cHJvbXB0NzY"),
    ("library76session76", "bGlicmFyeTc2c2Vzc2lvbjc2"),
    ("service76session76", "c2VydmljZTc2c2Vzc2lvbjc2"),
    ("service76library76", "c2VydmljZTc2bGlicmFyeTc2"),
    ("service76service76", "c2VydmljZTc2c2VydmljZTc2"),
    ("service76gateway76", "c2VydmljZTc2Z2F0ZXdheTc2"),
    ("gateway76gateway76", "Z2F0ZXdheTc2Z2F0ZXdheTc2"),
    ("gateway76storage76", "Z2F0ZXdheTc2c3RvcmFnZTc2"),
    ("gateway76network76", "Z2F0ZXdheTc2bmV0d29yazc2"),
    ("gateway76latency76", "Z2F0ZXdheTc2bGF0ZW5jeTc2"),
    ("storage76latency76", "c3RvcmFnZTc2bGF0ZW5jeTc2"),
    ("storage76buffer76", "c3RvcmFnZTc2YnVmZmVyNzY"),
    ("storage76queue76", "c3RvcmFnZTc2cXVldWU3Ng"),
    ("storage76worker76", "c3RvcmFnZTc2d29ya2VyNzY"),
    ("network76worker76", "bmV0d29yazc2d29ya2VyNzY"),
    ("network76kernel76", "bmV0d29yazc2a2VybmVsNzY"),
    ("network76signal76", "bmV0d29yazc2c2lnbmFsNzY"),
    ("network76packet76", "bmV0d29yazc2cGFja2V0NzY"),
    ("latency76packet76", "bGF0ZW5jeTc2cGFja2V0NzY"),
    ("latency76router76", "bGF0ZW5jeTc2cm91dGVyNzY"),
    ("latency76cluster76", "bGF0ZW5jeTc2Y2x1c3Rlcjc2"),
    ("latency76mirror76", "bGF0ZW5jeTc2bWlycm9yNzY"),
    ("buffer76mirror76", "YnVmZmVyNzZtaXJyb3I3Ng"),
    ("buffer76filter76", "YnVmZmVyNzZmaWx0ZXI3Ng"),
    ("buffer76ranking76", "YnVmZmVyNzZyYW5raW5nNzY"),
    ("buffer76encoding76", "YnVmZmVyNzZlbmNvZGluZzc2"),
    ("queue76encoding76", "cXVldWU3NmVuY29kaW5nNzY"),
    ("queue76mapping76", "cXVldWU3Nm1hcHBpbmc3Ng"),
    ("queue76record76", "cXVldWU3NnJlY29yZDc2"),
    ("queue76candle76", "cXVldWU3NmNhbmRsZTc2"),
    ("worker76candle76", "d29ya2VyNzZjYW5kbGU3Ng"),
    ("worker76thread76", "d29ya2VyNzZ0aHJlYWQ3Ng"),
    ("worker76kitten76", "d29ya2VyNzZraXR0ZW43Ng"),
    ("worker76sitting76", "d29ya2VyNzZzaXR0aW5nNzY"),
    ("kernel76sitting76", "a2VybmVsNzZzaXR0aW5nNzY"),
    ("kernel76agent76", "a2VybmVsNzZhZ2VudDc2"),
    ("kernel76angle76", "a2VybmVsNzZhbmdsZTc2"),
    ("kernel76universe76", "a2VybmVsNzZ1bml2ZXJzZTc2"),
    ("signal76universe76", "c2lnbmFsNzZ1bml2ZXJzZTc2"),
    ("signal76memory76", "c2lnbmFsNzZtZW1vcnk3Ng"),
    ("signal76stream76", "c2lnbmFsNzZzdHJlYW03Ng"),
    ("signal76context76", "c2lnbmFsNzZjb250ZXh0NzY"),
    ("packet76context76", "cGFja2V0NzZjb250ZXh0NzY"),
    ("packet76knowledge76", "cGFja2V0NzZrbm93bGVkZ2U3Ng"),
    ("packet76vector76", "cGFja2V0NzZ2ZWN0b3I3Ng"),
    ("packet76processor76", "cGFja2V0NzZwcm9jZXNzb3I3Ng"),
    ("router76processor76", "cm91dGVyNzZwcm9jZXNzb3I3Ng"),
    ("router76reasoning76", "cm91dGVyNzZyZWFzb25pbmc3Ng"),
    ("router76machine76", "cm91dGVyNzZtYWNoaW5lNzY"),
    ("router76learning76", "cm91dGVyNzZsZWFybmluZzc2"),
    ("cluster76learning76", "Y2x1c3Rlcjc2bGVhcm5pbmc3Ng"),
    ("cluster76model76", "Y2x1c3Rlcjc2bW9kZWw3Ng"),
    ("cluster76token76", "Y2x1c3Rlcjc2dG9rZW43Ng"),
    ("cluster76prompt76", "Y2x1c3Rlcjc2cHJvbXB0NzY"),
    ("mirror76prompt76", "bWlycm9yNzZwcm9tcHQ3Ng"),
    ("mirror76session76", "bWlycm9yNzZzZXNzaW9uNzY"),
    ("mirror76library76", "bWlycm9yNzZsaWJyYXJ5NzY"),
    ("mirror76service76", "bWlycm9yNzZzZXJ2aWNlNzY"),
    ("filter76service76", "ZmlsdGVyNzZzZXJ2aWNlNzY"),
    ("filter76gateway76", "ZmlsdGVyNzZnYXRld2F5NzY"),
    ("filter76storage76", "ZmlsdGVyNzZzdG9yYWdlNzY"),
    ("filter76network76", "ZmlsdGVyNzZuZXR3b3JrNzY"),
    ("ranking76network76", "cmFua2luZzc2bmV0d29yazc2"),
    ("ranking76latency76", "cmFua2luZzc2bGF0ZW5jeTc2"),
    ("ranking76buffer76", "cmFua2luZzc2YnVmZmVyNzY"),
    ("ranking76queue76", "cmFua2luZzc2cXVldWU3Ng"),
    ("encoding76queue76", "ZW5jb2Rpbmc3NnF1ZXVlNzY"),
    ("encoding76worker76", "ZW5jb2Rpbmc3Nndvcmtlcjc2"),
    ("encoding76kernel76", "ZW5jb2Rpbmc3Nmtlcm5lbDc2"),
    ("encoding76signal76", "ZW5jb2Rpbmc3NnNpZ25hbDc2"),
    ("mapping76signal76", "bWFwcGluZzc2c2lnbmFsNzY"),
    ("mapping76packet76", "bWFwcGluZzc2cGFja2V0NzY"),
    ("mapping76router76", "bWFwcGluZzc2cm91dGVyNzY"),
    ("mapping76cluster76", "bWFwcGluZzc2Y2x1c3Rlcjc2"),
    ("record76cluster76", "cmVjb3JkNzZjbHVzdGVyNzY"),
    ("record76mirror76", "cmVjb3JkNzZtaXJyb3I3Ng"),
    ("record76filter76", "cmVjb3JkNzZmaWx0ZXI3Ng"),
    ("record76ranking76", "cmVjb3JkNzZyYW5raW5nNzY"),
    ("candle76ranking76", "Y2FuZGxlNzZyYW5raW5nNzY"),
    ("candle76encoding76", "Y2FuZGxlNzZlbmNvZGluZzc2"),
    ("candle76mapping76", "Y2FuZGxlNzZtYXBwaW5nNzY"),
    ("candle76record76", "Y2FuZGxlNzZyZWNvcmQ3Ng"),
    ("thread76record76", "dGhyZWFkNzZyZWNvcmQ3Ng"),
    ("thread76candle76", "dGhyZWFkNzZjYW5kbGU3Ng"),
    ("thread76thread76", "dGhyZWFkNzZ0aHJlYWQ3Ng"),
    ("thread76kitten76", "dGhyZWFkNzZraXR0ZW43Ng"),
    (
        "round 76: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzY6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 76: agentuniverse is a framework for multi agents",
        "cm91bmQgNzY6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 76: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzY6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 76: the processor reads the record then stops",
        "cm91bmQgNzY6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 76: a worker pulls the next task from the queue",
        "cm91bmQgNzY6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 76: signals travel through the network layer",
        "cm91bmQgNzY6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 76: the gateway routes each request by policy",
        "cm91bmQgNzY6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 76: memory grows until the buffer is full",
        "cm91bmQgNzY6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 76: the cluster mirrors every packet twice",
        "cm91bmQgNzY6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 76: ranking uses tokens learned from the corpus",
        "cm91bmQgNzY6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 76: a long session ends when the candle dies",
        "cm91bmQgNzY6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 76: encode the prompt then map the result",
        "cm91bmQgNzY6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 76: the kernel wakes the worker at dawn", "cm91bmQgNzY6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 76: service latency drops after the patch",
        "cm91bmQgNzY6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 76: the library caches every vector it sees",
        "cm91bmQgNzY6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 76: agents argue then the debate resolves",
        "cm91bmQgNzY6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 76: the filter keeps only strong matches",
        "cm91bmQgNzY6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 76: the model answers with a short reply",
        "cm91bmQgNzY6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 76: the recorder stores the reasoning trace",
        "cm91bmQgNzY6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 76: the angel watches the processor run", "cm91bmQgNzY6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 76: angle of the vector decides the match",
        "cm91bmQgNzY6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 76: the candle burns twice as long at night",
        "cm91bmQgNzY6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 76: a mirror of the universe in one line",
        "cm91bmQgNzY6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 76: the queue drains before the storm", "cm91bmQgNzY6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
