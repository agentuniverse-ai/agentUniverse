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
    ((["comet", "breeze", "humid", "pulsar", "nebula"], ["comet", "aurora", "corona", "rain", "moon", "delta"]), 0.1),
    (
        (
            ["storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["clouds", "pulsar", "stellar", "wind", "galaxy", "mirage", "frost"],
        ),
        0.181818,
    ),
    (
        (
            ["clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            ["frost", "meteor", "venus", "fog", "lunar", "shower", "humid", "plasma"],
        ),
        0.071429,
    ),
    (
        (
            ["breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["humid", "plasma", "tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow"],
        ),
        0.133333,
    ),
    (
        (
            ["frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["zenith", "cosmic", "snow", "star", "oasis", "breeze", "quasar", "gravity", "mist", "orbit"],
        ),
        0.117647,
    ),
    (
        (
            ["hail", "zenith", "meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            ["quasar", "gravity", "mist", "orbit", "vapor", "hail", "nebula", "mars", "dew", "solar", "comet"],
        ),
        0.166667,
    ),
    (
        (
            ["humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            [
                "nebula",
                "mars",
                "dew",
                "solar",
                "comet",
                "aurora",
                "corona",
                "rain",
                "moon",
                "delta",
                "clouds",
                "pulsar",
            ],
        ),
        0.210526,
    ),
    (
        (
            [
                "aurora",
                "quasar",
                "plasma",
                "stellar",
                "mars",
                "snow",
                "fog",
                "moon",
                "orbit",
                "arctic",
                "mirage",
                "comet",
            ],
            ["corona", "rain", "moon", "delta"],
        ),
        0.066667,
    ),
    ((["zenith", "meteor", "corona", "gravity", "tide"], ["stellar", "wind", "galaxy", "mirage", "frost"]), 0.0),
    (
        (
            ["pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["venus", "fog", "lunar", "shower", "humid", "plasma"],
        ),
        0.090909,
    ),
    (
        (
            ["quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow"],
        ),
        0.076923,
    ),
    (
        (
            ["meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            ["snow", "star", "oasis", "breeze", "quasar", "gravity", "mist", "orbit"],
        ),
        0.142857,
    ),
    (
        (
            ["nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["mist", "orbit", "vapor", "hail", "nebula", "mars", "dew", "solar", "comet"],
        ),
        0.2,
    ),
    (
        (
            ["plasma", "stellar", "mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["dew", "solar", "comet", "aurora", "corona", "rain", "moon", "delta", "clouds", "pulsar"],
        ),
        0.111111,
    ),
    (
        (
            ["corona", "gravity", "tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            [
                "moon",
                "delta",
                "clouds",
                "pulsar",
                "stellar",
                "wind",
                "galaxy",
                "mirage",
                "frost",
                "meteor",
                "venus",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "cosmic",
                "venus",
                "rain",
                "mist",
                "sun",
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
            ],
            [
                "galaxy",
                "mirage",
                "frost",
                "meteor",
                "venus",
                "fog",
                "lunar",
                "shower",
                "humid",
                "plasma",
                "tide",
                "sun",
            ],
        ),
        0.2,
    ),
    ((["stellar", "mars", "snow", "fog", "moon"], ["lunar", "shower", "humid", "plasma"]), 0.0),
    ((["gravity", "tide", "wind", "dew", "star", "lunar"], ["arctic", "storm", "zenith", "cosmic", "snow"]), 0.0),
    (
        (
            ["venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["oasis", "breeze", "quasar", "gravity", "mist", "orbit"],
        ),
        0.181818,
    ),
    (
        (
            ["mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["vapor", "hail", "nebula", "mars", "dew", "solar", "comet"],
        ),
        0.153846,
    ),
    (
        (
            ["tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["comet", "aurora", "corona", "rain", "moon", "delta", "clouds", "pulsar"],
        ),
        0.0625,
    ),
    (
        (
            ["rain", "mist", "sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["clouds", "pulsar", "stellar", "wind", "galaxy", "mirage", "frost", "meteor", "venus"],
        ),
        0.117647,
    ),
    (
        (
            ["snow", "fog", "moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["frost", "meteor", "venus", "fog", "lunar", "shower", "humid", "plasma", "tide", "sun"],
        ),
        0.105263,
    ),
    (
        (
            [
                "wind",
                "dew",
                "star",
                "lunar",
                "delta",
                "vapor",
                "storm",
                "frost",
                "aurora",
                "quasar",
                "plasma",
                "stellar",
            ],
            ["humid", "plasma", "tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis"],
        ),
        0.15,
    ),
    (
        (
            ["mist", "sun", "galaxy", "solar", "oasis"],
            [
                "zenith",
                "cosmic",
                "snow",
                "star",
                "oasis",
                "breeze",
                "quasar",
                "gravity",
                "mist",
                "orbit",
                "vapor",
                "hail",
            ],
        ),
        0.133333,
    ),
    ((["fog", "moon", "orbit", "arctic", "mirage", "comet"], ["quasar", "gravity", "mist", "orbit"]), 0.111111),
    (
        (
            ["dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["nebula", "mars", "dew", "solar", "comet"],
        ),
        0.090909,
    ),
    (
        (
            ["sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["corona", "rain", "moon", "delta", "clouds", "pulsar"],
        ),
        0.076923,
    ),
    (
        (
            ["moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["stellar", "wind", "galaxy", "mirage", "frost", "meteor", "venus"],
        ),
        0.066667,
    ),
    (
        (
            ["star", "lunar", "delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["venus", "fog", "lunar", "shower", "humid", "plasma", "tide", "sun"],
        ),
        0.125,
    ),
    (
        (
            [
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
            ],
            ["tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis"],
        ),
        0.176471,
    ),
    (
        (
            [
                "orbit",
                "arctic",
                "mirage",
                "comet",
                "breeze",
                "humid",
                "pulsar",
                "nebula",
                "cosmic",
                "venus",
                "rain",
                "mist",
            ],
            ["snow", "star", "oasis", "breeze", "quasar", "gravity", "mist", "orbit", "vapor", "hail"],
        ),
        0.157895,
    ),
    (
        (
            ["lunar", "delta", "vapor", "storm", "frost"],
            ["mist", "orbit", "vapor", "hail", "nebula", "mars", "dew", "solar", "comet", "aurora", "corona"],
        ),
        0.066667,
    ),
    (
        (
            ["solar", "oasis", "shower", "clouds", "hail", "zenith"],
            [
                "dew",
                "solar",
                "comet",
                "aurora",
                "corona",
                "rain",
                "moon",
                "delta",
                "clouds",
                "pulsar",
                "stellar",
                "wind",
            ],
        ),
        0.125,
    ),
    (
        (
            ["arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["moon", "delta", "clouds", "pulsar"],
        ),
        0.1,
    ),
    (
        (
            ["delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["galaxy", "mirage", "frost", "meteor", "venus"],
        ),
        0.083333,
    ),
    (
        (
            ["oasis", "shower", "clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            ["lunar", "shower", "humid", "plasma", "tide", "sun"],
        ),
        0.153846,
    ),
    (
        (
            ["mirage", "comet", "breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis"],
        ),
        0.0625,
    ),
    (
        (
            ["vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["oasis", "breeze", "quasar", "gravity", "mist", "orbit", "vapor", "hail"],
        ),
        0.117647,
    ),
    (
        (
            [
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
                "wind",
                "dew",
                "star",
                "lunar",
            ],
            ["vapor", "hail", "nebula", "mars", "dew", "solar", "comet", "aurora", "corona"],
        ),
        0.166667,
    ),
    (
        (
            ["comet", "breeze", "humid", "pulsar", "nebula"],
            ["comet", "aurora", "corona", "rain", "moon", "delta", "clouds", "pulsar", "stellar", "wind"],
        ),
        0.153846,
    ),
    (
        (
            ["storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            [
                "clouds",
                "pulsar",
                "stellar",
                "wind",
                "galaxy",
                "mirage",
                "frost",
                "meteor",
                "venus",
                "fog",
                "lunar",
            ],
        ),
        0.133333,
    ),
    (
        (
            ["clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            [
                "frost",
                "meteor",
                "venus",
                "fog",
                "lunar",
                "shower",
                "humid",
                "plasma",
                "tide",
                "sun",
                "arctic",
                "storm",
            ],
        ),
        0.117647,
    ),
    (
        (
            ["breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["humid", "plasma", "tide", "sun"],
        ),
        0.090909,
    ),
    (
        (
            ["frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["zenith", "cosmic", "snow", "star", "oasis"],
        ),
        0.076923,
    ),
    (
        (
            ["hail", "zenith", "meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            ["quasar", "gravity", "mist", "orbit", "vapor", "hail"],
        ),
        0.142857,
    ),
    (
        (
            ["humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["nebula", "mars", "dew", "solar", "comet", "aurora", "corona"],
        ),
        0.125,
    ),
    (
        (
            [
                "aurora",
                "quasar",
                "plasma",
                "stellar",
                "mars",
                "snow",
                "fog",
                "moon",
                "orbit",
                "arctic",
                "mirage",
                "comet",
            ],
            ["corona", "rain", "moon", "delta", "clouds", "pulsar", "stellar", "wind"],
        ),
        0.111111,
    ),
    (
        (
            ["zenith", "meteor", "corona", "gravity", "tide"],
            ["stellar", "wind", "galaxy", "mirage", "frost", "meteor", "venus", "fog", "lunar"],
        ),
        0.076923,
    ),
    (
        (
            ["pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["venus", "fog", "lunar", "shower", "humid", "plasma", "tide", "sun", "arctic", "storm"],
        ),
        0.066667,
    ),
    (
        (
            ["quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis", "breeze", "quasar"],
        ),
        0.125,
    ),
    (
        (
            ["meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            [
                "snow",
                "star",
                "oasis",
                "breeze",
                "quasar",
                "gravity",
                "mist",
                "orbit",
                "vapor",
                "hail",
                "nebula",
                "mars",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["mist", "orbit", "vapor", "hail"],
        ),
        0.083333,
    ),
    (
        (
            ["plasma", "stellar", "mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["dew", "solar", "comet", "aurora", "corona"],
        ),
        0.071429,
    ),
    (
        (
            ["corona", "gravity", "tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["moon", "delta", "clouds", "pulsar", "stellar", "wind"],
        ),
        0.133333,
    ),
    (
        (
            [
                "cosmic",
                "venus",
                "rain",
                "mist",
                "sun",
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
            ],
            ["galaxy", "mirage", "frost", "meteor", "venus", "fog", "lunar"],
        ),
        0.117647,
    ),
    (
        (
            ["stellar", "mars", "snow", "fog", "moon"],
            ["lunar", "shower", "humid", "plasma", "tide", "sun", "arctic", "storm"],
        ),
        0.0,
    ),
    (
        (
            ["gravity", "tide", "wind", "dew", "star", "lunar"],
            ["arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis", "breeze", "quasar"],
        ),
        0.071429,
    ),
    (
        (
            ["venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["oasis", "breeze", "quasar", "gravity", "mist", "orbit", "vapor", "hail", "nebula", "mars"],
        ),
        0.133333,
    ),
    (
        (
            ["mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["vapor", "hail", "nebula", "mars", "dew", "solar", "comet", "aurora", "corona", "rain", "moon"],
        ),
        0.1875,
    ),
    (
        (
            ["tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            [
                "comet",
                "aurora",
                "corona",
                "rain",
                "moon",
                "delta",
                "clouds",
                "pulsar",
                "stellar",
                "wind",
                "galaxy",
                "mirage",
            ],
        ),
        0.105263,
    ),
    (
        (
            ["rain", "mist", "sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["clouds", "pulsar", "stellar", "wind"],
        ),
        0.076923,
    ),
    (
        (
            ["snow", "fog", "moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["frost", "meteor", "venus", "fog", "lunar"],
        ),
        0.066667,
    ),
    (
        (
            [
                "wind",
                "dew",
                "star",
                "lunar",
                "delta",
                "vapor",
                "storm",
                "frost",
                "aurora",
                "quasar",
                "plasma",
                "stellar",
            ],
            ["humid", "plasma", "tide", "sun", "arctic", "storm"],
        ),
        0.125,
    ),
    (
        (
            ["mist", "sun", "galaxy", "solar", "oasis"],
            ["zenith", "cosmic", "snow", "star", "oasis", "breeze", "quasar"],
        ),
        0.090909,
    ),
    (
        (
            ["fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["quasar", "gravity", "mist", "orbit", "vapor", "hail", "nebula", "mars"],
        ),
        0.076923,
    ),
    (
        (
            ["dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["nebula", "mars", "dew", "solar", "comet", "aurora", "corona", "rain", "moon"],
        ),
        0.066667,
    ),
    (
        (
            ["sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["corona", "rain", "moon", "delta", "clouds", "pulsar", "stellar", "wind", "galaxy", "mirage"],
        ),
        0.125,
    ),
    (
        (
            ["moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            [
                "stellar",
                "wind",
                "galaxy",
                "mirage",
                "frost",
                "meteor",
                "venus",
                "fog",
                "lunar",
                "shower",
                "humid",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["star", "lunar", "delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            [
                "venus",
                "fog",
                "lunar",
                "shower",
                "humid",
                "plasma",
                "tide",
                "sun",
                "arctic",
                "storm",
                "zenith",
                "cosmic",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
            ],
            ["tide", "sun", "arctic", "storm"],
        ),
        0.071429,
    ),
    (
        (
            [
                "orbit",
                "arctic",
                "mirage",
                "comet",
                "breeze",
                "humid",
                "pulsar",
                "nebula",
                "cosmic",
                "venus",
                "rain",
                "mist",
            ],
            ["snow", "star", "oasis", "breeze", "quasar"],
        ),
        0.0625,
    ),
    ((["lunar", "delta", "vapor", "storm", "frost"], ["mist", "orbit", "vapor", "hail", "nebula", "mars"]), 0.1),
    (
        (
            ["solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["dew", "solar", "comet", "aurora", "corona", "rain", "moon"],
        ),
        0.083333,
    ),
    (
        (
            ["arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["moon", "delta", "clouds", "pulsar", "stellar", "wind", "galaxy", "mirage"],
        ),
        0.153846,
    ),
    (
        (
            ["delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["galaxy", "mirage", "frost", "meteor", "venus", "fog", "lunar", "shower", "humid"],
        ),
        0.0625,
    ),
    (
        (
            ["oasis", "shower", "clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            ["lunar", "shower", "humid", "plasma", "tide", "sun", "arctic", "storm", "zenith", "cosmic"],
        ),
        0.1875,
    ),
    (
        (
            ["mirage", "comet", "breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            [
                "arctic",
                "storm",
                "zenith",
                "cosmic",
                "snow",
                "star",
                "oasis",
                "breeze",
                "quasar",
                "gravity",
                "mist",
            ],
        ),
        0.166667,
    ),
    (
        (
            ["vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            [
                "oasis",
                "breeze",
                "quasar",
                "gravity",
                "mist",
                "orbit",
                "vapor",
                "hail",
                "nebula",
                "mars",
                "dew",
                "solar",
            ],
        ),
        0.15,
    ),
    (
        (
            [
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
                "wind",
                "dew",
                "star",
                "lunar",
            ],
            ["vapor", "hail", "nebula", "mars"],
        ),
        0.066667,
    ),
    ((["comet", "breeze", "humid", "pulsar", "nebula"], ["comet", "aurora", "corona", "rain", "moon"]), 0.111111),
    (
        (
            ["storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["clouds", "pulsar", "stellar", "wind", "galaxy", "mirage"],
        ),
        0.090909,
    ),
    (
        (
            ["clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            ["frost", "meteor", "venus", "fog", "lunar", "shower", "humid"],
        ),
        0.076923,
    ),
    (
        (
            ["breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["humid", "plasma", "tide", "sun", "arctic", "storm", "zenith", "cosmic"],
        ),
        0.142857,
    ),
    (
        (
            ["frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["zenith", "cosmic", "snow", "star", "oasis", "breeze", "quasar", "gravity", "mist"],
        ),
        0.125,
    ),
    (
        (
            ["hail", "zenith", "meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            ["quasar", "gravity", "mist", "orbit", "vapor", "hail", "nebula", "mars", "dew", "solar"],
        ),
        0.176471,
    ),
    (
        (
            ["humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["nebula", "mars", "dew", "solar", "comet", "aurora", "corona", "rain", "moon", "delta", "clouds"],
        ),
        0.157895,
    ),
    (
        (
            [
                "aurora",
                "quasar",
                "plasma",
                "stellar",
                "mars",
                "snow",
                "fog",
                "moon",
                "orbit",
                "arctic",
                "mirage",
                "comet",
            ],
            [
                "corona",
                "rain",
                "moon",
                "delta",
                "clouds",
                "pulsar",
                "stellar",
                "wind",
                "galaxy",
                "mirage",
                "frost",
                "meteor",
            ],
        ),
        0.142857,
    ),
    ((["zenith", "meteor", "corona", "gravity", "tide"], ["stellar", "wind", "galaxy", "mirage"]), 0.0),
    ((["pulsar", "nebula", "cosmic", "venus", "rain", "mist"], ["venus", "fog", "lunar", "shower", "humid"]), 0.1),
    (
        (
            ["quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["tide", "sun", "arctic", "storm", "zenith", "cosmic"],
        ),
        0.0,
    ),
    (
        (
            ["meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            ["snow", "star", "oasis", "breeze", "quasar", "gravity", "mist"],
        ),
        0.153846,
    ),
    (
        (
            ["nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["mist", "orbit", "vapor", "hail", "nebula", "mars", "dew", "solar"],
        ),
        0.214286,
    ),
    (
        (
            ["plasma", "stellar", "mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["dew", "solar", "comet", "aurora", "corona", "rain", "moon", "delta", "clouds"],
        ),
        0.117647,
    ),
    (
        (
            ["corona", "gravity", "tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["moon", "delta", "clouds", "pulsar", "stellar", "wind", "galaxy", "mirage", "frost", "meteor"],
        ),
        0.166667,
    ),
    (
        (
            [
                "cosmic",
                "venus",
                "rain",
                "mist",
                "sun",
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
            ],
            [
                "galaxy",
                "mirage",
                "frost",
                "meteor",
                "venus",
                "fog",
                "lunar",
                "shower",
                "humid",
                "plasma",
                "tide",
            ],
        ),
        0.15,
    ),
    (
        (
            ["stellar", "mars", "snow", "fog", "moon"],
            [
                "lunar",
                "shower",
                "humid",
                "plasma",
                "tide",
                "sun",
                "arctic",
                "storm",
                "zenith",
                "cosmic",
                "snow",
                "star",
            ],
        ),
        0.0625,
    ),
    ((["gravity", "tide", "wind", "dew", "star", "lunar"], ["arctic", "storm", "zenith", "cosmic"]), 0.0),
    (
        (
            ["venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["oasis", "breeze", "quasar", "gravity", "mist"],
        ),
        0.2,
    ),
    (
        (
            ["mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["vapor", "hail", "nebula", "mars", "dew", "solar"],
        ),
        0.076923,
    ),
    (
        (
            ["tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["comet", "aurora", "corona", "rain", "moon", "delta", "clouds"],
        ),
        0.066667,
    ),
    (
        (
            ["rain", "mist", "sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["clouds", "pulsar", "stellar", "wind", "galaxy", "mirage", "frost", "meteor"],
        ),
        0.125,
    ),
    (
        (
            ["snow", "fog", "moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["frost", "meteor", "venus", "fog", "lunar", "shower", "humid", "plasma", "tide"],
        ),
        0.111111,
    ),
    (
        (
            [
                "wind",
                "dew",
                "star",
                "lunar",
                "delta",
                "vapor",
                "storm",
                "frost",
                "aurora",
                "quasar",
                "plasma",
                "stellar",
            ],
            ["humid", "plasma", "tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow", "star"],
        ),
        0.157895,
    ),
    (
        (
            ["mist", "sun", "galaxy", "solar", "oasis"],
            [
                "zenith",
                "cosmic",
                "snow",
                "star",
                "oasis",
                "breeze",
                "quasar",
                "gravity",
                "mist",
                "orbit",
                "vapor",
            ],
        ),
        0.142857,
    ),
    (
        (
            ["fog", "moon", "orbit", "arctic", "mirage", "comet"],
            [
                "quasar",
                "gravity",
                "mist",
                "orbit",
                "vapor",
                "hail",
                "nebula",
                "mars",
                "dew",
                "solar",
                "comet",
                "aurora",
            ],
        ),
        0.125,
    ),
    ((["dew", "star", "lunar", "delta", "vapor", "storm", "frost"], ["nebula", "mars", "dew", "solar"]), 0.1),
    (
        (
            ["sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["corona", "rain", "moon", "delta", "clouds"],
        ),
        0.083333,
    ),
    (
        (
            ["moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["stellar", "wind", "galaxy", "mirage", "frost", "meteor"],
        ),
        0.071429,
    ),
    (
        (
            ["star", "lunar", "delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["venus", "fog", "lunar", "shower", "humid", "plasma", "tide"],
        ),
        0.133333,
    ),
    (
        (
            [
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
            ],
            ["tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow", "star"],
        ),
        0.117647,
    ),
    (
        (
            [
                "orbit",
                "arctic",
                "mirage",
                "comet",
                "breeze",
                "humid",
                "pulsar",
                "nebula",
                "cosmic",
                "venus",
                "rain",
                "mist",
            ],
            ["snow", "star", "oasis", "breeze", "quasar", "gravity", "mist", "orbit", "vapor"],
        ),
        0.166667,
    ),
    (
        (
            ["lunar", "delta", "vapor", "storm", "frost"],
            ["mist", "orbit", "vapor", "hail", "nebula", "mars", "dew", "solar", "comet", "aurora"],
        ),
        0.071429,
    ),
    (
        (
            ["solar", "oasis", "shower", "clouds", "hail", "zenith"],
            [
                "dew",
                "solar",
                "comet",
                "aurora",
                "corona",
                "rain",
                "moon",
                "delta",
                "clouds",
                "pulsar",
                "stellar",
            ],
        ),
        0.133333,
    ),
    (
        (
            ["arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            [
                "moon",
                "delta",
                "clouds",
                "pulsar",
                "stellar",
                "wind",
                "galaxy",
                "mirage",
                "frost",
                "meteor",
                "venus",
                "fog",
            ],
        ),
        0.117647,
    ),
    (
        (
            ["delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["galaxy", "mirage", "frost", "meteor"],
        ),
        0.090909,
    ),
    (
        (
            ["oasis", "shower", "clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            ["lunar", "shower", "humid", "plasma", "tide"],
        ),
        0.166667,
    ),
    (
        (
            ["mirage", "comet", "breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["arctic", "storm", "zenith", "cosmic", "snow", "star"],
        ),
        0.066667,
    ),
    (
        (
            ["vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["oasis", "breeze", "quasar", "gravity", "mist", "orbit", "vapor"],
        ),
        0.125,
    ),
    (
        (
            [
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
                "wind",
                "dew",
                "star",
                "lunar",
            ],
            ["vapor", "hail", "nebula", "mars", "dew", "solar", "comet", "aurora"],
        ),
        0.111111,
    ),
    (
        (
            ["comet", "breeze", "humid", "pulsar", "nebula"],
            ["comet", "aurora", "corona", "rain", "moon", "delta", "clouds", "pulsar", "stellar"],
        ),
        0.166667,
    ),
    (
        (
            ["storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["clouds", "pulsar", "stellar", "wind", "galaxy", "mirage", "frost", "meteor", "venus", "fog"],
        ),
        0.142857,
    ),
    (
        (
            ["clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            ["frost", "meteor", "venus", "fog", "lunar", "shower", "humid", "plasma", "tide", "sun", "arctic"],
        ),
        0.125,
    ),
    (
        (
            ["breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            [
                "humid",
                "plasma",
                "tide",
                "sun",
                "arctic",
                "storm",
                "zenith",
                "cosmic",
                "snow",
                "star",
                "oasis",
                "breeze",
            ],
        ),
        0.176471,
    ),
    (
        (
            ["frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["zenith", "cosmic", "snow", "star"],
        ),
        0.083333,
    ),
    (
        (
            ["hail", "zenith", "meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            ["quasar", "gravity", "mist", "orbit", "vapor"],
        ),
        0.071429,
    ),
    (
        (
            ["humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["nebula", "mars", "dew", "solar", "comet", "aurora"],
        ),
        0.133333,
    ),
    (
        (
            [
                "aurora",
                "quasar",
                "plasma",
                "stellar",
                "mars",
                "snow",
                "fog",
                "moon",
                "orbit",
                "arctic",
                "mirage",
                "comet",
            ],
            ["corona", "rain", "moon", "delta", "clouds", "pulsar", "stellar"],
        ),
        0.117647,
    ),
    (
        (
            ["zenith", "meteor", "corona", "gravity", "tide"],
            ["stellar", "wind", "galaxy", "mirage", "frost", "meteor", "venus", "fog"],
        ),
        0.083333,
    ),
    (
        (
            ["pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["venus", "fog", "lunar", "shower", "humid", "plasma", "tide", "sun", "arctic"],
        ),
        0.071429,
    ),
    (
        (
            ["quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis", "breeze"],
        ),
        0.0625,
    ),
    (
        (
            ["meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            ["snow", "star", "oasis", "breeze", "quasar", "gravity", "mist", "orbit", "vapor", "hail", "nebula"],
        ),
        0.117647,
    ),
    (
        (
            ["nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            [
                "mist",
                "orbit",
                "vapor",
                "hail",
                "nebula",
                "mars",
                "dew",
                "solar",
                "comet",
                "aurora",
                "corona",
                "rain",
            ],
        ),
        0.235294,
    ),
    (
        (
            ["plasma", "stellar", "mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["dew", "solar", "comet", "aurora"],
        ),
        0.076923,
    ),
    (
        (
            ["corona", "gravity", "tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["moon", "delta", "clouds", "pulsar", "stellar"],
        ),
        0.066667,
    ),
    (
        (
            [
                "cosmic",
                "venus",
                "rain",
                "mist",
                "sun",
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
            ],
            ["galaxy", "mirage", "frost", "meteor", "venus", "fog"],
        ),
        0.125,
    ),
    (
        (
            ["stellar", "mars", "snow", "fog", "moon"],
            ["lunar", "shower", "humid", "plasma", "tide", "sun", "arctic"],
        ),
        0.0,
    ),
    (
        (
            ["gravity", "tide", "wind", "dew", "star", "lunar"],
            ["arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis", "breeze"],
        ),
        0.076923,
    ),
    (
        (
            ["venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["oasis", "breeze", "quasar", "gravity", "mist", "orbit", "vapor", "hail", "nebula"],
        ),
        0.142857,
    ),
    (
        (
            ["mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["vapor", "hail", "nebula", "mars", "dew", "solar", "comet", "aurora", "corona", "rain"],
        ),
        0.125,
    ),
    (
        (
            ["tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            [
                "comet",
                "aurora",
                "corona",
                "rain",
                "moon",
                "delta",
                "clouds",
                "pulsar",
                "stellar",
                "wind",
                "galaxy",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["rain", "mist", "sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            [
                "clouds",
                "pulsar",
                "stellar",
                "wind",
                "galaxy",
                "mirage",
                "frost",
                "meteor",
                "venus",
                "fog",
                "lunar",
                "shower",
            ],
        ),
        0.157895,
    ),
    (
        (
            ["snow", "fog", "moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["frost", "meteor", "venus", "fog"],
        ),
        0.071429,
    ),
    (
        (
            [
                "wind",
                "dew",
                "star",
                "lunar",
                "delta",
                "vapor",
                "storm",
                "frost",
                "aurora",
                "quasar",
                "plasma",
                "stellar",
            ],
            ["humid", "plasma", "tide", "sun", "arctic"],
        ),
        0.0625,
    ),
    ((["mist", "sun", "galaxy", "solar", "oasis"], ["zenith", "cosmic", "snow", "star", "oasis", "breeze"]), 0.1),
    (
        (
            ["fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["quasar", "gravity", "mist", "orbit", "vapor", "hail", "nebula"],
        ),
        0.083333,
    ),
    (
        (
            ["dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["nebula", "mars", "dew", "solar", "comet", "aurora", "corona", "rain"],
        ),
        0.071429,
    ),
    (
        (
            ["sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["corona", "rain", "moon", "delta", "clouds", "pulsar", "stellar", "wind", "galaxy"],
        ),
        0.133333,
    ),
    (
        (
            ["moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["stellar", "wind", "galaxy", "mirage", "frost", "meteor", "venus", "fog", "lunar", "shower"],
        ),
        0.055556,
    ),
    (
        (
            ["star", "lunar", "delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["venus", "fog", "lunar", "shower", "humid", "plasma", "tide", "sun", "arctic", "storm", "zenith"],
        ),
        0.166667,
    ),
    (
        (
            [
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
            ],
            [
                "tide",
                "sun",
                "arctic",
                "storm",
                "zenith",
                "cosmic",
                "snow",
                "star",
                "oasis",
                "breeze",
                "quasar",
                "gravity",
            ],
        ),
        0.210526,
    ),
    (
        (
            [
                "orbit",
                "arctic",
                "mirage",
                "comet",
                "breeze",
                "humid",
                "pulsar",
                "nebula",
                "cosmic",
                "venus",
                "rain",
                "mist",
            ],
            ["snow", "star", "oasis", "breeze"],
        ),
        0.066667,
    ),
    ((["lunar", "delta", "vapor", "storm", "frost"], ["mist", "orbit", "vapor", "hail", "nebula"]), 0.111111),
    (
        (
            ["solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["dew", "solar", "comet", "aurora", "corona", "rain"],
        ),
        0.090909,
    ),
    (
        (
            ["arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["moon", "delta", "clouds", "pulsar", "stellar", "wind", "galaxy"],
        ),
        0.076923,
    ),
    (
        (
            ["delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["galaxy", "mirage", "frost", "meteor", "venus", "fog", "lunar", "shower"],
        ),
        0.066667,
    ),
    (
        (
            ["oasis", "shower", "clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            ["lunar", "shower", "humid", "plasma", "tide", "sun", "arctic", "storm", "zenith"],
        ),
        0.2,
    ),
    (
        (
            ["mirage", "comet", "breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis", "breeze", "quasar", "gravity"],
        ),
        0.111111,
    ),
    (
        (
            ["vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["oasis", "breeze", "quasar", "gravity", "mist", "orbit", "vapor", "hail", "nebula", "mars", "dew"],
        ),
        0.157895,
    ),
    (
        (
            [
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
                "wind",
                "dew",
                "star",
                "lunar",
            ],
            [
                "vapor",
                "hail",
                "nebula",
                "mars",
                "dew",
                "solar",
                "comet",
                "aurora",
                "corona",
                "rain",
                "moon",
                "delta",
            ],
        ),
        0.142857,
    ),
    ((["comet", "breeze", "humid", "pulsar", "nebula"], ["comet", "aurora", "corona", "rain"]), 0.125),
    (
        (
            ["storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["clouds", "pulsar", "stellar", "wind", "galaxy"],
        ),
        0.1,
    ),
    (
        (
            ["clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            ["frost", "meteor", "venus", "fog", "lunar", "shower"],
        ),
        0.083333,
    ),
    (
        (
            ["breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["humid", "plasma", "tide", "sun", "arctic", "storm", "zenith"],
        ),
        0.071429,
    ),
    (
        (
            ["frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["zenith", "cosmic", "snow", "star", "oasis", "breeze", "quasar", "gravity"],
        ),
        0.133333,
    ),
    (
        (
            ["hail", "zenith", "meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            ["quasar", "gravity", "mist", "orbit", "vapor", "hail", "nebula", "mars", "dew"],
        ),
        0.1875,
    ),
    (
        (
            ["humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["nebula", "mars", "dew", "solar", "comet", "aurora", "corona", "rain", "moon", "delta"],
        ),
        0.166667,
    ),
    (
        (
            [
                "aurora",
                "quasar",
                "plasma",
                "stellar",
                "mars",
                "snow",
                "fog",
                "moon",
                "orbit",
                "arctic",
                "mirage",
                "comet",
            ],
            [
                "corona",
                "rain",
                "moon",
                "delta",
                "clouds",
                "pulsar",
                "stellar",
                "wind",
                "galaxy",
                "mirage",
                "frost",
            ],
        ),
        0.15,
    ),
    (
        (
            ["zenith", "meteor", "corona", "gravity", "tide"],
            [
                "stellar",
                "wind",
                "galaxy",
                "mirage",
                "frost",
                "meteor",
                "venus",
                "fog",
                "lunar",
                "shower",
                "humid",
                "plasma",
            ],
        ),
        0.0625,
    ),
    ((["pulsar", "nebula", "cosmic", "venus", "rain", "mist"], ["venus", "fog", "lunar", "shower"]), 0.111111),
    (
        (
            ["quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["tide", "sun", "arctic", "storm", "zenith"],
        ),
        0.0,
    ),
    (
        (
            ["meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            ["snow", "star", "oasis", "breeze", "quasar", "gravity"],
        ),
        0.166667,
    ),
    (
        (
            ["nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["mist", "orbit", "vapor", "hail", "nebula", "mars", "dew"],
        ),
        0.142857,
    ),
    (
        (
            ["plasma", "stellar", "mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["dew", "solar", "comet", "aurora", "corona", "rain", "moon", "delta"],
        ),
        0.125,
    ),
    (
        (
            ["corona", "gravity", "tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["moon", "delta", "clouds", "pulsar", "stellar", "wind", "galaxy", "mirage", "frost"],
        ),
        0.176471,
    ),
    (
        (
            [
                "cosmic",
                "venus",
                "rain",
                "mist",
                "sun",
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
            ],
            ["galaxy", "mirage", "frost", "meteor", "venus", "fog", "lunar", "shower", "humid", "plasma"],
        ),
        0.157895,
    ),
    (
        (
            ["stellar", "mars", "snow", "fog", "moon"],
            ["lunar", "shower", "humid", "plasma", "tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow"],
        ),
        0.066667,
    ),
    (
        (
            ["gravity", "tide", "wind", "dew", "star", "lunar"],
            [
                "arctic",
                "storm",
                "zenith",
                "cosmic",
                "snow",
                "star",
                "oasis",
                "breeze",
                "quasar",
                "gravity",
                "mist",
                "orbit",
            ],
        ),
        0.125,
    ),
    ((["venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"], ["oasis", "breeze", "quasar", "gravity"]), 0.1),
    (
        (
            ["mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["vapor", "hail", "nebula", "mars", "dew"],
        ),
        0.083333,
    ),
    (
        (
            ["tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["comet", "aurora", "corona", "rain", "moon", "delta"],
        ),
        0.071429,
    ),
    (
        (
            ["rain", "mist", "sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["clouds", "pulsar", "stellar", "wind", "galaxy", "mirage", "frost"],
        ),
        0.133333,
    ),
    (
        (
            ["snow", "fog", "moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["frost", "meteor", "venus", "fog", "lunar", "shower", "humid", "plasma"],
        ),
        0.117647,
    ),
    (
        (
            [
                "wind",
                "dew",
                "star",
                "lunar",
                "delta",
                "vapor",
                "storm",
                "frost",
                "aurora",
                "quasar",
                "plasma",
                "stellar",
            ],
            ["humid", "plasma", "tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow"],
        ),
        0.105263,
    ),
    (
        (
            ["mist", "sun", "galaxy", "solar", "oasis"],
            ["zenith", "cosmic", "snow", "star", "oasis", "breeze", "quasar", "gravity", "mist", "orbit"],
        ),
        0.153846,
    ),
    (
        (
            ["fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["quasar", "gravity", "mist", "orbit", "vapor", "hail", "nebula", "mars", "dew", "solar", "comet"],
        ),
        0.133333,
    ),
    (
        (
            ["dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            [
                "nebula",
                "mars",
                "dew",
                "solar",
                "comet",
                "aurora",
                "corona",
                "rain",
                "moon",
                "delta",
                "clouds",
                "pulsar",
            ],
        ),
        0.117647,
    ),
    (
        (
            ["sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["corona", "rain", "moon", "delta"],
        ),
        0.0,
    ),
    (
        (
            ["moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["stellar", "wind", "galaxy", "mirage", "frost"],
        ),
        0.076923,
    ),
    (
        (
            ["star", "lunar", "delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["venus", "fog", "lunar", "shower", "humid", "plasma"],
        ),
        0.142857,
    ),
    (
        (
            [
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
            ],
            ["tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow"],
        ),
        0.125,
    ),
    (
        (
            [
                "orbit",
                "arctic",
                "mirage",
                "comet",
                "breeze",
                "humid",
                "pulsar",
                "nebula",
                "cosmic",
                "venus",
                "rain",
                "mist",
            ],
            ["snow", "star", "oasis", "breeze", "quasar", "gravity", "mist", "orbit"],
        ),
        0.176471,
    ),
    (
        (
            ["lunar", "delta", "vapor", "storm", "frost"],
            ["mist", "orbit", "vapor", "hail", "nebula", "mars", "dew", "solar", "comet"],
        ),
        0.076923,
    ),
    (
        (
            ["solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["dew", "solar", "comet", "aurora", "corona", "rain", "moon", "delta", "clouds", "pulsar"],
        ),
        0.142857,
    ),
    (
        (
            ["arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            [
                "moon",
                "delta",
                "clouds",
                "pulsar",
                "stellar",
                "wind",
                "galaxy",
                "mirage",
                "frost",
                "meteor",
                "venus",
            ],
        ),
        0.125,
    ),
    (
        (
            ["delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            [
                "galaxy",
                "mirage",
                "frost",
                "meteor",
                "venus",
                "fog",
                "lunar",
                "shower",
                "humid",
                "plasma",
                "tide",
                "sun",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["oasis", "shower", "clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            ["lunar", "shower", "humid", "plasma"],
        ),
        0.083333,
    ),
    (
        (
            ["mirage", "comet", "breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["arctic", "storm", "zenith", "cosmic", "snow"],
        ),
        0.071429,
    ),
    (
        (
            ["vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["oasis", "breeze", "quasar", "gravity", "mist", "orbit"],
        ),
        0.0625,
    ),
    (
        (
            [
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
                "wind",
                "dew",
                "star",
                "lunar",
            ],
            ["vapor", "hail", "nebula", "mars", "dew", "solar", "comet"],
        ),
        0.117647,
    ),
    (
        (
            ["comet", "breeze", "humid", "pulsar", "nebula"],
            ["comet", "aurora", "corona", "rain", "moon", "delta", "clouds", "pulsar"],
        ),
        0.181818,
    ),
    (
        (
            ["storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["clouds", "pulsar", "stellar", "wind", "galaxy", "mirage", "frost", "meteor", "venus"],
        ),
        0.153846,
    ),
    (
        (
            ["clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            ["frost", "meteor", "venus", "fog", "lunar", "shower", "humid", "plasma", "tide", "sun"],
        ),
        0.133333,
    ),
    (
        (
            ["breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["humid", "plasma", "tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis"],
        ),
        0.117647,
    ),
    (
        (
            ["frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            [
                "zenith",
                "cosmic",
                "snow",
                "star",
                "oasis",
                "breeze",
                "quasar",
                "gravity",
                "mist",
                "orbit",
                "vapor",
                "hail",
            ],
        ),
        0.105263,
    ),
    (
        (
            ["hail", "zenith", "meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            ["quasar", "gravity", "mist", "orbit"],
        ),
        0.076923,
    ),
    (
        (
            ["humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["nebula", "mars", "dew", "solar", "comet"],
        ),
        0.142857,
    ),
    (
        (
            [
                "aurora",
                "quasar",
                "plasma",
                "stellar",
                "mars",
                "snow",
                "fog",
                "moon",
                "orbit",
                "arctic",
                "mirage",
                "comet",
            ],
            ["corona", "rain", "moon", "delta", "clouds", "pulsar"],
        ),
        0.058824,
    ),
    (
        (
            ["zenith", "meteor", "corona", "gravity", "tide"],
            ["stellar", "wind", "galaxy", "mirage", "frost", "meteor", "venus"],
        ),
        0.090909,
    ),
    (
        (
            ["pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["venus", "fog", "lunar", "shower", "humid", "plasma", "tide", "sun"],
        ),
        0.076923,
    ),
    (
        (
            ["quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis"],
        ),
        0.066667,
    ),
    (
        (
            ["meteor", "corona", "gravity", "tide", "wind", "dew", "star", "lunar"],
            ["snow", "star", "oasis", "breeze", "quasar", "gravity", "mist", "orbit", "vapor", "hail"],
        ),
        0.125,
    ),
    (
        (
            ["nebula", "cosmic", "venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["mist", "orbit", "vapor", "hail", "nebula", "mars", "dew", "solar", "comet", "aurora", "corona"],
        ),
        0.176471,
    ),
    (
        (
            ["plasma", "stellar", "mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            [
                "dew",
                "solar",
                "comet",
                "aurora",
                "corona",
                "rain",
                "moon",
                "delta",
                "clouds",
                "pulsar",
                "stellar",
                "wind",
            ],
        ),
        0.157895,
    ),
    (
        (
            ["corona", "gravity", "tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["moon", "delta", "clouds", "pulsar"],
        ),
        0.071429,
    ),
    (
        (
            [
                "cosmic",
                "venus",
                "rain",
                "mist",
                "sun",
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
            ],
            ["galaxy", "mirage", "frost", "meteor", "venus"],
        ),
        0.133333,
    ),
    ((["stellar", "mars", "snow", "fog", "moon"], ["lunar", "shower", "humid", "plasma", "tide", "sun"]), 0.0),
    (
        (
            ["gravity", "tide", "wind", "dew", "star", "lunar"],
            ["arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis"],
        ),
        0.083333,
    ),
    (
        (
            ["venus", "rain", "mist", "sun", "galaxy", "solar", "oasis"],
            ["oasis", "breeze", "quasar", "gravity", "mist", "orbit", "vapor", "hail"],
        ),
        0.153846,
    ),
    (
        (
            ["mars", "snow", "fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["vapor", "hail", "nebula", "mars", "dew", "solar", "comet", "aurora", "corona"],
        ),
        0.133333,
    ),
    (
        (
            ["tide", "wind", "dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["comet", "aurora", "corona", "rain", "moon", "delta", "clouds", "pulsar", "stellar", "wind"],
        ),
        0.117647,
    ),
    (
        (
            ["rain", "mist", "sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            [
                "clouds",
                "pulsar",
                "stellar",
                "wind",
                "galaxy",
                "mirage",
                "frost",
                "meteor",
                "venus",
                "fog",
                "lunar",
            ],
        ),
        0.105263,
    ),
    (
        (
            ["snow", "fog", "moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            [
                "frost",
                "meteor",
                "venus",
                "fog",
                "lunar",
                "shower",
                "humid",
                "plasma",
                "tide",
                "sun",
                "arctic",
                "storm",
            ],
        ),
        0.15,
    ),
    (
        (
            [
                "wind",
                "dew",
                "star",
                "lunar",
                "delta",
                "vapor",
                "storm",
                "frost",
                "aurora",
                "quasar",
                "plasma",
                "stellar",
            ],
            ["humid", "plasma", "tide", "sun"],
        ),
        0.066667,
    ),
    ((["mist", "sun", "galaxy", "solar", "oasis"], ["zenith", "cosmic", "snow", "star", "oasis"]), 0.111111),
    (
        (
            ["fog", "moon", "orbit", "arctic", "mirage", "comet"],
            ["quasar", "gravity", "mist", "orbit", "vapor", "hail"],
        ),
        0.090909,
    ),
    (
        (
            ["dew", "star", "lunar", "delta", "vapor", "storm", "frost"],
            ["nebula", "mars", "dew", "solar", "comet", "aurora", "corona"],
        ),
        0.076923,
    ),
    (
        (
            ["sun", "galaxy", "solar", "oasis", "shower", "clouds", "hail", "zenith"],
            ["corona", "rain", "moon", "delta", "clouds", "pulsar", "stellar", "wind"],
        ),
        0.066667,
    ),
    (
        (
            ["moon", "orbit", "arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["stellar", "wind", "galaxy", "mirage", "frost", "meteor", "venus", "fog", "lunar"],
        ),
        0.058824,
    ),
    (
        (
            ["star", "lunar", "delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["venus", "fog", "lunar", "shower", "humid", "plasma", "tide", "sun", "arctic", "storm"],
        ),
        0.176471,
    ),
    (
        (
            [
                "galaxy",
                "solar",
                "oasis",
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
            ],
            ["tide", "sun", "arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis", "breeze", "quasar"],
        ),
        0.157895,
    ),
    (
        (
            [
                "orbit",
                "arctic",
                "mirage",
                "comet",
                "breeze",
                "humid",
                "pulsar",
                "nebula",
                "cosmic",
                "venus",
                "rain",
                "mist",
            ],
            [
                "snow",
                "star",
                "oasis",
                "breeze",
                "quasar",
                "gravity",
                "mist",
                "orbit",
                "vapor",
                "hail",
                "nebula",
                "mars",
            ],
        ),
        0.2,
    ),
    ((["lunar", "delta", "vapor", "storm", "frost"], ["mist", "orbit", "vapor", "hail"]), 0.125),
    ((["solar", "oasis", "shower", "clouds", "hail", "zenith"], ["dew", "solar", "comet", "aurora", "corona"]), 0.1),
    (
        (
            ["arctic", "mirage", "comet", "breeze", "humid", "pulsar", "nebula"],
            ["moon", "delta", "clouds", "pulsar", "stellar", "wind"],
        ),
        0.083333,
    ),
    (
        (
            ["delta", "vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar"],
            ["galaxy", "mirage", "frost", "meteor", "venus", "fog", "lunar"],
        ),
        0.071429,
    ),
    (
        (
            ["oasis", "shower", "clouds", "hail", "zenith", "meteor", "corona", "gravity", "tide"],
            ["lunar", "shower", "humid", "plasma", "tide", "sun", "arctic", "storm"],
        ),
        0.133333,
    ),
    (
        (
            ["mirage", "comet", "breeze", "humid", "pulsar", "nebula", "cosmic", "venus", "rain", "mist"],
            ["arctic", "storm", "zenith", "cosmic", "snow", "star", "oasis", "breeze", "quasar"],
        ),
        0.117647,
    ),
    (
        (
            ["vapor", "storm", "frost", "aurora", "quasar", "plasma", "stellar", "mars", "snow", "fog", "moon"],
            ["oasis", "breeze", "quasar", "gravity", "mist", "orbit", "vapor", "hail", "nebula", "mars"],
        ),
        0.166667,
    ),
    (
        (
            [
                "shower",
                "clouds",
                "hail",
                "zenith",
                "meteor",
                "corona",
                "gravity",
                "tide",
                "wind",
                "dew",
                "star",
                "lunar",
            ],
            ["vapor", "hail", "nebula", "mars", "dew", "solar", "comet", "aurora", "corona", "rain", "moon"],
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
