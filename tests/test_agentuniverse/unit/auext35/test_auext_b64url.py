"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten35kitten35", "a2l0dGVuMzVraXR0ZW4zNQ"),
    ("kitten35sitting35", "a2l0dGVuMzVzaXR0aW5nMzU"),
    ("kitten35agent35", "a2l0dGVuMzVhZ2VudDM1"),
    ("kitten35angle35", "a2l0dGVuMzVhbmdsZTM1"),
    ("sitting35angle35", "c2l0dGluZzM1YW5nbGUzNQ"),
    ("sitting35universe35", "c2l0dGluZzM1dW5pdmVyc2UzNQ"),
    ("sitting35memory35", "c2l0dGluZzM1bWVtb3J5MzU"),
    ("sitting35stream35", "c2l0dGluZzM1c3RyZWFtMzU"),
    ("agent35stream35", "YWdlbnQzNXN0cmVhbTM1"),
    ("agent35context35", "YWdlbnQzNWNvbnRleHQzNQ"),
    ("agent35knowledge35", "YWdlbnQzNWtub3dsZWRnZTM1"),
    ("agent35vector35", "YWdlbnQzNXZlY3RvcjM1"),
    ("angle35vector35", "YW5nbGUzNXZlY3RvcjM1"),
    ("angle35processor35", "YW5nbGUzNXByb2Nlc3NvcjM1"),
    ("angle35reasoning35", "YW5nbGUzNXJlYXNvbmluZzM1"),
    ("angle35machine35", "YW5nbGUzNW1hY2hpbmUzNQ"),
    ("universe35machine35", "dW5pdmVyc2UzNW1hY2hpbmUzNQ"),
    ("universe35learning35", "dW5pdmVyc2UzNWxlYXJuaW5nMzU"),
    ("universe35model35", "dW5pdmVyc2UzNW1vZGVsMzU"),
    ("universe35token35", "dW5pdmVyc2UzNXRva2VuMzU"),
    ("memory35token35", "bWVtb3J5MzV0b2tlbjM1"),
    ("memory35prompt35", "bWVtb3J5MzVwcm9tcHQzNQ"),
    ("memory35session35", "bWVtb3J5MzVzZXNzaW9uMzU"),
    ("memory35library35", "bWVtb3J5MzVsaWJyYXJ5MzU"),
    ("stream35library35", "c3RyZWFtMzVsaWJyYXJ5MzU"),
    ("stream35service35", "c3RyZWFtMzVzZXJ2aWNlMzU"),
    ("stream35gateway35", "c3RyZWFtMzVnYXRld2F5MzU"),
    ("stream35storage35", "c3RyZWFtMzVzdG9yYWdlMzU"),
    ("context35storage35", "Y29udGV4dDM1c3RvcmFnZTM1"),
    ("context35network35", "Y29udGV4dDM1bmV0d29yazM1"),
    ("context35latency35", "Y29udGV4dDM1bGF0ZW5jeTM1"),
    ("context35buffer35", "Y29udGV4dDM1YnVmZmVyMzU"),
    ("knowledge35buffer35", "a25vd2xlZGdlMzVidWZmZXIzNQ"),
    ("knowledge35queue35", "a25vd2xlZGdlMzVxdWV1ZTM1"),
    ("knowledge35worker35", "a25vd2xlZGdlMzV3b3JrZXIzNQ"),
    ("knowledge35kernel35", "a25vd2xlZGdlMzVrZXJuZWwzNQ"),
    ("vector35kernel35", "dmVjdG9yMzVrZXJuZWwzNQ"),
    ("vector35signal35", "dmVjdG9yMzVzaWduYWwzNQ"),
    ("vector35packet35", "dmVjdG9yMzVwYWNrZXQzNQ"),
    ("vector35router35", "dmVjdG9yMzVyb3V0ZXIzNQ"),
    ("processor35router35", "cHJvY2Vzc29yMzVyb3V0ZXIzNQ"),
    ("processor35cluster35", "cHJvY2Vzc29yMzVjbHVzdGVyMzU"),
    ("processor35mirror35", "cHJvY2Vzc29yMzVtaXJyb3IzNQ"),
    ("processor35filter35", "cHJvY2Vzc29yMzVmaWx0ZXIzNQ"),
    ("reasoning35filter35", "cmVhc29uaW5nMzVmaWx0ZXIzNQ"),
    ("reasoning35ranking35", "cmVhc29uaW5nMzVyYW5raW5nMzU"),
    ("reasoning35encoding35", "cmVhc29uaW5nMzVlbmNvZGluZzM1"),
    ("reasoning35mapping35", "cmVhc29uaW5nMzVtYXBwaW5nMzU"),
    ("machine35mapping35", "bWFjaGluZTM1bWFwcGluZzM1"),
    ("machine35record35", "bWFjaGluZTM1cmVjb3JkMzU"),
    ("machine35candle35", "bWFjaGluZTM1Y2FuZGxlMzU"),
    ("machine35thread35", "bWFjaGluZTM1dGhyZWFkMzU"),
    ("learning35thread35", "bGVhcm5pbmczNXRocmVhZDM1"),
    ("learning35kitten35", "bGVhcm5pbmczNWtpdHRlbjM1"),
    ("learning35sitting35", "bGVhcm5pbmczNXNpdHRpbmczNQ"),
    ("learning35agent35", "bGVhcm5pbmczNWFnZW50MzU"),
    ("model35agent35", "bW9kZWwzNWFnZW50MzU"),
    ("model35angle35", "bW9kZWwzNWFuZ2xlMzU"),
    ("model35universe35", "bW9kZWwzNXVuaXZlcnNlMzU"),
    ("model35memory35", "bW9kZWwzNW1lbW9yeTM1"),
    ("token35memory35", "dG9rZW4zNW1lbW9yeTM1"),
    ("token35stream35", "dG9rZW4zNXN0cmVhbTM1"),
    ("token35context35", "dG9rZW4zNWNvbnRleHQzNQ"),
    ("token35knowledge35", "dG9rZW4zNWtub3dsZWRnZTM1"),
    ("prompt35knowledge35", "cHJvbXB0MzVrbm93bGVkZ2UzNQ"),
    ("prompt35vector35", "cHJvbXB0MzV2ZWN0b3IzNQ"),
    ("prompt35processor35", "cHJvbXB0MzVwcm9jZXNzb3IzNQ"),
    ("prompt35reasoning35", "cHJvbXB0MzVyZWFzb25pbmczNQ"),
    ("session35reasoning35", "c2Vzc2lvbjM1cmVhc29uaW5nMzU"),
    ("session35machine35", "c2Vzc2lvbjM1bWFjaGluZTM1"),
    ("session35learning35", "c2Vzc2lvbjM1bGVhcm5pbmczNQ"),
    ("session35model35", "c2Vzc2lvbjM1bW9kZWwzNQ"),
    ("library35model35", "bGlicmFyeTM1bW9kZWwzNQ"),
    ("library35token35", "bGlicmFyeTM1dG9rZW4zNQ"),
    ("library35prompt35", "bGlicmFyeTM1cHJvbXB0MzU"),
    ("library35session35", "bGlicmFyeTM1c2Vzc2lvbjM1"),
    ("service35session35", "c2VydmljZTM1c2Vzc2lvbjM1"),
    ("service35library35", "c2VydmljZTM1bGlicmFyeTM1"),
    ("service35service35", "c2VydmljZTM1c2VydmljZTM1"),
    ("service35gateway35", "c2VydmljZTM1Z2F0ZXdheTM1"),
    ("gateway35gateway35", "Z2F0ZXdheTM1Z2F0ZXdheTM1"),
    ("gateway35storage35", "Z2F0ZXdheTM1c3RvcmFnZTM1"),
    ("gateway35network35", "Z2F0ZXdheTM1bmV0d29yazM1"),
    ("gateway35latency35", "Z2F0ZXdheTM1bGF0ZW5jeTM1"),
    ("storage35latency35", "c3RvcmFnZTM1bGF0ZW5jeTM1"),
    ("storage35buffer35", "c3RvcmFnZTM1YnVmZmVyMzU"),
    ("storage35queue35", "c3RvcmFnZTM1cXVldWUzNQ"),
    ("storage35worker35", "c3RvcmFnZTM1d29ya2VyMzU"),
    ("network35worker35", "bmV0d29yazM1d29ya2VyMzU"),
    ("network35kernel35", "bmV0d29yazM1a2VybmVsMzU"),
    ("network35signal35", "bmV0d29yazM1c2lnbmFsMzU"),
    ("network35packet35", "bmV0d29yazM1cGFja2V0MzU"),
    ("latency35packet35", "bGF0ZW5jeTM1cGFja2V0MzU"),
    ("latency35router35", "bGF0ZW5jeTM1cm91dGVyMzU"),
    ("latency35cluster35", "bGF0ZW5jeTM1Y2x1c3RlcjM1"),
    ("latency35mirror35", "bGF0ZW5jeTM1bWlycm9yMzU"),
    ("buffer35mirror35", "YnVmZmVyMzVtaXJyb3IzNQ"),
    ("buffer35filter35", "YnVmZmVyMzVmaWx0ZXIzNQ"),
    ("buffer35ranking35", "YnVmZmVyMzVyYW5raW5nMzU"),
    ("buffer35encoding35", "YnVmZmVyMzVlbmNvZGluZzM1"),
    ("queue35encoding35", "cXVldWUzNWVuY29kaW5nMzU"),
    ("queue35mapping35", "cXVldWUzNW1hcHBpbmczNQ"),
    ("queue35record35", "cXVldWUzNXJlY29yZDM1"),
    ("queue35candle35", "cXVldWUzNWNhbmRsZTM1"),
    ("worker35candle35", "d29ya2VyMzVjYW5kbGUzNQ"),
    ("worker35thread35", "d29ya2VyMzV0aHJlYWQzNQ"),
    ("worker35kitten35", "d29ya2VyMzVraXR0ZW4zNQ"),
    ("worker35sitting35", "d29ya2VyMzVzaXR0aW5nMzU"),
    ("kernel35sitting35", "a2VybmVsMzVzaXR0aW5nMzU"),
    ("kernel35agent35", "a2VybmVsMzVhZ2VudDM1"),
    ("kernel35angle35", "a2VybmVsMzVhbmdsZTM1"),
    ("kernel35universe35", "a2VybmVsMzV1bml2ZXJzZTM1"),
    ("signal35universe35", "c2lnbmFsMzV1bml2ZXJzZTM1"),
    ("signal35memory35", "c2lnbmFsMzVtZW1vcnkzNQ"),
    ("signal35stream35", "c2lnbmFsMzVzdHJlYW0zNQ"),
    ("signal35context35", "c2lnbmFsMzVjb250ZXh0MzU"),
    ("packet35context35", "cGFja2V0MzVjb250ZXh0MzU"),
    ("packet35knowledge35", "cGFja2V0MzVrbm93bGVkZ2UzNQ"),
    ("packet35vector35", "cGFja2V0MzV2ZWN0b3IzNQ"),
    ("packet35processor35", "cGFja2V0MzVwcm9jZXNzb3IzNQ"),
    ("router35processor35", "cm91dGVyMzVwcm9jZXNzb3IzNQ"),
    ("router35reasoning35", "cm91dGVyMzVyZWFzb25pbmczNQ"),
    ("router35machine35", "cm91dGVyMzVtYWNoaW5lMzU"),
    ("router35learning35", "cm91dGVyMzVsZWFybmluZzM1"),
    ("cluster35learning35", "Y2x1c3RlcjM1bGVhcm5pbmczNQ"),
    ("cluster35model35", "Y2x1c3RlcjM1bW9kZWwzNQ"),
    ("cluster35token35", "Y2x1c3RlcjM1dG9rZW4zNQ"),
    ("cluster35prompt35", "Y2x1c3RlcjM1cHJvbXB0MzU"),
    ("mirror35prompt35", "bWlycm9yMzVwcm9tcHQzNQ"),
    ("mirror35session35", "bWlycm9yMzVzZXNzaW9uMzU"),
    ("mirror35library35", "bWlycm9yMzVsaWJyYXJ5MzU"),
    ("mirror35service35", "bWlycm9yMzVzZXJ2aWNlMzU"),
    ("filter35service35", "ZmlsdGVyMzVzZXJ2aWNlMzU"),
    ("filter35gateway35", "ZmlsdGVyMzVnYXRld2F5MzU"),
    ("filter35storage35", "ZmlsdGVyMzVzdG9yYWdlMzU"),
    ("filter35network35", "ZmlsdGVyMzVuZXR3b3JrMzU"),
    ("ranking35network35", "cmFua2luZzM1bmV0d29yazM1"),
    ("ranking35latency35", "cmFua2luZzM1bGF0ZW5jeTM1"),
    ("ranking35buffer35", "cmFua2luZzM1YnVmZmVyMzU"),
    ("ranking35queue35", "cmFua2luZzM1cXVldWUzNQ"),
    ("encoding35queue35", "ZW5jb2RpbmczNXF1ZXVlMzU"),
    ("encoding35worker35", "ZW5jb2RpbmczNXdvcmtlcjM1"),
    ("encoding35kernel35", "ZW5jb2RpbmczNWtlcm5lbDM1"),
    ("encoding35signal35", "ZW5jb2RpbmczNXNpZ25hbDM1"),
    ("mapping35signal35", "bWFwcGluZzM1c2lnbmFsMzU"),
    ("mapping35packet35", "bWFwcGluZzM1cGFja2V0MzU"),
    ("mapping35router35", "bWFwcGluZzM1cm91dGVyMzU"),
    ("mapping35cluster35", "bWFwcGluZzM1Y2x1c3RlcjM1"),
    ("record35cluster35", "cmVjb3JkMzVjbHVzdGVyMzU"),
    ("record35mirror35", "cmVjb3JkMzVtaXJyb3IzNQ"),
    ("record35filter35", "cmVjb3JkMzVmaWx0ZXIzNQ"),
    ("record35ranking35", "cmVjb3JkMzVyYW5raW5nMzU"),
    ("candle35ranking35", "Y2FuZGxlMzVyYW5raW5nMzU"),
    ("candle35encoding35", "Y2FuZGxlMzVlbmNvZGluZzM1"),
    ("candle35mapping35", "Y2FuZGxlMzVtYXBwaW5nMzU"),
    ("candle35record35", "Y2FuZGxlMzVyZWNvcmQzNQ"),
    ("thread35record35", "dGhyZWFkMzVyZWNvcmQzNQ"),
    ("thread35candle35", "dGhyZWFkMzVjYW5kbGUzNQ"),
    ("thread35thread35", "dGhyZWFkMzV0aHJlYWQzNQ"),
    ("thread35kitten35", "dGhyZWFkMzVraXR0ZW4zNQ"),
    (
        "round 35: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMzU6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 35: agentuniverse is a framework for multi agents",
        "cm91bmQgMzU6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 35: knowledge stored as vectors enables retrieval",
        "cm91bmQgMzU6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 35: the processor reads the record then stops",
        "cm91bmQgMzU6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 35: a worker pulls the next task from the queue",
        "cm91bmQgMzU6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 35: signals travel through the network layer",
        "cm91bmQgMzU6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 35: the gateway routes each request by policy",
        "cm91bmQgMzU6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 35: memory grows until the buffer is full",
        "cm91bmQgMzU6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 35: the cluster mirrors every packet twice",
        "cm91bmQgMzU6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 35: ranking uses tokens learned from the corpus",
        "cm91bmQgMzU6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 35: a long session ends when the candle dies",
        "cm91bmQgMzU6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 35: encode the prompt then map the result",
        "cm91bmQgMzU6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 35: the kernel wakes the worker at dawn", "cm91bmQgMzU6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 35: service latency drops after the patch",
        "cm91bmQgMzU6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 35: the library caches every vector it sees",
        "cm91bmQgMzU6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 35: agents argue then the debate resolves",
        "cm91bmQgMzU6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 35: the filter keeps only strong matches",
        "cm91bmQgMzU6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 35: the model answers with a short reply",
        "cm91bmQgMzU6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 35: the recorder stores the reasoning trace",
        "cm91bmQgMzU6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 35: the angel watches the processor run", "cm91bmQgMzU6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 35: angle of the vector decides the match",
        "cm91bmQgMzU6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 35: the candle burns twice as long at night",
        "cm91bmQgMzU6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 35: a mirror of the universe in one line",
        "cm91bmQgMzU6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 35: the queue drains before the storm", "cm91bmQgMzU6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
