#!/usr/bin/env python3
"""ANSI escape sequence analysis for terminal output processing.

The tool implements the ECMA-48 §5.4 control-function grammar plus the xterm
ctlseqs extensions with a hand-rolled state machine.  Each grammar state
(CSI parameter run, intermediate run, final byte, OSC body, string data) is
scanned with a per-state character-class run, so parsing is linear in the
input size and never re-scans bytes.

Design notes / documented deterministic rules:

* Bare C0 controls outside sequences (``\\r``, ``\\n``, ``\\t``, BEL ...) are
  preserved: they belong to the text layer (progress bars rely on ``\\r``),
  not to the ECMA-48 escape layer this tool targets.
* OSC runs are terminated by BEL or ST (``ESC \\`` / U+009C).  A DCS / SOS /
  PM / APC run is terminated by ST only (BEL is data, per xterm).
* An OSC run that reaches EOF without a terminator is consumed to EOF and
  flagged ``truncated_at_eof`` (documented: consume to EOF + flag).
* A CSI / escape run abandoned by ESC, a C1 introducer, or any byte outside
  its grammar class is removed as ``invalid``; the scan resumes at the
  offending byte, so plain text following a malformed run survives.
* 8-bit C1 introducers (U+0090/U+0098/U+009B/U+009D/U+009E/U+009F) are
  parsed per grammar when they form a complete control function.  A C1
  introducer that cannot complete a sequence is treated as a literal text
  character (kept) because C1 bytes cannot legally occur inside UTF-8 and
  usually indicate mojibake; the result carries ``c1_8bit_detected`` and an
  info note about non-UTF-8-safe contexts.
* ``sanitize`` re-emits kept sequences as their original input slice, so
  kept sequences are byte-preserved (canonical passthrough, no rewriting).
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import re
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

_ESC = "\x1b"
_BEL = "\x07"

# C1 control functions (ECMA-48 8-bit forms).  U+009C is ST, the terminator.
_C1_DCS, _C1_SOS, _C1_CSI, _C1_OSC, _C1_PM, _C1_APC = "\x90", "\x98", "\x9b", "\x9d", "\x9e", "\x9f"
_C1_ST = "\x9c"
_C1_INTRODUCERS = frozenset({_C1_DCS, _C1_SOS, _C1_CSI, _C1_OSC, _C1_PM, _C1_APC})

_STR_TYPES = {"P": "dcs", "X": "sos", "^": "pm", "_": "apc"}
_C1_STR_TYPES = {_C1_DCS: "dcs", _C1_SOS: "sos", _C1_PM: "pm", _C1_APC: "apc"}

# Per-state character-class runs (each regex implements one grammar state).
_RE_CTRL = re.compile("[\x1b\x90\x98\x9b\x9c\x9d\x9e\x9f]")
_RE_CSI = re.compile("\x1b\\[([0-9:;<=>?]*)([ -/]*)([@-~])?")
_RE_C1_CSI = re.compile("\x9b([0-9:;<=>?]*)([ -/]*)([@-~])?")
_RE_OSC = re.compile("\x1b\\]([^\x07\x1b\x90\x98\x9b\x9c\x9d\x9e\x9f]*)")
_RE_C1_OSC = re.compile("\x9d([^\x07\x1b\x90\x98\x9b\x9c\x9d\x9e\x9f]*)")
_RE_STR = re.compile("\x1b([PX^_])([^\x1b\x90\x98\x9b\x9c\x9d\x9e\x9f]*)")
_RE_C1_STR = re.compile("([\x90\x98\x9e\x9f])([^\x1b\x90\x98\x9b\x9c\x9d\x9e\x9f]*)")
_RE_ESC = re.compile("\x1b([ -/]*)([0-~])?")

# CSI final-byte groups (cursor/erase/scroll handled before this fallback).
_CURSOR_FINALS = frozenset("ABCDEFGH`adeufsZ")
_ERASE_FINALS = frozenset("JKX")
_SCROLL_FINALS = frozenset("STrLM")
_MODE_FINALS = frozenset("hl")

_BASIC_FG = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]
_SGR_SIMPLE = {
    0: "Reset all attributes (0)",
    1: "Set bold (1)",
    2: "Set dim/faint (2)",
    3: "Set italic (3)",
    4: "Set underline (4)",
    5: "Set slow blink (5)",
    6: "Set rapid blink (6)",
    7: "Set reverse video (7)",
    8: "Set conceal/hidden (8)",
    9: "Set crossed-out (9)",
    22: "Normal intensity, not bold or dim (22)",
    23: "Not italic (23)",
    24: "Not underlined (24)",
    25: "Not blinking (25)",
    27: "Not reversed (27)",
    28: "Reveal, not concealed (28)",
    29: "Not crossed out (29)",
    39: "Set default foreground color (39)",
    49: "Set default background color (49)",
    59: "Set default underline color (59)",
}

_DEC_MODES = {
    1: ("Enable application cursor keys (DECCKM ?1)", "Disable application cursor keys (DECCKM ?1)"),
    7: ("Enable autowrap (DECAWM ?7)", "Disable autowrap (DECAWM ?7)"),
    25: ("Show cursor (DECTCEM ?25 set)", "Hide cursor (DECTCEM ?25 reset)"),
    47: ("Switch to alternate screen buffer (DEC ?47)", "Switch back to primary screen buffer (DEC ?47)"),
    1000: ("Enable X10 mouse reporting (?1000)", "Disable X10 mouse reporting (?1000)"),
    1002: ("Enable button-event mouse tracking (?1002)", "Disable button-event mouse tracking (?1002)"),
    1003: ("Enable any-event mouse tracking (?1003)", "Disable any-event mouse tracking (?1003)"),
    1005: ("Enable UTF-8 extended mouse mode (?1005)", "Disable UTF-8 extended mouse mode (?1005)"),
    1006: ("Enable SGR extended mouse mode (?1006)", "Disable SGR extended mouse mode (?1006)"),
    1015: ("Enable urxvt extended mouse mode (?1015)", "Disable urxvt extended mouse mode (?1015)"),
    1047: ("Switch to alternate screen buffer (DEC ?1047)", "Switch back to primary screen buffer (DEC ?1047)"),
    1049: (
        "Switch to alternate screen buffer with cursor save (DEC ?1049)",
        "Switch back to primary screen buffer restoring cursor (DEC ?1049)",
    ),
    2004: ("Enable bracketed paste mode (DEC ?2004)", "Disable bracketed paste mode (DEC ?2004)"),
}
_ANSI_MODES = {
    4: ("Set insert mode (IRM 4)", "Reset insert mode, replace (IRM 4)"),
    20: ("Set newline mode (LNM 20)", "Reset newline mode (LNM 20)"),
}

_DECSCUSR = {
    0: "blinking block",
    1: "blinking block",
    2: "steady block",
    3: "blinking underline",
    4: "steady underline",
    5: "blinking bar",
    6: "steady bar",
}

_C1_NOTE = (
    "8-bit C1 control characters detected; they are not UTF-8-safe (a C1 code "
    "in UTF-8 text usually indicates latin-1 decoding or mojibake); terminals "
    "in UTF-8 mode ignore the 8-bit forms, prefer the 7-bit ESC sequences"
)
_STRAY_ESC_NOTE = "stray ESC byte kept as literal text (no valid escape followed)"
_OSC_EOF_NOTE = "unterminated OSC run consumed to end of input (no BEL/ST terminator found)"


def _bounded(value: str, limit: int) -> str:
    """Return the string capped to the given length."""
    return value if len(value) <= limit else value[:limit]


def _ints(params: str) -> list[int | None]:
    """Split a CSI parameter string into integers, empty parts as None."""
    if not params:
        return []
    out: list[int | None] = []
    for part in params.lstrip("<=>?").split(";"):
        head = part.split(":", 1)[0]
        out.append(int(head) if head.isdigit() else None)
    return out


def _num(values: list[int | None], index: int, default: int) -> int:
    """Return the 1-based numeric parameter at index or the default."""
    if index < len(values) and values[index] is not None:
        return values[index]
    return default


def _idx_color(index: int) -> str:
    """Describe xterm 256-palette index 0-255 (names, cube, grayscale)."""
    if index < 0 or index > 255:
        return f"index {index} (out of range)"
    if index < 8:
        return _BASIC_FG[index]
    if index < 16:
        return f"bright {_BASIC_FG[index - 8]}"
    if index < 232:
        n = index - 16
        r, rest = divmod(n, 36)
        g, b = divmod(rest, 6)
        chan = lambda v: 0 if v == 0 else 55 + 40 * v
        return f"RGB {chan(r)},{chan(g)},{chan(b)} (color cube)"
    v = 8 + 10 * (index - 232)
    return f"RGB {v},{v},{v} (grayscale)"


class _Scan:
    """One linear scan over the input producing grammar events."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.events: list[dict[str, Any]] = []
        self.truncated_at_eof = False
        self.pending_start: int | None = None
        self.c1_detected = False
        self.stray_escapes = 0
        self.invalid_runs = 0
        self.incomplete_runs = 0
        self.osc_eof_runs = 0

    # -- event helpers -------------------------------------------------
    def _text(self, start: int, end: int) -> None:
        if end > start:
            self.events.append({"kind": "text", "start": start, "end": end})

    def _seq(self, token: dict[str, Any]) -> None:
        self.events.append(token)

    def _bad(self, start: int, end: int, reason: str) -> None:
        self.events.append({"kind": "bad", "start": start, "end": end, "reason": reason})
        if reason == "incomplete":
            self.incomplete_runs += 1
        else:
            self.invalid_runs += 1

    def _incomplete_at_eof(self, start: int, osc_eof: bool) -> None:
        self._bad(start, len(self.text), "incomplete")
        self.truncated_at_eof = True
        self.pending_start = start
        if osc_eof:
            self.osc_eof_runs += 1

    # -- state machine -------------------------------------------------
    def run(self) -> "_Scan":
        text, n = self.text, len(self.text)
        i = 0
        while i < n:
            m = _RE_CTRL.search(text, i)
            if m is None:
                self._text(i, n)
                break
            if m.start() > i:
                self._text(i, m.start())
            i = m.start()
            ch = text[i]
            if ch == _ESC:
                i = self._scan_esc(i)
            elif ch == _C1_ST:
                # A stray ST with nothing to terminate: keep as literal text.
                self.c1_detected = True
                self._text(i, i + 1)
                i += 1
            else:
                i = self._scan_c1(i)
        return self

    def _scan_esc(self, i: int) -> int:
        """Scan an escape sequence introduced by a 7-bit ESC at i."""
        text, n = self.text, len(self.text)
        nxt = i + 1
        if nxt >= n:
            self._incomplete_at_eof(i, osc_eof=False)
            return n
        ch = text[nxt]
        if ch == "[":
            return self._csi(i, _RE_CSI.match(self.text, i), c1=False)
        if ch == "]":
            return self._osc(i, _RE_OSC.match(self.text, i), "ESC ]", c1=False)
        if ch in _STR_TYPES:
            return self._string(i, _RE_STR.match(self.text, i), "ESC " + ch, _STR_TYPES[ch], c1=False)
        return self._simple_esc(i)

    def _scan_c1(self, i: int) -> int:
        """Scan a sequence introduced by an 8-bit C1 byte at i.

        A C1 introducer that cannot complete a control function is kept as a
        literal text character (mojibake-safe downgrade) and the scan resumes
        right after it.
        """
        text = self.text
        ch = text[i]
        self.c1_detected = True
        if ch == _C1_CSI:
            nxt = self._csi(i, _RE_C1_CSI.match(text, i), c1=True)
            if nxt < 0:
                self._text(i, i + 1)
                return i + 1
            return nxt
        if ch == _C1_OSC:
            nxt = self._osc(i, _RE_C1_OSC.match(text, i), "C1 OSC (U+009D)", c1=True)
            if nxt < 0:
                self._text(i, i + 1)
                return i + 1
            return nxt
        stype = _C1_STR_TYPES.get(ch)
        if stype is not None:
            nxt = self._string(i, _RE_C1_STR.match(text, i), "C1 " + stype.upper(), stype, c1=True)
            if nxt < 0:
                self._text(i, i + 1)
                return i + 1
            return nxt
        self._text(i, i + 1)
        return i + 1

    def _csi(self, i: int, m: re.Match | None, c1: bool) -> int:
        """Scan a CSI sequence starting at i; negative return means failed C1."""
        text, n = self.text, len(self.text)
        if m is None:  # pragma: no cover - introducer byte always matches
            return -1 if c1 else i + 2
        params, inters, final = m.group(1), m.group(2), m.group(3)
        if final is not None:
            self._seq(
                {
                    "kind": "csi",
                    "start": i,
                    "end": m.end(),
                    "params": params,
                    "inters": inters,
                    "final": final,
                    "c1": c1,
                }
            )
            return m.end()
        if m.end() >= n:
            if c1:
                return -1
            self._incomplete_at_eof(i, osc_eof=False)
            return n
        # Abandoned run: remove the grammar prefix, resume at the offending byte.
        if c1:
            return -1
        self._bad(i, m.end(), "invalid")
        return m.end()

    def _osc(self, i: int, m: re.Match | None, introducer: str, c1: bool) -> int:
        """Scan an OSC run (BEL / ST terminated); negative return = failed C1."""
        text, n = self.text, len(self.text)
        if m is None:  # pragma: no cover - introducer byte always matches
            return -1 if c1 else i + 2
        body, end = m.group(1), m.end()
        if end >= n:
            # Documented rule: consume to EOF and flag.
            if c1:
                return -1
            self._incomplete_at_eof(i, osc_eof=True)
            return n
        ch = text[end]
        if ch == _BEL:
            self._seq({"kind": "osc", "start": i, "end": end + 1, "body": body, "term": "bel", "c1": c1, "intro": introducer})
            return end + 1
        if ch == _ESC:
            if end + 1 < n and text[end + 1] == "\\":
                self._seq({"kind": "osc", "start": i, "end": end + 2, "body": body, "term": "st", "c1": c1, "intro": introducer})
                return end + 2
        elif ch == _C1_ST:
            self._seq({"kind": "osc", "start": i, "end": end + 1, "body": body, "term": "st", "c1": c1, "intro": introducer})
            return end + 1
        if c1:
            return -1
        self._bad(i, end, "invalid")
        return end

    def _string(self, i: int, m: re.Match | None, introducer: str, stype: str, c1: bool) -> int:
        """Scan DCS/SOS/PM/APC data (ST terminated, BEL is data)."""
        text, n = self.text, len(self.text)
        if m is None:  # pragma: no cover - introducer byte always matches
            return -1 if c1 else i + 2
        body, end = m.group(2), m.end()
        if end >= n:
            if c1:
                return -1
            self._incomplete_at_eof(i, osc_eof=False)
            return n
        ch = text[end]
        if ch == _ESC and end + 1 < n and text[end + 1] == "\\":
            self._seq({"kind": "str", "start": i, "end": end + 2, "stype": stype, "body": body, "term": "st", "c1": c1, "intro": introducer})
            return end + 2
        if ch == _C1_ST:
            self._seq({"kind": "str", "start": i, "end": end + 1, "stype": stype, "body": body, "term": "st", "c1": c1, "intro": introducer})
            return end + 1
        if c1:
            return -1
        self._bad(i, end, "invalid")
        return end

    def _simple_esc(self, i: int) -> int:
        """Scan a two-or-more-character escape (final 0x30-0x7E after ESC)."""
        text, n = self.text, len(self.text)
        m = _RE_ESC.match(text, i)
        inters, final = m.group(1), m.group(2)
        if final is not None:
            self._seq({"kind": "esc", "start": i, "end": m.end(), "inters": inters, "final": final, "c1": False})
            return m.end()
        if m.end() >= n:
            self._incomplete_at_eof(i, osc_eof=False)
            return n
        if not inters:
            # ESC followed directly by a byte outside the grammar: keep the
            # ESC itself as literal text and rescan the offending byte.
            self.stray_escapes += 1
            self._text(i, i + 1)
            return i + 1
        self._bad(i, m.end(), "invalid")
        return m.end()


def _category(token: dict[str, Any]) -> str:
    """Map a completed sequence token to its inventory category."""
    kind = token["kind"]
    if kind == "csi":
        final, inters = token["final"], token["inters"]
        if final == "m":
            return "sgr"
        if final in _MODE_FINALS:
            return "mode"
        if final in _ERASE_FINALS:
            return "erase"
        if final in _SCROLL_FINALS:
            return "scroll"
        if final == "q" and inters == " ":
            return "cursor"  # DECSCUSR cursor style
        if final in _CURSOR_FINALS:
            return "cursor"
        return "other"
    if kind == "osc":
        body = token["body"]
        cmd = body.split(";", 1)[0]
        if cmd == "8":
            return "osc-link"
        if cmd in ("0", "1", "2"):
            return "osc-title"
        return "other"
    if kind == "esc":
        if token["inters"] == "" and token["final"] in ("7", "8", "D", "M", "E"):
            return "cursor"
        return "other"
    return "other"


def _code(token: dict[str, Any]) -> str:
    """Stable per-sequence code string (final byte + parameters)."""
    kind = token["kind"]
    if kind == "csi":
        return "CSI " + token["params"] + token["inters"] + token["final"]
    if kind == "osc":
        body = token["body"]
        head = body.split(";", 1)[0]
        if head == "8":
            return "OSC 8 " + _bounded(_osc8_uri(body), 40)
        return "OSC " + (head if head.isdigit() else "data")
    if kind == "esc":
        return "ESC " + token["inters"] + token["final"]
    return token["stype"].upper() + " data"


def _osc8_uri(body: str) -> str:
    """Extract the URI from an OSC 8 body (empty string means closing link)."""
    cmd = body.split(";", 1)[0]
    rest = body[len(cmd) :]
    payload = rest[1:] if rest.startswith(";") else rest
    return payload.split(";", 1)[1] if ";" in payload else ""


def _sgr_part(part: str) -> str:
    """Human meaning of one SGR parameter (colon subparameters supported)."""
    if ":" in part:
        sub = part.split(":")
        try:
            head = int(sub[0])
        except ValueError:
            return f"Set graphic rendition {part} (unparsed subparameters)"
        if head in (38, 48, 58) and len(sub) >= 3:
            who = {38: "foreground", 48: "background", 58: "underline"}[head]
            if sub[1] == "5" and sub[2].isdigit():
                idx = int(sub[2])
                return f"Set {who} color {part} ({_idx_color(idx)})"
            if sub[1] == "2" and len(sub) >= 5 and all(s.isdigit() for s in sub[2:5]):
                r, g, b = (int(v) for v in sub[2:5])
                return f"Set {who} color {part} (RGB {r},{g},{b})"
        return f"Set graphic rendition {part} (unparsed subparameters)"
    if not part:
        return _SGR_SIMPLE[0]
    if not part.isdigit():
        return f"Set graphic rendition {part} (unparsed parameter)"
    p = int(part)
    if p in _SGR_SIMPLE:
        return _SGR_SIMPLE[p]
    if p == 10:
        return "Select primary font (10)"
    if 11 <= p <= 19:
        return f"Select alternative font {p - 10} ({p})"
    if p == 20:
        return "Select fraktur/Gothic font (20)"
    if p == 21:
        return "Set double underline (21; ECMA-48; some terminals: bold off)"
    if 30 <= p <= 37:
        return f"Set foreground color {p} ({_BASIC_FG[p - 30]})"
    if 40 <= p <= 47:
        return f"Set background color {p} ({_BASIC_FG[p - 40]})"
    if 90 <= p <= 97:
        name = "bright black (gray)" if p == 90 else f"bright {_BASIC_FG[p - 90]}"
        return f"Set foreground color {p} ({name})"
    if 100 <= p <= 107:
        name = "bright black (gray)" if p == 100 else f"bright {_BASIC_FG[p - 100]}"
        return f"Set background color {p} ({name})"
    if p in (38, 48, 58):
        who = {38: "foreground", 48: "background", 58: "underline"}[p]
        return f"Set {who} color {p} (extended color, malformed parameters)"
    return f"Set graphic rendition {p} (unassigned/proprietary)"


def _sgr_human(params: str) -> str:
    """Human meaning of a full SGR sequence, handling 38/48/58 consuming."""
    raw = params.lstrip("<=>?")
    if not raw:
        return _SGR_SIMPLE[0]
    parts = raw.split(";")
    out: list[str] = []
    i = 0
    while i < len(parts):
        part = parts[i]
        if part in ("38", "48", "58") and i + 1 < len(parts):
            who = {"38": "foreground", "48": "background", "58": "underline"}[part]
            if parts[i + 1] == "5" and i + 2 < len(parts) and parts[i + 2].isdigit():
                idx = int(parts[i + 2])
                out.append(f"Set {who} color {part};5;{idx} ({_idx_color(idx)})")
                i += 3
                continue
            if parts[i + 1] == "2" and i + 4 < len(parts) and all(p.isdigit() for p in parts[i + 2 : i + 5]):
                r, g, b = (int(v) for v in parts[i + 2 : i + 5])
                out.append(f"Set {who} color {part};2;{r};{g};{b} (RGB {r},{g},{b})")
                i += 5
                continue
        out.append(_sgr_part(part))
        i += 1
    return "; ".join(out) if out else _SGR_SIMPLE[0]


def _mode_human(params: str, set_mode: bool) -> str:
    """Human meaning for SM/RM (h/l), including DEC private modes."""
    values = _ints(params)
    private = params[:1] in ("<", "=", ">", "?")
    table = _DEC_MODES if private else _ANSI_MODES
    out: list[str] = []
    for v in values:
        if v is not None and v in table:
            out.append(table[v][0 if set_mode else 1])
        elif v is not None:
            verb = "Set" if set_mode else "Reset"
            scope = "DEC private mode" if private else "ANSI mode"
            out.append(f"{verb} {scope} {v}")
        else:
            out.append("Set/Reset mode (empty parameter)")
    return "; ".join(out) if out else "Set/Reset mode (default)"


def _osc_human(token: dict[str, Any], label: str | None = None) -> str:
    """Human meaning of an OSC run; hyperlinks get URL (and label)."""
    body = token["body"]
    cmd = body.split(";", 1)[0]
    rest = body[len(cmd) :]
    payload = rest[1:] if rest.startswith(";") else rest
    if cmd == "8":
        uri = _osc8_uri(body)
        if not uri:
            return "Close hyperlink (OSC 8 end)"
        human = f"Open hyperlink to {_bounded(uri, 60)}"
        if label:
            human += f' (label "{_bounded(label, 40)}")'
        elif label is None:
            human += " (unclosed)"
        return human
    if cmd == "0":
        return f'Set window and icon title "{_bounded(payload, 40)}" (OSC 0)'
    if cmd == "1":
        return f'Set icon name "{_bounded(payload, 40)}" (OSC 1)'
    if cmd == "2":
        return f'Set window title "{_bounded(payload, 40)}" (OSC 2)'
    if cmd == "4":
        return "Set or query palette color (OSC 4)"
    if cmd in ("10", "11"):
        return f"Set or query {'foreground' if cmd == '10' else 'background'} color (OSC {cmd})"
    if cmd == "7":
        return f"Set working directory to {_bounded(payload, 60)} (xterm OSC 7)"
    if cmd == "52":
        return "Set or read system clipboard (OSC 52)"
    if cmd == "104":
        return "Reset palette color(s) (OSC 104)"
    if cmd in ("110", "111"):
        return f"Reset default {'foreground' if cmd == '110' else 'background'} color (OSC {cmd})"
    if cmd == "133":
        return "Shell integration prompt/mark (OSC 133)"
    if cmd.isdigit():
        return f"OSC {cmd} sequence (unlisted command)"
    return "OSC sequence (non-numeric command)"


def _human(token: dict[str, Any], label: str | None = None) -> str:
    """Human-readable meaning of one completed sequence token."""
    kind = token["kind"]
    if kind == "csi":
        params, inters, final = token["params"], token["inters"], token["final"]
        values = _ints(params)
        private = params[:1] in ("<", "=", ">", "?")
        if final == "m":
            return _sgr_human(params)
        if final in ("h", "l"):
            return _mode_human(params, set_mode=final == "h")
        if final == "J":
            p = _num(values, 0, 0)
            if private:
                return f"Selectively erase display option {p} (DECSED)"
            return {
                0: "Erase display from cursor to end of screen (ED 0)",
                1: "Erase display from start of screen to cursor (ED 1)",
                2: "Erase entire display (ED 2)",
                3: "Erase entire display and scrollback buffer (ED 3, xterm)",
            }.get(p, f"Erase display option {p} (ED)")
        if final == "K":
            p = _num(values, 0, 0)
            if private:
                return f"Selectively erase line option {p} (DECSEL)"
            return {
                0: "Erase line from cursor to end of line (EL 0)",
                1: "Erase line from start of line to cursor (EL 1)",
                2: "Erase entire line (EL 2)",
            }.get(p, f"Erase line option {p} (EL)")
        if final == "X":
            return f"Erase {_num(values, 0, 1)} characters from cursor (ECH)"
        if final == "S":
            return f"Scroll display up {_num(values, 0, 1)} lines (SU)"
        if final == "T":
            return f"Scroll display down {_num(values, 0, 1)} lines (SD)"
        if final == "r":
            top, bottom = _num(values, 0, 1), _num(values, 1, 0)
            return f"Set scrolling region rows {top}-{bottom or 'end'} (DECSTBM)"
        if final == "L":
            return f"Insert {_num(values, 0, 1)} blank lines at cursor (IL)"
        if final == "M":
            return f"Delete {_num(values, 0, 1)} lines at cursor (DL)"
        if final == "A":
            return f"Cursor up {_num(values, 0, 1)} lines (CUU)"
        if final == "B":
            return f"Cursor down {_num(values, 0, 1)} lines (CUD)"
        if final == "C":
            return f"Cursor forward {_num(values, 0, 1)} columns (CUF)"
        if final == "D":
            return f"Cursor back {_num(values, 0, 1)} columns (CUB)"
        if final == "E":
            return f"Cursor next line x{_num(values, 0, 1)} (CNL)"
        if final == "F":
            return f"Cursor previous line x{_num(values, 0, 1)} (CPL)"
        if final in ("G", "`"):
            name = "CHA" if final == "G" else "HPA"
            return f"Cursor to column {_num(values, 0, 1)} ({name})"
        if final in ("H", "f"):
            return f"Cursor to row {_num(values, 0, 1)}, column {_num(values, 1, 1)} ({'CUP' if final == 'H' else 'HVP'})"
        if final == "d":
            return f"Cursor to row {_num(values, 0, 1)} (VPA)"
        if final == "e":
            return f"Cursor down {_num(values, 0, 1)} rows (VPR)"
        if final == "a":
            return f"Cursor forward {_num(values, 0, 1)} columns (HPR)"
        if final == "Z":
            return f"Cursor back {_num(values, 0, 1)} tab stops (CBT)"
        if final == "s":
            return "Save cursor position (SCOSC)"
        if final == "u":
            return "Restore cursor position (SCORC)"
        if final == "q" and inters == " ":
            style = _DECSCUSR.get(_num(values, 0, 0), "unknown style")
            return f"Set cursor style: {style} (DECSCUSR)"
        label_map = {"n": "device status report (DSR)", "c": "primary device attributes (DA)", "t": "window manipulation (xterm)", "@": "insert blank characters (ICH)", "P": "delete characters (DCH)", "g": "tab clearance (TBC)"}
        if final in label_map:
            return f"Request/perform {label_map[final]}"
        return f"CSI {params}{inters}{final or '?'} (unlisted control function)"
    if kind == "osc":
        return _osc_human(token, label)
    if kind == "esc":
        inters, final = token["inters"], token["final"]
        if inters == "":
            named = {
                "7": "Save cursor position and attributes (DECSC)",
                "8": "Restore cursor position and attributes (DECRC)",
                "D": "Index: cursor down one line, same column (IND)",
                "M": "Reverse index: cursor up one line (RI)",
                "E": "Next line: cursor down to column 1 (NEL)",
                "c": "Reset terminal to initial state (RIS)",
                "=": "Enable application keypad mode (DECKPAM)",
                ">": "Enable numeric keypad mode (DECKPnm)",
                "\\": "String terminator (ST)",
            }
            return named.get(final, f"Two-character escape ESC {final} (rare/proprietary)")
        if inters in ("(" , ")" ):
            gset = "G0" if inters == "(" else "G1"
            charset = {"B": "US-ASCII", "0": "DEC special graphics (line drawing)", "A": "UK national"}.get(final, f"charset {final}")
            return f"Select {gset} character set {final} ({charset})"
        return f"Escape ESC {inters} {final} (rare/proprietary)"
    if kind == "str":
        names = {"dcs": "Device control string data, consumed to terminator (DCS)", "sos": "Start of string data, consumed to terminator (SOS)", "pm": "Privacy message data, consumed to terminator (PM)", "apc": "Application program command data, consumed to terminator (APC)"}
        return names[token["stype"]]
    return "Unknown sequence"


def _sgr_note(params: str) -> str | None:
    """xterm-vs-ECMA-48 divergence note for SGR sequences, when relevant."""
    raw = params.lstrip("<=>?")
    parts = [p.split(":", 1)[0] for p in raw.split(";")] if raw else [""]
    try:
        values = [int(p) if p.isdigit() else None for p in parts]
    except ValueError:  # pragma: no cover - digit check guards this
        values = []
    notes = []
    if any(v in range(30, 38) or v in range(40, 48) for v in values if v is not None):
        notes.append("ECMA-48 leaves SGR color parameters uninterpreted; the color naming here follows the xterm/PC convention")
    if any(v in range(90, 98) or v in range(100, 108) for v in values if v is not None):
        notes.append("SGR 90-97/100-107 bright colors are the aixterm extension, not in ECMA-48")
    if any(v in (38, 48, 58) for v in values if v is not None):
        notes.append("SGR 38/48/58 indexed (ITU T.416) and 24-bit RGB colors postdate ECMA-48")
    if 21 in values:
        notes.append("ECMA-48 defines 21 as double underline; some terminals treat it as bold off")
    return "; ".join(notes) if notes else None


def _spec_note(token: dict[str, Any]) -> str:
    """Note where xterm and ECMA-48 differ for a sequence, '' when aligned."""
    kind = token["kind"]
    if kind == "csi":
        params, inters, final = token["params"], token["inters"], token["final"]
        private = params[:1] in ("<", "=", ">", "?")
        if final == "m":
            note = _sgr_note(params) or ""
        elif final == "X":
            note = "ECH (erase character) is an xterm extension, not in ECMA-48"
        elif final == "T":
            note = "xterm defines CSI T as scroll down (SD); some terminals (e.g. URxvt) repurpose it for mouse highlight init"
        elif final == "r":
            note = "DECSTBM scrolling regions are a DEC/xterm extension, not in ECMA-48"
        elif final in ("h", "l") and private:
            note = "DEC private modes (leading ?) are outside ECMA-48; ANSI modes 4/20 are ECMA-48 IRM/LNM"
        elif final == "J" and _num(_ints(params), 0, 0) == 3:
            note = "ED 3 (scrollback erase) is an xterm extension, not in ECMA-48"
        else:
            note = ""
    elif kind == "osc":
        notes = []
        if token["term"] == "bel":
            notes.append("ECMA-48 terminates OSC with ST only; BEL termination is an xterm/legacy convention")
        if token["body"].split(";", 1)[0] == "8":
            notes.append("OSC 8 hyperlinks are an xterm/iTerm2 extension, not part of ECMA-48")
        note = "; ".join(notes)
    elif kind == "esc":
        if token["inters"] == "" and token["final"] in ("7", "8"):
            note = "DECSC/DECRC are DEC-specific; ECMA-48-based systems use CSI s / CSI u (SCOSC/SCORC)"
        elif token["inters"] in ("(", ")"):
            note = "Character set designation is a DEC/ECMA-35 mechanism outside the ECMA-48 control-function set"
        else:
            note = ""
    else:
        note = ""
    if token.get("c1"):
        c1 = "8-bit C1 introducers are the ECMA-48 forms but are not valid inside UTF-8 streams (xterm ignores them in UTF-8 mode)"
        note = c1 + ("; " + note if note else "")
    return note


def _decomposition(token: dict[str, Any]) -> dict[str, Any]:
    """Grammar decomposition of one sequence token."""
    kind = token["kind"]
    if kind == "csi":
        params, inters, final = token["params"], token["inters"], token["final"]
        private = params[:1] in ("<", "=", ">", "?")
        return {
            "introducer": "C1 CSI (U+009B)" if token["c1"] else "ESC [",
            "private_parameter": params[0] if private else None,
            "parameters": params.lstrip("<=>?"),
            "parameter_list": params.lstrip("<=>?").split(";") if params.lstrip("<=>?") else [],
            "intermediates": inters,
            "final_byte": final,
            "length": token["end"] - token["start"],
        }
    if kind == "osc":
        body = token["body"]
        cmd = body.split(";", 1)[0]
        return {
            "introducer": token["intro"],
            "command": cmd if cmd.isdigit() else None,
            "payload": _bounded(body[len(cmd) :].lstrip(";"), 80),
            "terminator": "BEL (0x07)" if token["term"] == "bel" else "ST",
            "length": token["end"] - token["start"],
        }
    if kind == "esc":
        return {
            "introducer": "ESC",
            "intermediates": token["inters"],
            "final_byte": token["final"],
            "length": token["end"] - token["start"],
        }
    return {
        "introducer": token["intro"],
        "string_type": token["stype"].upper(),
        "terminator": token["term"],
        "length": token["end"] - token["start"],
    }


def _hyperlink_labels(events: list[dict[str, Any]], text: str, cap: int) -> dict[int, str | None]:
    """Find the visible label for each OSC 8 open (up to its closing OSC 8)."""
    labels: dict[int, str | None] = {}
    opens: list[dict[str, Any]] = []
    for tok in events:
        if tok.get("kind") != "osc" or tok["body"].split(";", 1)[0] != "8":
            continue
        if _osc8_uri(tok["body"]):
            opens.append(tok)
            if len(opens) > cap:
                opens.pop(0)
        elif opens:
            opener = opens.pop(0)
            label = text[opener["end"] : tok["start"]]
            labels[opener["start"]] = label if label.strip() else ""
    for tok in opens:
        labels[tok["start"]] = None  # unclosed link
    return labels


class ConsoleAnsiTool(Tool):
    """Parse, classify, strip, sanitize, and explain ANSI escape sequences."""

    max_input_chars: int = 2_000_000
    max_codes: int = 200
    max_samples: int = 8
    max_sample_chars: int = 48
    max_pending_chars: int = 64

    _MODES: ClassVar[tuple[str, ...]] = ("strip", "classify", "sanitize", "explain")
    _KEEP: ClassVar[dict[str, frozenset[str]]] = {
        "none": frozenset(),
        "sgr-only": frozenset({"sgr"}),
        "safe": frozenset({"sgr", "osc-link"}),
    }

    def execute(
        self,
        mode: str,
        text: str | None = None,
        sequence: str | None = None,
        keep: str = "none",
    ) -> dict[str, Any]:
        try:
            self._validate_config()
            if mode not in self._MODES:
                raise ValueError(f"mode must be one of {list(self._MODES)}")
            if mode == "explain":
                return self._explain(sequence)
            if not isinstance(text, str):
                raise ValueError("text must be a string")
            if keep != "none" and mode != "sanitize":
                raise ValueError("keep is only valid with mode=sanitize")
            if mode == "sanitize" and keep not in self._KEEP:
                raise ValueError(f"keep must be one of {list(self._KEEP)}")
            if len(text) > self.max_input_chars:
                raise ValueError(f"text exceeds max_input_chars={self.max_input_chars}")
            scan = _Scan(text).run()
            if mode == "strip":
                return self._strip(text, scan)
            if mode == "classify":
                return self._classify(text, scan)
            return self._sanitize(text, scan, keep)
        except (TypeError, ValueError) as exc:
            return {"status": "error", "error_type": "validation_error", "error": str(exc), "mode": mode}

    # -- modes ----------------------------------------------------------
    def _meta(self, text: str, scan: _Scan) -> dict[str, Any]:
        info: list[str] = []
        if scan.c1_detected:
            info.append(_C1_NOTE)
        if scan.stray_escapes:
            info.append(_STRAY_ESC_NOTE)
        if scan.osc_eof_runs:
            info.append(_OSC_EOF_NOTE)
        meta: dict[str, Any] = {
            "input_chars": len(text),
            "truncated_at_eof": scan.truncated_at_eof,
            "c1_8bit_detected": scan.c1_detected,
            "info": info,
        }
        if scan.truncated_at_eof and scan.pending_start is not None:
            pending = text[scan.pending_start :]
            meta["pending"] = _bounded(pending, self.max_pending_chars)
            meta["pending_truncated"] = len(pending) > self.max_pending_chars
        return meta

    def _strip(self, text: str, scan: _Scan) -> dict[str, Any]:
        clean_parts: list[str] = []
        classes: dict[str, int] = {}
        removed = 0
        for event in scan.events:
            if event["kind"] == "text":
                clean_parts.append(text[event["start"] : event["end"]])
            elif event["kind"] == "bad":
                removed += 1
            else:
                removed += 1
                category = _category(event)
                classes[category] = classes.get(category, 0) + 1
        clean = "".join(clean_parts)
        result = {
            "status": "success",
            "mode": "strip",
            "clean": clean,
            "removed_count": removed,
            "classes_removed": classes,
            "bytes_removed": len(text) - len(clean),
            "invalid_removed": scan.invalid_runs,
            "incomplete_removed": scan.incomplete_runs,
        }
        result.update(self._meta(text, scan))
        return result

    def _classify(self, text: str, scan: _Scan) -> dict[str, Any]:
        labels = _hyperlink_labels(scan.events, text, cap=4 * self.max_codes)
        grouped: dict[str, dict[str, Any]] = {}
        order: list[str] = []
        total = 0
        for event in scan.events:
            if event["kind"] in ("text", "bad"):
                continue
            total += 1
            code = _code(event)
            entry = grouped.get(code)
            if entry is None:
                entry = {"category": _category(event), "occurrences": 0, "samples": [], "token": event}
                grouped[code] = entry
                order.append(code)
            entry["occurrences"] += 1
            if len(entry["samples"]) < self.max_samples:
                entry["samples"].append((event["start"], event["end"]))
        inventory: list[dict[str, Any]] = []
        omitted = 0
        for code in order[: self.max_codes]:
            entry = grouped[code]
            token = entry["token"]
            label = labels.get(token["start"]) if entry["category"] == "osc-link" else None
            inventory.append(
                {
                    "category": entry["category"],
                    "code": code,
                    "human": _human(token, label),
                    "occurrences": entry["occurrences"],
                    "span_samples": [
                        {"start": s, "end": e, "text": _bounded(text[s:e], self.max_sample_chars)}
                        for s, e in entry["samples"]
                    ],
                }
            )
        omitted = max(0, len(order) - self.max_codes)
        text_chars = sum(e["end"] - e["start"] for e in scan.events if e["kind"] == "text")
        result = {
            "status": "success",
            "mode": "classify",
            "inventory": inventory,
            "distinct_codes": len(order),
            "inventory_truncated": omitted > 0,
            "omitted_codes": omitted,
            "total_sequences": total,
            "total_text_chars": text_chars,
        }
        result.update(self._meta(text, scan))
        return result

    def _sanitize(self, text: str, scan: _Scan, keep: str) -> dict[str, Any]:
        keep_set = self._KEEP[keep]
        out: list[str] = []
        kept = 0
        removed_by: dict[str, int] = {}
        for event in scan.events:
            kind = event["kind"]
            if kind == "text":
                out.append(text[event["start"] : event["end"]])
            elif kind == "bad":
                key = "incomplete" if event["reason"] == "incomplete" else "invalid"
                removed_by[key] = removed_by.get(key, 0) + 1
            else:
                category = _category(event)
                if category in keep_set:
                    kept += 1
                    out.append(text[event["start"] : event["end"]])  # canonical passthrough
                else:
                    removed_by[category] = removed_by.get(category, 0) + 1
        result = {
            "status": "success",
            "mode": "sanitize",
            "keep": keep,
            "output": "".join(out),
            "kept_count": kept,
            "removed_count": sum(removed_by.values()),
            "removed": removed_by,
        }
        result.update(self._meta(text, scan))
        return result

    def _explain(self, sequence: str | None) -> dict[str, Any]:
        if not isinstance(sequence, str):
            raise ValueError("sequence must be a string")
        if len(sequence) > self.max_input_chars:
            raise ValueError(f"sequence exceeds max_input_chars={self.max_input_chars}")
        scan = _Scan(sequence).run()
        seqs = [e for e in scan.events if e["kind"] not in ("text", "bad")]
        text_chars = [e for e in scan.events if e["kind"] == "text" and e["end"] > e["start"]]
        bad = [e for e in scan.events if e["kind"] == "bad"]
        if len(seqs) == 1 and not text_chars and not bad:
            token = seqs[0]
            return {
                "status": "success",
                "mode": "explain",
                "complete": True,
                "category": _category(token),
                "code": _code(token),
                "decomposition": _decomposition(token),
                "human": _human(token),
                "spec_note": _spec_note(token),
                "c1_8bit_detected": scan.c1_detected,
            }
        if not seqs and bad and bad[-1]["reason"] == "incomplete" and not text_chars:
            return {
                "status": "success",
                "mode": "explain",
                "complete": False,
                "category": "incomplete",
                "code": "incomplete",
                "decomposition": {"pending": _bounded(sequence, self.max_pending_chars)},
                "human": "Incomplete escape sequence (no final byte / terminator before end of input)",
                "spec_note": "",
                "truncated_at_eof": True,
            }
        raise ValueError("explain expects exactly one complete escape sequence and no surrounding text")

    def _validate_config(self) -> None:
        for name in ("max_input_chars", "max_codes", "max_samples", "max_sample_chars", "max_pending_chars"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
