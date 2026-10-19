"""Semantic version comparison: deterministic known-answer vectors (auext)."""

def _ref_semver_compare(case):
    """Compare two semantic versions; -1, 0, 1, or -9 when either is invalid.

    Numeric parts dominate, then a prerelease loses to its absence, then
    prerelease identifiers compare with numeric < alphanumeric < none.
    """
    a, b = case

    def parse(v):
        core = v
        if "+" in core:
            core = core.split("+")[0]
        pre = None
        if "-" in core:
            core, pre = core.split("-", 1)
        parts = core.split(".")
        if len(parts) != 3:
            return None
        nums = []
        for p in parts:
            if not p or not p.isdigit():
                return None
            nums.append(int(p))
        return nums, pre

    pa = parse(a)
    pb = parse(b)
    if pa is None or pb is None:
        return -9
    if pa[0] < pb[0]:
        return -1
    if pa[0] > pb[0]:
        return 1
    if pa[1] == pb[1]:
        return 0
    if pa[1] is None:
        return 1
    if pb[1] is None:
        return -1
    ta = pa[1].split(".")
    tb = pb[1].split(".")

    def rank(tok):
        if tok.isdigit():
            return (0, int(tok), "")
        return (1, 0, tok)

    for i in range(min(len(ta), len(tb))):
        ra, rb = rank(ta[i]), rank(tb[i])
        if ra < rb:
            return -1
        if ra > rb:
            return 1
    if len(ta) < len(tb):
        return -1
    if len(ta) > len(tb):
        return 1
    return 0

_CASES = [
    (("1.2.3", "1.2.3"), 0),
    (("1.2.3", "1.2.3-rc.1"), 1),
    (("1.2.3", "1.2.3-rc.2"), 1),
    (("1.2.3", "1.2.10"), -1),
    (("1.2.3", "0.9.9"), 1),
    (("1.2.3", "1.2"), -9),
    (("1.2.3", "1.2.3+build"), 0),
    (("1.2.3", "2.0.0-1"), -1),
    (("1.2.3", "2.0.0-alpha"), -1),
    (("1.2.3", "1.2.3-0.3.7"), 1),
    (("1.2.3", "1.2.3-7"), 1),
    (("1.2.3-rc.1", "1.2.3"), -1),
    (("1.2.3-rc.1", "1.2.3-rc.1"), 0),
    (("1.2.3-rc.1", "1.2.3-rc.2"), -1),
    (("1.2.3-rc.1", "1.2.10"), -1),
    (("1.2.3-rc.1", "0.9.9"), 1),
    (("1.2.3-rc.1", "1.2"), -9),
    (("1.2.3-rc.1", "1.2.3+build"), -1),
    (("1.2.3-rc.1", "2.0.0-1"), -1),
    (("1.2.3-rc.1", "2.0.0-alpha"), -1),
    (("1.2.3-rc.1", "1.2.3-0.3.7"), 1),
    (("1.2.3-rc.1", "1.2.3-7"), 1),
    (("1.2.3-rc.2", "1.2.3"), -1),
    (("1.2.3-rc.2", "1.2.3-rc.1"), 1),
    (("1.2.3-rc.2", "1.2.3-rc.2"), 0),
    (("1.2.3-rc.2", "1.2.10"), -1),
    (("1.2.3-rc.2", "0.9.9"), 1),
    (("1.2.3-rc.2", "1.2"), -9),
    (("1.2.3-rc.2", "1.2.3+build"), -1),
    (("1.2.3-rc.2", "2.0.0-1"), -1),
    (("1.2.3-rc.2", "2.0.0-alpha"), -1),
    (("1.2.3-rc.2", "1.2.3-0.3.7"), 1),
    (("1.2.3-rc.2", "1.2.3-7"), 1),
    (("1.2.10", "1.2.3"), 1),
    (("1.2.10", "1.2.3-rc.1"), 1),
    (("1.2.10", "1.2.3-rc.2"), 1),
    (("1.2.10", "1.2.10"), 0),
    (("1.2.10", "0.9.9"), 1),
    (("1.2.10", "1.2"), -9),
    (("1.2.10", "1.2.3+build"), 1),
    (("1.2.10", "2.0.0-1"), -1),
    (("1.2.10", "2.0.0-alpha"), -1),
    (("1.2.10", "1.2.3-0.3.7"), 1),
    (("1.2.10", "1.2.3-7"), 1),
    (("0.9.9", "1.2.3"), -1),
    (("0.9.9", "1.2.3-rc.1"), -1),
    (("0.9.9", "1.2.3-rc.2"), -1),
    (("0.9.9", "1.2.10"), -1),
    (("0.9.9", "0.9.9"), 0),
    (("0.9.9", "1.2"), -9),
    (("0.9.9", "1.2.3+build"), -1),
    (("0.9.9", "2.0.0-1"), -1),
    (("0.9.9", "2.0.0-alpha"), -1),
    (("0.9.9", "1.2.3-0.3.7"), -1),
    (("0.9.9", "1.2.3-7"), -1),
    (("1.2", "1.2.3"), -9),
    (("1.2", "1.2.3-rc.1"), -9),
    (("1.2", "1.2.3-rc.2"), -9),
    (("1.2", "1.2.10"), -9),
    (("1.2", "0.9.9"), -9),
    (("1.2", "1.2"), -9),
    (("1.2", "1.2.3+build"), -9),
    (("1.2", "2.0.0-1"), -9),
    (("1.2", "2.0.0-alpha"), -9),
    (("1.2", "1.2.3-0.3.7"), -9),
    (("1.2", "1.2.3-7"), -9),
    (("1.2.3+build", "1.2.3"), 0),
    (("1.2.3+build", "1.2.3-rc.1"), 1),
    (("1.2.3+build", "1.2.3-rc.2"), 1),
    (("1.2.3+build", "1.2.10"), -1),
    (("1.2.3+build", "0.9.9"), 1),
    (("1.2.3+build", "1.2"), -9),
    (("1.2.3+build", "1.2.3+build"), 0),
    (("1.2.3+build", "2.0.0-1"), -1),
    (("1.2.3+build", "2.0.0-alpha"), -1),
    (("1.2.3+build", "1.2.3-0.3.7"), 1),
    (("1.2.3+build", "1.2.3-7"), 1),
    (("2.0.0-1", "1.2.3"), 1),
    (("2.0.0-1", "1.2.3-rc.1"), 1),
    (("2.0.0-1", "1.2.3-rc.2"), 1),
    (("2.0.0-1", "1.2.10"), 1),
    (("2.0.0-1", "0.9.9"), 1),
    (("2.0.0-1", "1.2"), -9),
    (("2.0.0-1", "1.2.3+build"), 1),
    (("2.0.0-1", "2.0.0-1"), 0),
    (("2.0.0-1", "2.0.0-alpha"), -1),
    (("2.0.0-1", "1.2.3-0.3.7"), 1),
    (("2.0.0-1", "1.2.3-7"), 1),
    (("2.0.0-alpha", "1.2.3"), 1),
    (("2.0.0-alpha", "1.2.3-rc.1"), 1),
    (("2.0.0-alpha", "1.2.3-rc.2"), 1),
    (("2.0.0-alpha", "1.2.10"), 1),
    (("2.0.0-alpha", "0.9.9"), 1),
    (("2.0.0-alpha", "1.2"), -9),
    (("2.0.0-alpha", "1.2.3+build"), 1),
    (("2.0.0-alpha", "2.0.0-1"), 1),
    (("2.0.0-alpha", "2.0.0-alpha"), 0),
    (("2.0.0-alpha", "1.2.3-0.3.7"), 1),
    (("2.0.0-alpha", "1.2.3-7"), 1),
    (("1.2.3-0.3.7", "1.2.3"), -1),
    (("1.2.3-0.3.7", "1.2.3-rc.1"), -1),
    (("1.2.3-0.3.7", "1.2.3-rc.2"), -1),
    (("1.2.3-0.3.7", "1.2.10"), -1),
    (("1.2.3-0.3.7", "0.9.9"), 1),
    (("1.2.3-0.3.7", "1.2"), -9),
    (("1.2.3-0.3.7", "1.2.3+build"), -1),
    (("1.2.3-0.3.7", "2.0.0-1"), -1),
    (("1.2.3-0.3.7", "2.0.0-alpha"), -1),
    (("1.2.3-0.3.7", "1.2.3-0.3.7"), 0),
    (("1.2.3-0.3.7", "1.2.3-7"), -1),
    (("1.2.3-7", "1.2.3"), -1),
    (("1.2.3-7", "1.2.3-rc.1"), -1),
    (("1.2.3-7", "1.2.3-rc.2"), -1),
    (("1.2.3-7", "1.2.10"), -1),
    (("1.2.3-7", "0.9.9"), 1),
    (("1.2.3-7", "1.2"), -9),
    (("1.2.3-7", "1.2.3+build"), -1),
    (("1.2.3-7", "2.0.0-1"), -1),
    (("1.2.3-7", "2.0.0-alpha"), -1),
    (("1.2.3-7", "1.2.3-0.3.7"), 1),
    (("1.2.3-7", "1.2.3-7"), 0),
    (("1.0.0", "1.0.0"), 0),
    (("01.2.3", "1.2.3"), 0),
    (("1..3", "1.2.3"), -9),
    (("1.2.3.4", "1.2.3"), -9),
    (("v1.2.3", "1.2.3"), -9),
    (("", "1.2.3"), -9),
]

_EXPECTED_COUNT = 127

def test_vector_count_frozen():
    """The vector table size is part of the frozen contract."""
    assert len(_CASES) == _EXPECTED_COUNT

def test_vectors_000():
    """Known-answer vectors 0..119."""
    for case, expected in _CASES[0:120]:
        assert _ref_semver_compare(case) == expected

def test_vectors_120():
    """Known-answer vectors 120..126."""
    for case, expected in _CASES[120:127]:
        assert _ref_semver_compare(case) == expected

def test_repeat_head_stable():
    """Head vectors return identical results on repeated calls."""
    for case, expected in _CASES[:64]:
        assert _ref_semver_compare(case) == expected
        assert _ref_semver_compare(case) == expected

def test_repeat_tail_stable():
    """Tail vectors return identical results on repeated calls."""
    for case, expected in _CASES[-64:]:
        assert _ref_semver_compare(case) == expected
        assert _ref_semver_compare(case) == expected
