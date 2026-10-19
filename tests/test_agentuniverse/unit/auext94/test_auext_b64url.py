"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten94kitten94", "a2l0dGVuOTRraXR0ZW45NA"),
    ("kitten94sitting94", "a2l0dGVuOTRzaXR0aW5nOTQ"),
    ("kitten94agent94", "a2l0dGVuOTRhZ2VudDk0"),
    ("kitten94angle94", "a2l0dGVuOTRhbmdsZTk0"),
    ("sitting94angle94", "c2l0dGluZzk0YW5nbGU5NA"),
    ("sitting94universe94", "c2l0dGluZzk0dW5pdmVyc2U5NA"),
    ("sitting94memory94", "c2l0dGluZzk0bWVtb3J5OTQ"),
    ("sitting94stream94", "c2l0dGluZzk0c3RyZWFtOTQ"),
    ("agent94stream94", "YWdlbnQ5NHN0cmVhbTk0"),
    ("agent94context94", "YWdlbnQ5NGNvbnRleHQ5NA"),
    ("agent94knowledge94", "YWdlbnQ5NGtub3dsZWRnZTk0"),
    ("agent94vector94", "YWdlbnQ5NHZlY3Rvcjk0"),
    ("angle94vector94", "YW5nbGU5NHZlY3Rvcjk0"),
    ("angle94processor94", "YW5nbGU5NHByb2Nlc3Nvcjk0"),
    ("angle94reasoning94", "YW5nbGU5NHJlYXNvbmluZzk0"),
    ("angle94machine94", "YW5nbGU5NG1hY2hpbmU5NA"),
    ("universe94machine94", "dW5pdmVyc2U5NG1hY2hpbmU5NA"),
    ("universe94learning94", "dW5pdmVyc2U5NGxlYXJuaW5nOTQ"),
    ("universe94model94", "dW5pdmVyc2U5NG1vZGVsOTQ"),
    ("universe94token94", "dW5pdmVyc2U5NHRva2VuOTQ"),
    ("memory94token94", "bWVtb3J5OTR0b2tlbjk0"),
    ("memory94prompt94", "bWVtb3J5OTRwcm9tcHQ5NA"),
    ("memory94session94", "bWVtb3J5OTRzZXNzaW9uOTQ"),
    ("memory94library94", "bWVtb3J5OTRsaWJyYXJ5OTQ"),
    ("stream94library94", "c3RyZWFtOTRsaWJyYXJ5OTQ"),
    ("stream94service94", "c3RyZWFtOTRzZXJ2aWNlOTQ"),
    ("stream94gateway94", "c3RyZWFtOTRnYXRld2F5OTQ"),
    ("stream94storage94", "c3RyZWFtOTRzdG9yYWdlOTQ"),
    ("context94storage94", "Y29udGV4dDk0c3RvcmFnZTk0"),
    ("context94network94", "Y29udGV4dDk0bmV0d29yazk0"),
    ("context94latency94", "Y29udGV4dDk0bGF0ZW5jeTk0"),
    ("context94buffer94", "Y29udGV4dDk0YnVmZmVyOTQ"),
    ("knowledge94buffer94", "a25vd2xlZGdlOTRidWZmZXI5NA"),
    ("knowledge94queue94", "a25vd2xlZGdlOTRxdWV1ZTk0"),
    ("knowledge94worker94", "a25vd2xlZGdlOTR3b3JrZXI5NA"),
    ("knowledge94kernel94", "a25vd2xlZGdlOTRrZXJuZWw5NA"),
    ("vector94kernel94", "dmVjdG9yOTRrZXJuZWw5NA"),
    ("vector94signal94", "dmVjdG9yOTRzaWduYWw5NA"),
    ("vector94packet94", "dmVjdG9yOTRwYWNrZXQ5NA"),
    ("vector94router94", "dmVjdG9yOTRyb3V0ZXI5NA"),
    ("processor94router94", "cHJvY2Vzc29yOTRyb3V0ZXI5NA"),
    ("processor94cluster94", "cHJvY2Vzc29yOTRjbHVzdGVyOTQ"),
    ("processor94mirror94", "cHJvY2Vzc29yOTRtaXJyb3I5NA"),
    ("processor94filter94", "cHJvY2Vzc29yOTRmaWx0ZXI5NA"),
    ("reasoning94filter94", "cmVhc29uaW5nOTRmaWx0ZXI5NA"),
    ("reasoning94ranking94", "cmVhc29uaW5nOTRyYW5raW5nOTQ"),
    ("reasoning94encoding94", "cmVhc29uaW5nOTRlbmNvZGluZzk0"),
    ("reasoning94mapping94", "cmVhc29uaW5nOTRtYXBwaW5nOTQ"),
    ("machine94mapping94", "bWFjaGluZTk0bWFwcGluZzk0"),
    ("machine94record94", "bWFjaGluZTk0cmVjb3JkOTQ"),
    ("machine94candle94", "bWFjaGluZTk0Y2FuZGxlOTQ"),
    ("machine94thread94", "bWFjaGluZTk0dGhyZWFkOTQ"),
    ("learning94thread94", "bGVhcm5pbmc5NHRocmVhZDk0"),
    ("learning94kitten94", "bGVhcm5pbmc5NGtpdHRlbjk0"),
    ("learning94sitting94", "bGVhcm5pbmc5NHNpdHRpbmc5NA"),
    ("learning94agent94", "bGVhcm5pbmc5NGFnZW50OTQ"),
    ("model94agent94", "bW9kZWw5NGFnZW50OTQ"),
    ("model94angle94", "bW9kZWw5NGFuZ2xlOTQ"),
    ("model94universe94", "bW9kZWw5NHVuaXZlcnNlOTQ"),
    ("model94memory94", "bW9kZWw5NG1lbW9yeTk0"),
    ("token94memory94", "dG9rZW45NG1lbW9yeTk0"),
    ("token94stream94", "dG9rZW45NHN0cmVhbTk0"),
    ("token94context94", "dG9rZW45NGNvbnRleHQ5NA"),
    ("token94knowledge94", "dG9rZW45NGtub3dsZWRnZTk0"),
    ("prompt94knowledge94", "cHJvbXB0OTRrbm93bGVkZ2U5NA"),
    ("prompt94vector94", "cHJvbXB0OTR2ZWN0b3I5NA"),
    ("prompt94processor94", "cHJvbXB0OTRwcm9jZXNzb3I5NA"),
    ("prompt94reasoning94", "cHJvbXB0OTRyZWFzb25pbmc5NA"),
    ("session94reasoning94", "c2Vzc2lvbjk0cmVhc29uaW5nOTQ"),
    ("session94machine94", "c2Vzc2lvbjk0bWFjaGluZTk0"),
    ("session94learning94", "c2Vzc2lvbjk0bGVhcm5pbmc5NA"),
    ("session94model94", "c2Vzc2lvbjk0bW9kZWw5NA"),
    ("library94model94", "bGlicmFyeTk0bW9kZWw5NA"),
    ("library94token94", "bGlicmFyeTk0dG9rZW45NA"),
    ("library94prompt94", "bGlicmFyeTk0cHJvbXB0OTQ"),
    ("library94session94", "bGlicmFyeTk0c2Vzc2lvbjk0"),
    ("service94session94", "c2VydmljZTk0c2Vzc2lvbjk0"),
    ("service94library94", "c2VydmljZTk0bGlicmFyeTk0"),
    ("service94service94", "c2VydmljZTk0c2VydmljZTk0"),
    ("service94gateway94", "c2VydmljZTk0Z2F0ZXdheTk0"),
    ("gateway94gateway94", "Z2F0ZXdheTk0Z2F0ZXdheTk0"),
    ("gateway94storage94", "Z2F0ZXdheTk0c3RvcmFnZTk0"),
    ("gateway94network94", "Z2F0ZXdheTk0bmV0d29yazk0"),
    ("gateway94latency94", "Z2F0ZXdheTk0bGF0ZW5jeTk0"),
    ("storage94latency94", "c3RvcmFnZTk0bGF0ZW5jeTk0"),
    ("storage94buffer94", "c3RvcmFnZTk0YnVmZmVyOTQ"),
    ("storage94queue94", "c3RvcmFnZTk0cXVldWU5NA"),
    ("storage94worker94", "c3RvcmFnZTk0d29ya2VyOTQ"),
    ("network94worker94", "bmV0d29yazk0d29ya2VyOTQ"),
    ("network94kernel94", "bmV0d29yazk0a2VybmVsOTQ"),
    ("network94signal94", "bmV0d29yazk0c2lnbmFsOTQ"),
    ("network94packet94", "bmV0d29yazk0cGFja2V0OTQ"),
    ("latency94packet94", "bGF0ZW5jeTk0cGFja2V0OTQ"),
    ("latency94router94", "bGF0ZW5jeTk0cm91dGVyOTQ"),
    ("latency94cluster94", "bGF0ZW5jeTk0Y2x1c3Rlcjk0"),
    ("latency94mirror94", "bGF0ZW5jeTk0bWlycm9yOTQ"),
    ("buffer94mirror94", "YnVmZmVyOTRtaXJyb3I5NA"),
    ("buffer94filter94", "YnVmZmVyOTRmaWx0ZXI5NA"),
    ("buffer94ranking94", "YnVmZmVyOTRyYW5raW5nOTQ"),
    ("buffer94encoding94", "YnVmZmVyOTRlbmNvZGluZzk0"),
    ("queue94encoding94", "cXVldWU5NGVuY29kaW5nOTQ"),
    ("queue94mapping94", "cXVldWU5NG1hcHBpbmc5NA"),
    ("queue94record94", "cXVldWU5NHJlY29yZDk0"),
    ("queue94candle94", "cXVldWU5NGNhbmRsZTk0"),
    ("worker94candle94", "d29ya2VyOTRjYW5kbGU5NA"),
    ("worker94thread94", "d29ya2VyOTR0aHJlYWQ5NA"),
    ("worker94kitten94", "d29ya2VyOTRraXR0ZW45NA"),
    ("worker94sitting94", "d29ya2VyOTRzaXR0aW5nOTQ"),
    ("kernel94sitting94", "a2VybmVsOTRzaXR0aW5nOTQ"),
    ("kernel94agent94", "a2VybmVsOTRhZ2VudDk0"),
    ("kernel94angle94", "a2VybmVsOTRhbmdsZTk0"),
    ("kernel94universe94", "a2VybmVsOTR1bml2ZXJzZTk0"),
    ("signal94universe94", "c2lnbmFsOTR1bml2ZXJzZTk0"),
    ("signal94memory94", "c2lnbmFsOTRtZW1vcnk5NA"),
    ("signal94stream94", "c2lnbmFsOTRzdHJlYW05NA"),
    ("signal94context94", "c2lnbmFsOTRjb250ZXh0OTQ"),
    ("packet94context94", "cGFja2V0OTRjb250ZXh0OTQ"),
    ("packet94knowledge94", "cGFja2V0OTRrbm93bGVkZ2U5NA"),
    ("packet94vector94", "cGFja2V0OTR2ZWN0b3I5NA"),
    ("packet94processor94", "cGFja2V0OTRwcm9jZXNzb3I5NA"),
    ("router94processor94", "cm91dGVyOTRwcm9jZXNzb3I5NA"),
    ("router94reasoning94", "cm91dGVyOTRyZWFzb25pbmc5NA"),
    ("router94machine94", "cm91dGVyOTRtYWNoaW5lOTQ"),
    ("router94learning94", "cm91dGVyOTRsZWFybmluZzk0"),
    ("cluster94learning94", "Y2x1c3Rlcjk0bGVhcm5pbmc5NA"),
    ("cluster94model94", "Y2x1c3Rlcjk0bW9kZWw5NA"),
    ("cluster94token94", "Y2x1c3Rlcjk0dG9rZW45NA"),
    ("cluster94prompt94", "Y2x1c3Rlcjk0cHJvbXB0OTQ"),
    ("mirror94prompt94", "bWlycm9yOTRwcm9tcHQ5NA"),
    ("mirror94session94", "bWlycm9yOTRzZXNzaW9uOTQ"),
    ("mirror94library94", "bWlycm9yOTRsaWJyYXJ5OTQ"),
    ("mirror94service94", "bWlycm9yOTRzZXJ2aWNlOTQ"),
    ("filter94service94", "ZmlsdGVyOTRzZXJ2aWNlOTQ"),
    ("filter94gateway94", "ZmlsdGVyOTRnYXRld2F5OTQ"),
    ("filter94storage94", "ZmlsdGVyOTRzdG9yYWdlOTQ"),
    ("filter94network94", "ZmlsdGVyOTRuZXR3b3JrOTQ"),
    ("ranking94network94", "cmFua2luZzk0bmV0d29yazk0"),
    ("ranking94latency94", "cmFua2luZzk0bGF0ZW5jeTk0"),
    ("ranking94buffer94", "cmFua2luZzk0YnVmZmVyOTQ"),
    ("ranking94queue94", "cmFua2luZzk0cXVldWU5NA"),
    ("encoding94queue94", "ZW5jb2Rpbmc5NHF1ZXVlOTQ"),
    ("encoding94worker94", "ZW5jb2Rpbmc5NHdvcmtlcjk0"),
    ("encoding94kernel94", "ZW5jb2Rpbmc5NGtlcm5lbDk0"),
    ("encoding94signal94", "ZW5jb2Rpbmc5NHNpZ25hbDk0"),
    ("mapping94signal94", "bWFwcGluZzk0c2lnbmFsOTQ"),
    ("mapping94packet94", "bWFwcGluZzk0cGFja2V0OTQ"),
    ("mapping94router94", "bWFwcGluZzk0cm91dGVyOTQ"),
    ("mapping94cluster94", "bWFwcGluZzk0Y2x1c3Rlcjk0"),
    ("record94cluster94", "cmVjb3JkOTRjbHVzdGVyOTQ"),
    ("record94mirror94", "cmVjb3JkOTRtaXJyb3I5NA"),
    ("record94filter94", "cmVjb3JkOTRmaWx0ZXI5NA"),
    ("record94ranking94", "cmVjb3JkOTRyYW5raW5nOTQ"),
    ("candle94ranking94", "Y2FuZGxlOTRyYW5raW5nOTQ"),
    ("candle94encoding94", "Y2FuZGxlOTRlbmNvZGluZzk0"),
    ("candle94mapping94", "Y2FuZGxlOTRtYXBwaW5nOTQ"),
    ("candle94record94", "Y2FuZGxlOTRyZWNvcmQ5NA"),
    ("thread94record94", "dGhyZWFkOTRyZWNvcmQ5NA"),
    ("thread94candle94", "dGhyZWFkOTRjYW5kbGU5NA"),
    ("thread94thread94", "dGhyZWFkOTR0aHJlYWQ5NA"),
    ("thread94kitten94", "dGhyZWFkOTRraXR0ZW45NA"),
    (
        "round 94: the quick brown fox jumps over the lazy dog",
        "cm91bmQgOTQ6IHRoZSBxdWljayBicm93biBmb3gganVtcHMgb3ZlciB0aGUgbGF6eSBkb2c",
    ),
    (
        "round 94: agentuniverse is a framework for multi agents",
        "cm91bmQgOTQ6IGFnZW50dW5pdmVyc2UgaXMgYSBmcmFtZXdvcmsgZm9yIG11bHRpIGFnZW50cw",
    ),
    (
        "round 94: knowledge stored as vectors enables retrieval",
        "cm91bmQgOTQ6IGtub3dsZWRnZSBzdG9yZWQgYXMgdmVjdG9ycyBlbmFibGVzIHJldHJpZXZhbA",
    ),
    (
        "round 94: the processor reads the record then stops",
        "cm91bmQgOTQ6IHRoZSBwcm9jZXNzb3IgcmVhZHMgdGhlIHJlY29yZCB0aGVuIHN0b3Bz",
    ),
    (
        "round 94: a worker pulls the next task from the queue",
        "cm91bmQgOTQ6IGEgd29ya2VyIHB1bGxzIHRoZSBuZXh0IHRhc2sgZnJvbSB0aGUgcXVldWU",
    ),
    (
        "round 94: signals travel through the network layer",
        "cm91bmQgOTQ6IHNpZ25hbHMgdHJhdmVsIHRocm91Z2ggdGhlIG5ldHdvcmsgbGF5ZXI",
    ),
    (
        "round 94: the gateway routes each request by policy",
        "cm91bmQgOTQ6IHRoZSBnYXRld2F5IHJvdXRlcyBlYWNoIHJlcXVlc3QgYnkgcG9saWN5",
    ),
    (
        "round 94: memory grows until the buffer is full",
        "cm91bmQgOTQ6IG1lbW9yeSBncm93cyB1bnRpbCB0aGUgYnVmZmVyIGlzIGZ1bGw",
    ),
    (
        "round 94: the cluster mirrors every packet twice",
        "cm91bmQgOTQ6IHRoZSBjbHVzdGVyIG1pcnJvcnMgZXZlcnkgcGFja2V0IHR3aWNl",
    ),
    (
        "round 94: ranking uses tokens learned from the corpus",
        "cm91bmQgOTQ6IHJhbmtpbmcgdXNlcyB0b2tlbnMgbGVhcm5lZCBmcm9tIHRoZSBjb3JwdXM",
    ),
    (
        "round 94: a long session ends when the candle dies",
        "cm91bmQgOTQ6IGEgbG9uZyBzZXNzaW9uIGVuZHMgd2hlbiB0aGUgY2FuZGxlIGRpZXM",
    ),
    (
        "round 94: encode the prompt then map the result",
        "cm91bmQgOTQ6IGVuY29kZSB0aGUgcHJvbXB0IHRoZW4gbWFwIHRoZSByZXN1bHQ",
    ),
    ("round 94: the kernel wakes the worker at dawn", "cm91bmQgOTQ6IHRoZSBrZXJuZWwgd2FrZXMgdGhlIHdvcmtlciBhdCBkYXdu"),
    (
        "round 94: service latency drops after the patch",
        "cm91bmQgOTQ6IHNlcnZpY2UgbGF0ZW5jeSBkcm9wcyBhZnRlciB0aGUgcGF0Y2g",
    ),
    (
        "round 94: the library caches every vector it sees",
        "cm91bmQgOTQ6IHRoZSBsaWJyYXJ5IGNhY2hlcyBldmVyeSB2ZWN0b3IgaXQgc2Vlcw",
    ),
    (
        "round 94: agents argue then the debate resolves",
        "cm91bmQgOTQ6IGFnZW50cyBhcmd1ZSB0aGVuIHRoZSBkZWJhdGUgcmVzb2x2ZXM",
    ),
    (
        "round 94: the filter keeps only strong matches",
        "cm91bmQgOTQ6IHRoZSBmaWx0ZXIga2VlcHMgb25seSBzdHJvbmcgbWF0Y2hlcw",
    ),
    (
        "round 94: the model answers with a short reply",
        "cm91bmQgOTQ6IHRoZSBtb2RlbCBhbnN3ZXJzIHdpdGggYSBzaG9ydCByZXBseQ",
    ),
    (
        "round 94: the recorder stores the reasoning trace",
        "cm91bmQgOTQ6IHRoZSByZWNvcmRlciBzdG9yZXMgdGhlIHJlYXNvbmluZyB0cmFjZQ",
    ),
    ("round 94: the angel watches the processor run", "cm91bmQgOTQ6IHRoZSBhbmdlbCB3YXRjaGVzIHRoZSBwcm9jZXNzb3IgcnVu"),
    (
        "round 94: angle of the vector decides the match",
        "cm91bmQgOTQ6IGFuZ2xlIG9mIHRoZSB2ZWN0b3IgZGVjaWRlcyB0aGUgbWF0Y2g",
    ),
    (
        "round 94: the candle burns twice as long at night",
        "cm91bmQgOTQ6IHRoZSBjYW5kbGUgYnVybnMgdHdpY2UgYXMgbG9uZyBhdCBuaWdodA",
    ),
    (
        "round 94: a mirror of the universe in one line",
        "cm91bmQgOTQ6IGEgbWlycm9yIG9mIHRoZSB1bml2ZXJzZSBpbiBvbmUgbGluZQ",
    ),
    ("round 94: the queue drains before the storm", "cm91bmQgOTQ6IHRoZSBxdWV1ZSBkcmFpbnMgYmVmb3JlIHRoZSBzdG9ybQ"),
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
