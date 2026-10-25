"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten25kitten25", "a2l0dGVuMjVraXR0ZW4yNQ"),
    ("kitten25sitting25", "a2l0dGVuMjVzaXR0aW5nMjU"),
    ("kitten25agent25", "a2l0dGVuMjVhZ2VudDI1"),
    ("kitten25angle25", "a2l0dGVuMjVhbmdsZTI1"),
    ("sitting25angle25", "c2l0dGluZzI1YW5nbGUyNQ"),
    ("sitting25universe25", "c2l0dGluZzI1dW5pdmVyc2UyNQ"),
    ("sitting25memory25", "c2l0dGluZzI1bWVtb3J5MjU"),
    ("sitting25stream25", "c2l0dGluZzI1c3RyZWFtMjU"),
    ("agent25stream25", "YWdlbnQyNXN0cmVhbTI1"),
    ("agent25context25", "YWdlbnQyNWNvbnRleHQyNQ"),
    ("agent25knowledge25", "YWdlbnQyNWtub3dsZWRnZTI1"),
    ("agent25vector25", "YWdlbnQyNXZlY3RvcjI1"),
    ("angle25vector25", "YW5nbGUyNXZlY3RvcjI1"),
    ("angle25processor25", "YW5nbGUyNXByb2Nlc3NvcjI1"),
    ("angle25reasoning25", "YW5nbGUyNXJlYXNvbmluZzI1"),
    ("angle25machine25", "YW5nbGUyNW1hY2hpbmUyNQ"),
    ("universe25machine25", "dW5pdmVyc2UyNW1hY2hpbmUyNQ"),
    ("universe25learning25", "dW5pdmVyc2UyNWxlYXJuaW5nMjU"),
    ("universe25model25", "dW5pdmVyc2UyNW1vZGVsMjU"),
    ("universe25token25", "dW5pdmVyc2UyNXRva2VuMjU"),
    ("memory25token25", "bWVtb3J5MjV0b2tlbjI1"),
    ("memory25prompt25", "bWVtb3J5MjVwcm9tcHQyNQ"),
    ("memory25session25", "bWVtb3J5MjVzZXNzaW9uMjU"),
    ("memory25library25", "bWVtb3J5MjVsaWJyYXJ5MjU"),
    ("stream25library25", "c3RyZWFtMjVsaWJyYXJ5MjU"),
    ("stream25service25", "c3RyZWFtMjVzZXJ2aWNlMjU"),
    ("stream25gateway25", "c3RyZWFtMjVnYXRld2F5MjU"),
    ("stream25storage25", "c3RyZWFtMjVzdG9yYWdlMjU"),
    ("context25storage25", "Y29udGV4dDI1c3RvcmFnZTI1"),
    ("context25network25", "Y29udGV4dDI1bmV0d29yazI1"),
    ("context25latency25", "Y29udGV4dDI1bGF0ZW5jeTI1"),
    ("context25buffer25", "Y29udGV4dDI1YnVmZmVyMjU"),
    ("knowledge25buffer25", "a25vd2xlZGdlMjVidWZmZXIyNQ"),
    ("knowledge25queue25", "a25vd2xlZGdlMjVxdWV1ZTI1"),
    ("knowledge25worker25", "a25vd2xlZGdlMjV3b3JrZXIyNQ"),
    ("knowledge25kernel25", "a25vd2xlZGdlMjVrZXJuZWwyNQ"),
    ("vector25kernel25", "dmVjdG9yMjVrZXJuZWwyNQ"),
    ("vector25signal25", "dmVjdG9yMjVzaWduYWwyNQ"),
    ("vector25packet25", "dmVjdG9yMjVwYWNrZXQyNQ"),
    ("vector25router25", "dmVjdG9yMjVyb3V0ZXIyNQ"),
    ("processor25router25", "cHJvY2Vzc29yMjVyb3V0ZXIyNQ"),
    ("processor25cluster25", "cHJvY2Vzc29yMjVjbHVzdGVyMjU"),
    ("processor25mirror25", "cHJvY2Vzc29yMjVtaXJyb3IyNQ"),
    ("processor25filter25", "cHJvY2Vzc29yMjVmaWx0ZXIyNQ"),
    ("reasoning25filter25", "cmVhc29uaW5nMjVmaWx0ZXIyNQ"),
    ("reasoning25ranking25", "cmVhc29uaW5nMjVyYW5raW5nMjU"),
    ("reasoning25encoding25", "cmVhc29uaW5nMjVlbmNvZGluZzI1"),
    ("reasoning25mapping25", "cmVhc29uaW5nMjVtYXBwaW5nMjU"),
    ("machine25mapping25", "bWFjaGluZTI1bWFwcGluZzI1"),
    ("machine25record25", "bWFjaGluZTI1cmVjb3JkMjU"),
    ("machine25candle25", "bWFjaGluZTI1Y2FuZGxlMjU"),
    ("machine25thread25", "bWFjaGluZTI1dGhyZWFkMjU"),
    ("learning25thread25", "bGVhcm5pbmcyNXRocmVhZDI1"),
    ("learning25kitten25", "bGVhcm5pbmcyNWtpdHRlbjI1"),
    ("learning25sitting25", "bGVhcm5pbmcyNXNpdHRpbmcyNQ"),
    ("learning25agent25", "bGVhcm5pbmcyNWFnZW50MjU"),
    ("model25agent25", "bW9kZWwyNWFnZW50MjU"),
    ("model25angle25", "bW9kZWwyNWFuZ2xlMjU"),
    ("model25universe25", "bW9kZWwyNXVuaXZlcnNlMjU"),
    ("model25memory25", "bW9kZWwyNW1lbW9yeTI1"),
    ("token25memory25", "dG9rZW4yNW1lbW9yeTI1"),
    ("token25stream25", "dG9rZW4yNXN0cmVhbTI1"),
    ("token25context25", "dG9rZW4yNWNvbnRleHQyNQ"),
    ("token25knowledge25", "dG9rZW4yNWtub3dsZWRnZTI1"),
    ("prompt25knowledge25", "cHJvbXB0MjVrbm93bGVkZ2UyNQ"),
    ("prompt25vector25", "cHJvbXB0MjV2ZWN0b3IyNQ"),
    ("prompt25processor25", "cHJvbXB0MjVwcm9jZXNzb3IyNQ"),
    ("prompt25reasoning25", "cHJvbXB0MjVyZWFzb25pbmcyNQ"),
    ("session25reasoning25", "c2Vzc2lvbjI1cmVhc29uaW5nMjU"),
    ("session25machine25", "c2Vzc2lvbjI1bWFjaGluZTI1"),
    ("session25learning25", "c2Vzc2lvbjI1bGVhcm5pbmcyNQ"),
    ("session25model25", "c2Vzc2lvbjI1bW9kZWwyNQ"),
    ("library25model25", "bGlicmFyeTI1bW9kZWwyNQ"),
    ("library25token25", "bGlicmFyeTI1dG9rZW4yNQ"),
    ("library25prompt25", "bGlicmFyeTI1cHJvbXB0MjU"),
    ("library25session25", "bGlicmFyeTI1c2Vzc2lvbjI1"),
    ("service25session25", "c2VydmljZTI1c2Vzc2lvbjI1"),
    ("service25library25", "c2VydmljZTI1bGlicmFyeTI1"),
    ("service25service25", "c2VydmljZTI1c2VydmljZTI1"),
    ("service25gateway25", "c2VydmljZTI1Z2F0ZXdheTI1"),
    ("gateway25gateway25", "Z2F0ZXdheTI1Z2F0ZXdheTI1"),
    ("gateway25storage25", "Z2F0ZXdheTI1c3RvcmFnZTI1"),
    ("gateway25network25", "Z2F0ZXdheTI1bmV0d29yazI1"),
    ("gateway25latency25", "Z2F0ZXdheTI1bGF0ZW5jeTI1"),
    ("storage25latency25", "c3RvcmFnZTI1bGF0ZW5jeTI1"),
    ("storage25buffer25", "c3RvcmFnZTI1YnVmZmVyMjU"),
    ("storage25queue25", "c3RvcmFnZTI1cXVldWUyNQ"),
    ("storage25worker25", "c3RvcmFnZTI1d29ya2VyMjU"),
    ("network25worker25", "bmV0d29yazI1d29ya2VyMjU"),
    ("network25kernel25", "bmV0d29yazI1a2VybmVsMjU"),
    ("network25signal25", "bmV0d29yazI1c2lnbmFsMjU"),
    ("network25packet25", "bmV0d29yazI1cGFja2V0MjU"),
    ("latency25packet25", "bGF0ZW5jeTI1cGFja2V0MjU"),
    ("latency25router25", "bGF0ZW5jeTI1cm91dGVyMjU"),
    ("latency25cluster25", "bGF0ZW5jeTI1Y2x1c3RlcjI1"),
    ("latency25mirror25", "bGF0ZW5jeTI1bWlycm9yMjU"),
    ("buffer25mirror25", "YnVmZmVyMjVtaXJyb3IyNQ"),
    ("buffer25filter25", "YnVmZmVyMjVmaWx0ZXIyNQ"),
    ("buffer25ranking25", "YnVmZmVyMjVyYW5raW5nMjU"),
    ("buffer25encoding25", "YnVmZmVyMjVlbmNvZGluZzI1"),
    ("queue25encoding25", "cXVldWUyNWVuY29kaW5nMjU"),
    ("queue25mapping25", "cXVldWUyNW1hcHBpbmcyNQ"),
    ("queue25record25", "cXVldWUyNXJlY29yZDI1"),
    ("queue25candle25", "cXVldWUyNWNhbmRsZTI1"),
    ("worker25candle25", "d29ya2VyMjVjYW5kbGUyNQ"),
    ("worker25thread25", "d29ya2VyMjV0aHJlYWQyNQ"),
    ("worker25kitten25", "d29ya2VyMjVraXR0ZW4yNQ"),
    ("worker25sitting25", "d29ya2VyMjVzaXR0aW5nMjU"),
    ("kernel25sitting25", "a2VybmVsMjVzaXR0aW5nMjU"),
    ("kernel25agent25", "a2VybmVsMjVhZ2VudDI1"),
    ("kernel25angle25", "a2VybmVsMjVhbmdsZTI1"),
    ("kernel25universe25", "a2VybmVsMjV1bml2ZXJzZTI1"),
    ("signal25universe25", "c2lnbmFsMjV1bml2ZXJzZTI1"),
    ("signal25memory25", "c2lnbmFsMjVtZW1vcnkyNQ"),
    ("signal25stream25", "c2lnbmFsMjVzdHJlYW0yNQ"),
    ("signal25context25", "c2lnbmFsMjVjb250ZXh0MjU"),
    ("packet25context25", "cGFja2V0MjVjb250ZXh0MjU"),
    ("packet25knowledge25", "cGFja2V0MjVrbm93bGVkZ2UyNQ"),
    ("packet25vector25", "cGFja2V0MjV2ZWN0b3IyNQ"),
    ("packet25processor25", "cGFja2V0MjVwcm9jZXNzb3IyNQ"),
    ("router25processor25", "cm91dGVyMjVwcm9jZXNzb3IyNQ"),
    ("router25reasoning25", "cm91dGVyMjVyZWFzb25pbmcyNQ"),
    ("router25machine25", "cm91dGVyMjVtYWNoaW5lMjU"),
    ("router25learning25", "cm91dGVyMjVsZWFybmluZzI1"),
    ("cluster25learning25", "Y2x1c3RlcjI1bGVhcm5pbmcyNQ"),
    ("cluster25model25", "Y2x1c3RlcjI1bW9kZWwyNQ"),
    ("cluster25token25", "Y2x1c3RlcjI1dG9rZW4yNQ"),
    ("cluster25prompt25", "Y2x1c3RlcjI1cHJvbXB0MjU"),
    ("mirror25prompt25", "bWlycm9yMjVwcm9tcHQyNQ"),
    ("mirror25session25", "bWlycm9yMjVzZXNzaW9uMjU"),
    ("mirror25library25", "bWlycm9yMjVsaWJyYXJ5MjU"),
    ("mirror25service25", "bWlycm9yMjVzZXJ2aWNlMjU"),
    ("filter25service25", "ZmlsdGVyMjVzZXJ2aWNlMjU"),
    ("filter25gateway25", "ZmlsdGVyMjVnYXRld2F5MjU"),
    ("filter25storage25", "ZmlsdGVyMjVzdG9yYWdlMjU"),
    ("filter25network25", "ZmlsdGVyMjVuZXR3b3JrMjU"),
    ("ranking25network25", "cmFua2luZzI1bmV0d29yazI1"),
    ("ranking25latency25", "cmFua2luZzI1bGF0ZW5jeTI1"),
    ("ranking25buffer25", "cmFua2luZzI1YnVmZmVyMjU"),
    ("ranking25queue25", "cmFua2luZzI1cXVldWUyNQ"),
    ("encoding25queue25", "ZW5jb2RpbmcyNXF1ZXVlMjU"),
    ("encoding25worker25", "ZW5jb2RpbmcyNXdvcmtlcjI1"),
    ("encoding25kernel25", "ZW5jb2RpbmcyNWtlcm5lbDI1"),
    ("encoding25signal25", "ZW5jb2RpbmcyNXNpZ25hbDI1"),
    ("mapping25signal25", "bWFwcGluZzI1c2lnbmFsMjU"),
    ("mapping25packet25", "bWFwcGluZzI1cGFja2V0MjU"),
    ("mapping25router25", "bWFwcGluZzI1cm91dGVyMjU"),
    ("mapping25cluster25", "bWFwcGluZzI1Y2x1c3RlcjI1"),
    ("record25cluster25", "cmVjb3JkMjVjbHVzdGVyMjU"),
    ("record25mirror25", "cmVjb3JkMjVtaXJyb3IyNQ"),
    ("record25filter25", "cmVjb3JkMjVmaWx0ZXIyNQ"),
    ("record25ranking25", "cmVjb3JkMjVyYW5raW5nMjU"),
    ("candle25ranking25", "Y2FuZGxlMjVyYW5raW5nMjU"),
    ("candle25encoding25", "Y2FuZGxlMjVlbmNvZGluZzI1"),
    ("candle25mapping25", "Y2FuZGxlMjVtYXBwaW5nMjU"),
    ("candle25record25", "Y2FuZGxlMjVyZWNvcmQyNQ"),
    ("thread25record25", "dGhyZWFkMjVyZWNvcmQyNQ"),
    ("thread25candle25", "dGhyZWFkMjVjYW5kbGUyNQ"),
    ("thread25thread25", "dGhyZWFkMjV0aHJlYWQyNQ"),
    ("thread25kitten25", "dGhyZWFkMjVraXR0ZW4yNQ"),
    (
        "round 25: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjU6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 25: agentuniverse is a framework for multi agents",
        "cm91bmQgMjU6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 25: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjU6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 25: the processor reads the record then stops",
        "cm91bmQgMjU6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 25: a worker pulls the next task from the queue",
        "cm91bmQgMjU6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 25: signals travel through the network layer",
        "cm91bmQgMjU6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 25: the gateway routes each request by policy",
        "cm91bmQgMjU6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 25: memory grows until the buffer is full",
        "cm91bmQgMjU6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 25: the cluster mirrors every packet twice",
        "cm91bmQgMjU6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 25: ranking uses tokens learned from the corpus",
        "cm91bmQgMjU6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 25: a long session ends when the candle dies",
        "cm91bmQgMjU6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 25: encode the prompt then map the result",
        "cm91bmQgMjU6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 25: the kernel wakes the worker at dawn", "cm91bmQgMjU6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 25: service latency drops after the patch",
        "cm91bmQgMjU6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 25: the library caches every vector it sees",
        "cm91bmQgMjU6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 25: agents argue then the debate resolves",
        "cm91bmQgMjU6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 25: the filter keeps only strong matches",
        "cm91bmQgMjU6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 25: the model answers with a short reply",
        "cm91bmQgMjU6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 25: the recorder stores the reasoning trace",
        "cm91bmQgMjU6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 25: the angel watches the processor run", "cm91bmQgMjU6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 25: angle of the vector decides the match",
        "cm91bmQgMjU6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 25: the candle burns twice as long at night",
        "cm91bmQgMjU6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 25: a mirror of the universe in one line",
        "cm91bmQgMjU6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 25: the queue drains before the storm", "cm91bmQgMjU6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
