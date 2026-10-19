"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten82kitten82", "a2l0dGVuODJraXR0ZW44Mg"),
    ("kitten82sitting82", "a2l0dGVuODJzaXR0aW5nODI"),
    ("kitten82agent82", "a2l0dGVuODJhZ2VudDgy"),
    ("kitten82angle82", "a2l0dGVuODJhbmdsZTgy"),
    ("sitting82angle82", "c2l0dGluZzgyYW5nbGU4Mg"),
    ("sitting82universe82", "c2l0dGluZzgydW5pdmVyc2U4Mg"),
    ("sitting82memory82", "c2l0dGluZzgybWVtb3J5ODI"),
    ("sitting82stream82", "c2l0dGluZzgyc3RyZWFtODI"),
    ("agent82stream82", "YWdlbnQ4MnN0cmVhbTgy"),
    ("agent82context82", "YWdlbnQ4MmNvbnRleHQ4Mg"),
    ("agent82knowledge82", "YWdlbnQ4Mmtub3dsZWRnZTgy"),
    ("agent82vector82", "YWdlbnQ4MnZlY3Rvcjgy"),
    ("angle82vector82", "YW5nbGU4MnZlY3Rvcjgy"),
    ("angle82processor82", "YW5nbGU4MnByb2Nlc3Nvcjgy"),
    ("angle82reasoning82", "YW5nbGU4MnJlYXNvbmluZzgy"),
    ("angle82machine82", "YW5nbGU4Mm1hY2hpbmU4Mg"),
    ("universe82machine82", "dW5pdmVyc2U4Mm1hY2hpbmU4Mg"),
    ("universe82learning82", "dW5pdmVyc2U4MmxlYXJuaW5nODI"),
    ("universe82model82", "dW5pdmVyc2U4Mm1vZGVsODI"),
    ("universe82token82", "dW5pdmVyc2U4MnRva2VuODI"),
    ("memory82token82", "bWVtb3J5ODJ0b2tlbjgy"),
    ("memory82prompt82", "bWVtb3J5ODJwcm9tcHQ4Mg"),
    ("memory82session82", "bWVtb3J5ODJzZXNzaW9uODI"),
    ("memory82library82", "bWVtb3J5ODJsaWJyYXJ5ODI"),
    ("stream82library82", "c3RyZWFtODJsaWJyYXJ5ODI"),
    ("stream82service82", "c3RyZWFtODJzZXJ2aWNlODI"),
    ("stream82gateway82", "c3RyZWFtODJnYXRld2F5ODI"),
    ("stream82storage82", "c3RyZWFtODJzdG9yYWdlODI"),
    ("context82storage82", "Y29udGV4dDgyc3RvcmFnZTgy"),
    ("context82network82", "Y29udGV4dDgybmV0d29yazgy"),
    ("context82latency82", "Y29udGV4dDgybGF0ZW5jeTgy"),
    ("context82buffer82", "Y29udGV4dDgyYnVmZmVyODI"),
    ("knowledge82buffer82", "a25vd2xlZGdlODJidWZmZXI4Mg"),
    ("knowledge82queue82", "a25vd2xlZGdlODJxdWV1ZTgy"),
    ("knowledge82worker82", "a25vd2xlZGdlODJ3b3JrZXI4Mg"),
    ("knowledge82kernel82", "a25vd2xlZGdlODJrZXJuZWw4Mg"),
    ("vector82kernel82", "dmVjdG9yODJrZXJuZWw4Mg"),
    ("vector82signal82", "dmVjdG9yODJzaWduYWw4Mg"),
    ("vector82packet82", "dmVjdG9yODJwYWNrZXQ4Mg"),
    ("vector82router82", "dmVjdG9yODJyb3V0ZXI4Mg"),
    ("processor82router82", "cHJvY2Vzc29yODJyb3V0ZXI4Mg"),
    ("processor82cluster82", "cHJvY2Vzc29yODJjbHVzdGVyODI"),
    ("processor82mirror82", "cHJvY2Vzc29yODJtaXJyb3I4Mg"),
    ("processor82filter82", "cHJvY2Vzc29yODJmaWx0ZXI4Mg"),
    ("reasoning82filter82", "cmVhc29uaW5nODJmaWx0ZXI4Mg"),
    ("reasoning82ranking82", "cmVhc29uaW5nODJyYW5raW5nODI"),
    ("reasoning82encoding82", "cmVhc29uaW5nODJlbmNvZGluZzgy"),
    ("reasoning82mapping82", "cmVhc29uaW5nODJtYXBwaW5nODI"),
    ("machine82mapping82", "bWFjaGluZTgybWFwcGluZzgy"),
    ("machine82record82", "bWFjaGluZTgycmVjb3JkODI"),
    ("machine82candle82", "bWFjaGluZTgyY2FuZGxlODI"),
    ("machine82thread82", "bWFjaGluZTgydGhyZWFkODI"),
    ("learning82thread82", "bGVhcm5pbmc4MnRocmVhZDgy"),
    ("learning82kitten82", "bGVhcm5pbmc4MmtpdHRlbjgy"),
    ("learning82sitting82", "bGVhcm5pbmc4MnNpdHRpbmc4Mg"),
    ("learning82agent82", "bGVhcm5pbmc4MmFnZW50ODI"),
    ("model82agent82", "bW9kZWw4MmFnZW50ODI"),
    ("model82angle82", "bW9kZWw4MmFuZ2xlODI"),
    ("model82universe82", "bW9kZWw4MnVuaXZlcnNlODI"),
    ("model82memory82", "bW9kZWw4Mm1lbW9yeTgy"),
    ("token82memory82", "dG9rZW44Mm1lbW9yeTgy"),
    ("token82stream82", "dG9rZW44MnN0cmVhbTgy"),
    ("token82context82", "dG9rZW44MmNvbnRleHQ4Mg"),
    ("token82knowledge82", "dG9rZW44Mmtub3dsZWRnZTgy"),
    ("prompt82knowledge82", "cHJvbXB0ODJrbm93bGVkZ2U4Mg"),
    ("prompt82vector82", "cHJvbXB0ODJ2ZWN0b3I4Mg"),
    ("prompt82processor82", "cHJvbXB0ODJwcm9jZXNzb3I4Mg"),
    ("prompt82reasoning82", "cHJvbXB0ODJyZWFzb25pbmc4Mg"),
    ("session82reasoning82", "c2Vzc2lvbjgycmVhc29uaW5nODI"),
    ("session82machine82", "c2Vzc2lvbjgybWFjaGluZTgy"),
    ("session82learning82", "c2Vzc2lvbjgybGVhcm5pbmc4Mg"),
    ("session82model82", "c2Vzc2lvbjgybW9kZWw4Mg"),
    ("library82model82", "bGlicmFyeTgybW9kZWw4Mg"),
    ("library82token82", "bGlicmFyeTgydG9rZW44Mg"),
    ("library82prompt82", "bGlicmFyeTgycHJvbXB0ODI"),
    ("library82session82", "bGlicmFyeTgyc2Vzc2lvbjgy"),
    ("service82session82", "c2VydmljZTgyc2Vzc2lvbjgy"),
    ("service82library82", "c2VydmljZTgybGlicmFyeTgy"),
    ("service82service82", "c2VydmljZTgyc2VydmljZTgy"),
    ("service82gateway82", "c2VydmljZTgyZ2F0ZXdheTgy"),
    ("gateway82gateway82", "Z2F0ZXdheTgyZ2F0ZXdheTgy"),
    ("gateway82storage82", "Z2F0ZXdheTgyc3RvcmFnZTgy"),
    ("gateway82network82", "Z2F0ZXdheTgybmV0d29yazgy"),
    ("gateway82latency82", "Z2F0ZXdheTgybGF0ZW5jeTgy"),
    ("storage82latency82", "c3RvcmFnZTgybGF0ZW5jeTgy"),
    ("storage82buffer82", "c3RvcmFnZTgyYnVmZmVyODI"),
    ("storage82queue82", "c3RvcmFnZTgycXVldWU4Mg"),
    ("storage82worker82", "c3RvcmFnZTgyd29ya2VyODI"),
    ("network82worker82", "bmV0d29yazgyd29ya2VyODI"),
    ("network82kernel82", "bmV0d29yazgya2VybmVsODI"),
    ("network82signal82", "bmV0d29yazgyc2lnbmFsODI"),
    ("network82packet82", "bmV0d29yazgycGFja2V0ODI"),
    ("latency82packet82", "bGF0ZW5jeTgycGFja2V0ODI"),
    ("latency82router82", "bGF0ZW5jeTgycm91dGVyODI"),
    ("latency82cluster82", "bGF0ZW5jeTgyY2x1c3Rlcjgy"),
    ("latency82mirror82", "bGF0ZW5jeTgybWlycm9yODI"),
    ("buffer82mirror82", "YnVmZmVyODJtaXJyb3I4Mg"),
    ("buffer82filter82", "YnVmZmVyODJmaWx0ZXI4Mg"),
    ("buffer82ranking82", "YnVmZmVyODJyYW5raW5nODI"),
    ("buffer82encoding82", "YnVmZmVyODJlbmNvZGluZzgy"),
    ("queue82encoding82", "cXVldWU4MmVuY29kaW5nODI"),
    ("queue82mapping82", "cXVldWU4Mm1hcHBpbmc4Mg"),
    ("queue82record82", "cXVldWU4MnJlY29yZDgy"),
    ("queue82candle82", "cXVldWU4MmNhbmRsZTgy"),
    ("worker82candle82", "d29ya2VyODJjYW5kbGU4Mg"),
    ("worker82thread82", "d29ya2VyODJ0aHJlYWQ4Mg"),
    ("worker82kitten82", "d29ya2VyODJraXR0ZW44Mg"),
    ("worker82sitting82", "d29ya2VyODJzaXR0aW5nODI"),
    ("kernel82sitting82", "a2VybmVsODJzaXR0aW5nODI"),
    ("kernel82agent82", "a2VybmVsODJhZ2VudDgy"),
    ("kernel82angle82", "a2VybmVsODJhbmdsZTgy"),
    ("kernel82universe82", "a2VybmVsODJ1bml2ZXJzZTgy"),
    ("signal82universe82", "c2lnbmFsODJ1bml2ZXJzZTgy"),
    ("signal82memory82", "c2lnbmFsODJtZW1vcnk4Mg"),
    ("signal82stream82", "c2lnbmFsODJzdHJlYW04Mg"),
    ("signal82context82", "c2lnbmFsODJjb250ZXh0ODI"),
    ("packet82context82", "cGFja2V0ODJjb250ZXh0ODI"),
    ("packet82knowledge82", "cGFja2V0ODJrbm93bGVkZ2U4Mg"),
    ("packet82vector82", "cGFja2V0ODJ2ZWN0b3I4Mg"),
    ("packet82processor82", "cGFja2V0ODJwcm9jZXNzb3I4Mg"),
    ("router82processor82", "cm91dGVyODJwcm9jZXNzb3I4Mg"),
    ("router82reasoning82", "cm91dGVyODJyZWFzb25pbmc4Mg"),
    ("router82machine82", "cm91dGVyODJtYWNoaW5lODI"),
    ("router82learning82", "cm91dGVyODJsZWFybmluZzgy"),
    ("cluster82learning82", "Y2x1c3RlcjgybGVhcm5pbmc4Mg"),
    ("cluster82model82", "Y2x1c3RlcjgybW9kZWw4Mg"),
    ("cluster82token82", "Y2x1c3RlcjgydG9rZW44Mg"),
    ("cluster82prompt82", "Y2x1c3RlcjgycHJvbXB0ODI"),
    ("mirror82prompt82", "bWlycm9yODJwcm9tcHQ4Mg"),
    ("mirror82session82", "bWlycm9yODJzZXNzaW9uODI"),
    ("mirror82library82", "bWlycm9yODJsaWJyYXJ5ODI"),
    ("mirror82service82", "bWlycm9yODJzZXJ2aWNlODI"),
    ("filter82service82", "ZmlsdGVyODJzZXJ2aWNlODI"),
    ("filter82gateway82", "ZmlsdGVyODJnYXRld2F5ODI"),
    ("filter82storage82", "ZmlsdGVyODJzdG9yYWdlODI"),
    ("filter82network82", "ZmlsdGVyODJuZXR3b3JrODI"),
    ("ranking82network82", "cmFua2luZzgybmV0d29yazgy"),
    ("ranking82latency82", "cmFua2luZzgybGF0ZW5jeTgy"),
    ("ranking82buffer82", "cmFua2luZzgyYnVmZmVyODI"),
    ("ranking82queue82", "cmFua2luZzgycXVldWU4Mg"),
    ("encoding82queue82", "ZW5jb2Rpbmc4MnF1ZXVlODI"),
    ("encoding82worker82", "ZW5jb2Rpbmc4Mndvcmtlcjgy"),
    ("encoding82kernel82", "ZW5jb2Rpbmc4Mmtlcm5lbDgy"),
    ("encoding82signal82", "ZW5jb2Rpbmc4MnNpZ25hbDgy"),
    ("mapping82signal82", "bWFwcGluZzgyc2lnbmFsODI"),
    ("mapping82packet82", "bWFwcGluZzgycGFja2V0ODI"),
    ("mapping82router82", "bWFwcGluZzgycm91dGVyODI"),
    ("mapping82cluster82", "bWFwcGluZzgyY2x1c3Rlcjgy"),
    ("record82cluster82", "cmVjb3JkODJjbHVzdGVyODI"),
    ("record82mirror82", "cmVjb3JkODJtaXJyb3I4Mg"),
    ("record82filter82", "cmVjb3JkODJmaWx0ZXI4Mg"),
    ("record82ranking82", "cmVjb3JkODJyYW5raW5nODI"),
    ("candle82ranking82", "Y2FuZGxlODJyYW5raW5nODI"),
    ("candle82encoding82", "Y2FuZGxlODJlbmNvZGluZzgy"),
    ("candle82mapping82", "Y2FuZGxlODJtYXBwaW5nODI"),
    ("candle82record82", "Y2FuZGxlODJyZWNvcmQ4Mg"),
    ("thread82record82", "dGhyZWFkODJyZWNvcmQ4Mg"),
    ("thread82candle82", "dGhyZWFkODJjYW5kbGU4Mg"),
    ("thread82thread82", "dGhyZWFkODJ0aHJlYWQ4Mg"),
    ("thread82kitten82", "dGhyZWFkODJraXR0ZW44Mg"),
    (
        "round 82: the quick brown fox jumps over the lazy dog",
        "cm91bmQgODI6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 82: agentuniverse is a framework for multi agents",
        "cm91bmQgODI6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 82: knowledge stored as vectors enables retrieval",
        "cm91bmQgODI6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 82: the processor reads the record then stops",
        "cm91bmQgODI6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 82: a worker pulls the next task from the queue",
        "cm91bmQgODI6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 82: signals travel through the network layer",
        "cm91bmQgODI6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 82: the gateway routes each request by policy",
        "cm91bmQgODI6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 82: memory grows until the buffer is full",
        "cm91bmQgODI6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 82: the cluster mirrors every packet twice",
        "cm91bmQgODI6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 82: ranking uses tokens learned from the corpus",
        "cm91bmQgODI6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 82: a long session ends when the candle dies",
        "cm91bmQgODI6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 82: encode the prompt then map the result",
        "cm91bmQgODI6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 82: the kernel wakes the worker at dawn", "cm91bmQgODI6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 82: service latency drops after the patch",
        "cm91bmQgODI6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 82: the library caches every vector it sees",
        "cm91bmQgODI6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 82: agents argue then the debate resolves",
        "cm91bmQgODI6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 82: the filter keeps only strong matches",
        "cm91bmQgODI6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 82: the model answers with a short reply",
        "cm91bmQgODI6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 82: the recorder stores the reasoning trace",
        "cm91bmQgODI6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 82: the angel watches the processor run", "cm91bmQgODI6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 82: angle of the vector decides the match",
        "cm91bmQgODI6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 82: the candle burns twice as long at night",
        "cm91bmQgODI6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 82: a mirror of the universe in one line",
        "cm91bmQgODI6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 82: the queue drains before the storm", "cm91bmQgODI6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
