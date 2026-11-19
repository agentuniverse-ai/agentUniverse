"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten23kitten23", "a2l0dGVuMjNraXR0ZW4yMw"),
    ("kitten23sitting23", "a2l0dGVuMjNzaXR0aW5nMjM"),
    ("kitten23agent23", "a2l0dGVuMjNhZ2VudDIz"),
    ("kitten23angle23", "a2l0dGVuMjNhbmdsZTIz"),
    ("sitting23angle23", "c2l0dGluZzIzYW5nbGUyMw"),
    ("sitting23universe23", "c2l0dGluZzIzdW5pdmVyc2UyMw"),
    ("sitting23memory23", "c2l0dGluZzIzbWVtb3J5MjM"),
    ("sitting23stream23", "c2l0dGluZzIzc3RyZWFtMjM"),
    ("agent23stream23", "YWdlbnQyM3N0cmVhbTIz"),
    ("agent23context23", "YWdlbnQyM2NvbnRleHQyMw"),
    ("agent23knowledge23", "YWdlbnQyM2tub3dsZWRnZTIz"),
    ("agent23vector23", "YWdlbnQyM3ZlY3RvcjIz"),
    ("angle23vector23", "YW5nbGUyM3ZlY3RvcjIz"),
    ("angle23processor23", "YW5nbGUyM3Byb2Nlc3NvcjIz"),
    ("angle23reasoning23", "YW5nbGUyM3JlYXNvbmluZzIz"),
    ("angle23machine23", "YW5nbGUyM21hY2hpbmUyMw"),
    ("universe23machine23", "dW5pdmVyc2UyM21hY2hpbmUyMw"),
    ("universe23learning23", "dW5pdmVyc2UyM2xlYXJuaW5nMjM"),
    ("universe23model23", "dW5pdmVyc2UyM21vZGVsMjM"),
    ("universe23token23", "dW5pdmVyc2UyM3Rva2VuMjM"),
    ("memory23token23", "bWVtb3J5MjN0b2tlbjIz"),
    ("memory23prompt23", "bWVtb3J5MjNwcm9tcHQyMw"),
    ("memory23session23", "bWVtb3J5MjNzZXNzaW9uMjM"),
    ("memory23library23", "bWVtb3J5MjNsaWJyYXJ5MjM"),
    ("stream23library23", "c3RyZWFtMjNsaWJyYXJ5MjM"),
    ("stream23service23", "c3RyZWFtMjNzZXJ2aWNlMjM"),
    ("stream23gateway23", "c3RyZWFtMjNnYXRld2F5MjM"),
    ("stream23storage23", "c3RyZWFtMjNzdG9yYWdlMjM"),
    ("context23storage23", "Y29udGV4dDIzc3RvcmFnZTIz"),
    ("context23network23", "Y29udGV4dDIzbmV0d29yazIz"),
    ("context23latency23", "Y29udGV4dDIzbGF0ZW5jeTIz"),
    ("context23buffer23", "Y29udGV4dDIzYnVmZmVyMjM"),
    ("knowledge23buffer23", "a25vd2xlZGdlMjNidWZmZXIyMw"),
    ("knowledge23queue23", "a25vd2xlZGdlMjNxdWV1ZTIz"),
    ("knowledge23worker23", "a25vd2xlZGdlMjN3b3JrZXIyMw"),
    ("knowledge23kernel23", "a25vd2xlZGdlMjNrZXJuZWwyMw"),
    ("vector23kernel23", "dmVjdG9yMjNrZXJuZWwyMw"),
    ("vector23signal23", "dmVjdG9yMjNzaWduYWwyMw"),
    ("vector23packet23", "dmVjdG9yMjNwYWNrZXQyMw"),
    ("vector23router23", "dmVjdG9yMjNyb3V0ZXIyMw"),
    ("processor23router23", "cHJvY2Vzc29yMjNyb3V0ZXIyMw"),
    ("processor23cluster23", "cHJvY2Vzc29yMjNjbHVzdGVyMjM"),
    ("processor23mirror23", "cHJvY2Vzc29yMjNtaXJyb3IyMw"),
    ("processor23filter23", "cHJvY2Vzc29yMjNmaWx0ZXIyMw"),
    ("reasoning23filter23", "cmVhc29uaW5nMjNmaWx0ZXIyMw"),
    ("reasoning23ranking23", "cmVhc29uaW5nMjNyYW5raW5nMjM"),
    ("reasoning23encoding23", "cmVhc29uaW5nMjNlbmNvZGluZzIz"),
    ("reasoning23mapping23", "cmVhc29uaW5nMjNtYXBwaW5nMjM"),
    ("machine23mapping23", "bWFjaGluZTIzbWFwcGluZzIz"),
    ("machine23record23", "bWFjaGluZTIzcmVjb3JkMjM"),
    ("machine23candle23", "bWFjaGluZTIzY2FuZGxlMjM"),
    ("machine23thread23", "bWFjaGluZTIzdGhyZWFkMjM"),
    ("learning23thread23", "bGVhcm5pbmcyM3RocmVhZDIz"),
    ("learning23kitten23", "bGVhcm5pbmcyM2tpdHRlbjIz"),
    ("learning23sitting23", "bGVhcm5pbmcyM3NpdHRpbmcyMw"),
    ("learning23agent23", "bGVhcm5pbmcyM2FnZW50MjM"),
    ("model23agent23", "bW9kZWwyM2FnZW50MjM"),
    ("model23angle23", "bW9kZWwyM2FuZ2xlMjM"),
    ("model23universe23", "bW9kZWwyM3VuaXZlcnNlMjM"),
    ("model23memory23", "bW9kZWwyM21lbW9yeTIz"),
    ("token23memory23", "dG9rZW4yM21lbW9yeTIz"),
    ("token23stream23", "dG9rZW4yM3N0cmVhbTIz"),
    ("token23context23", "dG9rZW4yM2NvbnRleHQyMw"),
    ("token23knowledge23", "dG9rZW4yM2tub3dsZWRnZTIz"),
    ("prompt23knowledge23", "cHJvbXB0MjNrbm93bGVkZ2UyMw"),
    ("prompt23vector23", "cHJvbXB0MjN2ZWN0b3IyMw"),
    ("prompt23processor23", "cHJvbXB0MjNwcm9jZXNzb3IyMw"),
    ("prompt23reasoning23", "cHJvbXB0MjNyZWFzb25pbmcyMw"),
    ("session23reasoning23", "c2Vzc2lvbjIzcmVhc29uaW5nMjM"),
    ("session23machine23", "c2Vzc2lvbjIzbWFjaGluZTIz"),
    ("session23learning23", "c2Vzc2lvbjIzbGVhcm5pbmcyMw"),
    ("session23model23", "c2Vzc2lvbjIzbW9kZWwyMw"),
    ("library23model23", "bGlicmFyeTIzbW9kZWwyMw"),
    ("library23token23", "bGlicmFyeTIzdG9rZW4yMw"),
    ("library23prompt23", "bGlicmFyeTIzcHJvbXB0MjM"),
    ("library23session23", "bGlicmFyeTIzc2Vzc2lvbjIz"),
    ("service23session23", "c2VydmljZTIzc2Vzc2lvbjIz"),
    ("service23library23", "c2VydmljZTIzbGlicmFyeTIz"),
    ("service23service23", "c2VydmljZTIzc2VydmljZTIz"),
    ("service23gateway23", "c2VydmljZTIzZ2F0ZXdheTIz"),
    ("gateway23gateway23", "Z2F0ZXdheTIzZ2F0ZXdheTIz"),
    ("gateway23storage23", "Z2F0ZXdheTIzc3RvcmFnZTIz"),
    ("gateway23network23", "Z2F0ZXdheTIzbmV0d29yazIz"),
    ("gateway23latency23", "Z2F0ZXdheTIzbGF0ZW5jeTIz"),
    ("storage23latency23", "c3RvcmFnZTIzbGF0ZW5jeTIz"),
    ("storage23buffer23", "c3RvcmFnZTIzYnVmZmVyMjM"),
    ("storage23queue23", "c3RvcmFnZTIzcXVldWUyMw"),
    ("storage23worker23", "c3RvcmFnZTIzd29ya2VyMjM"),
    ("network23worker23", "bmV0d29yazIzd29ya2VyMjM"),
    ("network23kernel23", "bmV0d29yazIza2VybmVsMjM"),
    ("network23signal23", "bmV0d29yazIzc2lnbmFsMjM"),
    ("network23packet23", "bmV0d29yazIzcGFja2V0MjM"),
    ("latency23packet23", "bGF0ZW5jeTIzcGFja2V0MjM"),
    ("latency23router23", "bGF0ZW5jeTIzcm91dGVyMjM"),
    ("latency23cluster23", "bGF0ZW5jeTIzY2x1c3RlcjIz"),
    ("latency23mirror23", "bGF0ZW5jeTIzbWlycm9yMjM"),
    ("buffer23mirror23", "YnVmZmVyMjNtaXJyb3IyMw"),
    ("buffer23filter23", "YnVmZmVyMjNmaWx0ZXIyMw"),
    ("buffer23ranking23", "YnVmZmVyMjNyYW5raW5nMjM"),
    ("buffer23encoding23", "YnVmZmVyMjNlbmNvZGluZzIz"),
    ("queue23encoding23", "cXVldWUyM2VuY29kaW5nMjM"),
    ("queue23mapping23", "cXVldWUyM21hcHBpbmcyMw"),
    ("queue23record23", "cXVldWUyM3JlY29yZDIz"),
    ("queue23candle23", "cXVldWUyM2NhbmRsZTIz"),
    ("worker23candle23", "d29ya2VyMjNjYW5kbGUyMw"),
    ("worker23thread23", "d29ya2VyMjN0aHJlYWQyMw"),
    ("worker23kitten23", "d29ya2VyMjNraXR0ZW4yMw"),
    ("worker23sitting23", "d29ya2VyMjNzaXR0aW5nMjM"),
    ("kernel23sitting23", "a2VybmVsMjNzaXR0aW5nMjM"),
    ("kernel23agent23", "a2VybmVsMjNhZ2VudDIz"),
    ("kernel23angle23", "a2VybmVsMjNhbmdsZTIz"),
    ("kernel23universe23", "a2VybmVsMjN1bml2ZXJzZTIz"),
    ("signal23universe23", "c2lnbmFsMjN1bml2ZXJzZTIz"),
    ("signal23memory23", "c2lnbmFsMjNtZW1vcnkyMw"),
    ("signal23stream23", "c2lnbmFsMjNzdHJlYW0yMw"),
    ("signal23context23", "c2lnbmFsMjNjb250ZXh0MjM"),
    ("packet23context23", "cGFja2V0MjNjb250ZXh0MjM"),
    ("packet23knowledge23", "cGFja2V0MjNrbm93bGVkZ2UyMw"),
    ("packet23vector23", "cGFja2V0MjN2ZWN0b3IyMw"),
    ("packet23processor23", "cGFja2V0MjNwcm9jZXNzb3IyMw"),
    ("router23processor23", "cm91dGVyMjNwcm9jZXNzb3IyMw"),
    ("router23reasoning23", "cm91dGVyMjNyZWFzb25pbmcyMw"),
    ("router23machine23", "cm91dGVyMjNtYWNoaW5lMjM"),
    ("router23learning23", "cm91dGVyMjNsZWFybmluZzIz"),
    ("cluster23learning23", "Y2x1c3RlcjIzbGVhcm5pbmcyMw"),
    ("cluster23model23", "Y2x1c3RlcjIzbW9kZWwyMw"),
    ("cluster23token23", "Y2x1c3RlcjIzdG9rZW4yMw"),
    ("cluster23prompt23", "Y2x1c3RlcjIzcHJvbXB0MjM"),
    ("mirror23prompt23", "bWlycm9yMjNwcm9tcHQyMw"),
    ("mirror23session23", "bWlycm9yMjNzZXNzaW9uMjM"),
    ("mirror23library23", "bWlycm9yMjNsaWJyYXJ5MjM"),
    ("mirror23service23", "bWlycm9yMjNzZXJ2aWNlMjM"),
    ("filter23service23", "ZmlsdGVyMjNzZXJ2aWNlMjM"),
    ("filter23gateway23", "ZmlsdGVyMjNnYXRld2F5MjM"),
    ("filter23storage23", "ZmlsdGVyMjNzdG9yYWdlMjM"),
    ("filter23network23", "ZmlsdGVyMjNuZXR3b3JrMjM"),
    ("ranking23network23", "cmFua2luZzIzbmV0d29yazIz"),
    ("ranking23latency23", "cmFua2luZzIzbGF0ZW5jeTIz"),
    ("ranking23buffer23", "cmFua2luZzIzYnVmZmVyMjM"),
    ("ranking23queue23", "cmFua2luZzIzcXVldWUyMw"),
    ("encoding23queue23", "ZW5jb2RpbmcyM3F1ZXVlMjM"),
    ("encoding23worker23", "ZW5jb2RpbmcyM3dvcmtlcjIz"),
    ("encoding23kernel23", "ZW5jb2RpbmcyM2tlcm5lbDIz"),
    ("encoding23signal23", "ZW5jb2RpbmcyM3NpZ25hbDIz"),
    ("mapping23signal23", "bWFwcGluZzIzc2lnbmFsMjM"),
    ("mapping23packet23", "bWFwcGluZzIzcGFja2V0MjM"),
    ("mapping23router23", "bWFwcGluZzIzcm91dGVyMjM"),
    ("mapping23cluster23", "bWFwcGluZzIzY2x1c3RlcjIz"),
    ("record23cluster23", "cmVjb3JkMjNjbHVzdGVyMjM"),
    ("record23mirror23", "cmVjb3JkMjNtaXJyb3IyMw"),
    ("record23filter23", "cmVjb3JkMjNmaWx0ZXIyMw"),
    ("record23ranking23", "cmVjb3JkMjNyYW5raW5nMjM"),
    ("candle23ranking23", "Y2FuZGxlMjNyYW5raW5nMjM"),
    ("candle23encoding23", "Y2FuZGxlMjNlbmNvZGluZzIz"),
    ("candle23mapping23", "Y2FuZGxlMjNtYXBwaW5nMjM"),
    ("candle23record23", "Y2FuZGxlMjNyZWNvcmQyMw"),
    ("thread23record23", "dGhyZWFkMjNyZWNvcmQyMw"),
    ("thread23candle23", "dGhyZWFkMjNjYW5kbGUyMw"),
    ("thread23thread23", "dGhyZWFkMjN0aHJlYWQyMw"),
    ("thread23kitten23", "dGhyZWFkMjNraXR0ZW4yMw"),
    (
        "round 23: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMjM6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 23: agentuniverse is a framework for multi agents",
        "cm91bmQgMjM6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 23: knowledge stored as vectors enables retrieval",
        "cm91bmQgMjM6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 23: the processor reads the record then stops",
        "cm91bmQgMjM6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 23: a worker pulls the next task from the queue",
        "cm91bmQgMjM6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 23: signals travel through the network layer",
        "cm91bmQgMjM6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 23: the gateway routes each request by policy",
        "cm91bmQgMjM6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 23: memory grows until the buffer is full",
        "cm91bmQgMjM6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 23: the cluster mirrors every packet twice",
        "cm91bmQgMjM6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 23: ranking uses tokens learned from the corpus",
        "cm91bmQgMjM6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 23: a long session ends when the candle dies",
        "cm91bmQgMjM6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 23: encode the prompt then map the result",
        "cm91bmQgMjM6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 23: the kernel wakes the worker at dawn", "cm91bmQgMjM6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 23: service latency drops after the patch",
        "cm91bmQgMjM6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 23: the library caches every vector it sees",
        "cm91bmQgMjM6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 23: agents argue then the debate resolves",
        "cm91bmQgMjM6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 23: the filter keeps only strong matches",
        "cm91bmQgMjM6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 23: the model answers with a short reply",
        "cm91bmQgMjM6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 23: the recorder stores the reasoning trace",
        "cm91bmQgMjM6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 23: the angel watches the processor run", "cm91bmQgMjM6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 23: angle of the vector decides the match",
        "cm91bmQgMjM6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 23: the candle burns twice as long at night",
        "cm91bmQgMjM6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 23: a mirror of the universe in one line",
        "cm91bmQgMjM6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 23: the queue drains before the storm", "cm91bmQgMjM6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
