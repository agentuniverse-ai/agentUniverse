"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten18kitten18", "a2l0dGVuMThraXR0ZW4xOA"),
    ("kitten18sitting18", "a2l0dGVuMThzaXR0aW5nMTg"),
    ("kitten18agent18", "a2l0dGVuMThhZ2VudDE4"),
    ("kitten18angle18", "a2l0dGVuMThhbmdsZTE4"),
    ("sitting18angle18", "c2l0dGluZzE4YW5nbGUxOA"),
    ("sitting18universe18", "c2l0dGluZzE4dW5pdmVyc2UxOA"),
    ("sitting18memory18", "c2l0dGluZzE4bWVtb3J5MTg"),
    ("sitting18stream18", "c2l0dGluZzE4c3RyZWFtMTg"),
    ("agent18stream18", "YWdlbnQxOHN0cmVhbTE4"),
    ("agent18context18", "YWdlbnQxOGNvbnRleHQxOA"),
    ("agent18knowledge18", "YWdlbnQxOGtub3dsZWRnZTE4"),
    ("agent18vector18", "YWdlbnQxOHZlY3RvcjE4"),
    ("angle18vector18", "YW5nbGUxOHZlY3RvcjE4"),
    ("angle18processor18", "YW5nbGUxOHByb2Nlc3NvcjE4"),
    ("angle18reasoning18", "YW5nbGUxOHJlYXNvbmluZzE4"),
    ("angle18machine18", "YW5nbGUxOG1hY2hpbmUxOA"),
    ("universe18machine18", "dW5pdmVyc2UxOG1hY2hpbmUxOA"),
    ("universe18learning18", "dW5pdmVyc2UxOGxlYXJuaW5nMTg"),
    ("universe18model18", "dW5pdmVyc2UxOG1vZGVsMTg"),
    ("universe18token18", "dW5pdmVyc2UxOHRva2VuMTg"),
    ("memory18token18", "bWVtb3J5MTh0b2tlbjE4"),
    ("memory18prompt18", "bWVtb3J5MThwcm9tcHQxOA"),
    ("memory18session18", "bWVtb3J5MThzZXNzaW9uMTg"),
    ("memory18library18", "bWVtb3J5MThsaWJyYXJ5MTg"),
    ("stream18library18", "c3RyZWFtMThsaWJyYXJ5MTg"),
    ("stream18service18", "c3RyZWFtMThzZXJ2aWNlMTg"),
    ("stream18gateway18", "c3RyZWFtMThnYXRld2F5MTg"),
    ("stream18storage18", "c3RyZWFtMThzdG9yYWdlMTg"),
    ("context18storage18", "Y29udGV4dDE4c3RvcmFnZTE4"),
    ("context18network18", "Y29udGV4dDE4bmV0d29yazE4"),
    ("context18latency18", "Y29udGV4dDE4bGF0ZW5jeTE4"),
    ("context18buffer18", "Y29udGV4dDE4YnVmZmVyMTg"),
    ("knowledge18buffer18", "a25vd2xlZGdlMThidWZmZXIxOA"),
    ("knowledge18queue18", "a25vd2xlZGdlMThxdWV1ZTE4"),
    ("knowledge18worker18", "a25vd2xlZGdlMTh3b3JrZXIxOA"),
    ("knowledge18kernel18", "a25vd2xlZGdlMThrZXJuZWwxOA"),
    ("vector18kernel18", "dmVjdG9yMThrZXJuZWwxOA"),
    ("vector18signal18", "dmVjdG9yMThzaWduYWwxOA"),
    ("vector18packet18", "dmVjdG9yMThwYWNrZXQxOA"),
    ("vector18router18", "dmVjdG9yMThyb3V0ZXIxOA"),
    ("processor18router18", "cHJvY2Vzc29yMThyb3V0ZXIxOA"),
    ("processor18cluster18", "cHJvY2Vzc29yMThjbHVzdGVyMTg"),
    ("processor18mirror18", "cHJvY2Vzc29yMThtaXJyb3IxOA"),
    ("processor18filter18", "cHJvY2Vzc29yMThmaWx0ZXIxOA"),
    ("reasoning18filter18", "cmVhc29uaW5nMThmaWx0ZXIxOA"),
    ("reasoning18ranking18", "cmVhc29uaW5nMThyYW5raW5nMTg"),
    ("reasoning18encoding18", "cmVhc29uaW5nMThlbmNvZGluZzE4"),
    ("reasoning18mapping18", "cmVhc29uaW5nMThtYXBwaW5nMTg"),
    ("machine18mapping18", "bWFjaGluZTE4bWFwcGluZzE4"),
    ("machine18record18", "bWFjaGluZTE4cmVjb3JkMTg"),
    ("machine18candle18", "bWFjaGluZTE4Y2FuZGxlMTg"),
    ("machine18thread18", "bWFjaGluZTE4dGhyZWFkMTg"),
    ("learning18thread18", "bGVhcm5pbmcxOHRocmVhZDE4"),
    ("learning18kitten18", "bGVhcm5pbmcxOGtpdHRlbjE4"),
    ("learning18sitting18", "bGVhcm5pbmcxOHNpdHRpbmcxOA"),
    ("learning18agent18", "bGVhcm5pbmcxOGFnZW50MTg"),
    ("model18agent18", "bW9kZWwxOGFnZW50MTg"),
    ("model18angle18", "bW9kZWwxOGFuZ2xlMTg"),
    ("model18universe18", "bW9kZWwxOHVuaXZlcnNlMTg"),
    ("model18memory18", "bW9kZWwxOG1lbW9yeTE4"),
    ("token18memory18", "dG9rZW4xOG1lbW9yeTE4"),
    ("token18stream18", "dG9rZW4xOHN0cmVhbTE4"),
    ("token18context18", "dG9rZW4xOGNvbnRleHQxOA"),
    ("token18knowledge18", "dG9rZW4xOGtub3dsZWRnZTE4"),
    ("prompt18knowledge18", "cHJvbXB0MThrbm93bGVkZ2UxOA"),
    ("prompt18vector18", "cHJvbXB0MTh2ZWN0b3IxOA"),
    ("prompt18processor18", "cHJvbXB0MThwcm9jZXNzb3IxOA"),
    ("prompt18reasoning18", "cHJvbXB0MThyZWFzb25pbmcxOA"),
    ("session18reasoning18", "c2Vzc2lvbjE4cmVhc29uaW5nMTg"),
    ("session18machine18", "c2Vzc2lvbjE4bWFjaGluZTE4"),
    ("session18learning18", "c2Vzc2lvbjE4bGVhcm5pbmcxOA"),
    ("session18model18", "c2Vzc2lvbjE4bW9kZWwxOA"),
    ("library18model18", "bGlicmFyeTE4bW9kZWwxOA"),
    ("library18token18", "bGlicmFyeTE4dG9rZW4xOA"),
    ("library18prompt18", "bGlicmFyeTE4cHJvbXB0MTg"),
    ("library18session18", "bGlicmFyeTE4c2Vzc2lvbjE4"),
    ("service18session18", "c2VydmljZTE4c2Vzc2lvbjE4"),
    ("service18library18", "c2VydmljZTE4bGlicmFyeTE4"),
    ("service18service18", "c2VydmljZTE4c2VydmljZTE4"),
    ("service18gateway18", "c2VydmljZTE4Z2F0ZXdheTE4"),
    ("gateway18gateway18", "Z2F0ZXdheTE4Z2F0ZXdheTE4"),
    ("gateway18storage18", "Z2F0ZXdheTE4c3RvcmFnZTE4"),
    ("gateway18network18", "Z2F0ZXdheTE4bmV0d29yazE4"),
    ("gateway18latency18", "Z2F0ZXdheTE4bGF0ZW5jeTE4"),
    ("storage18latency18", "c3RvcmFnZTE4bGF0ZW5jeTE4"),
    ("storage18buffer18", "c3RvcmFnZTE4YnVmZmVyMTg"),
    ("storage18queue18", "c3RvcmFnZTE4cXVldWUxOA"),
    ("storage18worker18", "c3RvcmFnZTE4d29ya2VyMTg"),
    ("network18worker18", "bmV0d29yazE4d29ya2VyMTg"),
    ("network18kernel18", "bmV0d29yazE4a2VybmVsMTg"),
    ("network18signal18", "bmV0d29yazE4c2lnbmFsMTg"),
    ("network18packet18", "bmV0d29yazE4cGFja2V0MTg"),
    ("latency18packet18", "bGF0ZW5jeTE4cGFja2V0MTg"),
    ("latency18router18", "bGF0ZW5jeTE4cm91dGVyMTg"),
    ("latency18cluster18", "bGF0ZW5jeTE4Y2x1c3RlcjE4"),
    ("latency18mirror18", "bGF0ZW5jeTE4bWlycm9yMTg"),
    ("buffer18mirror18", "YnVmZmVyMThtaXJyb3IxOA"),
    ("buffer18filter18", "YnVmZmVyMThmaWx0ZXIxOA"),
    ("buffer18ranking18", "YnVmZmVyMThyYW5raW5nMTg"),
    ("buffer18encoding18", "YnVmZmVyMThlbmNvZGluZzE4"),
    ("queue18encoding18", "cXVldWUxOGVuY29kaW5nMTg"),
    ("queue18mapping18", "cXVldWUxOG1hcHBpbmcxOA"),
    ("queue18record18", "cXVldWUxOHJlY29yZDE4"),
    ("queue18candle18", "cXVldWUxOGNhbmRsZTE4"),
    ("worker18candle18", "d29ya2VyMThjYW5kbGUxOA"),
    ("worker18thread18", "d29ya2VyMTh0aHJlYWQxOA"),
    ("worker18kitten18", "d29ya2VyMThraXR0ZW4xOA"),
    ("worker18sitting18", "d29ya2VyMThzaXR0aW5nMTg"),
    ("kernel18sitting18", "a2VybmVsMThzaXR0aW5nMTg"),
    ("kernel18agent18", "a2VybmVsMThhZ2VudDE4"),
    ("kernel18angle18", "a2VybmVsMThhbmdsZTE4"),
    ("kernel18universe18", "a2VybmVsMTh1bml2ZXJzZTE4"),
    ("signal18universe18", "c2lnbmFsMTh1bml2ZXJzZTE4"),
    ("signal18memory18", "c2lnbmFsMThtZW1vcnkxOA"),
    ("signal18stream18", "c2lnbmFsMThzdHJlYW0xOA"),
    ("signal18context18", "c2lnbmFsMThjb250ZXh0MTg"),
    ("packet18context18", "cGFja2V0MThjb250ZXh0MTg"),
    ("packet18knowledge18", "cGFja2V0MThrbm93bGVkZ2UxOA"),
    ("packet18vector18", "cGFja2V0MTh2ZWN0b3IxOA"),
    ("packet18processor18", "cGFja2V0MThwcm9jZXNzb3IxOA"),
    ("router18processor18", "cm91dGVyMThwcm9jZXNzb3IxOA"),
    ("router18reasoning18", "cm91dGVyMThyZWFzb25pbmcxOA"),
    ("router18machine18", "cm91dGVyMThtYWNoaW5lMTg"),
    ("router18learning18", "cm91dGVyMThsZWFybmluZzE4"),
    ("cluster18learning18", "Y2x1c3RlcjE4bGVhcm5pbmcxOA"),
    ("cluster18model18", "Y2x1c3RlcjE4bW9kZWwxOA"),
    ("cluster18token18", "Y2x1c3RlcjE4dG9rZW4xOA"),
    ("cluster18prompt18", "Y2x1c3RlcjE4cHJvbXB0MTg"),
    ("mirror18prompt18", "bWlycm9yMThwcm9tcHQxOA"),
    ("mirror18session18", "bWlycm9yMThzZXNzaW9uMTg"),
    ("mirror18library18", "bWlycm9yMThsaWJyYXJ5MTg"),
    ("mirror18service18", "bWlycm9yMThzZXJ2aWNlMTg"),
    ("filter18service18", "ZmlsdGVyMThzZXJ2aWNlMTg"),
    ("filter18gateway18", "ZmlsdGVyMThnYXRld2F5MTg"),
    ("filter18storage18", "ZmlsdGVyMThzdG9yYWdlMTg"),
    ("filter18network18", "ZmlsdGVyMThuZXR3b3JrMTg"),
    ("ranking18network18", "cmFua2luZzE4bmV0d29yazE4"),
    ("ranking18latency18", "cmFua2luZzE4bGF0ZW5jeTE4"),
    ("ranking18buffer18", "cmFua2luZzE4YnVmZmVyMTg"),
    ("ranking18queue18", "cmFua2luZzE4cXVldWUxOA"),
    ("encoding18queue18", "ZW5jb2RpbmcxOHF1ZXVlMTg"),
    ("encoding18worker18", "ZW5jb2RpbmcxOHdvcmtlcjE4"),
    ("encoding18kernel18", "ZW5jb2RpbmcxOGtlcm5lbDE4"),
    ("encoding18signal18", "ZW5jb2RpbmcxOHNpZ25hbDE4"),
    ("mapping18signal18", "bWFwcGluZzE4c2lnbmFsMTg"),
    ("mapping18packet18", "bWFwcGluZzE4cGFja2V0MTg"),
    ("mapping18router18", "bWFwcGluZzE4cm91dGVyMTg"),
    ("mapping18cluster18", "bWFwcGluZzE4Y2x1c3RlcjE4"),
    ("record18cluster18", "cmVjb3JkMThjbHVzdGVyMTg"),
    ("record18mirror18", "cmVjb3JkMThtaXJyb3IxOA"),
    ("record18filter18", "cmVjb3JkMThmaWx0ZXIxOA"),
    ("record18ranking18", "cmVjb3JkMThyYW5raW5nMTg"),
    ("candle18ranking18", "Y2FuZGxlMThyYW5raW5nMTg"),
    ("candle18encoding18", "Y2FuZGxlMThlbmNvZGluZzE4"),
    ("candle18mapping18", "Y2FuZGxlMThtYXBwaW5nMTg"),
    ("candle18record18", "Y2FuZGxlMThyZWNvcmQxOA"),
    ("thread18record18", "dGhyZWFkMThyZWNvcmQxOA"),
    ("thread18candle18", "dGhyZWFkMThjYW5kbGUxOA"),
    ("thread18thread18", "dGhyZWFkMTh0aHJlYWQxOA"),
    ("thread18kitten18", "dGhyZWFkMThraXR0ZW4xOA"),
    (
        "round 18: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTg6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 18: agentuniverse is a framework for multi agents",
        "cm91bmQgMTg6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 18: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTg6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 18: the processor reads the record then stops",
        "cm91bmQgMTg6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 18: a worker pulls the next task from the queue",
        "cm91bmQgMTg6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 18: signals travel through the network layer",
        "cm91bmQgMTg6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 18: the gateway routes each request by policy",
        "cm91bmQgMTg6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 18: memory grows until the buffer is full",
        "cm91bmQgMTg6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 18: the cluster mirrors every packet twice",
        "cm91bmQgMTg6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 18: ranking uses tokens learned from the corpus",
        "cm91bmQgMTg6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 18: a long session ends when the candle dies",
        "cm91bmQgMTg6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 18: encode the prompt then map the result",
        "cm91bmQgMTg6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 18: the kernel wakes the worker at dawn", "cm91bmQgMTg6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 18: service latency drops after the patch",
        "cm91bmQgMTg6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 18: the library caches every vector it sees",
        "cm91bmQgMTg6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 18: agents argue then the debate resolves",
        "cm91bmQgMTg6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 18: the filter keeps only strong matches",
        "cm91bmQgMTg6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 18: the model answers with a short reply",
        "cm91bmQgMTg6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 18: the recorder stores the reasoning trace",
        "cm91bmQgMTg6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 18: the angel watches the processor run", "cm91bmQgMTg6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 18: angle of the vector decides the match",
        "cm91bmQgMTg6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 18: the candle burns twice as long at night",
        "cm91bmQgMTg6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 18: a mirror of the universe in one line",
        "cm91bmQgMTg6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 18: the queue drains before the storm", "cm91bmQgMTg6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
