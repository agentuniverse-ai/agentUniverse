"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten50kitten50", "a2l0dGVuNTBraXR0ZW41MA"),
    ("kitten50sitting50", "a2l0dGVuNTBzaXR0aW5nNTA"),
    ("kitten50agent50", "a2l0dGVuNTBhZ2VudDUw"),
    ("kitten50angle50", "a2l0dGVuNTBhbmdsZTUw"),
    ("sitting50angle50", "c2l0dGluZzUwYW5nbGU1MA"),
    ("sitting50universe50", "c2l0dGluZzUwdW5pdmVyc2U1MA"),
    ("sitting50memory50", "c2l0dGluZzUwbWVtb3J5NTA"),
    ("sitting50stream50", "c2l0dGluZzUwc3RyZWFtNTA"),
    ("agent50stream50", "YWdlbnQ1MHN0cmVhbTUw"),
    ("agent50context50", "YWdlbnQ1MGNvbnRleHQ1MA"),
    ("agent50knowledge50", "YWdlbnQ1MGtub3dsZWRnZTUw"),
    ("agent50vector50", "YWdlbnQ1MHZlY3RvcjUw"),
    ("angle50vector50", "YW5nbGU1MHZlY3RvcjUw"),
    ("angle50processor50", "YW5nbGU1MHByb2Nlc3NvcjUw"),
    ("angle50reasoning50", "YW5nbGU1MHJlYXNvbmluZzUw"),
    ("angle50machine50", "YW5nbGU1MG1hY2hpbmU1MA"),
    ("universe50machine50", "dW5pdmVyc2U1MG1hY2hpbmU1MA"),
    ("universe50learning50", "dW5pdmVyc2U1MGxlYXJuaW5nNTA"),
    ("universe50model50", "dW5pdmVyc2U1MG1vZGVsNTA"),
    ("universe50token50", "dW5pdmVyc2U1MHRva2VuNTA"),
    ("memory50token50", "bWVtb3J5NTB0b2tlbjUw"),
    ("memory50prompt50", "bWVtb3J5NTBwcm9tcHQ1MA"),
    ("memory50session50", "bWVtb3J5NTBzZXNzaW9uNTA"),
    ("memory50library50", "bWVtb3J5NTBsaWJyYXJ5NTA"),
    ("stream50library50", "c3RyZWFtNTBsaWJyYXJ5NTA"),
    ("stream50service50", "c3RyZWFtNTBzZXJ2aWNlNTA"),
    ("stream50gateway50", "c3RyZWFtNTBnYXRld2F5NTA"),
    ("stream50storage50", "c3RyZWFtNTBzdG9yYWdlNTA"),
    ("context50storage50", "Y29udGV4dDUwc3RvcmFnZTUw"),
    ("context50network50", "Y29udGV4dDUwbmV0d29yazUw"),
    ("context50latency50", "Y29udGV4dDUwbGF0ZW5jeTUw"),
    ("context50buffer50", "Y29udGV4dDUwYnVmZmVyNTA"),
    ("knowledge50buffer50", "a25vd2xlZGdlNTBidWZmZXI1MA"),
    ("knowledge50queue50", "a25vd2xlZGdlNTBxdWV1ZTUw"),
    ("knowledge50worker50", "a25vd2xlZGdlNTB3b3JrZXI1MA"),
    ("knowledge50kernel50", "a25vd2xlZGdlNTBrZXJuZWw1MA"),
    ("vector50kernel50", "dmVjdG9yNTBrZXJuZWw1MA"),
    ("vector50signal50", "dmVjdG9yNTBzaWduYWw1MA"),
    ("vector50packet50", "dmVjdG9yNTBwYWNrZXQ1MA"),
    ("vector50router50", "dmVjdG9yNTByb3V0ZXI1MA"),
    ("processor50router50", "cHJvY2Vzc29yNTByb3V0ZXI1MA"),
    ("processor50cluster50", "cHJvY2Vzc29yNTBjbHVzdGVyNTA"),
    ("processor50mirror50", "cHJvY2Vzc29yNTBtaXJyb3I1MA"),
    ("processor50filter50", "cHJvY2Vzc29yNTBmaWx0ZXI1MA"),
    ("reasoning50filter50", "cmVhc29uaW5nNTBmaWx0ZXI1MA"),
    ("reasoning50ranking50", "cmVhc29uaW5nNTByYW5raW5nNTA"),
    ("reasoning50encoding50", "cmVhc29uaW5nNTBlbmNvZGluZzUw"),
    ("reasoning50mapping50", "cmVhc29uaW5nNTBtYXBwaW5nNTA"),
    ("machine50mapping50", "bWFjaGluZTUwbWFwcGluZzUw"),
    ("machine50record50", "bWFjaGluZTUwcmVjb3JkNTA"),
    ("machine50candle50", "bWFjaGluZTUwY2FuZGxlNTA"),
    ("machine50thread50", "bWFjaGluZTUwdGhyZWFkNTA"),
    ("learning50thread50", "bGVhcm5pbmc1MHRocmVhZDUw"),
    ("learning50kitten50", "bGVhcm5pbmc1MGtpdHRlbjUw"),
    ("learning50sitting50", "bGVhcm5pbmc1MHNpdHRpbmc1MA"),
    ("learning50agent50", "bGVhcm5pbmc1MGFnZW50NTA"),
    ("model50agent50", "bW9kZWw1MGFnZW50NTA"),
    ("model50angle50", "bW9kZWw1MGFuZ2xlNTA"),
    ("model50universe50", "bW9kZWw1MHVuaXZlcnNlNTA"),
    ("model50memory50", "bW9kZWw1MG1lbW9yeTUw"),
    ("token50memory50", "dG9rZW41MG1lbW9yeTUw"),
    ("token50stream50", "dG9rZW41MHN0cmVhbTUw"),
    ("token50context50", "dG9rZW41MGNvbnRleHQ1MA"),
    ("token50knowledge50", "dG9rZW41MGtub3dsZWRnZTUw"),
    ("prompt50knowledge50", "cHJvbXB0NTBrbm93bGVkZ2U1MA"),
    ("prompt50vector50", "cHJvbXB0NTB2ZWN0b3I1MA"),
    ("prompt50processor50", "cHJvbXB0NTBwcm9jZXNzb3I1MA"),
    ("prompt50reasoning50", "cHJvbXB0NTByZWFzb25pbmc1MA"),
    ("session50reasoning50", "c2Vzc2lvbjUwcmVhc29uaW5nNTA"),
    ("session50machine50", "c2Vzc2lvbjUwbWFjaGluZTUw"),
    ("session50learning50", "c2Vzc2lvbjUwbGVhcm5pbmc1MA"),
    ("session50model50", "c2Vzc2lvbjUwbW9kZWw1MA"),
    ("library50model50", "bGlicmFyeTUwbW9kZWw1MA"),
    ("library50token50", "bGlicmFyeTUwdG9rZW41MA"),
    ("library50prompt50", "bGlicmFyeTUwcHJvbXB0NTA"),
    ("library50session50", "bGlicmFyeTUwc2Vzc2lvbjUw"),
    ("service50session50", "c2VydmljZTUwc2Vzc2lvbjUw"),
    ("service50library50", "c2VydmljZTUwbGlicmFyeTUw"),
    ("service50service50", "c2VydmljZTUwc2VydmljZTUw"),
    ("service50gateway50", "c2VydmljZTUwZ2F0ZXdheTUw"),
    ("gateway50gateway50", "Z2F0ZXdheTUwZ2F0ZXdheTUw"),
    ("gateway50storage50", "Z2F0ZXdheTUwc3RvcmFnZTUw"),
    ("gateway50network50", "Z2F0ZXdheTUwbmV0d29yazUw"),
    ("gateway50latency50", "Z2F0ZXdheTUwbGF0ZW5jeTUw"),
    ("storage50latency50", "c3RvcmFnZTUwbGF0ZW5jeTUw"),
    ("storage50buffer50", "c3RvcmFnZTUwYnVmZmVyNTA"),
    ("storage50queue50", "c3RvcmFnZTUwcXVldWU1MA"),
    ("storage50worker50", "c3RvcmFnZTUwd29ya2VyNTA"),
    ("network50worker50", "bmV0d29yazUwd29ya2VyNTA"),
    ("network50kernel50", "bmV0d29yazUwa2VybmVsNTA"),
    ("network50signal50", "bmV0d29yazUwc2lnbmFsNTA"),
    ("network50packet50", "bmV0d29yazUwcGFja2V0NTA"),
    ("latency50packet50", "bGF0ZW5jeTUwcGFja2V0NTA"),
    ("latency50router50", "bGF0ZW5jeTUwcm91dGVyNTA"),
    ("latency50cluster50", "bGF0ZW5jeTUwY2x1c3RlcjUw"),
    ("latency50mirror50", "bGF0ZW5jeTUwbWlycm9yNTA"),
    ("buffer50mirror50", "YnVmZmVyNTBtaXJyb3I1MA"),
    ("buffer50filter50", "YnVmZmVyNTBmaWx0ZXI1MA"),
    ("buffer50ranking50", "YnVmZmVyNTByYW5raW5nNTA"),
    ("buffer50encoding50", "YnVmZmVyNTBlbmNvZGluZzUw"),
    ("queue50encoding50", "cXVldWU1MGVuY29kaW5nNTA"),
    ("queue50mapping50", "cXVldWU1MG1hcHBpbmc1MA"),
    ("queue50record50", "cXVldWU1MHJlY29yZDUw"),
    ("queue50candle50", "cXVldWU1MGNhbmRsZTUw"),
    ("worker50candle50", "d29ya2VyNTBjYW5kbGU1MA"),
    ("worker50thread50", "d29ya2VyNTB0aHJlYWQ1MA"),
    ("worker50kitten50", "d29ya2VyNTBraXR0ZW41MA"),
    ("worker50sitting50", "d29ya2VyNTBzaXR0aW5nNTA"),
    ("kernel50sitting50", "a2VybmVsNTBzaXR0aW5nNTA"),
    ("kernel50agent50", "a2VybmVsNTBhZ2VudDUw"),
    ("kernel50angle50", "a2VybmVsNTBhbmdsZTUw"),
    ("kernel50universe50", "a2VybmVsNTB1bml2ZXJzZTUw"),
    ("signal50universe50", "c2lnbmFsNTB1bml2ZXJzZTUw"),
    ("signal50memory50", "c2lnbmFsNTBtZW1vcnk1MA"),
    ("signal50stream50", "c2lnbmFsNTBzdHJlYW01MA"),
    ("signal50context50", "c2lnbmFsNTBjb250ZXh0NTA"),
    ("packet50context50", "cGFja2V0NTBjb250ZXh0NTA"),
    ("packet50knowledge50", "cGFja2V0NTBrbm93bGVkZ2U1MA"),
    ("packet50vector50", "cGFja2V0NTB2ZWN0b3I1MA"),
    ("packet50processor50", "cGFja2V0NTBwcm9jZXNzb3I1MA"),
    ("router50processor50", "cm91dGVyNTBwcm9jZXNzb3I1MA"),
    ("router50reasoning50", "cm91dGVyNTByZWFzb25pbmc1MA"),
    ("router50machine50", "cm91dGVyNTBtYWNoaW5lNTA"),
    ("router50learning50", "cm91dGVyNTBsZWFybmluZzUw"),
    ("cluster50learning50", "Y2x1c3RlcjUwbGVhcm5pbmc1MA"),
    ("cluster50model50", "Y2x1c3RlcjUwbW9kZWw1MA"),
    ("cluster50token50", "Y2x1c3RlcjUwdG9rZW41MA"),
    ("cluster50prompt50", "Y2x1c3RlcjUwcHJvbXB0NTA"),
    ("mirror50prompt50", "bWlycm9yNTBwcm9tcHQ1MA"),
    ("mirror50session50", "bWlycm9yNTBzZXNzaW9uNTA"),
    ("mirror50library50", "bWlycm9yNTBsaWJyYXJ5NTA"),
    ("mirror50service50", "bWlycm9yNTBzZXJ2aWNlNTA"),
    ("filter50service50", "ZmlsdGVyNTBzZXJ2aWNlNTA"),
    ("filter50gateway50", "ZmlsdGVyNTBnYXRld2F5NTA"),
    ("filter50storage50", "ZmlsdGVyNTBzdG9yYWdlNTA"),
    ("filter50network50", "ZmlsdGVyNTBuZXR3b3JrNTA"),
    ("ranking50network50", "cmFua2luZzUwbmV0d29yazUw"),
    ("ranking50latency50", "cmFua2luZzUwbGF0ZW5jeTUw"),
    ("ranking50buffer50", "cmFua2luZzUwYnVmZmVyNTA"),
    ("ranking50queue50", "cmFua2luZzUwcXVldWU1MA"),
    ("encoding50queue50", "ZW5jb2Rpbmc1MHF1ZXVlNTA"),
    ("encoding50worker50", "ZW5jb2Rpbmc1MHdvcmtlcjUw"),
    ("encoding50kernel50", "ZW5jb2Rpbmc1MGtlcm5lbDUw"),
    ("encoding50signal50", "ZW5jb2Rpbmc1MHNpZ25hbDUw"),
    ("mapping50signal50", "bWFwcGluZzUwc2lnbmFsNTA"),
    ("mapping50packet50", "bWFwcGluZzUwcGFja2V0NTA"),
    ("mapping50router50", "bWFwcGluZzUwcm91dGVyNTA"),
    ("mapping50cluster50", "bWFwcGluZzUwY2x1c3RlcjUw"),
    ("record50cluster50", "cmVjb3JkNTBjbHVzdGVyNTA"),
    ("record50mirror50", "cmVjb3JkNTBtaXJyb3I1MA"),
    ("record50filter50", "cmVjb3JkNTBmaWx0ZXI1MA"),
    ("record50ranking50", "cmVjb3JkNTByYW5raW5nNTA"),
    ("candle50ranking50", "Y2FuZGxlNTByYW5raW5nNTA"),
    ("candle50encoding50", "Y2FuZGxlNTBlbmNvZGluZzUw"),
    ("candle50mapping50", "Y2FuZGxlNTBtYXBwaW5nNTA"),
    ("candle50record50", "Y2FuZGxlNTByZWNvcmQ1MA"),
    ("thread50record50", "dGhyZWFkNTByZWNvcmQ1MA"),
    ("thread50candle50", "dGhyZWFkNTBjYW5kbGU1MA"),
    ("thread50thread50", "dGhyZWFkNTB0aHJlYWQ1MA"),
    ("thread50kitten50", "dGhyZWFkNTBraXR0ZW41MA"),
    (
        "round 50: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNTA6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 50: agentuniverse is a framework for multi agents",
        "cm91bmQgNTA6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 50: knowledge stored as vectors enables retrieval",
        "cm91bmQgNTA6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 50: the processor reads the record then stops",
        "cm91bmQgNTA6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 50: a worker pulls the next task from the queue",
        "cm91bmQgNTA6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 50: signals travel through the network layer",
        "cm91bmQgNTA6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 50: the gateway routes each request by policy",
        "cm91bmQgNTA6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 50: memory grows until the buffer is full",
        "cm91bmQgNTA6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 50: the cluster mirrors every packet twice",
        "cm91bmQgNTA6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 50: ranking uses tokens learned from the corpus",
        "cm91bmQgNTA6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 50: a long session ends when the candle dies",
        "cm91bmQgNTA6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 50: encode the prompt then map the result",
        "cm91bmQgNTA6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 50: the kernel wakes the worker at dawn", "cm91bmQgNTA6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 50: service latency drops after the patch",
        "cm91bmQgNTA6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 50: the library caches every vector it sees",
        "cm91bmQgNTA6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 50: agents argue then the debate resolves",
        "cm91bmQgNTA6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 50: the filter keeps only strong matches",
        "cm91bmQgNTA6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 50: the model answers with a short reply",
        "cm91bmQgNTA6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 50: the recorder stores the reasoning trace",
        "cm91bmQgNTA6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 50: the angel watches the processor run", "cm91bmQgNTA6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 50: angle of the vector decides the match",
        "cm91bmQgNTA6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 50: the candle burns twice as long at night",
        "cm91bmQgNTA6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 50: a mirror of the universe in one line",
        "cm91bmQgNTA6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 50: the queue drains before the storm", "cm91bmQgNTA6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
