"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten92kitten92", "a2l0dGVuOTJraXR0ZW45Mg"),
    ("kitten92sitting92", "a2l0dGVuOTJzaXR0aW5nOTI"),
    ("kitten92agent92", "a2l0dGVuOTJhZ2VudDky"),
    ("kitten92angle92", "a2l0dGVuOTJhbmdsZTky"),
    ("sitting92angle92", "c2l0dGluZzkyYW5nbGU5Mg"),
    ("sitting92universe92", "c2l0dGluZzkydW5pdmVyc2U5Mg"),
    ("sitting92memory92", "c2l0dGluZzkybWVtb3J5OTI"),
    ("sitting92stream92", "c2l0dGluZzkyc3RyZWFtOTI"),
    ("agent92stream92", "YWdlbnQ5MnN0cmVhbTky"),
    ("agent92context92", "YWdlbnQ5MmNvbnRleHQ5Mg"),
    ("agent92knowledge92", "YWdlbnQ5Mmtub3dsZWRnZTky"),
    ("agent92vector92", "YWdlbnQ5MnZlY3Rvcjky"),
    ("angle92vector92", "YW5nbGU5MnZlY3Rvcjky"),
    ("angle92processor92", "YW5nbGU5MnByb2Nlc3Nvcjky"),
    ("angle92reasoning92", "YW5nbGU5MnJlYXNvbmluZzky"),
    ("angle92machine92", "YW5nbGU5Mm1hY2hpbmU5Mg"),
    ("universe92machine92", "dW5pdmVyc2U5Mm1hY2hpbmU5Mg"),
    ("universe92learning92", "dW5pdmVyc2U5MmxlYXJuaW5nOTI"),
    ("universe92model92", "dW5pdmVyc2U5Mm1vZGVsOTI"),
    ("universe92token92", "dW5pdmVyc2U5MnRva2VuOTI"),
    ("memory92token92", "bWVtb3J5OTJ0b2tlbjky"),
    ("memory92prompt92", "bWVtb3J5OTJwcm9tcHQ5Mg"),
    ("memory92session92", "bWVtb3J5OTJzZXNzaW9uOTI"),
    ("memory92library92", "bWVtb3J5OTJsaWJyYXJ5OTI"),
    ("stream92library92", "c3RyZWFtOTJsaWJyYXJ5OTI"),
    ("stream92service92", "c3RyZWFtOTJzZXJ2aWNlOTI"),
    ("stream92gateway92", "c3RyZWFtOTJnYXRld2F5OTI"),
    ("stream92storage92", "c3RyZWFtOTJzdG9yYWdlOTI"),
    ("context92storage92", "Y29udGV4dDkyc3RvcmFnZTky"),
    ("context92network92", "Y29udGV4dDkybmV0d29yazky"),
    ("context92latency92", "Y29udGV4dDkybGF0ZW5jeTky"),
    ("context92buffer92", "Y29udGV4dDkyYnVmZmVyOTI"),
    ("knowledge92buffer92", "a25vd2xlZGdlOTJidWZmZXI5Mg"),
    ("knowledge92queue92", "a25vd2xlZGdlOTJxdWV1ZTky"),
    ("knowledge92worker92", "a25vd2xlZGdlOTJ3b3JrZXI5Mg"),
    ("knowledge92kernel92", "a25vd2xlZGdlOTJrZXJuZWw5Mg"),
    ("vector92kernel92", "dmVjdG9yOTJrZXJuZWw5Mg"),
    ("vector92signal92", "dmVjdG9yOTJzaWduYWw5Mg"),
    ("vector92packet92", "dmVjdG9yOTJwYWNrZXQ5Mg"),
    ("vector92router92", "dmVjdG9yOTJyb3V0ZXI5Mg"),
    ("processor92router92", "cHJvY2Vzc29yOTJyb3V0ZXI5Mg"),
    ("processor92cluster92", "cHJvY2Vzc29yOTJjbHVzdGVyOTI"),
    ("processor92mirror92", "cHJvY2Vzc29yOTJtaXJyb3I5Mg"),
    ("processor92filter92", "cHJvY2Vzc29yOTJmaWx0ZXI5Mg"),
    ("reasoning92filter92", "cmVhc29uaW5nOTJmaWx0ZXI5Mg"),
    ("reasoning92ranking92", "cmVhc29uaW5nOTJyYW5raW5nOTI"),
    ("reasoning92encoding92", "cmVhc29uaW5nOTJlbmNvZGluZzky"),
    ("reasoning92mapping92", "cmVhc29uaW5nOTJtYXBwaW5nOTI"),
    ("machine92mapping92", "bWFjaGluZTkybWFwcGluZzky"),
    ("machine92record92", "bWFjaGluZTkycmVjb3JkOTI"),
    ("machine92candle92", "bWFjaGluZTkyY2FuZGxlOTI"),
    ("machine92thread92", "bWFjaGluZTkydGhyZWFkOTI"),
    ("learning92thread92", "bGVhcm5pbmc5MnRocmVhZDky"),
    ("learning92kitten92", "bGVhcm5pbmc5MmtpdHRlbjky"),
    ("learning92sitting92", "bGVhcm5pbmc5MnNpdHRpbmc5Mg"),
    ("learning92agent92", "bGVhcm5pbmc5MmFnZW50OTI"),
    ("model92agent92", "bW9kZWw5MmFnZW50OTI"),
    ("model92angle92", "bW9kZWw5MmFuZ2xlOTI"),
    ("model92universe92", "bW9kZWw5MnVuaXZlcnNlOTI"),
    ("model92memory92", "bW9kZWw5Mm1lbW9yeTky"),
    ("token92memory92", "dG9rZW45Mm1lbW9yeTky"),
    ("token92stream92", "dG9rZW45MnN0cmVhbTky"),
    ("token92context92", "dG9rZW45MmNvbnRleHQ5Mg"),
    ("token92knowledge92", "dG9rZW45Mmtub3dsZWRnZTky"),
    ("prompt92knowledge92", "cHJvbXB0OTJrbm93bGVkZ2U5Mg"),
    ("prompt92vector92", "cHJvbXB0OTJ2ZWN0b3I5Mg"),
    ("prompt92processor92", "cHJvbXB0OTJwcm9jZXNzb3I5Mg"),
    ("prompt92reasoning92", "cHJvbXB0OTJyZWFzb25pbmc5Mg"),
    ("session92reasoning92", "c2Vzc2lvbjkycmVhc29uaW5nOTI"),
    ("session92machine92", "c2Vzc2lvbjkybWFjaGluZTky"),
    ("session92learning92", "c2Vzc2lvbjkybGVhcm5pbmc5Mg"),
    ("session92model92", "c2Vzc2lvbjkybW9kZWw5Mg"),
    ("library92model92", "bGlicmFyeTkybW9kZWw5Mg"),
    ("library92token92", "bGlicmFyeTkydG9rZW45Mg"),
    ("library92prompt92", "bGlicmFyeTkycHJvbXB0OTI"),
    ("library92session92", "bGlicmFyeTkyc2Vzc2lvbjky"),
    ("service92session92", "c2VydmljZTkyc2Vzc2lvbjky"),
    ("service92library92", "c2VydmljZTkybGlicmFyeTky"),
    ("service92service92", "c2VydmljZTkyc2VydmljZTky"),
    ("service92gateway92", "c2VydmljZTkyZ2F0ZXdheTky"),
    ("gateway92gateway92", "Z2F0ZXdheTkyZ2F0ZXdheTky"),
    ("gateway92storage92", "Z2F0ZXdheTkyc3RvcmFnZTky"),
    ("gateway92network92", "Z2F0ZXdheTkybmV0d29yazky"),
    ("gateway92latency92", "Z2F0ZXdheTkybGF0ZW5jeTky"),
    ("storage92latency92", "c3RvcmFnZTkybGF0ZW5jeTky"),
    ("storage92buffer92", "c3RvcmFnZTkyYnVmZmVyOTI"),
    ("storage92queue92", "c3RvcmFnZTkycXVldWU5Mg"),
    ("storage92worker92", "c3RvcmFnZTkyd29ya2VyOTI"),
    ("network92worker92", "bmV0d29yazkyd29ya2VyOTI"),
    ("network92kernel92", "bmV0d29yazkya2VybmVsOTI"),
    ("network92signal92", "bmV0d29yazkyc2lnbmFsOTI"),
    ("network92packet92", "bmV0d29yazkycGFja2V0OTI"),
    ("latency92packet92", "bGF0ZW5jeTkycGFja2V0OTI"),
    ("latency92router92", "bGF0ZW5jeTkycm91dGVyOTI"),
    ("latency92cluster92", "bGF0ZW5jeTkyY2x1c3Rlcjky"),
    ("latency92mirror92", "bGF0ZW5jeTkybWlycm9yOTI"),
    ("buffer92mirror92", "YnVmZmVyOTJtaXJyb3I5Mg"),
    ("buffer92filter92", "YnVmZmVyOTJmaWx0ZXI5Mg"),
    ("buffer92ranking92", "YnVmZmVyOTJyYW5raW5nOTI"),
    ("buffer92encoding92", "YnVmZmVyOTJlbmNvZGluZzky"),
    ("queue92encoding92", "cXVldWU5MmVuY29kaW5nOTI"),
    ("queue92mapping92", "cXVldWU5Mm1hcHBpbmc5Mg"),
    ("queue92record92", "cXVldWU5MnJlY29yZDky"),
    ("queue92candle92", "cXVldWU5MmNhbmRsZTky"),
    ("worker92candle92", "d29ya2VyOTJjYW5kbGU5Mg"),
    ("worker92thread92", "d29ya2VyOTJ0aHJlYWQ5Mg"),
    ("worker92kitten92", "d29ya2VyOTJraXR0ZW45Mg"),
    ("worker92sitting92", "d29ya2VyOTJzaXR0aW5nOTI"),
    ("kernel92sitting92", "a2VybmVsOTJzaXR0aW5nOTI"),
    ("kernel92agent92", "a2VybmVsOTJhZ2VudDky"),
    ("kernel92angle92", "a2VybmVsOTJhbmdsZTky"),
    ("kernel92universe92", "a2VybmVsOTJ1bml2ZXJzZTky"),
    ("signal92universe92", "c2lnbmFsOTJ1bml2ZXJzZTky"),
    ("signal92memory92", "c2lnbmFsOTJtZW1vcnk5Mg"),
    ("signal92stream92", "c2lnbmFsOTJzdHJlYW05Mg"),
    ("signal92context92", "c2lnbmFsOTJjb250ZXh0OTI"),
    ("packet92context92", "cGFja2V0OTJjb250ZXh0OTI"),
    ("packet92knowledge92", "cGFja2V0OTJrbm93bGVkZ2U5Mg"),
    ("packet92vector92", "cGFja2V0OTJ2ZWN0b3I5Mg"),
    ("packet92processor92", "cGFja2V0OTJwcm9jZXNzb3I5Mg"),
    ("router92processor92", "cm91dGVyOTJwcm9jZXNzb3I5Mg"),
    ("router92reasoning92", "cm91dGVyOTJyZWFzb25pbmc5Mg"),
    ("router92machine92", "cm91dGVyOTJtYWNoaW5lOTI"),
    ("router92learning92", "cm91dGVyOTJsZWFybmluZzky"),
    ("cluster92learning92", "Y2x1c3RlcjkybGVhcm5pbmc5Mg"),
    ("cluster92model92", "Y2x1c3RlcjkybW9kZWw5Mg"),
    ("cluster92token92", "Y2x1c3RlcjkydG9rZW45Mg"),
    ("cluster92prompt92", "Y2x1c3RlcjkycHJvbXB0OTI"),
    ("mirror92prompt92", "bWlycm9yOTJwcm9tcHQ5Mg"),
    ("mirror92session92", "bWlycm9yOTJzZXNzaW9uOTI"),
    ("mirror92library92", "bWlycm9yOTJsaWJyYXJ5OTI"),
    ("mirror92service92", "bWlycm9yOTJzZXJ2aWNlOTI"),
    ("filter92service92", "ZmlsdGVyOTJzZXJ2aWNlOTI"),
    ("filter92gateway92", "ZmlsdGVyOTJnYXRld2F5OTI"),
    ("filter92storage92", "ZmlsdGVyOTJzdG9yYWdlOTI"),
    ("filter92network92", "ZmlsdGVyOTJuZXR3b3JrOTI"),
    ("ranking92network92", "cmFua2luZzkybmV0d29yazky"),
    ("ranking92latency92", "cmFua2luZzkybGF0ZW5jeTky"),
    ("ranking92buffer92", "cmFua2luZzkyYnVmZmVyOTI"),
    ("ranking92queue92", "cmFua2luZzkycXVldWU5Mg"),
    ("encoding92queue92", "ZW5jb2Rpbmc5MnF1ZXVlOTI"),
    ("encoding92worker92", "ZW5jb2Rpbmc5Mndvcmtlcjky"),
    ("encoding92kernel92", "ZW5jb2Rpbmc5Mmtlcm5lbDky"),
    ("encoding92signal92", "ZW5jb2Rpbmc5MnNpZ25hbDky"),
    ("mapping92signal92", "bWFwcGluZzkyc2lnbmFsOTI"),
    ("mapping92packet92", "bWFwcGluZzkycGFja2V0OTI"),
    ("mapping92router92", "bWFwcGluZzkycm91dGVyOTI"),
    ("mapping92cluster92", "bWFwcGluZzkyY2x1c3Rlcjky"),
    ("record92cluster92", "cmVjb3JkOTJjbHVzdGVyOTI"),
    ("record92mirror92", "cmVjb3JkOTJtaXJyb3I5Mg"),
    ("record92filter92", "cmVjb3JkOTJmaWx0ZXI5Mg"),
    ("record92ranking92", "cmVjb3JkOTJyYW5raW5nOTI"),
    ("candle92ranking92", "Y2FuZGxlOTJyYW5raW5nOTI"),
    ("candle92encoding92", "Y2FuZGxlOTJlbmNvZGluZzky"),
    ("candle92mapping92", "Y2FuZGxlOTJtYXBwaW5nOTI"),
    ("candle92record92", "Y2FuZGxlOTJyZWNvcmQ5Mg"),
    ("thread92record92", "dGhyZWFkOTJyZWNvcmQ5Mg"),
    ("thread92candle92", "dGhyZWFkOTJjYW5kbGU5Mg"),
    ("thread92thread92", "dGhyZWFkOTJ0aHJlYWQ5Mg"),
    ("thread92kitten92", "dGhyZWFkOTJraXR0ZW45Mg"),
    (
        "round 92: the quick brown fox jumps over the lazy dog",
        "cm91bmQgOTI6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 92: agentuniverse is a framework for multi agents",
        "cm91bmQgOTI6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 92: knowledge stored as vectors enables retrieval",
        "cm91bmQgOTI6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 92: the processor reads the record then stops",
        "cm91bmQgOTI6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 92: a worker pulls the next task from the queue",
        "cm91bmQgOTI6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 92: signals travel through the network layer",
        "cm91bmQgOTI6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 92: the gateway routes each request by policy",
        "cm91bmQgOTI6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 92: memory grows until the buffer is full",
        "cm91bmQgOTI6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 92: the cluster mirrors every packet twice",
        "cm91bmQgOTI6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 92: ranking uses tokens learned from the corpus",
        "cm91bmQgOTI6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 92: a long session ends when the candle dies",
        "cm91bmQgOTI6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 92: encode the prompt then map the result",
        "cm91bmQgOTI6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 92: the kernel wakes the worker at dawn", "cm91bmQgOTI6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 92: service latency drops after the patch",
        "cm91bmQgOTI6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 92: the library caches every vector it sees",
        "cm91bmQgOTI6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 92: agents argue then the debate resolves",
        "cm91bmQgOTI6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 92: the filter keeps only strong matches",
        "cm91bmQgOTI6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 92: the model answers with a short reply",
        "cm91bmQgOTI6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 92: the recorder stores the reasoning trace",
        "cm91bmQgOTI6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 92: the angel watches the processor run", "cm91bmQgOTI6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 92: angle of the vector decides the match",
        "cm91bmQgOTI6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 92: the candle burns twice as long at night",
        "cm91bmQgOTI6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 92: a mirror of the universe in one line",
        "cm91bmQgOTI6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 92: the queue drains before the storm", "cm91bmQgOTI6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
