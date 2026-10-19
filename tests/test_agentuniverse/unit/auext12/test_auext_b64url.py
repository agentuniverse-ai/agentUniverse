"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten12kitten12", "a2l0dGVuMTJraXR0ZW4xMg"),
    ("kitten12sitting12", "a2l0dGVuMTJzaXR0aW5nMTI"),
    ("kitten12agent12", "a2l0dGVuMTJhZ2VudDEy"),
    ("kitten12angle12", "a2l0dGVuMTJhbmdsZTEy"),
    ("sitting12angle12", "c2l0dGluZzEyYW5nbGUxMg"),
    ("sitting12universe12", "c2l0dGluZzEydW5pdmVyc2UxMg"),
    ("sitting12memory12", "c2l0dGluZzEybWVtb3J5MTI"),
    ("sitting12stream12", "c2l0dGluZzEyc3RyZWFtMTI"),
    ("agent12stream12", "YWdlbnQxMnN0cmVhbTEy"),
    ("agent12context12", "YWdlbnQxMmNvbnRleHQxMg"),
    ("agent12knowledge12", "YWdlbnQxMmtub3dsZWRnZTEy"),
    ("agent12vector12", "YWdlbnQxMnZlY3RvcjEy"),
    ("angle12vector12", "YW5nbGUxMnZlY3RvcjEy"),
    ("angle12processor12", "YW5nbGUxMnByb2Nlc3NvcjEy"),
    ("angle12reasoning12", "YW5nbGUxMnJlYXNvbmluZzEy"),
    ("angle12machine12", "YW5nbGUxMm1hY2hpbmUxMg"),
    ("universe12machine12", "dW5pdmVyc2UxMm1hY2hpbmUxMg"),
    ("universe12learning12", "dW5pdmVyc2UxMmxlYXJuaW5nMTI"),
    ("universe12model12", "dW5pdmVyc2UxMm1vZGVsMTI"),
    ("universe12token12", "dW5pdmVyc2UxMnRva2VuMTI"),
    ("memory12token12", "bWVtb3J5MTJ0b2tlbjEy"),
    ("memory12prompt12", "bWVtb3J5MTJwcm9tcHQxMg"),
    ("memory12session12", "bWVtb3J5MTJzZXNzaW9uMTI"),
    ("memory12library12", "bWVtb3J5MTJsaWJyYXJ5MTI"),
    ("stream12library12", "c3RyZWFtMTJsaWJyYXJ5MTI"),
    ("stream12service12", "c3RyZWFtMTJzZXJ2aWNlMTI"),
    ("stream12gateway12", "c3RyZWFtMTJnYXRld2F5MTI"),
    ("stream12storage12", "c3RyZWFtMTJzdG9yYWdlMTI"),
    ("context12storage12", "Y29udGV4dDEyc3RvcmFnZTEy"),
    ("context12network12", "Y29udGV4dDEybmV0d29yazEy"),
    ("context12latency12", "Y29udGV4dDEybGF0ZW5jeTEy"),
    ("context12buffer12", "Y29udGV4dDEyYnVmZmVyMTI"),
    ("knowledge12buffer12", "a25vd2xlZGdlMTJidWZmZXIxMg"),
    ("knowledge12queue12", "a25vd2xlZGdlMTJxdWV1ZTEy"),
    ("knowledge12worker12", "a25vd2xlZGdlMTJ3b3JrZXIxMg"),
    ("knowledge12kernel12", "a25vd2xlZGdlMTJrZXJuZWwxMg"),
    ("vector12kernel12", "dmVjdG9yMTJrZXJuZWwxMg"),
    ("vector12signal12", "dmVjdG9yMTJzaWduYWwxMg"),
    ("vector12packet12", "dmVjdG9yMTJwYWNrZXQxMg"),
    ("vector12router12", "dmVjdG9yMTJyb3V0ZXIxMg"),
    ("processor12router12", "cHJvY2Vzc29yMTJyb3V0ZXIxMg"),
    ("processor12cluster12", "cHJvY2Vzc29yMTJjbHVzdGVyMTI"),
    ("processor12mirror12", "cHJvY2Vzc29yMTJtaXJyb3IxMg"),
    ("processor12filter12", "cHJvY2Vzc29yMTJmaWx0ZXIxMg"),
    ("reasoning12filter12", "cmVhc29uaW5nMTJmaWx0ZXIxMg"),
    ("reasoning12ranking12", "cmVhc29uaW5nMTJyYW5raW5nMTI"),
    ("reasoning12encoding12", "cmVhc29uaW5nMTJlbmNvZGluZzEy"),
    ("reasoning12mapping12", "cmVhc29uaW5nMTJtYXBwaW5nMTI"),
    ("machine12mapping12", "bWFjaGluZTEybWFwcGluZzEy"),
    ("machine12record12", "bWFjaGluZTEycmVjb3JkMTI"),
    ("machine12candle12", "bWFjaGluZTEyY2FuZGxlMTI"),
    ("machine12thread12", "bWFjaGluZTEydGhyZWFkMTI"),
    ("learning12thread12", "bGVhcm5pbmcxMnRocmVhZDEy"),
    ("learning12kitten12", "bGVhcm5pbmcxMmtpdHRlbjEy"),
    ("learning12sitting12", "bGVhcm5pbmcxMnNpdHRpbmcxMg"),
    ("learning12agent12", "bGVhcm5pbmcxMmFnZW50MTI"),
    ("model12agent12", "bW9kZWwxMmFnZW50MTI"),
    ("model12angle12", "bW9kZWwxMmFuZ2xlMTI"),
    ("model12universe12", "bW9kZWwxMnVuaXZlcnNlMTI"),
    ("model12memory12", "bW9kZWwxMm1lbW9yeTEy"),
    ("token12memory12", "dG9rZW4xMm1lbW9yeTEy"),
    ("token12stream12", "dG9rZW4xMnN0cmVhbTEy"),
    ("token12context12", "dG9rZW4xMmNvbnRleHQxMg"),
    ("token12knowledge12", "dG9rZW4xMmtub3dsZWRnZTEy"),
    ("prompt12knowledge12", "cHJvbXB0MTJrbm93bGVkZ2UxMg"),
    ("prompt12vector12", "cHJvbXB0MTJ2ZWN0b3IxMg"),
    ("prompt12processor12", "cHJvbXB0MTJwcm9jZXNzb3IxMg"),
    ("prompt12reasoning12", "cHJvbXB0MTJyZWFzb25pbmcxMg"),
    ("session12reasoning12", "c2Vzc2lvbjEycmVhc29uaW5nMTI"),
    ("session12machine12", "c2Vzc2lvbjEybWFjaGluZTEy"),
    ("session12learning12", "c2Vzc2lvbjEybGVhcm5pbmcxMg"),
    ("session12model12", "c2Vzc2lvbjEybW9kZWwxMg"),
    ("library12model12", "bGlicmFyeTEybW9kZWwxMg"),
    ("library12token12", "bGlicmFyeTEydG9rZW4xMg"),
    ("library12prompt12", "bGlicmFyeTEycHJvbXB0MTI"),
    ("library12session12", "bGlicmFyeTEyc2Vzc2lvbjEy"),
    ("service12session12", "c2VydmljZTEyc2Vzc2lvbjEy"),
    ("service12library12", "c2VydmljZTEybGlicmFyeTEy"),
    ("service12service12", "c2VydmljZTEyc2VydmljZTEy"),
    ("service12gateway12", "c2VydmljZTEyZ2F0ZXdheTEy"),
    ("gateway12gateway12", "Z2F0ZXdheTEyZ2F0ZXdheTEy"),
    ("gateway12storage12", "Z2F0ZXdheTEyc3RvcmFnZTEy"),
    ("gateway12network12", "Z2F0ZXdheTEybmV0d29yazEy"),
    ("gateway12latency12", "Z2F0ZXdheTEybGF0ZW5jeTEy"),
    ("storage12latency12", "c3RvcmFnZTEybGF0ZW5jeTEy"),
    ("storage12buffer12", "c3RvcmFnZTEyYnVmZmVyMTI"),
    ("storage12queue12", "c3RvcmFnZTEycXVldWUxMg"),
    ("storage12worker12", "c3RvcmFnZTEyd29ya2VyMTI"),
    ("network12worker12", "bmV0d29yazEyd29ya2VyMTI"),
    ("network12kernel12", "bmV0d29yazEya2VybmVsMTI"),
    ("network12signal12", "bmV0d29yazEyc2lnbmFsMTI"),
    ("network12packet12", "bmV0d29yazEycGFja2V0MTI"),
    ("latency12packet12", "bGF0ZW5jeTEycGFja2V0MTI"),
    ("latency12router12", "bGF0ZW5jeTEycm91dGVyMTI"),
    ("latency12cluster12", "bGF0ZW5jeTEyY2x1c3RlcjEy"),
    ("latency12mirror12", "bGF0ZW5jeTEybWlycm9yMTI"),
    ("buffer12mirror12", "YnVmZmVyMTJtaXJyb3IxMg"),
    ("buffer12filter12", "YnVmZmVyMTJmaWx0ZXIxMg"),
    ("buffer12ranking12", "YnVmZmVyMTJyYW5raW5nMTI"),
    ("buffer12encoding12", "YnVmZmVyMTJlbmNvZGluZzEy"),
    ("queue12encoding12", "cXVldWUxMmVuY29kaW5nMTI"),
    ("queue12mapping12", "cXVldWUxMm1hcHBpbmcxMg"),
    ("queue12record12", "cXVldWUxMnJlY29yZDEy"),
    ("queue12candle12", "cXVldWUxMmNhbmRsZTEy"),
    ("worker12candle12", "d29ya2VyMTJjYW5kbGUxMg"),
    ("worker12thread12", "d29ya2VyMTJ0aHJlYWQxMg"),
    ("worker12kitten12", "d29ya2VyMTJraXR0ZW4xMg"),
    ("worker12sitting12", "d29ya2VyMTJzaXR0aW5nMTI"),
    ("kernel12sitting12", "a2VybmVsMTJzaXR0aW5nMTI"),
    ("kernel12agent12", "a2VybmVsMTJhZ2VudDEy"),
    ("kernel12angle12", "a2VybmVsMTJhbmdsZTEy"),
    ("kernel12universe12", "a2VybmVsMTJ1bml2ZXJzZTEy"),
    ("signal12universe12", "c2lnbmFsMTJ1bml2ZXJzZTEy"),
    ("signal12memory12", "c2lnbmFsMTJtZW1vcnkxMg"),
    ("signal12stream12", "c2lnbmFsMTJzdHJlYW0xMg"),
    ("signal12context12", "c2lnbmFsMTJjb250ZXh0MTI"),
    ("packet12context12", "cGFja2V0MTJjb250ZXh0MTI"),
    ("packet12knowledge12", "cGFja2V0MTJrbm93bGVkZ2UxMg"),
    ("packet12vector12", "cGFja2V0MTJ2ZWN0b3IxMg"),
    ("packet12processor12", "cGFja2V0MTJwcm9jZXNzb3IxMg"),
    ("router12processor12", "cm91dGVyMTJwcm9jZXNzb3IxMg"),
    ("router12reasoning12", "cm91dGVyMTJyZWFzb25pbmcxMg"),
    ("router12machine12", "cm91dGVyMTJtYWNoaW5lMTI"),
    ("router12learning12", "cm91dGVyMTJsZWFybmluZzEy"),
    ("cluster12learning12", "Y2x1c3RlcjEybGVhcm5pbmcxMg"),
    ("cluster12model12", "Y2x1c3RlcjEybW9kZWwxMg"),
    ("cluster12token12", "Y2x1c3RlcjEydG9rZW4xMg"),
    ("cluster12prompt12", "Y2x1c3RlcjEycHJvbXB0MTI"),
    ("mirror12prompt12", "bWlycm9yMTJwcm9tcHQxMg"),
    ("mirror12session12", "bWlycm9yMTJzZXNzaW9uMTI"),
    ("mirror12library12", "bWlycm9yMTJsaWJyYXJ5MTI"),
    ("mirror12service12", "bWlycm9yMTJzZXJ2aWNlMTI"),
    ("filter12service12", "ZmlsdGVyMTJzZXJ2aWNlMTI"),
    ("filter12gateway12", "ZmlsdGVyMTJnYXRld2F5MTI"),
    ("filter12storage12", "ZmlsdGVyMTJzdG9yYWdlMTI"),
    ("filter12network12", "ZmlsdGVyMTJuZXR3b3JrMTI"),
    ("ranking12network12", "cmFua2luZzEybmV0d29yazEy"),
    ("ranking12latency12", "cmFua2luZzEybGF0ZW5jeTEy"),
    ("ranking12buffer12", "cmFua2luZzEyYnVmZmVyMTI"),
    ("ranking12queue12", "cmFua2luZzEycXVldWUxMg"),
    ("encoding12queue12", "ZW5jb2RpbmcxMnF1ZXVlMTI"),
    ("encoding12worker12", "ZW5jb2RpbmcxMndvcmtlcjEy"),
    ("encoding12kernel12", "ZW5jb2RpbmcxMmtlcm5lbDEy"),
    ("encoding12signal12", "ZW5jb2RpbmcxMnNpZ25hbDEy"),
    ("mapping12signal12", "bWFwcGluZzEyc2lnbmFsMTI"),
    ("mapping12packet12", "bWFwcGluZzEycGFja2V0MTI"),
    ("mapping12router12", "bWFwcGluZzEycm91dGVyMTI"),
    ("mapping12cluster12", "bWFwcGluZzEyY2x1c3RlcjEy"),
    ("record12cluster12", "cmVjb3JkMTJjbHVzdGVyMTI"),
    ("record12mirror12", "cmVjb3JkMTJtaXJyb3IxMg"),
    ("record12filter12", "cmVjb3JkMTJmaWx0ZXIxMg"),
    ("record12ranking12", "cmVjb3JkMTJyYW5raW5nMTI"),
    ("candle12ranking12", "Y2FuZGxlMTJyYW5raW5nMTI"),
    ("candle12encoding12", "Y2FuZGxlMTJlbmNvZGluZzEy"),
    ("candle12mapping12", "Y2FuZGxlMTJtYXBwaW5nMTI"),
    ("candle12record12", "Y2FuZGxlMTJyZWNvcmQxMg"),
    ("thread12record12", "dGhyZWFkMTJyZWNvcmQxMg"),
    ("thread12candle12", "dGhyZWFkMTJjYW5kbGUxMg"),
    ("thread12thread12", "dGhyZWFkMTJ0aHJlYWQxMg"),
    ("thread12kitten12", "dGhyZWFkMTJraXR0ZW4xMg"),
    (
        "round 12: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTI6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 12: agentuniverse is a framework for multi agents",
        "cm91bmQgMTI6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 12: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTI6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 12: the processor reads the record then stops",
        "cm91bmQgMTI6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 12: a worker pulls the next task from the queue",
        "cm91bmQgMTI6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 12: signals travel through the network layer",
        "cm91bmQgMTI6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 12: the gateway routes each request by policy",
        "cm91bmQgMTI6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 12: memory grows until the buffer is full",
        "cm91bmQgMTI6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 12: the cluster mirrors every packet twice",
        "cm91bmQgMTI6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 12: ranking uses tokens learned from the corpus",
        "cm91bmQgMTI6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 12: a long session ends when the candle dies",
        "cm91bmQgMTI6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 12: encode the prompt then map the result",
        "cm91bmQgMTI6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 12: the kernel wakes the worker at dawn", "cm91bmQgMTI6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 12: service latency drops after the patch",
        "cm91bmQgMTI6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 12: the library caches every vector it sees",
        "cm91bmQgMTI6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 12: agents argue then the debate resolves",
        "cm91bmQgMTI6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 12: the filter keeps only strong matches",
        "cm91bmQgMTI6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 12: the model answers with a short reply",
        "cm91bmQgMTI6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 12: the recorder stores the reasoning trace",
        "cm91bmQgMTI6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 12: the angel watches the processor run", "cm91bmQgMTI6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 12: angle of the vector decides the match",
        "cm91bmQgMTI6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 12: the candle burns twice as long at night",
        "cm91bmQgMTI6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 12: a mirror of the universe in one line",
        "cm91bmQgMTI6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 12: the queue drains before the storm", "cm91bmQgMTI6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
