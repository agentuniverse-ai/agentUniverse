"""Server-sent events parser: deterministic known-answer vectors (auext)."""

def _ref_sse_parse(case):
    """Parse a Server-Sent Events text into event dictionaries.

    Fields: event (default "message"), joined data, optional id and retry.
    Colons start comments; unknown fields and values are ignored.
    """
    events = []
    cur = {}
    datas = []
    has_data = False

    def flush():
        if not (has_data or cur):
            return
        ev = {"event": cur.get("event", "message"), "data": "\n".join(datas)}
        if "id" in cur:
            ev["id"] = cur["id"]
        if "retry" in cur:
            ev["retry"] = cur["retry"]
        events.append(ev)

    for line in case.split("\n"):
        if line == "":
            flush()
            cur = {}
            datas = []
            has_data = False
        elif line.startswith(":"):
            continue
        else:
            if ":" in line:
                key, _, val = line.partition(":")
                if val.startswith(" "):
                    val = val[1:]
            else:
                key, val = line, ""
            if key == "data":
                datas.append(val)
                has_data = True
            elif key == "event":
                cur["event"] = val
            elif key == "id":
                cur["id"] = val
            elif key == "retry":
                if val.isdigit():
                    cur["retry"] = int(val)
    flush()
    return events

_CASES = [
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\n",
        [{"event": "message", "data": "nospace"}, {"event": "message", "data": "spaced "}],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    ("data: multi\nmore\ndata: here\n\n", [{"event": "message", "data": "multi\nhere"}]),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\n",
        [{"event": "message", "data": "line1\nline2"}, {"event": "message", "data": "end"}],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [{"event": "message", "data": "p", "id": "1"}, {"event": "message", "data": "q", "id": "2"}],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\n", [{"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    ("event: e\ndata: 1\n\n", [{"event": "e", "data": "1"}]),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    ("event: x\ndata: 3\nretry: 999\n\n", [{"event": "x", "data": "3", "retry": 999}]),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    ("retry: 3000\ndata: x\n\n", [{"event": "message", "data": "x", "retry": 3000}]),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    ("data: no-trailing-newline", [{"event": "message", "data": "no-trailing-newline"}]),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    ("event: add\ndata: 7\n\nid: 3\n\n", [{"event": "add", "data": "7"}, {"event": "message", "data": "", "id": "3"}]),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    ("no-colon\n\ndata: after\n\n", [{"event": "message", "data": "after"}]),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    ("unknown: 9\ndata: z\n\n", [{"event": "message", "data": "z"}]),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    ("data: 1\n\n\n\n\n", [{"event": "message", "data": "1"}]),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    ("data: a\n\n\ndata: b\n\n\n\n", [{"event": "message", "data": "a"}, {"event": "message", "data": "b"}]),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (":1\n:2\ndata: c\n\n", [{"event": "message", "data": "c"}]),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\n",
        [{"event": "message", "data": "nospace"}, {"event": "message", "data": "spaced "}],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    ("data: multi\nmore\ndata: here\n\n", [{"event": "message", "data": "multi\nhere"}]),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\n",
        [{"event": "message", "data": "line1\nline2"}, {"event": "message", "data": "end"}],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [{"event": "message", "data": "p", "id": "1"}, {"event": "message", "data": "q", "id": "2"}],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\n", [{"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    ("event: e\ndata: 1\n\n", [{"event": "e", "data": "1"}]),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    ("event: x\ndata: 3\nretry: 999\n\n", [{"event": "x", "data": "3", "retry": 999}]),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    ("retry: 3000\ndata: x\n\n", [{"event": "message", "data": "x", "retry": 3000}]),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    ("data: no-trailing-newline", [{"event": "message", "data": "no-trailing-newline"}]),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    ("event: add\ndata: 7\n\nid: 3\n\n", [{"event": "add", "data": "7"}, {"event": "message", "data": "", "id": "3"}]),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    ("no-colon\n\ndata: after\n\n", [{"event": "message", "data": "after"}]),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    ("unknown: 9\ndata: z\n\n", [{"event": "message", "data": "z"}]),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    ("data: 1\n\n\n\n\n", [{"event": "message", "data": "1"}]),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\ndata:nospace\n\ndata: spaced \n\n",
        [
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
            {
                "event": "message",
                "data": "nospace",
            },
            {
                "event": "message",
                "data": "spaced ",
            },
        ],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    ("data: a\n\n\ndata: b\n\n\n\n", [{"event": "message", "data": "a"}, {"event": "message", "data": "b"}]),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    (
        "data: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\ndata: multi\nmore\ndata: here\n\n",
        [
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
            {
                "event": "message",
                "data": "multi\nhere",
            },
        ],
    ),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (":1\n:2\ndata: c\n\n", [{"event": "message", "data": "c"}]),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n:only\n\n:only\n\n", []),
    ("data: hello\n\ndata: world\n\n", [{"event": "message", "data": "hello"}, {"event": "message", "data": "world"}]),
    ("event: add\ndata: 7\n\nevent: add\ndata: 7\n\n", [{"event": "add", "data": "7"}, {"event": "add", "data": "7"}]),
    (
        "event: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\nevent: add\ndata: 7\n\nid: 3\n\n",
        [
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
            {
                "event": "add",
                "data": "7",
            },
            {
                "event": "message",
                "data": "",
                "id": "3",
            },
        ],
    ),
    (":comment\ndata: keep\n\n", [{"event": "message", "data": "keep"}]),
    (
        "data: line1\ndata: line2\n\ndata: end\n\ndata: line1\ndata: line2\n\ndata: end\n\n",
        [
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
            {
                "event": "message",
                "data": "line1\nline2",
            },
            {
                "event": "message",
                "data": "end",
            },
        ],
    ),
    (
        "retry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\nretry: 3000\ndata: x\n\n",
        [
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
            {
                "event": "message",
                "data": "x",
                "retry": 3000,
            },
        ],
    ),
    ("retry: 30x\ndata: y\n\n", [{"event": "message", "data": "y"}]),
    (
        "data:nospace\n\ndata: spaced \n\n",
        [{"event": "message", "data": "nospace"}, {"event": "message", "data": "spaced "}],
    ),
    (
        "event: e\ndata: 1\n\nevent: e\ndata: 1\n\nevent: e\ndata: 1\n\n",
        [{"event": "e", "data": "1"}, {"event": "e", "data": "1"}, {"event": "e", "data": "1"}],
    ),
    ("data: 1\n\nevent: stop\n\n", [{"event": "message", "data": "1"}, {"event": "stop", "data": ""}]),
    (
        "data: a\n\n\ndata: b\n\n\n\ndata: a\n\n\ndata: b\n\n\n\n",
        [
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
            {
                "event": "message",
                "data": "a",
            },
            {
                "event": "message",
                "data": "b",
            },
        ],
    ),
    (
        "id: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\nid: 1\ndata: p\n\nid: 2\ndata: q\n\n",
        [
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
            {
                "event": "message",
                "data": "p",
                "id": "1",
            },
            {
                "event": "message",
                "data": "q",
                "id": "2",
            },
        ],
    ),
    ("data: \n\n", [{"event": "message", "data": ""}]),
    (
        "unknown: 9\ndata: z\n\nunknown: 9\ndata: z\n\n",
        [{"event": "message", "data": "z"}, {"event": "message", "data": "z"}],
    ),
    ("data: multi\nmore\ndata: here\n\n", [{"event": "message", "data": "multi\nhere"}]),
    ("event:\ndata:\n\n", [{"event": "", "data": ""}]),
    (
        "no-colon\n\ndata: after\n\nno-colon\n\ndata: after\n\n",
        [{"event": "message", "data": "after"}, {"event": "message", "data": "after"}],
    ),
    (
        ":1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n:1\n:2\ndata: c\n\n",
        [
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
            {
                "event": "message",
                "data": "c",
            },
        ],
    ),
    (
        "event: b\ndata: 1\nid: 7\nretry: 250\n\ndata: 2\n\n",
        [{"event": "b", "data": "1", "id": "7", "retry": 250}, {"event": "message", "data": "2"}],
    ),
    (
        "data: no-trailing-newlinedata: no-trailing-newline",
        [{"event": "message", "data": "no-trailing-newlinedata: no-trailing-newline"}],
    ),
    (
        "data: 1\n\n\n\n\ndata: 1\n\n\n\n\ndata: 1\n\n\n\n\n",
        [
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
            {
                "event": "message",
                "data": "1",
            },
        ],
    ),
    ("id: 9\n\n", [{"event": "message", "data": "", "id": "9"}]),
    (
        "event: x\ndata: 3\nretry: 999\n\nevent: x\ndata: 3\nretry: 999\n\n",
        [{"event": "x", "data": "3", "retry": 999}, {"event": "x", "data": "3", "retry": 999}],
    ),
    (":only\n\n:only\n\n:only\n\n", []),
]

_EXPECTED_COUNT = 360

def test_vector_count_frozen():
    """The vector table size is part of the frozen contract."""
    assert len(_CASES) == _EXPECTED_COUNT

def test_vectors_000():
    """Known-answer vectors 0..119."""
    for case, expected in _CASES[0:120]:
        assert _ref_sse_parse(case) == expected

def test_vectors_120():
    """Known-answer vectors 120..239."""
    for case, expected in _CASES[120:240]:
        assert _ref_sse_parse(case) == expected

def test_vectors_240():
    """Known-answer vectors 240..359."""
    for case, expected in _CASES[240:360]:
        assert _ref_sse_parse(case) == expected

def test_repeat_head_stable():
    """Head vectors return identical results on repeated calls."""
    for case, expected in _CASES[:64]:
        assert _ref_sse_parse(case) == expected
        assert _ref_sse_parse(case) == expected

def test_repeat_tail_stable():
    """Tail vectors return identical results on repeated calls."""
    for case, expected in _CASES[-64:]:
        assert _ref_sse_parse(case) == expected
        assert _ref_sse_parse(case) == expected
