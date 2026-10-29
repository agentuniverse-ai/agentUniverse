"""Unpadded URL-safe base 64: deterministic known-answer vectors (auext)."""

import base64

def _ref_b64_url(case):
    """URL-safe base 64 without padding of the UTF-8 encoded input."""
    raw = base64.urlsafe_b64encode(case.encode("utf-8")).decode("ascii")
    while raw.endswith("="):
        raw = raw[:-1]
    return raw

_CASES = [
    ("kitten186kitten186", "a2l0dGVuMTg2a2l0dGVuMTg2"),
    ("kitten186sitting186", "a2l0dGVuMTg2c2l0dGluZzE4Ng"),
    ("kitten186agent186", "a2l0dGVuMTg2YWdlbnQxODY"),
    ("kitten186angle186", "a2l0dGVuMTg2YW5nbGUxODY"),
    ("sitting186angle186", "c2l0dGluZzE4NmFuZ2xlMTg2"),
    ("sitting186universe186", "c2l0dGluZzE4NnVuaXZlcnNlMTg2"),
    ("sitting186memory186", "c2l0dGluZzE4Nm1lbW9yeTE4Ng"),
    ("sitting186stream186", "c2l0dGluZzE4NnN0cmVhbTE4Ng"),
    ("agent186stream186", "YWdlbnQxODZzdHJlYW0xODY"),
    ("agent186context186", "YWdlbnQxODZjb250ZXh0MTg2"),
    ("agent186knowledge186", "YWdlbnQxODZrbm93bGVkZ2UxODY"),
    ("agent186vector186", "YWdlbnQxODZ2ZWN0b3IxODY"),
    ("angle186vector186", "YW5nbGUxODZ2ZWN0b3IxODY"),
    ("angle186processor186", "YW5nbGUxODZwcm9jZXNzb3IxODY"),
    ("angle186reasoning186", "YW5nbGUxODZyZWFzb25pbmcxODY"),
    ("angle186machine186", "YW5nbGUxODZtYWNoaW5lMTg2"),
    ("universe186machine186", "dW5pdmVyc2UxODZtYWNoaW5lMTg2"),
    ("universe186learning186", "dW5pdmVyc2UxODZsZWFybmluZzE4Ng"),
    ("universe186model186", "dW5pdmVyc2UxODZtb2RlbDE4Ng"),
    ("universe186token186", "dW5pdmVyc2UxODZ0b2tlbjE4Ng"),
    ("memory186token186", "bWVtb3J5MTg2dG9rZW4xODY"),
    ("memory186prompt186", "bWVtb3J5MTg2cHJvbXB0MTg2"),
    ("memory186session186", "bWVtb3J5MTg2c2Vzc2lvbjE4Ng"),
    ("memory186library186", "bWVtb3J5MTg2bGlicmFyeTE4Ng"),
    ("stream186library186", "c3RyZWFtMTg2bGlicmFyeTE4Ng"),
    ("stream186service186", "c3RyZWFtMTg2c2VydmljZTE4Ng"),
    ("stream186gateway186", "c3RyZWFtMTg2Z2F0ZXdheTE4Ng"),
    ("stream186storage186", "c3RyZWFtMTg2c3RvcmFnZTE4Ng"),
    ("context186storage186", "Y29udGV4dDE4NnN0b3JhZ2UxODY"),
    ("context186network186", "Y29udGV4dDE4Nm5ldHdvcmsxODY"),
    ("context186latency186", "Y29udGV4dDE4NmxhdGVuY3kxODY"),
    ("context186buffer186", "Y29udGV4dDE4NmJ1ZmZlcjE4Ng"),
    ("knowledge186buffer186", "a25vd2xlZGdlMTg2YnVmZmVyMTg2"),
    ("knowledge186queue186", "a25vd2xlZGdlMTg2cXVldWUxODY"),
    ("knowledge186worker186", "a25vd2xlZGdlMTg2d29ya2VyMTg2"),
    ("knowledge186kernel186", "a25vd2xlZGdlMTg2a2VybmVsMTg2"),
    ("vector186kernel186", "dmVjdG9yMTg2a2VybmVsMTg2"),
    ("vector186signal186", "dmVjdG9yMTg2c2lnbmFsMTg2"),
    ("vector186packet186", "dmVjdG9yMTg2cGFja2V0MTg2"),
    ("vector186router186", "dmVjdG9yMTg2cm91dGVyMTg2"),
    ("processor186router186", "cHJvY2Vzc29yMTg2cm91dGVyMTg2"),
    ("processor186cluster186", "cHJvY2Vzc29yMTg2Y2x1c3RlcjE4Ng"),
    ("processor186mirror186", "cHJvY2Vzc29yMTg2bWlycm9yMTg2"),
    ("processor186filter186", "cHJvY2Vzc29yMTg2ZmlsdGVyMTg2"),
    ("reasoning186filter186", "cmVhc29uaW5nMTg2ZmlsdGVyMTg2"),
    ("reasoning186ranking186", "cmVhc29uaW5nMTg2cmFua2luZzE4Ng"),
    ("reasoning186encoding186", "cmVhc29uaW5nMTg2ZW5jb2RpbmcxODY"),
    ("reasoning186mapping186", "cmVhc29uaW5nMTg2bWFwcGluZzE4Ng"),
    ("machine186mapping186", "bWFjaGluZTE4Nm1hcHBpbmcxODY"),
    ("machine186record186", "bWFjaGluZTE4NnJlY29yZDE4Ng"),
    ("machine186candle186", "bWFjaGluZTE4NmNhbmRsZTE4Ng"),
    ("machine186thread186", "bWFjaGluZTE4NnRocmVhZDE4Ng"),
    ("learning186thread186", "bGVhcm5pbmcxODZ0aHJlYWQxODY"),
    ("learning186kitten186", "bGVhcm5pbmcxODZraXR0ZW4xODY"),
    ("learning186sitting186", "bGVhcm5pbmcxODZzaXR0aW5nMTg2"),
    ("learning186agent186", "bGVhcm5pbmcxODZhZ2VudDE4Ng"),
    ("model186agent186", "bW9kZWwxODZhZ2VudDE4Ng"),
    ("model186angle186", "bW9kZWwxODZhbmdsZTE4Ng"),
    ("model186universe186", "bW9kZWwxODZ1bml2ZXJzZTE4Ng"),
    ("model186memory186", "bW9kZWwxODZtZW1vcnkxODY"),
    ("token186memory186", "dG9rZW4xODZtZW1vcnkxODY"),
    ("token186stream186", "dG9rZW4xODZzdHJlYW0xODY"),
    ("token186context186", "dG9rZW4xODZjb250ZXh0MTg2"),
    ("token186knowledge186", "dG9rZW4xODZrbm93bGVkZ2UxODY"),
    ("prompt186knowledge186", "cHJvbXB0MTg2a25vd2xlZGdlMTg2"),
    ("prompt186vector186", "cHJvbXB0MTg2dmVjdG9yMTg2"),
    ("prompt186processor186", "cHJvbXB0MTg2cHJvY2Vzc29yMTg2"),
    ("prompt186reasoning186", "cHJvbXB0MTg2cmVhc29uaW5nMTg2"),
    ("session186reasoning186", "c2Vzc2lvbjE4NnJlYXNvbmluZzE4Ng"),
    ("session186machine186", "c2Vzc2lvbjE4Nm1hY2hpbmUxODY"),
    ("session186learning186", "c2Vzc2lvbjE4NmxlYXJuaW5nMTg2"),
    ("session186model186", "c2Vzc2lvbjE4Nm1vZGVsMTg2"),
    ("library186model186", "bGlicmFyeTE4Nm1vZGVsMTg2"),
    ("library186token186", "bGlicmFyeTE4NnRva2VuMTg2"),
    ("library186prompt186", "bGlicmFyeTE4NnByb21wdDE4Ng"),
    ("library186session186", "bGlicmFyeTE4NnNlc3Npb24xODY"),
    ("service186session186", "c2VydmljZTE4NnNlc3Npb24xODY"),
    ("service186library186", "c2VydmljZTE4NmxpYnJhcnkxODY"),
    ("service186service186", "c2VydmljZTE4NnNlcnZpY2UxODY"),
    ("service186gateway186", "c2VydmljZTE4NmdhdGV3YXkxODY"),
    ("gateway186gateway186", "Z2F0ZXdheTE4NmdhdGV3YXkxODY"),
    ("gateway186storage186", "Z2F0ZXdheTE4NnN0b3JhZ2UxODY"),
    ("gateway186network186", "Z2F0ZXdheTE4Nm5ldHdvcmsxODY"),
    ("gateway186latency186", "Z2F0ZXdheTE4NmxhdGVuY3kxODY"),
    ("storage186latency186", "c3RvcmFnZTE4NmxhdGVuY3kxODY"),
    ("storage186buffer186", "c3RvcmFnZTE4NmJ1ZmZlcjE4Ng"),
    ("storage186queue186", "c3RvcmFnZTE4NnF1ZXVlMTg2"),
    ("storage186worker186", "c3RvcmFnZTE4NndvcmtlcjE4Ng"),
    ("network186worker186", "bmV0d29yazE4NndvcmtlcjE4Ng"),
    ("network186kernel186", "bmV0d29yazE4Nmtlcm5lbDE4Ng"),
    ("network186signal186", "bmV0d29yazE4NnNpZ25hbDE4Ng"),
    ("network186packet186", "bmV0d29yazE4NnBhY2tldDE4Ng"),
    ("latency186packet186", "bGF0ZW5jeTE4NnBhY2tldDE4Ng"),
    ("latency186router186", "bGF0ZW5jeTE4NnJvdXRlcjE4Ng"),
    ("latency186cluster186", "bGF0ZW5jeTE4NmNsdXN0ZXIxODY"),
    ("latency186mirror186", "bGF0ZW5jeTE4Nm1pcnJvcjE4Ng"),
    ("buffer186mirror186", "YnVmZmVyMTg2bWlycm9yMTg2"),
    ("buffer186filter186", "YnVmZmVyMTg2ZmlsdGVyMTg2"),
    ("buffer186ranking186", "YnVmZmVyMTg2cmFua2luZzE4Ng"),
    ("buffer186encoding186", "YnVmZmVyMTg2ZW5jb2RpbmcxODY"),
    ("queue186encoding186", "cXVldWUxODZlbmNvZGluZzE4Ng"),
    ("queue186mapping186", "cXVldWUxODZtYXBwaW5nMTg2"),
    ("queue186record186", "cXVldWUxODZyZWNvcmQxODY"),
    ("queue186candle186", "cXVldWUxODZjYW5kbGUxODY"),
    ("worker186candle186", "d29ya2VyMTg2Y2FuZGxlMTg2"),
    ("worker186thread186", "d29ya2VyMTg2dGhyZWFkMTg2"),
    ("worker186kitten186", "d29ya2VyMTg2a2l0dGVuMTg2"),
    ("worker186sitting186", "d29ya2VyMTg2c2l0dGluZzE4Ng"),
    ("kernel186sitting186", "a2VybmVsMTg2c2l0dGluZzE4Ng"),
    ("kernel186agent186", "a2VybmVsMTg2YWdlbnQxODY"),
    ("kernel186angle186", "a2VybmVsMTg2YW5nbGUxODY"),
    ("kernel186universe186", "a2VybmVsMTg2dW5pdmVyc2UxODY"),
    ("signal186universe186", "c2lnbmFsMTg2dW5pdmVyc2UxODY"),
    ("signal186memory186", "c2lnbmFsMTg2bWVtb3J5MTg2"),
    ("signal186stream186", "c2lnbmFsMTg2c3RyZWFtMTg2"),
    ("signal186context186", "c2lnbmFsMTg2Y29udGV4dDE4Ng"),
    ("packet186context186", "cGFja2V0MTg2Y29udGV4dDE4Ng"),
    ("packet186knowledge186", "cGFja2V0MTg2a25vd2xlZGdlMTg2"),
    ("packet186vector186", "cGFja2V0MTg2dmVjdG9yMTg2"),
    ("packet186processor186", "cGFja2V0MTg2cHJvY2Vzc29yMTg2"),
    ("router186processor186", "cm91dGVyMTg2cHJvY2Vzc29yMTg2"),
    ("router186reasoning186", "cm91dGVyMTg2cmVhc29uaW5nMTg2"),
    ("router186machine186", "cm91dGVyMTg2bWFjaGluZTE4Ng"),
    ("router186learning186", "cm91dGVyMTg2bGVhcm5pbmcxODY"),
    ("cluster186learning186", "Y2x1c3RlcjE4NmxlYXJuaW5nMTg2"),
    ("cluster186model186", "Y2x1c3RlcjE4Nm1vZGVsMTg2"),
    ("cluster186token186", "Y2x1c3RlcjE4NnRva2VuMTg2"),
    ("cluster186prompt186", "Y2x1c3RlcjE4NnByb21wdDE4Ng"),
    ("mirror186prompt186", "bWlycm9yMTg2cHJvbXB0MTg2"),
    ("mirror186session186", "bWlycm9yMTg2c2Vzc2lvbjE4Ng"),
    ("mirror186library186", "bWlycm9yMTg2bGlicmFyeTE4Ng"),
    ("mirror186service186", "bWlycm9yMTg2c2VydmljZTE4Ng"),
    ("filter186service186", "ZmlsdGVyMTg2c2VydmljZTE4Ng"),
    ("filter186gateway186", "ZmlsdGVyMTg2Z2F0ZXdheTE4Ng"),
    ("filter186storage186", "ZmlsdGVyMTg2c3RvcmFnZTE4Ng"),
    ("filter186network186", "ZmlsdGVyMTg2bmV0d29yazE4Ng"),
    ("ranking186network186", "cmFua2luZzE4Nm5ldHdvcmsxODY"),
    ("ranking186latency186", "cmFua2luZzE4NmxhdGVuY3kxODY"),
    ("ranking186buffer186", "cmFua2luZzE4NmJ1ZmZlcjE4Ng"),
    ("ranking186queue186", "cmFua2luZzE4NnF1ZXVlMTg2"),
    ("encoding186queue186", "ZW5jb2RpbmcxODZxdWV1ZTE4Ng"),
    ("encoding186worker186", "ZW5jb2RpbmcxODZ3b3JrZXIxODY"),
    ("encoding186kernel186", "ZW5jb2RpbmcxODZrZXJuZWwxODY"),
    ("encoding186signal186", "ZW5jb2RpbmcxODZzaWduYWwxODY"),
    ("mapping186signal186", "bWFwcGluZzE4NnNpZ25hbDE4Ng"),
    ("mapping186packet186", "bWFwcGluZzE4NnBhY2tldDE4Ng"),
    ("mapping186router186", "bWFwcGluZzE4NnJvdXRlcjE4Ng"),
    ("mapping186cluster186", "bWFwcGluZzE4NmNsdXN0ZXIxODY"),
    ("record186cluster186", "cmVjb3JkMTg2Y2x1c3RlcjE4Ng"),
    ("record186mirror186", "cmVjb3JkMTg2bWlycm9yMTg2"),
    ("record186filter186", "cmVjb3JkMTg2ZmlsdGVyMTg2"),
    ("record186ranking186", "cmVjb3JkMTg2cmFua2luZzE4Ng"),
    ("candle186ranking186", "Y2FuZGxlMTg2cmFua2luZzE4Ng"),
    ("candle186encoding186", "Y2FuZGxlMTg2ZW5jb2RpbmcxODY"),
    ("candle186mapping186", "Y2FuZGxlMTg2bWFwcGluZzE4Ng"),
    ("candle186record186", "Y2FuZGxlMTg2cmVjb3JkMTg2"),
    ("thread186record186", "dGhyZWFkMTg2cmVjb3JkMTg2"),
    ("thread186candle186", "dGhyZWFkMTg2Y2FuZGxlMTg2"),
    ("thread186thread186", "dGhyZWFkMTg2dGhyZWFkMTg2"),
    ("thread186kitten186", "dGhyZWFkMTg2a2l0dGVuMTg2"),
    (
        "round 186: the quick brown fox jumps over the lazy dog",
        "cm91bmQgMTg2OiB0aGUgcXVpY2sgYnJvd24gZm94IGp1bXBzIG92ZXIgdGhlIGxhenkgZG9n",
    ),
    (
        "round 186: agentuniverse is a framework for multi agents",
        "cm91bmQgMTg2OiBhZ2VudHVuaXZlcnNlIGlzIGEgZnJhbWV3b3JrIGZvciBtdWx0aSBhZ2VudHM",
    ),
    (
        "round 186: knowledge stored as vectors enables retrieval",
        "cm91bmQgMTg2OiBrbm93bGVkZ2Ugc3RvcmVkIGFzIHZlY3RvcnMgZW5hYmxlcyByZXRyaWV2YWw",
    ),
    (
        "round 186: the processor reads the record then stops",
        "cm91bmQgMTg2OiB0aGUgcHJvY2Vzc29yIHJlYWRzIHRoZSByZWNvcmQgdGhlbiBzdG9wcw",
    ),
    (
        "round 186: a worker pulls the next task from the queue",
        "cm91bmQgMTg2OiBhIHdvcmtlciBwdWxscyB0aGUgbmV4dCB0YXNrIGZyb20gdGhlIHF1ZXVl",
    ),
    (
        "round 186: signals travel through the network layer",
        "cm91bmQgMTg2OiBzaWduYWxzIHRyYXZlbCB0aHJvdWdoIHRoZSBuZXR3b3JrIGxheWVy",
    ),
    (
        "round 186: the gateway routes each request by policy",
        "cm91bmQgMTg2OiB0aGUgZ2F0ZXdheSByb3V0ZXMgZWFjaCByZXF1ZXN0IGJ5IHBvbGljeQ",
    ),
    (
        "round 186: memory grows until the buffer is full",
        "cm91bmQgMTg2OiBtZW1vcnkgZ3Jvd3MgdW50aWwgdGhlIGJ1ZmZlciBpcyBmdWxs",
    ),
    (
        "round 186: the cluster mirrors every packet twice",
        "cm91bmQgMTg2OiB0aGUgY2x1c3RlciBtaXJyb3JzIGV2ZXJ5IHBhY2tldCB0d2ljZQ",
    ),
    (
        "round 186: ranking uses tokens learned from the corpus",
        "cm91bmQgMTg2OiByYW5raW5nIHVzZXMgdG9rZW5zIGxlYXJuZWQgZnJvbSB0aGUgY29ycHVz",
    ),
    (
        "round 186: a long session ends when the candle dies",
        "cm91bmQgMTg2OiBhIGxvbmcgc2Vzc2lvbiBlbmRzIHdoZW4gdGhlIGNhbmRsZSBkaWVz",
    ),
    (
        "round 186: encode the prompt then map the result",
        "cm91bmQgMTg2OiBlbmNvZGUgdGhlIHByb21wdCB0aGVuIG1hcCB0aGUgcmVzdWx0",
    ),
    (
        "round 186: the kernel wakes the worker at dawn",
        "cm91bmQgMTg2OiB0aGUga2VybmVsIHdha2VzIHRoZSB3b3JrZXIgYXQgZGF3bg",
    ),
    (
        "round 186: service latency drops after the patch",
        "cm91bmQgMTg2OiBzZXJ2aWNlIGxhdGVuY3kgZHJvcHMgYWZ0ZXIgdGhlIHBhdGNo",
    ),
    (
        "round 186: the library caches every vector it sees",
        "cm91bmQgMTg2OiB0aGUgbGlicmFyeSBjYWNoZXMgZXZlcnkgdmVjdG9yIGl0IHNlZXM",
    ),
    (
        "round 186: agents argue then the debate resolves",
        "cm91bmQgMTg2OiBhZ2VudHMgYXJndWUgdGhlbiB0aGUgZGViYXRlIHJlc29sdmVz",
    ),
    (
        "round 186: the filter keeps only strong matches",
        "cm91bmQgMTg2OiB0aGUgZmlsdGVyIGtlZXBzIG9ubHkgc3Ryb25nIG1hdGNoZXM",
    ),
    (
        "round 186: the model answers with a short reply",
        "cm91bmQgMTg2OiB0aGUgbW9kZWwgYW5zd2VycyB3aXRoIGEgc2hvcnQgcmVwbHk",
    ),
    (
        "round 186: the recorder stores the reasoning trace",
        "cm91bmQgMTg2OiB0aGUgcmVjb3JkZXIgc3RvcmVzIHRoZSByZWFzb25pbmcgdHJhY2U",
    ),
    (
        "round 186: the angel watches the processor run",
        "cm91bmQgMTg2OiB0aGUgYW5nZWwgd2F0Y2hlcyB0aGUgcHJvY2Vzc29yIHJ1bg",
    ),
    (
        "round 186: angle of the vector decides the match",
        "cm91bmQgMTg2OiBhbmdsZSBvZiB0aGUgdmVjdG9yIGRlY2lkZXMgdGhlIG1hdGNo",
    ),
    (
        "round 186: the candle burns twice as long at night",
        "cm91bmQgMTg2OiB0aGUgY2FuZGxlIGJ1cm5zIHR3aWNlIGFzIGxvbmcgYXQgbmlnaHQ",
    ),
    (
        "round 186: a mirror of the universe in one line",
        "cm91bmQgMTg2OiBhIG1pcnJvciBvZiB0aGUgdW5pdmVyc2UgaW4gb25lIGxpbmU",
    ),
    ("round 186: the queue drains before the storm", "cm91bmQgMTg2OiB0aGUgcXVldWUgZHJhaW5zIGJlZm9yZSB0aGUgc3Rvcm0"),
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
