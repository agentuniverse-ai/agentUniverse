"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten34kitten34", "a2l0dGVuMzRraXR0ZW4zNA"),
    ("kitten34sitting34", "a2l0dGVuMzRzaXR0aW5nMzQ"),
    ("kitten34agent34", "a2l0dGVuMzRhZ2VudDM0"),
    ("kitten34angle34", "a2l0dGVuMzRhbmdsZTM0"),
    ("sitting34angle34", "c2l0dGluZzM0YW5nbGUzNA"),
    ("sitting34universe34", "c2l0dGluZzM0dW5pdmVyc2UzNA"),
    ("sitting34memory34", "c2l0dGluZzM0bWVtb3J5MzQ"),
    ("sitting34stream34", "c2l0dGluZzM0c3RyZWFtMzQ"),
    ("agent34stream34", "YWdlbnQzNHN0cmVhbTM0"),
    ("agent34context34", "YWdlbnQzNGNvbnRleHQzNA"),
    ("agent34knowledge34", "YWdlbnQzNGtub3dsZWRnZTM0"),
    ("agent34vector34", "YWdlbnQzNHZlY3RvcjM0"),
    ("angle34vector34", "YW5nbGUzNHZlY3RvcjM0"),
    ("angle34processor34", "YW5nbGUzNHByb2Nlc3NvcjM0"),
    ("angle34reasoning34", "YW5nbGUzNHJlYXNvbmluZzM0"),
    ("angle34machine34", "YW5nbGUzNG1hY2hpbmUzNA"),
    ("universe34machine34", "dW5pdmVyc2UzNG1hY2hpbmUzNA"),
    ("universe34learning34", "dW5pdmVyc2UzNGxlYXJuaW5nMzQ"),
    ("universe34model34", "dW5pdmVyc2UzNG1vZGVsMzQ"),
    ("universe34token34", "dW5pdmVyc2UzNHRva2VuMzQ"),
    ("memory34token34", "bWVtb3J5MzR0b2tlbjM0"),
    ("memory34prompt34", "bWVtb3J5MzRwcm9tcHQzNA"),
    ("memory34session34", "bWVtb3J5MzRzZXNzaW9uMzQ"),
    ("memory34library34", "bWVtb3J5MzRsaWJyYXJ5MzQ"),
    ("stream34library34", "c3RyZWFtMzRsaWJyYXJ5MzQ"),
    ("stream34service34", "c3RyZWFtMzRzZXJ2aWNlMzQ"),
    ("stream34gateway34", "c3RyZWFtMzRnYXRld2F5MzQ"),
    ("stream34storage34", "c3RyZWFtMzRzdG9yYWdlMzQ"),
    ("context34storage34", "Y29udGV4dDM0c3RvcmFnZTM0"),
    ("context34network34", "Y29udGV4dDM0bmV0d29yazM0"),
    ("context34latency34", "Y29udGV4dDM0bGF0ZW5jeTM0"),
    ("context34buffer34", "Y29udGV4dDM0YnVmZmVyMzQ"),
    ("knowledge34buffer34", "a25vd2xlZGdlMzRidWZmZXIzNA"),
    ("knowledge34queue34", "a25vd2xlZGdlMzRxdWV1ZTM0"),
    ("knowledge34worker34", "a25vd2xlZGdlMzR3b3JrZXIzNA"),
    ("knowledge34kernel34", "a25vd2xlZGdlMzRrZXJuZWwzNA"),
    ("vector34kernel34", "dmVjdG9yMzRrZXJuZWwzNA"),
    ("vector34signal34", "dmVjdG9yMzRzaWduYWwzNA"),
    ("vector34packet34", "dmVjdG9yMzRwYWNrZXQzNA"),
    ("vector34router34", "dmVjdG9yMzRyb3V0ZXIzNA"),
    ("processor34router34", "cHJvY2Vzc29yMzRyb3V0ZXIzNA"),
    ("processor34cluster34", "cHJvY2Vzc29yMzRjbHVzdGVyMzQ"),
    ("processor34mirror34", "cHJvY2Vzc29yMzRtaXJyb3IzNA"),
    ("processor34filter34", "cHJvY2Vzc29yMzRmaWx0ZXIzNA"),
    ("reasoning34filter34", "cmVhc29uaW5nMzRmaWx0ZXIzNA"),
    ("reasoning34ranking34", "cmVhc29uaW5nMzRyYW5raW5nMzQ"),
    ("reasoning34encoding34", "cmVhc29uaW5nMzRlbmNvZGluZzM0"),
    ("reasoning34mapping34", "cmVhc29uaW5nMzRtYXBwaW5nMzQ"),
    ("machine34mapping34", "bWFjaGluZTM0bWFwcGluZzM0"),
    ("machine34record34", "bWFjaGluZTM0cmVjb3JkMzQ"),
    ("machine34candle34", "bWFjaGluZTM0Y2FuZGxlMzQ"),
    ("machine34thread34", "bWFjaGluZTM0dGhyZWFkMzQ"),
    ("learning34thread34", "bGVhcm5pbmczNHRocmVhZDM0"),
    ("learning34kitten34", "bGVhcm5pbmczNGtpdHRlbjM0"),
    ("learning34sitting34", "bGVhcm5pbmczNHNpdHRpbmczNA"),
    ("learning34agent34", "bGVhcm5pbmczNGFnZW50MzQ"),
    ("model34agent34", "bW9kZWwzNGFnZW50MzQ"),
    ("model34angle34", "bW9kZWwzNGFuZ2xlMzQ"),
    ("model34universe34", "bW9kZWwzNHVuaXZlcnNlMzQ"),
    ("model34memory34", "bW9kZWwzNG1lbW9yeTM0"),
    ("token34memory34", "dG9rZW4zNG1lbW9yeTM0"),
    ("token34stream34", "dG9rZW4zNHN0cmVhbTM0"),
    ("token34context34", "dG9rZW4zNGNvbnRleHQzNA"),
    ("token34knowledge34", "dG9rZW4zNGtub3dsZWRnZTM0"),
    ("prompt34knowledge34", "cHJvbXB0MzRrbm93bGVkZ2UzNA"),
    ("prompt34vector34", "cHJvbXB0MzR2ZWN0b3IzNA"),
    ("prompt34processor34", "cHJvbXB0MzRwcm9jZXNzb3IzNA"),
    ("prompt34reasoning34", "cHJvbXB0MzRyZWFzb25pbmczNA"),
    ("session34reasoning34", "c2Vzc2lvbjM0cmVhc29uaW5nMzQ"),
    ("session34machine34", "c2Vzc2lvbjM0bWFjaGluZTM0"),
    ("session34learning34", "c2Vzc2lvbjM0bGVhcm5pbmczNA"),
    ("session34model34", "c2Vzc2lvbjM0bW9kZWwzNA"),
    ("library34model34", "bGlicmFyeTM0bW9kZWwzNA"),
    ("library34token34", "bGlicmFyeTM0dG9rZW4zNA"),
    ("library34prompt34", "bGlicmFyeTM0cHJvbXB0MzQ"),
    ("library34session34", "bGlicmFyeTM0c2Vzc2lvbjM0"),
    ("service34session34", "c2VydmljZTM0c2Vzc2lvbjM0"),
    ("service34library34", "c2VydmljZTM0bGlicmFyeTM0"),
    ("service34service34", "c2VydmljZTM0c2VydmljZTM0"),
    ("service34gateway34", "c2VydmljZTM0Z2F0ZXdheTM0"),
    ("gateway34gateway34", "Z2F0ZXdheTM0Z2F0ZXdheTM0"),
    ("gateway34storage34", "Z2F0ZXdheTM0c3RvcmFnZTM0"),
    ("gateway34network34", "Z2F0ZXdheTM0bmV0d29yazM0"),
    ("gateway34latency34", "Z2F0ZXdheTM0bGF0ZW5jeTM0"),
    ("storage34latency34", "c3RvcmFnZTM0bGF0ZW5jeTM0"),
    ("storage34buffer34", "c3RvcmFnZTM0YnVmZmVyMzQ"),
    ("storage34queue34", "c3RvcmFnZTM0cXVldWUzNA"),
    ("storage34worker34", "c3RvcmFnZTM0d29ya2VyMzQ"),
    ("network34worker34", "bmV0d29yazM0d29ya2VyMzQ"),
    ("network34kernel34", "bmV0d29yazM0a2VybmVsMzQ"),
    ("network34signal34", "bmV0d29yazM0c2lnbmFsMzQ"),
    ("network34packet34", "bmV0d29yazM0cGFja2V0MzQ"),
    ("latency34packet34", "bGF0ZW5jeTM0cGFja2V0MzQ"),
    ("latency34router34", "bGF0ZW5jeTM0cm91dGVyMzQ"),
    ("latency34cluster34", "bGF0ZW5jeTM0Y2x1c3RlcjM0"),
    ("latency34mirror34", "bGF0ZW5jeTM0bWlycm9yMzQ"),
    ("buffer34mirror34", "YnVmZmVyMzRtaXJyb3IzNA"),
    ("buffer34filter34", "YnVmZmVyMzRmaWx0ZXIzNA"),
    ("buffer34ranking34", "YnVmZmVyMzRyYW5raW5nMzQ"),
    ("buffer34encoding34", "YnVmZmVyMzRlbmNvZGluZzM0"),
    ("queue34encoding34", "cXVldWUzNGVuY29kaW5nMzQ"),
    ("queue34mapping34", "cXVldWUzNG1hcHBpbmczNA"),
    ("queue34record34", "cXVldWUzNHJlY29yZDM0"),
    ("queue34candle34", "cXVldWUzNGNhbmRsZTM0"),
    ("worker34candle34", "d29ya2VyMzRjYW5kbGUzNA"),
    ("worker34thread34", "d29ya2VyMzR0aHJlYWQzNA"),
    ("worker34kitten34", "d29ya2VyMzRraXR0ZW4zNA"),
    ("worker34sitting34", "d29ya2VyMzRzaXR0aW5nMzQ"),
    ("kernel34sitting34", "a2VybmVsMzRzaXR0aW5nMzQ"),
    ("kernel34agent34", "a2VybmVsMzRhZ2VudDM0"),
    ("kernel34angle34", "a2VybmVsMzRhbmdsZTM0"),
    ("kernel34universe34", "a2VybmVsMzR1bml2ZXJzZTM0"),
    ("signal34universe34", "c2lnbmFsMzR1bml2ZXJzZTM0"),
    ("signal34memory34", "c2lnbmFsMzRtZW1vcnkzNA"),
    ("signal34stream34", "c2lnbmFsMzRzdHJlYW0zNA"),
    ("signal34context34", "c2lnbmFsMzRjb250ZXh0MzQ"),
    ("packet34context34", "cGFja2V0MzRjb250ZXh0MzQ"),
    ("packet34knowledge34", "cGFja2V0MzRrbm93bGVkZ2UzNA"),
    ("packet34vector34", "cGFja2V0MzR2ZWN0b3IzNA"),
    ("packet34processor34", "cGFja2V0MzRwcm9jZXNzb3IzNA"),
    ("router34processor34", "cm91dGVyMzRwcm9jZXNzb3IzNA"),
    ("router34reasoning34", "cm91dGVyMzRyZWFzb25pbmczNA"),
    ("router34machine34", "cm91dGVyMzRtYWNoaW5lMzQ"),
    ("router34learning34", "cm91dGVyMzRsZWFybmluZzM0"),
    ("cluster34learning34", "Y2x1c3RlcjM0bGVhcm5pbmczNA"),
    ("cluster34model34", "Y2x1c3RlcjM0bW9kZWwzNA"),
    ("cluster34token34", "Y2x1c3RlcjM0dG9rZW4zNA"),
    ("cluster34prompt34", "Y2x1c3RlcjM0cHJvbXB0MzQ"),
    ("mirror34prompt34", "bWlycm9yMzRwcm9tcHQzNA"),
    ("mirror34session34", "bWlycm9yMzRzZXNzaW9uMzQ"),
    ("mirror34library34", "bWlycm9yMzRsaWJyYXJ5MzQ"),
    ("mirror34service34", "bWlycm9yMzRzZXJ2aWNlMzQ"),
    ("filter34service34", "ZmlsdGVyMzRzZXJ2aWNlMzQ"),
    ("filter34gateway34", "ZmlsdGVyMzRnYXRld2F5MzQ"),
    ("filter34storage34", "ZmlsdGVyMzRzdG9yYWdlMzQ"),
    ("filter34network34", "ZmlsdGVyMzRuZXR3b3JrMzQ"),
    ("ranking34network34", "cmFua2luZzM0bmV0d29yazM0"),
    ("ranking34latency34", "cmFua2luZzM0bGF0ZW5jeTM0"),
    ("ranking34buffer34", "cmFua2luZzM0YnVmZmVyMzQ"),
    ("ranking34queue34", "cmFua2luZzM0cXVldWUzNA"),
    ("encoding34queue34", "ZW5jb2RpbmczNHF1ZXVlMzQ"),
    ("encoding34worker34", "ZW5jb2RpbmczNHdvcmtlcjM0"),
    ("encoding34kernel34", "ZW5jb2RpbmczNGtlcm5lbDM0"),
    ("encoding34signal34", "ZW5jb2RpbmczNHNpZ25hbDM0"),
    ("mapping34signal34", "bWFwcGluZzM0c2lnbmFsMzQ"),
    ("mapping34packet34", "bWFwcGluZzM0cGFja2V0MzQ"),
    ("mapping34router34", "bWFwcGluZzM0cm91dGVyMzQ"),
    ("mapping34cluster34", "bWFwcGluZzM0Y2x1c3RlcjM0"),
    ("record34cluster34", "cmVjb3JkMzRjbHVzdGVyMzQ"),
    ("record34mirror34", "cmVjb3JkMzRtaXJyb3IzNA"),
    ("record34filter34", "cmVjb3JkMzRmaWx0ZXIzNA"),
    ("record34ranking34", "cmVjb3JkMzRyYW5raW5nMzQ"),
    ("candle34ranking34", "Y2FuZGxlMzRyYW5raW5nMzQ"),
    ("candle34encoding34", "Y2FuZGxlMzRlbmNvZGluZzM0"),
    ("candle34mapping34", "Y2FuZGxlMzRtYXBwaW5nMzQ"),
    ("candle34record34", "Y2FuZGxlMzRyZWNvcmQzNA"),
    ("thread34record34", "dGhyZWFkMzRyZWNvcmQzNA"),
    ("thread34candle34", "dGhyZWFkMzRjYW5kbGUzNA"),
    ("thread34thread34", "dGhyZWFkMzR0aHJlYWQzNA"),
    ("thread34kitten34", "dGhyZWFkMzRraXR0ZW4zNA"),
    (
        "round 34: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMzQ6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 34: agentuniverse is a framework for multi agents",
        "cm91bmQgMzQ6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 34: knowledge stored as vectors enables retrieval",
        "cm91bmQgMzQ6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 34: the processor reads the record then stops",
        "cm91bmQgMzQ6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 34: a worker pulls the next task from the queue",
        "cm91bmQgMzQ6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 34: signals travel through the network layer",
        "cm91bmQgMzQ6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 34: the gateway routes each request by policy",
        "cm91bmQgMzQ6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 34: memory grows until the buffer is full",
        "cm91bmQgMzQ6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 34: the cluster mirrors every packet twice",
        "cm91bmQgMzQ6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 34: ranking uses tokens learned from the corpus",
        "cm91bmQgMzQ6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 34: a long session ends when the candle dies",
        "cm91bmQgMzQ6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 34: encode the prompt then map the result",
        "cm91bmQgMzQ6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 34: the kernel wakes the worker at dawn", "cm91bmQgMzQ6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 34: service latency drops after the patch",
        "cm91bmQgMzQ6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 34: the library caches every vector it sees",
        "cm91bmQgMzQ6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 34: agents argue then the debate resolves",
        "cm91bmQgMzQ6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 34: the filter keeps only strong matches",
        "cm91bmQgMzQ6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 34: the model answers with a short reply",
        "cm91bmQgMzQ6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 34: the recorder stores the reasoning trace",
        "cm91bmQgMzQ6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 34: the angel watches the processor run", "cm91bmQgMzQ6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 34: angle of the vector decides the match",
        "cm91bmQgMzQ6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 34: the candle burns twice as long at night",
        "cm91bmQgMzQ6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 34: a mirror of the universe in one line",
        "cm91bmQgMzQ6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 34: the queue drains before the storm", "cm91bmQgMzQ6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
