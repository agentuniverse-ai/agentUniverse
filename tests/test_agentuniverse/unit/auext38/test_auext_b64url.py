"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten38kitten38", "a2l0dGVuMzhraXR0ZW4zOA"),
    ("kitten38sitting38", "a2l0dGVuMzhzaXR0aW5nMzg"),
    ("kitten38agent38", "a2l0dGVuMzhhZ2VudDM4"),
    ("kitten38angle38", "a2l0dGVuMzhhbmdsZTM4"),
    ("sitting38angle38", "c2l0dGluZzM4YW5nbGUzOA"),
    ("sitting38universe38", "c2l0dGluZzM4dW5pdmVyc2UzOA"),
    ("sitting38memory38", "c2l0dGluZzM4bWVtb3J5Mzg"),
    ("sitting38stream38", "c2l0dGluZzM4c3RyZWFtMzg"),
    ("agent38stream38", "YWdlbnQzOHN0cmVhbTM4"),
    ("agent38context38", "YWdlbnQzOGNvbnRleHQzOA"),
    ("agent38knowledge38", "YWdlbnQzOGtub3dsZWRnZTM4"),
    ("agent38vector38", "YWdlbnQzOHZlY3RvcjM4"),
    ("angle38vector38", "YW5nbGUzOHZlY3RvcjM4"),
    ("angle38processor38", "YW5nbGUzOHByb2Nlc3NvcjM4"),
    ("angle38reasoning38", "YW5nbGUzOHJlYXNvbmluZzM4"),
    ("angle38machine38", "YW5nbGUzOG1hY2hpbmUzOA"),
    ("universe38machine38", "dW5pdmVyc2UzOG1hY2hpbmUzOA"),
    ("universe38learning38", "dW5pdmVyc2UzOGxlYXJuaW5nMzg"),
    ("universe38model38", "dW5pdmVyc2UzOG1vZGVsMzg"),
    ("universe38token38", "dW5pdmVyc2UzOHRva2VuMzg"),
    ("memory38token38", "bWVtb3J5Mzh0b2tlbjM4"),
    ("memory38prompt38", "bWVtb3J5Mzhwcm9tcHQzOA"),
    ("memory38session38", "bWVtb3J5MzhzZXNzaW9uMzg"),
    ("memory38library38", "bWVtb3J5MzhsaWJyYXJ5Mzg"),
    ("stream38library38", "c3RyZWFtMzhsaWJyYXJ5Mzg"),
    ("stream38service38", "c3RyZWFtMzhzZXJ2aWNlMzg"),
    ("stream38gateway38", "c3RyZWFtMzhnYXRld2F5Mzg"),
    ("stream38storage38", "c3RyZWFtMzhzdG9yYWdlMzg"),
    ("context38storage38", "Y29udGV4dDM4c3RvcmFnZTM4"),
    ("context38network38", "Y29udGV4dDM4bmV0d29yazM4"),
    ("context38latency38", "Y29udGV4dDM4bGF0ZW5jeTM4"),
    ("context38buffer38", "Y29udGV4dDM4YnVmZmVyMzg"),
    ("knowledge38buffer38", "a25vd2xlZGdlMzhidWZmZXIzOA"),
    ("knowledge38queue38", "a25vd2xlZGdlMzhxdWV1ZTM4"),
    ("knowledge38worker38", "a25vd2xlZGdlMzh3b3JrZXIzOA"),
    ("knowledge38kernel38", "a25vd2xlZGdlMzhrZXJuZWwzOA"),
    ("vector38kernel38", "dmVjdG9yMzhrZXJuZWwzOA"),
    ("vector38signal38", "dmVjdG9yMzhzaWduYWwzOA"),
    ("vector38packet38", "dmVjdG9yMzhwYWNrZXQzOA"),
    ("vector38router38", "dmVjdG9yMzhyb3V0ZXIzOA"),
    ("processor38router38", "cHJvY2Vzc29yMzhyb3V0ZXIzOA"),
    ("processor38cluster38", "cHJvY2Vzc29yMzhjbHVzdGVyMzg"),
    ("processor38mirror38", "cHJvY2Vzc29yMzhtaXJyb3IzOA"),
    ("processor38filter38", "cHJvY2Vzc29yMzhmaWx0ZXIzOA"),
    ("reasoning38filter38", "cmVhc29uaW5nMzhmaWx0ZXIzOA"),
    ("reasoning38ranking38", "cmVhc29uaW5nMzhyYW5raW5nMzg"),
    ("reasoning38encoding38", "cmVhc29uaW5nMzhlbmNvZGluZzM4"),
    ("reasoning38mapping38", "cmVhc29uaW5nMzhtYXBwaW5nMzg"),
    ("machine38mapping38", "bWFjaGluZTM4bWFwcGluZzM4"),
    ("machine38record38", "bWFjaGluZTM4cmVjb3JkMzg"),
    ("machine38candle38", "bWFjaGluZTM4Y2FuZGxlMzg"),
    ("machine38thread38", "bWFjaGluZTM4dGhyZWFkMzg"),
    ("learning38thread38", "bGVhcm5pbmczOHRocmVhZDM4"),
    ("learning38kitten38", "bGVhcm5pbmczOGtpdHRlbjM4"),
    ("learning38sitting38", "bGVhcm5pbmczOHNpdHRpbmczOA"),
    ("learning38agent38", "bGVhcm5pbmczOGFnZW50Mzg"),
    ("model38agent38", "bW9kZWwzOGFnZW50Mzg"),
    ("model38angle38", "bW9kZWwzOGFuZ2xlMzg"),
    ("model38universe38", "bW9kZWwzOHVuaXZlcnNlMzg"),
    ("model38memory38", "bW9kZWwzOG1lbW9yeTM4"),
    ("token38memory38", "dG9rZW4zOG1lbW9yeTM4"),
    ("token38stream38", "dG9rZW4zOHN0cmVhbTM4"),
    ("token38context38", "dG9rZW4zOGNvbnRleHQzOA"),
    ("token38knowledge38", "dG9rZW4zOGtub3dsZWRnZTM4"),
    ("prompt38knowledge38", "cHJvbXB0Mzhrbm93bGVkZ2UzOA"),
    ("prompt38vector38", "cHJvbXB0Mzh2ZWN0b3IzOA"),
    ("prompt38processor38", "cHJvbXB0Mzhwcm9jZXNzb3IzOA"),
    ("prompt38reasoning38", "cHJvbXB0MzhyZWFzb25pbmczOA"),
    ("session38reasoning38", "c2Vzc2lvbjM4cmVhc29uaW5nMzg"),
    ("session38machine38", "c2Vzc2lvbjM4bWFjaGluZTM4"),
    ("session38learning38", "c2Vzc2lvbjM4bGVhcm5pbmczOA"),
    ("session38model38", "c2Vzc2lvbjM4bW9kZWwzOA"),
    ("library38model38", "bGlicmFyeTM4bW9kZWwzOA"),
    ("library38token38", "bGlicmFyeTM4dG9rZW4zOA"),
    ("library38prompt38", "bGlicmFyeTM4cHJvbXB0Mzg"),
    ("library38session38", "bGlicmFyeTM4c2Vzc2lvbjM4"),
    ("service38session38", "c2VydmljZTM4c2Vzc2lvbjM4"),
    ("service38library38", "c2VydmljZTM4bGlicmFyeTM4"),
    ("service38service38", "c2VydmljZTM4c2VydmljZTM4"),
    ("service38gateway38", "c2VydmljZTM4Z2F0ZXdheTM4"),
    ("gateway38gateway38", "Z2F0ZXdheTM4Z2F0ZXdheTM4"),
    ("gateway38storage38", "Z2F0ZXdheTM4c3RvcmFnZTM4"),
    ("gateway38network38", "Z2F0ZXdheTM4bmV0d29yazM4"),
    ("gateway38latency38", "Z2F0ZXdheTM4bGF0ZW5jeTM4"),
    ("storage38latency38", "c3RvcmFnZTM4bGF0ZW5jeTM4"),
    ("storage38buffer38", "c3RvcmFnZTM4YnVmZmVyMzg"),
    ("storage38queue38", "c3RvcmFnZTM4cXVldWUzOA"),
    ("storage38worker38", "c3RvcmFnZTM4d29ya2VyMzg"),
    ("network38worker38", "bmV0d29yazM4d29ya2VyMzg"),
    ("network38kernel38", "bmV0d29yazM4a2VybmVsMzg"),
    ("network38signal38", "bmV0d29yazM4c2lnbmFsMzg"),
    ("network38packet38", "bmV0d29yazM4cGFja2V0Mzg"),
    ("latency38packet38", "bGF0ZW5jeTM4cGFja2V0Mzg"),
    ("latency38router38", "bGF0ZW5jeTM4cm91dGVyMzg"),
    ("latency38cluster38", "bGF0ZW5jeTM4Y2x1c3RlcjM4"),
    ("latency38mirror38", "bGF0ZW5jeTM4bWlycm9yMzg"),
    ("buffer38mirror38", "YnVmZmVyMzhtaXJyb3IzOA"),
    ("buffer38filter38", "YnVmZmVyMzhmaWx0ZXIzOA"),
    ("buffer38ranking38", "YnVmZmVyMzhyYW5raW5nMzg"),
    ("buffer38encoding38", "YnVmZmVyMzhlbmNvZGluZzM4"),
    ("queue38encoding38", "cXVldWUzOGVuY29kaW5nMzg"),
    ("queue38mapping38", "cXVldWUzOG1hcHBpbmczOA"),
    ("queue38record38", "cXVldWUzOHJlY29yZDM4"),
    ("queue38candle38", "cXVldWUzOGNhbmRsZTM4"),
    ("worker38candle38", "d29ya2VyMzhjYW5kbGUzOA"),
    ("worker38thread38", "d29ya2VyMzh0aHJlYWQzOA"),
    ("worker38kitten38", "d29ya2VyMzhraXR0ZW4zOA"),
    ("worker38sitting38", "d29ya2VyMzhzaXR0aW5nMzg"),
    ("kernel38sitting38", "a2VybmVsMzhzaXR0aW5nMzg"),
    ("kernel38agent38", "a2VybmVsMzhhZ2VudDM4"),
    ("kernel38angle38", "a2VybmVsMzhhbmdsZTM4"),
    ("kernel38universe38", "a2VybmVsMzh1bml2ZXJzZTM4"),
    ("signal38universe38", "c2lnbmFsMzh1bml2ZXJzZTM4"),
    ("signal38memory38", "c2lnbmFsMzhtZW1vcnkzOA"),
    ("signal38stream38", "c2lnbmFsMzhzdHJlYW0zOA"),
    ("signal38context38", "c2lnbmFsMzhjb250ZXh0Mzg"),
    ("packet38context38", "cGFja2V0Mzhjb250ZXh0Mzg"),
    ("packet38knowledge38", "cGFja2V0Mzhrbm93bGVkZ2UzOA"),
    ("packet38vector38", "cGFja2V0Mzh2ZWN0b3IzOA"),
    ("packet38processor38", "cGFja2V0Mzhwcm9jZXNzb3IzOA"),
    ("router38processor38", "cm91dGVyMzhwcm9jZXNzb3IzOA"),
    ("router38reasoning38", "cm91dGVyMzhyZWFzb25pbmczOA"),
    ("router38machine38", "cm91dGVyMzhtYWNoaW5lMzg"),
    ("router38learning38", "cm91dGVyMzhsZWFybmluZzM4"),
    ("cluster38learning38", "Y2x1c3RlcjM4bGVhcm5pbmczOA"),
    ("cluster38model38", "Y2x1c3RlcjM4bW9kZWwzOA"),
    ("cluster38token38", "Y2x1c3RlcjM4dG9rZW4zOA"),
    ("cluster38prompt38", "Y2x1c3RlcjM4cHJvbXB0Mzg"),
    ("mirror38prompt38", "bWlycm9yMzhwcm9tcHQzOA"),
    ("mirror38session38", "bWlycm9yMzhzZXNzaW9uMzg"),
    ("mirror38library38", "bWlycm9yMzhsaWJyYXJ5Mzg"),
    ("mirror38service38", "bWlycm9yMzhzZXJ2aWNlMzg"),
    ("filter38service38", "ZmlsdGVyMzhzZXJ2aWNlMzg"),
    ("filter38gateway38", "ZmlsdGVyMzhnYXRld2F5Mzg"),
    ("filter38storage38", "ZmlsdGVyMzhzdG9yYWdlMzg"),
    ("filter38network38", "ZmlsdGVyMzhuZXR3b3JrMzg"),
    ("ranking38network38", "cmFua2luZzM4bmV0d29yazM4"),
    ("ranking38latency38", "cmFua2luZzM4bGF0ZW5jeTM4"),
    ("ranking38buffer38", "cmFua2luZzM4YnVmZmVyMzg"),
    ("ranking38queue38", "cmFua2luZzM4cXVldWUzOA"),
    ("encoding38queue38", "ZW5jb2RpbmczOHF1ZXVlMzg"),
    ("encoding38worker38", "ZW5jb2RpbmczOHdvcmtlcjM4"),
    ("encoding38kernel38", "ZW5jb2RpbmczOGtlcm5lbDM4"),
    ("encoding38signal38", "ZW5jb2RpbmczOHNpZ25hbDM4"),
    ("mapping38signal38", "bWFwcGluZzM4c2lnbmFsMzg"),
    ("mapping38packet38", "bWFwcGluZzM4cGFja2V0Mzg"),
    ("mapping38router38", "bWFwcGluZzM4cm91dGVyMzg"),
    ("mapping38cluster38", "bWFwcGluZzM4Y2x1c3RlcjM4"),
    ("record38cluster38", "cmVjb3JkMzhjbHVzdGVyMzg"),
    ("record38mirror38", "cmVjb3JkMzhtaXJyb3IzOA"),
    ("record38filter38", "cmVjb3JkMzhmaWx0ZXIzOA"),
    ("record38ranking38", "cmVjb3JkMzhyYW5raW5nMzg"),
    ("candle38ranking38", "Y2FuZGxlMzhyYW5raW5nMzg"),
    ("candle38encoding38", "Y2FuZGxlMzhlbmNvZGluZzM4"),
    ("candle38mapping38", "Y2FuZGxlMzhtYXBwaW5nMzg"),
    ("candle38record38", "Y2FuZGxlMzhyZWNvcmQzOA"),
    ("thread38record38", "dGhyZWFkMzhyZWNvcmQzOA"),
    ("thread38candle38", "dGhyZWFkMzhjYW5kbGUzOA"),
    ("thread38thread38", "dGhyZWFkMzh0aHJlYWQzOA"),
    ("thread38kitten38", "dGhyZWFkMzhraXR0ZW4zOA"),
    (
        "round 38: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMzg6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 38: agentuniverse is a framework for multi agents",
        "cm91bmQgMzg6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 38: knowledge stored as vectors enables retrieval",
        "cm91bmQgMzg6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 38: the processor reads the record then stops",
        "cm91bmQgMzg6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 38: a worker pulls the next task from the queue",
        "cm91bmQgMzg6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 38: signals travel through the network layer",
        "cm91bmQgMzg6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 38: the gateway routes each request by policy",
        "cm91bmQgMzg6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 38: memory grows until the buffer is full",
        "cm91bmQgMzg6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 38: the cluster mirrors every packet twice",
        "cm91bmQgMzg6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 38: ranking uses tokens learned from the corpus",
        "cm91bmQgMzg6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 38: a long session ends when the candle dies",
        "cm91bmQgMzg6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 38: encode the prompt then map the result",
        "cm91bmQgMzg6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 38: the kernel wakes the worker at dawn", "cm91bmQgMzg6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 38: service latency drops after the patch",
        "cm91bmQgMzg6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 38: the library caches every vector it sees",
        "cm91bmQgMzg6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 38: agents argue then the debate resolves",
        "cm91bmQgMzg6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 38: the filter keeps only strong matches",
        "cm91bmQgMzg6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 38: the model answers with a short reply",
        "cm91bmQgMzg6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 38: the recorder stores the reasoning trace",
        "cm91bmQgMzg6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 38: the angel watches the processor run", "cm91bmQgMzg6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 38: angle of the vector decides the match",
        "cm91bmQgMzg6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 38: the candle burns twice as long at night",
        "cm91bmQgMzg6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 38: a mirror of the universe in one line",
        "cm91bmQgMzg6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 38: the queue drains before the storm", "cm91bmQgMzg6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
