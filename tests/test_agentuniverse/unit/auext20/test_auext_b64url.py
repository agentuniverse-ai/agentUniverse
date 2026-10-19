"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten20kitten20", "a2l0dGVuMjBraXR0ZW4yMA"),
    ("kitten20sitting20", "a2l0dGVuMjBzaXR0aW5nMjA"),
    ("kitten20agent20", "a2l0dGVuMjBhZ2VudDIw"),
    ("kitten20angle20", "a2l0dGVuMjBhbmdsZTIw"),
    ("sitting20angle20", "c2l0dGluZzIwYW5nbGUyMA"),
    ("sitting20universe20", "c2l0dGluZzIwdW5pdmVyc2UyMA"),
    ("sitting20memory20", "c2l0dGluZzIwbWVtb3J5MjA"),
    ("sitting20stream20", "c2l0dGluZzIwc3RyZWFtMjA"),
    ("agent20stream20", "YWdlbnQyMHN0cmVhbTIw"),
    ("agent20context20", "YWdlbnQyMGNvbnRleHQyMA"),
    ("agent20knowledge20", "YWdlbnQyMGtub3dsZWRnZTIw"),
    ("agent20vector20", "YWdlbnQyMHZlY3RvcjIw"),
    ("angle20vector20", "YW5nbGUyMHZlY3RvcjIw"),
    ("angle20processor20", "YW5nbGUyMHByb2Nlc3NvcjIw"),
    ("angle20reasoning20", "YW5nbGUyMHJlYXNvbmluZzIw"),
    ("angle20machine20", "YW5nbGUyMG1hY2hpbmUyMA"),
    ("universe20machine20", "dW5pdmVyc2UyMG1hY2hpbmUyMA"),
    ("universe20learning20", "dW5pdmVyc2UyMGxlYXJuaW5nMjA"),
    ("universe20model20", "dW5pdmVyc2UyMG1vZGVsMjA"),
    ("universe20token20", "dW5pdmVyc2UyMHRva2VuMjA"),
    ("memory20token20", "bWVtb3J5MjB0b2tlbjIw"),
    ("memory20prompt20", "bWVtb3J5MjBwcm9tcHQyMA"),
    ("memory20session20", "bWVtb3J5MjBzZXNzaW9uMjA"),
    ("memory20library20", "bWVtb3J5MjBsaWJyYXJ5MjA"),
    ("stream20library20", "c3RyZWFtMjBsaWJyYXJ5MjA"),
    ("stream20service20", "c3RyZWFtMjBzZXJ2aWNlMjA"),
    ("stream20gateway20", "c3RyZWFtMjBnYXRld2F5MjA"),
    ("stream20storage20", "c3RyZWFtMjBzdG9yYWdlMjA"),
    ("context20storage20", "Y29udGV4dDIwc3RvcmFnZTIw"),
    ("context20network20", "Y29udGV4dDIwbmV0d29yazIw"),
    ("context20latency20", "Y29udGV4dDIwbGF0ZW5jeTIw"),
    ("context20buffer20", "Y29udGV4dDIwYnVmZmVyMjA"),
    ("knowledge20buffer20", "a25vd2xlZGdlMjBidWZmZXIyMA"),
    ("knowledge20queue20", "a25vd2xlZGdlMjBxdWV1ZTIw"),
    ("knowledge20worker20", "a25vd2xlZGdlMjB3b3JrZXIyMA"),
    ("knowledge20kernel20", "a25vd2xlZGdlMjBrZXJuZWwyMA"),
    ("vector20kernel20", "dmVjdG9yMjBrZXJuZWwyMA"),
    ("vector20signal20", "dmVjdG9yMjBzaWduYWwyMA"),
    ("vector20packet20", "dmVjdG9yMjBwYWNrZXQyMA"),
    ("vector20router20", "dmVjdG9yMjByb3V0ZXIyMA"),
    ("processor20router20", "cHJvY2Vzc29yMjByb3V0ZXIyMA"),
    ("processor20cluster20", "cHJvY2Vzc29yMjBjbHVzdGVyMjA"),
    ("processor20mirror20", "cHJvY2Vzc29yMjBtaXJyb3IyMA"),
    ("processor20filter20", "cHJvY2Vzc29yMjBmaWx0ZXIyMA"),
    ("reasoning20filter20", "cmVhc29uaW5nMjBmaWx0ZXIyMA"),
    ("reasoning20ranking20", "cmVhc29uaW5nMjByYW5raW5nMjA"),
    ("reasoning20encoding20", "cmVhc29uaW5nMjBlbmNvZGluZzIw"),
    ("reasoning20mapping20", "cmVhc29uaW5nMjBtYXBwaW5nMjA"),
    ("machine20mapping20", "bWFjaGluZTIwbWFwcGluZzIw"),
    ("machine20record20", "bWFjaGluZTIwcmVjb3JkMjA"),
    ("machine20candle20", "bWFjaGluZTIwY2FuZGxlMjA"),
    ("machine20thread20", "bWFjaGluZTIwdGhyZWFkMjA"),
    ("learning20thread20", "bGVhcm5pbmcyMHRocmVhZDIw"),
    ("learning20kitten20", "bGVhcm5pbmcyMGtpdHRlbjIw"),
    ("learning20sitting20", "bGVhcm5pbmcyMHNpdHRpbmcyMA"),
    ("learning20agent20", "bGVhcm5pbmcyMGFnZW50MjA"),
    ("model20agent20", "bW9kZWwyMGFnZW50MjA"),
    ("model20angle20", "bW9kZWwyMGFuZ2xlMjA"),
    ("model20universe20", "bW9kZWwyMHVuaXZlcnNlMjA"),
    ("model20memory20", "bW9kZWwyMG1lbW9yeTIw"),
    ("token20memory20", "dG9rZW4yMG1lbW9yeTIw"),
    ("token20stream20", "dG9rZW4yMHN0cmVhbTIw"),
    ("token20context20", "dG9rZW4yMGNvbnRleHQyMA"),
    ("token20knowledge20", "dG9rZW4yMGtub3dsZWRnZTIw"),
    ("prompt20knowledge20", "cHJvbXB0MjBrbm93bGVkZ2UyMA"),
    ("prompt20vector20", "cHJvbXB0MjB2ZWN0b3IyMA"),
    ("prompt20processor20", "cHJvbXB0MjBwcm9jZXNzb3IyMA"),
    ("prompt20reasoning20", "cHJvbXB0MjByZWFzb25pbmcyMA"),
    ("session20reasoning20", "c2Vzc2lvbjIwcmVhc29uaW5nMjA"),
    ("session20machine20", "c2Vzc2lvbjIwbWFjaGluZTIw"),
    ("session20learning20", "c2Vzc2lvbjIwbGVhcm5pbmcyMA"),
    ("session20model20", "c2Vzc2lvbjIwbW9kZWwyMA"),
    ("library20model20", "bGlicmFyeTIwbW9kZWwyMA"),
    ("library20token20", "bGlicmFyeTIwdG9rZW4yMA"),
    ("library20prompt20", "bGlicmFyeTIwcHJvbXB0MjA"),
    ("library20session20", "bGlicmFyeTIwc2Vzc2lvbjIw"),
    ("service20session20", "c2VydmljZTIwc2Vzc2lvbjIw"),
    ("service20library20", "c2VydmljZTIwbGlicmFyeTIw"),
    ("service20service20", "c2VydmljZTIwc2VydmljZTIw"),
    ("service20gateway20", "c2VydmljZTIwZ2F0ZXdheTIw"),
    ("gateway20gateway20", "Z2F0ZXdheTIwZ2F0ZXdheTIw"),
    ("gateway20storage20", "Z2F0ZXdheTIwc3RvcmFnZTIw"),
    ("gateway20network20", "Z2F0ZXdheTIwbmV0d29yazIw"),
    ("gateway20latency20", "Z2F0ZXdheTIwbGF0ZW5jeTIw"),
    ("storage20latency20", "c3RvcmFnZTIwbGF0ZW5jeTIw"),
    ("storage20buffer20", "c3RvcmFnZTIwYnVmZmVyMjA"),
    ("storage20queue20", "c3RvcmFnZTIwcXVldWUyMA"),
    ("storage20worker20", "c3RvcmFnZTIwd29ya2VyMjA"),
    ("network20worker20", "bmV0d29yazIwd29ya2VyMjA"),
    ("network20kernel20", "bmV0d29yazIwa2VybmVsMjA"),
    ("network20signal20", "bmV0d29yazIwc2lnbmFsMjA"),
    ("network20packet20", "bmV0d29yazIwcGFja2V0MjA"),
    ("latency20packet20", "bGF0ZW5jeTIwcGFja2V0MjA"),
    ("latency20router20", "bGF0ZW5jeTIwcm91dGVyMjA"),
    ("latency20cluster20", "bGF0ZW5jeTIwY2x1c3RlcjIw"),
    ("latency20mirror20", "bGF0ZW5jeTIwbWlycm9yMjA"),
    ("buffer20mirror20", "YnVmZmVyMjBtaXJyb3IyMA"),
    ("buffer20filter20", "YnVmZmVyMjBmaWx0ZXIyMA"),
    ("buffer20ranking20", "YnVmZmVyMjByYW5raW5nMjA"),
    ("buffer20encoding20", "YnVmZmVyMjBlbmNvZGluZzIw"),
    ("queue20encoding20", "cXVldWUyMGVuY29kaW5nMjA"),
    ("queue20mapping20", "cXVldWUyMG1hcHBpbmcyMA"),
    ("queue20record20", "cXVldWUyMHJlY29yZDIw"),
    ("queue20candle20", "cXVldWUyMGNhbmRsZTIw"),
    ("worker20candle20", "d29ya2VyMjBjYW5kbGUyMA"),
    ("worker20thread20", "d29ya2VyMjB0aHJlYWQyMA"),
    ("worker20kitten20", "d29ya2VyMjBraXR0ZW4yMA"),
    ("worker20sitting20", "d29ya2VyMjBzaXR0aW5nMjA"),
    ("kernel20sitting20", "a2VybmVsMjBzaXR0aW5nMjA"),
    ("kernel20agent20", "a2VybmVsMjBhZ2VudDIw"),
    ("kernel20angle20", "a2VybmVsMjBhbmdsZTIw"),
    ("kernel20universe20", "a2VybmVsMjB1bml2ZXJzZTIw"),
    ("signal20universe20", "c2lnbmFsMjB1bml2ZXJzZTIw"),
    ("signal20memory20", "c2lnbmFsMjBtZW1vcnkyMA"),
    ("signal20stream20", "c2lnbmFsMjBzdHJlYW0yMA"),
    ("signal20context20", "c2lnbmFsMjBjb250ZXh0MjA"),
    ("packet20context20", "cGFja2V0MjBjb250ZXh0MjA"),
    ("packet20knowledge20", "cGFja2V0MjBrbm93bGVkZ2UyMA"),
    ("packet20vector20", "cGFja2V0MjB2ZWN0b3IyMA"),
    ("packet20processor20", "cGFja2V0MjBwcm9jZXNzb3IyMA"),
    ("router20processor20", "cm91dGVyMjBwcm9jZXNzb3IyMA"),
    ("router20reasoning20", "cm91dGVyMjByZWFzb25pbmcyMA"),
    ("router20machine20", "cm91dGVyMjBtYWNoaW5lMjA"),
    ("router20learning20", "cm91dGVyMjBsZWFybmluZzIw"),
    ("cluster20learning20", "Y2x1c3RlcjIwbGVhcm5pbmcyMA"),
    ("cluster20model20", "Y2x1c3RlcjIwbW9kZWwyMA"),
    ("cluster20token20", "Y2x1c3RlcjIwdG9rZW4yMA"),
    ("cluster20prompt20", "Y2x1c3RlcjIwcHJvbXB0MjA"),
    ("mirror20prompt20", "bWlycm9yMjBwcm9tcHQyMA"),
    ("mirror20session20", "bWlycm9yMjBzZXNzaW9uMjA"),
    ("mirror20library20", "bWlycm9yMjBsaWJyYXJ5MjA"),
    ("mirror20service20", "bWlycm9yMjBzZXJ2aWNlMjA"),
    ("filter20service20", "ZmlsdGVyMjBzZXJ2aWNlMjA"),
    ("filter20gateway20", "ZmlsdGVyMjBnYXRld2F5MjA"),
    ("filter20storage20", "ZmlsdGVyMjBzdG9yYWdlMjA"),
    ("filter20network20", "ZmlsdGVyMjBuZXR3b3JrMjA"),
    ("ranking20network20", "cmFua2luZzIwbmV0d29yazIw"),
    ("ranking20latency20", "cmFua2luZzIwbGF0ZW5jeTIw"),
    ("ranking20buffer20", "cmFua2luZzIwYnVmZmVyMjA"),
    ("ranking20queue20", "cmFua2luZzIwcXVldWUyMA"),
    ("encoding20queue20", "ZW5jb2RpbmcyMHF1ZXVlMjA"),
    ("encoding20worker20", "ZW5jb2RpbmcyMHdvcmtlcjIw"),
    ("encoding20kernel20", "ZW5jb2RpbmcyMGtlcm5lbDIw"),
    ("encoding20signal20", "ZW5jb2RpbmcyMHNpZ25hbDIw"),
    ("mapping20signal20", "bWFwcGluZzIwc2lnbmFsMjA"),
    ("mapping20packet20", "bWFwcGluZzIwcGFja2V0MjA"),
    ("mapping20router20", "bWFwcGluZzIwcm91dGVyMjA"),
    ("mapping20cluster20", "bWFwcGluZzIwY2x1c3RlcjIw"),
    ("record20cluster20", "cmVjb3JkMjBjbHVzdGVyMjA"),
    ("record20mirror20", "cmVjb3JkMjBtaXJyb3IyMA"),
    ("record20filter20", "cmVjb3JkMjBmaWx0ZXIyMA"),
    ("record20ranking20", "cmVjb3JkMjByYW5raW5nMjA"),
    ("candle20ranking20", "Y2FuZGxlMjByYW5raW5nMjA"),
    ("candle20encoding20", "Y2FuZGxlMjBlbmNvZGluZzIw"),
    ("candle20mapping20", "Y2FuZGxlMjBtYXBwaW5nMjA"),
    ("candle20record20", "Y2FuZGxlMjByZWNvcmQyMA"),
    ("thread20record20", "dGhyZWFkMjByZWNvcmQyMA"),
    ("thread20candle20", "dGhyZWFkMjBjYW5kbGUyMA"),
    ("thread20thread20", "dGhyZWFkMjB0aHJlYWQyMA"),
    ("thread20kitten20", "dGhyZWFkMjBraXR0ZW4yMA"),
    (
        "round 20: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjA6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 20: agentuniverse is a framework for multi agents",
        "cm91bmQgMjA6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 20: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjA6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 20: the processor reads the record then stops",
        "cm91bmQgMjA6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 20: a worker pulls the next task from the queue",
        "cm91bmQgMjA6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 20: signals travel through the network layer",
        "cm91bmQgMjA6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 20: the gateway routes each request by policy",
        "cm91bmQgMjA6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 20: memory grows until the buffer is full",
        "cm91bmQgMjA6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 20: the cluster mirrors every packet twice",
        "cm91bmQgMjA6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 20: ranking uses tokens learned from the corpus",
        "cm91bmQgMjA6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 20: a long session ends when the candle dies",
        "cm91bmQgMjA6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 20: encode the prompt then map the result",
        "cm91bmQgMjA6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 20: the kernel wakes the worker at dawn", "cm91bmQgMjA6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 20: service latency drops after the patch",
        "cm91bmQgMjA6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 20: the library caches every vector it sees",
        "cm91bmQgMjA6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 20: agents argue then the debate resolves",
        "cm91bmQgMjA6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 20: the filter keeps only strong matches",
        "cm91bmQgMjA6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 20: the model answers with a short reply",
        "cm91bmQgMjA6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 20: the recorder stores the reasoning trace",
        "cm91bmQgMjA6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 20: the angel watches the processor run", "cm91bmQgMjA6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 20: angle of the vector decides the match",
        "cm91bmQgMjA6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 20: the candle burns twice as long at night",
        "cm91bmQgMjA6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 20: a mirror of the universe in one line",
        "cm91bmQgMjA6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 20: the queue drains before the storm", "cm91bmQgMjA6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
