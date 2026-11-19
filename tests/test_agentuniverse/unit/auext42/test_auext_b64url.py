"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten42kitten42", "a2l0dGVuNDJraXR0ZW40Mg"),
    ("kitten42sitting42", "a2l0dGVuNDJzaXR0aW5nNDI"),
    ("kitten42agent42", "a2l0dGVuNDJhZ2VudDQy"),
    ("kitten42angle42", "a2l0dGVuNDJhbmdsZTQy"),
    ("sitting42angle42", "c2l0dGluZzQyYW5nbGU0Mg"),
    ("sitting42universe42", "c2l0dGluZzQydW5pdmVyc2U0Mg"),
    ("sitting42memory42", "c2l0dGluZzQybWVtb3J5NDI"),
    ("sitting42stream42", "c2l0dGluZzQyc3RyZWFtNDI"),
    ("agent42stream42", "YWdlbnQ0MnN0cmVhbTQy"),
    ("agent42context42", "YWdlbnQ0MmNvbnRleHQ0Mg"),
    ("agent42knowledge42", "YWdlbnQ0Mmtub3dsZWRnZTQy"),
    ("agent42vector42", "YWdlbnQ0MnZlY3RvcjQy"),
    ("angle42vector42", "YW5nbGU0MnZlY3RvcjQy"),
    ("angle42processor42", "YW5nbGU0MnByb2Nlc3NvcjQy"),
    ("angle42reasoning42", "YW5nbGU0MnJlYXNvbmluZzQy"),
    ("angle42machine42", "YW5nbGU0Mm1hY2hpbmU0Mg"),
    ("universe42machine42", "dW5pdmVyc2U0Mm1hY2hpbmU0Mg"),
    ("universe42learning42", "dW5pdmVyc2U0MmxlYXJuaW5nNDI"),
    ("universe42model42", "dW5pdmVyc2U0Mm1vZGVsNDI"),
    ("universe42token42", "dW5pdmVyc2U0MnRva2VuNDI"),
    ("memory42token42", "bWVtb3J5NDJ0b2tlbjQy"),
    ("memory42prompt42", "bWVtb3J5NDJwcm9tcHQ0Mg"),
    ("memory42session42", "bWVtb3J5NDJzZXNzaW9uNDI"),
    ("memory42library42", "bWVtb3J5NDJsaWJyYXJ5NDI"),
    ("stream42library42", "c3RyZWFtNDJsaWJyYXJ5NDI"),
    ("stream42service42", "c3RyZWFtNDJzZXJ2aWNlNDI"),
    ("stream42gateway42", "c3RyZWFtNDJnYXRld2F5NDI"),
    ("stream42storage42", "c3RyZWFtNDJzdG9yYWdlNDI"),
    ("context42storage42", "Y29udGV4dDQyc3RvcmFnZTQy"),
    ("context42network42", "Y29udGV4dDQybmV0d29yazQy"),
    ("context42latency42", "Y29udGV4dDQybGF0ZW5jeTQy"),
    ("context42buffer42", "Y29udGV4dDQyYnVmZmVyNDI"),
    ("knowledge42buffer42", "a25vd2xlZGdlNDJidWZmZXI0Mg"),
    ("knowledge42queue42", "a25vd2xlZGdlNDJxdWV1ZTQy"),
    ("knowledge42worker42", "a25vd2xlZGdlNDJ3b3JrZXI0Mg"),
    ("knowledge42kernel42", "a25vd2xlZGdlNDJrZXJuZWw0Mg"),
    ("vector42kernel42", "dmVjdG9yNDJrZXJuZWw0Mg"),
    ("vector42signal42", "dmVjdG9yNDJzaWduYWw0Mg"),
    ("vector42packet42", "dmVjdG9yNDJwYWNrZXQ0Mg"),
    ("vector42router42", "dmVjdG9yNDJyb3V0ZXI0Mg"),
    ("processor42router42", "cHJvY2Vzc29yNDJyb3V0ZXI0Mg"),
    ("processor42cluster42", "cHJvY2Vzc29yNDJjbHVzdGVyNDI"),
    ("processor42mirror42", "cHJvY2Vzc29yNDJtaXJyb3I0Mg"),
    ("processor42filter42", "cHJvY2Vzc29yNDJmaWx0ZXI0Mg"),
    ("reasoning42filter42", "cmVhc29uaW5nNDJmaWx0ZXI0Mg"),
    ("reasoning42ranking42", "cmVhc29uaW5nNDJyYW5raW5nNDI"),
    ("reasoning42encoding42", "cmVhc29uaW5nNDJlbmNvZGluZzQy"),
    ("reasoning42mapping42", "cmVhc29uaW5nNDJtYXBwaW5nNDI"),
    ("machine42mapping42", "bWFjaGluZTQybWFwcGluZzQy"),
    ("machine42record42", "bWFjaGluZTQycmVjb3JkNDI"),
    ("machine42candle42", "bWFjaGluZTQyY2FuZGxlNDI"),
    ("machine42thread42", "bWFjaGluZTQydGhyZWFkNDI"),
    ("learning42thread42", "bGVhcm5pbmc0MnRocmVhZDQy"),
    ("learning42kitten42", "bGVhcm5pbmc0MmtpdHRlbjQy"),
    ("learning42sitting42", "bGVhcm5pbmc0MnNpdHRpbmc0Mg"),
    ("learning42agent42", "bGVhcm5pbmc0MmFnZW50NDI"),
    ("model42agent42", "bW9kZWw0MmFnZW50NDI"),
    ("model42angle42", "bW9kZWw0MmFuZ2xlNDI"),
    ("model42universe42", "bW9kZWw0MnVuaXZlcnNlNDI"),
    ("model42memory42", "bW9kZWw0Mm1lbW9yeTQy"),
    ("token42memory42", "dG9rZW40Mm1lbW9yeTQy"),
    ("token42stream42", "dG9rZW40MnN0cmVhbTQy"),
    ("token42context42", "dG9rZW40MmNvbnRleHQ0Mg"),
    ("token42knowledge42", "dG9rZW40Mmtub3dsZWRnZTQy"),
    ("prompt42knowledge42", "cHJvbXB0NDJrbm93bGVkZ2U0Mg"),
    ("prompt42vector42", "cHJvbXB0NDJ2ZWN0b3I0Mg"),
    ("prompt42processor42", "cHJvbXB0NDJwcm9jZXNzb3I0Mg"),
    ("prompt42reasoning42", "cHJvbXB0NDJyZWFzb25pbmc0Mg"),
    ("session42reasoning42", "c2Vzc2lvbjQycmVhc29uaW5nNDI"),
    ("session42machine42", "c2Vzc2lvbjQybWFjaGluZTQy"),
    ("session42learning42", "c2Vzc2lvbjQybGVhcm5pbmc0Mg"),
    ("session42model42", "c2Vzc2lvbjQybW9kZWw0Mg"),
    ("library42model42", "bGlicmFyeTQybW9kZWw0Mg"),
    ("library42token42", "bGlicmFyeTQydG9rZW40Mg"),
    ("library42prompt42", "bGlicmFyeTQycHJvbXB0NDI"),
    ("library42session42", "bGlicmFyeTQyc2Vzc2lvbjQy"),
    ("service42session42", "c2VydmljZTQyc2Vzc2lvbjQy"),
    ("service42library42", "c2VydmljZTQybGlicmFyeTQy"),
    ("service42service42", "c2VydmljZTQyc2VydmljZTQy"),
    ("service42gateway42", "c2VydmljZTQyZ2F0ZXdheTQy"),
    ("gateway42gateway42", "Z2F0ZXdheTQyZ2F0ZXdheTQy"),
    ("gateway42storage42", "Z2F0ZXdheTQyc3RvcmFnZTQy"),
    ("gateway42network42", "Z2F0ZXdheTQybmV0d29yazQy"),
    ("gateway42latency42", "Z2F0ZXdheTQybGF0ZW5jeTQy"),
    ("storage42latency42", "c3RvcmFnZTQybGF0ZW5jeTQy"),
    ("storage42buffer42", "c3RvcmFnZTQyYnVmZmVyNDI"),
    ("storage42queue42", "c3RvcmFnZTQycXVldWU0Mg"),
    ("storage42worker42", "c3RvcmFnZTQyd29ya2VyNDI"),
    ("network42worker42", "bmV0d29yazQyd29ya2VyNDI"),
    ("network42kernel42", "bmV0d29yazQya2VybmVsNDI"),
    ("network42signal42", "bmV0d29yazQyc2lnbmFsNDI"),
    ("network42packet42", "bmV0d29yazQycGFja2V0NDI"),
    ("latency42packet42", "bGF0ZW5jeTQycGFja2V0NDI"),
    ("latency42router42", "bGF0ZW5jeTQycm91dGVyNDI"),
    ("latency42cluster42", "bGF0ZW5jeTQyY2x1c3RlcjQy"),
    ("latency42mirror42", "bGF0ZW5jeTQybWlycm9yNDI"),
    ("buffer42mirror42", "YnVmZmVyNDJtaXJyb3I0Mg"),
    ("buffer42filter42", "YnVmZmVyNDJmaWx0ZXI0Mg"),
    ("buffer42ranking42", "YnVmZmVyNDJyYW5raW5nNDI"),
    ("buffer42encoding42", "YnVmZmVyNDJlbmNvZGluZzQy"),
    ("queue42encoding42", "cXVldWU0MmVuY29kaW5nNDI"),
    ("queue42mapping42", "cXVldWU0Mm1hcHBpbmc0Mg"),
    ("queue42record42", "cXVldWU0MnJlY29yZDQy"),
    ("queue42candle42", "cXVldWU0MmNhbmRsZTQy"),
    ("worker42candle42", "d29ya2VyNDJjYW5kbGU0Mg"),
    ("worker42thread42", "d29ya2VyNDJ0aHJlYWQ0Mg"),
    ("worker42kitten42", "d29ya2VyNDJraXR0ZW40Mg"),
    ("worker42sitting42", "d29ya2VyNDJzaXR0aW5nNDI"),
    ("kernel42sitting42", "a2VybmVsNDJzaXR0aW5nNDI"),
    ("kernel42agent42", "a2VybmVsNDJhZ2VudDQy"),
    ("kernel42angle42", "a2VybmVsNDJhbmdsZTQy"),
    ("kernel42universe42", "a2VybmVsNDJ1bml2ZXJzZTQy"),
    ("signal42universe42", "c2lnbmFsNDJ1bml2ZXJzZTQy"),
    ("signal42memory42", "c2lnbmFsNDJtZW1vcnk0Mg"),
    ("signal42stream42", "c2lnbmFsNDJzdHJlYW00Mg"),
    ("signal42context42", "c2lnbmFsNDJjb250ZXh0NDI"),
    ("packet42context42", "cGFja2V0NDJjb250ZXh0NDI"),
    ("packet42knowledge42", "cGFja2V0NDJrbm93bGVkZ2U0Mg"),
    ("packet42vector42", "cGFja2V0NDJ2ZWN0b3I0Mg"),
    ("packet42processor42", "cGFja2V0NDJwcm9jZXNzb3I0Mg"),
    ("router42processor42", "cm91dGVyNDJwcm9jZXNzb3I0Mg"),
    ("router42reasoning42", "cm91dGVyNDJyZWFzb25pbmc0Mg"),
    ("router42machine42", "cm91dGVyNDJtYWNoaW5lNDI"),
    ("router42learning42", "cm91dGVyNDJsZWFybmluZzQy"),
    ("cluster42learning42", "Y2x1c3RlcjQybGVhcm5pbmc0Mg"),
    ("cluster42model42", "Y2x1c3RlcjQybW9kZWw0Mg"),
    ("cluster42token42", "Y2x1c3RlcjQydG9rZW40Mg"),
    ("cluster42prompt42", "Y2x1c3RlcjQycHJvbXB0NDI"),
    ("mirror42prompt42", "bWlycm9yNDJwcm9tcHQ0Mg"),
    ("mirror42session42", "bWlycm9yNDJzZXNzaW9uNDI"),
    ("mirror42library42", "bWlycm9yNDJsaWJyYXJ5NDI"),
    ("mirror42service42", "bWlycm9yNDJzZXJ2aWNlNDI"),
    ("filter42service42", "ZmlsdGVyNDJzZXJ2aWNlNDI"),
    ("filter42gateway42", "ZmlsdGVyNDJnYXRld2F5NDI"),
    ("filter42storage42", "ZmlsdGVyNDJzdG9yYWdlNDI"),
    ("filter42network42", "ZmlsdGVyNDJuZXR3b3JrNDI"),
    ("ranking42network42", "cmFua2luZzQybmV0d29yazQy"),
    ("ranking42latency42", "cmFua2luZzQybGF0ZW5jeTQy"),
    ("ranking42buffer42", "cmFua2luZzQyYnVmZmVyNDI"),
    ("ranking42queue42", "cmFua2luZzQycXVldWU0Mg"),
    ("encoding42queue42", "ZW5jb2Rpbmc0MnF1ZXVlNDI"),
    ("encoding42worker42", "ZW5jb2Rpbmc0MndvcmtlcjQy"),
    ("encoding42kernel42", "ZW5jb2Rpbmc0Mmtlcm5lbDQy"),
    ("encoding42signal42", "ZW5jb2Rpbmc0MnNpZ25hbDQy"),
    ("mapping42signal42", "bWFwcGluZzQyc2lnbmFsNDI"),
    ("mapping42packet42", "bWFwcGluZzQycGFja2V0NDI"),
    ("mapping42router42", "bWFwcGluZzQycm91dGVyNDI"),
    ("mapping42cluster42", "bWFwcGluZzQyY2x1c3RlcjQy"),
    ("record42cluster42", "cmVjb3JkNDJjbHVzdGVyNDI"),
    ("record42mirror42", "cmVjb3JkNDJtaXJyb3I0Mg"),
    ("record42filter42", "cmVjb3JkNDJmaWx0ZXI0Mg"),
    ("record42ranking42", "cmVjb3JkNDJyYW5raW5nNDI"),
    ("candle42ranking42", "Y2FuZGxlNDJyYW5raW5nNDI"),
    ("candle42encoding42", "Y2FuZGxlNDJlbmNvZGluZzQy"),
    ("candle42mapping42", "Y2FuZGxlNDJtYXBwaW5nNDI"),
    ("candle42record42", "Y2FuZGxlNDJyZWNvcmQ0Mg"),
    ("thread42record42", "dGhyZWFkNDJyZWNvcmQ0Mg"),
    ("thread42candle42", "dGhyZWFkNDJjYW5kbGU0Mg"),
    ("thread42thread42", "dGhyZWFkNDJ0aHJlYWQ0Mg"),
    ("thread42kitten42", "dGhyZWFkNDJraXR0ZW40Mg"),
    (
        "round 42: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNDI6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 42: agentuniverse is a framework for multi agents",
        "cm91bmQgNDI6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 42: knowledge stored as vectors enables retrieval",
        "cm91bmQgNDI6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 42: the processor reads the record then stops",
        "cm91bmQgNDI6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 42: a worker pulls the next task from the queue",
        "cm91bmQgNDI6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 42: signals travel through the network layer",
        "cm91bmQgNDI6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 42: the gateway routes each request by policy",
        "cm91bmQgNDI6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 42: memory grows until the buffer is full",
        "cm91bmQgNDI6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 42: the cluster mirrors every packet twice",
        "cm91bmQgNDI6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 42: ranking uses tokens learned from the corpus",
        "cm91bmQgNDI6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 42: a long session ends when the candle dies",
        "cm91bmQgNDI6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 42: encode the prompt then map the result",
        "cm91bmQgNDI6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 42: the kernel wakes the worker at dawn", "cm91bmQgNDI6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 42: service latency drops after the patch",
        "cm91bmQgNDI6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 42: the library caches every vector it sees",
        "cm91bmQgNDI6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 42: agents argue then the debate resolves",
        "cm91bmQgNDI6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 42: the filter keeps only strong matches",
        "cm91bmQgNDI6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 42: the model answers with a short reply",
        "cm91bmQgNDI6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 42: the recorder stores the reasoning trace",
        "cm91bmQgNDI6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 42: the angel watches the processor run", "cm91bmQgNDI6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 42: angle of the vector decides the match",
        "cm91bmQgNDI6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 42: the candle burns twice as long at night",
        "cm91bmQgNDI6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 42: a mirror of the universe in one line",
        "cm91bmQgNDI6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 42: the queue drains before the storm", "cm91bmQgNDI6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
