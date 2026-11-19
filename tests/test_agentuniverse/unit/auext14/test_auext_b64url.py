"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten14kitten14", "a2l0dGVuMTRraXR0ZW4xNA"),
    ("kitten14sitting14", "a2l0dGVuMTRzaXR0aW5nMTQ"),
    ("kitten14agent14", "a2l0dGVuMTRhZ2VudDE0"),
    ("kitten14angle14", "a2l0dGVuMTRhbmdsZTE0"),
    ("sitting14angle14", "c2l0dGluZzE0YW5nbGUxNA"),
    ("sitting14universe14", "c2l0dGluZzE0dW5pdmVyc2UxNA"),
    ("sitting14memory14", "c2l0dGluZzE0bWVtb3J5MTQ"),
    ("sitting14stream14", "c2l0dGluZzE0c3RyZWFtMTQ"),
    ("agent14stream14", "YWdlbnQxNHN0cmVhbTE0"),
    ("agent14context14", "YWdlbnQxNGNvbnRleHQxNA"),
    ("agent14knowledge14", "YWdlbnQxNGtub3dsZWRnZTE0"),
    ("agent14vector14", "YWdlbnQxNHZlY3RvcjE0"),
    ("angle14vector14", "YW5nbGUxNHZlY3RvcjE0"),
    ("angle14processor14", "YW5nbGUxNHByb2Nlc3NvcjE0"),
    ("angle14reasoning14", "YW5nbGUxNHJlYXNvbmluZzE0"),
    ("angle14machine14", "YW5nbGUxNG1hY2hpbmUxNA"),
    ("universe14machine14", "dW5pdmVyc2UxNG1hY2hpbmUxNA"),
    ("universe14learning14", "dW5pdmVyc2UxNGxlYXJuaW5nMTQ"),
    ("universe14model14", "dW5pdmVyc2UxNG1vZGVsMTQ"),
    ("universe14token14", "dW5pdmVyc2UxNHRva2VuMTQ"),
    ("memory14token14", "bWVtb3J5MTR0b2tlbjE0"),
    ("memory14prompt14", "bWVtb3J5MTRwcm9tcHQxNA"),
    ("memory14session14", "bWVtb3J5MTRzZXNzaW9uMTQ"),
    ("memory14library14", "bWVtb3J5MTRsaWJyYXJ5MTQ"),
    ("stream14library14", "c3RyZWFtMTRsaWJyYXJ5MTQ"),
    ("stream14service14", "c3RyZWFtMTRzZXJ2aWNlMTQ"),
    ("stream14gateway14", "c3RyZWFtMTRnYXRld2F5MTQ"),
    ("stream14storage14", "c3RyZWFtMTRzdG9yYWdlMTQ"),
    ("context14storage14", "Y29udGV4dDE0c3RvcmFnZTE0"),
    ("context14network14", "Y29udGV4dDE0bmV0d29yazE0"),
    ("context14latency14", "Y29udGV4dDE0bGF0ZW5jeTE0"),
    ("context14buffer14", "Y29udGV4dDE0YnVmZmVyMTQ"),
    ("knowledge14buffer14", "a25vd2xlZGdlMTRidWZmZXIxNA"),
    ("knowledge14queue14", "a25vd2xlZGdlMTRxdWV1ZTE0"),
    ("knowledge14worker14", "a25vd2xlZGdlMTR3b3JrZXIxNA"),
    ("knowledge14kernel14", "a25vd2xlZGdlMTRrZXJuZWwxNA"),
    ("vector14kernel14", "dmVjdG9yMTRrZXJuZWwxNA"),
    ("vector14signal14", "dmVjdG9yMTRzaWduYWwxNA"),
    ("vector14packet14", "dmVjdG9yMTRwYWNrZXQxNA"),
    ("vector14router14", "dmVjdG9yMTRyb3V0ZXIxNA"),
    ("processor14router14", "cHJvY2Vzc29yMTRyb3V0ZXIxNA"),
    ("processor14cluster14", "cHJvY2Vzc29yMTRjbHVzdGVyMTQ"),
    ("processor14mirror14", "cHJvY2Vzc29yMTRtaXJyb3IxNA"),
    ("processor14filter14", "cHJvY2Vzc29yMTRmaWx0ZXIxNA"),
    ("reasoning14filter14", "cmVhc29uaW5nMTRmaWx0ZXIxNA"),
    ("reasoning14ranking14", "cmVhc29uaW5nMTRyYW5raW5nMTQ"),
    ("reasoning14encoding14", "cmVhc29uaW5nMTRlbmNvZGluZzE0"),
    ("reasoning14mapping14", "cmVhc29uaW5nMTRtYXBwaW5nMTQ"),
    ("machine14mapping14", "bWFjaGluZTE0bWFwcGluZzE0"),
    ("machine14record14", "bWFjaGluZTE0cmVjb3JkMTQ"),
    ("machine14candle14", "bWFjaGluZTE0Y2FuZGxlMTQ"),
    ("machine14thread14", "bWFjaGluZTE0dGhyZWFkMTQ"),
    ("learning14thread14", "bGVhcm5pbmcxNHRocmVhZDE0"),
    ("learning14kitten14", "bGVhcm5pbmcxNGtpdHRlbjE0"),
    ("learning14sitting14", "bGVhcm5pbmcxNHNpdHRpbmcxNA"),
    ("learning14agent14", "bGVhcm5pbmcxNGFnZW50MTQ"),
    ("model14agent14", "bW9kZWwxNGFnZW50MTQ"),
    ("model14angle14", "bW9kZWwxNGFuZ2xlMTQ"),
    ("model14universe14", "bW9kZWwxNHVuaXZlcnNlMTQ"),
    ("model14memory14", "bW9kZWwxNG1lbW9yeTE0"),
    ("token14memory14", "dG9rZW4xNG1lbW9yeTE0"),
    ("token14stream14", "dG9rZW4xNHN0cmVhbTE0"),
    ("token14context14", "dG9rZW4xNGNvbnRleHQxNA"),
    ("token14knowledge14", "dG9rZW4xNGtub3dsZWRnZTE0"),
    ("prompt14knowledge14", "cHJvbXB0MTRrbm93bGVkZ2UxNA"),
    ("prompt14vector14", "cHJvbXB0MTR2ZWN0b3IxNA"),
    ("prompt14processor14", "cHJvbXB0MTRwcm9jZXNzb3IxNA"),
    ("prompt14reasoning14", "cHJvbXB0MTRyZWFzb25pbmcxNA"),
    ("session14reasoning14", "c2Vzc2lvbjE0cmVhc29uaW5nMTQ"),
    ("session14machine14", "c2Vzc2lvbjE0bWFjaGluZTE0"),
    ("session14learning14", "c2Vzc2lvbjE0bGVhcm5pbmcxNA"),
    ("session14model14", "c2Vzc2lvbjE0bW9kZWwxNA"),
    ("library14model14", "bGlicmFyeTE0bW9kZWwxNA"),
    ("library14token14", "bGlicmFyeTE0dG9rZW4xNA"),
    ("library14prompt14", "bGlicmFyeTE0cHJvbXB0MTQ"),
    ("library14session14", "bGlicmFyeTE0c2Vzc2lvbjE0"),
    ("service14session14", "c2VydmljZTE0c2Vzc2lvbjE0"),
    ("service14library14", "c2VydmljZTE0bGlicmFyeTE0"),
    ("service14service14", "c2VydmljZTE0c2VydmljZTE0"),
    ("service14gateway14", "c2VydmljZTE0Z2F0ZXdheTE0"),
    ("gateway14gateway14", "Z2F0ZXdheTE0Z2F0ZXdheTE0"),
    ("gateway14storage14", "Z2F0ZXdheTE0c3RvcmFnZTE0"),
    ("gateway14network14", "Z2F0ZXdheTE0bmV0d29yazE0"),
    ("gateway14latency14", "Z2F0ZXdheTE0bGF0ZW5jeTE0"),
    ("storage14latency14", "c3RvcmFnZTE0bGF0ZW5jeTE0"),
    ("storage14buffer14", "c3RvcmFnZTE0YnVmZmVyMTQ"),
    ("storage14queue14", "c3RvcmFnZTE0cXVldWUxNA"),
    ("storage14worker14", "c3RvcmFnZTE0d29ya2VyMTQ"),
    ("network14worker14", "bmV0d29yazE0d29ya2VyMTQ"),
    ("network14kernel14", "bmV0d29yazE0a2VybmVsMTQ"),
    ("network14signal14", "bmV0d29yazE0c2lnbmFsMTQ"),
    ("network14packet14", "bmV0d29yazE0cGFja2V0MTQ"),
    ("latency14packet14", "bGF0ZW5jeTE0cGFja2V0MTQ"),
    ("latency14router14", "bGF0ZW5jeTE0cm91dGVyMTQ"),
    ("latency14cluster14", "bGF0ZW5jeTE0Y2x1c3RlcjE0"),
    ("latency14mirror14", "bGF0ZW5jeTE0bWlycm9yMTQ"),
    ("buffer14mirror14", "YnVmZmVyMTRtaXJyb3IxNA"),
    ("buffer14filter14", "YnVmZmVyMTRmaWx0ZXIxNA"),
    ("buffer14ranking14", "YnVmZmVyMTRyYW5raW5nMTQ"),
    ("buffer14encoding14", "YnVmZmVyMTRlbmNvZGluZzE0"),
    ("queue14encoding14", "cXVldWUxNGVuY29kaW5nMTQ"),
    ("queue14mapping14", "cXVldWUxNG1hcHBpbmcxNA"),
    ("queue14record14", "cXVldWUxNHJlY29yZDE0"),
    ("queue14candle14", "cXVldWUxNGNhbmRsZTE0"),
    ("worker14candle14", "d29ya2VyMTRjYW5kbGUxNA"),
    ("worker14thread14", "d29ya2VyMTR0aHJlYWQxNA"),
    ("worker14kitten14", "d29ya2VyMTRraXR0ZW4xNA"),
    ("worker14sitting14", "d29ya2VyMTRzaXR0aW5nMTQ"),
    ("kernel14sitting14", "a2VybmVsMTRzaXR0aW5nMTQ"),
    ("kernel14agent14", "a2VybmVsMTRhZ2VudDE0"),
    ("kernel14angle14", "a2VybmVsMTRhbmdsZTE0"),
    ("kernel14universe14", "a2VybmVsMTR1bml2ZXJzZTE0"),
    ("signal14universe14", "c2lnbmFsMTR1bml2ZXJzZTE0"),
    ("signal14memory14", "c2lnbmFsMTRtZW1vcnkxNA"),
    ("signal14stream14", "c2lnbmFsMTRzdHJlYW0xNA"),
    ("signal14context14", "c2lnbmFsMTRjb250ZXh0MTQ"),
    ("packet14context14", "cGFja2V0MTRjb250ZXh0MTQ"),
    ("packet14knowledge14", "cGFja2V0MTRrbm93bGVkZ2UxNA"),
    ("packet14vector14", "cGFja2V0MTR2ZWN0b3IxNA"),
    ("packet14processor14", "cGFja2V0MTRwcm9jZXNzb3IxNA"),
    ("router14processor14", "cm91dGVyMTRwcm9jZXNzb3IxNA"),
    ("router14reasoning14", "cm91dGVyMTRyZWFzb25pbmcxNA"),
    ("router14machine14", "cm91dGVyMTRtYWNoaW5lMTQ"),
    ("router14learning14", "cm91dGVyMTRsZWFybmluZzE0"),
    ("cluster14learning14", "Y2x1c3RlcjE0bGVhcm5pbmcxNA"),
    ("cluster14model14", "Y2x1c3RlcjE0bW9kZWwxNA"),
    ("cluster14token14", "Y2x1c3RlcjE0dG9rZW4xNA"),
    ("cluster14prompt14", "Y2x1c3RlcjE0cHJvbXB0MTQ"),
    ("mirror14prompt14", "bWlycm9yMTRwcm9tcHQxNA"),
    ("mirror14session14", "bWlycm9yMTRzZXNzaW9uMTQ"),
    ("mirror14library14", "bWlycm9yMTRsaWJyYXJ5MTQ"),
    ("mirror14service14", "bWlycm9yMTRzZXJ2aWNlMTQ"),
    ("filter14service14", "ZmlsdGVyMTRzZXJ2aWNlMTQ"),
    ("filter14gateway14", "ZmlsdGVyMTRnYXRld2F5MTQ"),
    ("filter14storage14", "ZmlsdGVyMTRzdG9yYWdlMTQ"),
    ("filter14network14", "ZmlsdGVyMTRuZXR3b3JrMTQ"),
    ("ranking14network14", "cmFua2luZzE0bmV0d29yazE0"),
    ("ranking14latency14", "cmFua2luZzE0bGF0ZW5jeTE0"),
    ("ranking14buffer14", "cmFua2luZzE0YnVmZmVyMTQ"),
    ("ranking14queue14", "cmFua2luZzE0cXVldWUxNA"),
    ("encoding14queue14", "ZW5jb2RpbmcxNHF1ZXVlMTQ"),
    ("encoding14worker14", "ZW5jb2RpbmcxNHdvcmtlcjE0"),
    ("encoding14kernel14", "ZW5jb2RpbmcxNGtlcm5lbDE0"),
    ("encoding14signal14", "ZW5jb2RpbmcxNHNpZ25hbDE0"),
    ("mapping14signal14", "bWFwcGluZzE0c2lnbmFsMTQ"),
    ("mapping14packet14", "bWFwcGluZzE0cGFja2V0MTQ"),
    ("mapping14router14", "bWFwcGluZzE0cm91dGVyMTQ"),
    ("mapping14cluster14", "bWFwcGluZzE0Y2x1c3RlcjE0"),
    ("record14cluster14", "cmVjb3JkMTRjbHVzdGVyMTQ"),
    ("record14mirror14", "cmVjb3JkMTRtaXJyb3IxNA"),
    ("record14filter14", "cmVjb3JkMTRmaWx0ZXIxNA"),
    ("record14ranking14", "cmVjb3JkMTRyYW5raW5nMTQ"),
    ("candle14ranking14", "Y2FuZGxlMTRyYW5raW5nMTQ"),
    ("candle14encoding14", "Y2FuZGxlMTRlbmNvZGluZzE0"),
    ("candle14mapping14", "Y2FuZGxlMTRtYXBwaW5nMTQ"),
    ("candle14record14", "Y2FuZGxlMTRyZWNvcmQxNA"),
    ("thread14record14", "dGhyZWFkMTRyZWNvcmQxNA"),
    ("thread14candle14", "dGhyZWFkMTRjYW5kbGUxNA"),
    ("thread14thread14", "dGhyZWFkMTR0aHJlYWQxNA"),
    ("thread14kitten14", "dGhyZWFkMTRraXR0ZW4xNA"),
    (
        "round 14: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTQ6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 14: agentuniverse is a framework for multi agents",
        "cm91bmQgMTQ6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 14: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTQ6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 14: the processor reads the record then stops",
        "cm91bmQgMTQ6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 14: a worker pulls the next task from the queue",
        "cm91bmQgMTQ6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 14: signals travel through the network layer",
        "cm91bmQgMTQ6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 14: the gateway routes each request by policy",
        "cm91bmQgMTQ6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 14: memory grows until the buffer is full",
        "cm91bmQgMTQ6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 14: the cluster mirrors every packet twice",
        "cm91bmQgMTQ6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 14: ranking uses tokens learned from the corpus",
        "cm91bmQgMTQ6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 14: a long session ends when the candle dies",
        "cm91bmQgMTQ6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 14: encode the prompt then map the result",
        "cm91bmQgMTQ6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 14: the kernel wakes the worker at dawn", "cm91bmQgMTQ6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 14: service latency drops after the patch",
        "cm91bmQgMTQ6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 14: the library caches every vector it sees",
        "cm91bmQgMTQ6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 14: agents argue then the debate resolves",
        "cm91bmQgMTQ6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 14: the filter keeps only strong matches",
        "cm91bmQgMTQ6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 14: the model answers with a short reply",
        "cm91bmQgMTQ6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 14: the recorder stores the reasoning trace",
        "cm91bmQgMTQ6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 14: the angel watches the processor run", "cm91bmQgMTQ6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 14: angle of the vector decides the match",
        "cm91bmQgMTQ6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 14: the candle burns twice as long at night",
        "cm91bmQgMTQ6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 14: a mirror of the universe in one line",
        "cm91bmQgMTQ6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 14: the queue drains before the storm", "cm91bmQgMTQ6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
