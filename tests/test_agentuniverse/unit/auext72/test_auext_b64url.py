"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten72kitten72", "a2l0dGVuNzJraXR0ZW43Mg"),
    ("kitten72sitting72", "a2l0dGVuNzJzaXR0aW5nNzI"),
    ("kitten72agent72", "a2l0dGVuNzJhZ2VudDcy"),
    ("kitten72angle72", "a2l0dGVuNzJhbmdsZTcy"),
    ("sitting72angle72", "c2l0dGluZzcyYW5nbGU3Mg"),
    ("sitting72universe72", "c2l0dGluZzcydW5pdmVyc2U3Mg"),
    ("sitting72memory72", "c2l0dGluZzcybWVtb3J5NzI"),
    ("sitting72stream72", "c2l0dGluZzcyc3RyZWFtNzI"),
    ("agent72stream72", "YWdlbnQ3MnN0cmVhbTcy"),
    ("agent72context72", "YWdlbnQ3MmNvbnRleHQ3Mg"),
    ("agent72knowledge72", "YWdlbnQ3Mmtub3dsZWRnZTcy"),
    ("agent72vector72", "YWdlbnQ3MnZlY3Rvcjcy"),
    ("angle72vector72", "YW5nbGU3MnZlY3Rvcjcy"),
    ("angle72processor72", "YW5nbGU3MnByb2Nlc3Nvcjcy"),
    ("angle72reasoning72", "YW5nbGU3MnJlYXNvbmluZzcy"),
    ("angle72machine72", "YW5nbGU3Mm1hY2hpbmU3Mg"),
    ("universe72machine72", "dW5pdmVyc2U3Mm1hY2hpbmU3Mg"),
    ("universe72learning72", "dW5pdmVyc2U3MmxlYXJuaW5nNzI"),
    ("universe72model72", "dW5pdmVyc2U3Mm1vZGVsNzI"),
    ("universe72token72", "dW5pdmVyc2U3MnRva2VuNzI"),
    ("memory72token72", "bWVtb3J5NzJ0b2tlbjcy"),
    ("memory72prompt72", "bWVtb3J5NzJwcm9tcHQ3Mg"),
    ("memory72session72", "bWVtb3J5NzJzZXNzaW9uNzI"),
    ("memory72library72", "bWVtb3J5NzJsaWJyYXJ5NzI"),
    ("stream72library72", "c3RyZWFtNzJsaWJyYXJ5NzI"),
    ("stream72service72", "c3RyZWFtNzJzZXJ2aWNlNzI"),
    ("stream72gateway72", "c3RyZWFtNzJnYXRld2F5NzI"),
    ("stream72storage72", "c3RyZWFtNzJzdG9yYWdlNzI"),
    ("context72storage72", "Y29udGV4dDcyc3RvcmFnZTcy"),
    ("context72network72", "Y29udGV4dDcybmV0d29yazcy"),
    ("context72latency72", "Y29udGV4dDcybGF0ZW5jeTcy"),
    ("context72buffer72", "Y29udGV4dDcyYnVmZmVyNzI"),
    ("knowledge72buffer72", "a25vd2xlZGdlNzJidWZmZXI3Mg"),
    ("knowledge72queue72", "a25vd2xlZGdlNzJxdWV1ZTcy"),
    ("knowledge72worker72", "a25vd2xlZGdlNzJ3b3JrZXI3Mg"),
    ("knowledge72kernel72", "a25vd2xlZGdlNzJrZXJuZWw3Mg"),
    ("vector72kernel72", "dmVjdG9yNzJrZXJuZWw3Mg"),
    ("vector72signal72", "dmVjdG9yNzJzaWduYWw3Mg"),
    ("vector72packet72", "dmVjdG9yNzJwYWNrZXQ3Mg"),
    ("vector72router72", "dmVjdG9yNzJyb3V0ZXI3Mg"),
    ("processor72router72", "cHJvY2Vzc29yNzJyb3V0ZXI3Mg"),
    ("processor72cluster72", "cHJvY2Vzc29yNzJjbHVzdGVyNzI"),
    ("processor72mirror72", "cHJvY2Vzc29yNzJtaXJyb3I3Mg"),
    ("processor72filter72", "cHJvY2Vzc29yNzJmaWx0ZXI3Mg"),
    ("reasoning72filter72", "cmVhc29uaW5nNzJmaWx0ZXI3Mg"),
    ("reasoning72ranking72", "cmVhc29uaW5nNzJyYW5raW5nNzI"),
    ("reasoning72encoding72", "cmVhc29uaW5nNzJlbmNvZGluZzcy"),
    ("reasoning72mapping72", "cmVhc29uaW5nNzJtYXBwaW5nNzI"),
    ("machine72mapping72", "bWFjaGluZTcybWFwcGluZzcy"),
    ("machine72record72", "bWFjaGluZTcycmVjb3JkNzI"),
    ("machine72candle72", "bWFjaGluZTcyY2FuZGxlNzI"),
    ("machine72thread72", "bWFjaGluZTcydGhyZWFkNzI"),
    ("learning72thread72", "bGVhcm5pbmc3MnRocmVhZDcy"),
    ("learning72kitten72", "bGVhcm5pbmc3MmtpdHRlbjcy"),
    ("learning72sitting72", "bGVhcm5pbmc3MnNpdHRpbmc3Mg"),
    ("learning72agent72", "bGVhcm5pbmc3MmFnZW50NzI"),
    ("model72agent72", "bW9kZWw3MmFnZW50NzI"),
    ("model72angle72", "bW9kZWw3MmFuZ2xlNzI"),
    ("model72universe72", "bW9kZWw3MnVuaXZlcnNlNzI"),
    ("model72memory72", "bW9kZWw3Mm1lbW9yeTcy"),
    ("token72memory72", "dG9rZW43Mm1lbW9yeTcy"),
    ("token72stream72", "dG9rZW43MnN0cmVhbTcy"),
    ("token72context72", "dG9rZW43MmNvbnRleHQ3Mg"),
    ("token72knowledge72", "dG9rZW43Mmtub3dsZWRnZTcy"),
    ("prompt72knowledge72", "cHJvbXB0NzJrbm93bGVkZ2U3Mg"),
    ("prompt72vector72", "cHJvbXB0NzJ2ZWN0b3I3Mg"),
    ("prompt72processor72", "cHJvbXB0NzJwcm9jZXNzb3I3Mg"),
    ("prompt72reasoning72", "cHJvbXB0NzJyZWFzb25pbmc3Mg"),
    ("session72reasoning72", "c2Vzc2lvbjcycmVhc29uaW5nNzI"),
    ("session72machine72", "c2Vzc2lvbjcybWFjaGluZTcy"),
    ("session72learning72", "c2Vzc2lvbjcybGVhcm5pbmc3Mg"),
    ("session72model72", "c2Vzc2lvbjcybW9kZWw3Mg"),
    ("library72model72", "bGlicmFyeTcybW9kZWw3Mg"),
    ("library72token72", "bGlicmFyeTcydG9rZW43Mg"),
    ("library72prompt72", "bGlicmFyeTcycHJvbXB0NzI"),
    ("library72session72", "bGlicmFyeTcyc2Vzc2lvbjcy"),
    ("service72session72", "c2VydmljZTcyc2Vzc2lvbjcy"),
    ("service72library72", "c2VydmljZTcybGlicmFyeTcy"),
    ("service72service72", "c2VydmljZTcyc2VydmljZTcy"),
    ("service72gateway72", "c2VydmljZTcyZ2F0ZXdheTcy"),
    ("gateway72gateway72", "Z2F0ZXdheTcyZ2F0ZXdheTcy"),
    ("gateway72storage72", "Z2F0ZXdheTcyc3RvcmFnZTcy"),
    ("gateway72network72", "Z2F0ZXdheTcybmV0d29yazcy"),
    ("gateway72latency72", "Z2F0ZXdheTcybGF0ZW5jeTcy"),
    ("storage72latency72", "c3RvcmFnZTcybGF0ZW5jeTcy"),
    ("storage72buffer72", "c3RvcmFnZTcyYnVmZmVyNzI"),
    ("storage72queue72", "c3RvcmFnZTcycXVldWU3Mg"),
    ("storage72worker72", "c3RvcmFnZTcyd29ya2VyNzI"),
    ("network72worker72", "bmV0d29yazcyd29ya2VyNzI"),
    ("network72kernel72", "bmV0d29yazcya2VybmVsNzI"),
    ("network72signal72", "bmV0d29yazcyc2lnbmFsNzI"),
    ("network72packet72", "bmV0d29yazcycGFja2V0NzI"),
    ("latency72packet72", "bGF0ZW5jeTcycGFja2V0NzI"),
    ("latency72router72", "bGF0ZW5jeTcycm91dGVyNzI"),
    ("latency72cluster72", "bGF0ZW5jeTcyY2x1c3Rlcjcy"),
    ("latency72mirror72", "bGF0ZW5jeTcybWlycm9yNzI"),
    ("buffer72mirror72", "YnVmZmVyNzJtaXJyb3I3Mg"),
    ("buffer72filter72", "YnVmZmVyNzJmaWx0ZXI3Mg"),
    ("buffer72ranking72", "YnVmZmVyNzJyYW5raW5nNzI"),
    ("buffer72encoding72", "YnVmZmVyNzJlbmNvZGluZzcy"),
    ("queue72encoding72", "cXVldWU3MmVuY29kaW5nNzI"),
    ("queue72mapping72", "cXVldWU3Mm1hcHBpbmc3Mg"),
    ("queue72record72", "cXVldWU3MnJlY29yZDcy"),
    ("queue72candle72", "cXVldWU3MmNhbmRsZTcy"),
    ("worker72candle72", "d29ya2VyNzJjYW5kbGU3Mg"),
    ("worker72thread72", "d29ya2VyNzJ0aHJlYWQ3Mg"),
    ("worker72kitten72", "d29ya2VyNzJraXR0ZW43Mg"),
    ("worker72sitting72", "d29ya2VyNzJzaXR0aW5nNzI"),
    ("kernel72sitting72", "a2VybmVsNzJzaXR0aW5nNzI"),
    ("kernel72agent72", "a2VybmVsNzJhZ2VudDcy"),
    ("kernel72angle72", "a2VybmVsNzJhbmdsZTcy"),
    ("kernel72universe72", "a2VybmVsNzJ1bml2ZXJzZTcy"),
    ("signal72universe72", "c2lnbmFsNzJ1bml2ZXJzZTcy"),
    ("signal72memory72", "c2lnbmFsNzJtZW1vcnk3Mg"),
    ("signal72stream72", "c2lnbmFsNzJzdHJlYW03Mg"),
    ("signal72context72", "c2lnbmFsNzJjb250ZXh0NzI"),
    ("packet72context72", "cGFja2V0NzJjb250ZXh0NzI"),
    ("packet72knowledge72", "cGFja2V0NzJrbm93bGVkZ2U3Mg"),
    ("packet72vector72", "cGFja2V0NzJ2ZWN0b3I3Mg"),
    ("packet72processor72", "cGFja2V0NzJwcm9jZXNzb3I3Mg"),
    ("router72processor72", "cm91dGVyNzJwcm9jZXNzb3I3Mg"),
    ("router72reasoning72", "cm91dGVyNzJyZWFzb25pbmc3Mg"),
    ("router72machine72", "cm91dGVyNzJtYWNoaW5lNzI"),
    ("router72learning72", "cm91dGVyNzJsZWFybmluZzcy"),
    ("cluster72learning72", "Y2x1c3RlcjcybGVhcm5pbmc3Mg"),
    ("cluster72model72", "Y2x1c3RlcjcybW9kZWw3Mg"),
    ("cluster72token72", "Y2x1c3RlcjcydG9rZW43Mg"),
    ("cluster72prompt72", "Y2x1c3RlcjcycHJvbXB0NzI"),
    ("mirror72prompt72", "bWlycm9yNzJwcm9tcHQ3Mg"),
    ("mirror72session72", "bWlycm9yNzJzZXNzaW9uNzI"),
    ("mirror72library72", "bWlycm9yNzJsaWJyYXJ5NzI"),
    ("mirror72service72", "bWlycm9yNzJzZXJ2aWNlNzI"),
    ("filter72service72", "ZmlsdGVyNzJzZXJ2aWNlNzI"),
    ("filter72gateway72", "ZmlsdGVyNzJnYXRld2F5NzI"),
    ("filter72storage72", "ZmlsdGVyNzJzdG9yYWdlNzI"),
    ("filter72network72", "ZmlsdGVyNzJuZXR3b3JrNzI"),
    ("ranking72network72", "cmFua2luZzcybmV0d29yazcy"),
    ("ranking72latency72", "cmFua2luZzcybGF0ZW5jeTcy"),
    ("ranking72buffer72", "cmFua2luZzcyYnVmZmVyNzI"),
    ("ranking72queue72", "cmFua2luZzcycXVldWU3Mg"),
    ("encoding72queue72", "ZW5jb2Rpbmc3MnF1ZXVlNzI"),
    ("encoding72worker72", "ZW5jb2Rpbmc3Mndvcmtlcjcy"),
    ("encoding72kernel72", "ZW5jb2Rpbmc3Mmtlcm5lbDcy"),
    ("encoding72signal72", "ZW5jb2Rpbmc3MnNpZ25hbDcy"),
    ("mapping72signal72", "bWFwcGluZzcyc2lnbmFsNzI"),
    ("mapping72packet72", "bWFwcGluZzcycGFja2V0NzI"),
    ("mapping72router72", "bWFwcGluZzcycm91dGVyNzI"),
    ("mapping72cluster72", "bWFwcGluZzcyY2x1c3Rlcjcy"),
    ("record72cluster72", "cmVjb3JkNzJjbHVzdGVyNzI"),
    ("record72mirror72", "cmVjb3JkNzJtaXJyb3I3Mg"),
    ("record72filter72", "cmVjb3JkNzJmaWx0ZXI3Mg"),
    ("record72ranking72", "cmVjb3JkNzJyYW5raW5nNzI"),
    ("candle72ranking72", "Y2FuZGxlNzJyYW5raW5nNzI"),
    ("candle72encoding72", "Y2FuZGxlNzJlbmNvZGluZzcy"),
    ("candle72mapping72", "Y2FuZGxlNzJtYXBwaW5nNzI"),
    ("candle72record72", "Y2FuZGxlNzJyZWNvcmQ3Mg"),
    ("thread72record72", "dGhyZWFkNzJyZWNvcmQ3Mg"),
    ("thread72candle72", "dGhyZWFkNzJjYW5kbGU3Mg"),
    ("thread72thread72", "dGhyZWFkNzJ0aHJlYWQ3Mg"),
    ("thread72kitten72", "dGhyZWFkNzJraXR0ZW43Mg"),
    (
        "round 72: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzI6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 72: agentuniverse is a framework for multi agents",
        "cm91bmQgNzI6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 72: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzI6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 72: the processor reads the record then stops",
        "cm91bmQgNzI6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 72: a worker pulls the next task from the queue",
        "cm91bmQgNzI6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 72: signals travel through the network layer",
        "cm91bmQgNzI6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 72: the gateway routes each request by policy",
        "cm91bmQgNzI6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 72: memory grows until the buffer is full",
        "cm91bmQgNzI6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 72: the cluster mirrors every packet twice",
        "cm91bmQgNzI6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 72: ranking uses tokens learned from the corpus",
        "cm91bmQgNzI6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 72: a long session ends when the candle dies",
        "cm91bmQgNzI6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 72: encode the prompt then map the result",
        "cm91bmQgNzI6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 72: the kernel wakes the worker at dawn", "cm91bmQgNzI6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 72: service latency drops after the patch",
        "cm91bmQgNzI6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 72: the library caches every vector it sees",
        "cm91bmQgNzI6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 72: agents argue then the debate resolves",
        "cm91bmQgNzI6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 72: the filter keeps only strong matches",
        "cm91bmQgNzI6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 72: the model answers with a short reply",
        "cm91bmQgNzI6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 72: the recorder stores the reasoning trace",
        "cm91bmQgNzI6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 72: the angel watches the processor run", "cm91bmQgNzI6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 72: angle of the vector decides the match",
        "cm91bmQgNzI6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 72: the candle burns twice as long at night",
        "cm91bmQgNzI6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 72: a mirror of the universe in one line",
        "cm91bmQgNzI6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 72: the queue drains before the storm", "cm91bmQgNzI6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
