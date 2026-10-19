"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten17kitten17", "a2l0dGVuMTdraXR0ZW4xNw"),
    ("kitten17sitting17", "a2l0dGVuMTdzaXR0aW5nMTc"),
    ("kitten17agent17", "a2l0dGVuMTdhZ2VudDE3"),
    ("kitten17angle17", "a2l0dGVuMTdhbmdsZTE3"),
    ("sitting17angle17", "c2l0dGluZzE3YW5nbGUxNw"),
    ("sitting17universe17", "c2l0dGluZzE3dW5pdmVyc2UxNw"),
    ("sitting17memory17", "c2l0dGluZzE3bWVtb3J5MTc"),
    ("sitting17stream17", "c2l0dGluZzE3c3RyZWFtMTc"),
    ("agent17stream17", "YWdlbnQxN3N0cmVhbTE3"),
    ("agent17context17", "YWdlbnQxN2NvbnRleHQxNw"),
    ("agent17knowledge17", "YWdlbnQxN2tub3dsZWRnZTE3"),
    ("agent17vector17", "YWdlbnQxN3ZlY3RvcjE3"),
    ("angle17vector17", "YW5nbGUxN3ZlY3RvcjE3"),
    ("angle17processor17", "YW5nbGUxN3Byb2Nlc3NvcjE3"),
    ("angle17reasoning17", "YW5nbGUxN3JlYXNvbmluZzE3"),
    ("angle17machine17", "YW5nbGUxN21hY2hpbmUxNw"),
    ("universe17machine17", "dW5pdmVyc2UxN21hY2hpbmUxNw"),
    ("universe17learning17", "dW5pdmVyc2UxN2xlYXJuaW5nMTc"),
    ("universe17model17", "dW5pdmVyc2UxN21vZGVsMTc"),
    ("universe17token17", "dW5pdmVyc2UxN3Rva2VuMTc"),
    ("memory17token17", "bWVtb3J5MTd0b2tlbjE3"),
    ("memory17prompt17", "bWVtb3J5MTdwcm9tcHQxNw"),
    ("memory17session17", "bWVtb3J5MTdzZXNzaW9uMTc"),
    ("memory17library17", "bWVtb3J5MTdsaWJyYXJ5MTc"),
    ("stream17library17", "c3RyZWFtMTdsaWJyYXJ5MTc"),
    ("stream17service17", "c3RyZWFtMTdzZXJ2aWNlMTc"),
    ("stream17gateway17", "c3RyZWFtMTdnYXRld2F5MTc"),
    ("stream17storage17", "c3RyZWFtMTdzdG9yYWdlMTc"),
    ("context17storage17", "Y29udGV4dDE3c3RvcmFnZTE3"),
    ("context17network17", "Y29udGV4dDE3bmV0d29yazE3"),
    ("context17latency17", "Y29udGV4dDE3bGF0ZW5jeTE3"),
    ("context17buffer17", "Y29udGV4dDE3YnVmZmVyMTc"),
    ("knowledge17buffer17", "a25vd2xlZGdlMTdidWZmZXIxNw"),
    ("knowledge17queue17", "a25vd2xlZGdlMTdxdWV1ZTE3"),
    ("knowledge17worker17", "a25vd2xlZGdlMTd3b3JrZXIxNw"),
    ("knowledge17kernel17", "a25vd2xlZGdlMTdrZXJuZWwxNw"),
    ("vector17kernel17", "dmVjdG9yMTdrZXJuZWwxNw"),
    ("vector17signal17", "dmVjdG9yMTdzaWduYWwxNw"),
    ("vector17packet17", "dmVjdG9yMTdwYWNrZXQxNw"),
    ("vector17router17", "dmVjdG9yMTdyb3V0ZXIxNw"),
    ("processor17router17", "cHJvY2Vzc29yMTdyb3V0ZXIxNw"),
    ("processor17cluster17", "cHJvY2Vzc29yMTdjbHVzdGVyMTc"),
    ("processor17mirror17", "cHJvY2Vzc29yMTdtaXJyb3IxNw"),
    ("processor17filter17", "cHJvY2Vzc29yMTdmaWx0ZXIxNw"),
    ("reasoning17filter17", "cmVhc29uaW5nMTdmaWx0ZXIxNw"),
    ("reasoning17ranking17", "cmVhc29uaW5nMTdyYW5raW5nMTc"),
    ("reasoning17encoding17", "cmVhc29uaW5nMTdlbmNvZGluZzE3"),
    ("reasoning17mapping17", "cmVhc29uaW5nMTdtYXBwaW5nMTc"),
    ("machine17mapping17", "bWFjaGluZTE3bWFwcGluZzE3"),
    ("machine17record17", "bWFjaGluZTE3cmVjb3JkMTc"),
    ("machine17candle17", "bWFjaGluZTE3Y2FuZGxlMTc"),
    ("machine17thread17", "bWFjaGluZTE3dGhyZWFkMTc"),
    ("learning17thread17", "bGVhcm5pbmcxN3RocmVhZDE3"),
    ("learning17kitten17", "bGVhcm5pbmcxN2tpdHRlbjE3"),
    ("learning17sitting17", "bGVhcm5pbmcxN3NpdHRpbmcxNw"),
    ("learning17agent17", "bGVhcm5pbmcxN2FnZW50MTc"),
    ("model17agent17", "bW9kZWwxN2FnZW50MTc"),
    ("model17angle17", "bW9kZWwxN2FuZ2xlMTc"),
    ("model17universe17", "bW9kZWwxN3VuaXZlcnNlMTc"),
    ("model17memory17", "bW9kZWwxN21lbW9yeTE3"),
    ("token17memory17", "dG9rZW4xN21lbW9yeTE3"),
    ("token17stream17", "dG9rZW4xN3N0cmVhbTE3"),
    ("token17context17", "dG9rZW4xN2NvbnRleHQxNw"),
    ("token17knowledge17", "dG9rZW4xN2tub3dsZWRnZTE3"),
    ("prompt17knowledge17", "cHJvbXB0MTdrbm93bGVkZ2UxNw"),
    ("prompt17vector17", "cHJvbXB0MTd2ZWN0b3IxNw"),
    ("prompt17processor17", "cHJvbXB0MTdwcm9jZXNzb3IxNw"),
    ("prompt17reasoning17", "cHJvbXB0MTdyZWFzb25pbmcxNw"),
    ("session17reasoning17", "c2Vzc2lvbjE3cmVhc29uaW5nMTc"),
    ("session17machine17", "c2Vzc2lvbjE3bWFjaGluZTE3"),
    ("session17learning17", "c2Vzc2lvbjE3bGVhcm5pbmcxNw"),
    ("session17model17", "c2Vzc2lvbjE3bW9kZWwxNw"),
    ("library17model17", "bGlicmFyeTE3bW9kZWwxNw"),
    ("library17token17", "bGlicmFyeTE3dG9rZW4xNw"),
    ("library17prompt17", "bGlicmFyeTE3cHJvbXB0MTc"),
    ("library17session17", "bGlicmFyeTE3c2Vzc2lvbjE3"),
    ("service17session17", "c2VydmljZTE3c2Vzc2lvbjE3"),
    ("service17library17", "c2VydmljZTE3bGlicmFyeTE3"),
    ("service17service17", "c2VydmljZTE3c2VydmljZTE3"),
    ("service17gateway17", "c2VydmljZTE3Z2F0ZXdheTE3"),
    ("gateway17gateway17", "Z2F0ZXdheTE3Z2F0ZXdheTE3"),
    ("gateway17storage17", "Z2F0ZXdheTE3c3RvcmFnZTE3"),
    ("gateway17network17", "Z2F0ZXdheTE3bmV0d29yazE3"),
    ("gateway17latency17", "Z2F0ZXdheTE3bGF0ZW5jeTE3"),
    ("storage17latency17", "c3RvcmFnZTE3bGF0ZW5jeTE3"),
    ("storage17buffer17", "c3RvcmFnZTE3YnVmZmVyMTc"),
    ("storage17queue17", "c3RvcmFnZTE3cXVldWUxNw"),
    ("storage17worker17", "c3RvcmFnZTE3d29ya2VyMTc"),
    ("network17worker17", "bmV0d29yazE3d29ya2VyMTc"),
    ("network17kernel17", "bmV0d29yazE3a2VybmVsMTc"),
    ("network17signal17", "bmV0d29yazE3c2lnbmFsMTc"),
    ("network17packet17", "bmV0d29yazE3cGFja2V0MTc"),
    ("latency17packet17", "bGF0ZW5jeTE3cGFja2V0MTc"),
    ("latency17router17", "bGF0ZW5jeTE3cm91dGVyMTc"),
    ("latency17cluster17", "bGF0ZW5jeTE3Y2x1c3RlcjE3"),
    ("latency17mirror17", "bGF0ZW5jeTE3bWlycm9yMTc"),
    ("buffer17mirror17", "YnVmZmVyMTdtaXJyb3IxNw"),
    ("buffer17filter17", "YnVmZmVyMTdmaWx0ZXIxNw"),
    ("buffer17ranking17", "YnVmZmVyMTdyYW5raW5nMTc"),
    ("buffer17encoding17", "YnVmZmVyMTdlbmNvZGluZzE3"),
    ("queue17encoding17", "cXVldWUxN2VuY29kaW5nMTc"),
    ("queue17mapping17", "cXVldWUxN21hcHBpbmcxNw"),
    ("queue17record17", "cXVldWUxN3JlY29yZDE3"),
    ("queue17candle17", "cXVldWUxN2NhbmRsZTE3"),
    ("worker17candle17", "d29ya2VyMTdjYW5kbGUxNw"),
    ("worker17thread17", "d29ya2VyMTd0aHJlYWQxNw"),
    ("worker17kitten17", "d29ya2VyMTdraXR0ZW4xNw"),
    ("worker17sitting17", "d29ya2VyMTdzaXR0aW5nMTc"),
    ("kernel17sitting17", "a2VybmVsMTdzaXR0aW5nMTc"),
    ("kernel17agent17", "a2VybmVsMTdhZ2VudDE3"),
    ("kernel17angle17", "a2VybmVsMTdhbmdsZTE3"),
    ("kernel17universe17", "a2VybmVsMTd1bml2ZXJzZTE3"),
    ("signal17universe17", "c2lnbmFsMTd1bml2ZXJzZTE3"),
    ("signal17memory17", "c2lnbmFsMTdtZW1vcnkxNw"),
    ("signal17stream17", "c2lnbmFsMTdzdHJlYW0xNw"),
    ("signal17context17", "c2lnbmFsMTdjb250ZXh0MTc"),
    ("packet17context17", "cGFja2V0MTdjb250ZXh0MTc"),
    ("packet17knowledge17", "cGFja2V0MTdrbm93bGVkZ2UxNw"),
    ("packet17vector17", "cGFja2V0MTd2ZWN0b3IxNw"),
    ("packet17processor17", "cGFja2V0MTdwcm9jZXNzb3IxNw"),
    ("router17processor17", "cm91dGVyMTdwcm9jZXNzb3IxNw"),
    ("router17reasoning17", "cm91dGVyMTdyZWFzb25pbmcxNw"),
    ("router17machine17", "cm91dGVyMTdtYWNoaW5lMTc"),
    ("router17learning17", "cm91dGVyMTdsZWFybmluZzE3"),
    ("cluster17learning17", "Y2x1c3RlcjE3bGVhcm5pbmcxNw"),
    ("cluster17model17", "Y2x1c3RlcjE3bW9kZWwxNw"),
    ("cluster17token17", "Y2x1c3RlcjE3dG9rZW4xNw"),
    ("cluster17prompt17", "Y2x1c3RlcjE3cHJvbXB0MTc"),
    ("mirror17prompt17", "bWlycm9yMTdwcm9tcHQxNw"),
    ("mirror17session17", "bWlycm9yMTdzZXNzaW9uMTc"),
    ("mirror17library17", "bWlycm9yMTdsaWJyYXJ5MTc"),
    ("mirror17service17", "bWlycm9yMTdzZXJ2aWNlMTc"),
    ("filter17service17", "ZmlsdGVyMTdzZXJ2aWNlMTc"),
    ("filter17gateway17", "ZmlsdGVyMTdnYXRld2F5MTc"),
    ("filter17storage17", "ZmlsdGVyMTdzdG9yYWdlMTc"),
    ("filter17network17", "ZmlsdGVyMTduZXR3b3JrMTc"),
    ("ranking17network17", "cmFua2luZzE3bmV0d29yazE3"),
    ("ranking17latency17", "cmFua2luZzE3bGF0ZW5jeTE3"),
    ("ranking17buffer17", "cmFua2luZzE3YnVmZmVyMTc"),
    ("ranking17queue17", "cmFua2luZzE3cXVldWUxNw"),
    ("encoding17queue17", "ZW5jb2RpbmcxN3F1ZXVlMTc"),
    ("encoding17worker17", "ZW5jb2RpbmcxN3dvcmtlcjE3"),
    ("encoding17kernel17", "ZW5jb2RpbmcxN2tlcm5lbDE3"),
    ("encoding17signal17", "ZW5jb2RpbmcxN3NpZ25hbDE3"),
    ("mapping17signal17", "bWFwcGluZzE3c2lnbmFsMTc"),
    ("mapping17packet17", "bWFwcGluZzE3cGFja2V0MTc"),
    ("mapping17router17", "bWFwcGluZzE3cm91dGVyMTc"),
    ("mapping17cluster17", "bWFwcGluZzE3Y2x1c3RlcjE3"),
    ("record17cluster17", "cmVjb3JkMTdjbHVzdGVyMTc"),
    ("record17mirror17", "cmVjb3JkMTdtaXJyb3IxNw"),
    ("record17filter17", "cmVjb3JkMTdmaWx0ZXIxNw"),
    ("record17ranking17", "cmVjb3JkMTdyYW5raW5nMTc"),
    ("candle17ranking17", "Y2FuZGxlMTdyYW5raW5nMTc"),
    ("candle17encoding17", "Y2FuZGxlMTdlbmNvZGluZzE3"),
    ("candle17mapping17", "Y2FuZGxlMTdtYXBwaW5nMTc"),
    ("candle17record17", "Y2FuZGxlMTdyZWNvcmQxNw"),
    ("thread17record17", "dGhyZWFkMTdyZWNvcmQxNw"),
    ("thread17candle17", "dGhyZWFkMTdjYW5kbGUxNw"),
    ("thread17thread17", "dGhyZWFkMTd0aHJlYWQxNw"),
    ("thread17kitten17", "dGhyZWFkMTdraXR0ZW4xNw"),
    (
        "round 17: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTc6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 17: agentuniverse is a framework for multi agents",
        "cm91bmQgMTc6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 17: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTc6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 17: the processor reads the record then stops",
        "cm91bmQgMTc6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 17: a worker pulls the next task from the queue",
        "cm91bmQgMTc6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 17: signals travel through the network layer",
        "cm91bmQgMTc6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 17: the gateway routes each request by policy",
        "cm91bmQgMTc6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 17: memory grows until the buffer is full",
        "cm91bmQgMTc6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 17: the cluster mirrors every packet twice",
        "cm91bmQgMTc6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 17: ranking uses tokens learned from the corpus",
        "cm91bmQgMTc6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 17: a long session ends when the candle dies",
        "cm91bmQgMTc6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 17: encode the prompt then map the result",
        "cm91bmQgMTc6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 17: the kernel wakes the worker at dawn", "cm91bmQgMTc6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 17: service latency drops after the patch",
        "cm91bmQgMTc6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 17: the library caches every vector it sees",
        "cm91bmQgMTc6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 17: agents argue then the debate resolves",
        "cm91bmQgMTc6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 17: the filter keeps only strong matches",
        "cm91bmQgMTc6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 17: the model answers with a short reply",
        "cm91bmQgMTc6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 17: the recorder stores the reasoning trace",
        "cm91bmQgMTc6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 17: the angel watches the processor run", "cm91bmQgMTc6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 17: angle of the vector decides the match",
        "cm91bmQgMTc6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 17: the candle burns twice as long at night",
        "cm91bmQgMTc6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 17: a mirror of the universe in one line",
        "cm91bmQgMTc6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 17: the queue drains before the storm", "cm91bmQgMTc6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
