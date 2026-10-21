#!/usr/bin/env python3
"""MIME transfer-encoding validation and RFC 2047/2231 header decoding."""

# stdlib only; strict validation, bounded inputs, deterministic output.
#
# Decoding contract: the tool models RFC 2045/2047/2231 precisely and reports
# every rule as a finding, but the *decoded preview* follows the lenient
# stdlib-decoder semantics byte-for-byte (binascii.a2b_qp / base64): invalid
# "=x" escapes emit both characters ("==" collapses to one "="), and
# trailing whitespace before a hard line break is kept, because those are
# the bytes a real lenient decoder yields. The stricter RFC-mandated
# behavior (trailing whitespace on a line must be deleted by decoders,
# RFC 2045 section 6.7 rule 3 note) is reported as a finding instead of
# being silently applied, so callers see both the transport reality and
# the rule.

import base64
import binascii
import codecs
import hashlib
import quopri
import re
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")
_B64_STD_ALPHABET = frozenset(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
)
_B64_STD_SPECIALS = frozenset("+/")
_B64_URL_SPECIALS = frozenset("-_")
_WHITESPACE = frozenset(" \t\r\n\v\f")
_QP_LINE_LIMIT = 76  # RFC 2045 section 6.7 rule 5.
_B64_LINE_LIMIT = 76  # RFC 2045 section 6.8 step 3.
_WORD_CHAR_BUDGET = 75  # RFC 2047 section 2: whole encoded-word <= 75 octets.

# Common charset registry (RFC 2047 plus widely deployed legacy charsets).
# Membership is advisory: charsets resolvable through Python's codec registry
# decode normally with an informational note; only fully unknown names take
# the graceful UTF-8/latin-1 fallback chain.
_COMMON_CHARSETS = frozenset({
    "us-ascii", "ascii", "iso-8859-1", "iso-8859-2", "iso-8859-3",
    "iso-8859-4", "iso-8859-5", "iso-8859-6", "iso-8859-7", "iso-8859-8",
    "iso-8859-9", "iso-8859-10", "iso-8859-11", "iso-8859-13", "iso-8859-14",
    "iso-8859-15", "utf-7", "utf-8", "windows-1252", "koi8-r", "gb2312",
    "gbk", "big5", "shift_jis", "euc-jp",
})

# RFC 2047 section 2 mime-charset-token characters (no "?", no space).
_CHARSET_TOKEN_RE = re.compile(r"^[!#$%&'+\-.^_`|~0-9A-Za-z]+$")
# RFC 2231 attribute characters: token characters minus "*", "'", "%".
_ATTR_TOKEN_RE = re.compile(r"^[!#$%&+\-.^_`|~0-9A-Za-z]+$")
# Parameter-looking tokens (RFC 2231 sections use "*" markers).
_PARAM_RE = re.compile(r"([!#$%&'*+\-.^_`|~0-9A-Za-z]+)\s*=", re.ASCII)


class MimeCodecTool(Tool):
    """Analyze and repair MIME transfer encodings offline.

    Modes: validate_qp, validate_base64, decode_words, encode_preview.
    """

    max_text_chars: int = 200000
    max_header_chars: int = 65536
    max_preview_chars: int = 512
    max_findings: int = 200
    max_words: int = 1000
    max_output_chars: int = 512
    output_hard_cap: int = 65536

    _MODES: ClassVar[frozenset[str]] = frozenset(
        {"validate_qp", "validate_base64", "decode_words", "encode_preview"}
    )
    _TARGETS: ClassVar[frozenset[str]] = frozenset(
        {"base64", "qp", "word-b", "word-q", "word"}
    )

    # ------------------------------------------------------------ dispatch

    def execute(
        self,
        mode: str,
        text: str | None = None,
        header: str | None = None,
        target: str | None = None,
        charset: str | None = None,
        strict: bool = False,
        max_output_chars: int | None = None,
    ) -> dict[str, Any]:
        operation = None
        try:
            self._validate_config()
            operation = self._mode(mode)
            if operation == "validate_qp":
                return self._validate_qp(text)
            if operation == "validate_base64":
                return self._validate_base64(text, strict)
            if operation == "decode_words":
                return self._decode_words(header)
            return self._encode_preview(text, target, charset, max_output_chars)
        except (TypeError, ValueError) as exc:
            return self._error(operation or mode, "validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive
            return self._error(
                operation or mode, "operation_error",
                f"MIME codec operation failed: {exc}",
            )

    # ---------------------------------------------------------------- util

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        return {
            "mode": mode if isinstance(mode, str) else "",
            "status": "error",
            "error_type": kind,
            "error": message,
        }

    def _validate_config(self) -> None:
        for bound_name in (
            "max_text_chars", "max_header_chars", "max_preview_chars",
            "max_findings", "max_words", "max_output_chars", "output_hard_cap",
        ):
            bound = getattr(self, bound_name)
            if isinstance(bound, bool) or not isinstance(bound, int) or bound <= 0:
                raise ValueError(f"{bound_name} must be a positive integer")
        if self.max_output_chars > self.output_hard_cap:
            raise ValueError(
                f"max_output_chars must not exceed output_hard_cap ({self.output_hard_cap})"
            )

    def _mode(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in self._MODES:
            raise ValueError(
                "mode must be validate_qp, validate_base64, decode_words, or encode_preview"
            )
        return mode

    @staticmethod
    def _text_arg(value: Any, name: str, cap: int) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string")
        if len(value) > cap:
            raise ValueError(f"{name} exceeds {cap} characters")
        return value

    @staticmethod
    def _bool_arg(value: Any, name: str) -> bool:
        if not isinstance(value, bool):
            raise TypeError(f"{name} must be a boolean")
        return value

    def _clip(self, findings: list[dict[str, Any]], total: int) -> dict[str, Any]:
        kept = findings[: self.max_findings]
        return {
            "findings": kept,
            "findings_total": total,
            "findings_truncated": total > len(kept),
        }

    @staticmethod
    def _preview(text: str, cap: int) -> tuple[str, bool]:
        return (text[:cap], len(text) > cap)

    # ---------------------------------------------------------- validate_qp

    def _validate_qp(self, value: Any) -> dict[str, Any]:
        text = self._text_arg(value, "text", self.max_text_chars)
        findings: list[dict[str, Any]] = []
        total = 0

        def note(severity: str, code: str, line: int, column: int,
                 message: str, **extra: Any) -> None:
            nonlocal total
            total += 1
            if len(findings) < self.max_findings:
                finding: dict[str, Any] = {
                    "code": code, "severity": severity, "line": line,
                    "column": column, "message": message,
                }
                finding.update(extra)
                findings.append(finding)

        out: list[int] = []
        lines = soft_breaks = escapes = lowercase = 0
        max_line_len = 0
        i, n = 0, len(text)
        while i < n:
            lines += 1
            line_start = i
            # Locate the line terminator (CRLF canonical; bare LF/CR lenient).
            j = line_start
            terminator = ""
            while j < n:
                ch = text[j]
                if ch == "\r":
                    terminator = "\r\n" if j + 1 < n and text[j + 1] == "\n" else "\r"
                    break
                if ch == "\n":
                    terminator = "\n"
                    break
                j += 1
            content_end = j if j < n else n
            line_len = content_end - line_start
            max_line_len = max(max_line_len, line_len)
            if terminator == "\n":
                note("warning", "bare_lf_line_break", lines, line_len + 1,
                     "Non-canonical line break: bare LF. RFC 2045 section "
                     "6.7 rule 1 admits only CRLF as the literal line break; "
                     "lenient decoders accept bare LF.")
            elif terminator == "\r":
                note("warning", "bare_cr_line_break", lines, line_len + 1,
                     "Non-canonical line break: bare CR. RFC 2045 section "
                     "6.7 rule 1 admits only CRLF; lenient decoders keep a "
                     "bare CR literally.")
            if line_len > _QP_LINE_LIMIT:
                note("warning", "line_too_long", lines, _QP_LINE_LIMIT + 1,
                     f"Encoded line is {line_len} characters; RFC 2045 "
                     f"section 6.7 rule 5 requires lines of no more than "
                     f"{_QP_LINE_LIMIT} characters.", length=line_len)
            # Scan the line content.
            k = line_start
            soft_here = False
            while k < content_end:
                ch = text[k]
                column = k - line_start + 1
                if ch == "=":
                    if (k + 2 < content_end
                            and text[k + 1] in _HEX_DIGITS
                            and text[k + 2] in _HEX_DIGITS):
                        out.append(int(text[k + 1 : k + 3], 16))
                        escapes += 1
                        if text[k + 1].islower() or text[k + 2].islower():
                            lowercase += 1
                            note("info", "escape_lowercase_hex", lines, column,
                                 "Lowercase hexadecimal escape is accepted by "
                                 "robust decoders per RFC 2045 section 6.7 "
                                 "rule 1, but generators should emit "
                                 "uppercase.", raw=text[k : k + 3])
                        k += 3
                        continue
                    if k == content_end - 1:
                        # Soft line break: '=' as the final character.
                        soft_breaks += 1
                        soft_here = True
                        if not terminator:
                            note("info", "soft_break_at_eof", lines, column,
                                 "Soft line break at end of input: the '=' "
                                 "and nothing after it are dropped by "
                                 "decoders.")
                        k += 1
                        continue
                    if k + 2 >= content_end:
                        note("error", "escape_truncated", lines, column,
                             "'=' escape cut short by the line break; a "
                             "quoted-printable escape needs two hexadecimal "
                             "digits (RFC 2045 section 6.7 rule 1).",
                             raw=text[k:content_end])
                    else:
                        note("error", "escape_invalid", lines, column,
                             "Stray '=' followed by a non-hex pair; RFC 2045 "
                             "section 6.7 rule 2 requires '=' to be encoded "
                             "as =3D. Lenient decoders pass the stray '=' "
                             "and the offending character through literally.",
                             raw=text[k : k + 3])
                    # Lenient decode mirrors binascii.a2b_qp exactly: a
                    # failed escape emits '=' plus the offending character
                    # (two consumed), except '==' which collapses to one '='.
                    out.append(ord("="))
                    if k + 1 < content_end:
                        if text[k + 1] != "=":
                            out.append(ord(text[k + 1]) & 0xFF)
                        k += 2
                    else:
                        k += 1
                    continue
                if ch in (" ", "\t"):
                    out.append(ord(ch))
                    k += 1
                    continue
                code_point = ord(ch)
                if ch == "\ufffd":
                    note("warning", "replacement_char_in_input", lines, column,
                         "U+FFFD shows that raw 8-bit bytes were lossily "
                         "decoded before reaching this text contract; the "
                         "original octets are unrecoverable. Binary data "
                         "must travel as =XX escapes (RFC 2045 section 6.7 "
                         "rule 1).")
                    out.append(0x3F)
                elif code_point < 0x20 or code_point == 0x7F:
                    note("error", "raw_control_octet", lines, column,
                         f"Raw control character U+{code_point:04X} cannot "
                         "be represented literally; control and NUL octets "
                         "must be =XX encoded (RFC 2045 section 6.7 rule 2).",
                         char=repr(ch))
                    out.append(code_point & 0xFF)
                elif code_point > 0x7E:
                    note("error", "raw_8bit_octet", lines, column,
                         f"Character U+{code_point:04X} beyond US-ASCII "
                         "cannot appear literally in quoted-printable; "
                         "8-bit octets must be =XX encoded (RFC 2045 "
                         "section 6.7 rule 1).",
                         char=repr(ch))
                    out.append(0x3F)
                else:
                    out.append(code_point)
                k += 1
            # Trailing whitespace: legal to receive, deleted by decoders.
            if not soft_here and line_len:
                stripped_len = len(text[line_start:content_end].rstrip(" \t"))
                if stripped_len < line_len:
                    dropped = line_len - stripped_len
                    note("warning", "trailing_whitespace", lines,
                         stripped_len + 1,
                         f"{dropped} trailing space/tab characters before "
                         "the line break. RFC 2045 section 6.7 rule 3 note: "
                         "trailing white space on a line must be deleted by "
                         "decoders (transport agents add it), so it is "
                         "transparent and cannot carry data; generators must "
                         "emit =20/=09 instead.",
                         dropped=dropped)
            if not terminator:
                break
            # A soft break's terminator is consumed silently; a hard break's
            # terminator is data.
            if not soft_here:
                for ch in terminator:
                    out.append(ord(ch))
            i = content_end + len(terminator)

        decoded = bytes(out)
        preview, truncated = self._preview(
            decoded.decode("utf-8", "replace"), self.max_preview_chars
        )
        if re.search("=[0-9A-Fa-f]{2}", decoded.decode("latin-1")):
            note("info", "decoded_contains_qp_pattern", 0, 0,
                 "Decoded output itself contains '=XX' patterns - the input "
                 "may be double-encoded quoted-printable (=3D3D style).")
        clipped = self._clip(findings, total)
        return {
            "mode": "validate_qp",
            "status": "success",
            "valid": not any(
                f["severity"] == "error" for f in clipped["findings"]
            ),
            **clipped,
            "decoded_preview": preview,
            "decoded_preview_truncated": truncated,
            "decoded_hex_preview": decoded[:64].hex(),
            "decoded_length": len(decoded),
            "stats": {
                "lines": lines,
                "soft_breaks": soft_breaks,
                "escapes": escapes,
                "lowercase_escapes": lowercase,
                "max_line_len": max_line_len,
            },
        }

    # ----------------------------------------------------- validate_base64

    def _validate_base64(self, value: Any, strict: Any) -> dict[str, Any]:
        text = self._text_arg(value, "text", self.max_text_chars)
        strict = self._bool_arg(strict, "strict")
        findings: list[dict[str, Any]] = []
        total = 0

        def note(severity: str, code: str, position: int,
                 message: str, **extra: Any) -> None:
            nonlocal total
            total += 1
            if len(findings) < self.max_findings:
                finding: dict[str, Any] = {
                    "code": code, "severity": severity, "position": position,
                    "message": message,
                }
                finding.update(extra)
                findings.append(finding)

        data: list[str] = []
        ws_kinds: dict[str, int] = {}
        line_lens: list[int] = [0]
        has_std_special = has_url_special = False
        pad_seen = False
        for pos, ch in enumerate(text):
            if ch == "\r" or ch == "\n":
                line_lens.append(0)
                kind = "crlf" if ch == "\r" else "lf"
                ws_kinds[kind] = ws_kinds.get(kind, 0) + 1
                continue
            line_lens[-1] += 1
            if ch in " \t\v\f":
                ws_kinds[{" ": "space", "\t": "tab"}.get(ch, "other")] = (
                    ws_kinds.get({" ": "space", "\t": "tab"}.get(ch, "other"), 0) + 1
                )
                continue
            if ch == "=":
                data.append(ch)
                pad_seen = True
                continue
            if ch in _B64_STD_ALPHABET or ch in _B64_URL_SPECIALS:
                if pad_seen:
                    note("error", "padding_interior", pos,
                         "Alphabet character after '=': padding is legal "
                         "only as the final characters of the data (RFC "
                         "4648 section 3.5); no decoder accepts data after "
                         "a pad.", char=ch)
                if ch in _B64_STD_SPECIALS:
                    has_std_special = True
                elif ch in _B64_URL_SPECIALS:
                    has_url_special = True
                data.append(ch)
                continue
            note("error", "illegal_character", pos,
                 f"Character {ch!r} is outside the base64 alphabet (RFC "
                 "4648 section 4). RFC 2045 section 6.8 orders MIME decoders "
                 "to ignore non-alphabet characters, but RFC 4648 section "
                 "3.3 requires rejection unless the caller's specification "
                 "explicitly says otherwise.", char=ch)
        dialect = "standard"
        if has_std_special and has_url_special:
            dialect = "mixed"
            note("error", "dialect_mixed", 0,
                 "Input mixes the standard alphabet ('+' or '/') with the "
                 "URL-safe dialect ('-' or '_'); no single decoder accepts "
                 "both (RFC 4648 sections 4 and 5).")
        elif has_url_special:
            dialect = "urlsafe"
            note("info", "urlsafe_dialect", 0,
                 "URL- and filename-safe base64 dialect (RFC 4648 section "
                 "5): '-' and '_' replace '+' and '/'; decode with "
                 "altchars=b'-_' (base64.urlsafe_b64decode).")
        if ws_kinds:
            kinds = dict(sorted(ws_kinds.items()))
            if strict:
                note("error", "whitespace_strict", 0,
                     "Strict mode rejects all whitespace; RFC 4648 section "
                     "3.5 admits neither whitespace nor any character "
                     "outside the alphabet.", kinds=kinds)
            else:
                note("info", "whitespace_present", 0,
                     "Whitespace between base64 data is tolerated the way "
                     "MIME mandates (RFC 2045 section 6.8: all line breaks "
                     "or other characters not found in the alphabet must be "
                     "ignored by decoding software).", kinds=kinds)
        folded_lines = [l for l in line_lens if l]
        max_line = max(folded_lines) if folded_lines else 0
        folded = len(folded_lines) > 1
        if folded and max_line > _B64_LINE_LIMIT:
            note("warning", "line_too_long", 0,
                 f"Folded input has a {max_line}-character line; RFC 2045 "
                 f"section 6.8 requires lines of no more than "
                 f"{_B64_LINE_LIMIT} characters.", length=max_line)
        # Length and padding discipline on the whitespace-stripped data.
        data_str = "".join(data)
        data_len = len(data_str)
        pads = data_len - len(data_str.rstrip("="))
        core_len = data_len - pads
        core_mod = core_len % 4
        padding = {
            "count": pads, "data_length": data_len,
            "data_mod_4": data_len % 4, "core_length": core_len,
        }
        if data_len % 4 == 1:
            note("error", "length_indivisible", data_len,
                 f"Whitespace-stripped data is {data_len} characters "
                 "(mod 4 == 1): at least one 4-character quantum is "
                 "truncated; no decoder can recover it (RFC 4648 section "
                 "3.5).")
            padding["expected"] = None
        elif core_mod == 1:
            note("error", "padding_count", data_len - pads,
                 f"A lone leftover data character cannot be completed by "
                 f"any legal pad count (RFC 4648 section 3.5 allows only "
                 "2 data + '==' or 3 data + '=').",
                 expected=None, actual=pads)
            padding["expected"] = None
        else:
            expected = {0: 0, 2: 2, 3: 1}[core_mod]
            padding["expected"] = expected
            if pads != expected:
                note("error", "padding_count", data_len - pads,
                     f"{pads} padding '=' characters but {expected} are "
                     f"required for {core_mod} trailing data characters "
                     "(RFC 4648 section 3.5: 2 leftover characters need "
                     "'==', 3 need '=', 0 need none).",
                     expected=expected, actual=pads)
            if core_mod == 0 and pads:
                note("error", "padding_excess", data_len - pads,
                     "Padding after a complete quantum run; '=' is legal "
                     "only to finish a partial final quantum (RFC 4648 "
                     "section 3.5).")
        decoded = b""
        sha = ""
        if not any(f["severity"] == "error" for f in findings):
            normalized = data_str
            if dialect == "urlsafe":
                normalized = data_str.replace("-", "+").replace("_", "/")
            try:
                decoded = base64.b64decode(normalized, validate=True)
            except (binascii.Error, ValueError) as exc:  # pragma: no cover
                note("error", "decode_failed", 0, f"stdlib decoder refused: {exc}")
            else:
                sha = hashlib.sha256(decoded).hexdigest()[:64]
        clipped = self._clip(findings, total)
        return {
            "mode": "validate_base64",
            "status": "success",
            "valid": not any(
                f["severity"] == "error" for f in clipped["findings"]
            ),
            "strict": strict,
            **clipped,
            "dialect": dialect,
            "decoded_size": len(decoded),
            "sha256_first64": sha,
            "padding": padding,
            "folded": folded,
            "fold_lines": len(folded_lines) if folded else 0,
            "max_line_len": max_line,
        }

    # --------------------------------------------------------- decode_words

    def _decode_words(self, value: Any) -> dict[str, Any]:
        header = self._text_arg(value, "header", self.max_header_chars)
        findings: list[dict[str, Any]] = []
        total = 0

        def note(severity: str, code: str, position: int,
                 message: str, **extra: Any) -> None:
            nonlocal total
            total += 1
            if len(findings) < self.max_findings:
                finding: dict[str, Any] = {
                    "code": code, "severity": severity, "position": position,
                    "message": message,
                }
                finding.update(extra)
                findings.append(finding)

        entries: list[dict[str, Any]] = []  # {start, end, entry}
        i = 0
        while i < len(header):
            j = header.find("=?", i)
            if j < 0:
                break
            # Manual frame scan: =?charset?enc?body?= (RFC 2047 section 2).
            # The body runs to the first '?=' so nested '=?' frames inside
            # the body are visible to the nested-word check below. RFC 2231
            # section 5 language tags ride on the charset as charset*lang.
            q1 = header.find("?", j + 2)
            charset_raw = enc_raw = None
            body = None
            start = end = None
            language = None
            if q1 > 0 and q1 + 2 < len(header) and header[q1 + 2] == "?":
                candidate_charset = header[j + 2 : q1]
                candidate_language = None
                if "*" in candidate_charset:
                    candidate_charset, candidate_language = candidate_charset.split("*", 1)
                candidate_enc = header[q1 + 1]
                close = header.find("?=", q1 + 3)
                if (
                    candidate_enc in "BbQq"
                    and close >= 0
                    and _CHARSET_TOKEN_RE.match(candidate_charset or "")
                    and (
                        candidate_language is None
                        or re.fullmatch(r"[A-Za-z0-9-]{0,32}", candidate_language)
                    )
                ):
                    charset_raw = candidate_charset
                    language = candidate_language
                    enc_raw = candidate_enc
                    body = header[q1 + 3 : close]
                    start, end = j, close + 2
            if body is None:
                close = header.find("?=", j + 2)
                end = close + 2 if close >= 0 else len(header)
                error = self._diagnose_word_frame(header, j, q1)
                entries.append({
                    "start": j, "end": end,
                    "entry": {
                        "raw": header[j : min(end, j + 96)],
                        "charset": None, "encoding": None, "language": None,
                        "charset_used": None, "text": None, "ok": False,
                        "error": error,
                    },
                })
                note("error", error, j,
                     "Encoded-word frame is not '=?charset?enc?body?=' with "
                     "a single B/Q encoding token (RFC 2047 section 2).",
                     raw=header[j : min(end, j + 48)])
                i = end
                continue
            if len(entries) >= self.max_words:
                note("error", "too_many_words", j,
                     f"More than {self.max_words} encoded words in one "
                     "header; refusing the remainder.")
                break
            entry: dict[str, Any] = {
                "raw": header[start:end], "charset": None,
                "encoding": enc_raw.upper(),
                "language": None, "charset_used": None, "text": None,
                "ok": False, "error": None,
            }
            if " " in body or "\t" in body:
                note("info", "body_whitespace", start,
                     "Whitespace inside encoded-text is forbidden by RFC "
                     "2047 section 2; decoding it leniently.",
                     raw=body[:48])
            if "=?" in body:
                entry["error"] = "nested_word"
                note("error", "nested_word", start,
                     "Encoded-word body contains another '=?' frame; words "
                     "cannot nest (RFC 2047 section 2).", raw=body[:48])
            if "?" in body:
                note("warning", "body_question_mark", start,
                     "'?' inside encoded-text is forbidden by RFC 2047 "
                     "section 2; a lenient scanner stopped the word early.",
                     raw=body[:48])
            if language is not None:
                note("info", "rfc2231_language_tag", start,
                     f"RFC 2231 section 5 language tag {language or ''!r} "
                     "on the charset token.", language=language)
            entry["language"] = language
            charset = charset_raw.lower()
            entry["charset"] = charset or None
            raw_bytes = self._decode_word_body(body, enc_raw.upper(), note, start)
            if raw_bytes is not None:
                entry["text"], used = self._bytes_to_text(
                    raw_bytes, charset, note, start
                )
                entry["charset_used"] = used
                entry["ok"] = entry["error"] is None
            entries.append({"start": start, "end": end, "entry": entry})
            i = end
        # Joined text with the RFC 2047 section 8 whitespace rules.
        pieces: list[str] = []
        quote_open = False
        escaped = False
        cursor = 0
        prev_end = None
        for record in entries:
            start, end, entry = record["start"], record["end"], record["entry"]
            gap = header[cursor:start]
            for ch in gap:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    quote_open = not quote_open
            if quote_open:
                note("error", "word_in_quoted_string", start,
                     "Encoded-word inside a quoted-string is forbidden "
                     "(RFC 2047 section 5: an 'encoded-word' must not "
                     "appear within a 'quoted-string').",
                     raw=header[start:end][:48])
            if prev_end is not None:
                folded_gap = re.sub(r"\r\n|\r|\n", "", gap)
                if folded_gap and folded_gap.strip(" \t") == "":
                    if "\r" in gap or "\n" in gap:
                        note("info", "folded_word_gap", start,
                             "Adjacent encoded words separated by a folded "
                             "(CRLF + WSP) gap; the fold is ignored per RFC "
                             "2047 section 6.2.")
                    if len(folded_gap) > 1:
                        pieces.append(" " * (len(folded_gap) - 1))
                        note("info", "extra_separator_whitespace", start,
                             "More than one whitespace character separates "
                             "adjacent encoded words; RFC 2047 section 8 "
                             "keeps the surplus as literal spaces.",
                             gap=folded_gap[:16])
                else:
                    pieces.append(gap)
            else:
                pieces.append(gap)
            pieces.append(entry["text"] if entry["text"] is not None else "")
            prev_end = end
            cursor = end
        pieces.append(header[cursor:])
        rfc2231 = self._scan_rfc2231(header, note)
        clipped = self._clip(findings, total)
        charsets_seen = sorted(
            {e["entry"]["charset"] for e in entries if e["entry"]["charset"]}
            | {p["charset"] for p in rfc2231 if p.get("charset")}
        )
        return {
            "mode": "decode_words",
            "status": "success",
            "words": [e["entry"] for e in entries],
            "joined_text": "".join(pieces),
            "charset_candidates": charsets_seen,
            "rfc2231_params": rfc2231,
            **clipped,
        }

    @staticmethod
    def _diagnose_word_frame(header: str, start: int, q1: int) -> str:
        """Classify why an '=?...' frame did not parse as an encoded word."""
        if q1 < 0 or header.find("?=", q1 if q1 > 0 else start + 2) < 0:
            return "unterminated_word"
        if q1 <= start + 2:
            return "bad_charset_token"
        charset = header[start + 2 : q1]
        if "*" in charset:
            charset = charset.split("*", 1)[0]
        if not _CHARSET_TOKEN_RE.match(charset or ""):
            return "bad_charset_token"
        if q1 + 1 >= len(header) or header[q1 + 1] not in "BbQq":
            return "bad_encoding_token"
        return "malformed_word_frame"

    def _decode_word_body(
        self, body: str, encoding: str, note: Any, start: int,
    ) -> bytes | None:
        if encoding == "B":
            compact = re.sub(r"\s+", "", body)
            try:
                return base64.b64decode(compact, validate=True)
            except (binascii.Error, ValueError):
                padded = compact + "=" * ((4 - len(compact) % 4) % 4)
                try:
                    raw = base64.b64decode(padded, validate=True)
                except (binascii.Error, ValueError):
                    note("error", "bad_base64_body", start,
                         "Encoded-word body is not valid base64 (RFC 2047 "
                         "section 4.1).", raw=body[:48])
                    return None
                note("warning", "b64_body_unpadded", start,
                     "Encoded-word base64 body lacked its '=' padding; "
                     "repaired before decoding (RFC 2047 section 4.1 "
                     "requires padded output).", raw=body[:48])
                return raw
        out = bytearray()
        k = 0
        while k < len(body):
            ch = body[k]
            if ch == "_":
                out.append(0x20)
                k += 1
                continue
            if (ch == "=" and k + 2 < len(body)
                    and body[k + 1] in _HEX_DIGITS
                    and body[k + 2] in _HEX_DIGITS):
                out.append(int(body[k + 1 : k + 3], 16))
                k += 3
                continue
            if ch == "=":
                note("error", "bad_q_escape", start + k,
                     "Q-encoding escape without two hexadecimal digits "
                     "(RFC 2047 section 4.2).", raw=body[k : k + 3])
                out.append(ord("="))
                k += 1
                continue
            code_point = ord(ch)
            if code_point > 0x7E:
                note("error", "raw_8bit_in_body", start + k,
                     f"Character U+{code_point:04X} cannot appear in "
                     "encoded-text (RFC 2047 section 2: printable "
                     "US-ASCII only).", char=repr(ch))
                out.append(0x3F)
            else:
                out.append(code_point)
            k += 1
        return bytes(out)

    def _bytes_to_text(
        self, raw: bytes, charset: str, note: Any, start: int,
    ) -> tuple[str, str]:
        if charset in _COMMON_CHARSETS:
            used = charset
        else:
            try:
                codecs.lookup(charset)
            except LookupError:
                note("warning", "charset_unknown", start,
                     f"Charset {charset or ''!r} is not in the common "
                     "registry nor resolvable in the Python codec registry; "
                     "decoding falls back to UTF-8 then latin-1.",
                     charset=charset)
                for fallback in ("utf-8", "latin-1"):
                    try:
                        return raw.decode(fallback), fallback
                    except UnicodeDecodeError:
                        continue
                return raw.decode("latin-1"), "latin-1"
            used = charset
            note("info", "charset_not_common", start,
                 f"Charset {charset!r} is outside the curated common "
                 "registry but resolvable in the Python codec registry; "
                 "decoding proceeds with it.", charset=charset)
        try:
            return raw.decode(used), used
        except UnicodeDecodeError as exc:
            note("warning", "charset_decode_error", start,
                 f"Bytes are not valid {used}: {exc}; falling back to "
                 "latin-1 which accepts every byte.", charset=used)
            return raw.decode("latin-1"), "latin-1"

    # ----------------------------------------------------- RFC 2231 params

    def _scan_rfc2231(self, header: str, note: Any) -> list[dict[str, Any]]:
        quoted_mask = self._quoted_regions(header)
        params: dict[str, dict[int | None, dict[str, Any]]] = {}
        order: list[str] = []
        for match in _PARAM_RE.finditer(header):
            name = match.group(1)
            if "*" not in name:
                continue
            if quoted_mask[match.start(1)]:
                continue  # '*' marker inside a quoted value: not a parameter.
            parts = name.split("*")
            base = parts[0]
            if not _ATTR_TOKEN_RE.match(base):
                note("error", "bad_parameter_name", match.start(),
                     f"Parameter name {name!r} contains characters outside "
                     "the RFC 2231 attribute grammar.", raw=name[:48])
                continue
            idx: int | None = None
            extended = False
            rest = parts[1:]
            if rest and rest[-1] == "":
                extended = True
                rest = rest[:-1]
            if rest:
                if len(rest) > 1 or not rest[0].isdigit():
                    note("error", "bad_section_index", match.start(),
                         f"RFC 2231 section markers must be a single "
                         f"numeric index, got {name!r}.", raw=name[:48])
                    continue
                idx = int(rest[0])
            value_start = match.end()
            rest_text = header[value_start:].lstrip(" \t")
            if rest_text.startswith('"'):
                raw_value_chars: list[str] = []
                q = 1
                while q < len(rest_text):
                    ch = rest_text[q]
                    if ch == "\\" and q + 1 < len(rest_text):
                        raw_value_chars.append(rest_text[q + 1])
                        q += 2
                        continue
                    if ch == '"':
                        break
                    raw_value_chars.append(ch)
                    q += 1
                raw_value = "".join(raw_value_chars)
            else:
                cut = rest_text.find(";")
                raw_value = (
                    rest_text if cut < 0 else rest_text[:cut]
                ).strip()
            bucket = params.setdefault(base, {})
            if base not in order:
                order.append(base)
            bucket[idx] = {
                "index": idx, "extended": extended, "raw": raw_value,
            }
        results: list[dict[str, Any]] = []
        for base in order:
            bucket = params[base]
            indexes = sorted(k for k in bucket if k is not None)
            if indexes and indexes != list(range(len(indexes))):
                note("warning", "continuation_gap", 0,
                     f"Parameter {base!r} sections {indexes} are not "
                     "contiguous from 0.", indexes=indexes)
            keys: list[int | None] = (
                [None] + [k for k in indexes if k != 0] if None in bucket
                else list(indexes)
            )
            first_key = keys[0] if keys else None
            charset = language = ""
            ok = True
            error = None
            byte_chunks = bytearray()
            text_tail: list[tuple[int, str]] = []
            any_extended = any(c["extended"] for c in bucket.values())
            for key in keys:
                chunk = bucket[key]
                if not chunk["extended"]:
                    text_tail.append((chunk["index"] or 0, chunk["raw"]))
                    if any_extended:
                        note("info", "mixed_sections", 0,
                             f"Parameter {base!r} mixes extended and plain "
                             "sections; plain sections are appended "
                             "verbatim after charset decoding, matching the "
                             "RFC 2231 section 4 example.")
                    continue
                value = chunk["raw"]
                if key == first_key:
                    pieces = value.split("'", 2)
                    if len(pieces) != 3:
                        note("error", "missing_charset_decl", 0,
                             f"Extended initial section of {base!r} must be "
                             "charset'language'value.", raw=value[:48])
                        ok = False
                        error = error or "missing_charset_decl"
                        charset = "us-ascii"
                    else:
                        charset = pieces[0].lower()
                        language = pieces[1]
                        value = pieces[2]
                        if not charset:
                            note("error", "empty_charset_decl", 0,
                                 f"Extended initial section of {base!r} "
                                 "declares an empty charset.")
                            ok = False
                            error = error or "empty_charset_decl"
                            charset = "us-ascii"
                chunk_bytes, chunk_ok = self._percent_decode(value)
                if not chunk_ok:
                    note("error", "bad_percent_escape", 0,
                         f"Extended section of {base!r} contains '%' not "
                         "followed by two hexadecimal digits (RFC 2231 "
                         "section 4).", raw=value[:48])
                    ok = False
                    error = error or "bad_percent_escape"
                byte_chunks.extend(chunk_bytes)
            merged = ""
            if byte_chunks:
                merged, used = self._bytes_to_text(
                    bytes(byte_chunks), charset or "us-ascii", note, 0
                )
                charset = charset or used
            merged += "".join(text for _, text in sorted(text_tail))
            results.append({
                "name": base,
                "charset": charset or None,
                "language": language or None,
                "chunks": [
                    {
                        "index": bucket[key]["index"],
                        "extended": bucket[key]["extended"],
                        "raw": bucket[key]["raw"],
                    }
                    for key in keys
                ],
                "merged_value": merged,
                "ok": ok,
                "error": error,
            })
        return results

    @staticmethod
    def _quoted_regions(text: str) -> list[bool]:
        """True per character when inside a double-quoted string."""
        mask = [False] * len(text)
        inside = False
        escaped = False
        for i, ch in enumerate(text):
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                inside = not inside
                continue
            mask[i] = inside
        return mask

    @staticmethod
    def _percent_decode(value: str) -> tuple[bytes, bool]:
        out = bytearray()
        ok = True
        k = 0
        while k < len(value):
            ch = value[k]
            if (ch == "%" and k + 2 < len(value)
                    and value[k + 1] in _HEX_DIGITS
                    and value[k + 2] in _HEX_DIGITS):
                out.append(int(value[k + 1 : k + 3], 16))
                k += 3
                continue
            if ch == "%":
                out.append(0x25)
                ok = False
            else:
                out.append(ord(ch) & 0xFF)
            k += 1
        return bytes(out), ok

    # ------------------------------------------------------ encode_preview

    def _encode_preview(
        self, value: Any, target: Any, charset: Any, cap: Any,
    ) -> dict[str, Any]:
        text = self._text_arg(value, "text", self.max_text_chars)
        if not isinstance(target, str):
            raise TypeError("target must be a string")
        target = target.strip().lower()
        if target not in self._TARGETS:
            raise ValueError(
                "target must be base64, qp, word-b, word-q, or word"
            )
        charset = charset or "utf-8"
        if not isinstance(charset, str) or not _CHARSET_TOKEN_RE.match(charset):
            raise ValueError("charset must be an RFC 2047 charset token")
        charset = charset.lower()
        try:
            codecs.lookup(charset)
        except LookupError:
            raise ValueError(
                f"charset {charset!r} is not resolvable in the Python codec registry"
            ) from None
        if cap is None:
            cap = self.max_output_chars
        if isinstance(cap, bool) or not isinstance(cap, int) or not (
            1 <= cap <= self.output_hard_cap
        ):
            raise ValueError(
                f"max_output_chars must be an integer in 1..{self.output_hard_cap}"
            )
        data = text.encode(charset)
        notes: list[str] = []
        if target == "base64":
            encoded = base64.b64encode(data).decode("ascii")
            folded_encoded = self._fold_76(encoded)
            notes.append(
                "Base64 per RFC 4648 section 4; folded at 76 columns with "
                "CRLF terminators per RFC 2045 section 6.8."
            )
        elif target == "qp":
            encoded = quopri.encodestring(data).decode("ascii")
            folded_encoded = encoded
            notes.append(
                "Quoted-printable via the stdlib quopri encoder: soft line "
                "breaks ('=' at column 76) per RFC 2045 section 6.7 rule 5; "
                "the encoder already folds, so line_folded equals encoded."
            )
        else:
            if target == "word-b":
                encoded = self._encode_words(text, charset, "B")
            elif target == "word-q":
                encoded = self._encode_words(text, charset, "Q")
            else:  # word: pick whichever full encoding is shorter.
                b_full = self._encode_words(text, charset, "B")
                q_full = self._encode_words(text, charset, "Q")
                if len(q_full) < len(b_full):
                    encoded = q_full
                    notes.append(
                        f"Auto-selected Q: {len(q_full)} characters vs "
                        f"{len(b_full)} for B (shorter wins; ties go to B)."
                    )
                else:
                    encoded = b_full
                    notes.append(
                        f"Auto-selected B: {len(b_full)} characters vs "
                        f"{len(q_full)} for Q (shorter wins; ties go to B)."
                    )
            folded_encoded = encoded
            notes.append(
                f"Encoded words capped at {_WORD_CHAR_BUDGET} characters "
                "including delimiters per RFC 2047 section 2; multiple "
                "words are joined by CRLF + space folds, which decoders "
                "merge back per RFC 2047 section 6.2."
            )
            if target == "word-b":
                notes.append(
                    "B bodies are padded base64 (RFC 2047 section 4.1)."
                )
            if target == "word-q":
                notes.append(
                    "Q bodies use '_' for space and =HH uppercase escapes "
                    "(RFC 2047 section 4.2)."
                )
        preview, truncated = self._preview(encoded, cap)
        folded_preview, folded_truncated = self._preview(folded_encoded, cap)
        return {
            "mode": "encode_preview",
            "status": "success",
            "target": target,
            "charset": charset,
            "encoded": preview,
            "encoded_truncated": truncated,
            "full_length": len(encoded),
            "line_folded": folded_preview,
            "line_folded_truncated": folded_truncated,
            "folded": folded_encoded != encoded or "\r\n" in folded_encoded,
            "notes": notes,
        }

    @staticmethod
    def _fold_76(text: str) -> str:
        if len(text) <= _B64_LINE_LIMIT:
            return text
        return "\r\n".join(
            text[i : i + _B64_LINE_LIMIT]
            for i in range(0, len(text), _B64_LINE_LIMIT)
        )

    def _encode_words(self, text: str, charset: str, encoding: str) -> str:
        """Split text into whole-character chunks, one encoded word each.

        Chunking on character boundaries (not bytes) keeps every multibyte
        character inside a single word so each word decodes independently;
        the body of each word is capped to keep the whole word at or below
        the RFC 2047 section 2 limit of 75 characters.
        """
        prefix = f"=?{charset}?{encoding}?"
        budget = _WORD_CHAR_BUDGET - len(prefix) - 2  # minus closing '?='
        chunks: list[str] = []
        if encoding == "B":
            # Largest byte count whose base64 expansion fits the budget.
            max_bytes = max(3, budget // 4 * 3)
            buf = b""
            for ch in text:
                encoded_char = ch.encode(charset)
                if buf and len(buf) + len(encoded_char) > max_bytes:
                    chunks.append(
                        prefix + base64.b64encode(buf).decode("ascii") + "?="
                    )
                    buf = encoded_char
                else:
                    buf += encoded_char
            chunks.append(
                prefix + base64.b64encode(buf).decode("ascii") + "?="
            )
        else:
            body: list[str] = []
            used = 0
            for ch in text:
                piece = "".join(
                    self._q_octet(octet) for octet in ch.encode(charset)
                )
                if body and used + len(piece) > budget:
                    chunks.append(prefix + "".join(body) + "?=")
                    body, used = [], 0
                body.append(piece)
                used += len(piece)
            chunks.append(prefix + "".join(body) + "?=")
        return "\r\n ".join(chunks)

    @staticmethod
    def _q_octet(octet: int) -> str:
        ch = chr(octet)
        if ch == " ":
            return "_"
        if 0x21 <= octet <= 0x7E and ch not in ("=", "?", "_"):
            return ch
        return f"={octet:02X}"
