"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten51kitten51", "a2l0dGVuNTFraXR0ZW41MQ"),
    ("kitten51sitting51", "a2l0dGVuNTFzaXR0aW5nNTE"),
    ("kitten51agent51", "a2l0dGVuNTFhZ2VudDUx"),
    ("kitten51angle51", "a2l0dGVuNTFhbmdsZTUx"),
    ("sitting51angle51", "c2l0dGluZzUxYW5nbGU1MQ"),
    ("sitting51universe51", "c2l0dGluZzUxdW5pdmVyc2U1MQ"),
    ("sitting51memory51", "c2l0dGluZzUxbWVtb3J5NTE"),
    ("sitting51stream51", "c2l0dGluZzUxc3RyZWFtNTE"),
    ("agent51stream51", "YWdlbnQ1MXN0cmVhbTUx"),
    ("agent51context51", "YWdlbnQ1MWNvbnRleHQ1MQ"),
    ("agent51knowledge51", "YWdlbnQ1MWtub3dsZWRnZTUx"),
    ("agent51vector51", "YWdlbnQ1MXZlY3RvcjUx"),
    ("angle51vector51", "YW5nbGU1MXZlY3RvcjUx"),
    ("angle51processor51", "YW5nbGU1MXByb2Nlc3NvcjUx"),
    ("angle51reasoning51", "YW5nbGU1MXJlYXNvbmluZzUx"),
    ("angle51machine51", "YW5nbGU1MW1hY2hpbmU1MQ"),
    ("universe51machine51", "dW5pdmVyc2U1MW1hY2hpbmU1MQ"),
    ("universe51learning51", "dW5pdmVyc2U1MWxlYXJuaW5nNTE"),
    ("universe51model51", "dW5pdmVyc2U1MW1vZGVsNTE"),
    ("universe51token51", "dW5pdmVyc2U1MXRva2VuNTE"),
    ("memory51token51", "bWVtb3J5NTF0b2tlbjUx"),
    ("memory51prompt51", "bWVtb3J5NTFwcm9tcHQ1MQ"),
    ("memory51session51", "bWVtb3J5NTFzZXNzaW9uNTE"),
    ("memory51library51", "bWVtb3J5NTFsaWJyYXJ5NTE"),
    ("stream51library51", "c3RyZWFtNTFsaWJyYXJ5NTE"),
    ("stream51service51", "c3RyZWFtNTFzZXJ2aWNlNTE"),
    ("stream51gateway51", "c3RyZWFtNTFnYXRld2F5NTE"),
    ("stream51storage51", "c3RyZWFtNTFzdG9yYWdlNTE"),
    ("context51storage51", "Y29udGV4dDUxc3RvcmFnZTUx"),
    ("context51network51", "Y29udGV4dDUxbmV0d29yazUx"),
    ("context51latency51", "Y29udGV4dDUxbGF0ZW5jeTUx"),
    ("context51buffer51", "Y29udGV4dDUxYnVmZmVyNTE"),
    ("knowledge51buffer51", "a25vd2xlZGdlNTFidWZmZXI1MQ"),
    ("knowledge51queue51", "a25vd2xlZGdlNTFxdWV1ZTUx"),
    ("knowledge51worker51", "a25vd2xlZGdlNTF3b3JrZXI1MQ"),
    ("knowledge51kernel51", "a25vd2xlZGdlNTFrZXJuZWw1MQ"),
    ("vector51kernel51", "dmVjdG9yNTFrZXJuZWw1MQ"),
    ("vector51signal51", "dmVjdG9yNTFzaWduYWw1MQ"),
    ("vector51packet51", "dmVjdG9yNTFwYWNrZXQ1MQ"),
    ("vector51router51", "dmVjdG9yNTFyb3V0ZXI1MQ"),
    ("processor51router51", "cHJvY2Vzc29yNTFyb3V0ZXI1MQ"),
    ("processor51cluster51", "cHJvY2Vzc29yNTFjbHVzdGVyNTE"),
    ("processor51mirror51", "cHJvY2Vzc29yNTFtaXJyb3I1MQ"),
    ("processor51filter51", "cHJvY2Vzc29yNTFmaWx0ZXI1MQ"),
    ("reasoning51filter51", "cmVhc29uaW5nNTFmaWx0ZXI1MQ"),
    ("reasoning51ranking51", "cmVhc29uaW5nNTFyYW5raW5nNTE"),
    ("reasoning51encoding51", "cmVhc29uaW5nNTFlbmNvZGluZzUx"),
    ("reasoning51mapping51", "cmVhc29uaW5nNTFtYXBwaW5nNTE"),
    ("machine51mapping51", "bWFjaGluZTUxbWFwcGluZzUx"),
    ("machine51record51", "bWFjaGluZTUxcmVjb3JkNTE"),
    ("machine51candle51", "bWFjaGluZTUxY2FuZGxlNTE"),
    ("machine51thread51", "bWFjaGluZTUxdGhyZWFkNTE"),
    ("learning51thread51", "bGVhcm5pbmc1MXRocmVhZDUx"),
    ("learning51kitten51", "bGVhcm5pbmc1MWtpdHRlbjUx"),
    ("learning51sitting51", "bGVhcm5pbmc1MXNpdHRpbmc1MQ"),
    ("learning51agent51", "bGVhcm5pbmc1MWFnZW50NTE"),
    ("model51agent51", "bW9kZWw1MWFnZW50NTE"),
    ("model51angle51", "bW9kZWw1MWFuZ2xlNTE"),
    ("model51universe51", "bW9kZWw1MXVuaXZlcnNlNTE"),
    ("model51memory51", "bW9kZWw1MW1lbW9yeTUx"),
    ("token51memory51", "dG9rZW41MW1lbW9yeTUx"),
    ("token51stream51", "dG9rZW41MXN0cmVhbTUx"),
    ("token51context51", "dG9rZW41MWNvbnRleHQ1MQ"),
    ("token51knowledge51", "dG9rZW41MWtub3dsZWRnZTUx"),
    ("prompt51knowledge51", "cHJvbXB0NTFrbm93bGVkZ2U1MQ"),
    ("prompt51vector51", "cHJvbXB0NTF2ZWN0b3I1MQ"),
    ("prompt51processor51", "cHJvbXB0NTFwcm9jZXNzb3I1MQ"),
    ("prompt51reasoning51", "cHJvbXB0NTFyZWFzb25pbmc1MQ"),
    ("session51reasoning51", "c2Vzc2lvbjUxcmVhc29uaW5nNTE"),
    ("session51machine51", "c2Vzc2lvbjUxbWFjaGluZTUx"),
    ("session51learning51", "c2Vzc2lvbjUxbGVhcm5pbmc1MQ"),
    ("session51model51", "c2Vzc2lvbjUxbW9kZWw1MQ"),
    ("library51model51", "bGlicmFyeTUxbW9kZWw1MQ"),
    ("library51token51", "bGlicmFyeTUxdG9rZW41MQ"),
    ("library51prompt51", "bGlicmFyeTUxcHJvbXB0NTE"),
    ("library51session51", "bGlicmFyeTUxc2Vzc2lvbjUx"),
    ("service51session51", "c2VydmljZTUxc2Vzc2lvbjUx"),
    ("service51library51", "c2VydmljZTUxbGlicmFyeTUx"),
    ("service51service51", "c2VydmljZTUxc2VydmljZTUx"),
    ("service51gateway51", "c2VydmljZTUxZ2F0ZXdheTUx"),
    ("gateway51gateway51", "Z2F0ZXdheTUxZ2F0ZXdheTUx"),
    ("gateway51storage51", "Z2F0ZXdheTUxc3RvcmFnZTUx"),
    ("gateway51network51", "Z2F0ZXdheTUxbmV0d29yazUx"),
    ("gateway51latency51", "Z2F0ZXdheTUxbGF0ZW5jeTUx"),
    ("storage51latency51", "c3RvcmFnZTUxbGF0ZW5jeTUx"),
    ("storage51buffer51", "c3RvcmFnZTUxYnVmZmVyNTE"),
    ("storage51queue51", "c3RvcmFnZTUxcXVldWU1MQ"),
    ("storage51worker51", "c3RvcmFnZTUxd29ya2VyNTE"),
    ("network51worker51", "bmV0d29yazUxd29ya2VyNTE"),
    ("network51kernel51", "bmV0d29yazUxa2VybmVsNTE"),
    ("network51signal51", "bmV0d29yazUxc2lnbmFsNTE"),
    ("network51packet51", "bmV0d29yazUxcGFja2V0NTE"),
    ("latency51packet51", "bGF0ZW5jeTUxcGFja2V0NTE"),
    ("latency51router51", "bGF0ZW5jeTUxcm91dGVyNTE"),
    ("latency51cluster51", "bGF0ZW5jeTUxY2x1c3RlcjUx"),
    ("latency51mirror51", "bGF0ZW5jeTUxbWlycm9yNTE"),
    ("buffer51mirror51", "YnVmZmVyNTFtaXJyb3I1MQ"),
    ("buffer51filter51", "YnVmZmVyNTFmaWx0ZXI1MQ"),
    ("buffer51ranking51", "YnVmZmVyNTFyYW5raW5nNTE"),
    ("buffer51encoding51", "YnVmZmVyNTFlbmNvZGluZzUx"),
    ("queue51encoding51", "cXVldWU1MWVuY29kaW5nNTE"),
    ("queue51mapping51", "cXVldWU1MW1hcHBpbmc1MQ"),
    ("queue51record51", "cXVldWU1MXJlY29yZDUx"),
    ("queue51candle51", "cXVldWU1MWNhbmRsZTUx"),
    ("worker51candle51", "d29ya2VyNTFjYW5kbGU1MQ"),
    ("worker51thread51", "d29ya2VyNTF0aHJlYWQ1MQ"),
    ("worker51kitten51", "d29ya2VyNTFraXR0ZW41MQ"),
    ("worker51sitting51", "d29ya2VyNTFzaXR0aW5nNTE"),
    ("kernel51sitting51", "a2VybmVsNTFzaXR0aW5nNTE"),
    ("kernel51agent51", "a2VybmVsNTFhZ2VudDUx"),
    ("kernel51angle51", "a2VybmVsNTFhbmdsZTUx"),
    ("kernel51universe51", "a2VybmVsNTF1bml2ZXJzZTUx"),
    ("signal51universe51", "c2lnbmFsNTF1bml2ZXJzZTUx"),
    ("signal51memory51", "c2lnbmFsNTFtZW1vcnk1MQ"),
    ("signal51stream51", "c2lnbmFsNTFzdHJlYW01MQ"),
    ("signal51context51", "c2lnbmFsNTFjb250ZXh0NTE"),
    ("packet51context51", "cGFja2V0NTFjb250ZXh0NTE"),
    ("packet51knowledge51", "cGFja2V0NTFrbm93bGVkZ2U1MQ"),
    ("packet51vector51", "cGFja2V0NTF2ZWN0b3I1MQ"),
    ("packet51processor51", "cGFja2V0NTFwcm9jZXNzb3I1MQ"),
    ("router51processor51", "cm91dGVyNTFwcm9jZXNzb3I1MQ"),
    ("router51reasoning51", "cm91dGVyNTFyZWFzb25pbmc1MQ"),
    ("router51machine51", "cm91dGVyNTFtYWNoaW5lNTE"),
    ("router51learning51", "cm91dGVyNTFsZWFybmluZzUx"),
    ("cluster51learning51", "Y2x1c3RlcjUxbGVhcm5pbmc1MQ"),
    ("cluster51model51", "Y2x1c3RlcjUxbW9kZWw1MQ"),
    ("cluster51token51", "Y2x1c3RlcjUxdG9rZW41MQ"),
    ("cluster51prompt51", "Y2x1c3RlcjUxcHJvbXB0NTE"),
    ("mirror51prompt51", "bWlycm9yNTFwcm9tcHQ1MQ"),
    ("mirror51session51", "bWlycm9yNTFzZXNzaW9uNTE"),
    ("mirror51library51", "bWlycm9yNTFsaWJyYXJ5NTE"),
    ("mirror51service51", "bWlycm9yNTFzZXJ2aWNlNTE"),
    ("filter51service51", "ZmlsdGVyNTFzZXJ2aWNlNTE"),
    ("filter51gateway51", "ZmlsdGVyNTFnYXRld2F5NTE"),
    ("filter51storage51", "ZmlsdGVyNTFzdG9yYWdlNTE"),
    ("filter51network51", "ZmlsdGVyNTFuZXR3b3JrNTE"),
    ("ranking51network51", "cmFua2luZzUxbmV0d29yazUx"),
    ("ranking51latency51", "cmFua2luZzUxbGF0ZW5jeTUx"),
    ("ranking51buffer51", "cmFua2luZzUxYnVmZmVyNTE"),
    ("ranking51queue51", "cmFua2luZzUxcXVldWU1MQ"),
    ("encoding51queue51", "ZW5jb2Rpbmc1MXF1ZXVlNTE"),
    ("encoding51worker51", "ZW5jb2Rpbmc1MXdvcmtlcjUx"),
    ("encoding51kernel51", "ZW5jb2Rpbmc1MWtlcm5lbDUx"),
    ("encoding51signal51", "ZW5jb2Rpbmc1MXNpZ25hbDUx"),
    ("mapping51signal51", "bWFwcGluZzUxc2lnbmFsNTE"),
    ("mapping51packet51", "bWFwcGluZzUxcGFja2V0NTE"),
    ("mapping51router51", "bWFwcGluZzUxcm91dGVyNTE"),
    ("mapping51cluster51", "bWFwcGluZzUxY2x1c3RlcjUx"),
    ("record51cluster51", "cmVjb3JkNTFjbHVzdGVyNTE"),
    ("record51mirror51", "cmVjb3JkNTFtaXJyb3I1MQ"),
    ("record51filter51", "cmVjb3JkNTFmaWx0ZXI1MQ"),
    ("record51ranking51", "cmVjb3JkNTFyYW5raW5nNTE"),
    ("candle51ranking51", "Y2FuZGxlNTFyYW5raW5nNTE"),
    ("candle51encoding51", "Y2FuZGxlNTFlbmNvZGluZzUx"),
    ("candle51mapping51", "Y2FuZGxlNTFtYXBwaW5nNTE"),
    ("candle51record51", "Y2FuZGxlNTFyZWNvcmQ1MQ"),
    ("thread51record51", "dGhyZWFkNTFyZWNvcmQ1MQ"),
    ("thread51candle51", "dGhyZWFkNTFjYW5kbGU1MQ"),
    ("thread51thread51", "dGhyZWFkNTF0aHJlYWQ1MQ"),
    ("thread51kitten51", "dGhyZWFkNTFraXR0ZW41MQ"),
    (
        "round 51: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNTE6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 51: agentuniverse is a framework for multi agents",
        "cm91bmQgNTE6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 51: knowledge stored as vectors enables retrieval",
        "cm91bmQgNTE6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 51: the processor reads the record then stops",
        "cm91bmQgNTE6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 51: a worker pulls the next task from the queue",
        "cm91bmQgNTE6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 51: signals travel through the network layer",
        "cm91bmQgNTE6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 51: the gateway routes each request by policy",
        "cm91bmQgNTE6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 51: memory grows until the buffer is full",
        "cm91bmQgNTE6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 51: the cluster mirrors every packet twice",
        "cm91bmQgNTE6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 51: ranking uses tokens learned from the corpus",
        "cm91bmQgNTE6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 51: a long session ends when the candle dies",
        "cm91bmQgNTE6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 51: encode the prompt then map the result",
        "cm91bmQgNTE6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 51: the kernel wakes the worker at dawn", "cm91bmQgNTE6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 51: service latency drops after the patch",
        "cm91bmQgNTE6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 51: the library caches every vector it sees",
        "cm91bmQgNTE6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 51: agents argue then the debate resolves",
        "cm91bmQgNTE6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 51: the filter keeps only strong matches",
        "cm91bmQgNTE6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 51: the model answers with a short reply",
        "cm91bmQgNTE6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 51: the recorder stores the reasoning trace",
        "cm91bmQgNTE6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 51: the angel watches the processor run", "cm91bmQgNTE6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 51: angle of the vector decides the match",
        "cm91bmQgNTE6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 51: the candle burns twice as long at night",
        "cm91bmQgNTE6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 51: a mirror of the universe in one line",
        "cm91bmQgNTE6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 51: the queue drains before the storm", "cm91bmQgNTE6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
