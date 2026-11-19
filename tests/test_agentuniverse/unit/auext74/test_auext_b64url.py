"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten74kitten74", "a2l0dGVuNzRraXR0ZW43NA"),
    ("kitten74sitting74", "a2l0dGVuNzRzaXR0aW5nNzQ"),
    ("kitten74agent74", "a2l0dGVuNzRhZ2VudDc0"),
    ("kitten74angle74", "a2l0dGVuNzRhbmdsZTc0"),
    ("sitting74angle74", "c2l0dGluZzc0YW5nbGU3NA"),
    ("sitting74universe74", "c2l0dGluZzc0dW5pdmVyc2U3NA"),
    ("sitting74memory74", "c2l0dGluZzc0bWVtb3J5NzQ"),
    ("sitting74stream74", "c2l0dGluZzc0c3RyZWFtNzQ"),
    ("agent74stream74", "YWdlbnQ3NHN0cmVhbTc0"),
    ("agent74context74", "YWdlbnQ3NGNvbnRleHQ3NA"),
    ("agent74knowledge74", "YWdlbnQ3NGtub3dsZWRnZTc0"),
    ("agent74vector74", "YWdlbnQ3NHZlY3Rvcjc0"),
    ("angle74vector74", "YW5nbGU3NHZlY3Rvcjc0"),
    ("angle74processor74", "YW5nbGU3NHByb2Nlc3Nvcjc0"),
    ("angle74reasoning74", "YW5nbGU3NHJlYXNvbmluZzc0"),
    ("angle74machine74", "YW5nbGU3NG1hY2hpbmU3NA"),
    ("universe74machine74", "dW5pdmVyc2U3NG1hY2hpbmU3NA"),
    ("universe74learning74", "dW5pdmVyc2U3NGxlYXJuaW5nNzQ"),
    ("universe74model74", "dW5pdmVyc2U3NG1vZGVsNzQ"),
    ("universe74token74", "dW5pdmVyc2U3NHRva2VuNzQ"),
    ("memory74token74", "bWVtb3J5NzR0b2tlbjc0"),
    ("memory74prompt74", "bWVtb3J5NzRwcm9tcHQ3NA"),
    ("memory74session74", "bWVtb3J5NzRzZXNzaW9uNzQ"),
    ("memory74library74", "bWVtb3J5NzRsaWJyYXJ5NzQ"),
    ("stream74library74", "c3RyZWFtNzRsaWJyYXJ5NzQ"),
    ("stream74service74", "c3RyZWFtNzRzZXJ2aWNlNzQ"),
    ("stream74gateway74", "c3RyZWFtNzRnYXRld2F5NzQ"),
    ("stream74storage74", "c3RyZWFtNzRzdG9yYWdlNzQ"),
    ("context74storage74", "Y29udGV4dDc0c3RvcmFnZTc0"),
    ("context74network74", "Y29udGV4dDc0bmV0d29yazc0"),
    ("context74latency74", "Y29udGV4dDc0bGF0ZW5jeTc0"),
    ("context74buffer74", "Y29udGV4dDc0YnVmZmVyNzQ"),
    ("knowledge74buffer74", "a25vd2xlZGdlNzRidWZmZXI3NA"),
    ("knowledge74queue74", "a25vd2xlZGdlNzRxdWV1ZTc0"),
    ("knowledge74worker74", "a25vd2xlZGdlNzR3b3JrZXI3NA"),
    ("knowledge74kernel74", "a25vd2xlZGdlNzRrZXJuZWw3NA"),
    ("vector74kernel74", "dmVjdG9yNzRrZXJuZWw3NA"),
    ("vector74signal74", "dmVjdG9yNzRzaWduYWw3NA"),
    ("vector74packet74", "dmVjdG9yNzRwYWNrZXQ3NA"),
    ("vector74router74", "dmVjdG9yNzRyb3V0ZXI3NA"),
    ("processor74router74", "cHJvY2Vzc29yNzRyb3V0ZXI3NA"),
    ("processor74cluster74", "cHJvY2Vzc29yNzRjbHVzdGVyNzQ"),
    ("processor74mirror74", "cHJvY2Vzc29yNzRtaXJyb3I3NA"),
    ("processor74filter74", "cHJvY2Vzc29yNzRmaWx0ZXI3NA"),
    ("reasoning74filter74", "cmVhc29uaW5nNzRmaWx0ZXI3NA"),
    ("reasoning74ranking74", "cmVhc29uaW5nNzRyYW5raW5nNzQ"),
    ("reasoning74encoding74", "cmVhc29uaW5nNzRlbmNvZGluZzc0"),
    ("reasoning74mapping74", "cmVhc29uaW5nNzRtYXBwaW5nNzQ"),
    ("machine74mapping74", "bWFjaGluZTc0bWFwcGluZzc0"),
    ("machine74record74", "bWFjaGluZTc0cmVjb3JkNzQ"),
    ("machine74candle74", "bWFjaGluZTc0Y2FuZGxlNzQ"),
    ("machine74thread74", "bWFjaGluZTc0dGhyZWFkNzQ"),
    ("learning74thread74", "bGVhcm5pbmc3NHRocmVhZDc0"),
    ("learning74kitten74", "bGVhcm5pbmc3NGtpdHRlbjc0"),
    ("learning74sitting74", "bGVhcm5pbmc3NHNpdHRpbmc3NA"),
    ("learning74agent74", "bGVhcm5pbmc3NGFnZW50NzQ"),
    ("model74agent74", "bW9kZWw3NGFnZW50NzQ"),
    ("model74angle74", "bW9kZWw3NGFuZ2xlNzQ"),
    ("model74universe74", "bW9kZWw3NHVuaXZlcnNlNzQ"),
    ("model74memory74", "bW9kZWw3NG1lbW9yeTc0"),
    ("token74memory74", "dG9rZW43NG1lbW9yeTc0"),
    ("token74stream74", "dG9rZW43NHN0cmVhbTc0"),
    ("token74context74", "dG9rZW43NGNvbnRleHQ3NA"),
    ("token74knowledge74", "dG9rZW43NGtub3dsZWRnZTc0"),
    ("prompt74knowledge74", "cHJvbXB0NzRrbm93bGVkZ2U3NA"),
    ("prompt74vector74", "cHJvbXB0NzR2ZWN0b3I3NA"),
    ("prompt74processor74", "cHJvbXB0NzRwcm9jZXNzb3I3NA"),
    ("prompt74reasoning74", "cHJvbXB0NzRyZWFzb25pbmc3NA"),
    ("session74reasoning74", "c2Vzc2lvbjc0cmVhc29uaW5nNzQ"),
    ("session74machine74", "c2Vzc2lvbjc0bWFjaGluZTc0"),
    ("session74learning74", "c2Vzc2lvbjc0bGVhcm5pbmc3NA"),
    ("session74model74", "c2Vzc2lvbjc0bW9kZWw3NA"),
    ("library74model74", "bGlicmFyeTc0bW9kZWw3NA"),
    ("library74token74", "bGlicmFyeTc0dG9rZW43NA"),
    ("library74prompt74", "bGlicmFyeTc0cHJvbXB0NzQ"),
    ("library74session74", "bGlicmFyeTc0c2Vzc2lvbjc0"),
    ("service74session74", "c2VydmljZTc0c2Vzc2lvbjc0"),
    ("service74library74", "c2VydmljZTc0bGlicmFyeTc0"),
    ("service74service74", "c2VydmljZTc0c2VydmljZTc0"),
    ("service74gateway74", "c2VydmljZTc0Z2F0ZXdheTc0"),
    ("gateway74gateway74", "Z2F0ZXdheTc0Z2F0ZXdheTc0"),
    ("gateway74storage74", "Z2F0ZXdheTc0c3RvcmFnZTc0"),
    ("gateway74network74", "Z2F0ZXdheTc0bmV0d29yazc0"),
    ("gateway74latency74", "Z2F0ZXdheTc0bGF0ZW5jeTc0"),
    ("storage74latency74", "c3RvcmFnZTc0bGF0ZW5jeTc0"),
    ("storage74buffer74", "c3RvcmFnZTc0YnVmZmVyNzQ"),
    ("storage74queue74", "c3RvcmFnZTc0cXVldWU3NA"),
    ("storage74worker74", "c3RvcmFnZTc0d29ya2VyNzQ"),
    ("network74worker74", "bmV0d29yazc0d29ya2VyNzQ"),
    ("network74kernel74", "bmV0d29yazc0a2VybmVsNzQ"),
    ("network74signal74", "bmV0d29yazc0c2lnbmFsNzQ"),
    ("network74packet74", "bmV0d29yazc0cGFja2V0NzQ"),
    ("latency74packet74", "bGF0ZW5jeTc0cGFja2V0NzQ"),
    ("latency74router74", "bGF0ZW5jeTc0cm91dGVyNzQ"),
    ("latency74cluster74", "bGF0ZW5jeTc0Y2x1c3Rlcjc0"),
    ("latency74mirror74", "bGF0ZW5jeTc0bWlycm9yNzQ"),
    ("buffer74mirror74", "YnVmZmVyNzRtaXJyb3I3NA"),
    ("buffer74filter74", "YnVmZmVyNzRmaWx0ZXI3NA"),
    ("buffer74ranking74", "YnVmZmVyNzRyYW5raW5nNzQ"),
    ("buffer74encoding74", "YnVmZmVyNzRlbmNvZGluZzc0"),
    ("queue74encoding74", "cXVldWU3NGVuY29kaW5nNzQ"),
    ("queue74mapping74", "cXVldWU3NG1hcHBpbmc3NA"),
    ("queue74record74", "cXVldWU3NHJlY29yZDc0"),
    ("queue74candle74", "cXVldWU3NGNhbmRsZTc0"),
    ("worker74candle74", "d29ya2VyNzRjYW5kbGU3NA"),
    ("worker74thread74", "d29ya2VyNzR0aHJlYWQ3NA"),
    ("worker74kitten74", "d29ya2VyNzRraXR0ZW43NA"),
    ("worker74sitting74", "d29ya2VyNzRzaXR0aW5nNzQ"),
    ("kernel74sitting74", "a2VybmVsNzRzaXR0aW5nNzQ"),
    ("kernel74agent74", "a2VybmVsNzRhZ2VudDc0"),
    ("kernel74angle74", "a2VybmVsNzRhbmdsZTc0"),
    ("kernel74universe74", "a2VybmVsNzR1bml2ZXJzZTc0"),
    ("signal74universe74", "c2lnbmFsNzR1bml2ZXJzZTc0"),
    ("signal74memory74", "c2lnbmFsNzRtZW1vcnk3NA"),
    ("signal74stream74", "c2lnbmFsNzRzdHJlYW03NA"),
    ("signal74context74", "c2lnbmFsNzRjb250ZXh0NzQ"),
    ("packet74context74", "cGFja2V0NzRjb250ZXh0NzQ"),
    ("packet74knowledge74", "cGFja2V0NzRrbm93bGVkZ2U3NA"),
    ("packet74vector74", "cGFja2V0NzR2ZWN0b3I3NA"),
    ("packet74processor74", "cGFja2V0NzRwcm9jZXNzb3I3NA"),
    ("router74processor74", "cm91dGVyNzRwcm9jZXNzb3I3NA"),
    ("router74reasoning74", "cm91dGVyNzRyZWFzb25pbmc3NA"),
    ("router74machine74", "cm91dGVyNzRtYWNoaW5lNzQ"),
    ("router74learning74", "cm91dGVyNzRsZWFybmluZzc0"),
    ("cluster74learning74", "Y2x1c3Rlcjc0bGVhcm5pbmc3NA"),
    ("cluster74model74", "Y2x1c3Rlcjc0bW9kZWw3NA"),
    ("cluster74token74", "Y2x1c3Rlcjc0dG9rZW43NA"),
    ("cluster74prompt74", "Y2x1c3Rlcjc0cHJvbXB0NzQ"),
    ("mirror74prompt74", "bWlycm9yNzRwcm9tcHQ3NA"),
    ("mirror74session74", "bWlycm9yNzRzZXNzaW9uNzQ"),
    ("mirror74library74", "bWlycm9yNzRsaWJyYXJ5NzQ"),
    ("mirror74service74", "bWlycm9yNzRzZXJ2aWNlNzQ"),
    ("filter74service74", "ZmlsdGVyNzRzZXJ2aWNlNzQ"),
    ("filter74gateway74", "ZmlsdGVyNzRnYXRld2F5NzQ"),
    ("filter74storage74", "ZmlsdGVyNzRzdG9yYWdlNzQ"),
    ("filter74network74", "ZmlsdGVyNzRuZXR3b3JrNzQ"),
    ("ranking74network74", "cmFua2luZzc0bmV0d29yazc0"),
    ("ranking74latency74", "cmFua2luZzc0bGF0ZW5jeTc0"),
    ("ranking74buffer74", "cmFua2luZzc0YnVmZmVyNzQ"),
    ("ranking74queue74", "cmFua2luZzc0cXVldWU3NA"),
    ("encoding74queue74", "ZW5jb2Rpbmc3NHF1ZXVlNzQ"),
    ("encoding74worker74", "ZW5jb2Rpbmc3NHdvcmtlcjc0"),
    ("encoding74kernel74", "ZW5jb2Rpbmc3NGtlcm5lbDc0"),
    ("encoding74signal74", "ZW5jb2Rpbmc3NHNpZ25hbDc0"),
    ("mapping74signal74", "bWFwcGluZzc0c2lnbmFsNzQ"),
    ("mapping74packet74", "bWFwcGluZzc0cGFja2V0NzQ"),
    ("mapping74router74", "bWFwcGluZzc0cm91dGVyNzQ"),
    ("mapping74cluster74", "bWFwcGluZzc0Y2x1c3Rlcjc0"),
    ("record74cluster74", "cmVjb3JkNzRjbHVzdGVyNzQ"),
    ("record74mirror74", "cmVjb3JkNzRtaXJyb3I3NA"),
    ("record74filter74", "cmVjb3JkNzRmaWx0ZXI3NA"),
    ("record74ranking74", "cmVjb3JkNzRyYW5raW5nNzQ"),
    ("candle74ranking74", "Y2FuZGxlNzRyYW5raW5nNzQ"),
    ("candle74encoding74", "Y2FuZGxlNzRlbmNvZGluZzc0"),
    ("candle74mapping74", "Y2FuZGxlNzRtYXBwaW5nNzQ"),
    ("candle74record74", "Y2FuZGxlNzRyZWNvcmQ3NA"),
    ("thread74record74", "dGhyZWFkNzRyZWNvcmQ3NA"),
    ("thread74candle74", "dGhyZWFkNzRjYW5kbGU3NA"),
    ("thread74thread74", "dGhyZWFkNzR0aHJlYWQ3NA"),
    ("thread74kitten74", "dGhyZWFkNzRraXR0ZW43NA"),
    (
        "round 74: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzQ6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 74: agentuniverse is a framework for multi agents",
        "cm91bmQgNzQ6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 74: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzQ6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 74: the processor reads the record then stops",
        "cm91bmQgNzQ6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 74: a worker pulls the next task from the queue",
        "cm91bmQgNzQ6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 74: signals travel through the network layer",
        "cm91bmQgNzQ6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 74: the gateway routes each request by policy",
        "cm91bmQgNzQ6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 74: memory grows until the buffer is full",
        "cm91bmQgNzQ6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 74: the cluster mirrors every packet twice",
        "cm91bmQgNzQ6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 74: ranking uses tokens learned from the corpus",
        "cm91bmQgNzQ6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 74: a long session ends when the candle dies",
        "cm91bmQgNzQ6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 74: encode the prompt then map the result",
        "cm91bmQgNzQ6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 74: the kernel wakes the worker at dawn", "cm91bmQgNzQ6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 74: service latency drops after the patch",
        "cm91bmQgNzQ6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 74: the library caches every vector it sees",
        "cm91bmQgNzQ6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 74: agents argue then the debate resolves",
        "cm91bmQgNzQ6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 74: the filter keeps only strong matches",
        "cm91bmQgNzQ6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 74: the model answers with a short reply",
        "cm91bmQgNzQ6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 74: the recorder stores the reasoning trace",
        "cm91bmQgNzQ6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 74: the angel watches the processor run", "cm91bmQgNzQ6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 74: angle of the vector decides the match",
        "cm91bmQgNzQ6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 74: the candle burns twice as long at night",
        "cm91bmQgNzQ6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 74: a mirror of the universe in one line",
        "cm91bmQgNzQ6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 74: the queue drains before the storm", "cm91bmQgNzQ6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
