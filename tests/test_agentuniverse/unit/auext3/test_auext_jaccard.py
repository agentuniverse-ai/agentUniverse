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
    (
        (
            ["bridge", "engine", "helix", "valves", "bolts"],
            ["bridge", "ingots", "drills", "keels", "rivets", "beacon"],
        ),
        0.1,
    ),
    (
        (
            ["cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["diodes", "valves", "forges", "mixers", "wedges", "diesel", "fibers"],
        ),
        0.181818,
    ),
    (
        (
            ["diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            ["fibers", "anchor", "hanger", "orbit", "yokes", "furnace", "helix", "cranes"],
        ),
        0.071429,
    ),
    (
        (
            ["engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["helix", "cranes", "jets", "quarry", "asphalt", "cables", "joints", "exits", "lifts"],
        ),
        0.133333,
    ),
    (
        (
            ["fibers", "ingots", "welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            ["joints", "exits", "lifts", "shafts", "copper", "engine", "welder", "gantry", "nozzles", "xenons"],
        ),
        0.117647,
    ),
    (
        (
            ["gears", "joints", "anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            [
                "welder",
                "gantry",
                "nozzles",
                "xenons",
                "enamel",
                "gears",
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
            ],
        ),
        0.166667,
    ),
    (
        (
            [
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
            ],
            [
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
                "keels",
                "rivets",
                "beacon",
                "diodes",
                "valves",
            ],
        ),
        0.210526,
    ),
    (
        (
            [
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
            ],
            ["drills", "keels", "rivets", "beacon"],
        ),
        0.066667,
    ),
    ((["joints", "anchor", "drills", "gantry", "jets"], ["forges", "mixers", "wedges", "diesel", "fibers"]), 0.0),
    (
        (
            ["valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["hanger", "orbit", "yokes", "furnace", "helix", "cranes"],
        ),
        0.090909,
    ),
    (
        (
            ["welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            ["jets", "quarry", "asphalt", "cables", "joints", "exits", "lifts"],
        ),
        0.076923,
    ),
    (
        (
            ["anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["lifts", "shafts", "copper", "engine", "welder", "gantry", "nozzles", "xenons"],
        ),
        0.142857,
    ),
    (
        (
            ["bolts", "exits", "hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            ["nozzles", "xenons", "enamel", "gears", "bolts", "intake", "pumps", "zincs", "bridge"],
        ),
        0.2,
    ),
    (
        (
            ["cranes", "forges", "intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["pumps", "zincs", "bridge", "ingots", "drills", "keels", "rivets", "beacon", "diodes", "valves"],
        ),
        0.111111,
    ),
    (
        (
            [
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
            ],
            [
                "rivets",
                "beacon",
                "diodes",
                "valves",
                "forges",
                "mixers",
                "wedges",
                "diesel",
                "fibers",
                "anchor",
                "hanger",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
            ],
            [
                "wedges",
                "diesel",
                "fibers",
                "anchor",
                "hanger",
                "orbit",
                "yokes",
                "furnace",
                "helix",
                "cranes",
                "jets",
                "quarry",
            ],
        ),
        0.2,
    ),
    ((["forges", "intake", "lifts", "orbit", "rivets"], ["yokes", "furnace", "helix", "cranes"]), 0.0),
    (
        (
            ["gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["asphalt", "cables", "joints", "exits", "lifts"],
        ),
        0.0,
    ),
    (
        (
            ["hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            ["copper", "engine", "welder", "gantry", "nozzles", "xenons"],
        ),
        0.181818,
    ),
    (
        (
            ["intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["enamel", "gears", "bolts", "intake", "pumps", "zincs", "bridge"],
        ),
        0.153846,
    ),
    (
        (
            ["jets", "mixers", "pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            ["bridge", "ingots", "drills", "keels", "rivets", "beacon", "diodes", "valves"],
        ),
        0.0625,
    ),
    (
        (
            ["keels", "nozzles", "quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["diodes", "valves", "forges", "mixers", "wedges", "diesel", "fibers", "anchor", "hanger"],
        ),
        0.117647,
    ),
    (
        (
            [
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
            ],
            ["fibers", "anchor", "hanger", "orbit", "yokes", "furnace", "helix", "cranes", "jets", "quarry"],
        ),
        0.105263,
    ),
    (
        (
            [
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
            ],
            [
                "helix",
                "cranes",
                "jets",
                "quarry",
                "asphalt",
                "cables",
                "joints",
                "exits",
                "lifts",
                "shafts",
                "copper",
            ],
        ),
        0.15,
    ),
    (
        (
            ["nozzles", "quarry", "wedges", "zincs", "copper"],
            [
                "joints",
                "exits",
                "lifts",
                "shafts",
                "copper",
                "engine",
                "welder",
                "gantry",
                "nozzles",
                "xenons",
                "enamel",
                "gears",
            ],
        ),
        0.133333,
    ),
    (
        (
            ["orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["welder", "gantry", "nozzles", "xenons"],
        ),
        0.111111,
    ),
    (
        (
            ["pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            ["bolts", "intake", "pumps", "zincs", "bridge"],
        ),
        0.090909,
    ),
    (
        (
            ["quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["drills", "keels", "rivets", "beacon", "diodes", "valves"],
        ),
        0.076923,
    ),
    (
        (
            ["rivets", "xenons", "asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            ["forges", "mixers", "wedges", "diesel", "fibers", "anchor", "hanger"],
        ),
        0.066667,
    ),
    (
        (
            ["shafts", "yokes", "beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["hanger", "orbit", "yokes", "furnace", "helix", "cranes", "jets", "quarry"],
        ),
        0.125,
    ),
    (
        (
            [
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
            ],
            ["jets", "quarry", "asphalt", "cables", "joints", "exits", "lifts", "shafts", "copper"],
        ),
        0.176471,
    ),
    (
        (
            [
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
            ],
            ["lifts", "shafts", "copper", "engine", "welder", "gantry", "nozzles", "xenons", "enamel", "gears"],
        ),
        0.157895,
    ),
    (
        (
            ["yokes", "beacon", "enamel", "cables", "fibers"],
            [
                "nozzles",
                "xenons",
                "enamel",
                "gears",
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
            ],
        ),
        0.066667,
    ),
    (
        (
            ["zincs", "copper", "furnace", "diodes", "gears", "joints"],
            [
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
                "keels",
                "rivets",
                "beacon",
                "diodes",
                "valves",
                "forges",
                "mixers",
            ],
        ),
        0.125,
    ),
    (
        (
            ["asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            ["rivets", "beacon", "diodes", "valves"],
        ),
        0.1,
    ),
    (
        (
            ["beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["wedges", "diesel", "fibers", "anchor", "hanger"],
        ),
        0.083333,
    ),
    (
        (
            ["copper", "furnace", "diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            ["yokes", "furnace", "helix", "cranes", "jets", "quarry"],
        ),
        0.153846,
    ),
    (
        (
            ["diesel", "bridge", "engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["asphalt", "cables", "joints", "exits", "lifts", "shafts", "copper"],
        ),
        0.0625,
    ),
    (
        (
            [
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
            ],
            ["copper", "engine", "welder", "gantry", "nozzles", "xenons", "enamel", "gears"],
        ),
        0.117647,
    ),
    (
        (
            [
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
            ],
            ["enamel", "gears", "bolts", "intake", "pumps", "zincs", "bridge", "ingots", "drills"],
        ),
        0.166667,
    ),
    (
        (
            ["bridge", "engine", "helix", "valves", "bolts"],
            ["bridge", "ingots", "drills", "keels", "rivets", "beacon", "diodes", "valves", "forges", "mixers"],
        ),
        0.153846,
    ),
    (
        (
            ["cables", "fibers", "ingots", "welder", "cranes", "forges"],
            [
                "diodes",
                "valves",
                "forges",
                "mixers",
                "wedges",
                "diesel",
                "fibers",
                "anchor",
                "hanger",
                "orbit",
                "yokes",
            ],
        ),
        0.133333,
    ),
    (
        (
            ["diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            [
                "fibers",
                "anchor",
                "hanger",
                "orbit",
                "yokes",
                "furnace",
                "helix",
                "cranes",
                "jets",
                "quarry",
                "asphalt",
                "cables",
            ],
        ),
        0.117647,
    ),
    (
        (
            ["engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["helix", "cranes", "jets", "quarry"],
        ),
        0.090909,
    ),
    (
        (
            ["fibers", "ingots", "welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            ["joints", "exits", "lifts", "shafts", "copper"],
        ),
        0.076923,
    ),
    (
        (
            ["gears", "joints", "anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["welder", "gantry", "nozzles", "xenons", "enamel", "gears"],
        ),
        0.142857,
    ),
    (
        (
            [
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
            ],
            ["bolts", "intake", "pumps", "zincs", "bridge", "ingots", "drills"],
        ),
        0.125,
    ),
    (
        (
            [
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
            ],
            ["drills", "keels", "rivets", "beacon", "diodes", "valves", "forges", "mixers"],
        ),
        0.111111,
    ),
    (
        (
            ["joints", "anchor", "drills", "gantry", "jets"],
            ["forges", "mixers", "wedges", "diesel", "fibers", "anchor", "hanger", "orbit", "yokes"],
        ),
        0.076923,
    ),
    (
        (
            ["valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["hanger", "orbit", "yokes", "furnace", "helix", "cranes", "jets", "quarry", "asphalt", "cables"],
        ),
        0.066667,
    ),
    (
        (
            ["welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            [
                "jets",
                "quarry",
                "asphalt",
                "cables",
                "joints",
                "exits",
                "lifts",
                "shafts",
                "copper",
                "engine",
                "welder",
            ],
        ),
        0.125,
    ),
    (
        (
            ["anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            [
                "lifts",
                "shafts",
                "copper",
                "engine",
                "welder",
                "gantry",
                "nozzles",
                "xenons",
                "enamel",
                "gears",
                "bolts",
                "intake",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["bolts", "exits", "hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            ["nozzles", "xenons", "enamel", "gears"],
        ),
        0.083333,
    ),
    (
        (
            ["cranes", "forges", "intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["pumps", "zincs", "bridge", "ingots", "drills"],
        ),
        0.071429,
    ),
    (
        (
            [
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
            ],
            ["rivets", "beacon", "diodes", "valves", "forges", "mixers"],
        ),
        0.133333,
    ),
    (
        (
            [
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
            ],
            ["wedges", "diesel", "fibers", "anchor", "hanger", "orbit", "yokes"],
        ),
        0.117647,
    ),
    (
        (
            ["forges", "intake", "lifts", "orbit", "rivets"],
            ["yokes", "furnace", "helix", "cranes", "jets", "quarry", "asphalt", "cables"],
        ),
        0.0,
    ),
    (
        (
            ["gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["asphalt", "cables", "joints", "exits", "lifts", "shafts", "copper", "engine", "welder"],
        ),
        0.071429,
    ),
    (
        (
            ["hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            ["copper", "engine", "welder", "gantry", "nozzles", "xenons", "enamel", "gears", "bolts", "intake"],
        ),
        0.133333,
    ),
    (
        (
            ["intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            [
                "enamel",
                "gears",
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
                "keels",
                "rivets",
            ],
        ),
        0.1875,
    ),
    (
        (
            ["jets", "mixers", "pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            [
                "bridge",
                "ingots",
                "drills",
                "keels",
                "rivets",
                "beacon",
                "diodes",
                "valves",
                "forges",
                "mixers",
                "wedges",
                "diesel",
            ],
        ),
        0.105263,
    ),
    (
        (
            ["keels", "nozzles", "quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["diodes", "valves", "forges", "mixers"],
        ),
        0.076923,
    ),
    (
        (
            [
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
            ],
            ["fibers", "anchor", "hanger", "orbit", "yokes"],
        ),
        0.066667,
    ),
    (
        (
            [
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
            ],
            ["helix", "cranes", "jets", "quarry", "asphalt", "cables"],
        ),
        0.125,
    ),
    (
        (
            ["nozzles", "quarry", "wedges", "zincs", "copper"],
            ["joints", "exits", "lifts", "shafts", "copper", "engine", "welder"],
        ),
        0.090909,
    ),
    (
        (
            ["orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["welder", "gantry", "nozzles", "xenons", "enamel", "gears", "bolts", "intake"],
        ),
        0.076923,
    ),
    (
        (
            ["pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            ["bolts", "intake", "pumps", "zincs", "bridge", "ingots", "drills", "keels", "rivets"],
        ),
        0.066667,
    ),
    (
        (
            ["quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["drills", "keels", "rivets", "beacon", "diodes", "valves", "forges", "mixers", "wedges", "diesel"],
        ),
        0.125,
    ),
    (
        (
            ["rivets", "xenons", "asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            [
                "forges",
                "mixers",
                "wedges",
                "diesel",
                "fibers",
                "anchor",
                "hanger",
                "orbit",
                "yokes",
                "furnace",
                "helix",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["shafts", "yokes", "beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            [
                "hanger",
                "orbit",
                "yokes",
                "furnace",
                "helix",
                "cranes",
                "jets",
                "quarry",
                "asphalt",
                "cables",
                "joints",
                "exits",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
            ],
            ["jets", "quarry", "asphalt", "cables"],
        ),
        0.071429,
    ),
    (
        (
            [
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
            ],
            ["lifts", "shafts", "copper", "engine", "welder"],
        ),
        0.0625,
    ),
    (
        (
            ["yokes", "beacon", "enamel", "cables", "fibers"],
            ["nozzles", "xenons", "enamel", "gears", "bolts", "intake"],
        ),
        0.1,
    ),
    (
        (
            ["zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["pumps", "zincs", "bridge", "ingots", "drills", "keels", "rivets"],
        ),
        0.083333,
    ),
    (
        (
            ["asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            ["rivets", "beacon", "diodes", "valves", "forges", "mixers", "wedges", "diesel"],
        ),
        0.153846,
    ),
    (
        (
            ["beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["wedges", "diesel", "fibers", "anchor", "hanger", "orbit", "yokes", "furnace", "helix"],
        ),
        0.0625,
    ),
    (
        (
            ["copper", "furnace", "diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            ["yokes", "furnace", "helix", "cranes", "jets", "quarry", "asphalt", "cables", "joints", "exits"],
        ),
        0.1875,
    ),
    (
        (
            ["diesel", "bridge", "engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            [
                "asphalt",
                "cables",
                "joints",
                "exits",
                "lifts",
                "shafts",
                "copper",
                "engine",
                "welder",
                "gantry",
                "nozzles",
            ],
        ),
        0.166667,
    ),
    (
        (
            [
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
            ],
            [
                "copper",
                "engine",
                "welder",
                "gantry",
                "nozzles",
                "xenons",
                "enamel",
                "gears",
                "bolts",
                "intake",
                "pumps",
                "zincs",
            ],
        ),
        0.15,
    ),
    (
        (
            [
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
            ],
            ["enamel", "gears", "bolts", "intake"],
        ),
        0.066667,
    ),
    ((["bridge", "engine", "helix", "valves", "bolts"], ["bridge", "ingots", "drills", "keels", "rivets"]), 0.111111),
    (
        (
            ["cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["diodes", "valves", "forges", "mixers", "wedges", "diesel"],
        ),
        0.090909,
    ),
    (
        (
            ["diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            ["fibers", "anchor", "hanger", "orbit", "yokes", "furnace", "helix"],
        ),
        0.076923,
    ),
    (
        (
            ["engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["helix", "cranes", "jets", "quarry", "asphalt", "cables", "joints", "exits"],
        ),
        0.142857,
    ),
    (
        (
            ["fibers", "ingots", "welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            ["joints", "exits", "lifts", "shafts", "copper", "engine", "welder", "gantry", "nozzles"],
        ),
        0.125,
    ),
    (
        (
            ["gears", "joints", "anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["welder", "gantry", "nozzles", "xenons", "enamel", "gears", "bolts", "intake", "pumps", "zincs"],
        ),
        0.176471,
    ),
    (
        (
            [
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
            ],
            [
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
                "keels",
                "rivets",
                "beacon",
                "diodes",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
            ],
            [
                "drills",
                "keels",
                "rivets",
                "beacon",
                "diodes",
                "valves",
                "forges",
                "mixers",
                "wedges",
                "diesel",
                "fibers",
                "anchor",
            ],
        ),
        0.142857,
    ),
    ((["joints", "anchor", "drills", "gantry", "jets"], ["forges", "mixers", "wedges", "diesel"]), 0.0),
    (
        (
            ["valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["hanger", "orbit", "yokes", "furnace", "helix"],
        ),
        0.1,
    ),
    (
        (
            ["welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            ["jets", "quarry", "asphalt", "cables", "joints", "exits"],
        ),
        0.0,
    ),
    (
        (
            ["anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["lifts", "shafts", "copper", "engine", "welder", "gantry", "nozzles"],
        ),
        0.153846,
    ),
    (
        (
            ["bolts", "exits", "hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            ["nozzles", "xenons", "enamel", "gears", "bolts", "intake", "pumps", "zincs"],
        ),
        0.214286,
    ),
    (
        (
            ["cranes", "forges", "intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["pumps", "zincs", "bridge", "ingots", "drills", "keels", "rivets", "beacon", "diodes"],
        ),
        0.117647,
    ),
    (
        (
            [
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
            ],
            ["rivets", "beacon", "diodes", "valves", "forges", "mixers", "wedges", "diesel", "fibers", "anchor"],
        ),
        0.166667,
    ),
    (
        (
            [
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
            ],
            [
                "wedges",
                "diesel",
                "fibers",
                "anchor",
                "hanger",
                "orbit",
                "yokes",
                "furnace",
                "helix",
                "cranes",
                "jets",
            ],
        ),
        0.15,
    ),
    (
        (
            ["forges", "intake", "lifts", "orbit", "rivets"],
            [
                "yokes",
                "furnace",
                "helix",
                "cranes",
                "jets",
                "quarry",
                "asphalt",
                "cables",
                "joints",
                "exits",
                "lifts",
                "shafts",
            ],
        ),
        0.0625,
    ),
    ((["gantry", "jets", "mixers", "pumps", "shafts", "yokes"], ["asphalt", "cables", "joints", "exits"]), 0.0),
    (
        (
            ["hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            ["copper", "engine", "welder", "gantry", "nozzles"],
        ),
        0.2,
    ),
    (
        (
            ["intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["enamel", "gears", "bolts", "intake", "pumps", "zincs"],
        ),
        0.076923,
    ),
    (
        (
            ["jets", "mixers", "pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            ["bridge", "ingots", "drills", "keels", "rivets", "beacon", "diodes"],
        ),
        0.066667,
    ),
    (
        (
            ["keels", "nozzles", "quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["diodes", "valves", "forges", "mixers", "wedges", "diesel", "fibers", "anchor"],
        ),
        0.125,
    ),
    (
        (
            [
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
            ],
            ["fibers", "anchor", "hanger", "orbit", "yokes", "furnace", "helix", "cranes", "jets"],
        ),
        0.111111,
    ),
    (
        (
            [
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
            ],
            ["helix", "cranes", "jets", "quarry", "asphalt", "cables", "joints", "exits", "lifts", "shafts"],
        ),
        0.157895,
    ),
    (
        (
            ["nozzles", "quarry", "wedges", "zincs", "copper"],
            [
                "joints",
                "exits",
                "lifts",
                "shafts",
                "copper",
                "engine",
                "welder",
                "gantry",
                "nozzles",
                "xenons",
                "enamel",
            ],
        ),
        0.142857,
    ),
    (
        (
            ["orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            [
                "welder",
                "gantry",
                "nozzles",
                "xenons",
                "enamel",
                "gears",
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
                "ingots",
            ],
        ),
        0.125,
    ),
    (
        (
            ["pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            ["bolts", "intake", "pumps", "zincs"],
        ),
        0.1,
    ),
    (
        (
            ["quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["drills", "keels", "rivets", "beacon", "diodes"],
        ),
        0.083333,
    ),
    (
        (
            ["rivets", "xenons", "asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            ["forges", "mixers", "wedges", "diesel", "fibers", "anchor"],
        ),
        0.071429,
    ),
    (
        (
            ["shafts", "yokes", "beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["hanger", "orbit", "yokes", "furnace", "helix", "cranes", "jets"],
        ),
        0.133333,
    ),
    (
        (
            [
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
            ],
            ["jets", "quarry", "asphalt", "cables", "joints", "exits", "lifts", "shafts"],
        ),
        0.117647,
    ),
    (
        (
            [
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
            ],
            ["lifts", "shafts", "copper", "engine", "welder", "gantry", "nozzles", "xenons", "enamel"],
        ),
        0.166667,
    ),
    (
        (
            ["yokes", "beacon", "enamel", "cables", "fibers"],
            ["nozzles", "xenons", "enamel", "gears", "bolts", "intake", "pumps", "zincs", "bridge", "ingots"],
        ),
        0.071429,
    ),
    (
        (
            ["zincs", "copper", "furnace", "diodes", "gears", "joints"],
            [
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
                "keels",
                "rivets",
                "beacon",
                "diodes",
                "valves",
                "forges",
            ],
        ),
        0.133333,
    ),
    (
        (
            ["asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            [
                "rivets",
                "beacon",
                "diodes",
                "valves",
                "forges",
                "mixers",
                "wedges",
                "diesel",
                "fibers",
                "anchor",
                "hanger",
                "orbit",
            ],
        ),
        0.117647,
    ),
    (
        (
            ["beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["wedges", "diesel", "fibers", "anchor"],
        ),
        0.090909,
    ),
    (
        (
            ["copper", "furnace", "diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            ["yokes", "furnace", "helix", "cranes", "jets"],
        ),
        0.166667,
    ),
    (
        (
            ["diesel", "bridge", "engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["asphalt", "cables", "joints", "exits", "lifts", "shafts"],
        ),
        0.066667,
    ),
    (
        (
            [
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
            ],
            ["copper", "engine", "welder", "gantry", "nozzles", "xenons", "enamel"],
        ),
        0.125,
    ),
    (
        (
            [
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
            ],
            ["enamel", "gears", "bolts", "intake", "pumps", "zincs", "bridge", "ingots"],
        ),
        0.111111,
    ),
    (
        (
            ["bridge", "engine", "helix", "valves", "bolts"],
            ["bridge", "ingots", "drills", "keels", "rivets", "beacon", "diodes", "valves", "forges"],
        ),
        0.166667,
    ),
    (
        (
            ["cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["diodes", "valves", "forges", "mixers", "wedges", "diesel", "fibers", "anchor", "hanger", "orbit"],
        ),
        0.142857,
    ),
    (
        (
            ["diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            [
                "fibers",
                "anchor",
                "hanger",
                "orbit",
                "yokes",
                "furnace",
                "helix",
                "cranes",
                "jets",
                "quarry",
                "asphalt",
            ],
        ),
        0.125,
    ),
    (
        (
            ["engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            [
                "helix",
                "cranes",
                "jets",
                "quarry",
                "asphalt",
                "cables",
                "joints",
                "exits",
                "lifts",
                "shafts",
                "copper",
                "engine",
            ],
        ),
        0.176471,
    ),
    (
        (
            ["fibers", "ingots", "welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            ["joints", "exits", "lifts", "shafts"],
        ),
        0.083333,
    ),
    (
        (
            ["gears", "joints", "anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["welder", "gantry", "nozzles", "xenons", "enamel"],
        ),
        0.071429,
    ),
    (
        (
            [
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
            ],
            ["bolts", "intake", "pumps", "zincs", "bridge", "ingots"],
        ),
        0.133333,
    ),
    (
        (
            [
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
            ],
            ["drills", "keels", "rivets", "beacon", "diodes", "valves", "forges"],
        ),
        0.117647,
    ),
    (
        (
            ["joints", "anchor", "drills", "gantry", "jets"],
            ["forges", "mixers", "wedges", "diesel", "fibers", "anchor", "hanger", "orbit"],
        ),
        0.083333,
    ),
    (
        (
            ["valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["hanger", "orbit", "yokes", "furnace", "helix", "cranes", "jets", "quarry", "asphalt"],
        ),
        0.071429,
    ),
    (
        (
            ["welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            ["jets", "quarry", "asphalt", "cables", "joints", "exits", "lifts", "shafts", "copper", "engine"],
        ),
        0.0625,
    ),
    (
        (
            ["anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            [
                "lifts",
                "shafts",
                "copper",
                "engine",
                "welder",
                "gantry",
                "nozzles",
                "xenons",
                "enamel",
                "gears",
                "bolts",
            ],
        ),
        0.117647,
    ),
    (
        (
            ["bolts", "exits", "hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            [
                "nozzles",
                "xenons",
                "enamel",
                "gears",
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
                "keels",
            ],
        ),
        0.235294,
    ),
    (
        (
            ["cranes", "forges", "intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["pumps", "zincs", "bridge", "ingots"],
        ),
        0.076923,
    ),
    (
        (
            [
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
            ],
            ["rivets", "beacon", "diodes", "valves", "forges"],
        ),
        0.066667,
    ),
    (
        (
            [
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
            ],
            ["wedges", "diesel", "fibers", "anchor", "hanger", "orbit"],
        ),
        0.125,
    ),
    (
        (
            ["forges", "intake", "lifts", "orbit", "rivets"],
            ["yokes", "furnace", "helix", "cranes", "jets", "quarry", "asphalt"],
        ),
        0.0,
    ),
    (
        (
            ["gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["asphalt", "cables", "joints", "exits", "lifts", "shafts", "copper", "engine"],
        ),
        0.076923,
    ),
    (
        (
            ["hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            ["copper", "engine", "welder", "gantry", "nozzles", "xenons", "enamel", "gears", "bolts"],
        ),
        0.142857,
    ),
    (
        (
            ["intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["enamel", "gears", "bolts", "intake", "pumps", "zincs", "bridge", "ingots", "drills", "keels"],
        ),
        0.125,
    ),
    (
        (
            ["jets", "mixers", "pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            [
                "bridge",
                "ingots",
                "drills",
                "keels",
                "rivets",
                "beacon",
                "diodes",
                "valves",
                "forges",
                "mixers",
                "wedges",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["keels", "nozzles", "quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            [
                "diodes",
                "valves",
                "forges",
                "mixers",
                "wedges",
                "diesel",
                "fibers",
                "anchor",
                "hanger",
                "orbit",
                "yokes",
                "furnace",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
            ],
            ["fibers", "anchor", "hanger", "orbit"],
        ),
        0.071429,
    ),
    (
        (
            [
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
            ],
            ["helix", "cranes", "jets", "quarry", "asphalt"],
        ),
        0.0625,
    ),
    (
        (
            ["nozzles", "quarry", "wedges", "zincs", "copper"],
            ["joints", "exits", "lifts", "shafts", "copper", "engine"],
        ),
        0.1,
    ),
    (
        (
            ["orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["welder", "gantry", "nozzles", "xenons", "enamel", "gears", "bolts"],
        ),
        0.083333,
    ),
    (
        (
            ["pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            ["bolts", "intake", "pumps", "zincs", "bridge", "ingots", "drills", "keels"],
        ),
        0.071429,
    ),
    (
        (
            ["quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["drills", "keels", "rivets", "beacon", "diodes", "valves", "forges", "mixers", "wedges"],
        ),
        0.133333,
    ),
    (
        (
            ["rivets", "xenons", "asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            ["forges", "mixers", "wedges", "diesel", "fibers", "anchor", "hanger", "orbit", "yokes", "furnace"],
        ),
        0.055556,
    ),
    (
        (
            ["shafts", "yokes", "beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            [
                "hanger",
                "orbit",
                "yokes",
                "furnace",
                "helix",
                "cranes",
                "jets",
                "quarry",
                "asphalt",
                "cables",
                "joints",
            ],
        ),
        0.166667,
    ),
    (
        (
            [
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
            ],
            [
                "jets",
                "quarry",
                "asphalt",
                "cables",
                "joints",
                "exits",
                "lifts",
                "shafts",
                "copper",
                "engine",
                "welder",
                "gantry",
            ],
        ),
        0.210526,
    ),
    (
        (
            [
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
            ],
            ["lifts", "shafts", "copper", "engine"],
        ),
        0.066667,
    ),
    ((["yokes", "beacon", "enamel", "cables", "fibers"], ["nozzles", "xenons", "enamel", "gears", "bolts"]), 0.111111),
    (
        (
            ["zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["pumps", "zincs", "bridge", "ingots", "drills", "keels"],
        ),
        0.090909,
    ),
    (
        (
            ["asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            ["rivets", "beacon", "diodes", "valves", "forges", "mixers", "wedges"],
        ),
        0.076923,
    ),
    (
        (
            ["beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["wedges", "diesel", "fibers", "anchor", "hanger", "orbit", "yokes", "furnace"],
        ),
        0.066667,
    ),
    (
        (
            ["copper", "furnace", "diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            ["yokes", "furnace", "helix", "cranes", "jets", "quarry", "asphalt", "cables", "joints"],
        ),
        0.2,
    ),
    (
        (
            ["diesel", "bridge", "engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["asphalt", "cables", "joints", "exits", "lifts", "shafts", "copper", "engine", "welder", "gantry"],
        ),
        0.111111,
    ),
    (
        (
            [
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
            ],
            [
                "copper",
                "engine",
                "welder",
                "gantry",
                "nozzles",
                "xenons",
                "enamel",
                "gears",
                "bolts",
                "intake",
                "pumps",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
            ],
            [
                "enamel",
                "gears",
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
                "keels",
                "rivets",
                "beacon",
            ],
        ),
        0.142857,
    ),
    ((["bridge", "engine", "helix", "valves", "bolts"], ["bridge", "ingots", "drills", "keels"]), 0.125),
    (
        (
            ["cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["diodes", "valves", "forges", "mixers", "wedges"],
        ),
        0.1,
    ),
    (
        (
            ["diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            ["fibers", "anchor", "hanger", "orbit", "yokes", "furnace"],
        ),
        0.083333,
    ),
    (
        (
            ["engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["helix", "cranes", "jets", "quarry", "asphalt", "cables", "joints"],
        ),
        0.071429,
    ),
    (
        (
            ["fibers", "ingots", "welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            ["joints", "exits", "lifts", "shafts", "copper", "engine", "welder", "gantry"],
        ),
        0.133333,
    ),
    (
        (
            ["gears", "joints", "anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["welder", "gantry", "nozzles", "xenons", "enamel", "gears", "bolts", "intake", "pumps"],
        ),
        0.1875,
    ),
    (
        (
            [
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
            ],
            ["bolts", "intake", "pumps", "zincs", "bridge", "ingots", "drills", "keels", "rivets", "beacon"],
        ),
        0.166667,
    ),
    (
        (
            [
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
            ],
            [
                "drills",
                "keels",
                "rivets",
                "beacon",
                "diodes",
                "valves",
                "forges",
                "mixers",
                "wedges",
                "diesel",
                "fibers",
            ],
        ),
        0.15,
    ),
    (
        (
            ["joints", "anchor", "drills", "gantry", "jets"],
            [
                "forges",
                "mixers",
                "wedges",
                "diesel",
                "fibers",
                "anchor",
                "hanger",
                "orbit",
                "yokes",
                "furnace",
                "helix",
                "cranes",
            ],
        ),
        0.0625,
    ),
    ((["valves", "bolts", "exits", "hanger", "keels", "nozzles"], ["hanger", "orbit", "yokes", "furnace"]), 0.111111),
    (
        (
            ["welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            ["jets", "quarry", "asphalt", "cables", "joints"],
        ),
        0.0,
    ),
    (
        (
            ["anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["lifts", "shafts", "copper", "engine", "welder", "gantry"],
        ),
        0.166667,
    ),
    (
        (
            ["bolts", "exits", "hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            ["nozzles", "xenons", "enamel", "gears", "bolts", "intake", "pumps"],
        ),
        0.142857,
    ),
    (
        (
            ["cranes", "forges", "intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["pumps", "zincs", "bridge", "ingots", "drills", "keels", "rivets", "beacon"],
        ),
        0.125,
    ),
    (
        (
            [
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
            ],
            ["rivets", "beacon", "diodes", "valves", "forges", "mixers", "wedges", "diesel", "fibers"],
        ),
        0.176471,
    ),
    (
        (
            [
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
            ],
            ["wedges", "diesel", "fibers", "anchor", "hanger", "orbit", "yokes", "furnace", "helix", "cranes"],
        ),
        0.157895,
    ),
    (
        (
            ["forges", "intake", "lifts", "orbit", "rivets"],
            [
                "yokes",
                "furnace",
                "helix",
                "cranes",
                "jets",
                "quarry",
                "asphalt",
                "cables",
                "joints",
                "exits",
                "lifts",
            ],
        ),
        0.066667,
    ),
    (
        (
            ["gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            [
                "asphalt",
                "cables",
                "joints",
                "exits",
                "lifts",
                "shafts",
                "copper",
                "engine",
                "welder",
                "gantry",
                "nozzles",
                "xenons",
            ],
        ),
        0.125,
    ),
    (
        (
            ["hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            ["copper", "engine", "welder", "gantry"],
        ),
        0.1,
    ),
    (
        (
            ["intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["enamel", "gears", "bolts", "intake", "pumps"],
        ),
        0.083333,
    ),
    (
        (
            ["jets", "mixers", "pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            ["bridge", "ingots", "drills", "keels", "rivets", "beacon"],
        ),
        0.071429,
    ),
    (
        (
            ["keels", "nozzles", "quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["diodes", "valves", "forges", "mixers", "wedges", "diesel", "fibers"],
        ),
        0.133333,
    ),
    (
        (
            [
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
            ],
            ["fibers", "anchor", "hanger", "orbit", "yokes", "furnace", "helix", "cranes"],
        ),
        0.117647,
    ),
    (
        (
            [
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
            ],
            ["helix", "cranes", "jets", "quarry", "asphalt", "cables", "joints", "exits", "lifts"],
        ),
        0.105263,
    ),
    (
        (
            ["nozzles", "quarry", "wedges", "zincs", "copper"],
            ["joints", "exits", "lifts", "shafts", "copper", "engine", "welder", "gantry", "nozzles", "xenons"],
        ),
        0.153846,
    ),
    (
        (
            ["orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            [
                "welder",
                "gantry",
                "nozzles",
                "xenons",
                "enamel",
                "gears",
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
            ],
        ),
        0.133333,
    ),
    (
        (
            ["pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            [
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
                "keels",
                "rivets",
                "beacon",
                "diodes",
                "valves",
            ],
        ),
        0.117647,
    ),
    (
        (
            ["quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["drills", "keels", "rivets", "beacon"],
        ),
        0.0,
    ),
    (
        (
            ["rivets", "xenons", "asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            ["forges", "mixers", "wedges", "diesel", "fibers"],
        ),
        0.076923,
    ),
    (
        (
            ["shafts", "yokes", "beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["hanger", "orbit", "yokes", "furnace", "helix", "cranes"],
        ),
        0.142857,
    ),
    (
        (
            [
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
            ],
            ["jets", "quarry", "asphalt", "cables", "joints", "exits", "lifts"],
        ),
        0.125,
    ),
    (
        (
            [
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
            ],
            ["lifts", "shafts", "copper", "engine", "welder", "gantry", "nozzles", "xenons"],
        ),
        0.176471,
    ),
    (
        (
            ["yokes", "beacon", "enamel", "cables", "fibers"],
            ["nozzles", "xenons", "enamel", "gears", "bolts", "intake", "pumps", "zincs", "bridge"],
        ),
        0.076923,
    ),
    (
        (
            ["zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["pumps", "zincs", "bridge", "ingots", "drills", "keels", "rivets", "beacon", "diodes", "valves"],
        ),
        0.142857,
    ),
    (
        (
            ["asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            [
                "rivets",
                "beacon",
                "diodes",
                "valves",
                "forges",
                "mixers",
                "wedges",
                "diesel",
                "fibers",
                "anchor",
                "hanger",
            ],
        ),
        0.125,
    ),
    (
        (
            ["beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            [
                "wedges",
                "diesel",
                "fibers",
                "anchor",
                "hanger",
                "orbit",
                "yokes",
                "furnace",
                "helix",
                "cranes",
                "jets",
                "quarry",
            ],
        ),
        0.111111,
    ),
    (
        (
            ["copper", "furnace", "diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            ["yokes", "furnace", "helix", "cranes"],
        ),
        0.083333,
    ),
    (
        (
            ["diesel", "bridge", "engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["asphalt", "cables", "joints", "exits", "lifts"],
        ),
        0.071429,
    ),
    (
        (
            [
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
            ],
            ["copper", "engine", "welder", "gantry", "nozzles", "xenons"],
        ),
        0.0625,
    ),
    (
        (
            [
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
            ],
            ["enamel", "gears", "bolts", "intake", "pumps", "zincs", "bridge"],
        ),
        0.117647,
    ),
    (
        (
            ["bridge", "engine", "helix", "valves", "bolts"],
            ["bridge", "ingots", "drills", "keels", "rivets", "beacon", "diodes", "valves"],
        ),
        0.181818,
    ),
    (
        (
            ["cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["diodes", "valves", "forges", "mixers", "wedges", "diesel", "fibers", "anchor", "hanger"],
        ),
        0.153846,
    ),
    (
        (
            ["diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            ["fibers", "anchor", "hanger", "orbit", "yokes", "furnace", "helix", "cranes", "jets", "quarry"],
        ),
        0.133333,
    ),
    (
        (
            ["engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            [
                "helix",
                "cranes",
                "jets",
                "quarry",
                "asphalt",
                "cables",
                "joints",
                "exits",
                "lifts",
                "shafts",
                "copper",
            ],
        ),
        0.117647,
    ),
    (
        (
            ["fibers", "ingots", "welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            [
                "joints",
                "exits",
                "lifts",
                "shafts",
                "copper",
                "engine",
                "welder",
                "gantry",
                "nozzles",
                "xenons",
                "enamel",
                "gears",
            ],
        ),
        0.105263,
    ),
    (
        (
            ["gears", "joints", "anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["welder", "gantry", "nozzles", "xenons"],
        ),
        0.076923,
    ),
    (
        (
            [
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
            ],
            ["bolts", "intake", "pumps", "zincs", "bridge"],
        ),
        0.142857,
    ),
    (
        (
            [
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
            ],
            ["drills", "keels", "rivets", "beacon", "diodes", "valves"],
        ),
        0.058824,
    ),
    (
        (
            ["joints", "anchor", "drills", "gantry", "jets"],
            ["forges", "mixers", "wedges", "diesel", "fibers", "anchor", "hanger"],
        ),
        0.090909,
    ),
    (
        (
            ["valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["hanger", "orbit", "yokes", "furnace", "helix", "cranes", "jets", "quarry"],
        ),
        0.076923,
    ),
    (
        (
            ["welder", "cranes", "forges", "intake", "lifts", "orbit", "rivets"],
            ["jets", "quarry", "asphalt", "cables", "joints", "exits", "lifts", "shafts", "copper"],
        ),
        0.066667,
    ),
    (
        (
            ["anchor", "drills", "gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["lifts", "shafts", "copper", "engine", "welder", "gantry", "nozzles", "xenons", "enamel", "gears"],
        ),
        0.125,
    ),
    (
        (
            ["bolts", "exits", "hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            [
                "nozzles",
                "xenons",
                "enamel",
                "gears",
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
            ],
        ),
        0.176471,
    ),
    (
        (
            ["cranes", "forges", "intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            [
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
                "keels",
                "rivets",
                "beacon",
                "diodes",
                "valves",
                "forges",
                "mixers",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
            ],
            ["rivets", "beacon", "diodes", "valves"],
        ),
        0.071429,
    ),
    (
        (
            [
                "exits",
                "hanger",
                "keels",
                "nozzles",
                "quarry",
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
            ],
            ["wedges", "diesel", "fibers", "anchor", "hanger"],
        ),
        0.133333,
    ),
    (
        (
            ["forges", "intake", "lifts", "orbit", "rivets"],
            ["yokes", "furnace", "helix", "cranes", "jets", "quarry"],
        ),
        0.0,
    ),
    (
        (
            ["gantry", "jets", "mixers", "pumps", "shafts", "yokes"],
            ["asphalt", "cables", "joints", "exits", "lifts", "shafts", "copper"],
        ),
        0.083333,
    ),
    (
        (
            ["hanger", "keels", "nozzles", "quarry", "wedges", "zincs", "copper"],
            ["copper", "engine", "welder", "gantry", "nozzles", "xenons", "enamel", "gears"],
        ),
        0.153846,
    ),
    (
        (
            ["intake", "lifts", "orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["enamel", "gears", "bolts", "intake", "pumps", "zincs", "bridge", "ingots", "drills"],
        ),
        0.133333,
    ),
    (
        (
            ["jets", "mixers", "pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            ["bridge", "ingots", "drills", "keels", "rivets", "beacon", "diodes", "valves", "forges", "mixers"],
        ),
        0.117647,
    ),
    (
        (
            ["keels", "nozzles", "quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            [
                "diodes",
                "valves",
                "forges",
                "mixers",
                "wedges",
                "diesel",
                "fibers",
                "anchor",
                "hanger",
                "orbit",
                "yokes",
            ],
        ),
        0.105263,
    ),
    (
        (
            [
                "lifts",
                "orbit",
                "rivets",
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
            ],
            [
                "fibers",
                "anchor",
                "hanger",
                "orbit",
                "yokes",
                "furnace",
                "helix",
                "cranes",
                "jets",
                "quarry",
                "asphalt",
                "cables",
            ],
        ),
        0.15,
    ),
    (
        (
            [
                "mixers",
                "pumps",
                "shafts",
                "yokes",
                "beacon",
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
            ],
            ["helix", "cranes", "jets", "quarry"],
        ),
        0.066667,
    ),
    ((["nozzles", "quarry", "wedges", "zincs", "copper"], ["joints", "exits", "lifts", "shafts", "copper"]), 0.111111),
    (
        (
            ["orbit", "rivets", "xenons", "asphalt", "diesel", "bridge"],
            ["welder", "gantry", "nozzles", "xenons", "enamel", "gears"],
        ),
        0.090909,
    ),
    (
        (
            ["pumps", "shafts", "yokes", "beacon", "enamel", "cables", "fibers"],
            ["bolts", "intake", "pumps", "zincs", "bridge", "ingots", "drills"],
        ),
        0.076923,
    ),
    (
        (
            ["quarry", "wedges", "zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["drills", "keels", "rivets", "beacon", "diodes", "valves", "forges", "mixers"],
        ),
        0.066667,
    ),
    (
        (
            ["rivets", "xenons", "asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            ["forges", "mixers", "wedges", "diesel", "fibers", "anchor", "hanger", "orbit", "yokes"],
        ),
        0.058824,
    ),
    (
        (
            ["shafts", "yokes", "beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["hanger", "orbit", "yokes", "furnace", "helix", "cranes", "jets", "quarry", "asphalt", "cables"],
        ),
        0.176471,
    ),
    (
        (
            [
                "wedges",
                "zincs",
                "copper",
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
            ],
            [
                "jets",
                "quarry",
                "asphalt",
                "cables",
                "joints",
                "exits",
                "lifts",
                "shafts",
                "copper",
                "engine",
                "welder",
            ],
        ),
        0.157895,
    ),
    (
        (
            [
                "xenons",
                "asphalt",
                "diesel",
                "bridge",
                "engine",
                "helix",
                "valves",
                "bolts",
                "exits",
                "hanger",
                "keels",
                "nozzles",
            ],
            [
                "lifts",
                "shafts",
                "copper",
                "engine",
                "welder",
                "gantry",
                "nozzles",
                "xenons",
                "enamel",
                "gears",
                "bolts",
                "intake",
            ],
        ),
        0.2,
    ),
    ((["yokes", "beacon", "enamel", "cables", "fibers"], ["nozzles", "xenons", "enamel", "gears"]), 0.125),
    (
        (
            ["zincs", "copper", "furnace", "diodes", "gears", "joints"],
            ["pumps", "zincs", "bridge", "ingots", "drills"],
        ),
        0.1,
    ),
    (
        (
            ["asphalt", "diesel", "bridge", "engine", "helix", "valves", "bolts"],
            ["rivets", "beacon", "diodes", "valves", "forges", "mixers"],
        ),
        0.083333,
    ),
    (
        (
            ["beacon", "enamel", "cables", "fibers", "ingots", "welder", "cranes", "forges"],
            ["wedges", "diesel", "fibers", "anchor", "hanger", "orbit", "yokes"],
        ),
        0.071429,
    ),
    (
        (
            ["copper", "furnace", "diodes", "gears", "joints", "anchor", "drills", "gantry", "jets"],
            ["yokes", "furnace", "helix", "cranes", "jets", "quarry", "asphalt", "cables"],
        ),
        0.133333,
    ),
    (
        (
            ["diesel", "bridge", "engine", "helix", "valves", "bolts", "exits", "hanger", "keels", "nozzles"],
            ["asphalt", "cables", "joints", "exits", "lifts", "shafts", "copper", "engine", "welder"],
        ),
        0.117647,
    ),
    (
        (
            [
                "enamel",
                "cables",
                "fibers",
                "ingots",
                "welder",
                "cranes",
                "forges",
                "intake",
                "lifts",
                "orbit",
                "rivets",
            ],
            ["copper", "engine", "welder", "gantry", "nozzles", "xenons", "enamel", "gears", "bolts", "intake"],
        ),
        0.166667,
    ),
    (
        (
            [
                "furnace",
                "diodes",
                "gears",
                "joints",
                "anchor",
                "drills",
                "gantry",
                "jets",
                "mixers",
                "pumps",
                "shafts",
                "yokes",
            ],
            [
                "enamel",
                "gears",
                "bolts",
                "intake",
                "pumps",
                "zincs",
                "bridge",
                "ingots",
                "drills",
                "keels",
                "rivets",
            ],
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
