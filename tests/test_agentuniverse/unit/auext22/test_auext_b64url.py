"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten22kitten22", "a2l0dGVuMjJraXR0ZW4yMg"),
    ("kitten22sitting22", "a2l0dGVuMjJzaXR0aW5nMjI"),
    ("kitten22agent22", "a2l0dGVuMjJhZ2VudDIy"),
    ("kitten22angle22", "a2l0dGVuMjJhbmdsZTIy"),
    ("sitting22angle22", "c2l0dGluZzIyYW5nbGUyMg"),
    ("sitting22universe22", "c2l0dGluZzIydW5pdmVyc2UyMg"),
    ("sitting22memory22", "c2l0dGluZzIybWVtb3J5MjI"),
    ("sitting22stream22", "c2l0dGluZzIyc3RyZWFtMjI"),
    ("agent22stream22", "YWdlbnQyMnN0cmVhbTIy"),
    ("agent22context22", "YWdlbnQyMmNvbnRleHQyMg"),
    ("agent22knowledge22", "YWdlbnQyMmtub3dsZWRnZTIy"),
    ("agent22vector22", "YWdlbnQyMnZlY3RvcjIy"),
    ("angle22vector22", "YW5nbGUyMnZlY3RvcjIy"),
    ("angle22processor22", "YW5nbGUyMnByb2Nlc3NvcjIy"),
    ("angle22reasoning22", "YW5nbGUyMnJlYXNvbmluZzIy"),
    ("angle22machine22", "YW5nbGUyMm1hY2hpbmUyMg"),
    ("universe22machine22", "dW5pdmVyc2UyMm1hY2hpbmUyMg"),
    ("universe22learning22", "dW5pdmVyc2UyMmxlYXJuaW5nMjI"),
    ("universe22model22", "dW5pdmVyc2UyMm1vZGVsMjI"),
    ("universe22token22", "dW5pdmVyc2UyMnRva2VuMjI"),
    ("memory22token22", "bWVtb3J5MjJ0b2tlbjIy"),
    ("memory22prompt22", "bWVtb3J5MjJwcm9tcHQyMg"),
    ("memory22session22", "bWVtb3J5MjJzZXNzaW9uMjI"),
    ("memory22library22", "bWVtb3J5MjJsaWJyYXJ5MjI"),
    ("stream22library22", "c3RyZWFtMjJsaWJyYXJ5MjI"),
    ("stream22service22", "c3RyZWFtMjJzZXJ2aWNlMjI"),
    ("stream22gateway22", "c3RyZWFtMjJnYXRld2F5MjI"),
    ("stream22storage22", "c3RyZWFtMjJzdG9yYWdlMjI"),
    ("context22storage22", "Y29udGV4dDIyc3RvcmFnZTIy"),
    ("context22network22", "Y29udGV4dDIybmV0d29yazIy"),
    ("context22latency22", "Y29udGV4dDIybGF0ZW5jeTIy"),
    ("context22buffer22", "Y29udGV4dDIyYnVmZmVyMjI"),
    ("knowledge22buffer22", "a25vd2xlZGdlMjJidWZmZXIyMg"),
    ("knowledge22queue22", "a25vd2xlZGdlMjJxdWV1ZTIy"),
    ("knowledge22worker22", "a25vd2xlZGdlMjJ3b3JrZXIyMg"),
    ("knowledge22kernel22", "a25vd2xlZGdlMjJrZXJuZWwyMg"),
    ("vector22kernel22", "dmVjdG9yMjJrZXJuZWwyMg"),
    ("vector22signal22", "dmVjdG9yMjJzaWduYWwyMg"),
    ("vector22packet22", "dmVjdG9yMjJwYWNrZXQyMg"),
    ("vector22router22", "dmVjdG9yMjJyb3V0ZXIyMg"),
    ("processor22router22", "cHJvY2Vzc29yMjJyb3V0ZXIyMg"),
    ("processor22cluster22", "cHJvY2Vzc29yMjJjbHVzdGVyMjI"),
    ("processor22mirror22", "cHJvY2Vzc29yMjJtaXJyb3IyMg"),
    ("processor22filter22", "cHJvY2Vzc29yMjJmaWx0ZXIyMg"),
    ("reasoning22filter22", "cmVhc29uaW5nMjJmaWx0ZXIyMg"),
    ("reasoning22ranking22", "cmVhc29uaW5nMjJyYW5raW5nMjI"),
    ("reasoning22encoding22", "cmVhc29uaW5nMjJlbmNvZGluZzIy"),
    ("reasoning22mapping22", "cmVhc29uaW5nMjJtYXBwaW5nMjI"),
    ("machine22mapping22", "bWFjaGluZTIybWFwcGluZzIy"),
    ("machine22record22", "bWFjaGluZTIycmVjb3JkMjI"),
    ("machine22candle22", "bWFjaGluZTIyY2FuZGxlMjI"),
    ("machine22thread22", "bWFjaGluZTIydGhyZWFkMjI"),
    ("learning22thread22", "bGVhcm5pbmcyMnRocmVhZDIy"),
    ("learning22kitten22", "bGVhcm5pbmcyMmtpdHRlbjIy"),
    ("learning22sitting22", "bGVhcm5pbmcyMnNpdHRpbmcyMg"),
    ("learning22agent22", "bGVhcm5pbmcyMmFnZW50MjI"),
    ("model22agent22", "bW9kZWwyMmFnZW50MjI"),
    ("model22angle22", "bW9kZWwyMmFuZ2xlMjI"),
    ("model22universe22", "bW9kZWwyMnVuaXZlcnNlMjI"),
    ("model22memory22", "bW9kZWwyMm1lbW9yeTIy"),
    ("token22memory22", "dG9rZW4yMm1lbW9yeTIy"),
    ("token22stream22", "dG9rZW4yMnN0cmVhbTIy"),
    ("token22context22", "dG9rZW4yMmNvbnRleHQyMg"),
    ("token22knowledge22", "dG9rZW4yMmtub3dsZWRnZTIy"),
    ("prompt22knowledge22", "cHJvbXB0MjJrbm93bGVkZ2UyMg"),
    ("prompt22vector22", "cHJvbXB0MjJ2ZWN0b3IyMg"),
    ("prompt22processor22", "cHJvbXB0MjJwcm9jZXNzb3IyMg"),
    ("prompt22reasoning22", "cHJvbXB0MjJyZWFzb25pbmcyMg"),
    ("session22reasoning22", "c2Vzc2lvbjIycmVhc29uaW5nMjI"),
    ("session22machine22", "c2Vzc2lvbjIybWFjaGluZTIy"),
    ("session22learning22", "c2Vzc2lvbjIybGVhcm5pbmcyMg"),
    ("session22model22", "c2Vzc2lvbjIybW9kZWwyMg"),
    ("library22model22", "bGlicmFyeTIybW9kZWwyMg"),
    ("library22token22", "bGlicmFyeTIydG9rZW4yMg"),
    ("library22prompt22", "bGlicmFyeTIycHJvbXB0MjI"),
    ("library22session22", "bGlicmFyeTIyc2Vzc2lvbjIy"),
    ("service22session22", "c2VydmljZTIyc2Vzc2lvbjIy"),
    ("service22library22", "c2VydmljZTIybGlicmFyeTIy"),
    ("service22service22", "c2VydmljZTIyc2VydmljZTIy"),
    ("service22gateway22", "c2VydmljZTIyZ2F0ZXdheTIy"),
    ("gateway22gateway22", "Z2F0ZXdheTIyZ2F0ZXdheTIy"),
    ("gateway22storage22", "Z2F0ZXdheTIyc3RvcmFnZTIy"),
    ("gateway22network22", "Z2F0ZXdheTIybmV0d29yazIy"),
    ("gateway22latency22", "Z2F0ZXdheTIybGF0ZW5jeTIy"),
    ("storage22latency22", "c3RvcmFnZTIybGF0ZW5jeTIy"),
    ("storage22buffer22", "c3RvcmFnZTIyYnVmZmVyMjI"),
    ("storage22queue22", "c3RvcmFnZTIycXVldWUyMg"),
    ("storage22worker22", "c3RvcmFnZTIyd29ya2VyMjI"),
    ("network22worker22", "bmV0d29yazIyd29ya2VyMjI"),
    ("network22kernel22", "bmV0d29yazIya2VybmVsMjI"),
    ("network22signal22", "bmV0d29yazIyc2lnbmFsMjI"),
    ("network22packet22", "bmV0d29yazIycGFja2V0MjI"),
    ("latency22packet22", "bGF0ZW5jeTIycGFja2V0MjI"),
    ("latency22router22", "bGF0ZW5jeTIycm91dGVyMjI"),
    ("latency22cluster22", "bGF0ZW5jeTIyY2x1c3RlcjIy"),
    ("latency22mirror22", "bGF0ZW5jeTIybWlycm9yMjI"),
    ("buffer22mirror22", "YnVmZmVyMjJtaXJyb3IyMg"),
    ("buffer22filter22", "YnVmZmVyMjJmaWx0ZXIyMg"),
    ("buffer22ranking22", "YnVmZmVyMjJyYW5raW5nMjI"),
    ("buffer22encoding22", "YnVmZmVyMjJlbmNvZGluZzIy"),
    ("queue22encoding22", "cXVldWUyMmVuY29kaW5nMjI"),
    ("queue22mapping22", "cXVldWUyMm1hcHBpbmcyMg"),
    ("queue22record22", "cXVldWUyMnJlY29yZDIy"),
    ("queue22candle22", "cXVldWUyMmNhbmRsZTIy"),
    ("worker22candle22", "d29ya2VyMjJjYW5kbGUyMg"),
    ("worker22thread22", "d29ya2VyMjJ0aHJlYWQyMg"),
    ("worker22kitten22", "d29ya2VyMjJraXR0ZW4yMg"),
    ("worker22sitting22", "d29ya2VyMjJzaXR0aW5nMjI"),
    ("kernel22sitting22", "a2VybmVsMjJzaXR0aW5nMjI"),
    ("kernel22agent22", "a2VybmVsMjJhZ2VudDIy"),
    ("kernel22angle22", "a2VybmVsMjJhbmdsZTIy"),
    ("kernel22universe22", "a2VybmVsMjJ1bml2ZXJzZTIy"),
    ("signal22universe22", "c2lnbmFsMjJ1bml2ZXJzZTIy"),
    ("signal22memory22", "c2lnbmFsMjJtZW1vcnkyMg"),
    ("signal22stream22", "c2lnbmFsMjJzdHJlYW0yMg"),
    ("signal22context22", "c2lnbmFsMjJjb250ZXh0MjI"),
    ("packet22context22", "cGFja2V0MjJjb250ZXh0MjI"),
    ("packet22knowledge22", "cGFja2V0MjJrbm93bGVkZ2UyMg"),
    ("packet22vector22", "cGFja2V0MjJ2ZWN0b3IyMg"),
    ("packet22processor22", "cGFja2V0MjJwcm9jZXNzb3IyMg"),
    ("router22processor22", "cm91dGVyMjJwcm9jZXNzb3IyMg"),
    ("router22reasoning22", "cm91dGVyMjJyZWFzb25pbmcyMg"),
    ("router22machine22", "cm91dGVyMjJtYWNoaW5lMjI"),
    ("router22learning22", "cm91dGVyMjJsZWFybmluZzIy"),
    ("cluster22learning22", "Y2x1c3RlcjIybGVhcm5pbmcyMg"),
    ("cluster22model22", "Y2x1c3RlcjIybW9kZWwyMg"),
    ("cluster22token22", "Y2x1c3RlcjIydG9rZW4yMg"),
    ("cluster22prompt22", "Y2x1c3RlcjIycHJvbXB0MjI"),
    ("mirror22prompt22", "bWlycm9yMjJwcm9tcHQyMg"),
    ("mirror22session22", "bWlycm9yMjJzZXNzaW9uMjI"),
    ("mirror22library22", "bWlycm9yMjJsaWJyYXJ5MjI"),
    ("mirror22service22", "bWlycm9yMjJzZXJ2aWNlMjI"),
    ("filter22service22", "ZmlsdGVyMjJzZXJ2aWNlMjI"),
    ("filter22gateway22", "ZmlsdGVyMjJnYXRld2F5MjI"),
    ("filter22storage22", "ZmlsdGVyMjJzdG9yYWdlMjI"),
    ("filter22network22", "ZmlsdGVyMjJuZXR3b3JrMjI"),
    ("ranking22network22", "cmFua2luZzIybmV0d29yazIy"),
    ("ranking22latency22", "cmFua2luZzIybGF0ZW5jeTIy"),
    ("ranking22buffer22", "cmFua2luZzIyYnVmZmVyMjI"),
    ("ranking22queue22", "cmFua2luZzIycXVldWUyMg"),
    ("encoding22queue22", "ZW5jb2RpbmcyMnF1ZXVlMjI"),
    ("encoding22worker22", "ZW5jb2RpbmcyMndvcmtlcjIy"),
    ("encoding22kernel22", "ZW5jb2RpbmcyMmtlcm5lbDIy"),
    ("encoding22signal22", "ZW5jb2RpbmcyMnNpZ25hbDIy"),
    ("mapping22signal22", "bWFwcGluZzIyc2lnbmFsMjI"),
    ("mapping22packet22", "bWFwcGluZzIycGFja2V0MjI"),
    ("mapping22router22", "bWFwcGluZzIycm91dGVyMjI"),
    ("mapping22cluster22", "bWFwcGluZzIyY2x1c3RlcjIy"),
    ("record22cluster22", "cmVjb3JkMjJjbHVzdGVyMjI"),
    ("record22mirror22", "cmVjb3JkMjJtaXJyb3IyMg"),
    ("record22filter22", "cmVjb3JkMjJmaWx0ZXIyMg"),
    ("record22ranking22", "cmVjb3JkMjJyYW5raW5nMjI"),
    ("candle22ranking22", "Y2FuZGxlMjJyYW5raW5nMjI"),
    ("candle22encoding22", "Y2FuZGxlMjJlbmNvZGluZzIy"),
    ("candle22mapping22", "Y2FuZGxlMjJtYXBwaW5nMjI"),
    ("candle22record22", "Y2FuZGxlMjJyZWNvcmQyMg"),
    ("thread22record22", "dGhyZWFkMjJyZWNvcmQyMg"),
    ("thread22candle22", "dGhyZWFkMjJjYW5kbGUyMg"),
    ("thread22thread22", "dGhyZWFkMjJ0aHJlYWQyMg"),
    ("thread22kitten22", "dGhyZWFkMjJraXR0ZW4yMg"),
    (
        "round 22: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjI6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 22: agentuniverse is a framework for multi agents",
        "cm91bmQgMjI6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 22: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjI6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 22: the processor reads the record then stops",
        "cm91bmQgMjI6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 22: a worker pulls the next task from the queue",
        "cm91bmQgMjI6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 22: signals travel through the network layer",
        "cm91bmQgMjI6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 22: the gateway routes each request by policy",
        "cm91bmQgMjI6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 22: memory grows until the buffer is full",
        "cm91bmQgMjI6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 22: the cluster mirrors every packet twice",
        "cm91bmQgMjI6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 22: ranking uses tokens learned from the corpus",
        "cm91bmQgMjI6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 22: a long session ends when the candle dies",
        "cm91bmQgMjI6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 22: encode the prompt then map the result",
        "cm91bmQgMjI6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 22: the kernel wakes the worker at dawn", "cm91bmQgMjI6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 22: service latency drops after the patch",
        "cm91bmQgMjI6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 22: the library caches every vector it sees",
        "cm91bmQgMjI6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 22: agents argue then the debate resolves",
        "cm91bmQgMjI6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 22: the filter keeps only strong matches",
        "cm91bmQgMjI6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 22: the model answers with a short reply",
        "cm91bmQgMjI6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 22: the recorder stores the reasoning trace",
        "cm91bmQgMjI6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 22: the angel watches the processor run", "cm91bmQgMjI6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 22: angle of the vector decides the match",
        "cm91bmQgMjI6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 22: the candle burns twice as long at night",
        "cm91bmQgMjI6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 22: a mirror of the universe in one line",
        "cm91bmQgMjI6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 22: the queue drains before the storm", "cm91bmQgMjI6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
