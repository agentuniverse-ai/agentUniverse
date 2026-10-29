"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten90kitten90", "a2l0dGVuOTBraXR0ZW45MA"),
    ("kitten90sitting90", "a2l0dGVuOTBzaXR0aW5nOTA"),
    ("kitten90agent90", "a2l0dGVuOTBhZ2VudDkw"),
    ("kitten90angle90", "a2l0dGVuOTBhbmdsZTkw"),
    ("sitting90angle90", "c2l0dGluZzkwYW5nbGU5MA"),
    ("sitting90universe90", "c2l0dGluZzkwdW5pdmVyc2U5MA"),
    ("sitting90memory90", "c2l0dGluZzkwbWVtb3J5OTA"),
    ("sitting90stream90", "c2l0dGluZzkwc3RyZWFtOTA"),
    ("agent90stream90", "YWdlbnQ5MHN0cmVhbTkw"),
    ("agent90context90", "YWdlbnQ5MGNvbnRleHQ5MA"),
    ("agent90knowledge90", "YWdlbnQ5MGtub3dsZWRnZTkw"),
    ("agent90vector90", "YWdlbnQ5MHZlY3Rvcjkw"),
    ("angle90vector90", "YW5nbGU5MHZlY3Rvcjkw"),
    ("angle90processor90", "YW5nbGU5MHByb2Nlc3Nvcjkw"),
    ("angle90reasoning90", "YW5nbGU5MHJlYXNvbmluZzkw"),
    ("angle90machine90", "YW5nbGU5MG1hY2hpbmU5MA"),
    ("universe90machine90", "dW5pdmVyc2U5MG1hY2hpbmU5MA"),
    ("universe90learning90", "dW5pdmVyc2U5MGxlYXJuaW5nOTA"),
    ("universe90model90", "dW5pdmVyc2U5MG1vZGVsOTA"),
    ("universe90token90", "dW5pdmVyc2U5MHRva2VuOTA"),
    ("memory90token90", "bWVtb3J5OTB0b2tlbjkw"),
    ("memory90prompt90", "bWVtb3J5OTBwcm9tcHQ5MA"),
    ("memory90session90", "bWVtb3J5OTBzZXNzaW9uOTA"),
    ("memory90library90", "bWVtb3J5OTBsaWJyYXJ5OTA"),
    ("stream90library90", "c3RyZWFtOTBsaWJyYXJ5OTA"),
    ("stream90service90", "c3RyZWFtOTBzZXJ2aWNlOTA"),
    ("stream90gateway90", "c3RyZWFtOTBnYXRld2F5OTA"),
    ("stream90storage90", "c3RyZWFtOTBzdG9yYWdlOTA"),
    ("context90storage90", "Y29udGV4dDkwc3RvcmFnZTkw"),
    ("context90network90", "Y29udGV4dDkwbmV0d29yazkw"),
    ("context90latency90", "Y29udGV4dDkwbGF0ZW5jeTkw"),
    ("context90buffer90", "Y29udGV4dDkwYnVmZmVyOTA"),
    ("knowledge90buffer90", "a25vd2xlZGdlOTBidWZmZXI5MA"),
    ("knowledge90queue90", "a25vd2xlZGdlOTBxdWV1ZTkw"),
    ("knowledge90worker90", "a25vd2xlZGdlOTB3b3JrZXI5MA"),
    ("knowledge90kernel90", "a25vd2xlZGdlOTBrZXJuZWw5MA"),
    ("vector90kernel90", "dmVjdG9yOTBrZXJuZWw5MA"),
    ("vector90signal90", "dmVjdG9yOTBzaWduYWw5MA"),
    ("vector90packet90", "dmVjdG9yOTBwYWNrZXQ5MA"),
    ("vector90router90", "dmVjdG9yOTByb3V0ZXI5MA"),
    ("processor90router90", "cHJvY2Vzc29yOTByb3V0ZXI5MA"),
    ("processor90cluster90", "cHJvY2Vzc29yOTBjbHVzdGVyOTA"),
    ("processor90mirror90", "cHJvY2Vzc29yOTBtaXJyb3I5MA"),
    ("processor90filter90", "cHJvY2Vzc29yOTBmaWx0ZXI5MA"),
    ("reasoning90filter90", "cmVhc29uaW5nOTBmaWx0ZXI5MA"),
    ("reasoning90ranking90", "cmVhc29uaW5nOTByYW5raW5nOTA"),
    ("reasoning90encoding90", "cmVhc29uaW5nOTBlbmNvZGluZzkw"),
    ("reasoning90mapping90", "cmVhc29uaW5nOTBtYXBwaW5nOTA"),
    ("machine90mapping90", "bWFjaGluZTkwbWFwcGluZzkw"),
    ("machine90record90", "bWFjaGluZTkwcmVjb3JkOTA"),
    ("machine90candle90", "bWFjaGluZTkwY2FuZGxlOTA"),
    ("machine90thread90", "bWFjaGluZTkwdGhyZWFkOTA"),
    ("learning90thread90", "bGVhcm5pbmc5MHRocmVhZDkw"),
    ("learning90kitten90", "bGVhcm5pbmc5MGtpdHRlbjkw"),
    ("learning90sitting90", "bGVhcm5pbmc5MHNpdHRpbmc5MA"),
    ("learning90agent90", "bGVhcm5pbmc5MGFnZW50OTA"),
    ("model90agent90", "bW9kZWw5MGFnZW50OTA"),
    ("model90angle90", "bW9kZWw5MGFuZ2xlOTA"),
    ("model90universe90", "bW9kZWw5MHVuaXZlcnNlOTA"),
    ("model90memory90", "bW9kZWw5MG1lbW9yeTkw"),
    ("token90memory90", "dG9rZW45MG1lbW9yeTkw"),
    ("token90stream90", "dG9rZW45MHN0cmVhbTkw"),
    ("token90context90", "dG9rZW45MGNvbnRleHQ5MA"),
    ("token90knowledge90", "dG9rZW45MGtub3dsZWRnZTkw"),
    ("prompt90knowledge90", "cHJvbXB0OTBrbm93bGVkZ2U5MA"),
    ("prompt90vector90", "cHJvbXB0OTB2ZWN0b3I5MA"),
    ("prompt90processor90", "cHJvbXB0OTBwcm9jZXNzb3I5MA"),
    ("prompt90reasoning90", "cHJvbXB0OTByZWFzb25pbmc5MA"),
    ("session90reasoning90", "c2Vzc2lvbjkwcmVhc29uaW5nOTA"),
    ("session90machine90", "c2Vzc2lvbjkwbWFjaGluZTkw"),
    ("session90learning90", "c2Vzc2lvbjkwbGVhcm5pbmc5MA"),
    ("session90model90", "c2Vzc2lvbjkwbW9kZWw5MA"),
    ("library90model90", "bGlicmFyeTkwbW9kZWw5MA"),
    ("library90token90", "bGlicmFyeTkwdG9rZW45MA"),
    ("library90prompt90", "bGlicmFyeTkwcHJvbXB0OTA"),
    ("library90session90", "bGlicmFyeTkwc2Vzc2lvbjkw"),
    ("service90session90", "c2VydmljZTkwc2Vzc2lvbjkw"),
    ("service90library90", "c2VydmljZTkwbGlicmFyeTkw"),
    ("service90service90", "c2VydmljZTkwc2VydmljZTkw"),
    ("service90gateway90", "c2VydmljZTkwZ2F0ZXdheTkw"),
    ("gateway90gateway90", "Z2F0ZXdheTkwZ2F0ZXdheTkw"),
    ("gateway90storage90", "Z2F0ZXdheTkwc3RvcmFnZTkw"),
    ("gateway90network90", "Z2F0ZXdheTkwbmV0d29yazkw"),
    ("gateway90latency90", "Z2F0ZXdheTkwbGF0ZW5jeTkw"),
    ("storage90latency90", "c3RvcmFnZTkwbGF0ZW5jeTkw"),
    ("storage90buffer90", "c3RvcmFnZTkwYnVmZmVyOTA"),
    ("storage90queue90", "c3RvcmFnZTkwcXVldWU5MA"),
    ("storage90worker90", "c3RvcmFnZTkwd29ya2VyOTA"),
    ("network90worker90", "bmV0d29yazkwd29ya2VyOTA"),
    ("network90kernel90", "bmV0d29yazkwa2VybmVsOTA"),
    ("network90signal90", "bmV0d29yazkwc2lnbmFsOTA"),
    ("network90packet90", "bmV0d29yazkwcGFja2V0OTA"),
    ("latency90packet90", "bGF0ZW5jeTkwcGFja2V0OTA"),
    ("latency90router90", "bGF0ZW5jeTkwcm91dGVyOTA"),
    ("latency90cluster90", "bGF0ZW5jeTkwY2x1c3Rlcjkw"),
    ("latency90mirror90", "bGF0ZW5jeTkwbWlycm9yOTA"),
    ("buffer90mirror90", "YnVmZmVyOTBtaXJyb3I5MA"),
    ("buffer90filter90", "YnVmZmVyOTBmaWx0ZXI5MA"),
    ("buffer90ranking90", "YnVmZmVyOTByYW5raW5nOTA"),
    ("buffer90encoding90", "YnVmZmVyOTBlbmNvZGluZzkw"),
    ("queue90encoding90", "cXVldWU5MGVuY29kaW5nOTA"),
    ("queue90mapping90", "cXVldWU5MG1hcHBpbmc5MA"),
    ("queue90record90", "cXVldWU5MHJlY29yZDkw"),
    ("queue90candle90", "cXVldWU5MGNhbmRsZTkw"),
    ("worker90candle90", "d29ya2VyOTBjYW5kbGU5MA"),
    ("worker90thread90", "d29ya2VyOTB0aHJlYWQ5MA"),
    ("worker90kitten90", "d29ya2VyOTBraXR0ZW45MA"),
    ("worker90sitting90", "d29ya2VyOTBzaXR0aW5nOTA"),
    ("kernel90sitting90", "a2VybmVsOTBzaXR0aW5nOTA"),
    ("kernel90agent90", "a2VybmVsOTBhZ2VudDkw"),
    ("kernel90angle90", "a2VybmVsOTBhbmdsZTkw"),
    ("kernel90universe90", "a2VybmVsOTB1bml2ZXJzZTkw"),
    ("signal90universe90", "c2lnbmFsOTB1bml2ZXJzZTkw"),
    ("signal90memory90", "c2lnbmFsOTBtZW1vcnk5MA"),
    ("signal90stream90", "c2lnbmFsOTBzdHJlYW05MA"),
    ("signal90context90", "c2lnbmFsOTBjb250ZXh0OTA"),
    ("packet90context90", "cGFja2V0OTBjb250ZXh0OTA"),
    ("packet90knowledge90", "cGFja2V0OTBrbm93bGVkZ2U5MA"),
    ("packet90vector90", "cGFja2V0OTB2ZWN0b3I5MA"),
    ("packet90processor90", "cGFja2V0OTBwcm9jZXNzb3I5MA"),
    ("router90processor90", "cm91dGVyOTBwcm9jZXNzb3I5MA"),
    ("router90reasoning90", "cm91dGVyOTByZWFzb25pbmc5MA"),
    ("router90machine90", "cm91dGVyOTBtYWNoaW5lOTA"),
    ("router90learning90", "cm91dGVyOTBsZWFybmluZzkw"),
    ("cluster90learning90", "Y2x1c3RlcjkwbGVhcm5pbmc5MA"),
    ("cluster90model90", "Y2x1c3RlcjkwbW9kZWw5MA"),
    ("cluster90token90", "Y2x1c3RlcjkwdG9rZW45MA"),
    ("cluster90prompt90", "Y2x1c3RlcjkwcHJvbXB0OTA"),
    ("mirror90prompt90", "bWlycm9yOTBwcm9tcHQ5MA"),
    ("mirror90session90", "bWlycm9yOTBzZXNzaW9uOTA"),
    ("mirror90library90", "bWlycm9yOTBsaWJyYXJ5OTA"),
    ("mirror90service90", "bWlycm9yOTBzZXJ2aWNlOTA"),
    ("filter90service90", "ZmlsdGVyOTBzZXJ2aWNlOTA"),
    ("filter90gateway90", "ZmlsdGVyOTBnYXRld2F5OTA"),
    ("filter90storage90", "ZmlsdGVyOTBzdG9yYWdlOTA"),
    ("filter90network90", "ZmlsdGVyOTBuZXR3b3JrOTA"),
    ("ranking90network90", "cmFua2luZzkwbmV0d29yazkw"),
    ("ranking90latency90", "cmFua2luZzkwbGF0ZW5jeTkw"),
    ("ranking90buffer90", "cmFua2luZzkwYnVmZmVyOTA"),
    ("ranking90queue90", "cmFua2luZzkwcXVldWU5MA"),
    ("encoding90queue90", "ZW5jb2Rpbmc5MHF1ZXVlOTA"),
    ("encoding90worker90", "ZW5jb2Rpbmc5MHdvcmtlcjkw"),
    ("encoding90kernel90", "ZW5jb2Rpbmc5MGtlcm5lbDkw"),
    ("encoding90signal90", "ZW5jb2Rpbmc5MHNpZ25hbDkw"),
    ("mapping90signal90", "bWFwcGluZzkwc2lnbmFsOTA"),
    ("mapping90packet90", "bWFwcGluZzkwcGFja2V0OTA"),
    ("mapping90router90", "bWFwcGluZzkwcm91dGVyOTA"),
    ("mapping90cluster90", "bWFwcGluZzkwY2x1c3Rlcjkw"),
    ("record90cluster90", "cmVjb3JkOTBjbHVzdGVyOTA"),
    ("record90mirror90", "cmVjb3JkOTBtaXJyb3I5MA"),
    ("record90filter90", "cmVjb3JkOTBmaWx0ZXI5MA"),
    ("record90ranking90", "cmVjb3JkOTByYW5raW5nOTA"),
    ("candle90ranking90", "Y2FuZGxlOTByYW5raW5nOTA"),
    ("candle90encoding90", "Y2FuZGxlOTBlbmNvZGluZzkw"),
    ("candle90mapping90", "Y2FuZGxlOTBtYXBwaW5nOTA"),
    ("candle90record90", "Y2FuZGxlOTByZWNvcmQ5MA"),
    ("thread90record90", "dGhyZWFkOTByZWNvcmQ5MA"),
    ("thread90candle90", "dGhyZWFkOTBjYW5kbGU5MA"),
    ("thread90thread90", "dGhyZWFkOTB0aHJlYWQ5MA"),
    ("thread90kitten90", "dGhyZWFkOTBraXR0ZW45MA"),
    (
        "round 90: the quick brown fox jumps over the lazy dog",
        "cm91bmQgOTA6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 90: agentuniverse is a framework for multi agents",
        "cm91bmQgOTA6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 90: knowledge stored as vectors enables retrieval",
        "cm91bmQgOTA6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 90: the processor reads the record then stops",
        "cm91bmQgOTA6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 90: a worker pulls the next task from the queue",
        "cm91bmQgOTA6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 90: signals travel through the network layer",
        "cm91bmQgOTA6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 90: the gateway routes each request by policy",
        "cm91bmQgOTA6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 90: memory grows until the buffer is full",
        "cm91bmQgOTA6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 90: the cluster mirrors every packet twice",
        "cm91bmQgOTA6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 90: ranking uses tokens learned from the corpus",
        "cm91bmQgOTA6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 90: a long session ends when the candle dies",
        "cm91bmQgOTA6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 90: encode the prompt then map the result",
        "cm91bmQgOTA6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 90: the kernel wakes the worker at dawn", "cm91bmQgOTA6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 90: service latency drops after the patch",
        "cm91bmQgOTA6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 90: the library caches every vector it sees",
        "cm91bmQgOTA6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 90: agents argue then the debate resolves",
        "cm91bmQgOTA6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 90: the filter keeps only strong matches",
        "cm91bmQgOTA6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 90: the model answers with a short reply",
        "cm91bmQgOTA6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 90: the recorder stores the reasoning trace",
        "cm91bmQgOTA6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 90: the angel watches the processor run", "cm91bmQgOTA6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 90: angle of the vector decides the match",
        "cm91bmQgOTA6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 90: the candle burns twice as long at night",
        "cm91bmQgOTA6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 90: a mirror of the universe in one line",
        "cm91bmQgOTA6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 90: the queue drains before the storm", "cm91bmQgOTA6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
