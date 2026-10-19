"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten55kitten55", "a2l0dGVuNTVraXR0ZW41NQ"),
    ("kitten55sitting55", "a2l0dGVuNTVzaXR0aW5nNTU"),
    ("kitten55agent55", "a2l0dGVuNTVhZ2VudDU1"),
    ("kitten55angle55", "a2l0dGVuNTVhbmdsZTU1"),
    ("sitting55angle55", "c2l0dGluZzU1YW5nbGU1NQ"),
    ("sitting55universe55", "c2l0dGluZzU1dW5pdmVyc2U1NQ"),
    ("sitting55memory55", "c2l0dGluZzU1bWVtb3J5NTU"),
    ("sitting55stream55", "c2l0dGluZzU1c3RyZWFtNTU"),
    ("agent55stream55", "YWdlbnQ1NXN0cmVhbTU1"),
    ("agent55context55", "YWdlbnQ1NWNvbnRleHQ1NQ"),
    ("agent55knowledge55", "YWdlbnQ1NWtub3dsZWRnZTU1"),
    ("agent55vector55", "YWdlbnQ1NXZlY3RvcjU1"),
    ("angle55vector55", "YW5nbGU1NXZlY3RvcjU1"),
    ("angle55processor55", "YW5nbGU1NXByb2Nlc3NvcjU1"),
    ("angle55reasoning55", "YW5nbGU1NXJlYXNvbmluZzU1"),
    ("angle55machine55", "YW5nbGU1NW1hY2hpbmU1NQ"),
    ("universe55machine55", "dW5pdmVyc2U1NW1hY2hpbmU1NQ"),
    ("universe55learning55", "dW5pdmVyc2U1NWxlYXJuaW5nNTU"),
    ("universe55model55", "dW5pdmVyc2U1NW1vZGVsNTU"),
    ("universe55token55", "dW5pdmVyc2U1NXRva2VuNTU"),
    ("memory55token55", "bWVtb3J5NTV0b2tlbjU1"),
    ("memory55prompt55", "bWVtb3J5NTVwcm9tcHQ1NQ"),
    ("memory55session55", "bWVtb3J5NTVzZXNzaW9uNTU"),
    ("memory55library55", "bWVtb3J5NTVsaWJyYXJ5NTU"),
    ("stream55library55", "c3RyZWFtNTVsaWJyYXJ5NTU"),
    ("stream55service55", "c3RyZWFtNTVzZXJ2aWNlNTU"),
    ("stream55gateway55", "c3RyZWFtNTVnYXRld2F5NTU"),
    ("stream55storage55", "c3RyZWFtNTVzdG9yYWdlNTU"),
    ("context55storage55", "Y29udGV4dDU1c3RvcmFnZTU1"),
    ("context55network55", "Y29udGV4dDU1bmV0d29yazU1"),
    ("context55latency55", "Y29udGV4dDU1bGF0ZW5jeTU1"),
    ("context55buffer55", "Y29udGV4dDU1YnVmZmVyNTU"),
    ("knowledge55buffer55", "a25vd2xlZGdlNTVidWZmZXI1NQ"),
    ("knowledge55queue55", "a25vd2xlZGdlNTVxdWV1ZTU1"),
    ("knowledge55worker55", "a25vd2xlZGdlNTV3b3JrZXI1NQ"),
    ("knowledge55kernel55", "a25vd2xlZGdlNTVrZXJuZWw1NQ"),
    ("vector55kernel55", "dmVjdG9yNTVrZXJuZWw1NQ"),
    ("vector55signal55", "dmVjdG9yNTVzaWduYWw1NQ"),
    ("vector55packet55", "dmVjdG9yNTVwYWNrZXQ1NQ"),
    ("vector55router55", "dmVjdG9yNTVyb3V0ZXI1NQ"),
    ("processor55router55", "cHJvY2Vzc29yNTVyb3V0ZXI1NQ"),
    ("processor55cluster55", "cHJvY2Vzc29yNTVjbHVzdGVyNTU"),
    ("processor55mirror55", "cHJvY2Vzc29yNTVtaXJyb3I1NQ"),
    ("processor55filter55", "cHJvY2Vzc29yNTVmaWx0ZXI1NQ"),
    ("reasoning55filter55", "cmVhc29uaW5nNTVmaWx0ZXI1NQ"),
    ("reasoning55ranking55", "cmVhc29uaW5nNTVyYW5raW5nNTU"),
    ("reasoning55encoding55", "cmVhc29uaW5nNTVlbmNvZGluZzU1"),
    ("reasoning55mapping55", "cmVhc29uaW5nNTVtYXBwaW5nNTU"),
    ("machine55mapping55", "bWFjaGluZTU1bWFwcGluZzU1"),
    ("machine55record55", "bWFjaGluZTU1cmVjb3JkNTU"),
    ("machine55candle55", "bWFjaGluZTU1Y2FuZGxlNTU"),
    ("machine55thread55", "bWFjaGluZTU1dGhyZWFkNTU"),
    ("learning55thread55", "bGVhcm5pbmc1NXRocmVhZDU1"),
    ("learning55kitten55", "bGVhcm5pbmc1NWtpdHRlbjU1"),
    ("learning55sitting55", "bGVhcm5pbmc1NXNpdHRpbmc1NQ"),
    ("learning55agent55", "bGVhcm5pbmc1NWFnZW50NTU"),
    ("model55agent55", "bW9kZWw1NWFnZW50NTU"),
    ("model55angle55", "bW9kZWw1NWFuZ2xlNTU"),
    ("model55universe55", "bW9kZWw1NXVuaXZlcnNlNTU"),
    ("model55memory55", "bW9kZWw1NW1lbW9yeTU1"),
    ("token55memory55", "dG9rZW41NW1lbW9yeTU1"),
    ("token55stream55", "dG9rZW41NXN0cmVhbTU1"),
    ("token55context55", "dG9rZW41NWNvbnRleHQ1NQ"),
    ("token55knowledge55", "dG9rZW41NWtub3dsZWRnZTU1"),
    ("prompt55knowledge55", "cHJvbXB0NTVrbm93bGVkZ2U1NQ"),
    ("prompt55vector55", "cHJvbXB0NTV2ZWN0b3I1NQ"),
    ("prompt55processor55", "cHJvbXB0NTVwcm9jZXNzb3I1NQ"),
    ("prompt55reasoning55", "cHJvbXB0NTVyZWFzb25pbmc1NQ"),
    ("session55reasoning55", "c2Vzc2lvbjU1cmVhc29uaW5nNTU"),
    ("session55machine55", "c2Vzc2lvbjU1bWFjaGluZTU1"),
    ("session55learning55", "c2Vzc2lvbjU1bGVhcm5pbmc1NQ"),
    ("session55model55", "c2Vzc2lvbjU1bW9kZWw1NQ"),
    ("library55model55", "bGlicmFyeTU1bW9kZWw1NQ"),
    ("library55token55", "bGlicmFyeTU1dG9rZW41NQ"),
    ("library55prompt55", "bGlicmFyeTU1cHJvbXB0NTU"),
    ("library55session55", "bGlicmFyeTU1c2Vzc2lvbjU1"),
    ("service55session55", "c2VydmljZTU1c2Vzc2lvbjU1"),
    ("service55library55", "c2VydmljZTU1bGlicmFyeTU1"),
    ("service55service55", "c2VydmljZTU1c2VydmljZTU1"),
    ("service55gateway55", "c2VydmljZTU1Z2F0ZXdheTU1"),
    ("gateway55gateway55", "Z2F0ZXdheTU1Z2F0ZXdheTU1"),
    ("gateway55storage55", "Z2F0ZXdheTU1c3RvcmFnZTU1"),
    ("gateway55network55", "Z2F0ZXdheTU1bmV0d29yazU1"),
    ("gateway55latency55", "Z2F0ZXdheTU1bGF0ZW5jeTU1"),
    ("storage55latency55", "c3RvcmFnZTU1bGF0ZW5jeTU1"),
    ("storage55buffer55", "c3RvcmFnZTU1YnVmZmVyNTU"),
    ("storage55queue55", "c3RvcmFnZTU1cXVldWU1NQ"),
    ("storage55worker55", "c3RvcmFnZTU1d29ya2VyNTU"),
    ("network55worker55", "bmV0d29yazU1d29ya2VyNTU"),
    ("network55kernel55", "bmV0d29yazU1a2VybmVsNTU"),
    ("network55signal55", "bmV0d29yazU1c2lnbmFsNTU"),
    ("network55packet55", "bmV0d29yazU1cGFja2V0NTU"),
    ("latency55packet55", "bGF0ZW5jeTU1cGFja2V0NTU"),
    ("latency55router55", "bGF0ZW5jeTU1cm91dGVyNTU"),
    ("latency55cluster55", "bGF0ZW5jeTU1Y2x1c3RlcjU1"),
    ("latency55mirror55", "bGF0ZW5jeTU1bWlycm9yNTU"),
    ("buffer55mirror55", "YnVmZmVyNTVtaXJyb3I1NQ"),
    ("buffer55filter55", "YnVmZmVyNTVmaWx0ZXI1NQ"),
    ("buffer55ranking55", "YnVmZmVyNTVyYW5raW5nNTU"),
    ("buffer55encoding55", "YnVmZmVyNTVlbmNvZGluZzU1"),
    ("queue55encoding55", "cXVldWU1NWVuY29kaW5nNTU"),
    ("queue55mapping55", "cXVldWU1NW1hcHBpbmc1NQ"),
    ("queue55record55", "cXVldWU1NXJlY29yZDU1"),
    ("queue55candle55", "cXVldWU1NWNhbmRsZTU1"),
    ("worker55candle55", "d29ya2VyNTVjYW5kbGU1NQ"),
    ("worker55thread55", "d29ya2VyNTV0aHJlYWQ1NQ"),
    ("worker55kitten55", "d29ya2VyNTVraXR0ZW41NQ"),
    ("worker55sitting55", "d29ya2VyNTVzaXR0aW5nNTU"),
    ("kernel55sitting55", "a2VybmVsNTVzaXR0aW5nNTU"),
    ("kernel55agent55", "a2VybmVsNTVhZ2VudDU1"),
    ("kernel55angle55", "a2VybmVsNTVhbmdsZTU1"),
    ("kernel55universe55", "a2VybmVsNTV1bml2ZXJzZTU1"),
    ("signal55universe55", "c2lnbmFsNTV1bml2ZXJzZTU1"),
    ("signal55memory55", "c2lnbmFsNTVtZW1vcnk1NQ"),
    ("signal55stream55", "c2lnbmFsNTVzdHJlYW01NQ"),
    ("signal55context55", "c2lnbmFsNTVjb250ZXh0NTU"),
    ("packet55context55", "cGFja2V0NTVjb250ZXh0NTU"),
    ("packet55knowledge55", "cGFja2V0NTVrbm93bGVkZ2U1NQ"),
    ("packet55vector55", "cGFja2V0NTV2ZWN0b3I1NQ"),
    ("packet55processor55", "cGFja2V0NTVwcm9jZXNzb3I1NQ"),
    ("router55processor55", "cm91dGVyNTVwcm9jZXNzb3I1NQ"),
    ("router55reasoning55", "cm91dGVyNTVyZWFzb25pbmc1NQ"),
    ("router55machine55", "cm91dGVyNTVtYWNoaW5lNTU"),
    ("router55learning55", "cm91dGVyNTVsZWFybmluZzU1"),
    ("cluster55learning55", "Y2x1c3RlcjU1bGVhcm5pbmc1NQ"),
    ("cluster55model55", "Y2x1c3RlcjU1bW9kZWw1NQ"),
    ("cluster55token55", "Y2x1c3RlcjU1dG9rZW41NQ"),
    ("cluster55prompt55", "Y2x1c3RlcjU1cHJvbXB0NTU"),
    ("mirror55prompt55", "bWlycm9yNTVwcm9tcHQ1NQ"),
    ("mirror55session55", "bWlycm9yNTVzZXNzaW9uNTU"),
    ("mirror55library55", "bWlycm9yNTVsaWJyYXJ5NTU"),
    ("mirror55service55", "bWlycm9yNTVzZXJ2aWNlNTU"),
    ("filter55service55", "ZmlsdGVyNTVzZXJ2aWNlNTU"),
    ("filter55gateway55", "ZmlsdGVyNTVnYXRld2F5NTU"),
    ("filter55storage55", "ZmlsdGVyNTVzdG9yYWdlNTU"),
    ("filter55network55", "ZmlsdGVyNTVuZXR3b3JrNTU"),
    ("ranking55network55", "cmFua2luZzU1bmV0d29yazU1"),
    ("ranking55latency55", "cmFua2luZzU1bGF0ZW5jeTU1"),
    ("ranking55buffer55", "cmFua2luZzU1YnVmZmVyNTU"),
    ("ranking55queue55", "cmFua2luZzU1cXVldWU1NQ"),
    ("encoding55queue55", "ZW5jb2Rpbmc1NXF1ZXVlNTU"),
    ("encoding55worker55", "ZW5jb2Rpbmc1NXdvcmtlcjU1"),
    ("encoding55kernel55", "ZW5jb2Rpbmc1NWtlcm5lbDU1"),
    ("encoding55signal55", "ZW5jb2Rpbmc1NXNpZ25hbDU1"),
    ("mapping55signal55", "bWFwcGluZzU1c2lnbmFsNTU"),
    ("mapping55packet55", "bWFwcGluZzU1cGFja2V0NTU"),
    ("mapping55router55", "bWFwcGluZzU1cm91dGVyNTU"),
    ("mapping55cluster55", "bWFwcGluZzU1Y2x1c3RlcjU1"),
    ("record55cluster55", "cmVjb3JkNTVjbHVzdGVyNTU"),
    ("record55mirror55", "cmVjb3JkNTVtaXJyb3I1NQ"),
    ("record55filter55", "cmVjb3JkNTVmaWx0ZXI1NQ"),
    ("record55ranking55", "cmVjb3JkNTVyYW5raW5nNTU"),
    ("candle55ranking55", "Y2FuZGxlNTVyYW5raW5nNTU"),
    ("candle55encoding55", "Y2FuZGxlNTVlbmNvZGluZzU1"),
    ("candle55mapping55", "Y2FuZGxlNTVtYXBwaW5nNTU"),
    ("candle55record55", "Y2FuZGxlNTVyZWNvcmQ1NQ"),
    ("thread55record55", "dGhyZWFkNTVyZWNvcmQ1NQ"),
    ("thread55candle55", "dGhyZWFkNTVjYW5kbGU1NQ"),
    ("thread55thread55", "dGhyZWFkNTV0aHJlYWQ1NQ"),
    ("thread55kitten55", "dGhyZWFkNTVraXR0ZW41NQ"),
    (
        "round 55: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNTU6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 55: agentuniverse is a framework for multi agents",
        "cm91bmQgNTU6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 55: knowledge stored as vectors enables retrieval",
        "cm91bmQgNTU6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 55: the processor reads the record then stops",
        "cm91bmQgNTU6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 55: a worker pulls the next task from the queue",
        "cm91bmQgNTU6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 55: signals travel through the network layer",
        "cm91bmQgNTU6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 55: the gateway routes each request by policy",
        "cm91bmQgNTU6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 55: memory grows until the buffer is full",
        "cm91bmQgNTU6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 55: the cluster mirrors every packet twice",
        "cm91bmQgNTU6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 55: ranking uses tokens learned from the corpus",
        "cm91bmQgNTU6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 55: a long session ends when the candle dies",
        "cm91bmQgNTU6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 55: encode the prompt then map the result",
        "cm91bmQgNTU6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 55: the kernel wakes the worker at dawn", "cm91bmQgNTU6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 55: service latency drops after the patch",
        "cm91bmQgNTU6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 55: the library caches every vector it sees",
        "cm91bmQgNTU6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 55: agents argue then the debate resolves",
        "cm91bmQgNTU6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 55: the filter keeps only strong matches",
        "cm91bmQgNTU6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 55: the model answers with a short reply",
        "cm91bmQgNTU6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 55: the recorder stores the reasoning trace",
        "cm91bmQgNTU6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 55: the angel watches the processor run", "cm91bmQgNTU6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 55: angle of the vector decides the match",
        "cm91bmQgNTU6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 55: the candle burns twice as long at night",
        "cm91bmQgNTU6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 55: a mirror of the universe in one line",
        "cm91bmQgNTU6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 55: the queue drains before the storm", "cm91bmQgNTU6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
