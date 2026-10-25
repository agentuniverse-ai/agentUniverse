"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten11kitten11", "a2l0dGVuMTFraXR0ZW4xMQ"),
    ("kitten11sitting11", "a2l0dGVuMTFzaXR0aW5nMTE"),
    ("kitten11agent11", "a2l0dGVuMTFhZ2VudDEx"),
    ("kitten11angle11", "a2l0dGVuMTFhbmdsZTEx"),
    ("sitting11angle11", "c2l0dGluZzExYW5nbGUxMQ"),
    ("sitting11universe11", "c2l0dGluZzExdW5pdmVyc2UxMQ"),
    ("sitting11memory11", "c2l0dGluZzExbWVtb3J5MTE"),
    ("sitting11stream11", "c2l0dGluZzExc3RyZWFtMTE"),
    ("agent11stream11", "YWdlbnQxMXN0cmVhbTEx"),
    ("agent11context11", "YWdlbnQxMWNvbnRleHQxMQ"),
    ("agent11knowledge11", "YWdlbnQxMWtub3dsZWRnZTEx"),
    ("agent11vector11", "YWdlbnQxMXZlY3RvcjEx"),
    ("angle11vector11", "YW5nbGUxMXZlY3RvcjEx"),
    ("angle11processor11", "YW5nbGUxMXByb2Nlc3NvcjEx"),
    ("angle11reasoning11", "YW5nbGUxMXJlYXNvbmluZzEx"),
    ("angle11machine11", "YW5nbGUxMW1hY2hpbmUxMQ"),
    ("universe11machine11", "dW5pdmVyc2UxMW1hY2hpbmUxMQ"),
    ("universe11learning11", "dW5pdmVyc2UxMWxlYXJuaW5nMTE"),
    ("universe11model11", "dW5pdmVyc2UxMW1vZGVsMTE"),
    ("universe11token11", "dW5pdmVyc2UxMXRva2VuMTE"),
    ("memory11token11", "bWVtb3J5MTF0b2tlbjEx"),
    ("memory11prompt11", "bWVtb3J5MTFwcm9tcHQxMQ"),
    ("memory11session11", "bWVtb3J5MTFzZXNzaW9uMTE"),
    ("memory11library11", "bWVtb3J5MTFsaWJyYXJ5MTE"),
    ("stream11library11", "c3RyZWFtMTFsaWJyYXJ5MTE"),
    ("stream11service11", "c3RyZWFtMTFzZXJ2aWNlMTE"),
    ("stream11gateway11", "c3RyZWFtMTFnYXRld2F5MTE"),
    ("stream11storage11", "c3RyZWFtMTFzdG9yYWdlMTE"),
    ("context11storage11", "Y29udGV4dDExc3RvcmFnZTEx"),
    ("context11network11", "Y29udGV4dDExbmV0d29yazEx"),
    ("context11latency11", "Y29udGV4dDExbGF0ZW5jeTEx"),
    ("context11buffer11", "Y29udGV4dDExYnVmZmVyMTE"),
    ("knowledge11buffer11", "a25vd2xlZGdlMTFidWZmZXIxMQ"),
    ("knowledge11queue11", "a25vd2xlZGdlMTFxdWV1ZTEx"),
    ("knowledge11worker11", "a25vd2xlZGdlMTF3b3JrZXIxMQ"),
    ("knowledge11kernel11", "a25vd2xlZGdlMTFrZXJuZWwxMQ"),
    ("vector11kernel11", "dmVjdG9yMTFrZXJuZWwxMQ"),
    ("vector11signal11", "dmVjdG9yMTFzaWduYWwxMQ"),
    ("vector11packet11", "dmVjdG9yMTFwYWNrZXQxMQ"),
    ("vector11router11", "dmVjdG9yMTFyb3V0ZXIxMQ"),
    ("processor11router11", "cHJvY2Vzc29yMTFyb3V0ZXIxMQ"),
    ("processor11cluster11", "cHJvY2Vzc29yMTFjbHVzdGVyMTE"),
    ("processor11mirror11", "cHJvY2Vzc29yMTFtaXJyb3IxMQ"),
    ("processor11filter11", "cHJvY2Vzc29yMTFmaWx0ZXIxMQ"),
    ("reasoning11filter11", "cmVhc29uaW5nMTFmaWx0ZXIxMQ"),
    ("reasoning11ranking11", "cmVhc29uaW5nMTFyYW5raW5nMTE"),
    ("reasoning11encoding11", "cmVhc29uaW5nMTFlbmNvZGluZzEx"),
    ("reasoning11mapping11", "cmVhc29uaW5nMTFtYXBwaW5nMTE"),
    ("machine11mapping11", "bWFjaGluZTExbWFwcGluZzEx"),
    ("machine11record11", "bWFjaGluZTExcmVjb3JkMTE"),
    ("machine11candle11", "bWFjaGluZTExY2FuZGxlMTE"),
    ("machine11thread11", "bWFjaGluZTExdGhyZWFkMTE"),
    ("learning11thread11", "bGVhcm5pbmcxMXRocmVhZDEx"),
    ("learning11kitten11", "bGVhcm5pbmcxMWtpdHRlbjEx"),
    ("learning11sitting11", "bGVhcm5pbmcxMXNpdHRpbmcxMQ"),
    ("learning11agent11", "bGVhcm5pbmcxMWFnZW50MTE"),
    ("model11agent11", "bW9kZWwxMWFnZW50MTE"),
    ("model11angle11", "bW9kZWwxMWFuZ2xlMTE"),
    ("model11universe11", "bW9kZWwxMXVuaXZlcnNlMTE"),
    ("model11memory11", "bW9kZWwxMW1lbW9yeTEx"),
    ("token11memory11", "dG9rZW4xMW1lbW9yeTEx"),
    ("token11stream11", "dG9rZW4xMXN0cmVhbTEx"),
    ("token11context11", "dG9rZW4xMWNvbnRleHQxMQ"),
    ("token11knowledge11", "dG9rZW4xMWtub3dsZWRnZTEx"),
    ("prompt11knowledge11", "cHJvbXB0MTFrbm93bGVkZ2UxMQ"),
    ("prompt11vector11", "cHJvbXB0MTF2ZWN0b3IxMQ"),
    ("prompt11processor11", "cHJvbXB0MTFwcm9jZXNzb3IxMQ"),
    ("prompt11reasoning11", "cHJvbXB0MTFyZWFzb25pbmcxMQ"),
    ("session11reasoning11", "c2Vzc2lvbjExcmVhc29uaW5nMTE"),
    ("session11machine11", "c2Vzc2lvbjExbWFjaGluZTEx"),
    ("session11learning11", "c2Vzc2lvbjExbGVhcm5pbmcxMQ"),
    ("session11model11", "c2Vzc2lvbjExbW9kZWwxMQ"),
    ("library11model11", "bGlicmFyeTExbW9kZWwxMQ"),
    ("library11token11", "bGlicmFyeTExdG9rZW4xMQ"),
    ("library11prompt11", "bGlicmFyeTExcHJvbXB0MTE"),
    ("library11session11", "bGlicmFyeTExc2Vzc2lvbjEx"),
    ("service11session11", "c2VydmljZTExc2Vzc2lvbjEx"),
    ("service11library11", "c2VydmljZTExbGlicmFyeTEx"),
    ("service11service11", "c2VydmljZTExc2VydmljZTEx"),
    ("service11gateway11", "c2VydmljZTExZ2F0ZXdheTEx"),
    ("gateway11gateway11", "Z2F0ZXdheTExZ2F0ZXdheTEx"),
    ("gateway11storage11", "Z2F0ZXdheTExc3RvcmFnZTEx"),
    ("gateway11network11", "Z2F0ZXdheTExbmV0d29yazEx"),
    ("gateway11latency11", "Z2F0ZXdheTExbGF0ZW5jeTEx"),
    ("storage11latency11", "c3RvcmFnZTExbGF0ZW5jeTEx"),
    ("storage11buffer11", "c3RvcmFnZTExYnVmZmVyMTE"),
    ("storage11queue11", "c3RvcmFnZTExcXVldWUxMQ"),
    ("storage11worker11", "c3RvcmFnZTExd29ya2VyMTE"),
    ("network11worker11", "bmV0d29yazExd29ya2VyMTE"),
    ("network11kernel11", "bmV0d29yazExa2VybmVsMTE"),
    ("network11signal11", "bmV0d29yazExc2lnbmFsMTE"),
    ("network11packet11", "bmV0d29yazExcGFja2V0MTE"),
    ("latency11packet11", "bGF0ZW5jeTExcGFja2V0MTE"),
    ("latency11router11", "bGF0ZW5jeTExcm91dGVyMTE"),
    ("latency11cluster11", "bGF0ZW5jeTExY2x1c3RlcjEx"),
    ("latency11mirror11", "bGF0ZW5jeTExbWlycm9yMTE"),
    ("buffer11mirror11", "YnVmZmVyMTFtaXJyb3IxMQ"),
    ("buffer11filter11", "YnVmZmVyMTFmaWx0ZXIxMQ"),
    ("buffer11ranking11", "YnVmZmVyMTFyYW5raW5nMTE"),
    ("buffer11encoding11", "YnVmZmVyMTFlbmNvZGluZzEx"),
    ("queue11encoding11", "cXVldWUxMWVuY29kaW5nMTE"),
    ("queue11mapping11", "cXVldWUxMW1hcHBpbmcxMQ"),
    ("queue11record11", "cXVldWUxMXJlY29yZDEx"),
    ("queue11candle11", "cXVldWUxMWNhbmRsZTEx"),
    ("worker11candle11", "d29ya2VyMTFjYW5kbGUxMQ"),
    ("worker11thread11", "d29ya2VyMTF0aHJlYWQxMQ"),
    ("worker11kitten11", "d29ya2VyMTFraXR0ZW4xMQ"),
    ("worker11sitting11", "d29ya2VyMTFzaXR0aW5nMTE"),
    ("kernel11sitting11", "a2VybmVsMTFzaXR0aW5nMTE"),
    ("kernel11agent11", "a2VybmVsMTFhZ2VudDEx"),
    ("kernel11angle11", "a2VybmVsMTFhbmdsZTEx"),
    ("kernel11universe11", "a2VybmVsMTF1bml2ZXJzZTEx"),
    ("signal11universe11", "c2lnbmFsMTF1bml2ZXJzZTEx"),
    ("signal11memory11", "c2lnbmFsMTFtZW1vcnkxMQ"),
    ("signal11stream11", "c2lnbmFsMTFzdHJlYW0xMQ"),
    ("signal11context11", "c2lnbmFsMTFjb250ZXh0MTE"),
    ("packet11context11", "cGFja2V0MTFjb250ZXh0MTE"),
    ("packet11knowledge11", "cGFja2V0MTFrbm93bGVkZ2UxMQ"),
    ("packet11vector11", "cGFja2V0MTF2ZWN0b3IxMQ"),
    ("packet11processor11", "cGFja2V0MTFwcm9jZXNzb3IxMQ"),
    ("router11processor11", "cm91dGVyMTFwcm9jZXNzb3IxMQ"),
    ("router11reasoning11", "cm91dGVyMTFyZWFzb25pbmcxMQ"),
    ("router11machine11", "cm91dGVyMTFtYWNoaW5lMTE"),
    ("router11learning11", "cm91dGVyMTFsZWFybmluZzEx"),
    ("cluster11learning11", "Y2x1c3RlcjExbGVhcm5pbmcxMQ"),
    ("cluster11model11", "Y2x1c3RlcjExbW9kZWwxMQ"),
    ("cluster11token11", "Y2x1c3RlcjExdG9rZW4xMQ"),
    ("cluster11prompt11", "Y2x1c3RlcjExcHJvbXB0MTE"),
    ("mirror11prompt11", "bWlycm9yMTFwcm9tcHQxMQ"),
    ("mirror11session11", "bWlycm9yMTFzZXNzaW9uMTE"),
    ("mirror11library11", "bWlycm9yMTFsaWJyYXJ5MTE"),
    ("mirror11service11", "bWlycm9yMTFzZXJ2aWNlMTE"),
    ("filter11service11", "ZmlsdGVyMTFzZXJ2aWNlMTE"),
    ("filter11gateway11", "ZmlsdGVyMTFnYXRld2F5MTE"),
    ("filter11storage11", "ZmlsdGVyMTFzdG9yYWdlMTE"),
    ("filter11network11", "ZmlsdGVyMTFuZXR3b3JrMTE"),
    ("ranking11network11", "cmFua2luZzExbmV0d29yazEx"),
    ("ranking11latency11", "cmFua2luZzExbGF0ZW5jeTEx"),
    ("ranking11buffer11", "cmFua2luZzExYnVmZmVyMTE"),
    ("ranking11queue11", "cmFua2luZzExcXVldWUxMQ"),
    ("encoding11queue11", "ZW5jb2RpbmcxMXF1ZXVlMTE"),
    ("encoding11worker11", "ZW5jb2RpbmcxMXdvcmtlcjEx"),
    ("encoding11kernel11", "ZW5jb2RpbmcxMWtlcm5lbDEx"),
    ("encoding11signal11", "ZW5jb2RpbmcxMXNpZ25hbDEx"),
    ("mapping11signal11", "bWFwcGluZzExc2lnbmFsMTE"),
    ("mapping11packet11", "bWFwcGluZzExcGFja2V0MTE"),
    ("mapping11router11", "bWFwcGluZzExcm91dGVyMTE"),
    ("mapping11cluster11", "bWFwcGluZzExY2x1c3RlcjEx"),
    ("record11cluster11", "cmVjb3JkMTFjbHVzdGVyMTE"),
    ("record11mirror11", "cmVjb3JkMTFtaXJyb3IxMQ"),
    ("record11filter11", "cmVjb3JkMTFmaWx0ZXIxMQ"),
    ("record11ranking11", "cmVjb3JkMTFyYW5raW5nMTE"),
    ("candle11ranking11", "Y2FuZGxlMTFyYW5raW5nMTE"),
    ("candle11encoding11", "Y2FuZGxlMTFlbmNvZGluZzEx"),
    ("candle11mapping11", "Y2FuZGxlMTFtYXBwaW5nMTE"),
    ("candle11record11", "Y2FuZGxlMTFyZWNvcmQxMQ"),
    ("thread11record11", "dGhyZWFkMTFyZWNvcmQxMQ"),
    ("thread11candle11", "dGhyZWFkMTFjYW5kbGUxMQ"),
    ("thread11thread11", "dGhyZWFkMTF0aHJlYWQxMQ"),
    ("thread11kitten11", "dGhyZWFkMTFraXR0ZW4xMQ"),
    (
        "round 11: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTE6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 11: agentuniverse is a framework for multi agents",
        "cm91bmQgMTE6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 11: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTE6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 11: the processor reads the record then stops",
        "cm91bmQgMTE6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 11: a worker pulls the next task from the queue",
        "cm91bmQgMTE6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 11: signals travel through the network layer",
        "cm91bmQgMTE6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 11: the gateway routes each request by policy",
        "cm91bmQgMTE6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 11: memory grows until the buffer is full",
        "cm91bmQgMTE6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 11: the cluster mirrors every packet twice",
        "cm91bmQgMTE6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 11: ranking uses tokens learned from the corpus",
        "cm91bmQgMTE6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 11: a long session ends when the candle dies",
        "cm91bmQgMTE6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 11: encode the prompt then map the result",
        "cm91bmQgMTE6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 11: the kernel wakes the worker at dawn", "cm91bmQgMTE6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 11: service latency drops after the patch",
        "cm91bmQgMTE6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 11: the library caches every vector it sees",
        "cm91bmQgMTE6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 11: agents argue then the debate resolves",
        "cm91bmQgMTE6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 11: the filter keeps only strong matches",
        "cm91bmQgMTE6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 11: the model answers with a short reply",
        "cm91bmQgMTE6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 11: the recorder stores the reasoning trace",
        "cm91bmQgMTE6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 11: the angel watches the processor run", "cm91bmQgMTE6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 11: angle of the vector decides the match",
        "cm91bmQgMTE6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 11: the candle burns twice as long at night",
        "cm91bmQgMTE6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 11: a mirror of the universe in one line",
        "cm91bmQgMTE6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 11: the queue drains before the storm", "cm91bmQgMTE6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
