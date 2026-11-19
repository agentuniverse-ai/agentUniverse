"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten10kitten10", "a2l0dGVuMTBraXR0ZW4xMA"),
    ("kitten10sitting10", "a2l0dGVuMTBzaXR0aW5nMTA"),
    ("kitten10agent10", "a2l0dGVuMTBhZ2VudDEw"),
    ("kitten10angle10", "a2l0dGVuMTBhbmdsZTEw"),
    ("sitting10angle10", "c2l0dGluZzEwYW5nbGUxMA"),
    ("sitting10universe10", "c2l0dGluZzEwdW5pdmVyc2UxMA"),
    ("sitting10memory10", "c2l0dGluZzEwbWVtb3J5MTA"),
    ("sitting10stream10", "c2l0dGluZzEwc3RyZWFtMTA"),
    ("agent10stream10", "YWdlbnQxMHN0cmVhbTEw"),
    ("agent10context10", "YWdlbnQxMGNvbnRleHQxMA"),
    ("agent10knowledge10", "YWdlbnQxMGtub3dsZWRnZTEw"),
    ("agent10vector10", "YWdlbnQxMHZlY3RvcjEw"),
    ("angle10vector10", "YW5nbGUxMHZlY3RvcjEw"),
    ("angle10processor10", "YW5nbGUxMHByb2Nlc3NvcjEw"),
    ("angle10reasoning10", "YW5nbGUxMHJlYXNvbmluZzEw"),
    ("angle10machine10", "YW5nbGUxMG1hY2hpbmUxMA"),
    ("universe10machine10", "dW5pdmVyc2UxMG1hY2hpbmUxMA"),
    ("universe10learning10", "dW5pdmVyc2UxMGxlYXJuaW5nMTA"),
    ("universe10model10", "dW5pdmVyc2UxMG1vZGVsMTA"),
    ("universe10token10", "dW5pdmVyc2UxMHRva2VuMTA"),
    ("memory10token10", "bWVtb3J5MTB0b2tlbjEw"),
    ("memory10prompt10", "bWVtb3J5MTBwcm9tcHQxMA"),
    ("memory10session10", "bWVtb3J5MTBzZXNzaW9uMTA"),
    ("memory10library10", "bWVtb3J5MTBsaWJyYXJ5MTA"),
    ("stream10library10", "c3RyZWFtMTBsaWJyYXJ5MTA"),
    ("stream10service10", "c3RyZWFtMTBzZXJ2aWNlMTA"),
    ("stream10gateway10", "c3RyZWFtMTBnYXRld2F5MTA"),
    ("stream10storage10", "c3RyZWFtMTBzdG9yYWdlMTA"),
    ("context10storage10", "Y29udGV4dDEwc3RvcmFnZTEw"),
    ("context10network10", "Y29udGV4dDEwbmV0d29yazEw"),
    ("context10latency10", "Y29udGV4dDEwbGF0ZW5jeTEw"),
    ("context10buffer10", "Y29udGV4dDEwYnVmZmVyMTA"),
    ("knowledge10buffer10", "a25vd2xlZGdlMTBidWZmZXIxMA"),
    ("knowledge10queue10", "a25vd2xlZGdlMTBxdWV1ZTEw"),
    ("knowledge10worker10", "a25vd2xlZGdlMTB3b3JrZXIxMA"),
    ("knowledge10kernel10", "a25vd2xlZGdlMTBrZXJuZWwxMA"),
    ("vector10kernel10", "dmVjdG9yMTBrZXJuZWwxMA"),
    ("vector10signal10", "dmVjdG9yMTBzaWduYWwxMA"),
    ("vector10packet10", "dmVjdG9yMTBwYWNrZXQxMA"),
    ("vector10router10", "dmVjdG9yMTByb3V0ZXIxMA"),
    ("processor10router10", "cHJvY2Vzc29yMTByb3V0ZXIxMA"),
    ("processor10cluster10", "cHJvY2Vzc29yMTBjbHVzdGVyMTA"),
    ("processor10mirror10", "cHJvY2Vzc29yMTBtaXJyb3IxMA"),
    ("processor10filter10", "cHJvY2Vzc29yMTBmaWx0ZXIxMA"),
    ("reasoning10filter10", "cmVhc29uaW5nMTBmaWx0ZXIxMA"),
    ("reasoning10ranking10", "cmVhc29uaW5nMTByYW5raW5nMTA"),
    ("reasoning10encoding10", "cmVhc29uaW5nMTBlbmNvZGluZzEw"),
    ("reasoning10mapping10", "cmVhc29uaW5nMTBtYXBwaW5nMTA"),
    ("machine10mapping10", "bWFjaGluZTEwbWFwcGluZzEw"),
    ("machine10record10", "bWFjaGluZTEwcmVjb3JkMTA"),
    ("machine10candle10", "bWFjaGluZTEwY2FuZGxlMTA"),
    ("machine10thread10", "bWFjaGluZTEwdGhyZWFkMTA"),
    ("learning10thread10", "bGVhcm5pbmcxMHRocmVhZDEw"),
    ("learning10kitten10", "bGVhcm5pbmcxMGtpdHRlbjEw"),
    ("learning10sitting10", "bGVhcm5pbmcxMHNpdHRpbmcxMA"),
    ("learning10agent10", "bGVhcm5pbmcxMGFnZW50MTA"),
    ("model10agent10", "bW9kZWwxMGFnZW50MTA"),
    ("model10angle10", "bW9kZWwxMGFuZ2xlMTA"),
    ("model10universe10", "bW9kZWwxMHVuaXZlcnNlMTA"),
    ("model10memory10", "bW9kZWwxMG1lbW9yeTEw"),
    ("token10memory10", "dG9rZW4xMG1lbW9yeTEw"),
    ("token10stream10", "dG9rZW4xMHN0cmVhbTEw"),
    ("token10context10", "dG9rZW4xMGNvbnRleHQxMA"),
    ("token10knowledge10", "dG9rZW4xMGtub3dsZWRnZTEw"),
    ("prompt10knowledge10", "cHJvbXB0MTBrbm93bGVkZ2UxMA"),
    ("prompt10vector10", "cHJvbXB0MTB2ZWN0b3IxMA"),
    ("prompt10processor10", "cHJvbXB0MTBwcm9jZXNzb3IxMA"),
    ("prompt10reasoning10", "cHJvbXB0MTByZWFzb25pbmcxMA"),
    ("session10reasoning10", "c2Vzc2lvbjEwcmVhc29uaW5nMTA"),
    ("session10machine10", "c2Vzc2lvbjEwbWFjaGluZTEw"),
    ("session10learning10", "c2Vzc2lvbjEwbGVhcm5pbmcxMA"),
    ("session10model10", "c2Vzc2lvbjEwbW9kZWwxMA"),
    ("library10model10", "bGlicmFyeTEwbW9kZWwxMA"),
    ("library10token10", "bGlicmFyeTEwdG9rZW4xMA"),
    ("library10prompt10", "bGlicmFyeTEwcHJvbXB0MTA"),
    ("library10session10", "bGlicmFyeTEwc2Vzc2lvbjEw"),
    ("service10session10", "c2VydmljZTEwc2Vzc2lvbjEw"),
    ("service10library10", "c2VydmljZTEwbGlicmFyeTEw"),
    ("service10service10", "c2VydmljZTEwc2VydmljZTEw"),
    ("service10gateway10", "c2VydmljZTEwZ2F0ZXdheTEw"),
    ("gateway10gateway10", "Z2F0ZXdheTEwZ2F0ZXdheTEw"),
    ("gateway10storage10", "Z2F0ZXdheTEwc3RvcmFnZTEw"),
    ("gateway10network10", "Z2F0ZXdheTEwbmV0d29yazEw"),
    ("gateway10latency10", "Z2F0ZXdheTEwbGF0ZW5jeTEw"),
    ("storage10latency10", "c3RvcmFnZTEwbGF0ZW5jeTEw"),
    ("storage10buffer10", "c3RvcmFnZTEwYnVmZmVyMTA"),
    ("storage10queue10", "c3RvcmFnZTEwcXVldWUxMA"),
    ("storage10worker10", "c3RvcmFnZTEwd29ya2VyMTA"),
    ("network10worker10", "bmV0d29yazEwd29ya2VyMTA"),
    ("network10kernel10", "bmV0d29yazEwa2VybmVsMTA"),
    ("network10signal10", "bmV0d29yazEwc2lnbmFsMTA"),
    ("network10packet10", "bmV0d29yazEwcGFja2V0MTA"),
    ("latency10packet10", "bGF0ZW5jeTEwcGFja2V0MTA"),
    ("latency10router10", "bGF0ZW5jeTEwcm91dGVyMTA"),
    ("latency10cluster10", "bGF0ZW5jeTEwY2x1c3RlcjEw"),
    ("latency10mirror10", "bGF0ZW5jeTEwbWlycm9yMTA"),
    ("buffer10mirror10", "YnVmZmVyMTBtaXJyb3IxMA"),
    ("buffer10filter10", "YnVmZmVyMTBmaWx0ZXIxMA"),
    ("buffer10ranking10", "YnVmZmVyMTByYW5raW5nMTA"),
    ("buffer10encoding10", "YnVmZmVyMTBlbmNvZGluZzEw"),
    ("queue10encoding10", "cXVldWUxMGVuY29kaW5nMTA"),
    ("queue10mapping10", "cXVldWUxMG1hcHBpbmcxMA"),
    ("queue10record10", "cXVldWUxMHJlY29yZDEw"),
    ("queue10candle10", "cXVldWUxMGNhbmRsZTEw"),
    ("worker10candle10", "d29ya2VyMTBjYW5kbGUxMA"),
    ("worker10thread10", "d29ya2VyMTB0aHJlYWQxMA"),
    ("worker10kitten10", "d29ya2VyMTBraXR0ZW4xMA"),
    ("worker10sitting10", "d29ya2VyMTBzaXR0aW5nMTA"),
    ("kernel10sitting10", "a2VybmVsMTBzaXR0aW5nMTA"),
    ("kernel10agent10", "a2VybmVsMTBhZ2VudDEw"),
    ("kernel10angle10", "a2VybmVsMTBhbmdsZTEw"),
    ("kernel10universe10", "a2VybmVsMTB1bml2ZXJzZTEw"),
    ("signal10universe10", "c2lnbmFsMTB1bml2ZXJzZTEw"),
    ("signal10memory10", "c2lnbmFsMTBtZW1vcnkxMA"),
    ("signal10stream10", "c2lnbmFsMTBzdHJlYW0xMA"),
    ("signal10context10", "c2lnbmFsMTBjb250ZXh0MTA"),
    ("packet10context10", "cGFja2V0MTBjb250ZXh0MTA"),
    ("packet10knowledge10", "cGFja2V0MTBrbm93bGVkZ2UxMA"),
    ("packet10vector10", "cGFja2V0MTB2ZWN0b3IxMA"),
    ("packet10processor10", "cGFja2V0MTBwcm9jZXNzb3IxMA"),
    ("router10processor10", "cm91dGVyMTBwcm9jZXNzb3IxMA"),
    ("router10reasoning10", "cm91dGVyMTByZWFzb25pbmcxMA"),
    ("router10machine10", "cm91dGVyMTBtYWNoaW5lMTA"),
    ("router10learning10", "cm91dGVyMTBsZWFybmluZzEw"),
    ("cluster10learning10", "Y2x1c3RlcjEwbGVhcm5pbmcxMA"),
    ("cluster10model10", "Y2x1c3RlcjEwbW9kZWwxMA"),
    ("cluster10token10", "Y2x1c3RlcjEwdG9rZW4xMA"),
    ("cluster10prompt10", "Y2x1c3RlcjEwcHJvbXB0MTA"),
    ("mirror10prompt10", "bWlycm9yMTBwcm9tcHQxMA"),
    ("mirror10session10", "bWlycm9yMTBzZXNzaW9uMTA"),
    ("mirror10library10", "bWlycm9yMTBsaWJyYXJ5MTA"),
    ("mirror10service10", "bWlycm9yMTBzZXJ2aWNlMTA"),
    ("filter10service10", "ZmlsdGVyMTBzZXJ2aWNlMTA"),
    ("filter10gateway10", "ZmlsdGVyMTBnYXRld2F5MTA"),
    ("filter10storage10", "ZmlsdGVyMTBzdG9yYWdlMTA"),
    ("filter10network10", "ZmlsdGVyMTBuZXR3b3JrMTA"),
    ("ranking10network10", "cmFua2luZzEwbmV0d29yazEw"),
    ("ranking10latency10", "cmFua2luZzEwbGF0ZW5jeTEw"),
    ("ranking10buffer10", "cmFua2luZzEwYnVmZmVyMTA"),
    ("ranking10queue10", "cmFua2luZzEwcXVldWUxMA"),
    ("encoding10queue10", "ZW5jb2RpbmcxMHF1ZXVlMTA"),
    ("encoding10worker10", "ZW5jb2RpbmcxMHdvcmtlcjEw"),
    ("encoding10kernel10", "ZW5jb2RpbmcxMGtlcm5lbDEw"),
    ("encoding10signal10", "ZW5jb2RpbmcxMHNpZ25hbDEw"),
    ("mapping10signal10", "bWFwcGluZzEwc2lnbmFsMTA"),
    ("mapping10packet10", "bWFwcGluZzEwcGFja2V0MTA"),
    ("mapping10router10", "bWFwcGluZzEwcm91dGVyMTA"),
    ("mapping10cluster10", "bWFwcGluZzEwY2x1c3RlcjEw"),
    ("record10cluster10", "cmVjb3JkMTBjbHVzdGVyMTA"),
    ("record10mirror10", "cmVjb3JkMTBtaXJyb3IxMA"),
    ("record10filter10", "cmVjb3JkMTBmaWx0ZXIxMA"),
    ("record10ranking10", "cmVjb3JkMTByYW5raW5nMTA"),
    ("candle10ranking10", "Y2FuZGxlMTByYW5raW5nMTA"),
    ("candle10encoding10", "Y2FuZGxlMTBlbmNvZGluZzEw"),
    ("candle10mapping10", "Y2FuZGxlMTBtYXBwaW5nMTA"),
    ("candle10record10", "Y2FuZGxlMTByZWNvcmQxMA"),
    ("thread10record10", "dGhyZWFkMTByZWNvcmQxMA"),
    ("thread10candle10", "dGhyZWFkMTBjYW5kbGUxMA"),
    ("thread10thread10", "dGhyZWFkMTB0aHJlYWQxMA"),
    ("thread10kitten10", "dGhyZWFkMTBraXR0ZW4xMA"),
    (
        "round 10: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTA6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 10: agentuniverse is a framework for multi agents",
        "cm91bmQgMTA6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 10: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTA6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 10: the processor reads the record then stops",
        "cm91bmQgMTA6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 10: a worker pulls the next task from the queue",
        "cm91bmQgMTA6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 10: signals travel through the network layer",
        "cm91bmQgMTA6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 10: the gateway routes each request by policy",
        "cm91bmQgMTA6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 10: memory grows until the buffer is full",
        "cm91bmQgMTA6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 10: the cluster mirrors every packet twice",
        "cm91bmQgMTA6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 10: ranking uses tokens learned from the corpus",
        "cm91bmQgMTA6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 10: a long session ends when the candle dies",
        "cm91bmQgMTA6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 10: encode the prompt then map the result",
        "cm91bmQgMTA6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 10: the kernel wakes the worker at dawn", "cm91bmQgMTA6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 10: service latency drops after the patch",
        "cm91bmQgMTA6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 10: the library caches every vector it sees",
        "cm91bmQgMTA6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 10: agents argue then the debate resolves",
        "cm91bmQgMTA6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 10: the filter keeps only strong matches",
        "cm91bmQgMTA6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 10: the model answers with a short reply",
        "cm91bmQgMTA6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 10: the recorder stores the reasoning trace",
        "cm91bmQgMTA6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 10: the angel watches the processor run", "cm91bmQgMTA6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 10: angle of the vector decides the match",
        "cm91bmQgMTA6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 10: the candle burns twice as long at night",
        "cm91bmQgMTA6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 10: a mirror of the universe in one line",
        "cm91bmQgMTA6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 10: the queue drains before the storm", "cm91bmQgMTA6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
