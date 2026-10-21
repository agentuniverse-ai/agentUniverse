"""Tests for HttpHeaderTool: header grammar, list parsing, security audit, cookies.

Oracle strategy:
- validate: 400 seeded (name, value) pairs are adjudicated against the real
  ``http.client.putheader`` implementation; every rejection by CPython must be
  rejected here, and the only accepted-but-rejected divergences are the pinned
  RFC 7230 strictness categories (putheader is knowingly more lenient than the
  RFC token/field-value grammar). email.header folding is adjudicated
  separately as an obs-fold divergence.
- parse_list: 200 seeded list values are compared element-by-element with an
  independent reference parser implemented in this file.
- parse_cookie: 150 seeded Set-Cookie strings are compared against
  ``http.cookies.SimpleCookie`` with the lenient/strict divergences pinned
  ($Path/$Domain attachment, unquoting, whole-cookie drops).
- security_audit: OWASP secure-headers ground-truth battery (HSTS max-age
  parse, CSP3 directive examples, XFO/XSS-Protection/cache/cookie checks) plus
  a self-review battery pinning RFC 6797 whole-header-ignore semantics for
  non-conforming STS headers and CSP3 ignore rules (nonce/hash suppressing
  'unsafe-inline', 'strict-dynamic' suppressing host allowlists, unquoted
  nonce/hash tokens, sandbox's valid empty form, report-uri/report-to).
- cookie-date: 60 hand-derived RFC 6265 section 5.1.1 cases plus a second,
  disjoint 55-case battery re-derived during the hostile self-review.
- A second-generation putheader battery (300 fresh seeds) and parse_list
  battery (200 fresh values with unterminated quotes, ';=' chunks, and
  duplicated q parameters) guard against regressions in the seeded oracles.
"""

import email.header
import http.client
import http.cookies
import os
import random
import unittest

from agentuniverse.agent.action.tool.common_tool import http_header_tool as header_module
from agentuniverse.agent.action.tool.common_tool.http_header_tool import HttpHeaderTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(header_module.__file__), "http_header_tool.yaml")

# Finding codes tolerated when putheader ACCEPTS a pair but the stricter
# RFC 7230 token/field-value grammar rejects it (the pinned divergences).
PUTHEADER_DIVERGENCE_CODES = {
    "name_non_token",       # putheader allows SP/NUL/any non-colon bytes in names
    "value_nul",            # putheader allows NUL in values (latin-1 bytes)
    "value_ctl_char",       # putheader allows C0/DEL controls in values
    "value_non_ascii",      # putheader allows latin-1 high bytes in values
    "value_obs_fold",       # putheader accepts CR/LF followed by OWS continuations
}


def putheader_rejects(name, value):
    """Classify a pair with the real CPython http.client putheader validator."""
    connection = http.client.HTTPConnection("example.invalid")
    connection.putrequest("GET", "/")
    try:
        connection.putheader(name, value)
        return False
    except Exception:  # ValueError, UnicodeEncodeError, CannotSendHeader, ...
        return True


def reference_list_parse(value):
    """Independent RFC 7231 list parser (explicit scanner, no shared helpers).

    Returns a list of (token, [(param_name, param_value_or_None), ...], q,
    q_malformed) with quoting, escapes, duplicate tokens, and malformed q
    handled exactly as specified.
    """
    # Pass 1: split on commas outside quoted strings.
    elements = []
    buf = []
    quote = False
    esc = False
    for ch in value:
        if quote:
            buf.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                quote = False
            continue
        if ch == '"':
            buf.append(ch)
            quote = True
        elif ch == ",":
            elements.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    elements.append("".join(buf))

    result = []
    for element in elements:
        if not element.strip(" \t"):
            continue
        # Pass 2: split on semicolons outside quoted strings.
        pieces = []
        buf = []
        quote = False
        esc = False
        for ch in element:
            if quote:
                buf.append(ch)
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    quote = False
                continue
            if ch == '"':
                buf.append(ch)
                quote = True
            elif ch == ";":
                pieces.append("".join(buf))
                buf = []
            else:
                buf.append(ch)
        pieces.append("".join(buf))

        token = pieces[0].strip(" \t")
        params = []
        for piece in pieces[1:]:
            name, eq, val = piece.partition("=")
            name = name.strip(" \t")
            if not name:
                params.append(("", None))
                continue
            if not eq:
                params.append((name, None))
                continue
            val = val.strip(" \t")
            if len(val) >= 2 and val[0] == '"' and val[-1] == '"':
                inner = val[1:-1]
                out = []
                i = 0
                while i < len(inner):
                    if inner[i] == "\\" and i + 1 < len(inner):
                        out.append(inner[i + 1])
                        i += 2
                    else:
                        out.append(inner[i])
                        i += 1
                val = "".join(out)
            params.append((name, val))
        q = None
        q_malformed = False
        seen_q = False
        for pname, pvalue in params:
            if pname.lower() != "q":
                continue
            if seen_q:
                continue
            seen_q = True
            if pvalue is None:
                q_malformed = True
                continue
            if "." in pvalue:
                whole, _, frac = pvalue.partition(".")
                if whole == "0" and (frac == "" or (frac.isdigit() and len(frac) <= 3)):
                    q = float(pvalue)
                elif whole == "1" and (frac == "" or (set(frac) == {"0"} and len(frac) <= 3)):
                    q = 1.0 if not frac else float(pvalue)
                else:
                    q_malformed = True
            elif pvalue in ("0", "1"):
                q = float(pvalue)
            else:
                q_malformed = True
        result.append((token, tuple(params), q, q_malformed))
    return result


def seeded_pairs(count, seed):
    """Deterministically seed (name, value) pairs mixing valid and hostile input."""
    rng = random.Random(seed)
    names = [
        "Host", "Content-Type", "X-Custom-Header", "Accept", "Set-Cookie",
        "Cache-Control", "a", "X", "!#$%&'*+-.^_`|~", "0-1-2", "User-Agent",
        "Strict-Transport-Security", "Age", "Warning",
    ]
    values = [
        "example.com", "text/html;charset=utf-8", "0", "nosniff",
        "max-age=31536000; includeSubDomains", "a b c", "tab\tsep",
        "\"quoted string\"", "back\\slash", "!", "~", "Tue, 15 Nov 1994 08:12:31 GMT",
        "", " ",
    ]
    mutations = [
        "\r\n", "\n", "\r", "\r\n ", "\n\t", "\r ", "\x00", "\x01", "\x0b",
        "\x1f", "\x7f", "ÿ", "é", "€", "\U0001f600", " ", "  ", ":", "(",
        ")", "@", ",", ";", "\t",
    ]
    pairs = []
    for i in range(count):
        if i % 7 == 0:  # keep a clean subpopulation
            pairs.append((rng.choice(names), rng.choice(values)))
            continue
        name = list(rng.choice(names))
        value = list(rng.choice(values))
        for _ in range(rng.randint(1, 2)):
            mutation = rng.choice(mutations)
            target = rng.choice(("name", "value"))
            if name and target == "name":
                pos = rng.randrange(len(name) + 1)
                name.insert(pos, mutation)
            elif value:
                pos = rng.randrange(len(value) + 1)
                value.insert(pos, mutation)
        if rng.random() < 0.05:
            name = []
        if rng.random() < 0.05:
            value = []
        pairs.append(("".join(name), "".join(value)))
    return pairs


def seeded_lists(count, seed):
    """Deterministically seed list-header values (Accept/Cache-Control style)."""
    rng = random.Random(seed)
    tokens = [
        "text/html", "application/xhtml+xml", "application/xml;q=0.9", "*/*",
        "no-cache", "no-store", "max-age=3600", "public", "private", "gzip",
        "br", "compress;q=1", "iso-8859-1", "utf-8", "level=1", "\"quoted\"",
        "en-US", "de", "bytes=0-499", "w organ", "a\"b", "cache",
    ]
    params = [
        "", ";q=1", ";q=0", ";q=0.5", ";q=0.85", ";q=1.0", ";q=0.001",
        ";q=2", ";q=-1", ";q=1.5", ";q=abc", ";q=", ";q", ";level=1",
        ";level=2;q=0.3", ";charset=utf-8", ";foo=\"bar,baz\"", ";foo",
        ";bar=", ";x=\"a\\\"b\"", ";Q=0.5", ";q=0.1234", ";q=0.1;q=0.2",
    ]
    values = []
    for i in range(count):
        if i % 9 == 0:
            values.append(rng.choice(tokens))
            continue
        pieces = []
        for _ in range(rng.randint(1, 5)):
            pieces.append(rng.choice(tokens) + rng.choice(params))
        joiner = [",", ", ", " ,", " , ", ",,"][rng.randrange(5)]
        candidate = joiner.join(pieces)
        if rng.random() < 0.15:
            candidate += rng.choice([",", ", ", " ,"])
        if rng.random() < 0.15:
            candidate = rng.choice([",", ", "]) + candidate
        values.append(candidate)
    return values


def seeded_cookies(count, seed):
    """Deterministically seed Set-Cookie strings."""
    rng = random.Random(seed)
    names = ["sid", "sessionid", "a", "KEY_1", "tracking", "ke\"y", "na me", "x"]
    values = ["abc123", "1", "a,b", "\"quoted val\"", "sp ace", "x;y", "café", ""]
    attributes = [
        "Path=/", "Path=relative", "Domain=.example.com", "Domain=bad name",
        "Secure", "Secure=true", "HttpOnly", "SameSite=Lax", "SameSite=None",
        "SameSite=None; Secure", "SameSite=strict", "SameSite=invalid",
        "Max-Age=3600", "Max-Age=-1", "Max-Age=soon", "Expires=Wed, 09 Jun 2021 10:18:14 GMT",
        "Expires=never", "$Path=/x", "$Domain=example.com", "Unknown=v",
        "Comment=hi", "Version=1", "",
    ]
    cookies = []
    for i in range(count):
        if i % 11 == 0:
            cookies.append(rng.choice([
                "novalue", "=nokey", "", "novalue; Path=/", "  spaced  =  val  ",
            ]))
            continue
        parts = [f"{rng.choice(names)}={rng.choice(values)}"]
        for _ in range(rng.randint(0, 3)):
            parts.append(rng.choice(attributes))
        cookies.append("; ".join(parts))
    return cookies


def fresh_seeded_pairs(count, seed):
    """Second-generation hostile (name, value) pairs (self-review battery)."""
    rng = random.Random(seed)
    names = [
        "X-Good-1", "!#$%&'*+-.^_`|~", "a", "Z", "X_with_space", "X\tTabbed",
        "é-Name", "X-Foo:", ":Leading", " Leading", "X\rFoo", "X\nFoo",
        "Content-Length", "Set-Cookie", "Max-Forwards", "X-" + "y" * 30,
    ]
    values = [
        "ok", "", " ", "\t", "a\r\nb", "a\r\n b", "a\r b", "a\n b", "a\nb",
        "a\rb", "\r", "\n", "\r\n", "\r\n ", "\x00", "\x7f", "\x1f", "\x0b",
        "ÿ", "é", "€", "\U0001f600", 'q"q', "a\\b", "a: b", ";x", "(x)", "@y",
        "0" * 33, "ünïcodeÿ",
    ]
    mutations = ["\r", "\n", "\r\n", "\r\n ", "\r ", "\n\t", " ", "\t",
                 "\x00", "\x1f", "\x7f", "ÿ", "€", "\U0001f600", ":", ";", '"', "\\"]
    pairs = []
    for i in range(count):
        name = rng.choice(names)
        value = rng.choice(values)
        for _ in range(rng.randint(0, 2)):
            if rng.random() < 0.5 and name:
                pos = rng.randrange(len(name) + 1)
                name = name[:pos] + rng.choice(mutations) + name[pos:]
            elif value:
                pos = rng.randrange(len(value) + 1)
                value = value[:pos] + rng.choice(mutations) + value[pos:]
        if rng.random() < 0.04:
            name = ""
        if rng.random() < 0.04:
            value = ""
        pairs.append((name, value))
    return pairs


def fresh_seeded_lists(count, seed):
    """Second-generation list-header values (unterminated quotes, ;=, dup q)."""
    rng = random.Random(seed)
    tokens = [
        "text/html", "application/vnd.api+json", "image/avif", "*/*",
        "no-cache", "immutable", "stale-while-revalidate=60", "gzip", "zstd",
        "br;q=0.7", "en-GB", "*;q=0.2", "bytes=100-", "\"who, knows\"", "a\"b",
        "x\\y", "w/organ", "nosniff", "level=2", "mono", "UTF-16",
    ]
    params = [
        "", ";q=1", ";q=0", ";q=0.9", ";q=0.123", ";q=1.000", ";q=00", ";q=0.",
        ";q=1.", ";q=-0.5", ";q=2.0", ";q=0.1234", ";q=abc", ";q=", ";q",
        ";Q=0.3", ";charset=\"utf, 8\"", ";foo=bar;baz", ";x=\"unclosed",
        ";x=\"a\\\"b;c\"", ";q=0.5;q=0.6", "; ;", ";=", ";a=", ";=b",
    ]
    values = []
    for i in range(count):
        if i % 8 == 0:
            values.append(rng.choice(tokens))
            continue
        pieces = [rng.choice(tokens) + rng.choice(params)
                  for _ in range(rng.randint(1, 5))]
        joiner = rng.choice([",", ", ", " ,", " , ", ",,", ",\t"])
        candidate = joiner.join(pieces)
        if rng.random() < 0.18:
            candidate += rng.choice([",", ", ", " ,", ";"])
        if rng.random() < 0.15:
            candidate = rng.choice([", ", ","]) + candidate
        values.append(candidate)
    return values


class HttpHeaderValidateTest(unittest.TestCase):
    """Mode validate: RFC 7230 grammar + http.client.putheader oracle."""

    def setUp(self):
        """Create a default-configured tool."""
        self.tool = HttpHeaderTool()

    def test_valid_header(self):
        """Verify a plain valid header validates with no findings."""
        result = self.tool.execute("validate", name="Content-Type", value="text/html")
        self.assertTrue(result["name_valid"])
        self.assertTrue(result["value_valid"])
        self.assertEqual(result["findings"], [])
        self.assertTrue(result["known_field"])
        self.assertEqual(result["field_category"], "both")

    def test_putheader_oracle_400_seeded_pairs(self):
        """400 seeded pairs: every putheader rejection is rejected here.

        Acceptances that this tool still rejects must fall in the pinned
        divergence set (putheader is more lenient than the RFC grammar).
        """
        pairs = seeded_pairs(400, 20260921)
        self.assertEqual(len(pairs), 400)
        rejects = 0
        divergences = 0
        for name, value in pairs:
            result = self.tool.execute("validate", name=name, value=value)
            error_codes = {
                f["code"] for f in result["findings"] if f["severity"] == "error"
            }
            invalid = bool(error_codes)
            if putheader_rejects(name, value):
                rejects += 1
                self.assertTrue(
                    invalid,
                    f"putheader rejects {name!r}/{value!r} but tool accepts it",
                )
            elif invalid:
                divergences += 1
                self.assertTrue(
                    error_codes <= PUTHEADER_DIVERGENCE_CODES,
                    f"unexpected rejection of putheader-accepted "
                    f"{name!r}/{value!r}: {error_codes}",
                )
        self.assertGreater(rejects, 50, "oracle battery lost its hostile subpopulation")
        self.assertGreater(divergences, 20, "divergence adjudication never exercised")

    def test_putheader_oracle_300_fresh_seeds(self):
        """300 second-generation seeded pairs re-adjudicated against putheader.

        Hostile re-probe battery from the self-review: fresh generator mix
        (colon/whitespace-leading names, obs-fold continuations, non-latin-1
        values) under seed 20261021.
        """
        pairs = fresh_seeded_pairs(300, 20261021)
        rejects = 0
        divergences = 0
        for name, value in pairs:
            result = self.tool.execute("validate", name=name, value=value)
            error_codes = {
                f["code"] for f in result["findings"] if f["severity"] == "error"
            }
            if putheader_rejects(name, value):
                rejects += 1
                self.assertTrue(
                    error_codes,
                    f"putheader rejects {name!r}/{value!r} but tool accepts it",
                )
            elif error_codes:
                divergences += 1
                self.assertTrue(
                    error_codes <= PUTHEADER_DIVERGENCE_CODES,
                    f"unexpected rejection of putheader-accepted "
                    f"{name!r}/{value!r}: {error_codes}",
                )
        self.assertGreater(rejects, 100)
        self.assertGreater(divergences, 30)

    def test_rfc7230_hand_examples(self):
        """Hand-embedded RFC 7230 grammar examples."""
        # Section 3.2.4: no whitespace between field name and colon. putheader
        # accepts a space-suffixed name; the RFC token grammar does not.
        result = self.tool.execute("validate", name="X-Test ", value="1")
        self.assertFalse(result["name_valid"])
        self.assertIn("name_non_token", [f["code"] for f in result["findings"]])
        self.assertFalse(putheader_rejects("X-Test ", "1"))
        # Section 3.2.4 obs-fold example (continuation line).
        result = self.tool.execute("validate", name="X-Obj-1", value="Object type 1\r\n      ; to be continued")
        self.assertFalse(result["value_valid"])
        self.assertIn("value_obs_fold", [f["code"] for f in result["findings"]])
        # Section 3.2.6 token: full tchar alphabet as a name.
        tchar = "!#$%&'*+-.^_`|~0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        result = self.tool.execute("validate", name=tchar, value="v")
        self.assertTrue(result["name_valid"])
        # Empty name and empty value (section 3.2: field-name is 1*tchar).
        result = self.tool.execute("validate", name="", value="")
        self.assertFalse(result["name_valid"])
        self.assertTrue(result["value_valid"])
        self.assertIn("name_empty", [f["code"] for f in result["findings"]])
        # Bare CR and LF are injection vectors.
        result = self.tool.execute("validate", name="X", value="a\rX-Inj: 1")
        self.assertFalse(result["value_valid"])
        self.assertIn("value_cr_lf_injection", [f["code"] for f in result["findings"]])
        result = self.tool.execute("validate", name="X", value="a\nX-Inj: 1")
        self.assertFalse(result["value_valid"])
        self.assertIn("value_cr_lf_injection", [f["code"] for f in result["findings"]])
        # NUL truncation vector.
        result = self.tool.execute("validate", name="X", value="a\x00b")
        self.assertFalse(result["value_valid"])
        self.assertIn("value_nul", [f["code"] for f in result["findings"]])
        # Leading/trailing OWS tolerated with an info note.
        result = self.tool.execute("validate", name="X", value="  padded\t")
        self.assertTrue(result["value_valid"])
        self.assertTrue(any(f["code"].startswith("value_ows") for f in result["findings"]))

    def test_email_header_folding_is_obs_fold(self):
        """email.header folding output is adjudicated: MIME folds are obs-fold."""
        folded = email.header.Header("The quick brown fox jumps over the lazy dog", maxlinelen=20).encode()
        self.assertIn("\n", folded)  # the fold really happened
        result = self.tool.execute("validate", name="X-Subject", value=folded)
        self.assertFalse(result["value_valid"])
        self.assertIn("value_obs_fold", [f["code"] for f in result["findings"]])

    def test_known_field_cross_usage(self):
        """Host is request-only and Age is response-only; misuse is flagged."""
        result = self.tool.execute("validate", name="Host", value="example.com", which="request")
        self.assertEqual(result["field_category"], "request")
        self.assertFalse(any(f["code"] == "field_cross_usage" for f in result["findings"]))
        result = self.tool.execute("validate", name="Host", value="example.com", which="response")
        self.assertIn("field_cross_usage", [f["code"] for f in result["findings"]])
        result = self.tool.execute("validate", name="Age", value="3600", which="request")
        self.assertIn("field_cross_usage", [f["code"] for f in result["findings"]])
        result = self.tool.execute("validate", name="age", value="3600", which="response")
        self.assertEqual(result["field_category"], "response")
        self.assertFalse(any(f["code"] == "field_cross_usage" for f in result["findings"]))
        # Unknown fields are reported as unknown without findings.
        result = self.tool.execute("validate", name="X-Custom-Whatever", value="1")
        self.assertFalse(result["known_field"])
        self.assertIsNone(result["field_category"])

    def test_findings_carry_spans(self):
        """Every finding exposes a [start, end] character span."""
        result = self.tool.execute("validate", name="X Inj\x00ect", value="ok\r\n bad")
        for finding in result["findings"]:
            self.assertIn("span", finding)
            start, end = finding["span"]
            self.assertLessEqual(start, end)

    def test_validate_input_validation(self):
        """Strict validation: wrong types, bad which, oversized inputs."""
        for kwargs in (
            {"name": 1, "value": "v"},
            {"name": "X", "value": 2},
            {"name": "X", "value": "v", "which": "both; DROP"},
        ):
            result = self.tool.execute("validate", **kwargs)
            self.assertEqual(result["status"], "error")
            self.assertEqual(result["error_type"], "validation_error")
        long_name = "X" * (self.tool.max_name_len + 1)
        result = self.tool.execute("validate", name=long_name, value="v")
        self.assertEqual(result["status"], "error")
        self.assertIn("max_name_len", result["error"])
        long_value = "v" * (self.tool.max_value_len + 1)
        result = self.tool.execute("validate", name="X", value=long_value)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_value_len", result["error"])


class HttpHeaderParseListTest(unittest.TestCase):
    """Mode parse_list: RFC 7231 list semantics + independent reference parser."""

    def setUp(self):
        """Create a default-configured tool."""
        self.tool = HttpHeaderTool()

    def test_reference_parser_parity_200_seeds(self):
        """200 seeded values parse identically to the in-test reference parser."""
        for value in seeded_lists(200, 20260922):
            result = self.tool.execute("parse_list", value=value)
            self.assertEqual(result["status"], "success", value)
            reference = reference_list_parse(value)
            self.assertEqual(
                len(result["elements"]), len(reference),
                f"element count mismatch for {value!r}",
            )
            for element, (token, params, q, q_malformed) in zip(result["elements"], reference):
                self.assertEqual(element["token"], token, value)
                self.assertEqual(
                    [(p["name"], p["value"]) for p in element["params_list"]],
                    list(params), value,
                )
                self.assertEqual(element["q"], q, value)
                self.assertEqual(element["q_malformed"], q_malformed, value)

    def test_reference_parser_parity_200_fresh_values(self):
        """200 second-generation list values vs the independent reference.

        Fresh shapes from the self-review: unterminated quoted params, ';='
        chunks, duplicated q parameters, ',,' and ',\\t' joiners.
        """
        for value in fresh_seeded_lists(200, 20261022):
            result = self.tool.execute("parse_list", value=value)
            self.assertEqual(result["status"], "success", value)
            reference = reference_list_parse(value)
            self.assertEqual(len(result["elements"]), len(reference), value)
            for element, (token, params, q, q_malformed) in zip(result["elements"], reference):
                self.assertEqual(element["token"], token, value)
                self.assertEqual(
                    [(p["name"], p["value"]) for p in element["params_list"]],
                    list(params), value,
                )
                self.assertEqual(element["q"], q, value)
                self.assertEqual(element["q_malformed"], q_malformed, value)

    def test_accept_example(self):
        """The RFC 7231 section 5.3.2 Accept example parses element-wise."""
        result = self.tool.execute(
            "parse_list", value="text/plain; q=0.5, text/html, text/x-dvi; q=0.8, text/x-c"
        )
        tokens = [e["token"] for e in result["elements"]]
        self.assertEqual(tokens, ["text/plain", "text/html", "text/x-dvi", "text/x-c"])
        self.assertEqual([e["q"] for e in result["elements"]], [0.5, None, 0.8, None])
        self.assertEqual([e["order"] for e in result["elements"]], [0, 1, 2, 3])

    def test_quoted_strings_and_escapes(self):
        """Quoted commas do not split; quoted-pairs unescape in param values."""
        result = self.tool.execute("parse_list", value='a; x="1,2;3", b; y="q\\"z"')
        self.assertEqual(len(result["elements"]), 2)
        self.assertEqual(result["elements"][0]["params"]["x"], "1,2;3")
        self.assertEqual(result["elements"][1]["params"]["y"], 'q"z')

    def test_duplicate_tokens_and_empty_elements(self):
        """Duplicate tokens are kept; empty elements are counted and skipped."""
        result = self.tool.execute("parse_list", value="a, a ,a, , b")
        self.assertEqual([e["token"] for e in result["elements"]], ["a", "a", "a", "b"])
        self.assertEqual(result["empty_elements_ignored"], 1)

    def test_malformed_q_handling(self):
        """Malformed qvalues are flagged, not parsed."""
        result = self.tool.execute("parse_list", value="text/html;q=1.5, */*;q=abc, x;q")
        self.assertEqual([e["q_malformed"] for e in result["elements"]], [True, True, True])
        self.assertEqual([e["q"] for e in result["elements"]], [None, None, None])
        self.assertEqual([e["q_raw"] for e in result["elements"]], ["1.5", "abc", None])
        result = self.tool.execute("parse_list", value="x;q=0.1234")
        self.assertTrue(result["elements"][0]["q_malformed"])
        result = self.tool.execute("parse_list", value="x;q=0.123")
        self.assertEqual(result["elements"][0]["q"], 0.123)
        result = self.tool.execute("parse_list", value="x;q=1.000")
        self.assertEqual(result["elements"][0]["q"], 1.0)

    def test_set_cookie_warning(self):
        """Passing header=set-cookie produces the non-mergeable warning."""
        result = self.tool.execute(
            "parse_list",
            value="sid=abc; Expires=Wed, 09 Jun 2021 10:18:14 GMT",
            header="Set-Cookie",
        )
        self.assertTrue(any("Set-Cookie" in n for n in result["notes"]))

    def test_parse_list_input_validation(self):
        """Strict validation: non-string and oversized inputs fail cleanly."""
        result = self.tool.execute("parse_list", value=123)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.tool.max_list_elements = 2
        result = self.tool.execute("parse_list", value="a, b, c, d")
        self.assertEqual(result["status"], "error")
        self.assertIn("max_list_elements", result["error"])


class HttpHeaderSecurityAuditTest(unittest.TestCase):
    """Mode security_audit: OWASP secure-headers battery."""

    def setUp(self):
        """Create a default-configured tool and a fully hardened baseline."""
        self.tool = HttpHeaderTool()
        self.baseline_lines = {
            "strict-transport-security":
                "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
            "content-security-policy":
                "Content-Security-Policy: default-src 'none'; script-src 'self'",
            "x-content-type-options": "X-Content-Type-Options: nosniff",
            "referrer-policy": "Referrer-Policy: no-referrer",
            "permissions-policy": "Permissions-Policy: geolocation=()",
            "cache-control": "Cache-Control: no-store",
            "set-cookie": "Set-Cookie: sid=abc; Secure; HttpOnly; SameSite=Lax",
        }
        self.baseline = "\n".join(self.baseline_lines.values())

    def codes(self, headers):
        """Run the audit and return the (code, severity) pairs."""
        result = self.tool.execute("security_audit", headers=headers)
        self.assertEqual(result["status"], "success")
        return [(f["code"], f["severity"]) for f in result["findings"]]

    def codes_with(self, key, line):
        """Audit the baseline with one header line replaced (or dropped)."""
        lines = dict(self.baseline_lines)
        if line is None:
            lines.pop(key, None)
        else:
            lines[key] = line
        return self.codes("\n".join(lines.values()))

    def test_clean_baseline_has_no_findings(self):
        """A fully hardened header set produces zero findings."""
        self.assertEqual(self.codes(self.baseline), [])

    def test_missing_headers_each_reported_with_mitigation(self):
        """Each missing security header is reported with severity + mitigation text."""
        findings = self.tool.execute("security_audit", headers="Content-Type: text/html")["findings"]
        by_code = {f["code"]: f for f in findings}
        for code, severity in (
            ("hsts_missing", "medium"), ("csp_missing", "high"),
            ("xcto_missing", "medium"), ("referrer_policy_missing", "low"),
            ("permissions_policy_missing", "low"),
        ):
            self.assertEqual(by_code[code]["severity"], severity)
            self.assertGreater(len(by_code[code]["message"]), 40,
                               f"{code} message lacks mitigation text")
        # Cookie and caching checks on a sensitive-less response stay quiet.
        self.assertNotIn("cookie_missing_secure", by_code)
        self.assertNotIn("cache_control_missing_sensitive", by_code)

    def test_hsts_max_age_battery(self):
        """OWASP HSTS max-age ground truths: values, quotes, flags, overflow."""
        def hsts(value):
            codes_ = self.codes_with(
                "strict-transport-security",
                f"Strict-Transport-Security: {value}",
            )
            return {c for c, _ in codes_ if c.startswith("hsts")}
        self.assertEqual(hsts("max-age=31536000"), {"hsts_scope_limited"})
        self.assertEqual(hsts("max-age=31536000; includeSubDomains; preload"), set())
        self.assertIn("hsts_max_age_zero", hsts("max-age=0"))
        self.assertIn("hsts_max_age_low", hsts("max-age=15551999"))
        self.assertNotIn("hsts_max_age_low", hsts("max-age=15552000"))
        self.assertIn("hsts_max_age_invalid", hsts("max-age=-1"))
        self.assertIn("hsts_max_age_invalid", hsts('max-age="31536000"'))
        self.assertIn("hsts_max_age_invalid", hsts("max-age"))
        self.assertIn("hsts_max_age_overflow", hsts("max-age=999999999999"))
        self.assertIn("hsts_max_age_missing", hsts("includeSubDomains"))
        self.assertIn("hsts_duplicate_directive", hsts("max-age=1; max-age=2"))
        self.assertIn("hsts_unknown_directive", hsts("max-age=1; tomorrow"))

    def test_hsts_nonconforming_header_battery(self):
        """Self-review battery: RFC 6797 whole-header-ignore semantics.

        Section 6.1: "All directives MUST appear only once in an STS header
        field" and UAs MUST ignore any header that does not conform - so a
        duplicated directive (max-age, includeSubDomains, preload, or any
        other name) or an invalid delta-seconds voids the header; scope advice
        must be suppressed because no protection is applied at all.
        """
        def hsts(value):
            codes_ = self.codes_with(
                "strict-transport-security",
                f"Strict-Transport-Security: {value}",
            )
            return {c for c, _ in codes_ if c.startswith("hsts")}, {
                (c, s) for c, s in codes_ if c.startswith("hsts")
            }

        codes_, pairs = hsts("max-age=31536000; max-age=0")
        self.assertIn("hsts_duplicate_directive", codes_)
        self.assertIn(("hsts_duplicate_directive", "high"), pairs)
        self.assertNotIn("hsts_scope_limited", codes_)
        # invalid first max-age: the second must NOT resurrect the header
        codes_, pairs = hsts("max-age=abc; max-age=31536000")
        self.assertIn("hsts_max_age_invalid", codes_)
        self.assertIn("hsts_duplicate_directive", codes_)
        self.assertIn("hsts_max_age_missing", codes_)
        self.assertNotIn("hsts_scope_limited", codes_)
        for value in (
            "max-age=31536000; includeSubDomains; includeSubDomains",
            "max-age=31536000; preload; preload",
            "max-age=1; tomorrow; tomorrow",
            'max-age="abc"', "max-age=+100", "max-age=1e6",
        ):
            codes_, _ = hsts(value)
            self.assertNotIn("hsts_scope_limited", codes_, value)
        codes_, _ = hsts("max-age=31536000; includeSubDomains; preload")
        self.assertEqual(codes_, set())

    def test_csp_edge_grammar_battery(self):
        """Self-review battery: CSP3 ignore rules and source grammar.

        Pins: 'unsafe-inline' ignored when a nonce/hash shares the source
        list; host allowlists inert under 'strict-dynamic'; unquoted nonce-/
        hash- tokens are host-sources; empty sandbox is valid (maximum
        restrictions) while an empty require-trusted-types-for is not (it
        requires "'script'"); report-uri deprecation and report-to without a
        Reporting-Endpoints declaration.
        """
        def csp(value, extra=""):
            codes_ = self.codes_with("content-security-policy",
                                     f"Content-Security-Policy: {value}")
            if extra:
                codes_ = self.codes(
                    self.baseline + f"\nContent-Security-Policy: {value}\n{extra}")
            return codes_

        # quoted nonce + hash stay clean
        codes_ = csp("script-src 'self' 'nonce-R2lrL3Bvc3Q=' 'sha256-abc123'")
        self.assertNotIn(("csp_unsafe_inline", "high"), codes_)
        self.assertNotIn(("csp_unquoted_nonce_or_hash", "low"), codes_)
        # nonce suppresses 'unsafe-inline' (info, not high)
        codes_ = csp("script-src 'self' 'nonce-AbC123' 'unsafe-inline'")
        self.assertNotIn(("csp_unsafe_inline", "high"), codes_)
        self.assertIn(("csp_unsafe_inline_ignored_by_nonce", "info"), codes_)
        # hash suppresses 'unsafe-inline' too; without either it stays high
        codes_ = csp("style-src 'sha256-abc' 'unsafe-inline'")
        self.assertNotIn(("csp_unsafe_inline", "high"), codes_)
        self.assertIn(("csp_unsafe_inline_ignored_by_nonce", "info"), codes_)
        self.assertIn(("csp_unsafe_inline", "high"),
                      csp("script-src 'self' 'unsafe-inline'"))
        # 'strict-dynamic' ignores 'unsafe-inline' as well (any allowlist/
        # source expression is ignored per CSP3)
        codes_ = csp("script-src 'strict-dynamic' 'nonce-AbC123' 'unsafe-inline'")
        self.assertNotIn(("csp_unsafe_inline", "high"), codes_)
        self.assertIn(("csp_unsafe_inline_ignored_by_nonce", "info"), codes_)
        # 'strict-dynamic' makes plaintext host sources inert
        codes_ = csp("script-src 'strict-dynamic' 'nonce-AbC123' http://cdn.example.com")
        self.assertNotIn(("csp_insecure_source", "medium"), codes_)
        self.assertIn(("csp_insecure_source_ignored_by_strict_dynamic", "info"), codes_)
        self.assertIn(("csp_insecure_source", "medium"),
                      csp("script-src http: 'self'"))
        # unquoted nonce-/hash- tokens are host-sources, never applied
        for token in ("nonce-AbC123", "sha256-AbC123"):
            codes_ = csp(f"script-src 'self' {token}")
            self.assertIn(("csp_unquoted_nonce_or_hash", "low"), codes_, token)
        # empty sandbox is valid (maximum restrictions)
        codes_ = csp("default-src 'self'; sandbox")
        self.assertNotIn(("csp_empty_directive", "info"), codes_)
        self.assertNotIn(("csp_empty_directive", "info"),
                         csp("default-src 'self'; sandbox allow-scripts"))
        # empty require-trusted-types-for is grammar-invalid ('script' required)
        codes_ = csp("default-src 'self'; require-trusted-types-for")
        self.assertIn(("csp_empty_directive", "info"), codes_)
        self.assertNotIn(("csp_empty_directive", "info"),
                         csp("default-src 'self'; require-trusted-types-for 'script'"))
        # report-uri deprecated; report-to needs an endpoint declaration
        codes_ = csp("default-src 'self'; report-uri /csp-report")
        self.assertIn(("csp_report_uri_deprecated", "info"), codes_)
        codes_ = csp("default-src 'self'; report-to csp-endpoint")
        self.assertIn(("csp_report_to_no_endpoints", "info"), codes_)
        codes_ = csp("default-src 'self'; report-to csp-endpoint",
                     extra='Reporting-Endpoints: csp-endpoint="https://r.example/r"')
        self.assertNotIn(("csp_report_to_no_endpoints", "info"), codes_)

    def test_csp_directive_battery(self):
        """CSP3-spec-derived directive battery: flags, fallbacks, deprecated."""
        def csp(value, extra_deprecated=False):
            line = f"Content-Security-Policy: {value}"
            codes_ = self.codes_with("content-security-policy", line)
            if extra_deprecated:
                codes_ = self.codes(self.baseline + "\nX-WebKit-CSP: default-src 'none'\n"
                                    "X-Content-Security-Policy: default-src 'none'")
            return codes_

        codes_ = csp("default-src 'none'; script-src 'self'; connect-src 'self'; "
                     "img-src 'self'; style-src 'self'; frame-ancestors 'self'")
        self.assertEqual([c for c, _ in codes_ if c.startswith("csp")], [])
        result = self.tool.execute(
            "security_audit",
            headers="Content-Security-Policy: script-src 'self' https://example.com 'nonce-abc123'",
        )
        self.assertEqual(
            result["csp_directives"],
            [{"name": "script-src", "values": ["'self'", "https://example.com", "'nonce-abc123'"]}],
        )
        self.assertIn(("csp_unsafe_inline", "high"),
                      csp("script-src 'self' 'unsafe-inline'"))
        self.assertIn(("csp_unsafe_eval", "medium"),
                      csp("default-src 'unsafe-eval'"))
        codes_ = csp("style-src 'self' 'unsafe-inline' 'unsafe-eval'")
        self.assertIn(("csp_unsafe_inline", "high"), codes_)
        self.assertIn(("csp_unsafe_eval", "medium"), codes_)
        self.assertIn(("csp_insecure_source", "medium"), csp("script-src http: 'self'"))
        self.assertIn(("csp_insecure_source", "medium"),
                      csp("script-src http://static.example.com"))
        self.assertNotIn(("csp_empty_directive", "info"),
                         csp("upgrade-insecure-requests"))
        self.assertIn(("csp_empty_directive", "info"),
                      csp("script-src 'self'; img-src"))
        self.assertIn(("csp_none_with_sources", "info"), csp("script-src 'none' 'self'"))
        self.assertIn(("csp_no_default_src", "low"), csp("script-src 'self'"))
        self.assertIn(("csp_unknown_directive", "info"), csp("not-a-directive 'self'"))
        self.assertEqual(csp("", extra_deprecated=True).count(("csp_header_deprecated", "low")), 2)

    def test_xfo_battery(self):
        """X-Frame-Options: valid, case-insensitive, deprecated, invalid."""
        self.assertNotIn(("xfo_invalid", "medium"), self.codes("X-Frame-Options: DENY"))
        self.assertNotIn(("xfo_invalid", "medium"), self.codes("X-Frame-Options: deny"))
        self.assertNotIn(("xfo_invalid", "medium"), self.codes("X-Frame-Options: SAMEORIGIN"))
        self.assertIn(("xfo_allow_from_deprecated", "medium"),
                      self.codes("X-Frame-Options: ALLOW-FROM https://example.com"))
        for bad in ("SAMEORIGIN, DENY", "invalid", ""):
            self.assertIn(("xfo_invalid", "medium"), self.codes(f"X-Frame-Options: {bad}"))

    def test_xss_protection_and_xcto(self):
        """X-XSS-Protection deprecation and X-Content-Type-Options values."""
        self.assertIn(("xss_filter_deprecated", "low"), self.codes("X-XSS-Protection: 1; mode=block"))
        self.assertIn(("xss_filter_disabled", "info"), self.codes("X-XSS-Protection: 0"))
        self.assertNotIn("xss_filter_deprecated", {c for c, _ in self.codes("Content-Type: text/html")})
        self.assertNotIn(("xcto_invalid", "medium"), self.codes("X-Content-Type-Options: nosniff"))
        self.assertNotIn(("xcto_invalid", "medium"), self.codes("X-Content-Type-Options: Nosniff"))
        self.assertIn(("xcto_invalid", "medium"), self.codes("X-Content-Type-Options: no-sniff"))

    def test_caching_on_sensitive_responses(self):
        """Sensitive responses need no-store; others are not flagged."""
        sensitive = "Set-Cookie: sid=abc"
        self.assertIn(("cache_control_missing_sensitive", "medium"), self.codes(sensitive))
        self.assertIn(("cache_control_no_store_missing", "medium"),
                      self.codes(sensitive + "\nCache-Control: private, max-age=0"))
        clean = sensitive + "\nCache-Control: no-store"
        self.assertNotIn(("cache_control_no_store_missing", "medium"), self.codes(clean))
        self.assertNotIn(("cache_control_missing_sensitive", "medium"),
                         self.codes("Content-Type: text/html"))

    def test_cookie_and_info_leak_battery(self):
        """Cookie attribute findings and Server/X-Powered-By notes."""
        codes_ = self.codes("Set-Cookie: sid=abc")
        self.assertIn(("cookie_missing_secure", "high"), codes_)
        self.assertIn(("cookie_missing_httponly", "medium"), codes_)
        self.assertIn(("cookie_missing_samesite", "low"), codes_)
        codes_ = self.codes("Set-Cookie: sid=abc; SameSite=None")
        self.assertIn(("cookie_samesite_none_requires_secure", "high"), codes_)
        codes_ = self.codes("Set-Cookie: sid=abc; Secure; HttpOnly; SameSite=None")
        self.assertNotIn(("cookie_samesite_none_requires_secure", "high"), codes_)
        codes_ = self.codes("Server: nginx/1.19.3\nX-Powered-By: PHP/7.4")
        self.assertEqual(codes_.count(("server_version_info_leak", "low")), 2)

    def test_audit_structural_edges(self):
        """Malformed lines, duplicates, caps, and the summary are handled."""
        result = self.tool.execute("security_audit", headers="garbage line without colon\nX: 1\nX: 2")
        self.assertIn(("audit_duplicate_header", "info"),
                      [(f["code"], f["severity"]) for f in result["findings"]])
        self.assertIn("audit_line_unparsed", [f["code"] for f in result["findings"]])
        counts = result["summary"]["by_severity"]
        self.assertEqual(result["summary"]["finding_count"], sum(counts.values()))
        result = self.tool.execute("security_audit", headers="X" * 70000)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_audit_bytes", result["error"])
        result = self.tool.execute("security_audit", headers="\n".join(f"H{i}: v" for i in range(205)))
        self.assertEqual(result["status"], "error")
        self.assertIn("max_audit_lines", result["error"])
        result = self.tool.execute("security_audit", headers=5)
        self.assertEqual(result["status"], "error")


class HttpHeaderParseCookieTest(unittest.TestCase):
    """Mode parse_cookie: RFC 6265 parsing + http.cookies.SimpleCookie oracle."""

    def setUp(self):
        """Create a default-configured tool."""
        self.tool = HttpHeaderTool()

    def test_basic_attributes(self):
        """A fully attributed Set-Cookie parses into typed attributes."""
        result = self.tool.execute(
            "parse_cookie",
            value="sid=abc; Expires=Wed, 09 Jun 2021 10:18:14 GMT; Max-Age=3600; "
                  "Domain=.Example.com; Path=/app; Secure; HttpOnly; SameSite=Lax",
        )
        attributes = result["attributes"]
        self.assertEqual(result["name"], "sid")
        self.assertEqual(result["value"], "abc")
        self.assertEqual(attributes["expires"]["parsed"]["iso"], "2021-06-09T10:18:14Z")
        self.assertEqual(attributes["max_age"], 3600)
        self.assertEqual(attributes["domain"], "example.com")
        self.assertEqual(attributes["path"], "/app")
        self.assertTrue(attributes["secure"])
        self.assertTrue(attributes["httponly"])
        self.assertEqual(attributes["samesite"], "Lax")
        self.assertEqual(result["size"], 6)

    def test_simplecookie_oracle_150_seeds(self):
        """150 seeded Set-Cookies adjudicated against http.cookies.SimpleCookie."""
        aligned = diverged = dropped = 0
        for raw in seeded_cookies(150, 20260923):
            simple = http.cookies.SimpleCookie()
            try:
                simple.load(raw)
                simple_error = None
            except http.cookies.CookieError as exc:
                simple.clear()
                simple_error = str(exc)
            result = self.tool.execute("parse_cookie", value=raw)
            issue_codes = {i["code"] for i in result.get("rfc6265_strict", [])}

            if simple_error is not None or not simple:
                # SimpleCookie dropped (or raised): the pair must be either
                # aligned-dropped (missing '=' / empty name) or kept with an
                # issue documenting the divergence. Pinned SimpleCookie
                # artifacts: it drops the whole string on an invalid Expires
                # containing a space, on illegal key characters, and on any
                # valueless ';'-chunk (RFC 6265 keeps flags/unknown attributes).
                dropped += 1
                if result.get("ignored"):
                    self.assertIn(result["reason"], ("missing_equals", "empty_name"))
                else:
                    self.assertFalse(result["ignored"])
                    self.assertTrue(
                        issue_codes & {
                            "cookie_name_illegal_char", "cookie_value_illegal_char",
                            "cookie_expires_invalid", "cookie_pair_trimmed",
                            "cookie_unknown_attribute",
                        },
                        f"divergence for {raw!r} lacks an issue: {issue_codes}",
                    )
                continue

            first_name, first_morsel = next(iter(simple.items()))
            if result.get("ignored"):
                # SimpleCookie kept something but RFC 6265 ignores the string.
                dropped += 1
                self.assertIn(result["reason"], ("missing_equals", "empty_name"))
                continue

            aligned += 1
            self.assertEqual(result["name"], first_name, raw)
            if result["quoted"]:
                # Pinned divergence: SimpleCookie unquotes, RFC 6265 keeps raw.
                diverged += 1
                self.assertEqual(result["value"][1:-1], first_morsel.value, raw)
                self.assertIn("cookie_value_quoted", issue_codes)
            else:
                self.assertEqual(result["value"], first_morsel.value, raw)
        self.assertGreater(aligned, 40)
        self.assertGreater(dropped, 10)
        self.assertGreater(diverged, 0)

    def test_dollar_path_dollar_domain_not_processed(self):
        """$Path/$Domain must NOT be attached to the cookie (unlike SimpleCookie)."""
        raw = "sid=abc; $Path=/x; $Domain=example.com"
        simple = http.cookies.SimpleCookie()
        simple.load(raw)
        # SimpleCookie (RFC 2109 mode) attaches $Domain to the preceding cookie.
        self.assertEqual(dict(simple["sid"]).get("domain"), "example.com")
        result = self.tool.execute("parse_cookie", value=raw)
        self.assertEqual(result["name"], "sid")
        self.assertEqual(result["value"], "abc")
        self.assertIsNone(result["attributes"]["domain"])
        self.assertIsNone(result["attributes"]["path"])
        codes_ = {i["code"] for i in result["rfc6265_strict"]}
        self.assertIn("cookie_legacy_rfc2965_attribute", codes_)
        self.assertTrue(
            {"$Path", "$Domain"} <= {a["name"] for a in result["unknown_attributes"]}
        )

    def test_invalid_expires_divergence(self):
        """Invalid Expires: SimpleCookie stores it silently; RFC 6265 ignores it.

        SimpleCookie performs no cookie-date validation; a space inside an
        attribute value additionally makes SimpleCookie drop the whole string
        (a parse artifact, not a date check) - both pinned here.
        """
        raw = "sid=abc; Expires=never"
        simple = http.cookies.SimpleCookie()
        simple.load(raw)
        self.assertEqual(dict(simple["sid"]).get("expires"), "never")
        result = self.tool.execute("parse_cookie", value=raw)
        self.assertFalse(result["ignored"])
        self.assertEqual(result["name"], "sid")
        self.assertIsNone(result["attributes"]["expires"]["parsed"])
        self.assertIn("cookie_expires_invalid", {i["code"] for i in result["rfc6265_strict"]})
        with_space = "sid=abc; expires=invalid date"
        simple = http.cookies.SimpleCookie()
        simple.load(with_space)
        self.assertEqual(len(simple), 0)
        result = self.tool.execute("parse_cookie", value=with_space)
        self.assertFalse(result["ignored"])
        self.assertEqual(result["name"], "sid")
        self.assertIn("cookie_expires_invalid", {i["code"] for i in result["rfc6265_strict"]})

    def test_samesite_rules(self):
        """SameSite values are validated; None requires Secure."""
        result = self.tool.execute("parse_cookie", value="s=1; SameSite=None")
        self.assertIn("cookie_samesite_none_requires_secure",
                      {i["code"] for i in result["rfc6265_strict"]})
        result = self.tool.execute("parse_cookie", value="s=1; SameSite=None; Secure")
        self.assertNotIn("cookie_samesite_none_requires_secure",
                         {i["code"] for i in result["rfc6265_strict"]})
        result = self.tool.execute("parse_cookie", value="s=1; samesite=lax")
        self.assertEqual(result["attributes"]["samesite"], "lax")
        result = self.tool.execute("parse_cookie", value="s=1; SameSite=sometimes")
        self.assertIn("cookie_samesite_invalid", {i["code"] for i in result["rfc6265_strict"]})

    def test_strict_issues_and_ignores(self):
        """Ignore rules, trimming, flags-with-values, and caps."""
        result = self.tool.execute("parse_cookie", value="novalue; Path=/")
        self.assertTrue(result["ignored"])
        self.assertEqual(result["reason"], "missing_equals")
        result = self.tool.execute("parse_cookie", value="=nokey; Path=/")
        self.assertTrue(result["ignored"])
        self.assertEqual(result["reason"], "empty_name")
        result = self.tool.execute("parse_cookie", value="  spaced  =  val  ")
        self.assertEqual(result["name"], "spaced")
        self.assertEqual(result["value"], "val")
        self.assertIn("cookie_pair_trimmed", {i["code"] for i in result["rfc6265_strict"]})
        result = self.tool.execute("parse_cookie", value="s=1; Secure=true; HttpOnly=yes")
        self.assertTrue(result["attributes"]["secure"])
        self.assertTrue(result["attributes"]["httponly"])
        self.assertIn("cookie_secure_with_value", {i["code"] for i in result["rfc6265_strict"]})
        self.assertIn("cookie_httponly_with_value", {i["code"] for i in result["rfc6265_strict"]})
        result = self.tool.execute("parse_cookie", value="s=1; Max-Age=soon")
        self.assertIsNone(result["attributes"]["max_age"])
        self.assertIn("cookie_max_age_invalid", {i["code"] for i in result["rfc6265_strict"]})
        result = self.tool.execute("parse_cookie", value="s=1; Path=relative")
        self.assertIsNone(result["attributes"]["path"])
        result = self.tool.execute("parse_cookie", value="x" * 9000)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_cookie_len", result["error"])
        result = self.tool.execute("parse_cookie", value=None)
        self.assertEqual(result["status"], "error")


class HttpHeaderCookieDateTest(unittest.TestCase):
    """RFC 6265 section 5.1.1 cookie-date algorithm: 60 hand-derived cases."""

    def setUp(self):
        """Create a default-configured tool."""
        self.tool = HttpHeaderTool()

    def date_of(self, raw):
        """Run the cookie-date algorithm directly (attribute plumbing is
        covered by the parse_cookie tests; Expires cannot carry ';')."""
        parsed = header_module._cookie_date(raw)
        if parsed is None:
            return None
        return (
            parsed["year"], parsed["month"], parsed["day"],
            parsed["hour"], parsed["minute"], parsed["second"],
            parsed["calendar_valid"],
        )

    def test_cookie_date_battery(self):
        """60 hand-derived expectations for the lenient cookie-date algorithm."""
        cases = [
            # (expires value, expected components or None)
            ("Wed, 09 Jun 2021 10:18:14 GMT", (2021, 6, 9, 10, 18, 14, True)),
            ("Wed, 09-Jun-2021 10:18:14 GMT", (2021, 6, 9, 10, 18, 14, True)),
            ("Sun, 06 Nov 1994 08:49:37 GMT", (1994, 11, 6, 8, 49, 37, True)),
            ("Sunday, 06-Nov-94 08:49:37 GMT", (1994, 11, 6, 8, 49, 37, True)),
            ("Sun Nov  6 08:49:37 1994", (1994, 11, 6, 8, 49, 37, True)),
            ("Wed, 09 Jun 21 10:18:14 GMT", (2021, 6, 9, 10, 18, 14, True)),
            ("Wed, 09 Jun 69 10:18:14 GMT", (2069, 6, 9, 10, 18, 14, True)),
            ("Wed, 09 Jun 70 10:18:14 GMT", (1970, 6, 9, 10, 18, 14, True)),
            ("Thu, 01 Jan 1970 00:00:00 GMT", (1970, 1, 1, 0, 0, 0, True)),
            ("Wed, 09 Jun 1601 10:18:14 GMT", (1601, 6, 9, 10, 18, 14, True)),
            ("Wed, 09 Jun 1600 10:18:14 GMT", None),          # year < 1601
            ("Wed, 09 Jun 2021 10:18:14", (2021, 6, 9, 10, 18, 14, True)),
            ("WED, 09 JUN 2021 10:18:14 gmt", (2021, 6, 9, 10, 18, 14, True)),
            ("Wed, 09 JUNE 2021 10:18:14 GMT", (2021, 6, 9, 10, 18, 14, True)),
            ("Wed, 09 Junius 2021 10:18:14 GMT", (2021, 6, 9, 10, 18, 14, True)),
            ("Wed, 09 jun 2021 10:18:14 GMT", (2021, 6, 9, 10, 18, 14, True)),
            ("10:18:14 09 Jun 2021", (2021, 6, 9, 10, 18, 14, True)),
            ("Jun 09 10:18:14 2021", (2021, 6, 9, 10, 18, 14, True)),
            ("2021 Jun 09 10:18:14", (2021, 6, 9, 10, 18, 14, True)),
            ("09 2021 Jun 10:18:14", (2021, 6, 9, 10, 18, 14, True)),
            ("Wed;09;Jun;2021;10:18:14;GMT", (2021, 6, 9, 10, 18, 14, True)),
            ("Wed,09 Jun 2021 10:18:14 GMT", (2021, 6, 9, 10, 18, 14, True)),
            ("Wed, 09 Jun 2021 10:18:14 GMT ", (2021, 6, 9, 10, 18, 14, True)),
            ("  Wed, 09 Jun 2021 10:18:14 GMT", (2021, 6, 9, 10, 18, 14, True)),
            ("Wed, 09 Jun 2021 10:18:14\tGMT", (2021, 6, 9, 10, 18, 14, True)),
            ("Jun\t09\t2021\t10:18:14", (2021, 6, 9, 10, 18, 14, True)),
            ("25 Dec 2021 00:00:00", (2021, 12, 25, 0, 0, 0, True)),
            ("1 Jan 1601 00:00:00", (1601, 1, 1, 0, 0, 0, True)),
            ("9:8:4 9 Jun 2021", (2021, 6, 9, 9, 8, 4, True)),
            ("09:09:09 9 Jun 2021", (2021, 6, 9, 9, 9, 9, True)),
            ("Wed, 09 Jun 2021 23:59:59 GMT", (2021, 6, 9, 23, 59, 59, True)),
            ("Wed, 09 Jun 2021 10:18:14.5 GMT", (2021, 6, 9, 10, 18, 14, True)),
            ("12th Jun 2021 10:18:14", (2021, 6, 12, 10, 18, 14, True)),
            ("12.5 Jun 2021 10:18:14", (2021, 6, 12, 10, 18, 14, True)),
            ("1e2 Jun 2021 10:18:14", (2021, 6, 1, 10, 18, 14, True)),
            # a second time token takes day-of-month, and "09" then takes the
            # year slot (sticky flags) -> year 2009, day 10
            ("10:18:14 10:18:15 09 Jun 2021", (2009, 6, 10, 10, 18, 14, True)),
            ("09 Jun 2021 10:18:14 10:18:15", (2021, 6, 9, 10, 18, 14, True)),
            # calendar-invalid but algorithm-legal dates (no day/month cross-check)
            ("Wed, 31 Feb 2021 10:18:14 GMT", (2021, 2, 31, 10, 18, 14, False)),
            ("30 Feb 2021 10:18:14", (2021, 2, 30, 10, 18, 14, False)),
            ("29 Feb 2021 10:18:14", (2021, 2, 29, 10, 18, 14, False)),
            ("29 Feb 2020 10:18:14", (2020, 2, 29, 10, 18, 14, True)),
            ("29 Feb 2000 10:18:14", (2000, 2, 29, 10, 18, 14, True)),
            ("29 Feb 1900 10:18:14", (1900, 2, 29, 10, 18, 14, False)),
            ("Sep 31 1999 23:59:59 GMT", (1999, 9, 31, 23, 59, 59, False)),
            # failures: ranges, missing components, structure
            ("Wed, 00 Feb 2021 10:18:14 GMT", None),          # day < 1
            ("Wed, 32 Feb 2021 10:18:14 GMT", None),          # day > 31
            ("Wed, 99 Jun 2021 10:18:14 GMT", None),          # day > 31
            ("Wed, 09 Jun 2021 24:18:14 GMT", None),          # hour > 23
            ("Wed, 09 Jun 2021 10:60:14 GMT", None),          # minute > 59
            ("Wed, 09 Jun 2021 10:18:60 GMT", None),          # second > 59
            ("99:09:09 9 Jun 2021", None),                    # hour > 23
            ("10:99:09 9 Jun 2021", None),                    # minute > 59
            ("10:09:99 9 Jun 2021", None),                    # second > 59
            ("Wed, 09 Jun 2021 10:18", None),                 # no seconds
            ("Wed, 09 Jun 2021", None),                       # no time
            ("Wed, 09 10:18:14 GMT", None),                   # no month/year
            ("10:18:14 GMT", None),                           # no day/month/year
            ("010:09:09 9 Jun 2021", None),                   # 3-digit hour eats year
            ("2021st Jun 2020 10:18:14", None),               # year eats day slot
            ("999999 Jun 2021 10:18:14", None),               # unmatchable numbers
            ("09 Jün 2021 10:18:14", None),                   # non-ASCII month
            ("", None),
            ("   ", None),
            ("2021-06-09T10:18:14Z", None),                   # ISO is not a cookie-date
        ]
        self.assertGreaterEqual(len(cases), 60)
        for raw, expected in cases:
            self.assertEqual(self.date_of(raw), expected, f"cookie-date {raw!r}")

    def test_cookie_date_battery_55_fresh_cases(self):
        """55 disjoint hand-derived cookie-date cases (self-review battery).

        Re-derived during the hostile re-probe against an independent
        transliteration of RFC 6265 section 5.1.1; '.' being a delimiter is
        pinned by the 11:22:33.5 case ('15' then takes the year slot).
        """
        cases = [
            ("Fri, 31 Dec 2021 23:59:59 GMT", (2021, 12, 31, 23, 59, 59, True)),
            ("Sat, 01 Jan 2000 00:00:00 GMT", (2000, 1, 1, 0, 0, 0, True)),
            ("Tue, 29 Feb 2000 12:00:00 GMT", (2000, 2, 29, 12, 0, 0, True)),
            ("Mon, 28 Feb 2022 12:00:00 GMT", (2022, 2, 28, 12, 0, 0, True)),
            ("Wed, 29 Feb 2023 12:00:00 GMT", (2023, 2, 29, 12, 0, 0, False)),
            ("Thu, 04 Jul 2002 12:34:56 GMT", (2002, 7, 4, 12, 34, 56, True)),
            ("04 Jul 2002 12:34:56", (2002, 7, 4, 12, 34, 56, True)),
            ("Jul 4 2002 12:34:56", (2002, 7, 4, 12, 34, 56, True)),
            ("4 Jul 2002 12:34:56", (2002, 7, 4, 12, 34, 56, True)),
            ("2002 Jul 4 12:34:56", (2002, 7, 4, 12, 34, 56, True)),
            ("12:34:56 4 Jul 2002", (2002, 7, 4, 12, 34, 56, True)),
            ("Feb 30 2021 00:00:00", (2021, 2, 30, 0, 0, 0, False)),
            ("Feb 29 2024 00:00:00", (2024, 2, 29, 0, 0, 0, True)),
            ("Feb 29 2100 00:00:00", (2100, 2, 29, 0, 0, 0, False)),
            ("Feb 29 1600 00:00:00", None),          # year < 1601
            ("Dec 31 1969 23:59:59", (1969, 12, 31, 23, 59, 59, True)),
            ("31 Dec 99 23:59:59", (1999, 12, 31, 23, 59, 59, True)),
            ("31 Dec 68 23:59:59", (2068, 12, 31, 23, 59, 59, True)),
            ("31 Dec 69 23:59:59", (2069, 12, 31, 23, 59, 59, True)),
            ("31 Dec 70 23:59:59", (1970, 12, 31, 23, 59, 59, True)),
            ("Jan 1 100 00:00:00", None),            # 3-digit year stays 100
            ("Jan 1 1601 00:00:00", (1601, 1, 1, 0, 0, 0, True)),
            ("Sat, 02 Jan 9999 00:00:00 GMT", (9999, 1, 2, 0, 0, 0, True)),
            ("Sat, 02 Jan 10000 00:00:00 GMT", None),  # 5-digit year
            ("Jan 1 00 00:00:00", (2000, 1, 1, 0, 0, 0, True)),
            ("Jan 1 0 00:00:00", None),              # 1-digit year unmatchable
            ("Dec 25 (Christmas) 2021 00:00:00", (2021, 12, 25, 0, 0, 0, True)),
            ("Fri Dec 31 2021 24:00:00", None),      # hour 24
            ("Fri Dec 31 2021 12:60:00", None),      # minute 60
            ("Fri Dec 31 2021 12:30:61", None),      # second 61
            ("00:00:00 Dec 31 2021", (2021, 12, 31, 0, 0, 0, True)),
            ("23:59:59 31 Dec 2021", (2021, 12, 31, 23, 59, 59, True)),
            ("1:1:1 1 Jan 2001", (2001, 1, 1, 1, 1, 1, True)),
            ("01:01:01 Jan 2001", None),             # no day
            ("Nov 15 2021", None),                   # no time
            ("Mon, 15-Nov-2021 11:22:33 GMT", (2021, 11, 15, 11, 22, 33, True)),
            ("Mon,15 Nov 2021 11:22:33 GMT", (2021, 11, 15, 11, 22, 33, True)),
            ("MONDAY, 15 NOVEMBER 2021 11:22:33 GMT", (2021, 11, 15, 11, 22, 33, True)),
            ("Mon, 15 Nov 2021 11:22:33 +0100", (2021, 11, 15, 11, 22, 33, True)),
            ("Mon, 15 Nov 2021 11:22:33 GMT extra 99", (2021, 11, 15, 11, 22, 33, True)),
            ("Nov 2021 15 11:22:33", (2021, 11, 15, 11, 22, 33, True)),
            ("Sep 31 2021 00:00:00", (2021, 9, 31, 0, 0, 0, False)),
            ("Apr 31 2021 00:00:00", (2021, 4, 31, 0, 0, 0, False)),
            ("Jun 31 2021 00:00:00", (2021, 6, 31, 0, 0, 0, False)),
            ("Aug 32 2021 00:00:00", None),          # day > 31
            ("Aug 0 2021 00:00:00", None),           # day < 1
            ("Déc 15 2021 00:00:00", None),          # non-ASCII month
            ("Mon, 15 Nov 2021 11:22:33.999 GMT", (2021, 11, 15, 11, 22, 33, True)),
            ("Mon, 15 Nov 2021 11:22 GMT", None),    # no seconds
            ("11:22:33.5 15 Nov 2021", (2015, 11, 5, 11, 22, 33, True)),
            ("Nov\t15\t2021\t11:22:33", (2021, 11, 15, 11, 22, 33, True)),
            ("Mon; 15; Nov; 2021; 11:22:33", (2021, 11, 15, 11, 22, 33, True)),
            ("15 Nov 2021 11:22:33 16 Nov 2021", (2021, 11, 15, 11, 22, 33, True)),
            ("Sat, 05 May 2001 05:05:05 GMT", (2001, 5, 5, 5, 5, 5, True)),
            ("10:18:14:15 9 Jun 2021", (2021, 6, 9, 10, 18, 14, True)),
        ]
        self.assertGreaterEqual(len(cases), 55)
        for raw, expected in cases:
            self.assertEqual(self.date_of(raw), expected, f"cookie-date {raw!r}")

    def test_calendar_invalid_flag_semantics(self):
        """Algorithm-legal but calendar-invalid dates keep components + flag."""
        parsed = header_module._cookie_date("Wed, 31 Feb 2021 10:18:14 GMT")
        self.assertEqual((parsed["year"], parsed["month"], parsed["day"]), (2021, 2, 31))
        self.assertFalse(parsed["calendar_valid"])
        self.assertIsNone(parsed["iso"])


class HttpHeaderRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped http_header_tool.yaml."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the shipped yaml resolves to a tool component exposing HttpHeaderTool."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "HttpHeaderTool")

    def test_manager(self):
        """Verify the HttpHeaderTool is resolvable via ToolManager with its input keys."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, HttpHeaderTool)
        self.assertEqual(tool.input_keys, ["mode"])


class HttpHeaderDeterminismTest(unittest.TestCase):
    """Determinism and dispatch checks."""

    def setUp(self):
        """Create a default-configured tool."""
        self.tool = HttpHeaderTool()

    def test_repeated_calls_identical(self):
        """Repeated audits of the same input return byte-identical results."""
        headers = "Server: x\nSet-Cookie: s=1\nX-Frame-Options: bogus"
        first = self.tool.execute("security_audit", headers=headers)
        for _ in range(5):
            self.assertEqual(self.tool.execute("security_audit", headers=headers), first)

    def test_mode_dispatch_and_errors(self):
        """Unknown modes, wrong argument types, and case-insensitive modes."""
        result = self.tool.execute("bogus")
        self.assertEqual(result["status"], "error")
        self.assertIn("mode must be", result["error"])
        result = self.tool.execute(mode=1)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        result = self.tool.execute("VALIDATE", name="X", value="1")
        self.assertEqual(result["status"], "success")
        result = self.tool.execute("validate")
        self.assertEqual(result["status"], "error")
        self.assertIn("name must be a string", result["error"])


if __name__ == "__main__":
    unittest.main()
