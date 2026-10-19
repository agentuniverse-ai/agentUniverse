"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten78kitten78", "a2l0dGVuNzhraXR0ZW43OA"),
    ("kitten78sitting78", "a2l0dGVuNzhzaXR0aW5nNzg"),
    ("kitten78agent78", "a2l0dGVuNzhhZ2VudDc4"),
    ("kitten78angle78", "a2l0dGVuNzhhbmdsZTc4"),
    ("sitting78angle78", "c2l0dGluZzc4YW5nbGU3OA"),
    ("sitting78universe78", "c2l0dGluZzc4dW5pdmVyc2U3OA"),
    ("sitting78memory78", "c2l0dGluZzc4bWVtb3J5Nzg"),
    ("sitting78stream78", "c2l0dGluZzc4c3RyZWFtNzg"),
    ("agent78stream78", "YWdlbnQ3OHN0cmVhbTc4"),
    ("agent78context78", "YWdlbnQ3OGNvbnRleHQ3OA"),
    ("agent78knowledge78", "YWdlbnQ3OGtub3dsZWRnZTc4"),
    ("agent78vector78", "YWdlbnQ3OHZlY3Rvcjc4"),
    ("angle78vector78", "YW5nbGU3OHZlY3Rvcjc4"),
    ("angle78processor78", "YW5nbGU3OHByb2Nlc3Nvcjc4"),
    ("angle78reasoning78", "YW5nbGU3OHJlYXNvbmluZzc4"),
    ("angle78machine78", "YW5nbGU3OG1hY2hpbmU3OA"),
    ("universe78machine78", "dW5pdmVyc2U3OG1hY2hpbmU3OA"),
    ("universe78learning78", "dW5pdmVyc2U3OGxlYXJuaW5nNzg"),
    ("universe78model78", "dW5pdmVyc2U3OG1vZGVsNzg"),
    ("universe78token78", "dW5pdmVyc2U3OHRva2VuNzg"),
    ("memory78token78", "bWVtb3J5Nzh0b2tlbjc4"),
    ("memory78prompt78", "bWVtb3J5Nzhwcm9tcHQ3OA"),
    ("memory78session78", "bWVtb3J5NzhzZXNzaW9uNzg"),
    ("memory78library78", "bWVtb3J5NzhsaWJyYXJ5Nzg"),
    ("stream78library78", "c3RyZWFtNzhsaWJyYXJ5Nzg"),
    ("stream78service78", "c3RyZWFtNzhzZXJ2aWNlNzg"),
    ("stream78gateway78", "c3RyZWFtNzhnYXRld2F5Nzg"),
    ("stream78storage78", "c3RyZWFtNzhzdG9yYWdlNzg"),
    ("context78storage78", "Y29udGV4dDc4c3RvcmFnZTc4"),
    ("context78network78", "Y29udGV4dDc4bmV0d29yazc4"),
    ("context78latency78", "Y29udGV4dDc4bGF0ZW5jeTc4"),
    ("context78buffer78", "Y29udGV4dDc4YnVmZmVyNzg"),
    ("knowledge78buffer78", "a25vd2xlZGdlNzhidWZmZXI3OA"),
    ("knowledge78queue78", "a25vd2xlZGdlNzhxdWV1ZTc4"),
    ("knowledge78worker78", "a25vd2xlZGdlNzh3b3JrZXI3OA"),
    ("knowledge78kernel78", "a25vd2xlZGdlNzhrZXJuZWw3OA"),
    ("vector78kernel78", "dmVjdG9yNzhrZXJuZWw3OA"),
    ("vector78signal78", "dmVjdG9yNzhzaWduYWw3OA"),
    ("vector78packet78", "dmVjdG9yNzhwYWNrZXQ3OA"),
    ("vector78router78", "dmVjdG9yNzhyb3V0ZXI3OA"),
    ("processor78router78", "cHJvY2Vzc29yNzhyb3V0ZXI3OA"),
    ("processor78cluster78", "cHJvY2Vzc29yNzhjbHVzdGVyNzg"),
    ("processor78mirror78", "cHJvY2Vzc29yNzhtaXJyb3I3OA"),
    ("processor78filter78", "cHJvY2Vzc29yNzhmaWx0ZXI3OA"),
    ("reasoning78filter78", "cmVhc29uaW5nNzhmaWx0ZXI3OA"),
    ("reasoning78ranking78", "cmVhc29uaW5nNzhyYW5raW5nNzg"),
    ("reasoning78encoding78", "cmVhc29uaW5nNzhlbmNvZGluZzc4"),
    ("reasoning78mapping78", "cmVhc29uaW5nNzhtYXBwaW5nNzg"),
    ("machine78mapping78", "bWFjaGluZTc4bWFwcGluZzc4"),
    ("machine78record78", "bWFjaGluZTc4cmVjb3JkNzg"),
    ("machine78candle78", "bWFjaGluZTc4Y2FuZGxlNzg"),
    ("machine78thread78", "bWFjaGluZTc4dGhyZWFkNzg"),
    ("learning78thread78", "bGVhcm5pbmc3OHRocmVhZDc4"),
    ("learning78kitten78", "bGVhcm5pbmc3OGtpdHRlbjc4"),
    ("learning78sitting78", "bGVhcm5pbmc3OHNpdHRpbmc3OA"),
    ("learning78agent78", "bGVhcm5pbmc3OGFnZW50Nzg"),
    ("model78agent78", "bW9kZWw3OGFnZW50Nzg"),
    ("model78angle78", "bW9kZWw3OGFuZ2xlNzg"),
    ("model78universe78", "bW9kZWw3OHVuaXZlcnNlNzg"),
    ("model78memory78", "bW9kZWw3OG1lbW9yeTc4"),
    ("token78memory78", "dG9rZW43OG1lbW9yeTc4"),
    ("token78stream78", "dG9rZW43OHN0cmVhbTc4"),
    ("token78context78", "dG9rZW43OGNvbnRleHQ3OA"),
    ("token78knowledge78", "dG9rZW43OGtub3dsZWRnZTc4"),
    ("prompt78knowledge78", "cHJvbXB0Nzhrbm93bGVkZ2U3OA"),
    ("prompt78vector78", "cHJvbXB0Nzh2ZWN0b3I3OA"),
    ("prompt78processor78", "cHJvbXB0Nzhwcm9jZXNzb3I3OA"),
    ("prompt78reasoning78", "cHJvbXB0NzhyZWFzb25pbmc3OA"),
    ("session78reasoning78", "c2Vzc2lvbjc4cmVhc29uaW5nNzg"),
    ("session78machine78", "c2Vzc2lvbjc4bWFjaGluZTc4"),
    ("session78learning78", "c2Vzc2lvbjc4bGVhcm5pbmc3OA"),
    ("session78model78", "c2Vzc2lvbjc4bW9kZWw3OA"),
    ("library78model78", "bGlicmFyeTc4bW9kZWw3OA"),
    ("library78token78", "bGlicmFyeTc4dG9rZW43OA"),
    ("library78prompt78", "bGlicmFyeTc4cHJvbXB0Nzg"),
    ("library78session78", "bGlicmFyeTc4c2Vzc2lvbjc4"),
    ("service78session78", "c2VydmljZTc4c2Vzc2lvbjc4"),
    ("service78library78", "c2VydmljZTc4bGlicmFyeTc4"),
    ("service78service78", "c2VydmljZTc4c2VydmljZTc4"),
    ("service78gateway78", "c2VydmljZTc4Z2F0ZXdheTc4"),
    ("gateway78gateway78", "Z2F0ZXdheTc4Z2F0ZXdheTc4"),
    ("gateway78storage78", "Z2F0ZXdheTc4c3RvcmFnZTc4"),
    ("gateway78network78", "Z2F0ZXdheTc4bmV0d29yazc4"),
    ("gateway78latency78", "Z2F0ZXdheTc4bGF0ZW5jeTc4"),
    ("storage78latency78", "c3RvcmFnZTc4bGF0ZW5jeTc4"),
    ("storage78buffer78", "c3RvcmFnZTc4YnVmZmVyNzg"),
    ("storage78queue78", "c3RvcmFnZTc4cXVldWU3OA"),
    ("storage78worker78", "c3RvcmFnZTc4d29ya2VyNzg"),
    ("network78worker78", "bmV0d29yazc4d29ya2VyNzg"),
    ("network78kernel78", "bmV0d29yazc4a2VybmVsNzg"),
    ("network78signal78", "bmV0d29yazc4c2lnbmFsNzg"),
    ("network78packet78", "bmV0d29yazc4cGFja2V0Nzg"),
    ("latency78packet78", "bGF0ZW5jeTc4cGFja2V0Nzg"),
    ("latency78router78", "bGF0ZW5jeTc4cm91dGVyNzg"),
    ("latency78cluster78", "bGF0ZW5jeTc4Y2x1c3Rlcjc4"),
    ("latency78mirror78", "bGF0ZW5jeTc4bWlycm9yNzg"),
    ("buffer78mirror78", "YnVmZmVyNzhtaXJyb3I3OA"),
    ("buffer78filter78", "YnVmZmVyNzhmaWx0ZXI3OA"),
    ("buffer78ranking78", "YnVmZmVyNzhyYW5raW5nNzg"),
    ("buffer78encoding78", "YnVmZmVyNzhlbmNvZGluZzc4"),
    ("queue78encoding78", "cXVldWU3OGVuY29kaW5nNzg"),
    ("queue78mapping78", "cXVldWU3OG1hcHBpbmc3OA"),
    ("queue78record78", "cXVldWU3OHJlY29yZDc4"),
    ("queue78candle78", "cXVldWU3OGNhbmRsZTc4"),
    ("worker78candle78", "d29ya2VyNzhjYW5kbGU3OA"),
    ("worker78thread78", "d29ya2VyNzh0aHJlYWQ3OA"),
    ("worker78kitten78", "d29ya2VyNzhraXR0ZW43OA"),
    ("worker78sitting78", "d29ya2VyNzhzaXR0aW5nNzg"),
    ("kernel78sitting78", "a2VybmVsNzhzaXR0aW5nNzg"),
    ("kernel78agent78", "a2VybmVsNzhhZ2VudDc4"),
    ("kernel78angle78", "a2VybmVsNzhhbmdsZTc4"),
    ("kernel78universe78", "a2VybmVsNzh1bml2ZXJzZTc4"),
    ("signal78universe78", "c2lnbmFsNzh1bml2ZXJzZTc4"),
    ("signal78memory78", "c2lnbmFsNzhtZW1vcnk3OA"),
    ("signal78stream78", "c2lnbmFsNzhzdHJlYW03OA"),
    ("signal78context78", "c2lnbmFsNzhjb250ZXh0Nzg"),
    ("packet78context78", "cGFja2V0Nzhjb250ZXh0Nzg"),
    ("packet78knowledge78", "cGFja2V0Nzhrbm93bGVkZ2U3OA"),
    ("packet78vector78", "cGFja2V0Nzh2ZWN0b3I3OA"),
    ("packet78processor78", "cGFja2V0Nzhwcm9jZXNzb3I3OA"),
    ("router78processor78", "cm91dGVyNzhwcm9jZXNzb3I3OA"),
    ("router78reasoning78", "cm91dGVyNzhyZWFzb25pbmc3OA"),
    ("router78machine78", "cm91dGVyNzhtYWNoaW5lNzg"),
    ("router78learning78", "cm91dGVyNzhsZWFybmluZzc4"),
    ("cluster78learning78", "Y2x1c3Rlcjc4bGVhcm5pbmc3OA"),
    ("cluster78model78", "Y2x1c3Rlcjc4bW9kZWw3OA"),
    ("cluster78token78", "Y2x1c3Rlcjc4dG9rZW43OA"),
    ("cluster78prompt78", "Y2x1c3Rlcjc4cHJvbXB0Nzg"),
    ("mirror78prompt78", "bWlycm9yNzhwcm9tcHQ3OA"),
    ("mirror78session78", "bWlycm9yNzhzZXNzaW9uNzg"),
    ("mirror78library78", "bWlycm9yNzhsaWJyYXJ5Nzg"),
    ("mirror78service78", "bWlycm9yNzhzZXJ2aWNlNzg"),
    ("filter78service78", "ZmlsdGVyNzhzZXJ2aWNlNzg"),
    ("filter78gateway78", "ZmlsdGVyNzhnYXRld2F5Nzg"),
    ("filter78storage78", "ZmlsdGVyNzhzdG9yYWdlNzg"),
    ("filter78network78", "ZmlsdGVyNzhuZXR3b3JrNzg"),
    ("ranking78network78", "cmFua2luZzc4bmV0d29yazc4"),
    ("ranking78latency78", "cmFua2luZzc4bGF0ZW5jeTc4"),
    ("ranking78buffer78", "cmFua2luZzc4YnVmZmVyNzg"),
    ("ranking78queue78", "cmFua2luZzc4cXVldWU3OA"),
    ("encoding78queue78", "ZW5jb2Rpbmc3OHF1ZXVlNzg"),
    ("encoding78worker78", "ZW5jb2Rpbmc3OHdvcmtlcjc4"),
    ("encoding78kernel78", "ZW5jb2Rpbmc3OGtlcm5lbDc4"),
    ("encoding78signal78", "ZW5jb2Rpbmc3OHNpZ25hbDc4"),
    ("mapping78signal78", "bWFwcGluZzc4c2lnbmFsNzg"),
    ("mapping78packet78", "bWFwcGluZzc4cGFja2V0Nzg"),
    ("mapping78router78", "bWFwcGluZzc4cm91dGVyNzg"),
    ("mapping78cluster78", "bWFwcGluZzc4Y2x1c3Rlcjc4"),
    ("record78cluster78", "cmVjb3JkNzhjbHVzdGVyNzg"),
    ("record78mirror78", "cmVjb3JkNzhtaXJyb3I3OA"),
    ("record78filter78", "cmVjb3JkNzhmaWx0ZXI3OA"),
    ("record78ranking78", "cmVjb3JkNzhyYW5raW5nNzg"),
    ("candle78ranking78", "Y2FuZGxlNzhyYW5raW5nNzg"),
    ("candle78encoding78", "Y2FuZGxlNzhlbmNvZGluZzc4"),
    ("candle78mapping78", "Y2FuZGxlNzhtYXBwaW5nNzg"),
    ("candle78record78", "Y2FuZGxlNzhyZWNvcmQ3OA"),
    ("thread78record78", "dGhyZWFkNzhyZWNvcmQ3OA"),
    ("thread78candle78", "dGhyZWFkNzhjYW5kbGU3OA"),
    ("thread78thread78", "dGhyZWFkNzh0aHJlYWQ3OA"),
    ("thread78kitten78", "dGhyZWFkNzhraXR0ZW43OA"),
    (
        "round 78: the quick brown fox jumps over the lazy dog",
        "cm91bmQgNzg6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 78: agentuniverse is a framework for multi agents",
        "cm91bmQgNzg6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 78: knowledge stored as vectors enables retrieval",
        "cm91bmQgNzg6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 78: the processor reads the record then stops",
        "cm91bmQgNzg6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 78: a worker pulls the next task from the queue",
        "cm91bmQgNzg6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 78: signals travel through the network layer",
        "cm91bmQgNzg6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 78: the gateway routes each request by policy",
        "cm91bmQgNzg6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 78: memory grows until the buffer is full",
        "cm91bmQgNzg6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 78: the cluster mirrors every packet twice",
        "cm91bmQgNzg6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 78: ranking uses tokens learned from the corpus",
        "cm91bmQgNzg6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 78: a long session ends when the candle dies",
        "cm91bmQgNzg6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 78: encode the prompt then map the result",
        "cm91bmQgNzg6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 78: the kernel wakes the worker at dawn", "cm91bmQgNzg6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 78: service latency drops after the patch",
        "cm91bmQgNzg6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 78: the library caches every vector it sees",
        "cm91bmQgNzg6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 78: agents argue then the debate resolves",
        "cm91bmQgNzg6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 78: the filter keeps only strong matches",
        "cm91bmQgNzg6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 78: the model answers with a short reply",
        "cm91bmQgNzg6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 78: the recorder stores the reasoning trace",
        "cm91bmQgNzg6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 78: the angel watches the processor run", "cm91bmQgNzg6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 78: angle of the vector decides the match",
        "cm91bmQgNzg6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 78: the candle burns twice as long at night",
        "cm91bmQgNzg6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 78: a mirror of the universe in one line",
        "cm91bmQgNzg6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 78: the queue drains before the storm", "cm91bmQgNzg6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
