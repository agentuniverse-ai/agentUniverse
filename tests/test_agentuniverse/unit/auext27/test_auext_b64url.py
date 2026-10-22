"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten27kitten27", "a2l0dGVuMjdraXR0ZW4yNw"),
    ("kitten27sitting27", "a2l0dGVuMjdzaXR0aW5nMjc"),
    ("kitten27agent27", "a2l0dGVuMjdhZ2VudDI3"),
    ("kitten27angle27", "a2l0dGVuMjdhbmdsZTI3"),
    ("sitting27angle27", "c2l0dGluZzI3YW5nbGUyNw"),
    ("sitting27universe27", "c2l0dGluZzI3dW5pdmVyc2UyNw"),
    ("sitting27memory27", "c2l0dGluZzI3bWVtb3J5Mjc"),
    ("sitting27stream27", "c2l0dGluZzI3c3RyZWFtMjc"),
    ("agent27stream27", "YWdlbnQyN3N0cmVhbTI3"),
    ("agent27context27", "YWdlbnQyN2NvbnRleHQyNw"),
    ("agent27knowledge27", "YWdlbnQyN2tub3dsZWRnZTI3"),
    ("agent27vector27", "YWdlbnQyN3ZlY3RvcjI3"),
    ("angle27vector27", "YW5nbGUyN3ZlY3RvcjI3"),
    ("angle27processor27", "YW5nbGUyN3Byb2Nlc3NvcjI3"),
    ("angle27reasoning27", "YW5nbGUyN3JlYXNvbmluZzI3"),
    ("angle27machine27", "YW5nbGUyN21hY2hpbmUyNw"),
    ("universe27machine27", "dW5pdmVyc2UyN21hY2hpbmUyNw"),
    ("universe27learning27", "dW5pdmVyc2UyN2xlYXJuaW5nMjc"),
    ("universe27model27", "dW5pdmVyc2UyN21vZGVsMjc"),
    ("universe27token27", "dW5pdmVyc2UyN3Rva2VuMjc"),
    ("memory27token27", "bWVtb3J5Mjd0b2tlbjI3"),
    ("memory27prompt27", "bWVtb3J5Mjdwcm9tcHQyNw"),
    ("memory27session27", "bWVtb3J5MjdzZXNzaW9uMjc"),
    ("memory27library27", "bWVtb3J5MjdsaWJyYXJ5Mjc"),
    ("stream27library27", "c3RyZWFtMjdsaWJyYXJ5Mjc"),
    ("stream27service27", "c3RyZWFtMjdzZXJ2aWNlMjc"),
    ("stream27gateway27", "c3RyZWFtMjdnYXRld2F5Mjc"),
    ("stream27storage27", "c3RyZWFtMjdzdG9yYWdlMjc"),
    ("context27storage27", "Y29udGV4dDI3c3RvcmFnZTI3"),
    ("context27network27", "Y29udGV4dDI3bmV0d29yazI3"),
    ("context27latency27", "Y29udGV4dDI3bGF0ZW5jeTI3"),
    ("context27buffer27", "Y29udGV4dDI3YnVmZmVyMjc"),
    ("knowledge27buffer27", "a25vd2xlZGdlMjdidWZmZXIyNw"),
    ("knowledge27queue27", "a25vd2xlZGdlMjdxdWV1ZTI3"),
    ("knowledge27worker27", "a25vd2xlZGdlMjd3b3JrZXIyNw"),
    ("knowledge27kernel27", "a25vd2xlZGdlMjdrZXJuZWwyNw"),
    ("vector27kernel27", "dmVjdG9yMjdrZXJuZWwyNw"),
    ("vector27signal27", "dmVjdG9yMjdzaWduYWwyNw"),
    ("vector27packet27", "dmVjdG9yMjdwYWNrZXQyNw"),
    ("vector27router27", "dmVjdG9yMjdyb3V0ZXIyNw"),
    ("processor27router27", "cHJvY2Vzc29yMjdyb3V0ZXIyNw"),
    ("processor27cluster27", "cHJvY2Vzc29yMjdjbHVzdGVyMjc"),
    ("processor27mirror27", "cHJvY2Vzc29yMjdtaXJyb3IyNw"),
    ("processor27filter27", "cHJvY2Vzc29yMjdmaWx0ZXIyNw"),
    ("reasoning27filter27", "cmVhc29uaW5nMjdmaWx0ZXIyNw"),
    ("reasoning27ranking27", "cmVhc29uaW5nMjdyYW5raW5nMjc"),
    ("reasoning27encoding27", "cmVhc29uaW5nMjdlbmNvZGluZzI3"),
    ("reasoning27mapping27", "cmVhc29uaW5nMjdtYXBwaW5nMjc"),
    ("machine27mapping27", "bWFjaGluZTI3bWFwcGluZzI3"),
    ("machine27record27", "bWFjaGluZTI3cmVjb3JkMjc"),
    ("machine27candle27", "bWFjaGluZTI3Y2FuZGxlMjc"),
    ("machine27thread27", "bWFjaGluZTI3dGhyZWFkMjc"),
    ("learning27thread27", "bGVhcm5pbmcyN3RocmVhZDI3"),
    ("learning27kitten27", "bGVhcm5pbmcyN2tpdHRlbjI3"),
    ("learning27sitting27", "bGVhcm5pbmcyN3NpdHRpbmcyNw"),
    ("learning27agent27", "bGVhcm5pbmcyN2FnZW50Mjc"),
    ("model27agent27", "bW9kZWwyN2FnZW50Mjc"),
    ("model27angle27", "bW9kZWwyN2FuZ2xlMjc"),
    ("model27universe27", "bW9kZWwyN3VuaXZlcnNlMjc"),
    ("model27memory27", "bW9kZWwyN21lbW9yeTI3"),
    ("token27memory27", "dG9rZW4yN21lbW9yeTI3"),
    ("token27stream27", "dG9rZW4yN3N0cmVhbTI3"),
    ("token27context27", "dG9rZW4yN2NvbnRleHQyNw"),
    ("token27knowledge27", "dG9rZW4yN2tub3dsZWRnZTI3"),
    ("prompt27knowledge27", "cHJvbXB0Mjdrbm93bGVkZ2UyNw"),
    ("prompt27vector27", "cHJvbXB0Mjd2ZWN0b3IyNw"),
    ("prompt27processor27", "cHJvbXB0Mjdwcm9jZXNzb3IyNw"),
    ("prompt27reasoning27", "cHJvbXB0MjdyZWFzb25pbmcyNw"),
    ("session27reasoning27", "c2Vzc2lvbjI3cmVhc29uaW5nMjc"),
    ("session27machine27", "c2Vzc2lvbjI3bWFjaGluZTI3"),
    ("session27learning27", "c2Vzc2lvbjI3bGVhcm5pbmcyNw"),
    ("session27model27", "c2Vzc2lvbjI3bW9kZWwyNw"),
    ("library27model27", "bGlicmFyeTI3bW9kZWwyNw"),
    ("library27token27", "bGlicmFyeTI3dG9rZW4yNw"),
    ("library27prompt27", "bGlicmFyeTI3cHJvbXB0Mjc"),
    ("library27session27", "bGlicmFyeTI3c2Vzc2lvbjI3"),
    ("service27session27", "c2VydmljZTI3c2Vzc2lvbjI3"),
    ("service27library27", "c2VydmljZTI3bGlicmFyeTI3"),
    ("service27service27", "c2VydmljZTI3c2VydmljZTI3"),
    ("service27gateway27", "c2VydmljZTI3Z2F0ZXdheTI3"),
    ("gateway27gateway27", "Z2F0ZXdheTI3Z2F0ZXdheTI3"),
    ("gateway27storage27", "Z2F0ZXdheTI3c3RvcmFnZTI3"),
    ("gateway27network27", "Z2F0ZXdheTI3bmV0d29yazI3"),
    ("gateway27latency27", "Z2F0ZXdheTI3bGF0ZW5jeTI3"),
    ("storage27latency27", "c3RvcmFnZTI3bGF0ZW5jeTI3"),
    ("storage27buffer27", "c3RvcmFnZTI3YnVmZmVyMjc"),
    ("storage27queue27", "c3RvcmFnZTI3cXVldWUyNw"),
    ("storage27worker27", "c3RvcmFnZTI3d29ya2VyMjc"),
    ("network27worker27", "bmV0d29yazI3d29ya2VyMjc"),
    ("network27kernel27", "bmV0d29yazI3a2VybmVsMjc"),
    ("network27signal27", "bmV0d29yazI3c2lnbmFsMjc"),
    ("network27packet27", "bmV0d29yazI3cGFja2V0Mjc"),
    ("latency27packet27", "bGF0ZW5jeTI3cGFja2V0Mjc"),
    ("latency27router27", "bGF0ZW5jeTI3cm91dGVyMjc"),
    ("latency27cluster27", "bGF0ZW5jeTI3Y2x1c3RlcjI3"),
    ("latency27mirror27", "bGF0ZW5jeTI3bWlycm9yMjc"),
    ("buffer27mirror27", "YnVmZmVyMjdtaXJyb3IyNw"),
    ("buffer27filter27", "YnVmZmVyMjdmaWx0ZXIyNw"),
    ("buffer27ranking27", "YnVmZmVyMjdyYW5raW5nMjc"),
    ("buffer27encoding27", "YnVmZmVyMjdlbmNvZGluZzI3"),
    ("queue27encoding27", "cXVldWUyN2VuY29kaW5nMjc"),
    ("queue27mapping27", "cXVldWUyN21hcHBpbmcyNw"),
    ("queue27record27", "cXVldWUyN3JlY29yZDI3"),
    ("queue27candle27", "cXVldWUyN2NhbmRsZTI3"),
    ("worker27candle27", "d29ya2VyMjdjYW5kbGUyNw"),
    ("worker27thread27", "d29ya2VyMjd0aHJlYWQyNw"),
    ("worker27kitten27", "d29ya2VyMjdraXR0ZW4yNw"),
    ("worker27sitting27", "d29ya2VyMjdzaXR0aW5nMjc"),
    ("kernel27sitting27", "a2VybmVsMjdzaXR0aW5nMjc"),
    ("kernel27agent27", "a2VybmVsMjdhZ2VudDI3"),
    ("kernel27angle27", "a2VybmVsMjdhbmdsZTI3"),
    ("kernel27universe27", "a2VybmVsMjd1bml2ZXJzZTI3"),
    ("signal27universe27", "c2lnbmFsMjd1bml2ZXJzZTI3"),
    ("signal27memory27", "c2lnbmFsMjdtZW1vcnkyNw"),
    ("signal27stream27", "c2lnbmFsMjdzdHJlYW0yNw"),
    ("signal27context27", "c2lnbmFsMjdjb250ZXh0Mjc"),
    ("packet27context27", "cGFja2V0Mjdjb250ZXh0Mjc"),
    ("packet27knowledge27", "cGFja2V0Mjdrbm93bGVkZ2UyNw"),
    ("packet27vector27", "cGFja2V0Mjd2ZWN0b3IyNw"),
    ("packet27processor27", "cGFja2V0Mjdwcm9jZXNzb3IyNw"),
    ("router27processor27", "cm91dGVyMjdwcm9jZXNzb3IyNw"),
    ("router27reasoning27", "cm91dGVyMjdyZWFzb25pbmcyNw"),
    ("router27machine27", "cm91dGVyMjdtYWNoaW5lMjc"),
    ("router27learning27", "cm91dGVyMjdsZWFybmluZzI3"),
    ("cluster27learning27", "Y2x1c3RlcjI3bGVhcm5pbmcyNw"),
    ("cluster27model27", "Y2x1c3RlcjI3bW9kZWwyNw"),
    ("cluster27token27", "Y2x1c3RlcjI3dG9rZW4yNw"),
    ("cluster27prompt27", "Y2x1c3RlcjI3cHJvbXB0Mjc"),
    ("mirror27prompt27", "bWlycm9yMjdwcm9tcHQyNw"),
    ("mirror27session27", "bWlycm9yMjdzZXNzaW9uMjc"),
    ("mirror27library27", "bWlycm9yMjdsaWJyYXJ5Mjc"),
    ("mirror27service27", "bWlycm9yMjdzZXJ2aWNlMjc"),
    ("filter27service27", "ZmlsdGVyMjdzZXJ2aWNlMjc"),
    ("filter27gateway27", "ZmlsdGVyMjdnYXRld2F5Mjc"),
    ("filter27storage27", "ZmlsdGVyMjdzdG9yYWdlMjc"),
    ("filter27network27", "ZmlsdGVyMjduZXR3b3JrMjc"),
    ("ranking27network27", "cmFua2luZzI3bmV0d29yazI3"),
    ("ranking27latency27", "cmFua2luZzI3bGF0ZW5jeTI3"),
    ("ranking27buffer27", "cmFua2luZzI3YnVmZmVyMjc"),
    ("ranking27queue27", "cmFua2luZzI3cXVldWUyNw"),
    ("encoding27queue27", "ZW5jb2RpbmcyN3F1ZXVlMjc"),
    ("encoding27worker27", "ZW5jb2RpbmcyN3dvcmtlcjI3"),
    ("encoding27kernel27", "ZW5jb2RpbmcyN2tlcm5lbDI3"),
    ("encoding27signal27", "ZW5jb2RpbmcyN3NpZ25hbDI3"),
    ("mapping27signal27", "bWFwcGluZzI3c2lnbmFsMjc"),
    ("mapping27packet27", "bWFwcGluZzI3cGFja2V0Mjc"),
    ("mapping27router27", "bWFwcGluZzI3cm91dGVyMjc"),
    ("mapping27cluster27", "bWFwcGluZzI3Y2x1c3RlcjI3"),
    ("record27cluster27", "cmVjb3JkMjdjbHVzdGVyMjc"),
    ("record27mirror27", "cmVjb3JkMjdtaXJyb3IyNw"),
    ("record27filter27", "cmVjb3JkMjdmaWx0ZXIyNw"),
    ("record27ranking27", "cmVjb3JkMjdyYW5raW5nMjc"),
    ("candle27ranking27", "Y2FuZGxlMjdyYW5raW5nMjc"),
    ("candle27encoding27", "Y2FuZGxlMjdlbmNvZGluZzI3"),
    ("candle27mapping27", "Y2FuZGxlMjdtYXBwaW5nMjc"),
    ("candle27record27", "Y2FuZGxlMjdyZWNvcmQyNw"),
    ("thread27record27", "dGhyZWFkMjdyZWNvcmQyNw"),
    ("thread27candle27", "dGhyZWFkMjdjYW5kbGUyNw"),
    ("thread27thread27", "dGhyZWFkMjd0aHJlYWQyNw"),
    ("thread27kitten27", "dGhyZWFkMjdraXR0ZW4yNw"),
    (
        "round 27: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjc6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 27: agentuniverse is a framework for multi agents",
        "cm91bmQgMjc6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 27: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjc6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 27: the processor reads the record then stops",
        "cm91bmQgMjc6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 27: a worker pulls the next task from the queue",
        "cm91bmQgMjc6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 27: signals travel through the network layer",
        "cm91bmQgMjc6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 27: the gateway routes each request by policy",
        "cm91bmQgMjc6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 27: memory grows until the buffer is full",
        "cm91bmQgMjc6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 27: the cluster mirrors every packet twice",
        "cm91bmQgMjc6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 27: ranking uses tokens learned from the corpus",
        "cm91bmQgMjc6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 27: a long session ends when the candle dies",
        "cm91bmQgMjc6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 27: encode the prompt then map the result",
        "cm91bmQgMjc6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 27: the kernel wakes the worker at dawn", "cm91bmQgMjc6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 27: service latency drops after the patch",
        "cm91bmQgMjc6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 27: the library caches every vector it sees",
        "cm91bmQgMjc6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 27: agents argue then the debate resolves",
        "cm91bmQgMjc6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 27: the filter keeps only strong matches",
        "cm91bmQgMjc6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 27: the model answers with a short reply",
        "cm91bmQgMjc6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 27: the recorder stores the reasoning trace",
        "cm91bmQgMjc6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 27: the angel watches the processor run", "cm91bmQgMjc6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 27: angle of the vector decides the match",
        "cm91bmQgMjc6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 27: the candle burns twice as long at night",
        "cm91bmQgMjc6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 27: a mirror of the universe in one line",
        "cm91bmQgMjc6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 27: the queue drains before the storm", "cm91bmQgMjc6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
