"""Jaccard similarity: deterministic known-answer vectors (auext)."""

def _ref_jaccard(case):
    """Jaccard similarity of the token sets of two lists, 1.0 when both empty."""
    a, b = case
    sa = set(a)
    sb = set(b)
    union = sa | sb
    if not union:
        return 1.0
    return round(len(sa & sb) / len(union), 6)

_CASES = [
    ((["alpha", "epsilon", "iota", "omicron", "tau"], ["alpha", "kappa", "phi", "sparta", "milos", "cosmos"]), 0.1),
    (
        (
            ["beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["gamma", "omicron", "omega", "kilos", "telos", "selene", "zeta"],
        ),
        0.181818,
    ),
    (
        (
            ["gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            ["zeta", "sigma", "oracle", "naxos", "pathos", "pallas", "iota", "upsilon"],
        ),
        0.071429,
    ),
    (
        (
            ["epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["iota", "upsilon", "athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia"],
        ),
        0.133333,
    ),
    (
        (
            ["zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["lambda", "psi", "lydia", "paros", "helios", "epsilon", "rho", "mythos", "delos", "ethos"],
        ),
        0.117647,
    ),
    (
        (
            ["theta", "lambda", "sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["rho", "mythos", "delos", "ethos", "hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha"],
        ),
        0.166667,
    ),
    (
        (
            ["iota", "omicron", "tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            [
                "tau",
                "delphi",
                "rhodes",
                "logos",
                "alpha",
                "kappa",
                "phi",
                "sparta",
                "milos",
                "cosmos",
                "gamma",
                "omicron",
            ],
        ),
        0.210526,
    ),
    (
        (
            [
                "kappa",
                "rho",
                "upsilon",
                "omega",
                "delphi",
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
            ],
            ["phi", "sparta", "milos", "cosmos"],
        ),
        0.066667,
    ),
    ((["lambda", "sigma", "phi", "mythos", "athens"], ["omega", "kilos", "telos", "selene", "zeta"]), 0.0),
    (
        (
            ["omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["oracle", "naxos", "pathos", "pallas", "iota", "upsilon"],
        ),
        0.090909,
    ),
    (
        (
            ["rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia"],
        ),
        0.076923,
    ),
    (
        (
            ["sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["lydia", "paros", "helios", "epsilon", "rho", "mythos", "delos", "ethos"],
        ),
        0.142857,
    ),
    (
        (
            ["tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["delos", "ethos", "hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha"],
        ),
        0.2,
    ),
    (
        (
            ["upsilon", "omega", "delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["rhodes", "logos", "alpha", "kappa", "phi", "sparta", "milos", "cosmos", "gamma", "omicron"],
        ),
        0.111111,
    ),
    (
        (
            [
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
            ],
            [
                "milos",
                "cosmos",
                "gamma",
                "omicron",
                "omega",
                "kilos",
                "telos",
                "selene",
                "zeta",
                "sigma",
                "oracle",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "psi",
                "oracle",
                "sparta",
                "delos",
                "corfu",
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
            ],
            [
                "telos",
                "selene",
                "zeta",
                "sigma",
                "oracle",
                "naxos",
                "pathos",
                "pallas",
                "iota",
                "upsilon",
                "athens",
                "corfu",
            ],
        ),
        0.2,
    ),
    ((["omega", "delphi", "lydia", "naxos", "milos"], ["pathos", "pallas", "iota", "upsilon"]), 0.0),
    ((["mythos", "athens", "kilos", "rhodes", "paros", "pathos"], ["nomos", "beta", "lambda", "psi", "lydia"]), 0.0),
    (
        (
            ["oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["helios", "epsilon", "rho", "mythos", "delos", "ethos"],
        ),
        0.181818,
    ),
    (
        (
            ["delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha"],
        ),
        0.153846,
    ),
    (
        (
            ["athens", "kilos", "rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"],
            ["alpha", "kappa", "phi", "sparta", "milos", "cosmos", "gamma", "omicron"],
        ),
        0.0625,
    ),
    (
        (
            ["sparta", "delos", "corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["gamma", "omicron", "omega", "kilos", "telos", "selene", "zeta", "sigma", "oracle"],
        ),
        0.117647,
    ),
    (
        (
            [
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
            ],
            ["zeta", "sigma", "oracle", "naxos", "pathos", "pallas", "iota", "upsilon", "athens", "corfu"],
        ),
        0.105263,
    ),
    (
        (
            [
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
                "kappa",
                "rho",
                "upsilon",
                "omega",
            ],
            ["iota", "upsilon", "athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia", "paros", "helios"],
        ),
        0.15,
    ),
    (
        (
            ["delos", "corfu", "telos", "logos", "helios"],
            [
                "lambda",
                "psi",
                "lydia",
                "paros",
                "helios",
                "epsilon",
                "rho",
                "mythos",
                "delos",
                "ethos",
                "hermes",
                "theta",
            ],
        ),
        0.133333,
    ),
    ((["naxos", "milos", "ethos", "nomos", "selene", "alpha"], ["rho", "mythos", "delos", "ethos"]), 0.111111),
    (
        (
            ["rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"],
            ["tau", "delphi", "rhodes", "logos", "alpha"],
        ),
        0.090909,
    ),
    (
        (
            ["corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["phi", "sparta", "milos", "cosmos", "gamma", "omicron"],
        ),
        0.076923,
    ),
    (
        (
            ["milos", "ethos", "nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"],
            ["omega", "kilos", "telos", "selene", "zeta", "sigma", "oracle"],
        ),
        0.066667,
    ),
    (
        (
            ["paros", "pathos", "cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["oracle", "naxos", "pathos", "pallas", "iota", "upsilon", "athens", "corfu"],
        ),
        0.125,
    ),
    (
        (
            [
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
            ],
            ["athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia", "paros", "helios"],
        ),
        0.176471,
    ),
    (
        (
            [
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
                "psi",
                "oracle",
                "sparta",
                "delos",
            ],
            ["lydia", "paros", "helios", "epsilon", "rho", "mythos", "delos", "ethos", "hermes", "theta"],
        ),
        0.157895,
    ),
    (
        (
            ["pathos", "cosmos", "hermes", "beta", "zeta"],
            ["delos", "ethos", "hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi"],
        ),
        0.066667,
    ),
    (
        (
            ["logos", "helios", "pallas", "gamma", "theta", "lambda"],
            [
                "rhodes",
                "logos",
                "alpha",
                "kappa",
                "phi",
                "sparta",
                "milos",
                "cosmos",
                "gamma",
                "omicron",
                "omega",
                "kilos",
            ],
        ),
        0.125,
    ),
    ((["nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"], ["milos", "cosmos", "gamma", "omicron"]), 0.1),
    (
        (
            ["cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["telos", "selene", "zeta", "sigma", "oracle"],
        ),
        0.083333,
    ),
    (
        (
            ["helios", "pallas", "gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            ["pathos", "pallas", "iota", "upsilon", "athens", "corfu"],
        ),
        0.153846,
    ),
    (
        (
            ["selene", "alpha", "epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["nomos", "beta", "lambda", "psi", "lydia", "paros", "helios"],
        ),
        0.0625,
    ),
    (
        (
            ["hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["helios", "epsilon", "rho", "mythos", "delos", "ethos", "hermes", "theta"],
        ),
        0.117647,
    ),
    (
        (
            [
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
            ],
            ["hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi"],
        ),
        0.166667,
    ),
    (
        (
            ["alpha", "epsilon", "iota", "omicron", "tau"],
            ["alpha", "kappa", "phi", "sparta", "milos", "cosmos", "gamma", "omicron", "omega", "kilos"],
        ),
        0.153846,
    ),
    (
        (
            ["beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            [
                "gamma",
                "omicron",
                "omega",
                "kilos",
                "telos",
                "selene",
                "zeta",
                "sigma",
                "oracle",
                "naxos",
                "pathos",
            ],
        ),
        0.133333,
    ),
    (
        (
            ["gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            [
                "zeta",
                "sigma",
                "oracle",
                "naxos",
                "pathos",
                "pallas",
                "iota",
                "upsilon",
                "athens",
                "corfu",
                "nomos",
                "beta",
            ],
        ),
        0.117647,
    ),
    (
        (
            ["epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["iota", "upsilon", "athens", "corfu"],
        ),
        0.090909,
    ),
    (
        (
            ["zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["lambda", "psi", "lydia", "paros", "helios"],
        ),
        0.076923,
    ),
    (
        (
            ["theta", "lambda", "sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["rho", "mythos", "delos", "ethos", "hermes", "theta"],
        ),
        0.142857,
    ),
    (
        (
            ["iota", "omicron", "tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi"],
        ),
        0.125,
    ),
    (
        (
            [
                "kappa",
                "rho",
                "upsilon",
                "omega",
                "delphi",
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
            ],
            ["phi", "sparta", "milos", "cosmos", "gamma", "omicron", "omega", "kilos"],
        ),
        0.111111,
    ),
    (
        (
            ["lambda", "sigma", "phi", "mythos", "athens"],
            ["omega", "kilos", "telos", "selene", "zeta", "sigma", "oracle", "naxos", "pathos"],
        ),
        0.076923,
    ),
    (
        (
            ["omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["oracle", "naxos", "pathos", "pallas", "iota", "upsilon", "athens", "corfu", "nomos", "beta"],
        ),
        0.066667,
    ),
    (
        (
            ["rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia", "paros", "helios", "epsilon", "rho"],
        ),
        0.125,
    ),
    (
        (
            ["sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            [
                "lydia",
                "paros",
                "helios",
                "epsilon",
                "rho",
                "mythos",
                "delos",
                "ethos",
                "hermes",
                "theta",
                "tau",
                "delphi",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["delos", "ethos", "hermes", "theta"],
        ),
        0.083333,
    ),
    (
        (
            ["upsilon", "omega", "delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["rhodes", "logos", "alpha", "kappa", "phi"],
        ),
        0.071429,
    ),
    (
        (
            [
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
            ],
            ["milos", "cosmos", "gamma", "omicron", "omega", "kilos"],
        ),
        0.133333,
    ),
    (
        (
            [
                "psi",
                "oracle",
                "sparta",
                "delos",
                "corfu",
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
            ],
            ["telos", "selene", "zeta", "sigma", "oracle", "naxos", "pathos"],
        ),
        0.117647,
    ),
    (
        (
            ["omega", "delphi", "lydia", "naxos", "milos"],
            ["pathos", "pallas", "iota", "upsilon", "athens", "corfu", "nomos", "beta"],
        ),
        0.0,
    ),
    (
        (
            ["mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["nomos", "beta", "lambda", "psi", "lydia", "paros", "helios", "epsilon", "rho"],
        ),
        0.071429,
    ),
    (
        (
            ["oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["helios", "epsilon", "rho", "mythos", "delos", "ethos", "hermes", "theta", "tau", "delphi"],
        ),
        0.133333,
    ),
    (
        (
            ["delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi", "sparta", "milos"],
        ),
        0.1875,
    ),
    (
        (
            ["athens", "kilos", "rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"],
            [
                "alpha",
                "kappa",
                "phi",
                "sparta",
                "milos",
                "cosmos",
                "gamma",
                "omicron",
                "omega",
                "kilos",
                "telos",
                "selene",
            ],
        ),
        0.105263,
    ),
    (
        (
            ["sparta", "delos", "corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["gamma", "omicron", "omega", "kilos"],
        ),
        0.076923,
    ),
    (
        (
            [
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
            ],
            ["zeta", "sigma", "oracle", "naxos", "pathos"],
        ),
        0.066667,
    ),
    (
        (
            [
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
                "kappa",
                "rho",
                "upsilon",
                "omega",
            ],
            ["iota", "upsilon", "athens", "corfu", "nomos", "beta"],
        ),
        0.125,
    ),
    (
        (
            ["delos", "corfu", "telos", "logos", "helios"],
            ["lambda", "psi", "lydia", "paros", "helios", "epsilon", "rho"],
        ),
        0.090909,
    ),
    (
        (
            ["naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["rho", "mythos", "delos", "ethos", "hermes", "theta", "tau", "delphi"],
        ),
        0.076923,
    ),
    (
        (
            ["rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"],
            ["tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi", "sparta", "milos"],
        ),
        0.066667,
    ),
    (
        (
            ["corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["phi", "sparta", "milos", "cosmos", "gamma", "omicron", "omega", "kilos", "telos", "selene"],
        ),
        0.125,
    ),
    (
        (
            ["milos", "ethos", "nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"],
            [
                "omega",
                "kilos",
                "telos",
                "selene",
                "zeta",
                "sigma",
                "oracle",
                "naxos",
                "pathos",
                "pallas",
                "iota",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["paros", "pathos", "cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            [
                "oracle",
                "naxos",
                "pathos",
                "pallas",
                "iota",
                "upsilon",
                "athens",
                "corfu",
                "nomos",
                "beta",
                "lambda",
                "psi",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
            ],
            ["athens", "corfu", "nomos", "beta"],
        ),
        0.071429,
    ),
    (
        (
            [
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
                "psi",
                "oracle",
                "sparta",
                "delos",
            ],
            ["lydia", "paros", "helios", "epsilon", "rho"],
        ),
        0.0625,
    ),
    ((["pathos", "cosmos", "hermes", "beta", "zeta"], ["delos", "ethos", "hermes", "theta", "tau", "delphi"]), 0.1),
    (
        (
            ["logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["rhodes", "logos", "alpha", "kappa", "phi", "sparta", "milos"],
        ),
        0.083333,
    ),
    (
        (
            ["nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"],
            ["milos", "cosmos", "gamma", "omicron", "omega", "kilos", "telos", "selene"],
        ),
        0.153846,
    ),
    (
        (
            ["cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["telos", "selene", "zeta", "sigma", "oracle", "naxos", "pathos", "pallas", "iota"],
        ),
        0.0625,
    ),
    (
        (
            ["helios", "pallas", "gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            ["pathos", "pallas", "iota", "upsilon", "athens", "corfu", "nomos", "beta", "lambda", "psi"],
        ),
        0.1875,
    ),
    (
        (
            ["selene", "alpha", "epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["nomos", "beta", "lambda", "psi", "lydia", "paros", "helios", "epsilon", "rho", "mythos", "delos"],
        ),
        0.166667,
    ),
    (
        (
            ["hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            [
                "helios",
                "epsilon",
                "rho",
                "mythos",
                "delos",
                "ethos",
                "hermes",
                "theta",
                "tau",
                "delphi",
                "rhodes",
                "logos",
            ],
        ),
        0.15,
    ),
    (
        (
            [
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
            ],
            ["hermes", "theta", "tau", "delphi"],
        ),
        0.066667,
    ),
    ((["alpha", "epsilon", "iota", "omicron", "tau"], ["alpha", "kappa", "phi", "sparta", "milos"]), 0.111111),
    (
        (
            ["beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["gamma", "omicron", "omega", "kilos", "telos", "selene"],
        ),
        0.090909,
    ),
    (
        (
            ["gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            ["zeta", "sigma", "oracle", "naxos", "pathos", "pallas", "iota"],
        ),
        0.076923,
    ),
    (
        (
            ["epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["iota", "upsilon", "athens", "corfu", "nomos", "beta", "lambda", "psi"],
        ),
        0.142857,
    ),
    (
        (
            ["zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["lambda", "psi", "lydia", "paros", "helios", "epsilon", "rho", "mythos", "delos"],
        ),
        0.125,
    ),
    (
        (
            ["theta", "lambda", "sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["rho", "mythos", "delos", "ethos", "hermes", "theta", "tau", "delphi", "rhodes", "logos"],
        ),
        0.176471,
    ),
    (
        (
            ["iota", "omicron", "tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi", "sparta", "milos", "cosmos", "gamma"],
        ),
        0.157895,
    ),
    (
        (
            [
                "kappa",
                "rho",
                "upsilon",
                "omega",
                "delphi",
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
            ],
            [
                "phi",
                "sparta",
                "milos",
                "cosmos",
                "gamma",
                "omicron",
                "omega",
                "kilos",
                "telos",
                "selene",
                "zeta",
                "sigma",
            ],
        ),
        0.142857,
    ),
    ((["lambda", "sigma", "phi", "mythos", "athens"], ["omega", "kilos", "telos", "selene"]), 0.0),
    ((["omicron", "tau", "psi", "oracle", "sparta", "delos"], ["oracle", "naxos", "pathos", "pallas", "iota"]), 0.1),
    (
        (
            ["rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["athens", "corfu", "nomos", "beta", "lambda", "psi"],
        ),
        0.0,
    ),
    (
        (
            ["sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["lydia", "paros", "helios", "epsilon", "rho", "mythos", "delos"],
        ),
        0.153846,
    ),
    (
        (
            ["tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["delos", "ethos", "hermes", "theta", "tau", "delphi", "rhodes", "logos"],
        ),
        0.214286,
    ),
    (
        (
            ["upsilon", "omega", "delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["rhodes", "logos", "alpha", "kappa", "phi", "sparta", "milos", "cosmos", "gamma"],
        ),
        0.117647,
    ),
    (
        (
            [
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
            ],
            ["milos", "cosmos", "gamma", "omicron", "omega", "kilos", "telos", "selene", "zeta", "sigma"],
        ),
        0.166667,
    ),
    (
        (
            [
                "psi",
                "oracle",
                "sparta",
                "delos",
                "corfu",
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
            ],
            [
                "telos",
                "selene",
                "zeta",
                "sigma",
                "oracle",
                "naxos",
                "pathos",
                "pallas",
                "iota",
                "upsilon",
                "athens",
            ],
        ),
        0.15,
    ),
    (
        (
            ["omega", "delphi", "lydia", "naxos", "milos"],
            [
                "pathos",
                "pallas",
                "iota",
                "upsilon",
                "athens",
                "corfu",
                "nomos",
                "beta",
                "lambda",
                "psi",
                "lydia",
                "paros",
            ],
        ),
        0.0625,
    ),
    ((["mythos", "athens", "kilos", "rhodes", "paros", "pathos"], ["nomos", "beta", "lambda", "psi"]), 0.0),
    (
        (
            ["oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["helios", "epsilon", "rho", "mythos", "delos"],
        ),
        0.2,
    ),
    (
        (
            ["delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["hermes", "theta", "tau", "delphi", "rhodes", "logos"],
        ),
        0.076923,
    ),
    (
        (
            ["athens", "kilos", "rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"],
            ["alpha", "kappa", "phi", "sparta", "milos", "cosmos", "gamma"],
        ),
        0.066667,
    ),
    (
        (
            ["sparta", "delos", "corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["gamma", "omicron", "omega", "kilos", "telos", "selene", "zeta", "sigma"],
        ),
        0.125,
    ),
    (
        (
            [
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
            ],
            ["zeta", "sigma", "oracle", "naxos", "pathos", "pallas", "iota", "upsilon", "athens"],
        ),
        0.111111,
    ),
    (
        (
            [
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
                "kappa",
                "rho",
                "upsilon",
                "omega",
            ],
            ["iota", "upsilon", "athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia", "paros"],
        ),
        0.157895,
    ),
    (
        (
            ["delos", "corfu", "telos", "logos", "helios"],
            [
                "lambda",
                "psi",
                "lydia",
                "paros",
                "helios",
                "epsilon",
                "rho",
                "mythos",
                "delos",
                "ethos",
                "hermes",
            ],
        ),
        0.142857,
    ),
    (
        (
            ["naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            [
                "rho",
                "mythos",
                "delos",
                "ethos",
                "hermes",
                "theta",
                "tau",
                "delphi",
                "rhodes",
                "logos",
                "alpha",
                "kappa",
            ],
        ),
        0.125,
    ),
    ((["rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"], ["tau", "delphi", "rhodes", "logos"]), 0.1),
    (
        (
            ["corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["phi", "sparta", "milos", "cosmos", "gamma"],
        ),
        0.083333,
    ),
    (
        (
            ["milos", "ethos", "nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"],
            ["omega", "kilos", "telos", "selene", "zeta", "sigma"],
        ),
        0.071429,
    ),
    (
        (
            ["paros", "pathos", "cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["oracle", "naxos", "pathos", "pallas", "iota", "upsilon", "athens"],
        ),
        0.133333,
    ),
    (
        (
            [
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
            ],
            ["athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia", "paros"],
        ),
        0.117647,
    ),
    (
        (
            [
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
                "psi",
                "oracle",
                "sparta",
                "delos",
            ],
            ["lydia", "paros", "helios", "epsilon", "rho", "mythos", "delos", "ethos", "hermes"],
        ),
        0.166667,
    ),
    (
        (
            ["pathos", "cosmos", "hermes", "beta", "zeta"],
            ["delos", "ethos", "hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha", "kappa"],
        ),
        0.071429,
    ),
    (
        (
            ["logos", "helios", "pallas", "gamma", "theta", "lambda"],
            [
                "rhodes",
                "logos",
                "alpha",
                "kappa",
                "phi",
                "sparta",
                "milos",
                "cosmos",
                "gamma",
                "omicron",
                "omega",
            ],
        ),
        0.133333,
    ),
    (
        (
            ["nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"],
            [
                "milos",
                "cosmos",
                "gamma",
                "omicron",
                "omega",
                "kilos",
                "telos",
                "selene",
                "zeta",
                "sigma",
                "oracle",
                "naxos",
            ],
        ),
        0.117647,
    ),
    (
        (
            ["cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["telos", "selene", "zeta", "sigma"],
        ),
        0.090909,
    ),
    (
        (
            ["helios", "pallas", "gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            ["pathos", "pallas", "iota", "upsilon", "athens"],
        ),
        0.166667,
    ),
    (
        (
            ["selene", "alpha", "epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["nomos", "beta", "lambda", "psi", "lydia", "paros"],
        ),
        0.066667,
    ),
    (
        (
            ["hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["helios", "epsilon", "rho", "mythos", "delos", "ethos", "hermes"],
        ),
        0.125,
    ),
    (
        (
            [
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
            ],
            ["hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha", "kappa"],
        ),
        0.111111,
    ),
    (
        (
            ["alpha", "epsilon", "iota", "omicron", "tau"],
            ["alpha", "kappa", "phi", "sparta", "milos", "cosmos", "gamma", "omicron", "omega"],
        ),
        0.166667,
    ),
    (
        (
            ["beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["gamma", "omicron", "omega", "kilos", "telos", "selene", "zeta", "sigma", "oracle", "naxos"],
        ),
        0.142857,
    ),
    (
        (
            ["gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            [
                "zeta",
                "sigma",
                "oracle",
                "naxos",
                "pathos",
                "pallas",
                "iota",
                "upsilon",
                "athens",
                "corfu",
                "nomos",
            ],
        ),
        0.125,
    ),
    (
        (
            ["epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            [
                "iota",
                "upsilon",
                "athens",
                "corfu",
                "nomos",
                "beta",
                "lambda",
                "psi",
                "lydia",
                "paros",
                "helios",
                "epsilon",
            ],
        ),
        0.176471,
    ),
    (
        (
            ["zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["lambda", "psi", "lydia", "paros"],
        ),
        0.083333,
    ),
    (
        (
            ["theta", "lambda", "sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["rho", "mythos", "delos", "ethos", "hermes"],
        ),
        0.071429,
    ),
    (
        (
            ["iota", "omicron", "tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["tau", "delphi", "rhodes", "logos", "alpha", "kappa"],
        ),
        0.133333,
    ),
    (
        (
            [
                "kappa",
                "rho",
                "upsilon",
                "omega",
                "delphi",
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
            ],
            ["phi", "sparta", "milos", "cosmos", "gamma", "omicron", "omega"],
        ),
        0.117647,
    ),
    (
        (
            ["lambda", "sigma", "phi", "mythos", "athens"],
            ["omega", "kilos", "telos", "selene", "zeta", "sigma", "oracle", "naxos"],
        ),
        0.083333,
    ),
    (
        (
            ["omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["oracle", "naxos", "pathos", "pallas", "iota", "upsilon", "athens", "corfu", "nomos"],
        ),
        0.071429,
    ),
    (
        (
            ["rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia", "paros", "helios", "epsilon"],
        ),
        0.0625,
    ),
    (
        (
            ["sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["lydia", "paros", "helios", "epsilon", "rho", "mythos", "delos", "ethos", "hermes", "theta", "tau"],
        ),
        0.117647,
    ),
    (
        (
            ["tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            [
                "delos",
                "ethos",
                "hermes",
                "theta",
                "tau",
                "delphi",
                "rhodes",
                "logos",
                "alpha",
                "kappa",
                "phi",
                "sparta",
            ],
        ),
        0.235294,
    ),
    (
        (
            ["upsilon", "omega", "delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["rhodes", "logos", "alpha", "kappa"],
        ),
        0.076923,
    ),
    (
        (
            [
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
            ],
            ["milos", "cosmos", "gamma", "omicron", "omega"],
        ),
        0.066667,
    ),
    (
        (
            [
                "psi",
                "oracle",
                "sparta",
                "delos",
                "corfu",
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
            ],
            ["telos", "selene", "zeta", "sigma", "oracle", "naxos"],
        ),
        0.125,
    ),
    (
        (
            ["omega", "delphi", "lydia", "naxos", "milos"],
            ["pathos", "pallas", "iota", "upsilon", "athens", "corfu", "nomos"],
        ),
        0.0,
    ),
    (
        (
            ["mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["nomos", "beta", "lambda", "psi", "lydia", "paros", "helios", "epsilon"],
        ),
        0.076923,
    ),
    (
        (
            ["oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["helios", "epsilon", "rho", "mythos", "delos", "ethos", "hermes", "theta", "tau"],
        ),
        0.142857,
    ),
    (
        (
            ["delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi", "sparta"],
        ),
        0.125,
    ),
    (
        (
            ["athens", "kilos", "rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"],
            [
                "alpha",
                "kappa",
                "phi",
                "sparta",
                "milos",
                "cosmos",
                "gamma",
                "omicron",
                "omega",
                "kilos",
                "telos",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["sparta", "delos", "corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            [
                "gamma",
                "omicron",
                "omega",
                "kilos",
                "telos",
                "selene",
                "zeta",
                "sigma",
                "oracle",
                "naxos",
                "pathos",
                "pallas",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
            ],
            ["zeta", "sigma", "oracle", "naxos"],
        ),
        0.071429,
    ),
    (
        (
            [
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
                "kappa",
                "rho",
                "upsilon",
                "omega",
            ],
            ["iota", "upsilon", "athens", "corfu", "nomos"],
        ),
        0.0625,
    ),
    ((["delos", "corfu", "telos", "logos", "helios"], ["lambda", "psi", "lydia", "paros", "helios", "epsilon"]), 0.1),
    (
        (
            ["naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["rho", "mythos", "delos", "ethos", "hermes", "theta", "tau"],
        ),
        0.083333,
    ),
    (
        (
            ["rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"],
            ["tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi", "sparta"],
        ),
        0.071429,
    ),
    (
        (
            ["corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["phi", "sparta", "milos", "cosmos", "gamma", "omicron", "omega", "kilos", "telos"],
        ),
        0.133333,
    ),
    (
        (
            ["milos", "ethos", "nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"],
            ["omega", "kilos", "telos", "selene", "zeta", "sigma", "oracle", "naxos", "pathos", "pallas"],
        ),
        0.055556,
    ),
    (
        (
            ["paros", "pathos", "cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            [
                "oracle",
                "naxos",
                "pathos",
                "pallas",
                "iota",
                "upsilon",
                "athens",
                "corfu",
                "nomos",
                "beta",
                "lambda",
            ],
        ),
        0.166667,
    ),
    (
        (
            [
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
            ],
            [
                "athens",
                "corfu",
                "nomos",
                "beta",
                "lambda",
                "psi",
                "lydia",
                "paros",
                "helios",
                "epsilon",
                "rho",
                "mythos",
            ],
        ),
        0.210526,
    ),
    (
        (
            [
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
                "psi",
                "oracle",
                "sparta",
                "delos",
            ],
            ["lydia", "paros", "helios", "epsilon"],
        ),
        0.066667,
    ),
    ((["pathos", "cosmos", "hermes", "beta", "zeta"], ["delos", "ethos", "hermes", "theta", "tau"]), 0.111111),
    (
        (
            ["logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["rhodes", "logos", "alpha", "kappa", "phi", "sparta"],
        ),
        0.090909,
    ),
    (
        (
            ["nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"],
            ["milos", "cosmos", "gamma", "omicron", "omega", "kilos", "telos"],
        ),
        0.076923,
    ),
    (
        (
            ["cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["telos", "selene", "zeta", "sigma", "oracle", "naxos", "pathos", "pallas"],
        ),
        0.066667,
    ),
    (
        (
            ["helios", "pallas", "gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            ["pathos", "pallas", "iota", "upsilon", "athens", "corfu", "nomos", "beta", "lambda"],
        ),
        0.2,
    ),
    (
        (
            ["selene", "alpha", "epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["nomos", "beta", "lambda", "psi", "lydia", "paros", "helios", "epsilon", "rho", "mythos"],
        ),
        0.111111,
    ),
    (
        (
            ["hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            [
                "helios",
                "epsilon",
                "rho",
                "mythos",
                "delos",
                "ethos",
                "hermes",
                "theta",
                "tau",
                "delphi",
                "rhodes",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
            ],
            [
                "hermes",
                "theta",
                "tau",
                "delphi",
                "rhodes",
                "logos",
                "alpha",
                "kappa",
                "phi",
                "sparta",
                "milos",
                "cosmos",
            ],
        ),
        0.142857,
    ),
    ((["alpha", "epsilon", "iota", "omicron", "tau"], ["alpha", "kappa", "phi", "sparta"]), 0.125),
    ((["beta", "zeta", "kappa", "rho", "upsilon", "omega"], ["gamma", "omicron", "omega", "kilos", "telos"]), 0.1),
    (
        (
            ["gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            ["zeta", "sigma", "oracle", "naxos", "pathos", "pallas"],
        ),
        0.083333,
    ),
    (
        (
            ["epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["iota", "upsilon", "athens", "corfu", "nomos", "beta", "lambda"],
        ),
        0.071429,
    ),
    (
        (
            ["zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["lambda", "psi", "lydia", "paros", "helios", "epsilon", "rho", "mythos"],
        ),
        0.133333,
    ),
    (
        (
            ["theta", "lambda", "sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["rho", "mythos", "delos", "ethos", "hermes", "theta", "tau", "delphi", "rhodes"],
        ),
        0.1875,
    ),
    (
        (
            ["iota", "omicron", "tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi", "sparta", "milos", "cosmos"],
        ),
        0.166667,
    ),
    (
        (
            [
                "kappa",
                "rho",
                "upsilon",
                "omega",
                "delphi",
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
            ],
            [
                "phi",
                "sparta",
                "milos",
                "cosmos",
                "gamma",
                "omicron",
                "omega",
                "kilos",
                "telos",
                "selene",
                "zeta",
            ],
        ),
        0.15,
    ),
    (
        (
            ["lambda", "sigma", "phi", "mythos", "athens"],
            [
                "omega",
                "kilos",
                "telos",
                "selene",
                "zeta",
                "sigma",
                "oracle",
                "naxos",
                "pathos",
                "pallas",
                "iota",
                "upsilon",
            ],
        ),
        0.0625,
    ),
    ((["omicron", "tau", "psi", "oracle", "sparta", "delos"], ["oracle", "naxos", "pathos", "pallas"]), 0.111111),
    (
        (
            ["rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["athens", "corfu", "nomos", "beta", "lambda"],
        ),
        0.0,
    ),
    (
        (
            ["sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["lydia", "paros", "helios", "epsilon", "rho", "mythos"],
        ),
        0.166667,
    ),
    (
        (
            ["tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["delos", "ethos", "hermes", "theta", "tau", "delphi", "rhodes"],
        ),
        0.142857,
    ),
    (
        (
            ["upsilon", "omega", "delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["rhodes", "logos", "alpha", "kappa", "phi", "sparta", "milos", "cosmos"],
        ),
        0.125,
    ),
    (
        (
            [
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
            ],
            ["milos", "cosmos", "gamma", "omicron", "omega", "kilos", "telos", "selene", "zeta"],
        ),
        0.176471,
    ),
    (
        (
            [
                "psi",
                "oracle",
                "sparta",
                "delos",
                "corfu",
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
            ],
            ["telos", "selene", "zeta", "sigma", "oracle", "naxos", "pathos", "pallas", "iota", "upsilon"],
        ),
        0.157895,
    ),
    (
        (
            ["omega", "delphi", "lydia", "naxos", "milos"],
            [
                "pathos",
                "pallas",
                "iota",
                "upsilon",
                "athens",
                "corfu",
                "nomos",
                "beta",
                "lambda",
                "psi",
                "lydia",
            ],
        ),
        0.066667,
    ),
    (
        (
            ["mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            [
                "nomos",
                "beta",
                "lambda",
                "psi",
                "lydia",
                "paros",
                "helios",
                "epsilon",
                "rho",
                "mythos",
                "delos",
                "ethos",
            ],
        ),
        0.125,
    ),
    ((["oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"], ["helios", "epsilon", "rho", "mythos"]), 0.1),
    (
        (
            ["delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["hermes", "theta", "tau", "delphi", "rhodes"],
        ),
        0.083333,
    ),
    (
        (
            ["athens", "kilos", "rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"],
            ["alpha", "kappa", "phi", "sparta", "milos", "cosmos"],
        ),
        0.071429,
    ),
    (
        (
            ["sparta", "delos", "corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["gamma", "omicron", "omega", "kilos", "telos", "selene", "zeta"],
        ),
        0.133333,
    ),
    (
        (
            [
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
            ],
            ["zeta", "sigma", "oracle", "naxos", "pathos", "pallas", "iota", "upsilon"],
        ),
        0.117647,
    ),
    (
        (
            [
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
                "kappa",
                "rho",
                "upsilon",
                "omega",
            ],
            ["iota", "upsilon", "athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia"],
        ),
        0.105263,
    ),
    (
        (
            ["delos", "corfu", "telos", "logos", "helios"],
            ["lambda", "psi", "lydia", "paros", "helios", "epsilon", "rho", "mythos", "delos", "ethos"],
        ),
        0.153846,
    ),
    (
        (
            ["naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["rho", "mythos", "delos", "ethos", "hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha"],
        ),
        0.133333,
    ),
    (
        (
            ["rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"],
            [
                "tau",
                "delphi",
                "rhodes",
                "logos",
                "alpha",
                "kappa",
                "phi",
                "sparta",
                "milos",
                "cosmos",
                "gamma",
                "omicron",
            ],
        ),
        0.117647,
    ),
    (
        (
            ["corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["phi", "sparta", "milos", "cosmos"],
        ),
        0.0,
    ),
    (
        (
            ["milos", "ethos", "nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"],
            ["omega", "kilos", "telos", "selene", "zeta"],
        ),
        0.076923,
    ),
    (
        (
            ["paros", "pathos", "cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["oracle", "naxos", "pathos", "pallas", "iota", "upsilon"],
        ),
        0.142857,
    ),
    (
        (
            [
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
            ],
            ["athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia"],
        ),
        0.125,
    ),
    (
        (
            [
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
                "psi",
                "oracle",
                "sparta",
                "delos",
            ],
            ["lydia", "paros", "helios", "epsilon", "rho", "mythos", "delos", "ethos"],
        ),
        0.176471,
    ),
    (
        (
            ["pathos", "cosmos", "hermes", "beta", "zeta"],
            ["delos", "ethos", "hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha"],
        ),
        0.076923,
    ),
    (
        (
            ["logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["rhodes", "logos", "alpha", "kappa", "phi", "sparta", "milos", "cosmos", "gamma", "omicron"],
        ),
        0.142857,
    ),
    (
        (
            ["nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"],
            [
                "milos",
                "cosmos",
                "gamma",
                "omicron",
                "omega",
                "kilos",
                "telos",
                "selene",
                "zeta",
                "sigma",
                "oracle",
            ],
        ),
        0.125,
    ),
    (
        (
            ["cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            [
                "telos",
                "selene",
                "zeta",
                "sigma",
                "oracle",
                "naxos",
                "pathos",
                "pallas",
                "iota",
                "upsilon",
                "athens",
                "corfu",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["helios", "pallas", "gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            ["pathos", "pallas", "iota", "upsilon"],
        ),
        0.083333,
    ),
    (
        (
            ["selene", "alpha", "epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["nomos", "beta", "lambda", "psi", "lydia"],
        ),
        0.071429,
    ),
    (
        (
            ["hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["helios", "epsilon", "rho", "mythos", "delos", "ethos"],
        ),
        0.0625,
    ),
    (
        (
            [
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
            ],
            ["hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha"],
        ),
        0.117647,
    ),
    (
        (
            ["alpha", "epsilon", "iota", "omicron", "tau"],
            ["alpha", "kappa", "phi", "sparta", "milos", "cosmos", "gamma", "omicron"],
        ),
        0.181818,
    ),
    (
        (
            ["beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["gamma", "omicron", "omega", "kilos", "telos", "selene", "zeta", "sigma", "oracle"],
        ),
        0.153846,
    ),
    (
        (
            ["gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            ["zeta", "sigma", "oracle", "naxos", "pathos", "pallas", "iota", "upsilon", "athens", "corfu"],
        ),
        0.133333,
    ),
    (
        (
            ["epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["iota", "upsilon", "athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia", "paros", "helios"],
        ),
        0.117647,
    ),
    (
        (
            ["zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            [
                "lambda",
                "psi",
                "lydia",
                "paros",
                "helios",
                "epsilon",
                "rho",
                "mythos",
                "delos",
                "ethos",
                "hermes",
                "theta",
            ],
        ),
        0.105263,
    ),
    (
        (
            ["theta", "lambda", "sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["rho", "mythos", "delos", "ethos"],
        ),
        0.076923,
    ),
    (
        (
            ["iota", "omicron", "tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["tau", "delphi", "rhodes", "logos", "alpha"],
        ),
        0.142857,
    ),
    (
        (
            [
                "kappa",
                "rho",
                "upsilon",
                "omega",
                "delphi",
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
            ],
            ["phi", "sparta", "milos", "cosmos", "gamma", "omicron"],
        ),
        0.058824,
    ),
    (
        (
            ["lambda", "sigma", "phi", "mythos", "athens"],
            ["omega", "kilos", "telos", "selene", "zeta", "sigma", "oracle"],
        ),
        0.090909,
    ),
    (
        (
            ["omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["oracle", "naxos", "pathos", "pallas", "iota", "upsilon", "athens", "corfu"],
        ),
        0.076923,
    ),
    (
        (
            ["rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia", "paros", "helios"],
        ),
        0.066667,
    ),
    (
        (
            ["sigma", "phi", "mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["lydia", "paros", "helios", "epsilon", "rho", "mythos", "delos", "ethos", "hermes", "theta"],
        ),
        0.125,
    ),
    (
        (
            ["tau", "psi", "oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["delos", "ethos", "hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi"],
        ),
        0.176471,
    ),
    (
        (
            ["upsilon", "omega", "delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            [
                "rhodes",
                "logos",
                "alpha",
                "kappa",
                "phi",
                "sparta",
                "milos",
                "cosmos",
                "gamma",
                "omicron",
                "omega",
                "kilos",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
            ],
            ["milos", "cosmos", "gamma", "omicron"],
        ),
        0.071429,
    ),
    (
        (
            [
                "psi",
                "oracle",
                "sparta",
                "delos",
                "corfu",
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
            ],
            ["telos", "selene", "zeta", "sigma", "oracle"],
        ),
        0.133333,
    ),
    ((["omega", "delphi", "lydia", "naxos", "milos"], ["pathos", "pallas", "iota", "upsilon", "athens", "corfu"]), 0.0),
    (
        (
            ["mythos", "athens", "kilos", "rhodes", "paros", "pathos"],
            ["nomos", "beta", "lambda", "psi", "lydia", "paros", "helios"],
        ),
        0.083333,
    ),
    (
        (
            ["oracle", "sparta", "delos", "corfu", "telos", "logos", "helios"],
            ["helios", "epsilon", "rho", "mythos", "delos", "ethos", "hermes", "theta"],
        ),
        0.153846,
    ),
    (
        (
            ["delphi", "lydia", "naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi"],
        ),
        0.133333,
    ),
    (
        (
            ["athens", "kilos", "rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"],
            ["alpha", "kappa", "phi", "sparta", "milos", "cosmos", "gamma", "omicron", "omega", "kilos"],
        ),
        0.117647,
    ),
    (
        (
            ["sparta", "delos", "corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            [
                "gamma",
                "omicron",
                "omega",
                "kilos",
                "telos",
                "selene",
                "zeta",
                "sigma",
                "oracle",
                "naxos",
                "pathos",
            ],
        ),
        0.105263,
    ),
    (
        (
            [
                "lydia",
                "naxos",
                "milos",
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
            ],
            [
                "zeta",
                "sigma",
                "oracle",
                "naxos",
                "pathos",
                "pallas",
                "iota",
                "upsilon",
                "athens",
                "corfu",
                "nomos",
                "beta",
            ],
        ),
        0.15,
    ),
    (
        (
            [
                "kilos",
                "rhodes",
                "paros",
                "pathos",
                "cosmos",
                "hermes",
                "beta",
                "zeta",
                "kappa",
                "rho",
                "upsilon",
                "omega",
            ],
            ["iota", "upsilon", "athens", "corfu"],
        ),
        0.066667,
    ),
    ((["delos", "corfu", "telos", "logos", "helios"], ["lambda", "psi", "lydia", "paros", "helios"]), 0.111111),
    (
        (
            ["naxos", "milos", "ethos", "nomos", "selene", "alpha"],
            ["rho", "mythos", "delos", "ethos", "hermes", "theta"],
        ),
        0.090909,
    ),
    (
        (
            ["rhodes", "paros", "pathos", "cosmos", "hermes", "beta", "zeta"],
            ["tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi"],
        ),
        0.076923,
    ),
    (
        (
            ["corfu", "telos", "logos", "helios", "pallas", "gamma", "theta", "lambda"],
            ["phi", "sparta", "milos", "cosmos", "gamma", "omicron", "omega", "kilos"],
        ),
        0.066667,
    ),
    (
        (
            ["milos", "ethos", "nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"],
            ["omega", "kilos", "telos", "selene", "zeta", "sigma", "oracle", "naxos", "pathos"],
        ),
        0.058824,
    ),
    (
        (
            ["paros", "pathos", "cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["oracle", "naxos", "pathos", "pallas", "iota", "upsilon", "athens", "corfu", "nomos", "beta"],
        ),
        0.176471,
    ),
    (
        (
            [
                "telos",
                "logos",
                "helios",
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
            ],
            ["athens", "corfu", "nomos", "beta", "lambda", "psi", "lydia", "paros", "helios", "epsilon", "rho"],
        ),
        0.157895,
    ),
    (
        (
            [
                "ethos",
                "nomos",
                "selene",
                "alpha",
                "epsilon",
                "iota",
                "omicron",
                "tau",
                "psi",
                "oracle",
                "sparta",
                "delos",
            ],
            [
                "lydia",
                "paros",
                "helios",
                "epsilon",
                "rho",
                "mythos",
                "delos",
                "ethos",
                "hermes",
                "theta",
                "tau",
                "delphi",
            ],
        ),
        0.2,
    ),
    ((["pathos", "cosmos", "hermes", "beta", "zeta"], ["delos", "ethos", "hermes", "theta"]), 0.125),
    ((["logos", "helios", "pallas", "gamma", "theta", "lambda"], ["rhodes", "logos", "alpha", "kappa", "phi"]), 0.1),
    (
        (
            ["nomos", "selene", "alpha", "epsilon", "iota", "omicron", "tau"],
            ["milos", "cosmos", "gamma", "omicron", "omega", "kilos"],
        ),
        0.083333,
    ),
    (
        (
            ["cosmos", "hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega"],
            ["telos", "selene", "zeta", "sigma", "oracle", "naxos", "pathos"],
        ),
        0.071429,
    ),
    (
        (
            ["helios", "pallas", "gamma", "theta", "lambda", "sigma", "phi", "mythos", "athens"],
            ["pathos", "pallas", "iota", "upsilon", "athens", "corfu", "nomos", "beta"],
        ),
        0.133333,
    ),
    (
        (
            ["selene", "alpha", "epsilon", "iota", "omicron", "tau", "psi", "oracle", "sparta", "delos"],
            ["nomos", "beta", "lambda", "psi", "lydia", "paros", "helios", "epsilon", "rho"],
        ),
        0.117647,
    ),
    (
        (
            ["hermes", "beta", "zeta", "kappa", "rho", "upsilon", "omega", "delphi", "lydia", "naxos", "milos"],
            ["helios", "epsilon", "rho", "mythos", "delos", "ethos", "hermes", "theta", "tau", "delphi"],
        ),
        0.166667,
    ),
    (
        (
            [
                "pallas",
                "gamma",
                "theta",
                "lambda",
                "sigma",
                "phi",
                "mythos",
                "athens",
                "kilos",
                "rhodes",
                "paros",
                "pathos",
            ],
            ["hermes", "theta", "tau", "delphi", "rhodes", "logos", "alpha", "kappa", "phi", "sparta", "milos"],
        ),
        0.15,
    ),
]

_EXPECTED_COUNT = 240

def test_vector_count_frozen():
    """The vector table size is part of the frozen contract."""
    assert len(_CASES) == _EXPECTED_COUNT

def test_vectors_000():
    """Known-answer vectors 0..119."""
    for case, expected in _CASES[0:120]:
        assert _ref_jaccard(case) == expected

def test_vectors_120():
    """Known-answer vectors 120..239."""
    for case, expected in _CASES[120:240]:
        assert _ref_jaccard(case) == expected

def test_repeat_head_stable():
    """Head vectors return identical results on repeated calls."""
    for case, expected in _CASES[:64]:
        assert _ref_jaccard(case) == expected
        assert _ref_jaccard(case) == expected

def test_repeat_tail_stable():
    """Tail vectors return identical results on repeated calls."""
    for case, expected in _CASES[-64:]:
        assert _ref_jaccard(case) == expected
        assert _ref_jaccard(case) == expected
