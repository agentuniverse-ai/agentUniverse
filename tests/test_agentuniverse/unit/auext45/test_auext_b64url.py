"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten45kitten45", "a2l0dGVuNDVraXR0ZW40NQ"),
    ("kitten45sitting45", "a2l0dGVuNDVzaXR0aW5nNDU"),
    ("kitten45agent45", "a2l0dGVuNDVhZ2VudDQ1"),
    ("kitten45angle45", "a2l0dGVuNDVhbmdsZTQ1"),
    ("sitting45angle45", "c2l0dGluZzQ1YW5nbGU0NQ"),
    ("sitting45universe45", "c2l0dGluZzQ1dW5pdmVyc2U0NQ"),
    ("sitting45memory45", "c2l0dGluZzQ1bWVtb3J5NDU"),
    ("sitting45stream45", "c2l0dGluZzQ1c3RyZWFtNDU"),
    ("agent45stream45", "YWdlbnQ0NXN0cmVhbTQ1"),
    ("agent45context45", "YWdlbnQ0NWNvbnRleHQ0NQ"),
    ("agent45knowledge45", "YWdlbnQ0NWtub3dsZWRnZTQ1"),
    ("agent45vector45", "YWdlbnQ0NXZlY3RvcjQ1"),
    ("angle45vector45", "YW5nbGU0NXZlY3RvcjQ1"),
    ("angle45processor45", "YW5nbGU0NXByb2Nlc3NvcjQ1"),
    ("angle45reasoning45", "YW5nbGU0NXJlYXNvbmluZzQ1"),
    ("angle45machine45", "YW5nbGU0NW1hY2hpbmU0NQ"),
    ("universe45machine45", "dW5pdmVyc2U0NW1hY2hpbmU0NQ"),
    ("universe45learning45", "dW5pdmVyc2U0NWxlYXJuaW5nNDU"),
    ("universe45model45", "dW5pdmVyc2U0NW1vZGVsNDU"),
    ("universe45token45", "dW5pdmVyc2U0NXRva2VuNDU"),
    ("memory45token45", "bWVtb3J5NDV0b2tlbjQ1"),
    ("memory45prompt45", "bWVtb3J5NDVwcm9tcHQ0NQ"),
    ("memory45session45", "bWVtb3J5NDVzZXNzaW9uNDU"),
    ("memory45library45", "bWVtb3J5NDVsaWJyYXJ5NDU"),
    ("stream45library45", "c3RyZWFtNDVsaWJyYXJ5NDU"),
    ("stream45service45", "c3RyZWFtNDVzZXJ2aWNlNDU"),
    ("stream45gateway45", "c3RyZWFtNDVnYXRld2F5NDU"),
    ("stream45storage45", "c3RyZWFtNDVzdG9yYWdlNDU"),
    ("context45storage45", "Y29udGV4dDQ1c3RvcmFnZTQ1"),
    ("context45network45", "Y29udGV4dDQ1bmV0d29yazQ1"),
    ("context45latency45", "Y29udGV4dDQ1bGF0ZW5jeTQ1"),
    ("context45buffer45", "Y29udGV4dDQ1YnVmZmVyNDU"),
    ("knowledge45buffer45", "a25vd2xlZGdlNDVidWZmZXI0NQ"),
    ("knowledge45queue45", "a25vd2xlZGdlNDVxdWV1ZTQ1"),
    ("knowledge45worker45", "a25vd2xlZGdlNDV3b3JrZXI0NQ"),
    ("knowledge45kernel45", "a25vd2xlZGdlNDVrZXJuZWw0NQ"),
    ("vector45kernel45", "dmVjdG9yNDVrZXJuZWw0NQ"),
    ("vector45signal45", "dmVjdG9yNDVzaWduYWw0NQ"),
    ("vector45packet45", "dmVjdG9yNDVwYWNrZXQ0NQ"),
    ("vector45router45", "dmVjdG9yNDVyb3V0ZXI0NQ"),
    ("processor45router45", "cHJvY2Vzc29yNDVyb3V0ZXI0NQ"),
    ("processor45cluster45", "cHJvY2Vzc29yNDVjbHVzdGVyNDU"),
    ("processor45mirror45", "cHJvY2Vzc29yNDVtaXJyb3I0NQ"),
    ("processor45filter45", "cHJvY2Vzc29yNDVmaWx0ZXI0NQ"),
    ("reasoning45filter45", "cmVhc29uaW5nNDVmaWx0ZXI0NQ"),
    ("reasoning45ranking45", "cmVhc29uaW5nNDVyYW5raW5nNDU"),
    ("reasoning45encoding45", "cmVhc29uaW5nNDVlbmNvZGluZzQ1"),
    ("reasoning45mapping45", "cmVhc29uaW5nNDVtYXBwaW5nNDU"),
    ("machine45mapping45", "bWFjaGluZTQ1bWFwcGluZzQ1"),
    ("machine45record45", "bWFjaGluZTQ1cmVjb3JkNDU"),
    ("machine45candle45", "bWFjaGluZTQ1Y2FuZGxlNDU"),
    ("machine45thread45", "bWFjaGluZTQ1dGhyZWFkNDU"),
    ("learning45thread45", "bGVhcm5pbmc0NXRocmVhZDQ1"),
    ("learning45kitten45", "bGVhcm5pbmc0NWtpdHRlbjQ1"),
    ("learning45sitting45", "bGVhcm5pbmc0NXNpdHRpbmc0NQ"),
    ("learning45agent45", "bGVhcm5pbmc0NWFnZW50NDU"),
    ("model45agent45", "bW9kZWw0NWFnZW50NDU"),
    ("model45angle45", "bW9kZWw0NWFuZ2xlNDU"),
    ("model45universe45", "bW9kZWw0NXVuaXZlcnNlNDU"),
    ("model45memory45", "bW9kZWw0NW1lbW9yeTQ1"),
    ("token45memory45", "dG9rZW40NW1lbW9yeTQ1"),
    ("token45stream45", "dG9rZW40NXN0cmVhbTQ1"),
    ("token45context45", "dG9rZW40NWNvbnRleHQ0NQ"),
    ("token45knowledge45", "dG9rZW40NWtub3dsZWRnZTQ1"),
    ("prompt45knowledge45", "cHJvbXB0NDVrbm93bGVkZ2U0NQ"),
    ("prompt45vector45", "cHJvbXB0NDV2ZWN0b3I0NQ"),
    ("prompt45processor45", "cHJvbXB0NDVwcm9jZXNzb3I0NQ"),
    ("prompt45reasoning45", "cHJvbXB0NDVyZWFzb25pbmc0NQ"),
    ("session45reasoning45", "c2Vzc2lvbjQ1cmVhc29uaW5nNDU"),
    ("session45machine45", "c2Vzc2lvbjQ1bWFjaGluZTQ1"),
    ("session45learning45", "c2Vzc2lvbjQ1bGVhcm5pbmc0NQ"),
    ("session45model45", "c2Vzc2lvbjQ1bW9kZWw0NQ"),
    ("library45model45", "bGlicmFyeTQ1bW9kZWw0NQ"),
    ("library45token45", "bGlicmFyeTQ1dG9rZW40NQ"),
    ("library45prompt45", "bGlicmFyeTQ1cHJvbXB0NDU"),
    ("library45session45", "bGlicmFyeTQ1c2Vzc2lvbjQ1"),
    ("service45session45", "c2VydmljZTQ1c2Vzc2lvbjQ1"),
    ("service45library45", "c2VydmljZTQ1bGlicmFyeTQ1"),
    ("service45service45", "c2VydmljZTQ1c2VydmljZTQ1"),
    ("service45gateway45", "c2VydmljZTQ1Z2F0ZXdheTQ1"),
    ("gateway45gateway45", "Z2F0ZXdheTQ1Z2F0ZXdheTQ1"),
    ("gateway45storage45", "Z2F0ZXdheTQ1c3RvcmFnZTQ1"),
    ("gateway45network45", "Z2F0ZXdheTQ1bmV0d29yazQ1"),
    ("gateway45latency45", "Z2F0ZXdheTQ1bGF0ZW5jeTQ1"),
    ("storage45latency45", "c3RvcmFnZTQ1bGF0ZW5jeTQ1"),
    ("storage45buffer45", "c3RvcmFnZTQ1YnVmZmVyNDU"),
    ("storage45queue45", "c3RvcmFnZTQ1cXVldWU0NQ"),
    ("storage45worker45", "c3RvcmFnZTQ1d29ya2VyNDU"),
    ("network45worker45", "bmV0d29yazQ1d29ya2VyNDU"),
    ("network45kernel45", "bmV0d29yazQ1a2VybmVsNDU"),
    ("network45signal45", "bmV0d29yazQ1c2lnbmFsNDU"),
    ("network45packet45", "bmV0d29yazQ1cGFja2V0NDU"),
    ("latency45packet45", "bGF0ZW5jeTQ1cGFja2V0NDU"),
    ("latency45router45", "bGF0ZW5jeTQ1cm91dGVyNDU"),
    ("latency45cluster45", "bGF0ZW5jeTQ1Y2x1c3RlcjQ1"),
    ("latency45mirror45", "bGF0ZW5jeTQ1bWlycm9yNDU"),
    ("buffer45mirror45", "YnVmZmVyNDVtaXJyb3I0NQ"),
    ("buffer45filter45", "YnVmZmVyNDVmaWx0ZXI0NQ"),
    ("buffer45ranking45", "YnVmZmVyNDVyYW5raW5nNDU"),
    ("buffer45encoding45", "YnVmZmVyNDVlbmNvZGluZzQ1"),
    ("queue45encoding45", "cXVldWU0NWVuY29kaW5nNDU"),
    ("queue45mapping45", "cXVldWU0NW1hcHBpbmc0NQ"),
    ("queue45record45", "cXVldWU0NXJlY29yZDQ1"),
    ("queue45candle45", "cXVldWU0NWNhbmRsZTQ1"),
    ("worker45candle45", "d29ya2VyNDVjYW5kbGU0NQ"),
    ("worker45thread45", "d29ya2VyNDV0aHJlYWQ0NQ"),
    ("worker45kitten45", "d29ya2VyNDVraXR0ZW40NQ"),
    ("worker45sitting45", "d29ya2VyNDVzaXR0aW5nNDU"),
    ("kernel45sitting45", "a2VybmVsNDVzaXR0aW5nNDU"),
    ("kernel45agent45", "a2VybmVsNDVhZ2VudDQ1"),
    ("kernel45angle45", "a2VybmVsNDVhbmdsZTQ1"),
    ("kernel45universe45", "a2VybmVsNDV1bml2ZXJzZTQ1"),
    ("signal45universe45", "c2lnbmFsNDV1bml2ZXJzZTQ1"),
    ("signal45memory45", "c2lnbmFsNDVtZW1vcnk0NQ"),
    ("signal45stream45", "c2lnbmFsNDVzdHJlYW00NQ"),
    ("signal45context45", "c2lnbmFsNDVjb250ZXh0NDU"),
    ("packet45context45", "cGFja2V0NDVjb250ZXh0NDU"),
    ("packet45knowledge45", "cGFja2V0NDVrbm93bGVkZ2U0NQ"),
    ("packet45vector45", "cGFja2V0NDV2ZWN0b3I0NQ"),
    ("packet45processor45", "cGFja2V0NDVwcm9jZXNzb3I0NQ"),
    ("router45processor45", "cm91dGVyNDVwcm9jZXNzb3I0NQ"),
    ("router45reasoning45", "cm91dGVyNDVyZWFzb25pbmc0NQ"),
    ("router45machine45", "cm91dGVyNDVtYWNoaW5lNDU"),
    ("router45learning45", "cm91dGVyNDVsZWFybmluZzQ1"),
    ("cluster45learning45", "Y2x1c3RlcjQ1bGVhcm5pbmc0NQ"),
    ("cluster45model45", "Y2x1c3RlcjQ1bW9kZWw0NQ"),
    ("cluster45token45", "Y2x1c3RlcjQ1dG9rZW40NQ"),
    ("cluster45prompt45", "Y2x1c3RlcjQ1cHJvbXB0NDU"),
    ("mirror45prompt45", "bWlycm9yNDVwcm9tcHQ0NQ"),
    ("mirror45session45", "bWlycm9yNDVzZXNzaW9uNDU"),
    ("mirror45library45", "bWlycm9yNDVsaWJyYXJ5NDU"),
    ("mirror45service45", "bWlycm9yNDVzZXJ2aWNlNDU"),
    ("filter45service45", "ZmlsdGVyNDVzZXJ2aWNlNDU"),
    ("filter45gateway45", "ZmlsdGVyNDVnYXRld2F5NDU"),
    ("filter45storage45", "ZmlsdGVyNDVzdG9yYWdlNDU"),
    ("filter45network45", "ZmlsdGVyNDVuZXR3b3JrNDU"),
    ("ranking45network45", "cmFua2luZzQ1bmV0d29yazQ1"),
    ("ranking45latency45", "cmFua2luZzQ1bGF0ZW5jeTQ1"),
    ("ranking45buffer45", "cmFua2luZzQ1YnVmZmVyNDU"),
    ("ranking45queue45", "cmFua2luZzQ1cXVldWU0NQ"),
    ("encoding45queue45", "ZW5jb2Rpbmc0NXF1ZXVlNDU"),
    ("encoding45worker45", "ZW5jb2Rpbmc0NXdvcmtlcjQ1"),
    ("encoding45kernel45", "ZW5jb2Rpbmc0NWtlcm5lbDQ1"),
    ("encoding45signal45", "ZW5jb2Rpbmc0NXNpZ25hbDQ1"),
    ("mapping45signal45", "bWFwcGluZzQ1c2lnbmFsNDU"),
    ("mapping45packet45", "bWFwcGluZzQ1cGFja2V0NDU"),
    ("mapping45router45", "bWFwcGluZzQ1cm91dGVyNDU"),
    ("mapping45cluster45", "bWFwcGluZzQ1Y2x1c3RlcjQ1"),
    ("record45cluster45", "cmVjb3JkNDVjbHVzdGVyNDU"),
    ("record45mirror45", "cmVjb3JkNDVtaXJyb3I0NQ"),
    ("record45filter45", "cmVjb3JkNDVmaWx0ZXI0NQ"),
    ("record45ranking45", "cmVjb3JkNDVyYW5raW5nNDU"),
    ("candle45ranking45", "Y2FuZGxlNDVyYW5raW5nNDU"),
    ("candle45encoding45", "Y2FuZGxlNDVlbmNvZGluZzQ1"),
    ("candle45mapping45", "Y2FuZGxlNDVtYXBwaW5nNDU"),
    ("candle45record45", "Y2FuZGxlNDVyZWNvcmQ0NQ"),
    ("thread45record45", "dGhyZWFkNDVyZWNvcmQ0NQ"),
    ("thread45candle45", "dGhyZWFkNDVjYW5kbGU0NQ"),
    ("thread45thread45", "dGhyZWFkNDV0aHJlYWQ0NQ"),
    ("thread45kitten45", "dGhyZWFkNDVraXR0ZW40NQ"),
    (
        "round 45: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNDU6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 45: agentuniverse is a framework for multi agents",
        "cm91bmQgNDU6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 45: knowledge stored as vectors enables retrieval",
        "cm91bmQgNDU6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 45: the processor reads the record then stops",
        "cm91bmQgNDU6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 45: a worker pulls the next task from the queue",
        "cm91bmQgNDU6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 45: signals travel through the network layer",
        "cm91bmQgNDU6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 45: the gateway routes each request by policy",
        "cm91bmQgNDU6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 45: memory grows until the buffer is full",
        "cm91bmQgNDU6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 45: the cluster mirrors every packet twice",
        "cm91bmQgNDU6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 45: ranking uses tokens learned from the corpus",
        "cm91bmQgNDU6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 45: a long session ends when the candle dies",
        "cm91bmQgNDU6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 45: encode the prompt then map the result",
        "cm91bmQgNDU6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 45: the kernel wakes the worker at dawn", "cm91bmQgNDU6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 45: service latency drops after the patch",
        "cm91bmQgNDU6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 45: the library caches every vector it sees",
        "cm91bmQgNDU6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 45: agents argue then the debate resolves",
        "cm91bmQgNDU6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 45: the filter keeps only strong matches",
        "cm91bmQgNDU6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 45: the model answers with a short reply",
        "cm91bmQgNDU6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 45: the recorder stores the reasoning trace",
        "cm91bmQgNDU6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 45: the angel watches the processor run", "cm91bmQgNDU6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 45: angle of the vector decides the match",
        "cm91bmQgNDU6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 45: the candle burns twice as long at night",
        "cm91bmQgNDU6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 45: a mirror of the universe in one line",
        "cm91bmQgNDU6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 45: the queue drains before the storm", "cm91bmQgNDU6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
