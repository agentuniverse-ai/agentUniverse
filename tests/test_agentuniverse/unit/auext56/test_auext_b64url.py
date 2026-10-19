"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten56kitten56", "a2l0dGVuNTZraXR0ZW41Ng"),
    ("kitten56sitting56", "a2l0dGVuNTZzaXR0aW5nNTY"),
    ("kitten56agent56", "a2l0dGVuNTZhZ2VudDU2"),
    ("kitten56angle56", "a2l0dGVuNTZhbmdsZTU2"),
    ("sitting56angle56", "c2l0dGluZzU2YW5nbGU1Ng"),
    ("sitting56universe56", "c2l0dGluZzU2dW5pdmVyc2U1Ng"),
    ("sitting56memory56", "c2l0dGluZzU2bWVtb3J5NTY"),
    ("sitting56stream56", "c2l0dGluZzU2c3RyZWFtNTY"),
    ("agent56stream56", "YWdlbnQ1NnN0cmVhbTU2"),
    ("agent56context56", "YWdlbnQ1NmNvbnRleHQ1Ng"),
    ("agent56knowledge56", "YWdlbnQ1Nmtub3dsZWRnZTU2"),
    ("agent56vector56", "YWdlbnQ1NnZlY3RvcjU2"),
    ("angle56vector56", "YW5nbGU1NnZlY3RvcjU2"),
    ("angle56processor56", "YW5nbGU1NnByb2Nlc3NvcjU2"),
    ("angle56reasoning56", "YW5nbGU1NnJlYXNvbmluZzU2"),
    ("angle56machine56", "YW5nbGU1Nm1hY2hpbmU1Ng"),
    ("universe56machine56", "dW5pdmVyc2U1Nm1hY2hpbmU1Ng"),
    ("universe56learning56", "dW5pdmVyc2U1NmxlYXJuaW5nNTY"),
    ("universe56model56", "dW5pdmVyc2U1Nm1vZGVsNTY"),
    ("universe56token56", "dW5pdmVyc2U1NnRva2VuNTY"),
    ("memory56token56", "bWVtb3J5NTZ0b2tlbjU2"),
    ("memory56prompt56", "bWVtb3J5NTZwcm9tcHQ1Ng"),
    ("memory56session56", "bWVtb3J5NTZzZXNzaW9uNTY"),
    ("memory56library56", "bWVtb3J5NTZsaWJyYXJ5NTY"),
    ("stream56library56", "c3RyZWFtNTZsaWJyYXJ5NTY"),
    ("stream56service56", "c3RyZWFtNTZzZXJ2aWNlNTY"),
    ("stream56gateway56", "c3RyZWFtNTZnYXRld2F5NTY"),
    ("stream56storage56", "c3RyZWFtNTZzdG9yYWdlNTY"),
    ("context56storage56", "Y29udGV4dDU2c3RvcmFnZTU2"),
    ("context56network56", "Y29udGV4dDU2bmV0d29yazU2"),
    ("context56latency56", "Y29udGV4dDU2bGF0ZW5jeTU2"),
    ("context56buffer56", "Y29udGV4dDU2YnVmZmVyNTY"),
    ("knowledge56buffer56", "a25vd2xlZGdlNTZidWZmZXI1Ng"),
    ("knowledge56queue56", "a25vd2xlZGdlNTZxdWV1ZTU2"),
    ("knowledge56worker56", "a25vd2xlZGdlNTZ3b3JrZXI1Ng"),
    ("knowledge56kernel56", "a25vd2xlZGdlNTZrZXJuZWw1Ng"),
    ("vector56kernel56", "dmVjdG9yNTZrZXJuZWw1Ng"),
    ("vector56signal56", "dmVjdG9yNTZzaWduYWw1Ng"),
    ("vector56packet56", "dmVjdG9yNTZwYWNrZXQ1Ng"),
    ("vector56router56", "dmVjdG9yNTZyb3V0ZXI1Ng"),
    ("processor56router56", "cHJvY2Vzc29yNTZyb3V0ZXI1Ng"),
    ("processor56cluster56", "cHJvY2Vzc29yNTZjbHVzdGVyNTY"),
    ("processor56mirror56", "cHJvY2Vzc29yNTZtaXJyb3I1Ng"),
    ("processor56filter56", "cHJvY2Vzc29yNTZmaWx0ZXI1Ng"),
    ("reasoning56filter56", "cmVhc29uaW5nNTZmaWx0ZXI1Ng"),
    ("reasoning56ranking56", "cmVhc29uaW5nNTZyYW5raW5nNTY"),
    ("reasoning56encoding56", "cmVhc29uaW5nNTZlbmNvZGluZzU2"),
    ("reasoning56mapping56", "cmVhc29uaW5nNTZtYXBwaW5nNTY"),
    ("machine56mapping56", "bWFjaGluZTU2bWFwcGluZzU2"),
    ("machine56record56", "bWFjaGluZTU2cmVjb3JkNTY"),
    ("machine56candle56", "bWFjaGluZTU2Y2FuZGxlNTY"),
    ("machine56thread56", "bWFjaGluZTU2dGhyZWFkNTY"),
    ("learning56thread56", "bGVhcm5pbmc1NnRocmVhZDU2"),
    ("learning56kitten56", "bGVhcm5pbmc1NmtpdHRlbjU2"),
    ("learning56sitting56", "bGVhcm5pbmc1NnNpdHRpbmc1Ng"),
    ("learning56agent56", "bGVhcm5pbmc1NmFnZW50NTY"),
    ("model56agent56", "bW9kZWw1NmFnZW50NTY"),
    ("model56angle56", "bW9kZWw1NmFuZ2xlNTY"),
    ("model56universe56", "bW9kZWw1NnVuaXZlcnNlNTY"),
    ("model56memory56", "bW9kZWw1Nm1lbW9yeTU2"),
    ("token56memory56", "dG9rZW41Nm1lbW9yeTU2"),
    ("token56stream56", "dG9rZW41NnN0cmVhbTU2"),
    ("token56context56", "dG9rZW41NmNvbnRleHQ1Ng"),
    ("token56knowledge56", "dG9rZW41Nmtub3dsZWRnZTU2"),
    ("prompt56knowledge56", "cHJvbXB0NTZrbm93bGVkZ2U1Ng"),
    ("prompt56vector56", "cHJvbXB0NTZ2ZWN0b3I1Ng"),
    ("prompt56processor56", "cHJvbXB0NTZwcm9jZXNzb3I1Ng"),
    ("prompt56reasoning56", "cHJvbXB0NTZyZWFzb25pbmc1Ng"),
    ("session56reasoning56", "c2Vzc2lvbjU2cmVhc29uaW5nNTY"),
    ("session56machine56", "c2Vzc2lvbjU2bWFjaGluZTU2"),
    ("session56learning56", "c2Vzc2lvbjU2bGVhcm5pbmc1Ng"),
    ("session56model56", "c2Vzc2lvbjU2bW9kZWw1Ng"),
    ("library56model56", "bGlicmFyeTU2bW9kZWw1Ng"),
    ("library56token56", "bGlicmFyeTU2dG9rZW41Ng"),
    ("library56prompt56", "bGlicmFyeTU2cHJvbXB0NTY"),
    ("library56session56", "bGlicmFyeTU2c2Vzc2lvbjU2"),
    ("service56session56", "c2VydmljZTU2c2Vzc2lvbjU2"),
    ("service56library56", "c2VydmljZTU2bGlicmFyeTU2"),
    ("service56service56", "c2VydmljZTU2c2VydmljZTU2"),
    ("service56gateway56", "c2VydmljZTU2Z2F0ZXdheTU2"),
    ("gateway56gateway56", "Z2F0ZXdheTU2Z2F0ZXdheTU2"),
    ("gateway56storage56", "Z2F0ZXdheTU2c3RvcmFnZTU2"),
    ("gateway56network56", "Z2F0ZXdheTU2bmV0d29yazU2"),
    ("gateway56latency56", "Z2F0ZXdheTU2bGF0ZW5jeTU2"),
    ("storage56latency56", "c3RvcmFnZTU2bGF0ZW5jeTU2"),
    ("storage56buffer56", "c3RvcmFnZTU2YnVmZmVyNTY"),
    ("storage56queue56", "c3RvcmFnZTU2cXVldWU1Ng"),
    ("storage56worker56", "c3RvcmFnZTU2d29ya2VyNTY"),
    ("network56worker56", "bmV0d29yazU2d29ya2VyNTY"),
    ("network56kernel56", "bmV0d29yazU2a2VybmVsNTY"),
    ("network56signal56", "bmV0d29yazU2c2lnbmFsNTY"),
    ("network56packet56", "bmV0d29yazU2cGFja2V0NTY"),
    ("latency56packet56", "bGF0ZW5jeTU2cGFja2V0NTY"),
    ("latency56router56", "bGF0ZW5jeTU2cm91dGVyNTY"),
    ("latency56cluster56", "bGF0ZW5jeTU2Y2x1c3RlcjU2"),
    ("latency56mirror56", "bGF0ZW5jeTU2bWlycm9yNTY"),
    ("buffer56mirror56", "YnVmZmVyNTZtaXJyb3I1Ng"),
    ("buffer56filter56", "YnVmZmVyNTZmaWx0ZXI1Ng"),
    ("buffer56ranking56", "YnVmZmVyNTZyYW5raW5nNTY"),
    ("buffer56encoding56", "YnVmZmVyNTZlbmNvZGluZzU2"),
    ("queue56encoding56", "cXVldWU1NmVuY29kaW5nNTY"),
    ("queue56mapping56", "cXVldWU1Nm1hcHBpbmc1Ng"),
    ("queue56record56", "cXVldWU1NnJlY29yZDU2"),
    ("queue56candle56", "cXVldWU1NmNhbmRsZTU2"),
    ("worker56candle56", "d29ya2VyNTZjYW5kbGU1Ng"),
    ("worker56thread56", "d29ya2VyNTZ0aHJlYWQ1Ng"),
    ("worker56kitten56", "d29ya2VyNTZraXR0ZW41Ng"),
    ("worker56sitting56", "d29ya2VyNTZzaXR0aW5nNTY"),
    ("kernel56sitting56", "a2VybmVsNTZzaXR0aW5nNTY"),
    ("kernel56agent56", "a2VybmVsNTZhZ2VudDU2"),
    ("kernel56angle56", "a2VybmVsNTZhbmdsZTU2"),
    ("kernel56universe56", "a2VybmVsNTZ1bml2ZXJzZTU2"),
    ("signal56universe56", "c2lnbmFsNTZ1bml2ZXJzZTU2"),
    ("signal56memory56", "c2lnbmFsNTZtZW1vcnk1Ng"),
    ("signal56stream56", "c2lnbmFsNTZzdHJlYW01Ng"),
    ("signal56context56", "c2lnbmFsNTZjb250ZXh0NTY"),
    ("packet56context56", "cGFja2V0NTZjb250ZXh0NTY"),
    ("packet56knowledge56", "cGFja2V0NTZrbm93bGVkZ2U1Ng"),
    ("packet56vector56", "cGFja2V0NTZ2ZWN0b3I1Ng"),
    ("packet56processor56", "cGFja2V0NTZwcm9jZXNzb3I1Ng"),
    ("router56processor56", "cm91dGVyNTZwcm9jZXNzb3I1Ng"),
    ("router56reasoning56", "cm91dGVyNTZyZWFzb25pbmc1Ng"),
    ("router56machine56", "cm91dGVyNTZtYWNoaW5lNTY"),
    ("router56learning56", "cm91dGVyNTZsZWFybmluZzU2"),
    ("cluster56learning56", "Y2x1c3RlcjU2bGVhcm5pbmc1Ng"),
    ("cluster56model56", "Y2x1c3RlcjU2bW9kZWw1Ng"),
    ("cluster56token56", "Y2x1c3RlcjU2dG9rZW41Ng"),
    ("cluster56prompt56", "Y2x1c3RlcjU2cHJvbXB0NTY"),
    ("mirror56prompt56", "bWlycm9yNTZwcm9tcHQ1Ng"),
    ("mirror56session56", "bWlycm9yNTZzZXNzaW9uNTY"),
    ("mirror56library56", "bWlycm9yNTZsaWJyYXJ5NTY"),
    ("mirror56service56", "bWlycm9yNTZzZXJ2aWNlNTY"),
    ("filter56service56", "ZmlsdGVyNTZzZXJ2aWNlNTY"),
    ("filter56gateway56", "ZmlsdGVyNTZnYXRld2F5NTY"),
    ("filter56storage56", "ZmlsdGVyNTZzdG9yYWdlNTY"),
    ("filter56network56", "ZmlsdGVyNTZuZXR3b3JrNTY"),
    ("ranking56network56", "cmFua2luZzU2bmV0d29yazU2"),
    ("ranking56latency56", "cmFua2luZzU2bGF0ZW5jeTU2"),
    ("ranking56buffer56", "cmFua2luZzU2YnVmZmVyNTY"),
    ("ranking56queue56", "cmFua2luZzU2cXVldWU1Ng"),
    ("encoding56queue56", "ZW5jb2Rpbmc1NnF1ZXVlNTY"),
    ("encoding56worker56", "ZW5jb2Rpbmc1NndvcmtlcjU2"),
    ("encoding56kernel56", "ZW5jb2Rpbmc1Nmtlcm5lbDU2"),
    ("encoding56signal56", "ZW5jb2Rpbmc1NnNpZ25hbDU2"),
    ("mapping56signal56", "bWFwcGluZzU2c2lnbmFsNTY"),
    ("mapping56packet56", "bWFwcGluZzU2cGFja2V0NTY"),
    ("mapping56router56", "bWFwcGluZzU2cm91dGVyNTY"),
    ("mapping56cluster56", "bWFwcGluZzU2Y2x1c3RlcjU2"),
    ("record56cluster56", "cmVjb3JkNTZjbHVzdGVyNTY"),
    ("record56mirror56", "cmVjb3JkNTZtaXJyb3I1Ng"),
    ("record56filter56", "cmVjb3JkNTZmaWx0ZXI1Ng"),
    ("record56ranking56", "cmVjb3JkNTZyYW5raW5nNTY"),
    ("candle56ranking56", "Y2FuZGxlNTZyYW5raW5nNTY"),
    ("candle56encoding56", "Y2FuZGxlNTZlbmNvZGluZzU2"),
    ("candle56mapping56", "Y2FuZGxlNTZtYXBwaW5nNTY"),
    ("candle56record56", "Y2FuZGxlNTZyZWNvcmQ1Ng"),
    ("thread56record56", "dGhyZWFkNTZyZWNvcmQ1Ng"),
    ("thread56candle56", "dGhyZWFkNTZjYW5kbGU1Ng"),
    ("thread56thread56", "dGhyZWFkNTZ0aHJlYWQ1Ng"),
    ("thread56kitten56", "dGhyZWFkNTZraXR0ZW41Ng"),
    (
        "round 56: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNTY6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 56: agentuniverse is a framework for multi agents",
        "cm91bmQgNTY6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 56: knowledge stored as vectors enables retrieval",
        "cm91bmQgNTY6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 56: the processor reads the record then stops",
        "cm91bmQgNTY6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 56: a worker pulls the next task from the queue",
        "cm91bmQgNTY6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 56: signals travel through the network layer",
        "cm91bmQgNTY6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 56: the gateway routes each request by policy",
        "cm91bmQgNTY6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 56: memory grows until the buffer is full",
        "cm91bmQgNTY6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 56: the cluster mirrors every packet twice",
        "cm91bmQgNTY6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 56: ranking uses tokens learned from the corpus",
        "cm91bmQgNTY6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 56: a long session ends when the candle dies",
        "cm91bmQgNTY6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 56: encode the prompt then map the result",
        "cm91bmQgNTY6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 56: the kernel wakes the worker at dawn", "cm91bmQgNTY6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 56: service latency drops after the patch",
        "cm91bmQgNTY6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 56: the library caches every vector it sees",
        "cm91bmQgNTY6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 56: agents argue then the debate resolves",
        "cm91bmQgNTY6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 56: the filter keeps only strong matches",
        "cm91bmQgNTY6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 56: the model answers with a short reply",
        "cm91bmQgNTY6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 56: the recorder stores the reasoning trace",
        "cm91bmQgNTY6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 56: the angel watches the processor run", "cm91bmQgNTY6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 56: angle of the vector decides the match",
        "cm91bmQgNTY6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 56: the candle burns twice as long at night",
        "cm91bmQgNTY6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 56: a mirror of the universe in one line",
        "cm91bmQgNTY6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 56: the queue drains before the storm", "cm91bmQgNTY6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
