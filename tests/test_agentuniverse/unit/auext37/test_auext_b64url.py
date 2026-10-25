"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten37kitten37", "a2l0dGVuMzdraXR0ZW4zNw"),
    ("kitten37sitting37", "a2l0dGVuMzdzaXR0aW5nMzc"),
    ("kitten37agent37", "a2l0dGVuMzdhZ2VudDM3"),
    ("kitten37angle37", "a2l0dGVuMzdhbmdsZTM3"),
    ("sitting37angle37", "c2l0dGluZzM3YW5nbGUzNw"),
    ("sitting37universe37", "c2l0dGluZzM3dW5pdmVyc2UzNw"),
    ("sitting37memory37", "c2l0dGluZzM3bWVtb3J5Mzc"),
    ("sitting37stream37", "c2l0dGluZzM3c3RyZWFtMzc"),
    ("agent37stream37", "YWdlbnQzN3N0cmVhbTM3"),
    ("agent37context37", "YWdlbnQzN2NvbnRleHQzNw"),
    ("agent37knowledge37", "YWdlbnQzN2tub3dsZWRnZTM3"),
    ("agent37vector37", "YWdlbnQzN3ZlY3RvcjM3"),
    ("angle37vector37", "YW5nbGUzN3ZlY3RvcjM3"),
    ("angle37processor37", "YW5nbGUzN3Byb2Nlc3NvcjM3"),
    ("angle37reasoning37", "YW5nbGUzN3JlYXNvbmluZzM3"),
    ("angle37machine37", "YW5nbGUzN21hY2hpbmUzNw"),
    ("universe37machine37", "dW5pdmVyc2UzN21hY2hpbmUzNw"),
    ("universe37learning37", "dW5pdmVyc2UzN2xlYXJuaW5nMzc"),
    ("universe37model37", "dW5pdmVyc2UzN21vZGVsMzc"),
    ("universe37token37", "dW5pdmVyc2UzN3Rva2VuMzc"),
    ("memory37token37", "bWVtb3J5Mzd0b2tlbjM3"),
    ("memory37prompt37", "bWVtb3J5Mzdwcm9tcHQzNw"),
    ("memory37session37", "bWVtb3J5MzdzZXNzaW9uMzc"),
    ("memory37library37", "bWVtb3J5MzdsaWJyYXJ5Mzc"),
    ("stream37library37", "c3RyZWFtMzdsaWJyYXJ5Mzc"),
    ("stream37service37", "c3RyZWFtMzdzZXJ2aWNlMzc"),
    ("stream37gateway37", "c3RyZWFtMzdnYXRld2F5Mzc"),
    ("stream37storage37", "c3RyZWFtMzdzdG9yYWdlMzc"),
    ("context37storage37", "Y29udGV4dDM3c3RvcmFnZTM3"),
    ("context37network37", "Y29udGV4dDM3bmV0d29yazM3"),
    ("context37latency37", "Y29udGV4dDM3bGF0ZW5jeTM3"),
    ("context37buffer37", "Y29udGV4dDM3YnVmZmVyMzc"),
    ("knowledge37buffer37", "a25vd2xlZGdlMzdidWZmZXIzNw"),
    ("knowledge37queue37", "a25vd2xlZGdlMzdxdWV1ZTM3"),
    ("knowledge37worker37", "a25vd2xlZGdlMzd3b3JrZXIzNw"),
    ("knowledge37kernel37", "a25vd2xlZGdlMzdrZXJuZWwzNw"),
    ("vector37kernel37", "dmVjdG9yMzdrZXJuZWwzNw"),
    ("vector37signal37", "dmVjdG9yMzdzaWduYWwzNw"),
    ("vector37packet37", "dmVjdG9yMzdwYWNrZXQzNw"),
    ("vector37router37", "dmVjdG9yMzdyb3V0ZXIzNw"),
    ("processor37router37", "cHJvY2Vzc29yMzdyb3V0ZXIzNw"),
    ("processor37cluster37", "cHJvY2Vzc29yMzdjbHVzdGVyMzc"),
    ("processor37mirror37", "cHJvY2Vzc29yMzdtaXJyb3IzNw"),
    ("processor37filter37", "cHJvY2Vzc29yMzdmaWx0ZXIzNw"),
    ("reasoning37filter37", "cmVhc29uaW5nMzdmaWx0ZXIzNw"),
    ("reasoning37ranking37", "cmVhc29uaW5nMzdyYW5raW5nMzc"),
    ("reasoning37encoding37", "cmVhc29uaW5nMzdlbmNvZGluZzM3"),
    ("reasoning37mapping37", "cmVhc29uaW5nMzdtYXBwaW5nMzc"),
    ("machine37mapping37", "bWFjaGluZTM3bWFwcGluZzM3"),
    ("machine37record37", "bWFjaGluZTM3cmVjb3JkMzc"),
    ("machine37candle37", "bWFjaGluZTM3Y2FuZGxlMzc"),
    ("machine37thread37", "bWFjaGluZTM3dGhyZWFkMzc"),
    ("learning37thread37", "bGVhcm5pbmczN3RocmVhZDM3"),
    ("learning37kitten37", "bGVhcm5pbmczN2tpdHRlbjM3"),
    ("learning37sitting37", "bGVhcm5pbmczN3NpdHRpbmczNw"),
    ("learning37agent37", "bGVhcm5pbmczN2FnZW50Mzc"),
    ("model37agent37", "bW9kZWwzN2FnZW50Mzc"),
    ("model37angle37", "bW9kZWwzN2FuZ2xlMzc"),
    ("model37universe37", "bW9kZWwzN3VuaXZlcnNlMzc"),
    ("model37memory37", "bW9kZWwzN21lbW9yeTM3"),
    ("token37memory37", "dG9rZW4zN21lbW9yeTM3"),
    ("token37stream37", "dG9rZW4zN3N0cmVhbTM3"),
    ("token37context37", "dG9rZW4zN2NvbnRleHQzNw"),
    ("token37knowledge37", "dG9rZW4zN2tub3dsZWRnZTM3"),
    ("prompt37knowledge37", "cHJvbXB0Mzdrbm93bGVkZ2UzNw"),
    ("prompt37vector37", "cHJvbXB0Mzd2ZWN0b3IzNw"),
    ("prompt37processor37", "cHJvbXB0Mzdwcm9jZXNzb3IzNw"),
    ("prompt37reasoning37", "cHJvbXB0MzdyZWFzb25pbmczNw"),
    ("session37reasoning37", "c2Vzc2lvbjM3cmVhc29uaW5nMzc"),
    ("session37machine37", "c2Vzc2lvbjM3bWFjaGluZTM3"),
    ("session37learning37", "c2Vzc2lvbjM3bGVhcm5pbmczNw"),
    ("session37model37", "c2Vzc2lvbjM3bW9kZWwzNw"),
    ("library37model37", "bGlicmFyeTM3bW9kZWwzNw"),
    ("library37token37", "bGlicmFyeTM3dG9rZW4zNw"),
    ("library37prompt37", "bGlicmFyeTM3cHJvbXB0Mzc"),
    ("library37session37", "bGlicmFyeTM3c2Vzc2lvbjM3"),
    ("service37session37", "c2VydmljZTM3c2Vzc2lvbjM3"),
    ("service37library37", "c2VydmljZTM3bGlicmFyeTM3"),
    ("service37service37", "c2VydmljZTM3c2VydmljZTM3"),
    ("service37gateway37", "c2VydmljZTM3Z2F0ZXdheTM3"),
    ("gateway37gateway37", "Z2F0ZXdheTM3Z2F0ZXdheTM3"),
    ("gateway37storage37", "Z2F0ZXdheTM3c3RvcmFnZTM3"),
    ("gateway37network37", "Z2F0ZXdheTM3bmV0d29yazM3"),
    ("gateway37latency37", "Z2F0ZXdheTM3bGF0ZW5jeTM3"),
    ("storage37latency37", "c3RvcmFnZTM3bGF0ZW5jeTM3"),
    ("storage37buffer37", "c3RvcmFnZTM3YnVmZmVyMzc"),
    ("storage37queue37", "c3RvcmFnZTM3cXVldWUzNw"),
    ("storage37worker37", "c3RvcmFnZTM3d29ya2VyMzc"),
    ("network37worker37", "bmV0d29yazM3d29ya2VyMzc"),
    ("network37kernel37", "bmV0d29yazM3a2VybmVsMzc"),
    ("network37signal37", "bmV0d29yazM3c2lnbmFsMzc"),
    ("network37packet37", "bmV0d29yazM3cGFja2V0Mzc"),
    ("latency37packet37", "bGF0ZW5jeTM3cGFja2V0Mzc"),
    ("latency37router37", "bGF0ZW5jeTM3cm91dGVyMzc"),
    ("latency37cluster37", "bGF0ZW5jeTM3Y2x1c3RlcjM3"),
    ("latency37mirror37", "bGF0ZW5jeTM3bWlycm9yMzc"),
    ("buffer37mirror37", "YnVmZmVyMzdtaXJyb3IzNw"),
    ("buffer37filter37", "YnVmZmVyMzdmaWx0ZXIzNw"),
    ("buffer37ranking37", "YnVmZmVyMzdyYW5raW5nMzc"),
    ("buffer37encoding37", "YnVmZmVyMzdlbmNvZGluZzM3"),
    ("queue37encoding37", "cXVldWUzN2VuY29kaW5nMzc"),
    ("queue37mapping37", "cXVldWUzN21hcHBpbmczNw"),
    ("queue37record37", "cXVldWUzN3JlY29yZDM3"),
    ("queue37candle37", "cXVldWUzN2NhbmRsZTM3"),
    ("worker37candle37", "d29ya2VyMzdjYW5kbGUzNw"),
    ("worker37thread37", "d29ya2VyMzd0aHJlYWQzNw"),
    ("worker37kitten37", "d29ya2VyMzdraXR0ZW4zNw"),
    ("worker37sitting37", "d29ya2VyMzdzaXR0aW5nMzc"),
    ("kernel37sitting37", "a2VybmVsMzdzaXR0aW5nMzc"),
    ("kernel37agent37", "a2VybmVsMzdhZ2VudDM3"),
    ("kernel37angle37", "a2VybmVsMzdhbmdsZTM3"),
    ("kernel37universe37", "a2VybmVsMzd1bml2ZXJzZTM3"),
    ("signal37universe37", "c2lnbmFsMzd1bml2ZXJzZTM3"),
    ("signal37memory37", "c2lnbmFsMzdtZW1vcnkzNw"),
    ("signal37stream37", "c2lnbmFsMzdzdHJlYW0zNw"),
    ("signal37context37", "c2lnbmFsMzdjb250ZXh0Mzc"),
    ("packet37context37", "cGFja2V0Mzdjb250ZXh0Mzc"),
    ("packet37knowledge37", "cGFja2V0Mzdrbm93bGVkZ2UzNw"),
    ("packet37vector37", "cGFja2V0Mzd2ZWN0b3IzNw"),
    ("packet37processor37", "cGFja2V0Mzdwcm9jZXNzb3IzNw"),
    ("router37processor37", "cm91dGVyMzdwcm9jZXNzb3IzNw"),
    ("router37reasoning37", "cm91dGVyMzdyZWFzb25pbmczNw"),
    ("router37machine37", "cm91dGVyMzdtYWNoaW5lMzc"),
    ("router37learning37", "cm91dGVyMzdsZWFybmluZzM3"),
    ("cluster37learning37", "Y2x1c3RlcjM3bGVhcm5pbmczNw"),
    ("cluster37model37", "Y2x1c3RlcjM3bW9kZWwzNw"),
    ("cluster37token37", "Y2x1c3RlcjM3dG9rZW4zNw"),
    ("cluster37prompt37", "Y2x1c3RlcjM3cHJvbXB0Mzc"),
    ("mirror37prompt37", "bWlycm9yMzdwcm9tcHQzNw"),
    ("mirror37session37", "bWlycm9yMzdzZXNzaW9uMzc"),
    ("mirror37library37", "bWlycm9yMzdsaWJyYXJ5Mzc"),
    ("mirror37service37", "bWlycm9yMzdzZXJ2aWNlMzc"),
    ("filter37service37", "ZmlsdGVyMzdzZXJ2aWNlMzc"),
    ("filter37gateway37", "ZmlsdGVyMzdnYXRld2F5Mzc"),
    ("filter37storage37", "ZmlsdGVyMzdzdG9yYWdlMzc"),
    ("filter37network37", "ZmlsdGVyMzduZXR3b3JrMzc"),
    ("ranking37network37", "cmFua2luZzM3bmV0d29yazM3"),
    ("ranking37latency37", "cmFua2luZzM3bGF0ZW5jeTM3"),
    ("ranking37buffer37", "cmFua2luZzM3YnVmZmVyMzc"),
    ("ranking37queue37", "cmFua2luZzM3cXVldWUzNw"),
    ("encoding37queue37", "ZW5jb2RpbmczN3F1ZXVlMzc"),
    ("encoding37worker37", "ZW5jb2RpbmczN3dvcmtlcjM3"),
    ("encoding37kernel37", "ZW5jb2RpbmczN2tlcm5lbDM3"),
    ("encoding37signal37", "ZW5jb2RpbmczN3NpZ25hbDM3"),
    ("mapping37signal37", "bWFwcGluZzM3c2lnbmFsMzc"),
    ("mapping37packet37", "bWFwcGluZzM3cGFja2V0Mzc"),
    ("mapping37router37", "bWFwcGluZzM3cm91dGVyMzc"),
    ("mapping37cluster37", "bWFwcGluZzM3Y2x1c3RlcjM3"),
    ("record37cluster37", "cmVjb3JkMzdjbHVzdGVyMzc"),
    ("record37mirror37", "cmVjb3JkMzdtaXJyb3IzNw"),
    ("record37filter37", "cmVjb3JkMzdmaWx0ZXIzNw"),
    ("record37ranking37", "cmVjb3JkMzdyYW5raW5nMzc"),
    ("candle37ranking37", "Y2FuZGxlMzdyYW5raW5nMzc"),
    ("candle37encoding37", "Y2FuZGxlMzdlbmNvZGluZzM3"),
    ("candle37mapping37", "Y2FuZGxlMzdtYXBwaW5nMzc"),
    ("candle37record37", "Y2FuZGxlMzdyZWNvcmQzNw"),
    ("thread37record37", "dGhyZWFkMzdyZWNvcmQzNw"),
    ("thread37candle37", "dGhyZWFkMzdjYW5kbGUzNw"),
    ("thread37thread37", "dGhyZWFkMzd0aHJlYWQzNw"),
    ("thread37kitten37", "dGhyZWFkMzdraXR0ZW4zNw"),
    (
        "round 37: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMzc6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 37: agentuniverse is a framework for multi agents",
        "cm91bmQgMzc6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 37: knowledge stored as vectors enables retrieval",
        "cm91bmQgMzc6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 37: the processor reads the record then stops",
        "cm91bmQgMzc6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 37: a worker pulls the next task from the queue",
        "cm91bmQgMzc6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 37: signals travel through the network layer",
        "cm91bmQgMzc6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 37: the gateway routes each request by policy",
        "cm91bmQgMzc6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 37: memory grows until the buffer is full",
        "cm91bmQgMzc6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 37: the cluster mirrors every packet twice",
        "cm91bmQgMzc6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 37: ranking uses tokens learned from the corpus",
        "cm91bmQgMzc6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 37: a long session ends when the candle dies",
        "cm91bmQgMzc6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 37: encode the prompt then map the result",
        "cm91bmQgMzc6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 37: the kernel wakes the worker at dawn", "cm91bmQgMzc6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 37: service latency drops after the patch",
        "cm91bmQgMzc6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 37: the library caches every vector it sees",
        "cm91bmQgMzc6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 37: agents argue then the debate resolves",
        "cm91bmQgMzc6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 37: the filter keeps only strong matches",
        "cm91bmQgMzc6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 37: the model answers with a short reply",
        "cm91bmQgMzc6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 37: the recorder stores the reasoning trace",
        "cm91bmQgMzc6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 37: the angel watches the processor run", "cm91bmQgMzc6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 37: angle of the vector decides the match",
        "cm91bmQgMzc6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 37: the candle burns twice as long at night",
        "cm91bmQgMzc6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 37: a mirror of the universe in one line",
        "cm91bmQgMzc6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 37: the queue drains before the storm", "cm91bmQgMzc6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
