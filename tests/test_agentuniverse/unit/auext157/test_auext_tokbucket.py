"""Token bucket limiter: deterministic known-answer vectors (auext)."""

def _ref_token_bucket(case):
    """Integer token bucket: (capacity, refill rate, (time, need) events).

    Events must be sorted by non-decreasing time; the bucket starts full and
    the answer lists whether each request was satisfied.
    """
    cap, rate, events = case
    tokens = cap
    last = 0
    ok = []
    for t, need in events:
        if t > last:
            gain = (t - last) * rate
            if gain > 0:
                tokens = tokens + gain
                if tokens > cap:
                    tokens = cap
        last = t
        good = tokens >= need
        if good:
            tokens -= need
        ok.append(good)
    return ok

_CASES = [
    ((1, 1, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, False, True, True]),
    ((2, 1, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((3, 1, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((4, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (5, 1, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (1, 1, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [False, True, True, False, True, True, False, True, True],
    ),
    (
        (2, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            3,
            2,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            4,
            2,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((5, 2, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((1, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, False, True, True]),
    ((2, 2, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((3, 2, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (4, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (5, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (1, 3, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, False, True, True, False, True, True, False, True, True],
    ),
    (
        (
            2,
            3,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            3,
            3,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((4, 3, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((5, 3, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((1, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [False, True, True, False, True, True]),
    ((2, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (3, 1, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (4, 1, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (5, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            1,
            1,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, False, True, True, False, True, True, False, True, True],
    ),
    (
        (
            2,
            1,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((3, 1, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((4, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((5, 2, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((1, 2, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, False, True, True, False, True, True]),
    (
        (2, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (3, 2, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (4, 2, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            5,
            2,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            1,
            3,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [False, True, True, False, True, True, False, True, True, False, True, True],
    ),
    ((2, 3, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((3, 3, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((4, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((5, 3, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (1, 3, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, False, True, True, False, True, True],
    ),
    (
        (2, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (3, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            4,
            1,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            5,
            1,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((1, 1, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, False, True, True]),
    ((2, 1, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((3, 1, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((4, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (5, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (1, 2, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [False, True, True, False, True, True, False, True, True],
    ),
    (
        (2, 2, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            3,
            2,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            4,
            2,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((5, 2, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((1, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, False, True, True]),
    ((2, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((3, 3, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (4, 3, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (5, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (1, 3, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, False, True, True, False, True, True, False, True, True],
    ),
    (
        (
            2,
            3,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            3,
            3,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((4, 1, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((5, 1, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((1, 1, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [False, True, True, False, True, True]),
    ((2, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (3, 1, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (4, 1, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (5, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            1,
            2,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, False, True, True, False, True, True, False, True, True],
    ),
    (
        (
            2,
            2,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((3, 2, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((4, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((5, 2, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((1, 2, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, False, True, True, False, True, True]),
    (
        (2, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (3, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (4, 3, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            5,
            3,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            1,
            3,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [False, True, True, False, True, True, False, True, True, False, True, True],
    ),
    ((2, 3, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((3, 3, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((4, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((5, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (1, 1, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, False, True, True, False, True, True],
    ),
    (
        (2, 1, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (3, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            4,
            1,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            5,
            1,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((1, 1, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, False, True, True]),
    ((2, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((3, 2, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((4, 2, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (5, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (1, 2, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [False, True, True, False, True, True, False, True, True],
    ),
    (
        (2, 2, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            3,
            2,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            4,
            3,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((5, 3, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((1, 3, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, False, True, True]),
    ((2, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((3, 3, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (4, 3, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (5, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (1, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, False, True, True, False, True, True, False, True, True],
    ),
    (
        (
            2,
            1,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            3,
            1,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((4, 1, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((5, 1, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((1, 1, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [False, True, True, False, True, True]),
    ((2, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (3, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (4, 2, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (5, 2, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            1,
            2,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, False, True, True, False, True, True, False, True, True],
    ),
    (
        (
            2,
            2,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((3, 2, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((4, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((5, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((1, 3, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, False, True, True, False, True, True]),
    (
        (2, 3, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (3, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (4, 3, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            5,
            3,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            1,
            3,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [False, True, True, False, True, True, False, True, True, False, True, True],
    ),
    ((2, 1, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((3, 1, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((4, 1, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((5, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (1, 1, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, False, True, True, False, True, True],
    ),
    (
        (2, 1, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    (
        (3, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            4,
            2,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            5,
            2,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((1, 2, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, False, True, True]),
    ((2, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, True, True, True]),
    ((3, 2, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((4, 2, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (5, 2, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (1, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [False, True, True, False, True, True, False, True, True],
    ),
    (
        (2, 3, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0), (16, 2), (18, 1), (19, 0)]),
        [True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            3,
            3,
            [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0), (18, 2), (20, 1), (21, 0)],
        ),
        [True, True, True, True, True, True, True, True, True, True, True],
    ),
    (
        (
            4,
            3,
            [
                (3, 2),
                (5, 1),
                (6, 0),
                (9, 2),
                (11, 1),
                (12, 0),
                (15, 2),
                (17, 1),
                (18, 0),
                (21, 2),
                (23, 1),
                (24, 0),
            ],
        ),
        [True, True, True, True, True, True, True, True, True, True, True, True],
    ),
    ((5, 3, [(1, 0), (4, 2), (6, 1), (7, 0)]), [True, True, True, True]),
    ((1, 3, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0)]), [True, True, False, True, True]),
    ((2, 3, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0)]), [True, True, True, True, True, True]),
    ((3, 1, [(1, 0), (4, 2), (6, 1), (7, 0), (10, 2), (12, 1), (13, 0)]), [True, True, True, True, True, True, True]),
    (
        (4, 1, [(2, 1), (3, 0), (6, 2), (8, 1), (9, 0), (12, 2), (14, 1), (15, 0)]),
        [True, True, True, True, True, True, True, True],
    ),
    (
        (5, 1, [(3, 2), (5, 1), (6, 0), (9, 2), (11, 1), (12, 0), (15, 2), (17, 1), (18, 0)]),
        [True, True, True, True, True, True, True, True, True],
    ),
    ((0, 1, [(1, 0), (2, 1)]), [True, False]),
    ((3, 0, [(1, 2), (1, 1)]), [True, True]),
]

_EXPECTED_COUNT = 152

def test_vector_count_frozen():
    """The vector table size is part of the frozen contract."""
    assert len(_CASES) == _EXPECTED_COUNT

def test_vectors_000():
    """Known-answer vectors 0..119."""
    for case, expected in _CASES[0:120]:
        assert _ref_token_bucket(case) == expected

def test_vectors_120():
    """Known-answer vectors 120..151."""
    for case, expected in _CASES[120:152]:
        assert _ref_token_bucket(case) == expected

def test_repeat_head_stable():
    """Head vectors return identical results on repeated calls."""
    for case, expected in _CASES[:64]:
        assert _ref_token_bucket(case) == expected
        assert _ref_token_bucket(case) == expected

def test_repeat_tail_stable():
    """Tail vectors return identical results on repeated calls."""
    for case, expected in _CASES[-64:]:
        assert _ref_token_bucket(case) == expected
        assert _ref_token_bucket(case) == expected
