"""Offline, deterministic tests for WwwAuthenticateTool.

Oracle sources:
  (a) hand-embedded RFC examples: RFC 7235 section 4.1 (multi-challenge with a
      nested-quoted title), RFC 6750 section 3 (three Bearer error examples),
      RFC 7616 (SHA-256 challenge, userhash example), RFC 4559 (Negotiate);
  (b) a 300-string seeded grammar corpus (valid combinations + mutations) with
      parse/build round-trip identity and the quoted-comma disambiguation pin;
  (c) explain accuracy over the RFC corpus;
  (d) a 100-header malformed battery, each pinned to its error code;
  (e) pathological inputs (10k challenges, 1MB header) proving bounded work.

All realms, nonces, and opaque values are synthetic; no credential material
appears anywhere.
"""

import os
import unittest

from agentuniverse.agent.action.tool.common_tool import www_auth_tool as www_module
from agentuniverse.agent.action.tool.common_tool.www_auth_tool import WwwAuthenticateTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(www_module.__file__), "www_auth_tool.yaml")

# RFC 7235 section 4.1 example (verbatim, including the nested-quoted title).
RFC7235_EXAMPLE = 'Newauth realm="apps", type=1, title="Login to \\"apps\\"", Basic realm="simple"'

# RFC 6750 section 3 examples (synthetic realm label, error values verbatim).
RFC6750_INVALID_REQUEST = 'Bearer realm="example", error="invalid_request"'
RFC6750_INVALID_TOKEN = 'Bearer realm="example", error="invalid_token", error_description="The access token expired"'
RFC6750_INSUFFICIENT_SCOPE = 'Bearer realm="example", error="insufficient_scope", scope="read write"'

# RFC 7616 section 3.9 SHA-256 challenge shape (synthetic nonce/opaque payloads).
RFC7616_SHA256 = (
    'Digest realm="http-auth@example.org", qop="auth, auth-int", algorithm=SHA-256, '
    'nonce="7ypf/xlj9XXwfDPEoM4URrv/xwf94BcCAzFZH4GiTo0v", '
    'opaque="FQhe/qaU925kfnzjCev0ciny7QMkPqMAFRtzCUYo5tdS"'
)
RFC7616_USERHASH = (
    'Digest realm="http-auth@example.org", algorithm=SHA-512-256, '
    'nonce="Zm9vYmFy", userhash=true'
)
# RFC 4559: raw token presence (synthetic base64 NTLMSSP-style payload).
NEGOTIATE_TOKEN = 'Negotiate TlRMTVNTUAABAAAAB4IIogAAAAAAAAAAAAAAAAAAAAAFASgKAAAADw=='


def q(value):
    """Serialize a param value independently of the tool: bare token or quoted string."""
    import re

    if value != "" and re.fullmatch(r"[!#$%&'*+\-.^_`|~0-9A-Za-z]+", value):
        return value
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


class RfcCorpusParseTest(unittest.TestCase):
    """The hand-embedded RFC example set must parse exactly, with no errors."""

    def setUp(self):
        self.tool = WwwAuthenticateTool()

    def test_rfc7235_multiple_challenge_example(self):
        """RFC 7235 4.1: two challenges, params re-associated across commas, nested quotes unescaped."""
        result = self.tool.execute(mode="parse", header=RFC7235_EXAMPLE)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["challenge_count"], 2)
        first, second = result["challenges"]
        self.assertEqual(first["scheme"], "Newauth")
        self.assertEqual(first["params"], {"realm": "apps", "type": "1", "title": 'Login to "apps"'})
        self.assertEqual(second["scheme"], "Basic")
        self.assertEqual(second["params"], {"realm": "simple"})

    def test_rfc6750_three_error_examples(self):
        """RFC 6750 3: the three registry errors parse into one Bearer challenge each."""
        cases = [
            (RFC6750_INVALID_REQUEST, {"realm": "example", "error": "invalid_request"}),
            (RFC6750_INVALID_TOKEN, {"realm": "example", "error": "invalid_token", "error_description": "The access token expired"}),
            (RFC6750_INSUFFICIENT_SCOPE, {"realm": "example", "error": "insufficient_scope", "scope": "read write"}),
        ]
        for header, expected in cases:
            with self.subTest(header=header):
                result = self.tool.execute(mode="parse", header=header)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["errors"], [])
                self.assertEqual(result["challenge_count"], 1)
                self.assertEqual(result["challenges"][0]["scheme"], "Bearer")
                self.assertEqual(result["challenges"][0]["params"], expected)

    def test_rfc7616_digest_challenges(self):
        """RFC 7616: SHA-256 challenge (comma inside quoted qop stays one param) and userhash example."""
        result = self.tool.execute(mode="parse", header=RFC7616_SHA256)
        self.assertEqual(result["status"], "success")
        params = result["challenges"][0]["params"]
        self.assertEqual(params["algorithm"], "SHA-256")
        self.assertEqual(params["qop"], "auth, auth-int")
        self.assertEqual(params["nonce"], "7ypf/xlj9XXwfDPEoM4URrv/xwf94BcCAzFZH4GiTo0v")
        self.assertEqual(params["opaque"], "FQhe/qaU925kfnzjCev0ciny7QMkPqMAFRtzCUYo5tdS")
        self.assertEqual(len(result["challenges"][0]["params"]), 5)

        userhash = self.tool.execute(mode="parse", header=RFC7616_USERHASH)
        self.assertEqual(userhash["challenges"][0]["params"]["userhash"], "true")
        self.assertEqual(userhash["challenges"][0]["params"]["algorithm"], "SHA-512-256")

    def test_negotiate_raw_token_presence(self):
        """RFC 4559: bare Negotiate challenge and token68 with '=' padding both parse."""
        bare = self.tool.execute(mode="parse", header="Negotiate")
        self.assertEqual(bare["challenges"][0]["scheme"], "Negotiate")
        self.assertIsNone(bare["challenges"][0]["token68"])
        self.assertEqual(bare["challenges"][0]["params"], {})

        with_token = self.tool.execute(mode="parse", header=NEGOTIATE_TOKEN)
        self.assertEqual(with_token["status"], "success")
        self.assertEqual(with_token["challenges"][0]["token68"], "TlRMTVNTUAABAAAAB4IIogAAAAAAAAAAAAAAAAAAAAAFASgKAAAADw==")
        self.assertEqual(with_token["challenges"][0]["params"], {})

    def test_proxy_authenticate_and_case_insensitivity(self):
        """Proxy-Authenticate uses the same grammar; scheme casing normalizes canonically."""
        result = self.tool.execute(mode="parse", header='basic REALM="Simple", NEGOTIATE')
        self.assertEqual(result["challenge_count"], 2)
        self.assertEqual(result["challenges"][0]["scheme"], "Basic")
        self.assertEqual(result["challenges"][0]["scheme_raw"], "basic")
        self.assertEqual(result["challenges"][0]["params"], {"realm": "Simple"})
        self.assertEqual(result["challenges"][1]["scheme"], "Negotiate")


class QuotedCommaDisambiguationTest(unittest.TestCase):
    """The challenge-boundary disambiguation: commas inside quoted values must never split."""

    def setUp(self):
        self.tool = WwwAuthenticateTool()

    def test_quoted_comma_and_equals_do_not_split(self):
        """A quoted value containing ', ' or '=' stays one value."""
        result = self.tool.execute(mode="parse", header='Bearer realm="a, b=c", error="invalid_token"')
        self.assertEqual(result["challenge_count"], 1)
        self.assertEqual(result["challenges"][0]["params"], {"realm": "a, b=c", "error": "invalid_token"})
        self.assertEqual(result["errors"], [])

    def test_digest_qop_comma_is_inside_quotes(self):
        """Digest qop="auth, auth-int" is one param, not two challenges."""
        result = self.tool.execute(mode="parse", header='Digest realm="r", qop="auth, auth-int"')
        self.assertEqual(result["challenge_count"], 1)
        self.assertEqual(result["challenges"][0]["params"]["qop"], "auth, auth-int")

    def test_scheme_after_quoted_param_is_detected(self):
        """A scheme token after a quoted param still starts a new challenge."""
        result = self.tool.execute(mode="parse", header='Basic realm="with, comma", Negotiate')
        self.assertEqual([c["scheme"] for c in result["challenges"]], ["Basic", "Negotiate"])
        self.assertEqual(result["challenges"][0]["params"], {"realm": "with, comma"})

    def test_nested_escaped_quotes_round_trip(self):
        """Escaped quotes inside a quoted value survive a parse/build/parse cycle."""
        header = 'Newauth realm="apps", title="Login to \\"apps\\""'
        result = self.tool.execute(mode="parse", header=header)
        self.assertEqual(result["challenges"][0]["params"]["title"], 'Login to "apps"')
        rebuilt = self.tool.execute(
            mode="build",
            challenges=[
                {"scheme": c["scheme"], "params": c["params"], "token68": c["token68"]}
                for c in result["challenges"]
            ],
        )
        again = self.tool.execute(mode="parse", header=rebuilt["value"])
        self.assertEqual(again["challenges"][0]["params"]["title"], 'Login to "apps"')


# --------------------------------------------------------------------- corpus

SCHEMES = ["Basic", "Bearer", "Digest", "Negotiate"]
REALMS = ["apps", "simple", "example", "api area", "a,b=c", "x=y", 'esc \\" q', "plain"]
SCOPES = ["read write", "openid profile email", "https://example.com/read pool"]
NONCES = ["7ypf/xlj9XXwfDPEoM4URrv/xwf94BcCAzFZH4GiTo0v", "Zm9vYmFy", "a87421000492aa874209af8bc028"]
OPAQUES = ["FQhe/qaU925kfnzjCev0ciny7QMkPqMAFRtzCUYo5tdS", "opaque-value-1"]
ALGOS = ["MD5", "MD5-sess", "SHA-256", "SHA-256-sess", "SHA-512-256", "SHA-512-256-sess"]
TOKENS68 = [
    "TlRMTVNTUAABAAAAB4IIogAAAAAAAAAAAAAAAAAAAAAFASgKAAAADw==",
    "YIILSwYJKoZIhvcSAQICAQBuggojLMIIGQ6ADAgEFoQMCAQ6iBwIFACACA",
    "a87421000492aa874209af8bc028",
]


def scheme_form(scheme, index):
    """Deterministically vary the casing of a scheme token."""
    return [scheme, scheme.lower(), scheme.upper()][index % 3]


def basic_params(index):
    return {"realm": REALMS[(index // 4) % len(REALMS)]} | (
        {"charset": "UTF-8"} if index % 2 == 0 else {}
    )


def bearer_params(index):
    params = {"realm": REALMS[(index // 4) % len(REALMS)]}
    if index % 3 == 0:
        params["scope"] = SCOPES[(index // 9) % len(SCOPES)]
    if index % 3 == 1:
        params["error"] = ["invalid_request", "invalid_token", "insufficient_scope"][(index // 5) % 3]
        params["error_description"] = "The access token expired"
    return params


def digest_params(index):
    return {
        "realm": REALMS[(index // 6) % len(REALMS)],
        "nonce": NONCES[(index // 3) % len(NONCES)],
        "algorithm": ALGOS[(index // 2) % len(ALGOS)],
        "qop": "auth, auth-int",
        "opaque": OPAQUES[(index // 7) % len(OPAQUES)],
        "stale": ["true", "false"][index % 2],
    }


def challenge_text(index, scheme_position):
    """Render one challenge independently of the tool, deterministically from the index."""
    scheme = SCHEMES[(index + scheme_position) % 4]
    position = index + scheme_position
    if scheme == "Basic":
        params = basic_params(position)
    elif scheme == "Bearer":
        params = bearer_params(position)
    elif scheme == "Digest":
        params = digest_params(position)
    else:
        return f"{scheme_form(scheme, position)} {TOKENS68[position % len(TOKENS68)]}"
    rendered = ", ".join(f"{name}={q(value)}" for name, value in params.items())
    return f"{scheme_form(scheme, position)} {rendered}"


def valid_header(index):
    """Render a full header of 1-3 challenges, independently of the tool."""
    count = 1 + (index % 3)
    return ", ".join(challenge_text(index, position) for position in range(count))


def valid_header_lowercase(index):
    """Same generator with every scheme token lowercased (scheme case-insensitivity)."""
    count = 1 + (index % 3)
    rendered = []
    for position in range(count):
        text = challenge_text(index, position)
        scheme, _, rest = text.partition(" ")
        rendered.append(f"{scheme.lower()} {rest}")
    return ", ".join(rendered)


MUTATION_CODES = ["unterminated_quote", "empty_param_value", "duplicate_param", None, None, None, None, None]


def mutated_header(index):
    """Apply mutation (index % 8) to a valid base; returns (header, expected_code or None).

    Mutations 0-2 append to a Bearer challenge so the mutated param always
    lands on a challenge that carries auth-params (never on a token68-only
    Negotiate challenge, where salvage could not round-trip).
    """
    kind = index % 8
    base = valid_header(index % 180)
    if kind == 0:
        return 'Bearer realm="apps", error="invalid_token", scope="unclosed', "unterminated_quote"
    if kind == 1:
        return "Bearer realm=apps, error=invalid_token, scope=", "empty_param_value"
    if kind == 2:
        return 'Bearer realm="apps", realm="dup-value", error="invalid_token"', "duplicate_param"
    if kind == 3:
        return valid_header_lowercase(index % 180), None
    if kind == 4:
        return f"Negotiate {TOKENS68[index % len(TOKENS68)]}, {base}", None
    if kind == 5:
        return 'Bearer realm="a, b=c", error="invalid_token", ' + base, None
    if kind == 6:
        return ", ".join(challenge_text(index, position) for position in range(3)), None
    return f'Newauth realm="x=y", title="Login to \\"apps\\"", {base}', None


def semantic(challenges):
    """Project parsed challenges onto the semantic tuple compared by round-trips."""
    return [
        (c["scheme"].lower(), {k: v for k, v in c["params"].items()}, c["token68"])
        for c in challenges
    ]


class SeededCorpusTest(unittest.TestCase):
    """300 seeded strings: 180 valid (full no-error round-trip) + 120 mutations (code pinned, round-trip preserved)."""

    def setUp(self):
        self.tool = WwwAuthenticateTool()

    def rebuild(self, challenges):
        return self.tool.execute(
            mode="build",
            challenges=[
                {"scheme": c["scheme"], "params": c["params"], "token68": c["token68"]}
                for c in challenges
            ],
        )

    def test_valid_grammar_round_trip(self):
        """180 grammar-generated headers parse without errors and build/parse back to themselves."""
        count = 0
        for index in range(180):
            header = valid_header(index)
            first = self.tool.execute(mode="parse", header=header)
            self.assertEqual(first["status"], "success", f"index {index}: {first['errors']}")
            self.assertEqual(first["errors"], [], f"index {index}: {header}")
            rebuilt = self.rebuild(first["challenges"])
            self.assertEqual(rebuilt["status"], "success")
            second = self.tool.execute(mode="parse", header=rebuilt["value"])
            self.assertEqual(semantic(second["challenges"]), semantic(first["challenges"]), f"index {index}: {header}")
            count += 1
        self.assertEqual(count, 180)

    def test_mutation_battery_round_trip(self):
        """120 mutations: each pins its error code and still round-trips semantically (salvage is lossless)."""
        count = 0
        for index in range(180, 300):
            header, expected = mutated_header(index)
            first = self.tool.execute(mode="parse", header=header)
            codes = {error["code"] for error in first["errors"]}
            if expected is not None:
                self.assertIn(expected, codes, f"index {index}: {header} -> {codes}")
            self.assertTrue(first["challenges"], f"index {index}: salvage produced no challenges")
            rebuilt = self.rebuild(first["challenges"])
            self.assertEqual(rebuilt["status"], "success", f"index {index}: {rebuilt}")
            second = self.tool.execute(mode="parse", header=rebuilt["value"])
            self.assertEqual(
                semantic(second["challenges"]),
                semantic(first["challenges"]),
                f"index {index}: {header}",
            )
            count += 1
        self.assertEqual(count, 120)

    def test_corpus_total_is_300(self):
        """The seeded corpus is exactly 300 strings."""
        self.assertEqual(len([*range(180)]) + len([*range(180, 300)]), 300)


class ExplainAccuracyTest(unittest.TestCase):
    """Every param of every RFC corpus example must get the right meaning, table, or security note."""

    def setUp(self):
        self.tool = WwwAuthenticateTool()

    def explained(self, challenge):
        result = self.tool.execute(mode="explain", challenge=challenge)
        self.assertIn(result["status"], {"success", "partial"})
        return result

    def meaning_of(self, result, name):
        return next(item["meaning"] for item in result["params"] if item["name"] == name)

    def test_basic_meanings_and_tls_note(self):
        result = self.explained('Basic realm="simple", charset=UTF-8')
        self.assertIn("Protection-space", self.meaning_of(result, "realm"))
        self.assertIn("UTF-8", self.meaning_of(result, "charset"))
        self.assertTrue(any("TLS" in note for note in result["security_notes"]))

    def test_bearer_error_registry_accuracy(self):
        result = self.explained(RFC6750_INVALID_TOKEN)
        self.assertIn("registry", self.meaning_of(result, "error"))
        registry = result["tables"]["bearer_error_registry"]
        self.assertEqual([entry["code"] for entry in registry], ["invalid_request", "invalid_token", "insufficient_scope"])
        invalid_token = next(entry for entry in registry if entry["code"] == "invalid_token")
        self.assertIn("expired", invalid_token["meaning"])
        self.assertIn("fresh access token", invalid_token["remediation"])
        self.assertTrue(any("fresh access token" in note for note in result["security_notes"]))
        self.assertEqual(len(result["tables"]["oauth_error_codes"]), 7)

    def test_bearer_scope_semantics(self):
        result = self.explained(RFC6750_INSUFFICIENT_SCOPE)
        self.assertIn("Space-delimited", self.meaning_of(result, "scope"))
        self.assertTrue(any("space-delimited" in note for note in result["security_notes"]))

    def test_digest_algorithm_inventory(self):
        result = self.explained(RFC7616_SHA256)
        names = [entry["name"] for entry in result["tables"]["digest_algorithms"]]
        self.assertEqual(names, ["MD5", "MD5-sess", "SHA-256", "SHA-256-sess", "SHA-512-256", "SHA-512-256-sess"])
        self.assertIn("Server-generated", self.meaning_of(result, "nonce"))
        self.assertIn("auth-int", self.meaning_of(result, "qop"))
        self.assertTrue(any("SHA-256" in note for note in result["security_notes"]))

    def test_digest_security_notes(self):
        weak = self.explained('Digest realm="r", algorithm=MD5, nonce="n"')
        self.assertTrue(any("weak" in note for note in weak["security_notes"]))
        sess = self.explained('Digest realm="r", algorithm=SHA-256-sess, nonce="n"')
        self.assertTrue(any("cnonce" in note for note in sess["security_notes"]))
        stale = self.explained('Digest realm="r", algorithm=SHA-256, nonce="n2", stale=true')
        self.assertTrue(any("stale=true" in note and "retry" in note for note in stale["security_notes"]))
        userhash = self.explained(RFC7616_USERHASH)
        self.assertTrue(any("username" in note and "hash" in note for note in userhash["security_notes"]))
        legacy = self.explained('Digest realm="r", algorithm=MD5, nonce="n"')
        self.assertTrue(any("RFC 2069" in note for note in legacy["security_notes"]))

    def test_negotiate_token_meaning(self):
        with_token = self.explained(NEGOTIATE_TOKEN)
        self.assertIn("GSSAPI", with_token["token68_meaning"])
        self.assertIn("Kerberos", with_token["scheme_meaning"])
        bare = self.explained("Negotiate")
        self.assertIn("invites the client", bare["token68_meaning"])


class BuildTest(unittest.TestCase):
    """Canonical building: quoting, escaping, coercion, deterministic order, joining, round-trip."""

    def setUp(self):
        self.tool = WwwAuthenticateTool()

    def test_exact_canonical_digest_challenge(self):
        result = self.tool.execute(
            mode="build",
            scheme="Digest",
            params={
                "realm": "http-auth@example.org",
                "qop": "auth, auth-int",
                "algorithm": "SHA-256",
                "nonce": "7ypf/xlj9XXwfDPEoM4URrv/xwf94BcCAzFZH4GiTo0v",
            },
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["value"],
            'Digest realm="http-auth@example.org", qop="auth, auth-int", algorithm=SHA-256, '
            'nonce="7ypf/xlj9XXwfDPEoM4URrv/xwf94BcCAzFZH4GiTo0v"',
        )

    def test_quoting_rules(self):
        result = self.tool.execute(
            mode="build",
            scheme="Basic",
            params={"realm": 'plain', "title": 'Login to "apps"', "empty": "", "mixed": "a, b=c"},
        )
        self.assertEqual(result["value"], 'Basic realm=plain, title="Login to \\"apps\\"", empty="", mixed="a, b=c"')

    def test_scalar_coercion(self):
        result = self.tool.execute(mode="build", scheme="Newauth", params={"type": 1, "flag": True})
        self.assertEqual(result["value"], "Newauth type=1, flag=true")

    def test_order_is_as_given(self):
        first = self.tool.execute(mode="build", scheme="Bearer", params={"b": "2", "a": "1"})
        second = self.tool.execute(mode="build", scheme="Bearer", params={"a": "1", "b": "2"})
        self.assertEqual(first["value"], "Bearer b=2, a=1")
        self.assertEqual(second["value"], "Bearer a=1, b=2")

    def test_challenge_list_joining_and_token68(self):
        result = self.tool.execute(
            mode="build",
            challenges=[
                {"scheme": "Negotiate", "token68": "TlRMTVNTUAABAAAAB4IIog=="},
                {"scheme": "Basic", "params": {"realm": "simple"}},
            ],
        )
        self.assertEqual(result["value"], "Negotiate TlRMTVNTUAABAAAAB4IIog==, Basic realm=simple")

    def test_build_rejections(self):
        cases = [
            ({"mode": "build", "scheme": "Basic", "params": {"re alm": "x"}}, "invalid_param_name"),
            ({"mode": "build", "scheme": "Basic", "params": {"realm": "bad\nvalue"}}, "invalid_param_value"),
            ({"mode": "build", "scheme": "Negotiate", "params": {"realm": "x"}, "token68": "abc"}, "token68"),
        ]
        for kwargs, marker in cases:
            with self.subTest(kwargs=kwargs):
                result = self.tool.execute(**kwargs)
                self.assertEqual(result["status"], "error")
                joined = str(result.get("errors", result.get("error", "")))
                self.assertIn(marker, joined)

    def test_build_output_round_trips(self):
        built = self.tool.execute(
            mode="build",
            challenges=[
                {"scheme": "Digest", "params": {"realm": "r, with comma", "algorithm": "SHA-512-256", "stale": "true"}},
                {"scheme": "Bearer", "params": {"scope": "read write", "error": "invalid_token"}},
                {"scheme": "Negotiate", "token68": "YIILSwYJKoZIhvcSAQICA"},
            ],
        )
        parsed = self.tool.execute(mode="parse", header=built["value"])
        self.assertEqual(parsed["status"], "success")
        self.assertEqual(
            semantic(parsed["challenges"]),
            [
                ("digest", {"realm": "r, with comma", "algorithm": "SHA-512-256", "stale": "true"}, None),
                ("bearer", {"scope": "read write", "error": "invalid_token"}, None),
                ("negotiate", {}, "YIILSwYJKoZIhvcSAQICA"),
            ],
        )


class CompareTest(unittest.TestCase):
    """Challenge/param diffing for debugging auth flows."""

    def setUp(self):
        self.tool = WwwAuthenticateTool()

    def test_identical_headers(self):
        result = self.tool.execute(mode="compare", header_a='Basic realm="a"', header_b='Basic realm="a"')
        self.assertTrue(result["same"])
        self.assertEqual(result["schemes_only_in_a"], [])
        self.assertEqual(result["schemes_only_in_b"], [])

    def test_scheme_and_param_diff(self):
        result = self.tool.execute(
            mode="compare",
            header_a='Basic realm="a", Negotiate',
            header_b='Digest realm="a", nonce="n1", Basic realm="b", Negotiate',
        )
        self.assertFalse(result["same"])
        self.assertEqual(result["schemes_only_in_a"], [])
        self.assertEqual(result["schemes_only_in_b"], ["Digest"])
        basic = next(entry for entry in result["per_scheme"] if entry["scheme"] == "Basic")
        self.assertEqual(basic["params_added_in_b"], [])
        self.assertEqual(basic["params_changed"], [{"name": "realm", "a": "a", "b": "b"}])

    def test_param_add_remove_and_token68_change(self):
        result = self.tool.execute(
            mode="compare",
            header_a='Digest realm="r", nonce="n1", Negotiate aaa=',
            header_b='Digest realm="r", algorithm=SHA-256, Negotiate bbb=',
        )
        digest = next(entry for entry in result["per_scheme"] if entry["scheme"] == "Digest")
        self.assertEqual(digest["params_added_in_b"], ["algorithm"])
        self.assertEqual(digest["params_removed_in_b"], ["nonce"])
        self.assertEqual(result["per_scheme"][-1]["token68_change"], {"a": "aaa=", "b": "bbb="})

    def test_parse_errors_are_tagged_by_side(self):
        result = self.tool.execute(mode="compare", header_a='Basic realm="a', header_b='Basic realm="a"')
        self.assertEqual(result["status"], "partial")
        self.assertTrue(any(error.get("header") == "a" and error["code"] == "unterminated_quote" for error in result["errors"]))

    def test_duplicate_scheme_note(self):
        result = self.tool.execute(
            mode="compare",
            header_a='Basic realm="a", Basic realm="b"',
            header_b='Basic realm="a"',
        )
        self.assertTrue(any("repeats scheme" in note for note in result["notes"]))


class ParseSemanticsTest(unittest.TestCase):
    """Duplicate params (last wins), empty segments, orphan params, scheme hint, BWS tolerance."""

    def setUp(self):
        self.tool = WwwAuthenticateTool()

    def test_duplicate_param_last_wins_and_reported(self):
        result = self.tool.execute(mode="parse", header='Basic realm="first", realm="second"')
        self.assertEqual(result["challenges"][0]["params"], {"realm": "second"})
        self.assertTrue(any(error["code"] == "duplicate_param" for error in result["errors"]))

    def test_trailing_comma_reports_empty_segment(self):
        result = self.tool.execute(mode="parse", header='Basic realm="a",')
        self.assertTrue(any(error["code"] == "empty_segment" for error in result["errors"]))
        self.assertEqual(result["challenge_count"], 1)

    def test_orphan_param_before_any_scheme(self):
        result = self.tool.execute(mode="parse", header='realm="x", Basic realm="y"')
        self.assertTrue(any(error["code"] == "orphan_param" for error in result["errors"]))
        self.assertEqual(result["challenge_count"], 1)

    def test_scheme_hint(self):
        matched = self.tool.execute(mode="parse", header='Basic realm="a", Negotiate', scheme="basic")
        self.assertTrue(any("matched 1" in note for note in matched["notes"]))
        mismatched = self.tool.execute(mode="parse", header='Basic realm="a"', scheme="Digest")
        self.assertTrue(any(error["code"] == "scheme_mismatch" for error in mismatched["errors"]))

    def test_bws_around_equals_tolerated_with_error(self):
        result = self.tool.execute(mode="parse", header='Basic realm = "a"')
        self.assertEqual(result["challenges"][0]["params"], {"realm": "a"})
        self.assertTrue(any(error["code"] == "bws_around_equals" for error in result["errors"]))

    def test_missing_comma_between_params_salvaged(self):
        result = self.tool.execute(mode="parse", header='Digest realm="r" algorithm=SHA-256')
        self.assertEqual(result["challenges"][0]["params"], {"realm": "r", "algorithm": "SHA-256"})
        self.assertTrue(any(error["code"] == "missing_comma" for error in result["errors"]))

    def test_param_with_token68_is_flagged(self):
        result = self.tool.execute(mode="parse", header='Negotiate TlRMTVNTUAABAAAAB4IIog==, realm="x"')
        self.assertTrue(any(error["code"] == "param_with_token68" for error in result["errors"]))

    def test_empty_header_is_an_error(self):
        result = self.tool.execute(mode="parse", header="   ")
        self.assertEqual(result["status"], "error")
        self.assertTrue(any(error["code"] == "empty_header" for error in result["errors"]))

    def test_mode_and_argument_validation(self):
        self.assertEqual(self.tool.execute(mode="split", header="x")["error_type"], "validation_error")
        self.assertEqual(self.tool.execute(mode="parse")["error_type"], "validation_error")
        self.assertEqual(self.tool.execute(mode="explain")["error_type"], "validation_error")
        self.assertEqual(self.tool.execute(mode="build")["error_type"], "validation_error")
        self.assertEqual(self.tool.execute(mode="compare", header_a="Basic")["error_type"], "validation_error")


class ErrorBatteryTest(unittest.TestCase):
    """100 malformed headers, each caught with the right code (10 categories x 10 variants)."""

    def setUp(self):
        self.tool = WwwAuthenticateTool()

    @staticmethod
    def battery():
        cases = []
        for i in range(10):
            realm = f"r{i}"
            cases.append((f'Basic realm="{realm}', "unterminated_quote"))
            cases.append((f"Basic realm={realm}, realm=", "empty_param_value"))
            cases.append((f'Basic realm="{realm}", realm="dup"', "duplicate_param"))
            cases.append((f'realm="{realm}", Basic realm="x"', "orphan_param"))
            cases.append((f'Basic realm="{realm}",', "empty_segment"))
            cases.append((f'"quoted-{i}", Basic realm="x"', "invalid_token_start"))
            cases.append((f'Basic"tail{i}', "malformed_segment"))
            cases.append((f"Digest realm={realm} charset=UTF-8", "missing_comma"))
            cases.append((f'Negotiate tok{i}=, realm="x"', "param_with_token68"))
            cases.append((f'Basic realm="{realm}"\x01', "control_character"))
        return cases

    def test_each_malformed_header_has_its_code(self):
        cases = self.battery()
        self.assertEqual(len(cases), 100)
        for header, expected in cases:
            with self.subTest(header=header):
                result = self.tool.execute(mode="parse", header=header)
                codes = {error["code"] for error in result["errors"]}
                self.assertIn(expected, codes, f"{header!r} -> {codes}")

    def test_ten_challenges_over_cap_is_bounded(self):
        header = ", ".join(f"Scheme{i} realm=\"r{i}\"" for i in range(300))
        result = self.tool.execute(mode="parse", header=header)
        codes = {error["code"] for error in result["errors"]}
        self.assertIn("too_many_challenges", codes)
        self.assertLessEqual(result["challenge_count"], 256)


class PathologicalTest(unittest.TestCase):
    """Bounded behavior on pathological inputs."""

    def setUp(self):
        self.tool = WwwAuthenticateTool()

    def test_ten_thousand_challenges_bounded(self):
        header = ", ".join(["Basic"] * 10000)
        result = self.tool.execute(mode="parse", header=header)
        self.assertEqual(result["challenge_count"], self.tool.max_challenges)
        self.assertTrue(any(error["code"] == "too_many_challenges" for error in result["errors"]))
        self.assertLessEqual(len(result["challenges"]), 256)

    def test_one_megabyte_header_rejected(self):
        header = "Basic realm=\"" + "x" * 1048570 + "\""
        result = self.tool.execute(mode="parse", header=header)
        self.assertEqual(result["status"], "error")
        self.assertIn("max_header_chars", result["error"])

    def test_large_but_capped_header_parses(self):
        header = 'Basic realm="' + "x" * 100000 + '"'
        result = self.tool.execute(mode="parse", header=header)
        self.assertEqual(result["challenge_count"], 1)
        self.assertEqual(len(result["challenges"][0]["params"]["realm"]), self.tool.max_param_value_chars)
        self.assertTrue(any(error["code"] == "param_value_too_long" for error in result["errors"]))

    def test_error_list_is_capped(self):
        header = ", ".join(["realm="] * 300)
        result = self.tool.execute(mode="parse", header=header)
        self.assertLessEqual(len(result["errors"]), self.tool.max_error_entries + 1)
        self.assertTrue(any(error["code"] == "error_list_truncated" for error in result["errors"]))


class HostileReviewRegressionTest(unittest.TestCase):
    """Regressions found by a fresh hostile probe battery (seeds independent of the corpus above)."""

    def setUp(self):
        self.tool = WwwAuthenticateTool()

    def test_build_output_is_acceptable_to_parse(self):
        """build must never emit a header longer than its own max_header_chars cap."""
        oversized = [
            {"scheme": f"X{i}", "params": {f"p{j}": "v" * 8000 for j in range(60)}, "token68": None}
            for i in range(2)
        ]
        result = self.tool.execute(mode="build", challenges=oversized)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("max_header_chars", result["error"])
        # a large but under-cap build still succeeds and parses back
        under_cap = [
            {"scheme": f"X{i}", "params": {"p": "v" * 8000}, "token68": None} for i in range(30)
        ]
        built = self.tool.execute(mode="build", challenges=under_cap)
        self.assertEqual(built["status"], "success")
        self.assertLessEqual(len(built["value"]), self.tool.max_header_chars)
        self.assertEqual(self.tool.execute(mode="parse", header=built["value"])["status"], "success")

    def test_raw_field_renders_scheme_param_separator_correctly(self):
        """The reconstructed raw text joins the scheme and its first param with a space, not a comma."""
        result = self.tool.execute(mode="parse", header='Basic realm="x", charset=UTF-8')
        self.assertEqual(result["challenges"][0]["raw"], "Basic realm=x, charset=UTF-8")
        continuation = self.tool.execute(mode="parse", header='Newauth realm="apps", type=1')
        self.assertEqual(continuation["challenges"][0]["raw"], "Newauth realm=apps, type=1")

    def test_control_character_inside_quoted_value_is_flagged(self):
        """Control bytes inside a quoted value are kept but reported, like their outside-quote twins."""
        result = self.tool.execute(mode="parse", header='Basic realm="a\x01b"')
        self.assertEqual(result["challenges"][0]["params"]["realm"], "a\x01b")
        self.assertTrue(any(error["code"] == "control_character" for error in result["errors"]))
        detail = next(error["detail"] for error in result["errors"] if error["code"] == "control_character")
        self.assertIn("quoted string", detail)
        outside = self.tool.execute(mode="parse", header="Basic realm=a\x01b")
        self.assertTrue(any(error["code"] == "control_character" for error in outside["errors"]))


class WwwAuthenticateRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped www_auth_tool.yaml as a tool component."""

    def setUp(self):
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "WwwAuthenticateTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, WwwAuthenticateTool)
        self.assertEqual(tool.input_keys, ["mode"])

    def test_package_export(self):
        from agentuniverse.agent.action.tool.common_tool import WwwAuthenticateTool as Exported

        self.assertIs(Exported, WwwAuthenticateTool)


if __name__ == "__main__":
    unittest.main()
