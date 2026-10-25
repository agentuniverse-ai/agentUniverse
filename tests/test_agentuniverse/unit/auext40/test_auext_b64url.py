"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten40kitten40", "a2l0dGVuNDBraXR0ZW40MA"),
    ("kitten40sitting40", "a2l0dGVuNDBzaXR0aW5nNDA"),
    ("kitten40agent40", "a2l0dGVuNDBhZ2VudDQw"),
    ("kitten40angle40", "a2l0dGVuNDBhbmdsZTQw"),
    ("sitting40angle40", "c2l0dGluZzQwYW5nbGU0MA"),
    ("sitting40universe40", "c2l0dGluZzQwdW5pdmVyc2U0MA"),
    ("sitting40memory40", "c2l0dGluZzQwbWVtb3J5NDA"),
    ("sitting40stream40", "c2l0dGluZzQwc3RyZWFtNDA"),
    ("agent40stream40", "YWdlbnQ0MHN0cmVhbTQw"),
    ("agent40context40", "YWdlbnQ0MGNvbnRleHQ0MA"),
    ("agent40knowledge40", "YWdlbnQ0MGtub3dsZWRnZTQw"),
    ("agent40vector40", "YWdlbnQ0MHZlY3RvcjQw"),
    ("angle40vector40", "YW5nbGU0MHZlY3RvcjQw"),
    ("angle40processor40", "YW5nbGU0MHByb2Nlc3NvcjQw"),
    ("angle40reasoning40", "YW5nbGU0MHJlYXNvbmluZzQw"),
    ("angle40machine40", "YW5nbGU0MG1hY2hpbmU0MA"),
    ("universe40machine40", "dW5pdmVyc2U0MG1hY2hpbmU0MA"),
    ("universe40learning40", "dW5pdmVyc2U0MGxlYXJuaW5nNDA"),
    ("universe40model40", "dW5pdmVyc2U0MG1vZGVsNDA"),
    ("universe40token40", "dW5pdmVyc2U0MHRva2VuNDA"),
    ("memory40token40", "bWVtb3J5NDB0b2tlbjQw"),
    ("memory40prompt40", "bWVtb3J5NDBwcm9tcHQ0MA"),
    ("memory40session40", "bWVtb3J5NDBzZXNzaW9uNDA"),
    ("memory40library40", "bWVtb3J5NDBsaWJyYXJ5NDA"),
    ("stream40library40", "c3RyZWFtNDBsaWJyYXJ5NDA"),
    ("stream40service40", "c3RyZWFtNDBzZXJ2aWNlNDA"),
    ("stream40gateway40", "c3RyZWFtNDBnYXRld2F5NDA"),
    ("stream40storage40", "c3RyZWFtNDBzdG9yYWdlNDA"),
    ("context40storage40", "Y29udGV4dDQwc3RvcmFnZTQw"),
    ("context40network40", "Y29udGV4dDQwbmV0d29yazQw"),
    ("context40latency40", "Y29udGV4dDQwbGF0ZW5jeTQw"),
    ("context40buffer40", "Y29udGV4dDQwYnVmZmVyNDA"),
    ("knowledge40buffer40", "a25vd2xlZGdlNDBidWZmZXI0MA"),
    ("knowledge40queue40", "a25vd2xlZGdlNDBxdWV1ZTQw"),
    ("knowledge40worker40", "a25vd2xlZGdlNDB3b3JrZXI0MA"),
    ("knowledge40kernel40", "a25vd2xlZGdlNDBrZXJuZWw0MA"),
    ("vector40kernel40", "dmVjdG9yNDBrZXJuZWw0MA"),
    ("vector40signal40", "dmVjdG9yNDBzaWduYWw0MA"),
    ("vector40packet40", "dmVjdG9yNDBwYWNrZXQ0MA"),
    ("vector40router40", "dmVjdG9yNDByb3V0ZXI0MA"),
    ("processor40router40", "cHJvY2Vzc29yNDByb3V0ZXI0MA"),
    ("processor40cluster40", "cHJvY2Vzc29yNDBjbHVzdGVyNDA"),
    ("processor40mirror40", "cHJvY2Vzc29yNDBtaXJyb3I0MA"),
    ("processor40filter40", "cHJvY2Vzc29yNDBmaWx0ZXI0MA"),
    ("reasoning40filter40", "cmVhc29uaW5nNDBmaWx0ZXI0MA"),
    ("reasoning40ranking40", "cmVhc29uaW5nNDByYW5raW5nNDA"),
    ("reasoning40encoding40", "cmVhc29uaW5nNDBlbmNvZGluZzQw"),
    ("reasoning40mapping40", "cmVhc29uaW5nNDBtYXBwaW5nNDA"),
    ("machine40mapping40", "bWFjaGluZTQwbWFwcGluZzQw"),
    ("machine40record40", "bWFjaGluZTQwcmVjb3JkNDA"),
    ("machine40candle40", "bWFjaGluZTQwY2FuZGxlNDA"),
    ("machine40thread40", "bWFjaGluZTQwdGhyZWFkNDA"),
    ("learning40thread40", "bGVhcm5pbmc0MHRocmVhZDQw"),
    ("learning40kitten40", "bGVhcm5pbmc0MGtpdHRlbjQw"),
    ("learning40sitting40", "bGVhcm5pbmc0MHNpdHRpbmc0MA"),
    ("learning40agent40", "bGVhcm5pbmc0MGFnZW50NDA"),
    ("model40agent40", "bW9kZWw0MGFnZW50NDA"),
    ("model40angle40", "bW9kZWw0MGFuZ2xlNDA"),
    ("model40universe40", "bW9kZWw0MHVuaXZlcnNlNDA"),
    ("model40memory40", "bW9kZWw0MG1lbW9yeTQw"),
    ("token40memory40", "dG9rZW40MG1lbW9yeTQw"),
    ("token40stream40", "dG9rZW40MHN0cmVhbTQw"),
    ("token40context40", "dG9rZW40MGNvbnRleHQ0MA"),
    ("token40knowledge40", "dG9rZW40MGtub3dsZWRnZTQw"),
    ("prompt40knowledge40", "cHJvbXB0NDBrbm93bGVkZ2U0MA"),
    ("prompt40vector40", "cHJvbXB0NDB2ZWN0b3I0MA"),
    ("prompt40processor40", "cHJvbXB0NDBwcm9jZXNzb3I0MA"),
    ("prompt40reasoning40", "cHJvbXB0NDByZWFzb25pbmc0MA"),
    ("session40reasoning40", "c2Vzc2lvbjQwcmVhc29uaW5nNDA"),
    ("session40machine40", "c2Vzc2lvbjQwbWFjaGluZTQw"),
    ("session40learning40", "c2Vzc2lvbjQwbGVhcm5pbmc0MA"),
    ("session40model40", "c2Vzc2lvbjQwbW9kZWw0MA"),
    ("library40model40", "bGlicmFyeTQwbW9kZWw0MA"),
    ("library40token40", "bGlicmFyeTQwdG9rZW40MA"),
    ("library40prompt40", "bGlicmFyeTQwcHJvbXB0NDA"),
    ("library40session40", "bGlicmFyeTQwc2Vzc2lvbjQw"),
    ("service40session40", "c2VydmljZTQwc2Vzc2lvbjQw"),
    ("service40library40", "c2VydmljZTQwbGlicmFyeTQw"),
    ("service40service40", "c2VydmljZTQwc2VydmljZTQw"),
    ("service40gateway40", "c2VydmljZTQwZ2F0ZXdheTQw"),
    ("gateway40gateway40", "Z2F0ZXdheTQwZ2F0ZXdheTQw"),
    ("gateway40storage40", "Z2F0ZXdheTQwc3RvcmFnZTQw"),
    ("gateway40network40", "Z2F0ZXdheTQwbmV0d29yazQw"),
    ("gateway40latency40", "Z2F0ZXdheTQwbGF0ZW5jeTQw"),
    ("storage40latency40", "c3RvcmFnZTQwbGF0ZW5jeTQw"),
    ("storage40buffer40", "c3RvcmFnZTQwYnVmZmVyNDA"),
    ("storage40queue40", "c3RvcmFnZTQwcXVldWU0MA"),
    ("storage40worker40", "c3RvcmFnZTQwd29ya2VyNDA"),
    ("network40worker40", "bmV0d29yazQwd29ya2VyNDA"),
    ("network40kernel40", "bmV0d29yazQwa2VybmVsNDA"),
    ("network40signal40", "bmV0d29yazQwc2lnbmFsNDA"),
    ("network40packet40", "bmV0d29yazQwcGFja2V0NDA"),
    ("latency40packet40", "bGF0ZW5jeTQwcGFja2V0NDA"),
    ("latency40router40", "bGF0ZW5jeTQwcm91dGVyNDA"),
    ("latency40cluster40", "bGF0ZW5jeTQwY2x1c3RlcjQw"),
    ("latency40mirror40", "bGF0ZW5jeTQwbWlycm9yNDA"),
    ("buffer40mirror40", "YnVmZmVyNDBtaXJyb3I0MA"),
    ("buffer40filter40", "YnVmZmVyNDBmaWx0ZXI0MA"),
    ("buffer40ranking40", "YnVmZmVyNDByYW5raW5nNDA"),
    ("buffer40encoding40", "YnVmZmVyNDBlbmNvZGluZzQw"),
    ("queue40encoding40", "cXVldWU0MGVuY29kaW5nNDA"),
    ("queue40mapping40", "cXVldWU0MG1hcHBpbmc0MA"),
    ("queue40record40", "cXVldWU0MHJlY29yZDQw"),
    ("queue40candle40", "cXVldWU0MGNhbmRsZTQw"),
    ("worker40candle40", "d29ya2VyNDBjYW5kbGU0MA"),
    ("worker40thread40", "d29ya2VyNDB0aHJlYWQ0MA"),
    ("worker40kitten40", "d29ya2VyNDBraXR0ZW40MA"),
    ("worker40sitting40", "d29ya2VyNDBzaXR0aW5nNDA"),
    ("kernel40sitting40", "a2VybmVsNDBzaXR0aW5nNDA"),
    ("kernel40agent40", "a2VybmVsNDBhZ2VudDQw"),
    ("kernel40angle40", "a2VybmVsNDBhbmdsZTQw"),
    ("kernel40universe40", "a2VybmVsNDB1bml2ZXJzZTQw"),
    ("signal40universe40", "c2lnbmFsNDB1bml2ZXJzZTQw"),
    ("signal40memory40", "c2lnbmFsNDBtZW1vcnk0MA"),
    ("signal40stream40", "c2lnbmFsNDBzdHJlYW00MA"),
    ("signal40context40", "c2lnbmFsNDBjb250ZXh0NDA"),
    ("packet40context40", "cGFja2V0NDBjb250ZXh0NDA"),
    ("packet40knowledge40", "cGFja2V0NDBrbm93bGVkZ2U0MA"),
    ("packet40vector40", "cGFja2V0NDB2ZWN0b3I0MA"),
    ("packet40processor40", "cGFja2V0NDBwcm9jZXNzb3I0MA"),
    ("router40processor40", "cm91dGVyNDBwcm9jZXNzb3I0MA"),
    ("router40reasoning40", "cm91dGVyNDByZWFzb25pbmc0MA"),
    ("router40machine40", "cm91dGVyNDBtYWNoaW5lNDA"),
    ("router40learning40", "cm91dGVyNDBsZWFybmluZzQw"),
    ("cluster40learning40", "Y2x1c3RlcjQwbGVhcm5pbmc0MA"),
    ("cluster40model40", "Y2x1c3RlcjQwbW9kZWw0MA"),
    ("cluster40token40", "Y2x1c3RlcjQwdG9rZW40MA"),
    ("cluster40prompt40", "Y2x1c3RlcjQwcHJvbXB0NDA"),
    ("mirror40prompt40", "bWlycm9yNDBwcm9tcHQ0MA"),
    ("mirror40session40", "bWlycm9yNDBzZXNzaW9uNDA"),
    ("mirror40library40", "bWlycm9yNDBsaWJyYXJ5NDA"),
    ("mirror40service40", "bWlycm9yNDBzZXJ2aWNlNDA"),
    ("filter40service40", "ZmlsdGVyNDBzZXJ2aWNlNDA"),
    ("filter40gateway40", "ZmlsdGVyNDBnYXRld2F5NDA"),
    ("filter40storage40", "ZmlsdGVyNDBzdG9yYWdlNDA"),
    ("filter40network40", "ZmlsdGVyNDBuZXR3b3JrNDA"),
    ("ranking40network40", "cmFua2luZzQwbmV0d29yazQw"),
    ("ranking40latency40", "cmFua2luZzQwbGF0ZW5jeTQw"),
    ("ranking40buffer40", "cmFua2luZzQwYnVmZmVyNDA"),
    ("ranking40queue40", "cmFua2luZzQwcXVldWU0MA"),
    ("encoding40queue40", "ZW5jb2Rpbmc0MHF1ZXVlNDA"),
    ("encoding40worker40", "ZW5jb2Rpbmc0MHdvcmtlcjQw"),
    ("encoding40kernel40", "ZW5jb2Rpbmc0MGtlcm5lbDQw"),
    ("encoding40signal40", "ZW5jb2Rpbmc0MHNpZ25hbDQw"),
    ("mapping40signal40", "bWFwcGluZzQwc2lnbmFsNDA"),
    ("mapping40packet40", "bWFwcGluZzQwcGFja2V0NDA"),
    ("mapping40router40", "bWFwcGluZzQwcm91dGVyNDA"),
    ("mapping40cluster40", "bWFwcGluZzQwY2x1c3RlcjQw"),
    ("record40cluster40", "cmVjb3JkNDBjbHVzdGVyNDA"),
    ("record40mirror40", "cmVjb3JkNDBtaXJyb3I0MA"),
    ("record40filter40", "cmVjb3JkNDBmaWx0ZXI0MA"),
    ("record40ranking40", "cmVjb3JkNDByYW5raW5nNDA"),
    ("candle40ranking40", "Y2FuZGxlNDByYW5raW5nNDA"),
    ("candle40encoding40", "Y2FuZGxlNDBlbmNvZGluZzQw"),
    ("candle40mapping40", "Y2FuZGxlNDBtYXBwaW5nNDA"),
    ("candle40record40", "Y2FuZGxlNDByZWNvcmQ0MA"),
    ("thread40record40", "dGhyZWFkNDByZWNvcmQ0MA"),
    ("thread40candle40", "dGhyZWFkNDBjYW5kbGU0MA"),
    ("thread40thread40", "dGhyZWFkNDB0aHJlYWQ0MA"),
    ("thread40kitten40", "dGhyZWFkNDBraXR0ZW40MA"),
    (
        "round 40: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNDA6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 40: agentuniverse is a framework for multi agents",
        "cm91bmQgNDA6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 40: knowledge stored as vectors enables retrieval",
        "cm91bmQgNDA6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 40: the processor reads the record then stops",
        "cm91bmQgNDA6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 40: a worker pulls the next task from the queue",
        "cm91bmQgNDA6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 40: signals travel through the network layer",
        "cm91bmQgNDA6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 40: the gateway routes each request by policy",
        "cm91bmQgNDA6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 40: memory grows until the buffer is full",
        "cm91bmQgNDA6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 40: the cluster mirrors every packet twice",
        "cm91bmQgNDA6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 40: ranking uses tokens learned from the corpus",
        "cm91bmQgNDA6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 40: a long session ends when the candle dies",
        "cm91bmQgNDA6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 40: encode the prompt then map the result",
        "cm91bmQgNDA6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 40: the kernel wakes the worker at dawn", "cm91bmQgNDA6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 40: service latency drops after the patch",
        "cm91bmQgNDA6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 40: the library caches every vector it sees",
        "cm91bmQgNDA6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 40: agents argue then the debate resolves",
        "cm91bmQgNDA6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 40: the filter keeps only strong matches",
        "cm91bmQgNDA6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 40: the model answers with a short reply",
        "cm91bmQgNDA6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 40: the recorder stores the reasoning trace",
        "cm91bmQgNDA6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 40: the angel watches the processor run", "cm91bmQgNDA6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 40: angle of the vector decides the match",
        "cm91bmQgNDA6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 40: the candle burns twice as long at night",
        "cm91bmQgNDA6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 40: a mirror of the universe in one line",
        "cm91bmQgNDA6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 40: the queue drains before the storm", "cm91bmQgNDA6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
