"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten19kitten19", "a2l0dGVuMTlraXR0ZW4xOQ"),
    ("kitten19sitting19", "a2l0dGVuMTlzaXR0aW5nMTk"),
    ("kitten19agent19", "a2l0dGVuMTlhZ2VudDE5"),
    ("kitten19angle19", "a2l0dGVuMTlhbmdsZTE5"),
    ("sitting19angle19", "c2l0dGluZzE5YW5nbGUxOQ"),
    ("sitting19universe19", "c2l0dGluZzE5dW5pdmVyc2UxOQ"),
    ("sitting19memory19", "c2l0dGluZzE5bWVtb3J5MTk"),
    ("sitting19stream19", "c2l0dGluZzE5c3RyZWFtMTk"),
    ("agent19stream19", "YWdlbnQxOXN0cmVhbTE5"),
    ("agent19context19", "YWdlbnQxOWNvbnRleHQxOQ"),
    ("agent19knowledge19", "YWdlbnQxOWtub3dsZWRnZTE5"),
    ("agent19vector19", "YWdlbnQxOXZlY3RvcjE5"),
    ("angle19vector19", "YW5nbGUxOXZlY3RvcjE5"),
    ("angle19processor19", "YW5nbGUxOXByb2Nlc3NvcjE5"),
    ("angle19reasoning19", "YW5nbGUxOXJlYXNvbmluZzE5"),
    ("angle19machine19", "YW5nbGUxOW1hY2hpbmUxOQ"),
    ("universe19machine19", "dW5pdmVyc2UxOW1hY2hpbmUxOQ"),
    ("universe19learning19", "dW5pdmVyc2UxOWxlYXJuaW5nMTk"),
    ("universe19model19", "dW5pdmVyc2UxOW1vZGVsMTk"),
    ("universe19token19", "dW5pdmVyc2UxOXRva2VuMTk"),
    ("memory19token19", "bWVtb3J5MTl0b2tlbjE5"),
    ("memory19prompt19", "bWVtb3J5MTlwcm9tcHQxOQ"),
    ("memory19session19", "bWVtb3J5MTlzZXNzaW9uMTk"),
    ("memory19library19", "bWVtb3J5MTlsaWJyYXJ5MTk"),
    ("stream19library19", "c3RyZWFtMTlsaWJyYXJ5MTk"),
    ("stream19service19", "c3RyZWFtMTlzZXJ2aWNlMTk"),
    ("stream19gateway19", "c3RyZWFtMTlnYXRld2F5MTk"),
    ("stream19storage19", "c3RyZWFtMTlzdG9yYWdlMTk"),
    ("context19storage19", "Y29udGV4dDE5c3RvcmFnZTE5"),
    ("context19network19", "Y29udGV4dDE5bmV0d29yazE5"),
    ("context19latency19", "Y29udGV4dDE5bGF0ZW5jeTE5"),
    ("context19buffer19", "Y29udGV4dDE5YnVmZmVyMTk"),
    ("knowledge19buffer19", "a25vd2xlZGdlMTlidWZmZXIxOQ"),
    ("knowledge19queue19", "a25vd2xlZGdlMTlxdWV1ZTE5"),
    ("knowledge19worker19", "a25vd2xlZGdlMTl3b3JrZXIxOQ"),
    ("knowledge19kernel19", "a25vd2xlZGdlMTlrZXJuZWwxOQ"),
    ("vector19kernel19", "dmVjdG9yMTlrZXJuZWwxOQ"),
    ("vector19signal19", "dmVjdG9yMTlzaWduYWwxOQ"),
    ("vector19packet19", "dmVjdG9yMTlwYWNrZXQxOQ"),
    ("vector19router19", "dmVjdG9yMTlyb3V0ZXIxOQ"),
    ("processor19router19", "cHJvY2Vzc29yMTlyb3V0ZXIxOQ"),
    ("processor19cluster19", "cHJvY2Vzc29yMTljbHVzdGVyMTk"),
    ("processor19mirror19", "cHJvY2Vzc29yMTltaXJyb3IxOQ"),
    ("processor19filter19", "cHJvY2Vzc29yMTlmaWx0ZXIxOQ"),
    ("reasoning19filter19", "cmVhc29uaW5nMTlmaWx0ZXIxOQ"),
    ("reasoning19ranking19", "cmVhc29uaW5nMTlyYW5raW5nMTk"),
    ("reasoning19encoding19", "cmVhc29uaW5nMTllbmNvZGluZzE5"),
    ("reasoning19mapping19", "cmVhc29uaW5nMTltYXBwaW5nMTk"),
    ("machine19mapping19", "bWFjaGluZTE5bWFwcGluZzE5"),
    ("machine19record19", "bWFjaGluZTE5cmVjb3JkMTk"),
    ("machine19candle19", "bWFjaGluZTE5Y2FuZGxlMTk"),
    ("machine19thread19", "bWFjaGluZTE5dGhyZWFkMTk"),
    ("learning19thread19", "bGVhcm5pbmcxOXRocmVhZDE5"),
    ("learning19kitten19", "bGVhcm5pbmcxOWtpdHRlbjE5"),
    ("learning19sitting19", "bGVhcm5pbmcxOXNpdHRpbmcxOQ"),
    ("learning19agent19", "bGVhcm5pbmcxOWFnZW50MTk"),
    ("model19agent19", "bW9kZWwxOWFnZW50MTk"),
    ("model19angle19", "bW9kZWwxOWFuZ2xlMTk"),
    ("model19universe19", "bW9kZWwxOXVuaXZlcnNlMTk"),
    ("model19memory19", "bW9kZWwxOW1lbW9yeTE5"),
    ("token19memory19", "dG9rZW4xOW1lbW9yeTE5"),
    ("token19stream19", "dG9rZW4xOXN0cmVhbTE5"),
    ("token19context19", "dG9rZW4xOWNvbnRleHQxOQ"),
    ("token19knowledge19", "dG9rZW4xOWtub3dsZWRnZTE5"),
    ("prompt19knowledge19", "cHJvbXB0MTlrbm93bGVkZ2UxOQ"),
    ("prompt19vector19", "cHJvbXB0MTl2ZWN0b3IxOQ"),
    ("prompt19processor19", "cHJvbXB0MTlwcm9jZXNzb3IxOQ"),
    ("prompt19reasoning19", "cHJvbXB0MTlyZWFzb25pbmcxOQ"),
    ("session19reasoning19", "c2Vzc2lvbjE5cmVhc29uaW5nMTk"),
    ("session19machine19", "c2Vzc2lvbjE5bWFjaGluZTE5"),
    ("session19learning19", "c2Vzc2lvbjE5bGVhcm5pbmcxOQ"),
    ("session19model19", "c2Vzc2lvbjE5bW9kZWwxOQ"),
    ("library19model19", "bGlicmFyeTE5bW9kZWwxOQ"),
    ("library19token19", "bGlicmFyeTE5dG9rZW4xOQ"),
    ("library19prompt19", "bGlicmFyeTE5cHJvbXB0MTk"),
    ("library19session19", "bGlicmFyeTE5c2Vzc2lvbjE5"),
    ("service19session19", "c2VydmljZTE5c2Vzc2lvbjE5"),
    ("service19library19", "c2VydmljZTE5bGlicmFyeTE5"),
    ("service19service19", "c2VydmljZTE5c2VydmljZTE5"),
    ("service19gateway19", "c2VydmljZTE5Z2F0ZXdheTE5"),
    ("gateway19gateway19", "Z2F0ZXdheTE5Z2F0ZXdheTE5"),
    ("gateway19storage19", "Z2F0ZXdheTE5c3RvcmFnZTE5"),
    ("gateway19network19", "Z2F0ZXdheTE5bmV0d29yazE5"),
    ("gateway19latency19", "Z2F0ZXdheTE5bGF0ZW5jeTE5"),
    ("storage19latency19", "c3RvcmFnZTE5bGF0ZW5jeTE5"),
    ("storage19buffer19", "c3RvcmFnZTE5YnVmZmVyMTk"),
    ("storage19queue19", "c3RvcmFnZTE5cXVldWUxOQ"),
    ("storage19worker19", "c3RvcmFnZTE5d29ya2VyMTk"),
    ("network19worker19", "bmV0d29yazE5d29ya2VyMTk"),
    ("network19kernel19", "bmV0d29yazE5a2VybmVsMTk"),
    ("network19signal19", "bmV0d29yazE5c2lnbmFsMTk"),
    ("network19packet19", "bmV0d29yazE5cGFja2V0MTk"),
    ("latency19packet19", "bGF0ZW5jeTE5cGFja2V0MTk"),
    ("latency19router19", "bGF0ZW5jeTE5cm91dGVyMTk"),
    ("latency19cluster19", "bGF0ZW5jeTE5Y2x1c3RlcjE5"),
    ("latency19mirror19", "bGF0ZW5jeTE5bWlycm9yMTk"),
    ("buffer19mirror19", "YnVmZmVyMTltaXJyb3IxOQ"),
    ("buffer19filter19", "YnVmZmVyMTlmaWx0ZXIxOQ"),
    ("buffer19ranking19", "YnVmZmVyMTlyYW5raW5nMTk"),
    ("buffer19encoding19", "YnVmZmVyMTllbmNvZGluZzE5"),
    ("queue19encoding19", "cXVldWUxOWVuY29kaW5nMTk"),
    ("queue19mapping19", "cXVldWUxOW1hcHBpbmcxOQ"),
    ("queue19record19", "cXVldWUxOXJlY29yZDE5"),
    ("queue19candle19", "cXVldWUxOWNhbmRsZTE5"),
    ("worker19candle19", "d29ya2VyMTljYW5kbGUxOQ"),
    ("worker19thread19", "d29ya2VyMTl0aHJlYWQxOQ"),
    ("worker19kitten19", "d29ya2VyMTlraXR0ZW4xOQ"),
    ("worker19sitting19", "d29ya2VyMTlzaXR0aW5nMTk"),
    ("kernel19sitting19", "a2VybmVsMTlzaXR0aW5nMTk"),
    ("kernel19agent19", "a2VybmVsMTlhZ2VudDE5"),
    ("kernel19angle19", "a2VybmVsMTlhbmdsZTE5"),
    ("kernel19universe19", "a2VybmVsMTl1bml2ZXJzZTE5"),
    ("signal19universe19", "c2lnbmFsMTl1bml2ZXJzZTE5"),
    ("signal19memory19", "c2lnbmFsMTltZW1vcnkxOQ"),
    ("signal19stream19", "c2lnbmFsMTlzdHJlYW0xOQ"),
    ("signal19context19", "c2lnbmFsMTljb250ZXh0MTk"),
    ("packet19context19", "cGFja2V0MTljb250ZXh0MTk"),
    ("packet19knowledge19", "cGFja2V0MTlrbm93bGVkZ2UxOQ"),
    ("packet19vector19", "cGFja2V0MTl2ZWN0b3IxOQ"),
    ("packet19processor19", "cGFja2V0MTlwcm9jZXNzb3IxOQ"),
    ("router19processor19", "cm91dGVyMTlwcm9jZXNzb3IxOQ"),
    ("router19reasoning19", "cm91dGVyMTlyZWFzb25pbmcxOQ"),
    ("router19machine19", "cm91dGVyMTltYWNoaW5lMTk"),
    ("router19learning19", "cm91dGVyMTlsZWFybmluZzE5"),
    ("cluster19learning19", "Y2x1c3RlcjE5bGVhcm5pbmcxOQ"),
    ("cluster19model19", "Y2x1c3RlcjE5bW9kZWwxOQ"),
    ("cluster19token19", "Y2x1c3RlcjE5dG9rZW4xOQ"),
    ("cluster19prompt19", "Y2x1c3RlcjE5cHJvbXB0MTk"),
    ("mirror19prompt19", "bWlycm9yMTlwcm9tcHQxOQ"),
    ("mirror19session19", "bWlycm9yMTlzZXNzaW9uMTk"),
    ("mirror19library19", "bWlycm9yMTlsaWJyYXJ5MTk"),
    ("mirror19service19", "bWlycm9yMTlzZXJ2aWNlMTk"),
    ("filter19service19", "ZmlsdGVyMTlzZXJ2aWNlMTk"),
    ("filter19gateway19", "ZmlsdGVyMTlnYXRld2F5MTk"),
    ("filter19storage19", "ZmlsdGVyMTlzdG9yYWdlMTk"),
    ("filter19network19", "ZmlsdGVyMTluZXR3b3JrMTk"),
    ("ranking19network19", "cmFua2luZzE5bmV0d29yazE5"),
    ("ranking19latency19", "cmFua2luZzE5bGF0ZW5jeTE5"),
    ("ranking19buffer19", "cmFua2luZzE5YnVmZmVyMTk"),
    ("ranking19queue19", "cmFua2luZzE5cXVldWUxOQ"),
    ("encoding19queue19", "ZW5jb2RpbmcxOXF1ZXVlMTk"),
    ("encoding19worker19", "ZW5jb2RpbmcxOXdvcmtlcjE5"),
    ("encoding19kernel19", "ZW5jb2RpbmcxOWtlcm5lbDE5"),
    ("encoding19signal19", "ZW5jb2RpbmcxOXNpZ25hbDE5"),
    ("mapping19signal19", "bWFwcGluZzE5c2lnbmFsMTk"),
    ("mapping19packet19", "bWFwcGluZzE5cGFja2V0MTk"),
    ("mapping19router19", "bWFwcGluZzE5cm91dGVyMTk"),
    ("mapping19cluster19", "bWFwcGluZzE5Y2x1c3RlcjE5"),
    ("record19cluster19", "cmVjb3JkMTljbHVzdGVyMTk"),
    ("record19mirror19", "cmVjb3JkMTltaXJyb3IxOQ"),
    ("record19filter19", "cmVjb3JkMTlmaWx0ZXIxOQ"),
    ("record19ranking19", "cmVjb3JkMTlyYW5raW5nMTk"),
    ("candle19ranking19", "Y2FuZGxlMTlyYW5raW5nMTk"),
    ("candle19encoding19", "Y2FuZGxlMTllbmNvZGluZzE5"),
    ("candle19mapping19", "Y2FuZGxlMTltYXBwaW5nMTk"),
    ("candle19record19", "Y2FuZGxlMTlyZWNvcmQxOQ"),
    ("thread19record19", "dGhyZWFkMTlyZWNvcmQxOQ"),
    ("thread19candle19", "dGhyZWFkMTljYW5kbGUxOQ"),
    ("thread19thread19", "dGhyZWFkMTl0aHJlYWQxOQ"),
    ("thread19kitten19", "dGhyZWFkMTlraXR0ZW4xOQ"),
    (
        "round 19: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTk6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 19: agentuniverse is a framework for multi agents",
        "cm91bmQgMTk6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 19: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTk6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 19: the processor reads the record then stops",
        "cm91bmQgMTk6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 19: a worker pulls the next task from the queue",
        "cm91bmQgMTk6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 19: signals travel through the network layer",
        "cm91bmQgMTk6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 19: the gateway routes each request by policy",
        "cm91bmQgMTk6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 19: memory grows until the buffer is full",
        "cm91bmQgMTk6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 19: the cluster mirrors every packet twice",
        "cm91bmQgMTk6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 19: ranking uses tokens learned from the corpus",
        "cm91bmQgMTk6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 19: a long session ends when the candle dies",
        "cm91bmQgMTk6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 19: encode the prompt then map the result",
        "cm91bmQgMTk6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 19: the kernel wakes the worker at dawn", "cm91bmQgMTk6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 19: service latency drops after the patch",
        "cm91bmQgMTk6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 19: the library caches every vector it sees",
        "cm91bmQgMTk6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 19: agents argue then the debate resolves",
        "cm91bmQgMTk6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 19: the filter keeps only strong matches",
        "cm91bmQgMTk6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 19: the model answers with a short reply",
        "cm91bmQgMTk6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 19: the recorder stores the reasoning trace",
        "cm91bmQgMTk6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 19: the angel watches the processor run", "cm91bmQgMTk6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 19: angle of the vector decides the match",
        "cm91bmQgMTk6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 19: the candle burns twice as long at night",
        "cm91bmQgMTk6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 19: a mirror of the universe in one line",
        "cm91bmQgMTk6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 19: the queue drains before the storm", "cm91bmQgMTk6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
