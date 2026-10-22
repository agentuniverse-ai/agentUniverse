"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten15kitten15", "a2l0dGVuMTVraXR0ZW4xNQ"),
    ("kitten15sitting15", "a2l0dGVuMTVzaXR0aW5nMTU"),
    ("kitten15agent15", "a2l0dGVuMTVhZ2VudDE1"),
    ("kitten15angle15", "a2l0dGVuMTVhbmdsZTE1"),
    ("sitting15angle15", "c2l0dGluZzE1YW5nbGUxNQ"),
    ("sitting15universe15", "c2l0dGluZzE1dW5pdmVyc2UxNQ"),
    ("sitting15memory15", "c2l0dGluZzE1bWVtb3J5MTU"),
    ("sitting15stream15", "c2l0dGluZzE1c3RyZWFtMTU"),
    ("agent15stream15", "YWdlbnQxNXN0cmVhbTE1"),
    ("agent15context15", "YWdlbnQxNWNvbnRleHQxNQ"),
    ("agent15knowledge15", "YWdlbnQxNWtub3dsZWRnZTE1"),
    ("agent15vector15", "YWdlbnQxNXZlY3RvcjE1"),
    ("angle15vector15", "YW5nbGUxNXZlY3RvcjE1"),
    ("angle15processor15", "YW5nbGUxNXByb2Nlc3NvcjE1"),
    ("angle15reasoning15", "YW5nbGUxNXJlYXNvbmluZzE1"),
    ("angle15machine15", "YW5nbGUxNW1hY2hpbmUxNQ"),
    ("universe15machine15", "dW5pdmVyc2UxNW1hY2hpbmUxNQ"),
    ("universe15learning15", "dW5pdmVyc2UxNWxlYXJuaW5nMTU"),
    ("universe15model15", "dW5pdmVyc2UxNW1vZGVsMTU"),
    ("universe15token15", "dW5pdmVyc2UxNXRva2VuMTU"),
    ("memory15token15", "bWVtb3J5MTV0b2tlbjE1"),
    ("memory15prompt15", "bWVtb3J5MTVwcm9tcHQxNQ"),
    ("memory15session15", "bWVtb3J5MTVzZXNzaW9uMTU"),
    ("memory15library15", "bWVtb3J5MTVsaWJyYXJ5MTU"),
    ("stream15library15", "c3RyZWFtMTVsaWJyYXJ5MTU"),
    ("stream15service15", "c3RyZWFtMTVzZXJ2aWNlMTU"),
    ("stream15gateway15", "c3RyZWFtMTVnYXRld2F5MTU"),
    ("stream15storage15", "c3RyZWFtMTVzdG9yYWdlMTU"),
    ("context15storage15", "Y29udGV4dDE1c3RvcmFnZTE1"),
    ("context15network15", "Y29udGV4dDE1bmV0d29yazE1"),
    ("context15latency15", "Y29udGV4dDE1bGF0ZW5jeTE1"),
    ("context15buffer15", "Y29udGV4dDE1YnVmZmVyMTU"),
    ("knowledge15buffer15", "a25vd2xlZGdlMTVidWZmZXIxNQ"),
    ("knowledge15queue15", "a25vd2xlZGdlMTVxdWV1ZTE1"),
    ("knowledge15worker15", "a25vd2xlZGdlMTV3b3JrZXIxNQ"),
    ("knowledge15kernel15", "a25vd2xlZGdlMTVrZXJuZWwxNQ"),
    ("vector15kernel15", "dmVjdG9yMTVrZXJuZWwxNQ"),
    ("vector15signal15", "dmVjdG9yMTVzaWduYWwxNQ"),
    ("vector15packet15", "dmVjdG9yMTVwYWNrZXQxNQ"),
    ("vector15router15", "dmVjdG9yMTVyb3V0ZXIxNQ"),
    ("processor15router15", "cHJvY2Vzc29yMTVyb3V0ZXIxNQ"),
    ("processor15cluster15", "cHJvY2Vzc29yMTVjbHVzdGVyMTU"),
    ("processor15mirror15", "cHJvY2Vzc29yMTVtaXJyb3IxNQ"),
    ("processor15filter15", "cHJvY2Vzc29yMTVmaWx0ZXIxNQ"),
    ("reasoning15filter15", "cmVhc29uaW5nMTVmaWx0ZXIxNQ"),
    ("reasoning15ranking15", "cmVhc29uaW5nMTVyYW5raW5nMTU"),
    ("reasoning15encoding15", "cmVhc29uaW5nMTVlbmNvZGluZzE1"),
    ("reasoning15mapping15", "cmVhc29uaW5nMTVtYXBwaW5nMTU"),
    ("machine15mapping15", "bWFjaGluZTE1bWFwcGluZzE1"),
    ("machine15record15", "bWFjaGluZTE1cmVjb3JkMTU"),
    ("machine15candle15", "bWFjaGluZTE1Y2FuZGxlMTU"),
    ("machine15thread15", "bWFjaGluZTE1dGhyZWFkMTU"),
    ("learning15thread15", "bGVhcm5pbmcxNXRocmVhZDE1"),
    ("learning15kitten15", "bGVhcm5pbmcxNWtpdHRlbjE1"),
    ("learning15sitting15", "bGVhcm5pbmcxNXNpdHRpbmcxNQ"),
    ("learning15agent15", "bGVhcm5pbmcxNWFnZW50MTU"),
    ("model15agent15", "bW9kZWwxNWFnZW50MTU"),
    ("model15angle15", "bW9kZWwxNWFuZ2xlMTU"),
    ("model15universe15", "bW9kZWwxNXVuaXZlcnNlMTU"),
    ("model15memory15", "bW9kZWwxNW1lbW9yeTE1"),
    ("token15memory15", "dG9rZW4xNW1lbW9yeTE1"),
    ("token15stream15", "dG9rZW4xNXN0cmVhbTE1"),
    ("token15context15", "dG9rZW4xNWNvbnRleHQxNQ"),
    ("token15knowledge15", "dG9rZW4xNWtub3dsZWRnZTE1"),
    ("prompt15knowledge15", "cHJvbXB0MTVrbm93bGVkZ2UxNQ"),
    ("prompt15vector15", "cHJvbXB0MTV2ZWN0b3IxNQ"),
    ("prompt15processor15", "cHJvbXB0MTVwcm9jZXNzb3IxNQ"),
    ("prompt15reasoning15", "cHJvbXB0MTVyZWFzb25pbmcxNQ"),
    ("session15reasoning15", "c2Vzc2lvbjE1cmVhc29uaW5nMTU"),
    ("session15machine15", "c2Vzc2lvbjE1bWFjaGluZTE1"),
    ("session15learning15", "c2Vzc2lvbjE1bGVhcm5pbmcxNQ"),
    ("session15model15", "c2Vzc2lvbjE1bW9kZWwxNQ"),
    ("library15model15", "bGlicmFyeTE1bW9kZWwxNQ"),
    ("library15token15", "bGlicmFyeTE1dG9rZW4xNQ"),
    ("library15prompt15", "bGlicmFyeTE1cHJvbXB0MTU"),
    ("library15session15", "bGlicmFyeTE1c2Vzc2lvbjE1"),
    ("service15session15", "c2VydmljZTE1c2Vzc2lvbjE1"),
    ("service15library15", "c2VydmljZTE1bGlicmFyeTE1"),
    ("service15service15", "c2VydmljZTE1c2VydmljZTE1"),
    ("service15gateway15", "c2VydmljZTE1Z2F0ZXdheTE1"),
    ("gateway15gateway15", "Z2F0ZXdheTE1Z2F0ZXdheTE1"),
    ("gateway15storage15", "Z2F0ZXdheTE1c3RvcmFnZTE1"),
    ("gateway15network15", "Z2F0ZXdheTE1bmV0d29yazE1"),
    ("gateway15latency15", "Z2F0ZXdheTE1bGF0ZW5jeTE1"),
    ("storage15latency15", "c3RvcmFnZTE1bGF0ZW5jeTE1"),
    ("storage15buffer15", "c3RvcmFnZTE1YnVmZmVyMTU"),
    ("storage15queue15", "c3RvcmFnZTE1cXVldWUxNQ"),
    ("storage15worker15", "c3RvcmFnZTE1d29ya2VyMTU"),
    ("network15worker15", "bmV0d29yazE1d29ya2VyMTU"),
    ("network15kernel15", "bmV0d29yazE1a2VybmVsMTU"),
    ("network15signal15", "bmV0d29yazE1c2lnbmFsMTU"),
    ("network15packet15", "bmV0d29yazE1cGFja2V0MTU"),
    ("latency15packet15", "bGF0ZW5jeTE1cGFja2V0MTU"),
    ("latency15router15", "bGF0ZW5jeTE1cm91dGVyMTU"),
    ("latency15cluster15", "bGF0ZW5jeTE1Y2x1c3RlcjE1"),
    ("latency15mirror15", "bGF0ZW5jeTE1bWlycm9yMTU"),
    ("buffer15mirror15", "YnVmZmVyMTVtaXJyb3IxNQ"),
    ("buffer15filter15", "YnVmZmVyMTVmaWx0ZXIxNQ"),
    ("buffer15ranking15", "YnVmZmVyMTVyYW5raW5nMTU"),
    ("buffer15encoding15", "YnVmZmVyMTVlbmNvZGluZzE1"),
    ("queue15encoding15", "cXVldWUxNWVuY29kaW5nMTU"),
    ("queue15mapping15", "cXVldWUxNW1hcHBpbmcxNQ"),
    ("queue15record15", "cXVldWUxNXJlY29yZDE1"),
    ("queue15candle15", "cXVldWUxNWNhbmRsZTE1"),
    ("worker15candle15", "d29ya2VyMTVjYW5kbGUxNQ"),
    ("worker15thread15", "d29ya2VyMTV0aHJlYWQxNQ"),
    ("worker15kitten15", "d29ya2VyMTVraXR0ZW4xNQ"),
    ("worker15sitting15", "d29ya2VyMTVzaXR0aW5nMTU"),
    ("kernel15sitting15", "a2VybmVsMTVzaXR0aW5nMTU"),
    ("kernel15agent15", "a2VybmVsMTVhZ2VudDE1"),
    ("kernel15angle15", "a2VybmVsMTVhbmdsZTE1"),
    ("kernel15universe15", "a2VybmVsMTV1bml2ZXJzZTE1"),
    ("signal15universe15", "c2lnbmFsMTV1bml2ZXJzZTE1"),
    ("signal15memory15", "c2lnbmFsMTVtZW1vcnkxNQ"),
    ("signal15stream15", "c2lnbmFsMTVzdHJlYW0xNQ"),
    ("signal15context15", "c2lnbmFsMTVjb250ZXh0MTU"),
    ("packet15context15", "cGFja2V0MTVjb250ZXh0MTU"),
    ("packet15knowledge15", "cGFja2V0MTVrbm93bGVkZ2UxNQ"),
    ("packet15vector15", "cGFja2V0MTV2ZWN0b3IxNQ"),
    ("packet15processor15", "cGFja2V0MTVwcm9jZXNzb3IxNQ"),
    ("router15processor15", "cm91dGVyMTVwcm9jZXNzb3IxNQ"),
    ("router15reasoning15", "cm91dGVyMTVyZWFzb25pbmcxNQ"),
    ("router15machine15", "cm91dGVyMTVtYWNoaW5lMTU"),
    ("router15learning15", "cm91dGVyMTVsZWFybmluZzE1"),
    ("cluster15learning15", "Y2x1c3RlcjE1bGVhcm5pbmcxNQ"),
    ("cluster15model15", "Y2x1c3RlcjE1bW9kZWwxNQ"),
    ("cluster15token15", "Y2x1c3RlcjE1dG9rZW4xNQ"),
    ("cluster15prompt15", "Y2x1c3RlcjE1cHJvbXB0MTU"),
    ("mirror15prompt15", "bWlycm9yMTVwcm9tcHQxNQ"),
    ("mirror15session15", "bWlycm9yMTVzZXNzaW9uMTU"),
    ("mirror15library15", "bWlycm9yMTVsaWJyYXJ5MTU"),
    ("mirror15service15", "bWlycm9yMTVzZXJ2aWNlMTU"),
    ("filter15service15", "ZmlsdGVyMTVzZXJ2aWNlMTU"),
    ("filter15gateway15", "ZmlsdGVyMTVnYXRld2F5MTU"),
    ("filter15storage15", "ZmlsdGVyMTVzdG9yYWdlMTU"),
    ("filter15network15", "ZmlsdGVyMTVuZXR3b3JrMTU"),
    ("ranking15network15", "cmFua2luZzE1bmV0d29yazE1"),
    ("ranking15latency15", "cmFua2luZzE1bGF0ZW5jeTE1"),
    ("ranking15buffer15", "cmFua2luZzE1YnVmZmVyMTU"),
    ("ranking15queue15", "cmFua2luZzE1cXVldWUxNQ"),
    ("encoding15queue15", "ZW5jb2RpbmcxNXF1ZXVlMTU"),
    ("encoding15worker15", "ZW5jb2RpbmcxNXdvcmtlcjE1"),
    ("encoding15kernel15", "ZW5jb2RpbmcxNWtlcm5lbDE1"),
    ("encoding15signal15", "ZW5jb2RpbmcxNXNpZ25hbDE1"),
    ("mapping15signal15", "bWFwcGluZzE1c2lnbmFsMTU"),
    ("mapping15packet15", "bWFwcGluZzE1cGFja2V0MTU"),
    ("mapping15router15", "bWFwcGluZzE1cm91dGVyMTU"),
    ("mapping15cluster15", "bWFwcGluZzE1Y2x1c3RlcjE1"),
    ("record15cluster15", "cmVjb3JkMTVjbHVzdGVyMTU"),
    ("record15mirror15", "cmVjb3JkMTVtaXJyb3IxNQ"),
    ("record15filter15", "cmVjb3JkMTVmaWx0ZXIxNQ"),
    ("record15ranking15", "cmVjb3JkMTVyYW5raW5nMTU"),
    ("candle15ranking15", "Y2FuZGxlMTVyYW5raW5nMTU"),
    ("candle15encoding15", "Y2FuZGxlMTVlbmNvZGluZzE1"),
    ("candle15mapping15", "Y2FuZGxlMTVtYXBwaW5nMTU"),
    ("candle15record15", "Y2FuZGxlMTVyZWNvcmQxNQ"),
    ("thread15record15", "dGhyZWFkMTVyZWNvcmQxNQ"),
    ("thread15candle15", "dGhyZWFkMTVjYW5kbGUxNQ"),
    ("thread15thread15", "dGhyZWFkMTV0aHJlYWQxNQ"),
    ("thread15kitten15", "dGhyZWFkMTVraXR0ZW4xNQ"),
    (
        "round 15: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTU6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 15: agentuniverse is a framework for multi agents",
        "cm91bmQgMTU6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 15: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTU6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 15: the processor reads the record then stops",
        "cm91bmQgMTU6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 15: a worker pulls the next task from the queue",
        "cm91bmQgMTU6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 15: signals travel through the network layer",
        "cm91bmQgMTU6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 15: the gateway routes each request by policy",
        "cm91bmQgMTU6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 15: memory grows until the buffer is full",
        "cm91bmQgMTU6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 15: the cluster mirrors every packet twice",
        "cm91bmQgMTU6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 15: ranking uses tokens learned from the corpus",
        "cm91bmQgMTU6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 15: a long session ends when the candle dies",
        "cm91bmQgMTU6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 15: encode the prompt then map the result",
        "cm91bmQgMTU6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 15: the kernel wakes the worker at dawn", "cm91bmQgMTU6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 15: service latency drops after the patch",
        "cm91bmQgMTU6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 15: the library caches every vector it sees",
        "cm91bmQgMTU6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 15: agents argue then the debate resolves",
        "cm91bmQgMTU6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 15: the filter keeps only strong matches",
        "cm91bmQgMTU6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 15: the model answers with a short reply",
        "cm91bmQgMTU6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 15: the recorder stores the reasoning trace",
        "cm91bmQgMTU6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 15: the angel watches the processor run", "cm91bmQgMTU6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 15: angle of the vector decides the match",
        "cm91bmQgMTU6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 15: the candle burns twice as long at night",
        "cm91bmQgMTU6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 15: a mirror of the universe in one line",
        "cm91bmQgMTU6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 15: the queue drains before the storm", "cm91bmQgMTU6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
