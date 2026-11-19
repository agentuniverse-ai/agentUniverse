"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten21kitten21", "a2l0dGVuMjFraXR0ZW4yMQ"),
    ("kitten21sitting21", "a2l0dGVuMjFzaXR0aW5nMjE"),
    ("kitten21agent21", "a2l0dGVuMjFhZ2VudDIx"),
    ("kitten21angle21", "a2l0dGVuMjFhbmdsZTIx"),
    ("sitting21angle21", "c2l0dGluZzIxYW5nbGUyMQ"),
    ("sitting21universe21", "c2l0dGluZzIxdW5pdmVyc2UyMQ"),
    ("sitting21memory21", "c2l0dGluZzIxbWVtb3J5MjE"),
    ("sitting21stream21", "c2l0dGluZzIxc3RyZWFtMjE"),
    ("agent21stream21", "YWdlbnQyMXN0cmVhbTIx"),
    ("agent21context21", "YWdlbnQyMWNvbnRleHQyMQ"),
    ("agent21knowledge21", "YWdlbnQyMWtub3dsZWRnZTIx"),
    ("agent21vector21", "YWdlbnQyMXZlY3RvcjIx"),
    ("angle21vector21", "YW5nbGUyMXZlY3RvcjIx"),
    ("angle21processor21", "YW5nbGUyMXByb2Nlc3NvcjIx"),
    ("angle21reasoning21", "YW5nbGUyMXJlYXNvbmluZzIx"),
    ("angle21machine21", "YW5nbGUyMW1hY2hpbmUyMQ"),
    ("universe21machine21", "dW5pdmVyc2UyMW1hY2hpbmUyMQ"),
    ("universe21learning21", "dW5pdmVyc2UyMWxlYXJuaW5nMjE"),
    ("universe21model21", "dW5pdmVyc2UyMW1vZGVsMjE"),
    ("universe21token21", "dW5pdmVyc2UyMXRva2VuMjE"),
    ("memory21token21", "bWVtb3J5MjF0b2tlbjIx"),
    ("memory21prompt21", "bWVtb3J5MjFwcm9tcHQyMQ"),
    ("memory21session21", "bWVtb3J5MjFzZXNzaW9uMjE"),
    ("memory21library21", "bWVtb3J5MjFsaWJyYXJ5MjE"),
    ("stream21library21", "c3RyZWFtMjFsaWJyYXJ5MjE"),
    ("stream21service21", "c3RyZWFtMjFzZXJ2aWNlMjE"),
    ("stream21gateway21", "c3RyZWFtMjFnYXRld2F5MjE"),
    ("stream21storage21", "c3RyZWFtMjFzdG9yYWdlMjE"),
    ("context21storage21", "Y29udGV4dDIxc3RvcmFnZTIx"),
    ("context21network21", "Y29udGV4dDIxbmV0d29yazIx"),
    ("context21latency21", "Y29udGV4dDIxbGF0ZW5jeTIx"),
    ("context21buffer21", "Y29udGV4dDIxYnVmZmVyMjE"),
    ("knowledge21buffer21", "a25vd2xlZGdlMjFidWZmZXIyMQ"),
    ("knowledge21queue21", "a25vd2xlZGdlMjFxdWV1ZTIx"),
    ("knowledge21worker21", "a25vd2xlZGdlMjF3b3JrZXIyMQ"),
    ("knowledge21kernel21", "a25vd2xlZGdlMjFrZXJuZWwyMQ"),
    ("vector21kernel21", "dmVjdG9yMjFrZXJuZWwyMQ"),
    ("vector21signal21", "dmVjdG9yMjFzaWduYWwyMQ"),
    ("vector21packet21", "dmVjdG9yMjFwYWNrZXQyMQ"),
    ("vector21router21", "dmVjdG9yMjFyb3V0ZXIyMQ"),
    ("processor21router21", "cHJvY2Vzc29yMjFyb3V0ZXIyMQ"),
    ("processor21cluster21", "cHJvY2Vzc29yMjFjbHVzdGVyMjE"),
    ("processor21mirror21", "cHJvY2Vzc29yMjFtaXJyb3IyMQ"),
    ("processor21filter21", "cHJvY2Vzc29yMjFmaWx0ZXIyMQ"),
    ("reasoning21filter21", "cmVhc29uaW5nMjFmaWx0ZXIyMQ"),
    ("reasoning21ranking21", "cmVhc29uaW5nMjFyYW5raW5nMjE"),
    ("reasoning21encoding21", "cmVhc29uaW5nMjFlbmNvZGluZzIx"),
    ("reasoning21mapping21", "cmVhc29uaW5nMjFtYXBwaW5nMjE"),
    ("machine21mapping21", "bWFjaGluZTIxbWFwcGluZzIx"),
    ("machine21record21", "bWFjaGluZTIxcmVjb3JkMjE"),
    ("machine21candle21", "bWFjaGluZTIxY2FuZGxlMjE"),
    ("machine21thread21", "bWFjaGluZTIxdGhyZWFkMjE"),
    ("learning21thread21", "bGVhcm5pbmcyMXRocmVhZDIx"),
    ("learning21kitten21", "bGVhcm5pbmcyMWtpdHRlbjIx"),
    ("learning21sitting21", "bGVhcm5pbmcyMXNpdHRpbmcyMQ"),
    ("learning21agent21", "bGVhcm5pbmcyMWFnZW50MjE"),
    ("model21agent21", "bW9kZWwyMWFnZW50MjE"),
    ("model21angle21", "bW9kZWwyMWFuZ2xlMjE"),
    ("model21universe21", "bW9kZWwyMXVuaXZlcnNlMjE"),
    ("model21memory21", "bW9kZWwyMW1lbW9yeTIx"),
    ("token21memory21", "dG9rZW4yMW1lbW9yeTIx"),
    ("token21stream21", "dG9rZW4yMXN0cmVhbTIx"),
    ("token21context21", "dG9rZW4yMWNvbnRleHQyMQ"),
    ("token21knowledge21", "dG9rZW4yMWtub3dsZWRnZTIx"),
    ("prompt21knowledge21", "cHJvbXB0MjFrbm93bGVkZ2UyMQ"),
    ("prompt21vector21", "cHJvbXB0MjF2ZWN0b3IyMQ"),
    ("prompt21processor21", "cHJvbXB0MjFwcm9jZXNzb3IyMQ"),
    ("prompt21reasoning21", "cHJvbXB0MjFyZWFzb25pbmcyMQ"),
    ("session21reasoning21", "c2Vzc2lvbjIxcmVhc29uaW5nMjE"),
    ("session21machine21", "c2Vzc2lvbjIxbWFjaGluZTIx"),
    ("session21learning21", "c2Vzc2lvbjIxbGVhcm5pbmcyMQ"),
    ("session21model21", "c2Vzc2lvbjIxbW9kZWwyMQ"),
    ("library21model21", "bGlicmFyeTIxbW9kZWwyMQ"),
    ("library21token21", "bGlicmFyeTIxdG9rZW4yMQ"),
    ("library21prompt21", "bGlicmFyeTIxcHJvbXB0MjE"),
    ("library21session21", "bGlicmFyeTIxc2Vzc2lvbjIx"),
    ("service21session21", "c2VydmljZTIxc2Vzc2lvbjIx"),
    ("service21library21", "c2VydmljZTIxbGlicmFyeTIx"),
    ("service21service21", "c2VydmljZTIxc2VydmljZTIx"),
    ("service21gateway21", "c2VydmljZTIxZ2F0ZXdheTIx"),
    ("gateway21gateway21", "Z2F0ZXdheTIxZ2F0ZXdheTIx"),
    ("gateway21storage21", "Z2F0ZXdheTIxc3RvcmFnZTIx"),
    ("gateway21network21", "Z2F0ZXdheTIxbmV0d29yazIx"),
    ("gateway21latency21", "Z2F0ZXdheTIxbGF0ZW5jeTIx"),
    ("storage21latency21", "c3RvcmFnZTIxbGF0ZW5jeTIx"),
    ("storage21buffer21", "c3RvcmFnZTIxYnVmZmVyMjE"),
    ("storage21queue21", "c3RvcmFnZTIxcXVldWUyMQ"),
    ("storage21worker21", "c3RvcmFnZTIxd29ya2VyMjE"),
    ("network21worker21", "bmV0d29yazIxd29ya2VyMjE"),
    ("network21kernel21", "bmV0d29yazIxa2VybmVsMjE"),
    ("network21signal21", "bmV0d29yazIxc2lnbmFsMjE"),
    ("network21packet21", "bmV0d29yazIxcGFja2V0MjE"),
    ("latency21packet21", "bGF0ZW5jeTIxcGFja2V0MjE"),
    ("latency21router21", "bGF0ZW5jeTIxcm91dGVyMjE"),
    ("latency21cluster21", "bGF0ZW5jeTIxY2x1c3RlcjIx"),
    ("latency21mirror21", "bGF0ZW5jeTIxbWlycm9yMjE"),
    ("buffer21mirror21", "YnVmZmVyMjFtaXJyb3IyMQ"),
    ("buffer21filter21", "YnVmZmVyMjFmaWx0ZXIyMQ"),
    ("buffer21ranking21", "YnVmZmVyMjFyYW5raW5nMjE"),
    ("buffer21encoding21", "YnVmZmVyMjFlbmNvZGluZzIx"),
    ("queue21encoding21", "cXVldWUyMWVuY29kaW5nMjE"),
    ("queue21mapping21", "cXVldWUyMW1hcHBpbmcyMQ"),
    ("queue21record21", "cXVldWUyMXJlY29yZDIx"),
    ("queue21candle21", "cXVldWUyMWNhbmRsZTIx"),
    ("worker21candle21", "d29ya2VyMjFjYW5kbGUyMQ"),
    ("worker21thread21", "d29ya2VyMjF0aHJlYWQyMQ"),
    ("worker21kitten21", "d29ya2VyMjFraXR0ZW4yMQ"),
    ("worker21sitting21", "d29ya2VyMjFzaXR0aW5nMjE"),
    ("kernel21sitting21", "a2VybmVsMjFzaXR0aW5nMjE"),
    ("kernel21agent21", "a2VybmVsMjFhZ2VudDIx"),
    ("kernel21angle21", "a2VybmVsMjFhbmdsZTIx"),
    ("kernel21universe21", "a2VybmVsMjF1bml2ZXJzZTIx"),
    ("signal21universe21", "c2lnbmFsMjF1bml2ZXJzZTIx"),
    ("signal21memory21", "c2lnbmFsMjFtZW1vcnkyMQ"),
    ("signal21stream21", "c2lnbmFsMjFzdHJlYW0yMQ"),
    ("signal21context21", "c2lnbmFsMjFjb250ZXh0MjE"),
    ("packet21context21", "cGFja2V0MjFjb250ZXh0MjE"),
    ("packet21knowledge21", "cGFja2V0MjFrbm93bGVkZ2UyMQ"),
    ("packet21vector21", "cGFja2V0MjF2ZWN0b3IyMQ"),
    ("packet21processor21", "cGFja2V0MjFwcm9jZXNzb3IyMQ"),
    ("router21processor21", "cm91dGVyMjFwcm9jZXNzb3IyMQ"),
    ("router21reasoning21", "cm91dGVyMjFyZWFzb25pbmcyMQ"),
    ("router21machine21", "cm91dGVyMjFtYWNoaW5lMjE"),
    ("router21learning21", "cm91dGVyMjFsZWFybmluZzIx"),
    ("cluster21learning21", "Y2x1c3RlcjIxbGVhcm5pbmcyMQ"),
    ("cluster21model21", "Y2x1c3RlcjIxbW9kZWwyMQ"),
    ("cluster21token21", "Y2x1c3RlcjIxdG9rZW4yMQ"),
    ("cluster21prompt21", "Y2x1c3RlcjIxcHJvbXB0MjE"),
    ("mirror21prompt21", "bWlycm9yMjFwcm9tcHQyMQ"),
    ("mirror21session21", "bWlycm9yMjFzZXNzaW9uMjE"),
    ("mirror21library21", "bWlycm9yMjFsaWJyYXJ5MjE"),
    ("mirror21service21", "bWlycm9yMjFzZXJ2aWNlMjE"),
    ("filter21service21", "ZmlsdGVyMjFzZXJ2aWNlMjE"),
    ("filter21gateway21", "ZmlsdGVyMjFnYXRld2F5MjE"),
    ("filter21storage21", "ZmlsdGVyMjFzdG9yYWdlMjE"),
    ("filter21network21", "ZmlsdGVyMjFuZXR3b3JrMjE"),
    ("ranking21network21", "cmFua2luZzIxbmV0d29yazIx"),
    ("ranking21latency21", "cmFua2luZzIxbGF0ZW5jeTIx"),
    ("ranking21buffer21", "cmFua2luZzIxYnVmZmVyMjE"),
    ("ranking21queue21", "cmFua2luZzIxcXVldWUyMQ"),
    ("encoding21queue21", "ZW5jb2RpbmcyMXF1ZXVlMjE"),
    ("encoding21worker21", "ZW5jb2RpbmcyMXdvcmtlcjIx"),
    ("encoding21kernel21", "ZW5jb2RpbmcyMWtlcm5lbDIx"),
    ("encoding21signal21", "ZW5jb2RpbmcyMXNpZ25hbDIx"),
    ("mapping21signal21", "bWFwcGluZzIxc2lnbmFsMjE"),
    ("mapping21packet21", "bWFwcGluZzIxcGFja2V0MjE"),
    ("mapping21router21", "bWFwcGluZzIxcm91dGVyMjE"),
    ("mapping21cluster21", "bWFwcGluZzIxY2x1c3RlcjIx"),
    ("record21cluster21", "cmVjb3JkMjFjbHVzdGVyMjE"),
    ("record21mirror21", "cmVjb3JkMjFtaXJyb3IyMQ"),
    ("record21filter21", "cmVjb3JkMjFmaWx0ZXIyMQ"),
    ("record21ranking21", "cmVjb3JkMjFyYW5raW5nMjE"),
    ("candle21ranking21", "Y2FuZGxlMjFyYW5raW5nMjE"),
    ("candle21encoding21", "Y2FuZGxlMjFlbmNvZGluZzIx"),
    ("candle21mapping21", "Y2FuZGxlMjFtYXBwaW5nMjE"),
    ("candle21record21", "Y2FuZGxlMjFyZWNvcmQyMQ"),
    ("thread21record21", "dGhyZWFkMjFyZWNvcmQyMQ"),
    ("thread21candle21", "dGhyZWFkMjFjYW5kbGUyMQ"),
    ("thread21thread21", "dGhyZWFkMjF0aHJlYWQyMQ"),
    ("thread21kitten21", "dGhyZWFkMjFraXR0ZW4yMQ"),
    (
        "round 21: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjE6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 21: agentuniverse is a framework for multi agents",
        "cm91bmQgMjE6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 21: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjE6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 21: the processor reads the record then stops",
        "cm91bmQgMjE6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 21: a worker pulls the next task from the queue",
        "cm91bmQgMjE6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 21: signals travel through the network layer",
        "cm91bmQgMjE6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 21: the gateway routes each request by policy",
        "cm91bmQgMjE6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 21: memory grows until the buffer is full",
        "cm91bmQgMjE6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 21: the cluster mirrors every packet twice",
        "cm91bmQgMjE6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 21: ranking uses tokens learned from the corpus",
        "cm91bmQgMjE6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 21: a long session ends when the candle dies",
        "cm91bmQgMjE6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 21: encode the prompt then map the result",
        "cm91bmQgMjE6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 21: the kernel wakes the worker at dawn", "cm91bmQgMjE6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 21: service latency drops after the patch",
        "cm91bmQgMjE6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 21: the library caches every vector it sees",
        "cm91bmQgMjE6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 21: agents argue then the debate resolves",
        "cm91bmQgMjE6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 21: the filter keeps only strong matches",
        "cm91bmQgMjE6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 21: the model answers with a short reply",
        "cm91bmQgMjE6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 21: the recorder stores the reasoning trace",
        "cm91bmQgMjE6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 21: the angel watches the processor run", "cm91bmQgMjE6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 21: angle of the vector decides the match",
        "cm91bmQgMjE6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 21: the candle burns twice as long at night",
        "cm91bmQgMjE6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 21: a mirror of the universe in one line",
        "cm91bmQgMjE6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 21: the queue drains before the storm", "cm91bmQgMjE6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
