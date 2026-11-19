"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten75kitten75", "a2l0dGVuNzVraXR0ZW43NQ"),
    ("kitten75sitting75", "a2l0dGVuNzVzaXR0aW5nNzU"),
    ("kitten75agent75", "a2l0dGVuNzVhZ2VudDc1"),
    ("kitten75angle75", "a2l0dGVuNzVhbmdsZTc1"),
    ("sitting75angle75", "c2l0dGluZzc1YW5nbGU3NQ"),
    ("sitting75universe75", "c2l0dGluZzc1dW5pdmVyc2U3NQ"),
    ("sitting75memory75", "c2l0dGluZzc1bWVtb3J5NzU"),
    ("sitting75stream75", "c2l0dGluZzc1c3RyZWFtNzU"),
    ("agent75stream75", "YWdlbnQ3NXN0cmVhbTc1"),
    ("agent75context75", "YWdlbnQ3NWNvbnRleHQ3NQ"),
    ("agent75knowledge75", "YWdlbnQ3NWtub3dsZWRnZTc1"),
    ("agent75vector75", "YWdlbnQ3NXZlY3Rvcjc1"),
    ("angle75vector75", "YW5nbGU3NXZlY3Rvcjc1"),
    ("angle75processor75", "YW5nbGU3NXByb2Nlc3Nvcjc1"),
    ("angle75reasoning75", "YW5nbGU3NXJlYXNvbmluZzc1"),
    ("angle75machine75", "YW5nbGU3NW1hY2hpbmU3NQ"),
    ("universe75machine75", "dW5pdmVyc2U3NW1hY2hpbmU3NQ"),
    ("universe75learning75", "dW5pdmVyc2U3NWxlYXJuaW5nNzU"),
    ("universe75model75", "dW5pdmVyc2U3NW1vZGVsNzU"),
    ("universe75token75", "dW5pdmVyc2U3NXRva2VuNzU"),
    ("memory75token75", "bWVtb3J5NzV0b2tlbjc1"),
    ("memory75prompt75", "bWVtb3J5NzVwcm9tcHQ3NQ"),
    ("memory75session75", "bWVtb3J5NzVzZXNzaW9uNzU"),
    ("memory75library75", "bWVtb3J5NzVsaWJyYXJ5NzU"),
    ("stream75library75", "c3RyZWFtNzVsaWJyYXJ5NzU"),
    ("stream75service75", "c3RyZWFtNzVzZXJ2aWNlNzU"),
    ("stream75gateway75", "c3RyZWFtNzVnYXRld2F5NzU"),
    ("stream75storage75", "c3RyZWFtNzVzdG9yYWdlNzU"),
    ("context75storage75", "Y29udGV4dDc1c3RvcmFnZTc1"),
    ("context75network75", "Y29udGV4dDc1bmV0d29yazc1"),
    ("context75latency75", "Y29udGV4dDc1bGF0ZW5jeTc1"),
    ("context75buffer75", "Y29udGV4dDc1YnVmZmVyNzU"),
    ("knowledge75buffer75", "a25vd2xlZGdlNzVidWZmZXI3NQ"),
    ("knowledge75queue75", "a25vd2xlZGdlNzVxdWV1ZTc1"),
    ("knowledge75worker75", "a25vd2xlZGdlNzV3b3JrZXI3NQ"),
    ("knowledge75kernel75", "a25vd2xlZGdlNzVrZXJuZWw3NQ"),
    ("vector75kernel75", "dmVjdG9yNzVrZXJuZWw3NQ"),
    ("vector75signal75", "dmVjdG9yNzVzaWduYWw3NQ"),
    ("vector75packet75", "dmVjdG9yNzVwYWNrZXQ3NQ"),
    ("vector75router75", "dmVjdG9yNzVyb3V0ZXI3NQ"),
    ("processor75router75", "cHJvY2Vzc29yNzVyb3V0ZXI3NQ"),
    ("processor75cluster75", "cHJvY2Vzc29yNzVjbHVzdGVyNzU"),
    ("processor75mirror75", "cHJvY2Vzc29yNzVtaXJyb3I3NQ"),
    ("processor75filter75", "cHJvY2Vzc29yNzVmaWx0ZXI3NQ"),
    ("reasoning75filter75", "cmVhc29uaW5nNzVmaWx0ZXI3NQ"),
    ("reasoning75ranking75", "cmVhc29uaW5nNzVyYW5raW5nNzU"),
    ("reasoning75encoding75", "cmVhc29uaW5nNzVlbmNvZGluZzc1"),
    ("reasoning75mapping75", "cmVhc29uaW5nNzVtYXBwaW5nNzU"),
    ("machine75mapping75", "bWFjaGluZTc1bWFwcGluZzc1"),
    ("machine75record75", "bWFjaGluZTc1cmVjb3JkNzU"),
    ("machine75candle75", "bWFjaGluZTc1Y2FuZGxlNzU"),
    ("machine75thread75", "bWFjaGluZTc1dGhyZWFkNzU"),
    ("learning75thread75", "bGVhcm5pbmc3NXRocmVhZDc1"),
    ("learning75kitten75", "bGVhcm5pbmc3NWtpdHRlbjc1"),
    ("learning75sitting75", "bGVhcm5pbmc3NXNpdHRpbmc3NQ"),
    ("learning75agent75", "bGVhcm5pbmc3NWFnZW50NzU"),
    ("model75agent75", "bW9kZWw3NWFnZW50NzU"),
    ("model75angle75", "bW9kZWw3NWFuZ2xlNzU"),
    ("model75universe75", "bW9kZWw3NXVuaXZlcnNlNzU"),
    ("model75memory75", "bW9kZWw3NW1lbW9yeTc1"),
    ("token75memory75", "dG9rZW43NW1lbW9yeTc1"),
    ("token75stream75", "dG9rZW43NXN0cmVhbTc1"),
    ("token75context75", "dG9rZW43NWNvbnRleHQ3NQ"),
    ("token75knowledge75", "dG9rZW43NWtub3dsZWRnZTc1"),
    ("prompt75knowledge75", "cHJvbXB0NzVrbm93bGVkZ2U3NQ"),
    ("prompt75vector75", "cHJvbXB0NzV2ZWN0b3I3NQ"),
    ("prompt75processor75", "cHJvbXB0NzVwcm9jZXNzb3I3NQ"),
    ("prompt75reasoning75", "cHJvbXB0NzVyZWFzb25pbmc3NQ"),
    ("session75reasoning75", "c2Vzc2lvbjc1cmVhc29uaW5nNzU"),
    ("session75machine75", "c2Vzc2lvbjc1bWFjaGluZTc1"),
    ("session75learning75", "c2Vzc2lvbjc1bGVhcm5pbmc3NQ"),
    ("session75model75", "c2Vzc2lvbjc1bW9kZWw3NQ"),
    ("library75model75", "bGlicmFyeTc1bW9kZWw3NQ"),
    ("library75token75", "bGlicmFyeTc1dG9rZW43NQ"),
    ("library75prompt75", "bGlicmFyeTc1cHJvbXB0NzU"),
    ("library75session75", "bGlicmFyeTc1c2Vzc2lvbjc1"),
    ("service75session75", "c2VydmljZTc1c2Vzc2lvbjc1"),
    ("service75library75", "c2VydmljZTc1bGlicmFyeTc1"),
    ("service75service75", "c2VydmljZTc1c2VydmljZTc1"),
    ("service75gateway75", "c2VydmljZTc1Z2F0ZXdheTc1"),
    ("gateway75gateway75", "Z2F0ZXdheTc1Z2F0ZXdheTc1"),
    ("gateway75storage75", "Z2F0ZXdheTc1c3RvcmFnZTc1"),
    ("gateway75network75", "Z2F0ZXdheTc1bmV0d29yazc1"),
    ("gateway75latency75", "Z2F0ZXdheTc1bGF0ZW5jeTc1"),
    ("storage75latency75", "c3RvcmFnZTc1bGF0ZW5jeTc1"),
    ("storage75buffer75", "c3RvcmFnZTc1YnVmZmVyNzU"),
    ("storage75queue75", "c3RvcmFnZTc1cXVldWU3NQ"),
    ("storage75worker75", "c3RvcmFnZTc1d29ya2VyNzU"),
    ("network75worker75", "bmV0d29yazc1d29ya2VyNzU"),
    ("network75kernel75", "bmV0d29yazc1a2VybmVsNzU"),
    ("network75signal75", "bmV0d29yazc1c2lnbmFsNzU"),
    ("network75packet75", "bmV0d29yazc1cGFja2V0NzU"),
    ("latency75packet75", "bGF0ZW5jeTc1cGFja2V0NzU"),
    ("latency75router75", "bGF0ZW5jeTc1cm91dGVyNzU"),
    ("latency75cluster75", "bGF0ZW5jeTc1Y2x1c3Rlcjc1"),
    ("latency75mirror75", "bGF0ZW5jeTc1bWlycm9yNzU"),
    ("buffer75mirror75", "YnVmZmVyNzVtaXJyb3I3NQ"),
    ("buffer75filter75", "YnVmZmVyNzVmaWx0ZXI3NQ"),
    ("buffer75ranking75", "YnVmZmVyNzVyYW5raW5nNzU"),
    ("buffer75encoding75", "YnVmZmVyNzVlbmNvZGluZzc1"),
    ("queue75encoding75", "cXVldWU3NWVuY29kaW5nNzU"),
    ("queue75mapping75", "cXVldWU3NW1hcHBpbmc3NQ"),
    ("queue75record75", "cXVldWU3NXJlY29yZDc1"),
    ("queue75candle75", "cXVldWU3NWNhbmRsZTc1"),
    ("worker75candle75", "d29ya2VyNzVjYW5kbGU3NQ"),
    ("worker75thread75", "d29ya2VyNzV0aHJlYWQ3NQ"),
    ("worker75kitten75", "d29ya2VyNzVraXR0ZW43NQ"),
    ("worker75sitting75", "d29ya2VyNzVzaXR0aW5nNzU"),
    ("kernel75sitting75", "a2VybmVsNzVzaXR0aW5nNzU"),
    ("kernel75agent75", "a2VybmVsNzVhZ2VudDc1"),
    ("kernel75angle75", "a2VybmVsNzVhbmdsZTc1"),
    ("kernel75universe75", "a2VybmVsNzV1bml2ZXJzZTc1"),
    ("signal75universe75", "c2lnbmFsNzV1bml2ZXJzZTc1"),
    ("signal75memory75", "c2lnbmFsNzVtZW1vcnk3NQ"),
    ("signal75stream75", "c2lnbmFsNzVzdHJlYW03NQ"),
    ("signal75context75", "c2lnbmFsNzVjb250ZXh0NzU"),
    ("packet75context75", "cGFja2V0NzVjb250ZXh0NzU"),
    ("packet75knowledge75", "cGFja2V0NzVrbm93bGVkZ2U3NQ"),
    ("packet75vector75", "cGFja2V0NzV2ZWN0b3I3NQ"),
    ("packet75processor75", "cGFja2V0NzVwcm9jZXNzb3I3NQ"),
    ("router75processor75", "cm91dGVyNzVwcm9jZXNzb3I3NQ"),
    ("router75reasoning75", "cm91dGVyNzVyZWFzb25pbmc3NQ"),
    ("router75machine75", "cm91dGVyNzVtYWNoaW5lNzU"),
    ("router75learning75", "cm91dGVyNzVsZWFybmluZzc1"),
    ("cluster75learning75", "Y2x1c3Rlcjc1bGVhcm5pbmc3NQ"),
    ("cluster75model75", "Y2x1c3Rlcjc1bW9kZWw3NQ"),
    ("cluster75token75", "Y2x1c3Rlcjc1dG9rZW43NQ"),
    ("cluster75prompt75", "Y2x1c3Rlcjc1cHJvbXB0NzU"),
    ("mirror75prompt75", "bWlycm9yNzVwcm9tcHQ3NQ"),
    ("mirror75session75", "bWlycm9yNzVzZXNzaW9uNzU"),
    ("mirror75library75", "bWlycm9yNzVsaWJyYXJ5NzU"),
    ("mirror75service75", "bWlycm9yNzVzZXJ2aWNlNzU"),
    ("filter75service75", "ZmlsdGVyNzVzZXJ2aWNlNzU"),
    ("filter75gateway75", "ZmlsdGVyNzVnYXRld2F5NzU"),
    ("filter75storage75", "ZmlsdGVyNzVzdG9yYWdlNzU"),
    ("filter75network75", "ZmlsdGVyNzVuZXR3b3JrNzU"),
    ("ranking75network75", "cmFua2luZzc1bmV0d29yazc1"),
    ("ranking75latency75", "cmFua2luZzc1bGF0ZW5jeTc1"),
    ("ranking75buffer75", "cmFua2luZzc1YnVmZmVyNzU"),
    ("ranking75queue75", "cmFua2luZzc1cXVldWU3NQ"),
    ("encoding75queue75", "ZW5jb2Rpbmc3NXF1ZXVlNzU"),
    ("encoding75worker75", "ZW5jb2Rpbmc3NXdvcmtlcjc1"),
    ("encoding75kernel75", "ZW5jb2Rpbmc3NWtlcm5lbDc1"),
    ("encoding75signal75", "ZW5jb2Rpbmc3NXNpZ25hbDc1"),
    ("mapping75signal75", "bWFwcGluZzc1c2lnbmFsNzU"),
    ("mapping75packet75", "bWFwcGluZzc1cGFja2V0NzU"),
    ("mapping75router75", "bWFwcGluZzc1cm91dGVyNzU"),
    ("mapping75cluster75", "bWFwcGluZzc1Y2x1c3Rlcjc1"),
    ("record75cluster75", "cmVjb3JkNzVjbHVzdGVyNzU"),
    ("record75mirror75", "cmVjb3JkNzVtaXJyb3I3NQ"),
    ("record75filter75", "cmVjb3JkNzVmaWx0ZXI3NQ"),
    ("record75ranking75", "cmVjb3JkNzVyYW5raW5nNzU"),
    ("candle75ranking75", "Y2FuZGxlNzVyYW5raW5nNzU"),
    ("candle75encoding75", "Y2FuZGxlNzVlbmNvZGluZzc1"),
    ("candle75mapping75", "Y2FuZGxlNzVtYXBwaW5nNzU"),
    ("candle75record75", "Y2FuZGxlNzVyZWNvcmQ3NQ"),
    ("thread75record75", "dGhyZWFkNzVyZWNvcmQ3NQ"),
    ("thread75candle75", "dGhyZWFkNzVjYW5kbGU3NQ"),
    ("thread75thread75", "dGhyZWFkNzV0aHJlYWQ3NQ"),
    ("thread75kitten75", "dGhyZWFkNzVraXR0ZW43NQ"),
    (
        "round 75: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzU6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 75: agentuniverse is a framework for multi agents",
        "cm91bmQgNzU6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 75: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzU6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 75: the processor reads the record then stops",
        "cm91bmQgNzU6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 75: a worker pulls the next task from the queue",
        "cm91bmQgNzU6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 75: signals travel through the network layer",
        "cm91bmQgNzU6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 75: the gateway routes each request by policy",
        "cm91bmQgNzU6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 75: memory grows until the buffer is full",
        "cm91bmQgNzU6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 75: the cluster mirrors every packet twice",
        "cm91bmQgNzU6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 75: ranking uses tokens learned from the corpus",
        "cm91bmQgNzU6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 75: a long session ends when the candle dies",
        "cm91bmQgNzU6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 75: encode the prompt then map the result",
        "cm91bmQgNzU6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 75: the kernel wakes the worker at dawn", "cm91bmQgNzU6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 75: service latency drops after the patch",
        "cm91bmQgNzU6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 75: the library caches every vector it sees",
        "cm91bmQgNzU6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 75: agents argue then the debate resolves",
        "cm91bmQgNzU6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 75: the filter keeps only strong matches",
        "cm91bmQgNzU6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 75: the model answers with a short reply",
        "cm91bmQgNzU6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 75: the recorder stores the reasoning trace",
        "cm91bmQgNzU6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 75: the angel watches the processor run", "cm91bmQgNzU6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 75: angle of the vector decides the match",
        "cm91bmQgNzU6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 75: the candle burns twice as long at night",
        "cm91bmQgNzU6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 75: a mirror of the universe in one line",
        "cm91bmQgNzU6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 75: the queue drains before the storm", "cm91bmQgNzU6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
