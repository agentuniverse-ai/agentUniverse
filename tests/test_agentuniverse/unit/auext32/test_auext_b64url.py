"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten32kitten32", "a2l0dGVuMzJraXR0ZW4zMg"),
    ("kitten32sitting32", "a2l0dGVuMzJzaXR0aW5nMzI"),
    ("kitten32agent32", "a2l0dGVuMzJhZ2VudDMy"),
    ("kitten32angle32", "a2l0dGVuMzJhbmdsZTMy"),
    ("sitting32angle32", "c2l0dGluZzMyYW5nbGUzMg"),
    ("sitting32universe32", "c2l0dGluZzMydW5pdmVyc2UzMg"),
    ("sitting32memory32", "c2l0dGluZzMybWVtb3J5MzI"),
    ("sitting32stream32", "c2l0dGluZzMyc3RyZWFtMzI"),
    ("agent32stream32", "YWdlbnQzMnN0cmVhbTMy"),
    ("agent32context32", "YWdlbnQzMmNvbnRleHQzMg"),
    ("agent32knowledge32", "YWdlbnQzMmtub3dsZWRnZTMy"),
    ("agent32vector32", "YWdlbnQzMnZlY3RvcjMy"),
    ("angle32vector32", "YW5nbGUzMnZlY3RvcjMy"),
    ("angle32processor32", "YW5nbGUzMnByb2Nlc3NvcjMy"),
    ("angle32reasoning32", "YW5nbGUzMnJlYXNvbmluZzMy"),
    ("angle32machine32", "YW5nbGUzMm1hY2hpbmUzMg"),
    ("universe32machine32", "dW5pdmVyc2UzMm1hY2hpbmUzMg"),
    ("universe32learning32", "dW5pdmVyc2UzMmxlYXJuaW5nMzI"),
    ("universe32model32", "dW5pdmVyc2UzMm1vZGVsMzI"),
    ("universe32token32", "dW5pdmVyc2UzMnRva2VuMzI"),
    ("memory32token32", "bWVtb3J5MzJ0b2tlbjMy"),
    ("memory32prompt32", "bWVtb3J5MzJwcm9tcHQzMg"),
    ("memory32session32", "bWVtb3J5MzJzZXNzaW9uMzI"),
    ("memory32library32", "bWVtb3J5MzJsaWJyYXJ5MzI"),
    ("stream32library32", "c3RyZWFtMzJsaWJyYXJ5MzI"),
    ("stream32service32", "c3RyZWFtMzJzZXJ2aWNlMzI"),
    ("stream32gateway32", "c3RyZWFtMzJnYXRld2F5MzI"),
    ("stream32storage32", "c3RyZWFtMzJzdG9yYWdlMzI"),
    ("context32storage32", "Y29udGV4dDMyc3RvcmFnZTMy"),
    ("context32network32", "Y29udGV4dDMybmV0d29yazMy"),
    ("context32latency32", "Y29udGV4dDMybGF0ZW5jeTMy"),
    ("context32buffer32", "Y29udGV4dDMyYnVmZmVyMzI"),
    ("knowledge32buffer32", "a25vd2xlZGdlMzJidWZmZXIzMg"),
    ("knowledge32queue32", "a25vd2xlZGdlMzJxdWV1ZTMy"),
    ("knowledge32worker32", "a25vd2xlZGdlMzJ3b3JrZXIzMg"),
    ("knowledge32kernel32", "a25vd2xlZGdlMzJrZXJuZWwzMg"),
    ("vector32kernel32", "dmVjdG9yMzJrZXJuZWwzMg"),
    ("vector32signal32", "dmVjdG9yMzJzaWduYWwzMg"),
    ("vector32packet32", "dmVjdG9yMzJwYWNrZXQzMg"),
    ("vector32router32", "dmVjdG9yMzJyb3V0ZXIzMg"),
    ("processor32router32", "cHJvY2Vzc29yMzJyb3V0ZXIzMg"),
    ("processor32cluster32", "cHJvY2Vzc29yMzJjbHVzdGVyMzI"),
    ("processor32mirror32", "cHJvY2Vzc29yMzJtaXJyb3IzMg"),
    ("processor32filter32", "cHJvY2Vzc29yMzJmaWx0ZXIzMg"),
    ("reasoning32filter32", "cmVhc29uaW5nMzJmaWx0ZXIzMg"),
    ("reasoning32ranking32", "cmVhc29uaW5nMzJyYW5raW5nMzI"),
    ("reasoning32encoding32", "cmVhc29uaW5nMzJlbmNvZGluZzMy"),
    ("reasoning32mapping32", "cmVhc29uaW5nMzJtYXBwaW5nMzI"),
    ("machine32mapping32", "bWFjaGluZTMybWFwcGluZzMy"),
    ("machine32record32", "bWFjaGluZTMycmVjb3JkMzI"),
    ("machine32candle32", "bWFjaGluZTMyY2FuZGxlMzI"),
    ("machine32thread32", "bWFjaGluZTMydGhyZWFkMzI"),
    ("learning32thread32", "bGVhcm5pbmczMnRocmVhZDMy"),
    ("learning32kitten32", "bGVhcm5pbmczMmtpdHRlbjMy"),
    ("learning32sitting32", "bGVhcm5pbmczMnNpdHRpbmczMg"),
    ("learning32agent32", "bGVhcm5pbmczMmFnZW50MzI"),
    ("model32agent32", "bW9kZWwzMmFnZW50MzI"),
    ("model32angle32", "bW9kZWwzMmFuZ2xlMzI"),
    ("model32universe32", "bW9kZWwzMnVuaXZlcnNlMzI"),
    ("model32memory32", "bW9kZWwzMm1lbW9yeTMy"),
    ("token32memory32", "dG9rZW4zMm1lbW9yeTMy"),
    ("token32stream32", "dG9rZW4zMnN0cmVhbTMy"),
    ("token32context32", "dG9rZW4zMmNvbnRleHQzMg"),
    ("token32knowledge32", "dG9rZW4zMmtub3dsZWRnZTMy"),
    ("prompt32knowledge32", "cHJvbXB0MzJrbm93bGVkZ2UzMg"),
    ("prompt32vector32", "cHJvbXB0MzJ2ZWN0b3IzMg"),
    ("prompt32processor32", "cHJvbXB0MzJwcm9jZXNzb3IzMg"),
    ("prompt32reasoning32", "cHJvbXB0MzJyZWFzb25pbmczMg"),
    ("session32reasoning32", "c2Vzc2lvbjMycmVhc29uaW5nMzI"),
    ("session32machine32", "c2Vzc2lvbjMybWFjaGluZTMy"),
    ("session32learning32", "c2Vzc2lvbjMybGVhcm5pbmczMg"),
    ("session32model32", "c2Vzc2lvbjMybW9kZWwzMg"),
    ("library32model32", "bGlicmFyeTMybW9kZWwzMg"),
    ("library32token32", "bGlicmFyeTMydG9rZW4zMg"),
    ("library32prompt32", "bGlicmFyeTMycHJvbXB0MzI"),
    ("library32session32", "bGlicmFyeTMyc2Vzc2lvbjMy"),
    ("service32session32", "c2VydmljZTMyc2Vzc2lvbjMy"),
    ("service32library32", "c2VydmljZTMybGlicmFyeTMy"),
    ("service32service32", "c2VydmljZTMyc2VydmljZTMy"),
    ("service32gateway32", "c2VydmljZTMyZ2F0ZXdheTMy"),
    ("gateway32gateway32", "Z2F0ZXdheTMyZ2F0ZXdheTMy"),
    ("gateway32storage32", "Z2F0ZXdheTMyc3RvcmFnZTMy"),
    ("gateway32network32", "Z2F0ZXdheTMybmV0d29yazMy"),
    ("gateway32latency32", "Z2F0ZXdheTMybGF0ZW5jeTMy"),
    ("storage32latency32", "c3RvcmFnZTMybGF0ZW5jeTMy"),
    ("storage32buffer32", "c3RvcmFnZTMyYnVmZmVyMzI"),
    ("storage32queue32", "c3RvcmFnZTMycXVldWUzMg"),
    ("storage32worker32", "c3RvcmFnZTMyd29ya2VyMzI"),
    ("network32worker32", "bmV0d29yazMyd29ya2VyMzI"),
    ("network32kernel32", "bmV0d29yazMya2VybmVsMzI"),
    ("network32signal32", "bmV0d29yazMyc2lnbmFsMzI"),
    ("network32packet32", "bmV0d29yazMycGFja2V0MzI"),
    ("latency32packet32", "bGF0ZW5jeTMycGFja2V0MzI"),
    ("latency32router32", "bGF0ZW5jeTMycm91dGVyMzI"),
    ("latency32cluster32", "bGF0ZW5jeTMyY2x1c3RlcjMy"),
    ("latency32mirror32", "bGF0ZW5jeTMybWlycm9yMzI"),
    ("buffer32mirror32", "YnVmZmVyMzJtaXJyb3IzMg"),
    ("buffer32filter32", "YnVmZmVyMzJmaWx0ZXIzMg"),
    ("buffer32ranking32", "YnVmZmVyMzJyYW5raW5nMzI"),
    ("buffer32encoding32", "YnVmZmVyMzJlbmNvZGluZzMy"),
    ("queue32encoding32", "cXVldWUzMmVuY29kaW5nMzI"),
    ("queue32mapping32", "cXVldWUzMm1hcHBpbmczMg"),
    ("queue32record32", "cXVldWUzMnJlY29yZDMy"),
    ("queue32candle32", "cXVldWUzMmNhbmRsZTMy"),
    ("worker32candle32", "d29ya2VyMzJjYW5kbGUzMg"),
    ("worker32thread32", "d29ya2VyMzJ0aHJlYWQzMg"),
    ("worker32kitten32", "d29ya2VyMzJraXR0ZW4zMg"),
    ("worker32sitting32", "d29ya2VyMzJzaXR0aW5nMzI"),
    ("kernel32sitting32", "a2VybmVsMzJzaXR0aW5nMzI"),
    ("kernel32agent32", "a2VybmVsMzJhZ2VudDMy"),
    ("kernel32angle32", "a2VybmVsMzJhbmdsZTMy"),
    ("kernel32universe32", "a2VybmVsMzJ1bml2ZXJzZTMy"),
    ("signal32universe32", "c2lnbmFsMzJ1bml2ZXJzZTMy"),
    ("signal32memory32", "c2lnbmFsMzJtZW1vcnkzMg"),
    ("signal32stream32", "c2lnbmFsMzJzdHJlYW0zMg"),
    ("signal32context32", "c2lnbmFsMzJjb250ZXh0MzI"),
    ("packet32context32", "cGFja2V0MzJjb250ZXh0MzI"),
    ("packet32knowledge32", "cGFja2V0MzJrbm93bGVkZ2UzMg"),
    ("packet32vector32", "cGFja2V0MzJ2ZWN0b3IzMg"),
    ("packet32processor32", "cGFja2V0MzJwcm9jZXNzb3IzMg"),
    ("router32processor32", "cm91dGVyMzJwcm9jZXNzb3IzMg"),
    ("router32reasoning32", "cm91dGVyMzJyZWFzb25pbmczMg"),
    ("router32machine32", "cm91dGVyMzJtYWNoaW5lMzI"),
    ("router32learning32", "cm91dGVyMzJsZWFybmluZzMy"),
    ("cluster32learning32", "Y2x1c3RlcjMybGVhcm5pbmczMg"),
    ("cluster32model32", "Y2x1c3RlcjMybW9kZWwzMg"),
    ("cluster32token32", "Y2x1c3RlcjMydG9rZW4zMg"),
    ("cluster32prompt32", "Y2x1c3RlcjMycHJvbXB0MzI"),
    ("mirror32prompt32", "bWlycm9yMzJwcm9tcHQzMg"),
    ("mirror32session32", "bWlycm9yMzJzZXNzaW9uMzI"),
    ("mirror32library32", "bWlycm9yMzJsaWJyYXJ5MzI"),
    ("mirror32service32", "bWlycm9yMzJzZXJ2aWNlMzI"),
    ("filter32service32", "ZmlsdGVyMzJzZXJ2aWNlMzI"),
    ("filter32gateway32", "ZmlsdGVyMzJnYXRld2F5MzI"),
    ("filter32storage32", "ZmlsdGVyMzJzdG9yYWdlMzI"),
    ("filter32network32", "ZmlsdGVyMzJuZXR3b3JrMzI"),
    ("ranking32network32", "cmFua2luZzMybmV0d29yazMy"),
    ("ranking32latency32", "cmFua2luZzMybGF0ZW5jeTMy"),
    ("ranking32buffer32", "cmFua2luZzMyYnVmZmVyMzI"),
    ("ranking32queue32", "cmFua2luZzMycXVldWUzMg"),
    ("encoding32queue32", "ZW5jb2RpbmczMnF1ZXVlMzI"),
    ("encoding32worker32", "ZW5jb2RpbmczMndvcmtlcjMy"),
    ("encoding32kernel32", "ZW5jb2RpbmczMmtlcm5lbDMy"),
    ("encoding32signal32", "ZW5jb2RpbmczMnNpZ25hbDMy"),
    ("mapping32signal32", "bWFwcGluZzMyc2lnbmFsMzI"),
    ("mapping32packet32", "bWFwcGluZzMycGFja2V0MzI"),
    ("mapping32router32", "bWFwcGluZzMycm91dGVyMzI"),
    ("mapping32cluster32", "bWFwcGluZzMyY2x1c3RlcjMy"),
    ("record32cluster32", "cmVjb3JkMzJjbHVzdGVyMzI"),
    ("record32mirror32", "cmVjb3JkMzJtaXJyb3IzMg"),
    ("record32filter32", "cmVjb3JkMzJmaWx0ZXIzMg"),
    ("record32ranking32", "cmVjb3JkMzJyYW5raW5nMzI"),
    ("candle32ranking32", "Y2FuZGxlMzJyYW5raW5nMzI"),
    ("candle32encoding32", "Y2FuZGxlMzJlbmNvZGluZzMy"),
    ("candle32mapping32", "Y2FuZGxlMzJtYXBwaW5nMzI"),
    ("candle32record32", "Y2FuZGxlMzJyZWNvcmQzMg"),
    ("thread32record32", "dGhyZWFkMzJyZWNvcmQzMg"),
    ("thread32candle32", "dGhyZWFkMzJjYW5kbGUzMg"),
    ("thread32thread32", "dGhyZWFkMzJ0aHJlYWQzMg"),
    ("thread32kitten32", "dGhyZWFkMzJraXR0ZW4zMg"),
    (
        "round 32: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMzI6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 32: agentuniverse is a framework for multi agents",
        "cm91bmQgMzI6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 32: knowledge stored as vectors enables retrieval",
        "cm91bmQgMzI6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 32: the processor reads the record then stops",
        "cm91bmQgMzI6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 32: a worker pulls the next task from the queue",
        "cm91bmQgMzI6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 32: signals travel through the network layer",
        "cm91bmQgMzI6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 32: the gateway routes each request by policy",
        "cm91bmQgMzI6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 32: memory grows until the buffer is full",
        "cm91bmQgMzI6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 32: the cluster mirrors every packet twice",
        "cm91bmQgMzI6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 32: ranking uses tokens learned from the corpus",
        "cm91bmQgMzI6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 32: a long session ends when the candle dies",
        "cm91bmQgMzI6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 32: encode the prompt then map the result",
        "cm91bmQgMzI6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 32: the kernel wakes the worker at dawn", "cm91bmQgMzI6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 32: service latency drops after the patch",
        "cm91bmQgMzI6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 32: the library caches every vector it sees",
        "cm91bmQgMzI6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 32: agents argue then the debate resolves",
        "cm91bmQgMzI6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 32: the filter keeps only strong matches",
        "cm91bmQgMzI6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 32: the model answers with a short reply",
        "cm91bmQgMzI6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 32: the recorder stores the reasoning trace",
        "cm91bmQgMzI6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 32: the angel watches the processor run", "cm91bmQgMzI6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 32: angle of the vector decides the match",
        "cm91bmQgMzI6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 32: the candle burns twice as long at night",
        "cm91bmQgMzI6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 32: a mirror of the universe in one line",
        "cm91bmQgMzI6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 32: the queue drains before the storm", "cm91bmQgMzI6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
