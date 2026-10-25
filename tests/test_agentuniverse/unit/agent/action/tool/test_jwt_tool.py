# Seeded PRNGs keep the corpus deterministic; they never guard secrets.
# ruff: noqa: S311

import base64
import datetime
import json
import os
import random
import time
import unittest

from agentuniverse.agent.action.tool.common_tool import jwt_tool as jwt_module
from agentuniverse.agent.action.tool.common_tool.jwt_tool import JwtTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

try:
    import jwt as pyjwt
except ImportError:  # PyJWT is a local test-only oracle, not a runtime dependency.
    pyjwt = None

YAML_PATH = os.path.join(os.path.dirname(jwt_module.__file__), "jwt_tool.yaml")
NOW_BASE = 1_800_000_000
SEED = 252


def segment(value):
    """Encode a JSON value or raw text as an unpadded base64url segment."""
    raw = value.encode("utf-8") if isinstance(value, str) else json.dumps(value, separators=(",", ":")).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def build_token(header, payload, signature="c2lnbmF0dXJl"):
    """Assemble a compact token from a header object and a payload object or raw JSON text."""
    return ".".join([segment(header), segment(payload), signature])


def iso(timestamp):
    """Render a POSIX timestamp as a UTC ISO 8601 string."""
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc).isoformat()


# RFC 7519 Appendix A example tokens, assembled at runtime from fragments.
RFC_A1_TOKEN = ".".join(
    [
        "eyJ0eXAiOiJKV1QiLA0KICJhbGciOi" + "JIUzI1NiJ9",
        "eyJpc3MiOiJqb2UiLA0KICJleHAiOjEzMDA4MT" + "kzODAsDQogImh0dHA6Ly9leGFtcGxlLmNvbS9pc19yb290Ijp0cnVlfQ",
        "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOE" + "jXk",
    ]
)
RFC_A2_TOKEN = ".".join(
    [
        "eyJhbGciOi" + "JSUzI1NiJ9",
        "eyJpc3MiOiJqb2UiLA0KICJleHAiOjEzMDA4MT" + "kzODAsDQogImh0dHA6Ly9leGFtcGxlLmNvbS9pc19yb290Ijp0cnVlfQ",
        "cC4hiUPoj9Eetdgtv3hF80EGrhuB__dzERat0XF9g2VtQgr9PJbu3XOiZj5RZmh7AAuHIm4Bh-0Qc_lF5YKt_O8W2Fp5jujGbds9u"
        "JdbF9CUAr7t1dnZcAcQjbKBYNX4BAynRFdiuB--f_nZLgrnbyTyWzO75vRK5h6xBArLIARNPvkSjtQBMHlb1L07Qe7K0GarZRmB_"
        "eSN9383LcOLn6_dO--xi12jzDwusC-eOkHWEsqtFZESc6BfI7noOPqvhJ1phCnvWh6IeYI2w9QOYEUipUTI8np6LbgGY9Fs98rqVt"
        "5AXLIhWkWywlVmtVrBp0igcN_IoypGlUPQGe77Rw",
    ]
)
RFC_CLAIMS = {"iss": "joe", "exp": 1300819380, "http://example.com/is_root": True}


def random_claims(rng):  # noqa: C901
    """Build bounded random claims including registered, custom, unicode, and NumericDate variants."""
    names = ["joe", "amy", "u" + str(rng.randint(0, 99999)), "overseas-actor-with-a-noticeably-long-name"]
    claims = {}
    if rng.random() < 0.9:
        claims["sub"] = rng.choice(names) + ("-很长的一段用户名信息" if rng.random() < 0.3 else "")
    if rng.random() < 0.7:
        claims["iss"] = rng.choice(["https://issuer.example", "issuer-" + str(rng.randint(0, 9999))])
    for name in ("exp", "nbf", "iat"):
        roll = rng.random()
        if roll < 0.6:
            claims[name] = NOW_BASE + rng.randint(-10**6, 10**6)
        elif roll < 0.7:
            claims[name] = float(NOW_BASE + rng.randint(-10**6, 10**6)) + rng.random()
        elif roll < 0.78:
            claims[name] = str(NOW_BASE + rng.randint(-10**6, 10**6))
        elif roll < 0.84:
            claims[name] = rng.choice([True, None, -1])
    if rng.random() < 0.5:
        claims["aud"] = rng.choice(["api", ["api", "web"], "mobile-client"])
    if rng.random() < 0.4:
        claims["roles"] = rng.sample(["admin", "editor", "viewer", "guest"], rng.randint(1, 3))
    if rng.random() < 0.3:
        claims["profile"] = {"locale": rng.choice(["en", "zh", "de"]), "verified": rng.random() < 0.5}
    if rng.random() < 0.3:
        claims["tracking_id"] = "trk" + "".join(rng.choice("0123456789abcdef") for _ in range(40))
    return claims


def walk_strings(value):
    """Collect every string value inside a JSON tree."""
    found = []
    if isinstance(value, str):
        found.append(value)
    elif isinstance(value, list):
        for item in value:
            found.extend(walk_strings(item))
    elif isinstance(value, dict):
        for item in value.values():
            found.extend(walk_strings(item))
    return found


class JwtToolTest(unittest.TestCase):
    """Deterministic offline unit tests for JwtTool decode, claims, audit, and explain modes."""

    def setUp(self):
        self.tool = JwtTool()

    def test_decode_reports_structure(self):
        result = self.tool.execute(mode="decode", token=build_token({"alg": "HS256", "typ": "JWT"}, {"sub": "joe", "exp": 100}))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["token_form"], "JWS")
        self.assertEqual(result["header"]["alg"], "HS256")
        self.assertEqual(result["header"]["typ"], "JWT")
        self.assertEqual(result["payload"]["claims"], {"sub": "joe", "exp": 100})
        self.assertTrue(result["signature"]["present"])
        self.assertEqual(result["signature"]["format"], "base64url")
        self.assertEqual(result["structure_errors"], [])

    def test_decode_masks_long_strings_by_default(self):
        claims = {"sub": "joe", "secret_note": "x" * 60, "short": "y" * 24, "nested": {"deep": "z" * 40}}
        result = self.tool.execute(mode="decode", token=build_token({"alg": "HS256"}, claims))
        self.assertEqual(result["payload"]["claims"]["sub"], "joe")
        self.assertEqual(result["payload"]["claims"]["short"], "y" * 24)
        self.assertEqual(result["payload"]["claims"]["secret_note"], "<masked:60 chars>")
        self.assertEqual(result["payload"]["claims"]["nested"]["deep"], "<masked:40 chars>")
        unmasked = self.tool.execute(mode="decode", token=build_token({"alg": "HS256"}, claims), mask_strings=False)
        self.assertEqual(unmasked["payload"]["claims"]["secret_note"], "x" * 60)

    def test_decode_accepts_unsecured_two_segment_form_with_flag(self):
        token = ".".join([segment({"alg": "none"}), segment({"sub": "joe"})])
        result = self.tool.execute(mode="decode", token=token)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["token_form"], "unsecured")
        self.assertFalse(result["signature"]["present"])
        codes = {item["code"] for item in result["structure_errors"]}
        self.assertEqual(codes, {"alg_none_unsecured"})

    def test_decode_flags_structure_errors(self):
        header = segment({"alg": "HS256"})
        payload = segment({"sub": "joe"})
        cases = {
            "a.b.c.d": "segment_count",
            build_token({"alg": "HS256"}, {"sub": "joe"}) + ".extra": "segment_count",
            header[:5] + "!" + header[5:] + "." + payload + ".s": "base64url_chars",
            header + "=." + payload + ".s": "base64url_padding",
            ".".join([header, segment("not json at all"), "s"]): "invalid_json",
            ".".join(["", payload, "s"]): "empty_segment",
            ".".join([header, "", "s"]): "empty_segment",
        }
        for token, expected in cases.items():
            result = self.tool.execute(mode="decode", token=token)
            self.assertEqual(result["status"], "error", token)
            self.assertIn(expected, {item["code"] for item in result["structure_errors"]})

    def test_decode_flags_zero_width_tricks(self):
        payload = segment(json.dumps({"sub": "jo\u200be"}))  # zero-width space inside the claim value
        token = ".".join([segment({"alg": "HS256"}), payload, "s"])
        result = self.tool.execute(mode="decode", token=token)
        self.assertEqual(result["status"], "success")
        codes = {item["code"] for item in result["structure_errors"]}
        self.assertIn("zero_width_chars", codes)
        smuggled = segment({"alg": "HS256"})
        token2 = ".".join([smuggled[:6] + "\u200b" + smuggled[6:], segment({"sub": "joe"}), "s"])
        result2 = self.tool.execute(mode="decode", token=token2)
        self.assertEqual(result2["status"], "error")
        self.assertIn("zero_width_chars", {item["code"] for item in result2["structure_errors"]})

    def test_decode_rejects_non_object_payload_without_cty(self):
        token = ".".join([segment({"alg": "HS256"}), segment('"just a string"'), "s"])
        result = self.tool.execute(mode="decode", token=token)
        self.assertEqual(result["status"], "error")
        self.assertIn("payload_not_object", {item["code"] for item in result["structure_errors"]})

    def test_decode_truncates_claim_inventory(self):
        tool = JwtTool(max_claims=100)
        claims = {f"k{index:03d}": index for index in range(120)}
        result = tool.execute(mode="decode", token=build_token({"alg": "HS256"}, claims))
        self.assertEqual(result["payload"]["claim_count"], 120)
        self.assertEqual(result["payload"]["omitted_claims"], 20)
        self.assertEqual(len(result["payload"]["claims"]), 100)

    def test_decode_bounds_huge_payload(self):
        claims = {"blob": "x" * 400_000}
        tool = JwtTool(max_token_bytes=2_000_000)
        result = tool.execute(mode="decode", token=build_token({"alg": "HS256"}, claims))
        self.assertEqual(result["status"], "error")
        self.assertIn("segment_oversize", {item["code"] for item in result["structure_errors"]})
        self.assertIsNone(result["payload"]["claims"])

    def test_decode_strips_bearer_prefix(self):
        token = build_token({"alg": "HS256", "typ": "JWT"}, {"sub": "joe"})
        result = self.tool.execute(mode="decode", token="Bearer " + token)
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["bearer_prefix_stripped"])
        self.assertEqual(result["payload"]["claims"], {"sub": "joe"})

    def test_nested_jwt_decodes_one_bounded_level(self):
        inner = build_token({"alg": "HS256", "typ": "JWT"}, {"sub": "inner-user", "note": "n" * 40})
        outer = build_token({"alg": "HS256", "typ": "JWT", "cty": "JWT"}, json.dumps(inner))
        result = self.tool.execute(mode="decode", token=outer)
        self.assertEqual(result["status"], "success")
        nested = result["nested"]
        self.assertTrue(nested["decoded"])
        self.assertEqual(nested["header"]["alg"], "HS256")
        self.assertEqual(nested["payload"]["claims"]["sub"], "inner-user")
        self.assertEqual(nested["payload"]["claims"]["note"], "<masked:40 chars>")
        self.assertEqual(result["payload"]["claims"]["__nested_jwt__"], f"<masked:{len(inner)} chars>")
        middle = build_token({"alg": "HS256", "typ": "JWT", "cty": "JWT"}, json.dumps(inner))
        outer_two = build_token({"alg": "HS256", "typ": "JWT", "cty": "JWT"}, json.dumps(middle))
        deep = self.tool.execute(mode="decode", token=outer_two)
        self.assertTrue(deep["nested"]["decoded"])
        self.assertTrue(deep["nested"]["truncated_at_depth"])
        self.assertTrue(deep["nested"]["nested"]["truncated_at_depth"])

    def test_analyze_claims_time_math(self):
        claims = {"exp": 1000, "nbf": 2000, "iat": 3000}
        token = build_token({"alg": "HS256"}, claims)
        result = self.tool.execute(mode="analyze_claims", token=token, now=iso(1500))
        self.assertEqual(result["checks"]["exp"]["verdict"], "expired")
        self.assertEqual(result["checks"]["exp"]["delta_seconds"], 500)
        self.assertEqual(result["checks"]["nbf"]["verdict"], "not_yet_valid")
        self.assertEqual(result["checks"]["iat"]["verdict"], "issued_in_future")
        self.assertEqual(result["checks"]["exp"]["math"], "now - exp = +500s -> expired (skew 0s, now " + iso(1500) + ")")

    def test_analyze_claims_skew_tolerance(self):
        token = build_token({"alg": "HS256"}, {"exp": 1000, "nbf": 3000, "iat": 3000})
        result = self.tool.execute(mode="analyze_claims", token=token, now=iso(1200), skew_seconds=300)
        self.assertEqual(result["checks"]["exp"]["verdict"], "valid")
        self.assertEqual(result["checks"]["nbf"]["verdict"], "not_yet_valid")
        self.assertEqual(result["checks"]["iat"]["verdict"], "issued_in_future")

    def test_analyze_claims_missing_and_invalid_numeric_dates(self):
        token = build_token({"alg": "HS256"}, {"exp": "1000", "nbf": True, "custom": 1})
        result = self.tool.execute(mode="analyze_claims", token=token, now=iso(1500))
        self.assertEqual(result["checks"]["exp"]["verdict"], "invalid")
        self.assertEqual(result["checks"]["nbf"]["verdict"], "invalid")
        self.assertEqual(result["checks"]["iat"]["verdict"], "absent")
        self.assertEqual(result["invalid_numeric_dates"][0]["claim"], "exp")
        self.assertIn("RFC 7519 NumericDate", result["invalid_numeric_dates"][0]["reason"])
        self.assertEqual(set(result["missing_registered_claims"]), {"iat", "iss", "aud", "sub"})
        self.assertEqual(result["custom_claims"], {"custom": "number"})

    def test_analyze_claims_audience_and_issuer(self):
        claims = {"aud": ["api", "web"], "iss": "issuer.example"}
        token = build_token({"alg": "HS256"}, claims)
        result = self.tool.execute(mode="analyze_claims", token=token, now=iso(1500), expected_aud="web", expected_iss="issuer.example")
        self.assertEqual(result["audience"]["verdict"], "match")
        self.assertEqual(result["issuer"]["verdict"], "match")
        other = self.tool.execute(mode="analyze_claims", token=token, now=iso(1500), expected_aud="mobile", expected_iss="other")
        self.assertEqual(other["audience"]["verdict"], "mismatch")
        self.assertEqual(other["issuer"]["verdict"], "mismatch")

    def test_audit_alg_findings(self):
        none_token = ".".join([segment({"alg": "none"}), segment({"sub": "joe"})])
        self.assertEqual(
            self.tool.execute(mode="audit_alg", token=none_token)["findings"][0]["code"], "alg_none_unsecured"
        )
        attack = build_token(
            {"alg": "HS256", "typ": "JWT", "kid": "../../etc/passwd", "jku": "https://evil.example/keys", "crit": ["missing_param"]},
            {"sub": "joe"},
        )
        result = self.tool.execute(mode="audit_alg", token=attack)
        codes = {item["code"] for item in result["findings"]}
        self.assertEqual(codes, {"symmetric_alg", "kid_suspicious", "jku_untrusted_key_fetch", "crit_parameter_conflict"})
        severities = {item["code"]: item["severity"] for item in result["findings"]}
        self.assertEqual(severities["jku_untrusted_key_fetch"], "high")
        x5u = build_token({"alg": "RS256", "x5u": "https://evil.example/cert"}, {"sub": "joe"})
        x5u_result = self.tool.execute(mode="audit_alg", token=x5u)
        self.assertEqual(x5u_result["alg_family"], "RSASSA-PKCS1-v1_5 with SHA-256, asymmetric RSA")
        self.assertEqual(x5u_result["findings"][0]["code"], "x5u_untrusted_key_fetch")
        no_alg = build_token({"typ": "JWT"}, {"sub": "joe"})
        self.assertEqual(self.tool.execute(mode="audit_alg", token=no_alg)["findings"][0], {
            "code": "alg_missing", "severity": "critical", "detail": 'header has no "alg" parameter'
        })
        crit_bad = build_token({"alg": "HS256", "crit": "exp"}, {"sub": "joe"})
        self.assertIn("crit_invalid", {item["code"] for item in self.tool.execute(mode="audit_alg", token=crit_bad)["findings"]})

    def test_audit_alg_recognizes_families(self):
        for alg, family_start in (("ES256", "ECDSA"), ("PS512", "RSASSA-PSS"), ("EdDSA", "Ed25519")):
            result = self.tool.execute(mode="audit_alg", token=build_token({"alg": alg}, {"sub": "joe"}))
            self.assertTrue(result["alg_family"].startswith(family_start))
            self.assertEqual(result["findings"], [])
        unknown = self.tool.execute(mode="audit_alg", token=build_token({"alg": "HS1"}, {"sub": "joe"}))
        self.assertIn("unknown_alg", {item["code"] for item in unknown["findings"]})

    def test_audit_alg_flags_nested_cty(self):
        result = self.tool.execute(mode="audit_alg", token=build_token({"alg": "RS256", "cty": "JWT"}, {"sub": "joe"}))
        self.assertTrue(result["nested_jwt"])
        self.assertIn("nested_jwt", {item["code"] for item in result["findings"]})

    def test_explain_human_readable_output(self):
        token = ".".join([segment({"alg": "none"}), segment({"sub": "joe-with-a-very-long-subject-name-value", "exp": 1000})])
        result = self.tool.execute(mode="explain", token=token, now=iso(2000))
        self.assertEqual(result["status"], "success")
        text = "\n".join(result["lines"])
        self.assertIn("form: unsecured", text)
        self.assertIn("not signed", text)
        self.assertIn("now - exp = +1000s -> expired", text)
        self.assertIn("did NOT verify any signature", text)
        self.assertNotIn("joe-with-a-very-long-subject-name-value", text)
        topics = {item["topic"] for item in result["verdicts"]}
        self.assertIn("exp", topics)
        self.assertIn("alg_none_unsecured", topics)

    def test_explain_uses_system_clock_only_when_now_absent(self):
        result = self.tool.execute(mode="explain", token=build_token({"alg": "HS256"}, {"sub": "joe"}))
        self.assertIn("system clock", "\n".join(result["lines"]))
        self.assertTrue(result["now"])

    def test_rfc7519_appendix_examples(self):
        for token, alg, family in ((RFC_A1_TOKEN, "HS256", "HMAC-SHA-256"), (RFC_A2_TOKEN, "RS256", "RSASSA-PKCS1-v1_5")):
            decoded = self.tool.execute(mode="decode", token=token)
            self.assertEqual(decoded["status"], "success")
            self.assertEqual(decoded["header"]["alg"], alg)
            self.assertEqual(decoded["payload"]["claims"], RFC_CLAIMS)
            audited = self.tool.execute(mode="audit_alg", token=token)
            self.assertTrue(audited["alg_family"].startswith(family))
            analyzed = self.tool.execute(mode="analyze_claims", token=token, now=iso(1_400_000_000))
            self.assertEqual(analyzed["checks"]["exp"]["verdict"], "expired")
            self.assertEqual(analyzed["checks"]["exp"]["delta_seconds"], 99_180_620)

    def test_input_validation(self):
        checks = [
            {"mode": "summary", "token": "a.b.c"},
            {"mode": "decode", "token": 123},
            {"mode": "decode", "token": "   "},
            {"mode": "decode", "token": "a" * 65537},
            {"mode": "analyze_claims", "token": "a.b.c", "now": "not-a-date"},
            {"mode": "analyze_claims", "token": "a.b.c", "skew_seconds": -1},
            {"mode": "analyze_claims", "token": "a.b.c", "skew_seconds": True},
            {"mode": "analyze_claims", "token": "a.b.c", "expected_aud": ""},
            {"mode": "decode", "token": "a.b.c", "mask_strings": "yes"},
            {"mode": "decode", "token": "Bearer "},
        ]
        for kwargs in checks:
            result = self.tool.execute(**kwargs)
            self.assertEqual(result["status"], "error", kwargs)
            self.assertEqual(result["error_type"], "validation_error", kwargs)

    def test_config_validation(self):
        for bad in ({"max_token_bytes": 0}, {"mask_length": 3}, {"max_nested_depth": 3}, {"max_depth": -1}):
            tool = JwtTool(**bad)
            result = tool.execute(mode="decode", token=build_token({"alg": "HS256"}, {"sub": "joe"}))
            self.assertEqual(result["status"], "error", bad)
            self.assertEqual(result["error_type"], "validation_error", bad)

    def test_masking_threshold_is_configurable(self):
        tool = JwtTool(mask_length=8)
        result = tool.execute(mode="decode", token=build_token({"alg": "HS256"}, {"note": "shortvalue"}))
        self.assertEqual(result["payload"]["claims"]["note"], "<masked:10 chars>")


class JwtRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped jwt_tool.yaml as a tool component."""

    def setUp(self):
        """Load the shipped yaml config and snapshot the current app configer state."""
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        """Restore the app configer snapshot taken in setUp."""
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        """Verify the shipped yaml resolves to a tool component exposing the JwtTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "JwtTool")

    def test_manager(self):
        """Verify the JwtTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, JwtTool)
        self.assertEqual(tool.input_keys, ["mode", "token"])


@unittest.skipIf(pyjwt is None, "PyJWT oracle is not installed")
class JwtOracleParityTest(unittest.TestCase):
    """Decode parity between JwtTool and PyJWT (test-only oracle) over a seeded corpus."""

    def setUp(self):
        self.tool = JwtTool(max_token_bytes=2_000_000)
        self.corpus = self._build_corpus()
        self.assertEqual(len(self.corpus), 500)

    @staticmethod
    def _key(rng):
        return rng.randbytes(72)

    def _build_corpus(self):  # noqa: C901
        rng = random.Random(SEED)
        corpus = []
        for index in range(220):
            claims = random_claims(rng)
            alg = ("HS256", "HS384", "HS512")[index % 3]
            token = pyjwt.encode(claims, self._key(rng), algorithm=alg)
            corpus.append({"token": token, "category": "valid", "claims": claims, "header": {"alg": alg, "typ": "JWT"}})
        for _ in range(40):
            claims = {"sub": "joe", "exp": NOW_BASE + rng.randint(-1000, 1000)}
            token = ".".join([segment({"alg": "none", "typ": "JWT"}), segment(claims)])
            corpus.append({"token": token, "category": "alg_none_2part", "claims": claims})
        inner_claims = {"sub": "inner-user", "exp": NOW_BASE}
        for _ in range(20):
            inner = pyjwt.encode(inner_claims, self._key(rng), algorithm="HS256")
            outer = build_token({"alg": "HS256", "typ": "JWT", "cty": "JWT"}, json.dumps(inner))
            corpus.append({"token": outer, "category": "nested_one", "claims": inner_claims})
        for _ in range(10):
            inner = pyjwt.encode(inner_claims, self._key(rng), algorithm="HS256")
            middle = build_token({"alg": "HS256", "typ": "JWT", "cty": "JWT"}, json.dumps(inner))
            outer = build_token({"alg": "HS256", "typ": "JWT", "cty": "JWT"}, json.dumps(middle))
            corpus.append({"token": outer, "category": "nested_two", "claims": inner_claims})
        base = build_token({"alg": "HS256", "typ": "JWT"}, {"sub": "joe", "exp": 100})
        for _ in range(30):
            corpus.append({"token": base + ".extra", "category": "four_parts"})
        for _ in range(10):
            corpus.append({"token": base + ".extra.more", "category": "five_parts"})
        header = segment({"alg": "HS256"})
        for _ in range(20):
            corpus.append({"token": ".".join([header[:5] + "?" + header[5:], segment({"sub": "joe"}), "sig"]), "category": "bad_char"})
        for _ in range(30):
            corpus.append({"token": segment({"alg": "HS256"}) + "=." + segment({"sub": "joe"}) + ".sig", "category": "padding"})
        for _ in range(20):
            corpus.append(
                {"token": ".".join([segment({"alg": "HS256"}), segment("not json"), "sig"]), "category": "non_json"}
            )
        for _ in range(15):
            corpus.append({"token": ".".join(["", segment({"sub": "joe"}), "sig"]), "category": "empty_header"})
        for _ in range(15):
            corpus.append({"token": ".".join([segment({"alg": "HS256"}), "", "sig"]), "category": "empty_payload"})
        for _ in range(20):
            corpus.append({"token": base[: len(base) - 12], "category": "empty_signature", "claims": {"sub": "joe", "exp": 100}})
        for _ in range(10):
            corpus.append({"token": build_token({"alg": "HS256"}, {"blob": "x" * 400_000}), "category": "huge_oversize"})
        for _ in range(10):
            claims = {"blob": "x" * 100_000, "sub": "joe"}
            corpus.append({"token": build_token({"alg": "HS256"}, claims), "category": "huge_ok", "claims": claims})
        for _ in range(10):
            smuggled = segment({"alg": "HS256"})
            token = ".".join([smuggled[:6] + "\u200b" + smuggled[6:], segment({"sub": "joe"}), "sig"])
            corpus.append({"token": token, "category": "zw_b64"})
        for _ in range(10):
            claims = {"sub": "jo\u200be"}
            corpus.append({"token": build_token({"alg": "HS256"}, claims), "category": "zw_json", "claims": claims})
        for _ in range(10):
            corpus.append(
                {"token": ".".join([segment({"alg": "HS256"}), segment('"just a string"'), "sig"]), "category": "not_object"}
            )
        return corpus

    def test_decode_parity_with_pyjwt(self):
        """Every corpus token agrees with PyJWT decode or maps its error to a structure error."""
        must_succeed = {"valid", "empty_signature", "zw_json", "huge_ok"}
        must_error = {
            "four_parts": "segment_count",
            "five_parts": "segment_count",
            "bad_char": "base64url_chars",
            "padding": "base64url_padding",
            "non_json": "invalid_json",
            "empty_header": "empty_segment",
            "empty_payload": "empty_segment",
            "huge_oversize": "segment_oversize",
            "zw_b64": "zero_width_chars",
            "not_object": "payload_not_object",
        }
        seen = set()
        for entry in self.corpus:
            category = entry["category"]
            seen.add(category)
            result = self.tool.execute(mode="decode", token=entry["token"], mask_strings=False)
            with self.subTest(category=category):
                if category in must_succeed:
                    self.assertEqual(result["status"], "success")
                    if category == "zw_json":
                        self.assertEqual({item["code"] for item in result["structure_errors"]}, {"zero_width_chars"})
                    else:
                        self.assertEqual(result["structure_errors"], [])
                    decoded = pyjwt.decode(entry["token"], options={"verify_signature": False})
                    self.assertEqual(decoded, entry["claims"])
                    if category != "huge_ok":
                        self.assertEqual(result["payload"]["claims"], entry["claims"])
                    if category == "valid":
                        self.assertEqual(result["header"]["fields"], entry["header"])
                elif category == "alg_none_2part":
                    self.assertEqual(result["status"], "success")
                    self.assertEqual({item["code"] for item in result["structure_errors"]}, {"alg_none_unsecured"})
                    self.assertEqual(result["payload"]["claims"], entry["claims"])
                    with self.assertRaises(pyjwt.DecodeError):
                        pyjwt.decode(entry["token"], options={"verify_signature": False})
                elif category in ("nested_one", "nested_two"):
                    self.assertEqual(result["status"], "success")
                    self.assertTrue(result["nested"]["decoded"])
                    if category == "nested_one":
                        self.assertEqual(result["nested"]["payload"]["claims"], entry["claims"])
                    else:
                        self.assertIn("__nested_jwt__", result["nested"]["payload"]["claims"])
                        self.assertTrue(result["nested"]["truncated_at_depth"])
                        self.assertFalse(result["nested"]["nested"]["decoded"])
                        self.assertTrue(result["nested"]["nested"]["truncated_at_depth"])
                    with self.assertRaises(pyjwt.InvalidTokenError):
                        pyjwt.decode(entry["token"], options={"verify_signature": False})
                else:
                    self.assertEqual(result["status"], "error", entry["token"][:32])
                    codes = {item["code"] for item in result["structure_errors"]}
                    self.assertIn(must_error[category], codes)
                    if category != "huge_oversize":
                        with self.assertRaises(pyjwt.InvalidTokenError):
                            pyjwt.decode(entry["token"], options={"verify_signature": False})
        self.assertEqual(seen, must_succeed | set(must_error) | {"alg_none_2part", "nested_one", "nested_two"})

    def test_unsecured_tokens_flagged_and_pyjwt_rejects_them(self):
        """The two-segment form decodes locally, is flagged, and PyJWT documents it as an error."""
        for entry in self.corpus:
            if entry["category"] != "alg_none_2part":
                continue
            result = self.tool.execute(mode="decode", token=entry["token"])
            codes = {item["code"] for item in result["structure_errors"]}
            self.assertEqual(codes, {"alg_none_unsecured"})
            self.assertEqual(result["payload"]["claims"], entry["claims"])
            with self.assertRaises(pyjwt.DecodeError):
                pyjwt.decode(entry["token"], options={"verify_signature": False})

    def test_rfc7519_examples_match_pyjwt(self):
        """RFC 7519 Appendix A examples decode identically in JwtTool and PyJWT."""
        for token in (RFC_A1_TOKEN, RFC_A2_TOKEN):
            mine = self.tool.execute(mode="decode", token=token)
            self.assertEqual(mine["payload"]["claims"], pyjwt.decode(token, options={"verify_signature": False}))


@unittest.skipIf(pyjwt is None, "PyJWT oracle is not installed")
class JwtOracleClaimsMathTest(unittest.TestCase):
    """Claims time-math parity against independent datetime arithmetic and PyJWT verify_exp."""

    def setUp(self):
        self.tool = JwtTool()

    def test_three_hundred_seeded_cases_match_independent_math(self):  # noqa: C901
        """Verdicts and deltas match arithmetic done independently with datetime objects."""
        rng = random.Random(SEED + 1)
        for index in range(300):
            now = NOW_BASE + rng.randint(-10**6, 10**6)
            skew = rng.choice([0, 0, 0, 5, 30, 120])
            claims = {}
            expected = {}
            for name in ("exp", "nbf", "iat"):
                roll = rng.random()
                if roll < 0.15:
                    continue
                offset = rng.choice([-10**6, -86400, -3600, -60, 0, 60, 3600, 86400, 10**6])
                if roll < 0.75:
                    claims[name] = now + offset
                elif roll < 0.85:
                    claims[name] = float(now + offset) + 0.25
                else:
                    claims[name] = str(now + offset)
                expected[name] = claims[name]
            token = build_token({"alg": "HS256", "typ": "JWT"}, claims)
            result = self.tool.execute(mode="analyze_claims", token=token, now=iso(now), skew_seconds=skew)
            with self.subTest(index=index):
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["now"], iso(now))
                for name in ("exp", "nbf", "iat"):
                    check = result["checks"][name]
                    if name not in claims:
                        self.assertEqual(check["verdict"], "absent")
                        continue
                    value = expected[name]
                    if isinstance(value, str):
                        self.assertEqual(check["verdict"], "invalid")
                        continue
                    moment = datetime.datetime.fromtimestamp(value, tz=datetime.timezone.utc)
                    current = datetime.datetime.fromtimestamp(now, tz=datetime.timezone.utc)
                    tolerance = datetime.timedelta(seconds=skew)
                    if name == "exp":
                        independent = "expired" if current - tolerance > moment else "valid"
                    elif name == "nbf":
                        independent = "not_yet_valid" if moment > current + tolerance else "valid"
                    else:
                        independent = "issued_in_future" if moment > current + tolerance else "valid"
                    self.assertEqual(check["verdict"], independent)
                    self.assertEqual(check["delta_seconds"], round(now - value))

    def test_fifty_cases_match_pyjwt_verify_exp(self):
        """Expired verdicts agree with PyJWT ExpiredSignatureError on wall-clock-relative tokens."""
        rng = random.Random(SEED + 2)
        for index in range(50):
            key = rng.randbytes(72)
            now_real = time.time()
            exp = now_real + rng.choice([-2_592_000, -3600, -120, 120, 3600, 2_592_000])
            token = pyjwt.encode({"exp": int(exp)}, key, algorithm="HS256")
            result = self.tool.execute(mode="analyze_claims", token=token, now=iso(now_real))
            try:
                pyjwt.decode(token, key, algorithms=["HS256"])
                expired = False
            except pyjwt.ExpiredSignatureError:
                expired = True
            with self.subTest(index=index):
                self.assertEqual(result["checks"]["exp"]["verdict"], "expired" if expired else "valid")


@unittest.skipIf(pyjwt is None, "PyJWT oracle is not installed")
class JwtMaskingInvariantTest(unittest.TestCase):
    """Meta-test: masked decode output never echoes a claim string longer than the threshold."""

    def setUp(self):
        self.tool = JwtTool()
        rng = random.Random(SEED)
        self.corpus = [random_claims(rng) for _ in range(120)]

    def test_no_long_claim_value_leaks_through_masked_output(self):
        for index, claims in enumerate(self.corpus):
            token = build_token({"alg": "HS256", "typ": "JWT"}, claims)
            result = self.tool.execute(mode="decode", token=token)
            dumped = json.dumps(result, ensure_ascii=False)
            for value in walk_strings(claims):
                if len(value) > self.tool.mask_length:
                    self.assertNotIn(value, dumped, f"leak at corpus index {index}")
            explain = self.tool.execute(mode="explain", token=token, now=iso(NOW_BASE))
            explain_dump = json.dumps(explain, ensure_ascii=False)
            for value in walk_strings(claims):
                if len(value) > self.tool.mask_length:
                    self.assertNotIn(value, explain_dump, f"explain leak at corpus index {index}")

    def test_masked_output_still_shows_claim_names_and_short_values(self):
        claims = {"sub": "short-sub", "very_long_secret": "s" * 80}
        token = build_token({"alg": "HS256"}, claims)
        result = self.tool.execute(mode="decode", token=token)
        dumped = json.dumps(result, ensure_ascii=False)
        self.assertIn("very_long_secret", dumped)
        self.assertIn("short-sub", dumped)
        self.assertNotIn("s" * 80, dumped)


if __name__ == "__main__":
    unittest.main()
