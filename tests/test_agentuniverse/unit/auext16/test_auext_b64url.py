"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten16kitten16", "a2l0dGVuMTZraXR0ZW4xNg"),
    ("kitten16sitting16", "a2l0dGVuMTZzaXR0aW5nMTY"),
    ("kitten16agent16", "a2l0dGVuMTZhZ2VudDE2"),
    ("kitten16angle16", "a2l0dGVuMTZhbmdsZTE2"),
    ("sitting16angle16", "c2l0dGluZzE2YW5nbGUxNg"),
    ("sitting16universe16", "c2l0dGluZzE2dW5pdmVyc2UxNg"),
    ("sitting16memory16", "c2l0dGluZzE2bWVtb3J5MTY"),
    ("sitting16stream16", "c2l0dGluZzE2c3RyZWFtMTY"),
    ("agent16stream16", "YWdlbnQxNnN0cmVhbTE2"),
    ("agent16context16", "YWdlbnQxNmNvbnRleHQxNg"),
    ("agent16knowledge16", "YWdlbnQxNmtub3dsZWRnZTE2"),
    ("agent16vector16", "YWdlbnQxNnZlY3RvcjE2"),
    ("angle16vector16", "YW5nbGUxNnZlY3RvcjE2"),
    ("angle16processor16", "YW5nbGUxNnByb2Nlc3NvcjE2"),
    ("angle16reasoning16", "YW5nbGUxNnJlYXNvbmluZzE2"),
    ("angle16machine16", "YW5nbGUxNm1hY2hpbmUxNg"),
    ("universe16machine16", "dW5pdmVyc2UxNm1hY2hpbmUxNg"),
    ("universe16learning16", "dW5pdmVyc2UxNmxlYXJuaW5nMTY"),
    ("universe16model16", "dW5pdmVyc2UxNm1vZGVsMTY"),
    ("universe16token16", "dW5pdmVyc2UxNnRva2VuMTY"),
    ("memory16token16", "bWVtb3J5MTZ0b2tlbjE2"),
    ("memory16prompt16", "bWVtb3J5MTZwcm9tcHQxNg"),
    ("memory16session16", "bWVtb3J5MTZzZXNzaW9uMTY"),
    ("memory16library16", "bWVtb3J5MTZsaWJyYXJ5MTY"),
    ("stream16library16", "c3RyZWFtMTZsaWJyYXJ5MTY"),
    ("stream16service16", "c3RyZWFtMTZzZXJ2aWNlMTY"),
    ("stream16gateway16", "c3RyZWFtMTZnYXRld2F5MTY"),
    ("stream16storage16", "c3RyZWFtMTZzdG9yYWdlMTY"),
    ("context16storage16", "Y29udGV4dDE2c3RvcmFnZTE2"),
    ("context16network16", "Y29udGV4dDE2bmV0d29yazE2"),
    ("context16latency16", "Y29udGV4dDE2bGF0ZW5jeTE2"),
    ("context16buffer16", "Y29udGV4dDE2YnVmZmVyMTY"),
    ("knowledge16buffer16", "a25vd2xlZGdlMTZidWZmZXIxNg"),
    ("knowledge16queue16", "a25vd2xlZGdlMTZxdWV1ZTE2"),
    ("knowledge16worker16", "a25vd2xlZGdlMTZ3b3JrZXIxNg"),
    ("knowledge16kernel16", "a25vd2xlZGdlMTZrZXJuZWwxNg"),
    ("vector16kernel16", "dmVjdG9yMTZrZXJuZWwxNg"),
    ("vector16signal16", "dmVjdG9yMTZzaWduYWwxNg"),
    ("vector16packet16", "dmVjdG9yMTZwYWNrZXQxNg"),
    ("vector16router16", "dmVjdG9yMTZyb3V0ZXIxNg"),
    ("processor16router16", "cHJvY2Vzc29yMTZyb3V0ZXIxNg"),
    ("processor16cluster16", "cHJvY2Vzc29yMTZjbHVzdGVyMTY"),
    ("processor16mirror16", "cHJvY2Vzc29yMTZtaXJyb3IxNg"),
    ("processor16filter16", "cHJvY2Vzc29yMTZmaWx0ZXIxNg"),
    ("reasoning16filter16", "cmVhc29uaW5nMTZmaWx0ZXIxNg"),
    ("reasoning16ranking16", "cmVhc29uaW5nMTZyYW5raW5nMTY"),
    ("reasoning16encoding16", "cmVhc29uaW5nMTZlbmNvZGluZzE2"),
    ("reasoning16mapping16", "cmVhc29uaW5nMTZtYXBwaW5nMTY"),
    ("machine16mapping16", "bWFjaGluZTE2bWFwcGluZzE2"),
    ("machine16record16", "bWFjaGluZTE2cmVjb3JkMTY"),
    ("machine16candle16", "bWFjaGluZTE2Y2FuZGxlMTY"),
    ("machine16thread16", "bWFjaGluZTE2dGhyZWFkMTY"),
    ("learning16thread16", "bGVhcm5pbmcxNnRocmVhZDE2"),
    ("learning16kitten16", "bGVhcm5pbmcxNmtpdHRlbjE2"),
    ("learning16sitting16", "bGVhcm5pbmcxNnNpdHRpbmcxNg"),
    ("learning16agent16", "bGVhcm5pbmcxNmFnZW50MTY"),
    ("model16agent16", "bW9kZWwxNmFnZW50MTY"),
    ("model16angle16", "bW9kZWwxNmFuZ2xlMTY"),
    ("model16universe16", "bW9kZWwxNnVuaXZlcnNlMTY"),
    ("model16memory16", "bW9kZWwxNm1lbW9yeTE2"),
    ("token16memory16", "dG9rZW4xNm1lbW9yeTE2"),
    ("token16stream16", "dG9rZW4xNnN0cmVhbTE2"),
    ("token16context16", "dG9rZW4xNmNvbnRleHQxNg"),
    ("token16knowledge16", "dG9rZW4xNmtub3dsZWRnZTE2"),
    ("prompt16knowledge16", "cHJvbXB0MTZrbm93bGVkZ2UxNg"),
    ("prompt16vector16", "cHJvbXB0MTZ2ZWN0b3IxNg"),
    ("prompt16processor16", "cHJvbXB0MTZwcm9jZXNzb3IxNg"),
    ("prompt16reasoning16", "cHJvbXB0MTZyZWFzb25pbmcxNg"),
    ("session16reasoning16", "c2Vzc2lvbjE2cmVhc29uaW5nMTY"),
    ("session16machine16", "c2Vzc2lvbjE2bWFjaGluZTE2"),
    ("session16learning16", "c2Vzc2lvbjE2bGVhcm5pbmcxNg"),
    ("session16model16", "c2Vzc2lvbjE2bW9kZWwxNg"),
    ("library16model16", "bGlicmFyeTE2bW9kZWwxNg"),
    ("library16token16", "bGlicmFyeTE2dG9rZW4xNg"),
    ("library16prompt16", "bGlicmFyeTE2cHJvbXB0MTY"),
    ("library16session16", "bGlicmFyeTE2c2Vzc2lvbjE2"),
    ("service16session16", "c2VydmljZTE2c2Vzc2lvbjE2"),
    ("service16library16", "c2VydmljZTE2bGlicmFyeTE2"),
    ("service16service16", "c2VydmljZTE2c2VydmljZTE2"),
    ("service16gateway16", "c2VydmljZTE2Z2F0ZXdheTE2"),
    ("gateway16gateway16", "Z2F0ZXdheTE2Z2F0ZXdheTE2"),
    ("gateway16storage16", "Z2F0ZXdheTE2c3RvcmFnZTE2"),
    ("gateway16network16", "Z2F0ZXdheTE2bmV0d29yazE2"),
    ("gateway16latency16", "Z2F0ZXdheTE2bGF0ZW5jeTE2"),
    ("storage16latency16", "c3RvcmFnZTE2bGF0ZW5jeTE2"),
    ("storage16buffer16", "c3RvcmFnZTE2YnVmZmVyMTY"),
    ("storage16queue16", "c3RvcmFnZTE2cXVldWUxNg"),
    ("storage16worker16", "c3RvcmFnZTE2d29ya2VyMTY"),
    ("network16worker16", "bmV0d29yazE2d29ya2VyMTY"),
    ("network16kernel16", "bmV0d29yazE2a2VybmVsMTY"),
    ("network16signal16", "bmV0d29yazE2c2lnbmFsMTY"),
    ("network16packet16", "bmV0d29yazE2cGFja2V0MTY"),
    ("latency16packet16", "bGF0ZW5jeTE2cGFja2V0MTY"),
    ("latency16router16", "bGF0ZW5jeTE2cm91dGVyMTY"),
    ("latency16cluster16", "bGF0ZW5jeTE2Y2x1c3RlcjE2"),
    ("latency16mirror16", "bGF0ZW5jeTE2bWlycm9yMTY"),
    ("buffer16mirror16", "YnVmZmVyMTZtaXJyb3IxNg"),
    ("buffer16filter16", "YnVmZmVyMTZmaWx0ZXIxNg"),
    ("buffer16ranking16", "YnVmZmVyMTZyYW5raW5nMTY"),
    ("buffer16encoding16", "YnVmZmVyMTZlbmNvZGluZzE2"),
    ("queue16encoding16", "cXVldWUxNmVuY29kaW5nMTY"),
    ("queue16mapping16", "cXVldWUxNm1hcHBpbmcxNg"),
    ("queue16record16", "cXVldWUxNnJlY29yZDE2"),
    ("queue16candle16", "cXVldWUxNmNhbmRsZTE2"),
    ("worker16candle16", "d29ya2VyMTZjYW5kbGUxNg"),
    ("worker16thread16", "d29ya2VyMTZ0aHJlYWQxNg"),
    ("worker16kitten16", "d29ya2VyMTZraXR0ZW4xNg"),
    ("worker16sitting16", "d29ya2VyMTZzaXR0aW5nMTY"),
    ("kernel16sitting16", "a2VybmVsMTZzaXR0aW5nMTY"),
    ("kernel16agent16", "a2VybmVsMTZhZ2VudDE2"),
    ("kernel16angle16", "a2VybmVsMTZhbmdsZTE2"),
    ("kernel16universe16", "a2VybmVsMTZ1bml2ZXJzZTE2"),
    ("signal16universe16", "c2lnbmFsMTZ1bml2ZXJzZTE2"),
    ("signal16memory16", "c2lnbmFsMTZtZW1vcnkxNg"),
    ("signal16stream16", "c2lnbmFsMTZzdHJlYW0xNg"),
    ("signal16context16", "c2lnbmFsMTZjb250ZXh0MTY"),
    ("packet16context16", "cGFja2V0MTZjb250ZXh0MTY"),
    ("packet16knowledge16", "cGFja2V0MTZrbm93bGVkZ2UxNg"),
    ("packet16vector16", "cGFja2V0MTZ2ZWN0b3IxNg"),
    ("packet16processor16", "cGFja2V0MTZwcm9jZXNzb3IxNg"),
    ("router16processor16", "cm91dGVyMTZwcm9jZXNzb3IxNg"),
    ("router16reasoning16", "cm91dGVyMTZyZWFzb25pbmcxNg"),
    ("router16machine16", "cm91dGVyMTZtYWNoaW5lMTY"),
    ("router16learning16", "cm91dGVyMTZsZWFybmluZzE2"),
    ("cluster16learning16", "Y2x1c3RlcjE2bGVhcm5pbmcxNg"),
    ("cluster16model16", "Y2x1c3RlcjE2bW9kZWwxNg"),
    ("cluster16token16", "Y2x1c3RlcjE2dG9rZW4xNg"),
    ("cluster16prompt16", "Y2x1c3RlcjE2cHJvbXB0MTY"),
    ("mirror16prompt16", "bWlycm9yMTZwcm9tcHQxNg"),
    ("mirror16session16", "bWlycm9yMTZzZXNzaW9uMTY"),
    ("mirror16library16", "bWlycm9yMTZsaWJyYXJ5MTY"),
    ("mirror16service16", "bWlycm9yMTZzZXJ2aWNlMTY"),
    ("filter16service16", "ZmlsdGVyMTZzZXJ2aWNlMTY"),
    ("filter16gateway16", "ZmlsdGVyMTZnYXRld2F5MTY"),
    ("filter16storage16", "ZmlsdGVyMTZzdG9yYWdlMTY"),
    ("filter16network16", "ZmlsdGVyMTZuZXR3b3JrMTY"),
    ("ranking16network16", "cmFua2luZzE2bmV0d29yazE2"),
    ("ranking16latency16", "cmFua2luZzE2bGF0ZW5jeTE2"),
    ("ranking16buffer16", "cmFua2luZzE2YnVmZmVyMTY"),
    ("ranking16queue16", "cmFua2luZzE2cXVldWUxNg"),
    ("encoding16queue16", "ZW5jb2RpbmcxNnF1ZXVlMTY"),
    ("encoding16worker16", "ZW5jb2RpbmcxNndvcmtlcjE2"),
    ("encoding16kernel16", "ZW5jb2RpbmcxNmtlcm5lbDE2"),
    ("encoding16signal16", "ZW5jb2RpbmcxNnNpZ25hbDE2"),
    ("mapping16signal16", "bWFwcGluZzE2c2lnbmFsMTY"),
    ("mapping16packet16", "bWFwcGluZzE2cGFja2V0MTY"),
    ("mapping16router16", "bWFwcGluZzE2cm91dGVyMTY"),
    ("mapping16cluster16", "bWFwcGluZzE2Y2x1c3RlcjE2"),
    ("record16cluster16", "cmVjb3JkMTZjbHVzdGVyMTY"),
    ("record16mirror16", "cmVjb3JkMTZtaXJyb3IxNg"),
    ("record16filter16", "cmVjb3JkMTZmaWx0ZXIxNg"),
    ("record16ranking16", "cmVjb3JkMTZyYW5raW5nMTY"),
    ("candle16ranking16", "Y2FuZGxlMTZyYW5raW5nMTY"),
    ("candle16encoding16", "Y2FuZGxlMTZlbmNvZGluZzE2"),
    ("candle16mapping16", "Y2FuZGxlMTZtYXBwaW5nMTY"),
    ("candle16record16", "Y2FuZGxlMTZyZWNvcmQxNg"),
    ("thread16record16", "dGhyZWFkMTZyZWNvcmQxNg"),
    ("thread16candle16", "dGhyZWFkMTZjYW5kbGUxNg"),
    ("thread16thread16", "dGhyZWFkMTZ0aHJlYWQxNg"),
    ("thread16kitten16", "dGhyZWFkMTZraXR0ZW4xNg"),
    (
        "round 16: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTY6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 16: agentuniverse is a framework for multi agents",
        "cm91bmQgMTY6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 16: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTY6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 16: the processor reads the record then stops",
        "cm91bmQgMTY6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 16: a worker pulls the next task from the queue",
        "cm91bmQgMTY6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 16: signals travel through the network layer",
        "cm91bmQgMTY6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 16: the gateway routes each request by policy",
        "cm91bmQgMTY6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 16: memory grows until the buffer is full",
        "cm91bmQgMTY6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 16: the cluster mirrors every packet twice",
        "cm91bmQgMTY6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 16: ranking uses tokens learned from the corpus",
        "cm91bmQgMTY6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 16: a long session ends when the candle dies",
        "cm91bmQgMTY6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 16: encode the prompt then map the result",
        "cm91bmQgMTY6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 16: the kernel wakes the worker at dawn", "cm91bmQgMTY6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 16: service latency drops after the patch",
        "cm91bmQgMTY6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 16: the library caches every vector it sees",
        "cm91bmQgMTY6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 16: agents argue then the debate resolves",
        "cm91bmQgMTY6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 16: the filter keeps only strong matches",
        "cm91bmQgMTY6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 16: the model answers with a short reply",
        "cm91bmQgMTY6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 16: the recorder stores the reasoning trace",
        "cm91bmQgMTY6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 16: the angel watches the processor run", "cm91bmQgMTY6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 16: angle of the vector decides the match",
        "cm91bmQgMTY6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 16: the candle burns twice as long at night",
        "cm91bmQgMTY6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 16: a mirror of the universe in one line",
        "cm91bmQgMTY6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 16: the queue drains before the storm", "cm91bmQgMTY6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
