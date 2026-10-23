import base64
import hashlib
import json
import os
import random
import unittest

from agentuniverse.agent.action.tool.common_tool import jwk_tool as jwk_module
from agentuniverse.agent.action.tool.common_tool.jwk_tool import JwkTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(jwk_module.__file__), "jwk_tool.yaml")


def b64u(data: bytes) -> str:
    """Encode bytes as unpadded base64url text."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def random_bytes(rng: random.Random, size: int) -> bytes:
    """Deterministic random bytes from a seeded generator."""
    return bytes(rng.getrandbits(8) for _ in range(size))


def reference_thumbprint(jwk: dict) -> str:
    """Independent RFC 7638 reference: canonical JSON built by direct string
    concatenation over the lexicographically ordered required members.

    Implemented separately from the tool on purpose; member values are
    base64url / registered ASCII names, so plain concatenation is exact.
    """
    members = {
        "RSA": ("e", "kty", "n"),
        "EC": ("crv", "kty", "x", "y"),
        "oct": ("k", "kty"),
        "OKP": ("crv", "kty", "x"),
    }[jwk["kty"]]
    canonical = "{" + ",".join('"%s":"%s"' % (m, jwk[m]) for m in sorted(members)) + "}"
    return b64u(hashlib.sha256(canonical.encode("ascii")).digest())


def rsa_public_jwk(rng: random.Random, bits: int) -> dict:
    """Synthetic RSA public JWK: odd modulus with the top bit set and e = 65537.

    The modulus is random filler, not a semiprime; the tool checks structure
    (oddness, sizes, ranges), never primality or other number theory.
    """
    modulus = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
    return {"kty": "RSA", "n": b64u(modulus.to_bytes((bits + 7) // 8, "big")), "e": "AQAB"}


def ec_public_jwk(rng: random.Random, crv: str, size: int) -> dict:
    """Synthetic EC JWK with coordinates of the right byte length for crv.

    Coordinates are random bytes and are generally NOT curve points; curve
    membership is out of scope for the structure tool and not checked.
    """
    return {"kty": "EC", "crv": crv, "x": b64u(random_bytes(rng, size)), "y": b64u(random_bytes(rng, size))}


def oct_jwk(rng: random.Random, size: int) -> dict:
    """Synthetic symmetric JWK (private material) of the given byte length."""
    return {"kty": "oct", "k": b64u(random_bytes(rng, size))}


def okp_public_jwk(rng: random.Random, crv: str, size: int) -> dict:
    """Synthetic OKP public JWK with the RFC 8037 key length for crv."""
    return {"kty": "OKP", "crv": crv, "x": b64u(random_bytes(rng, size))}


# --- RFC test vectors (public example values, embedded verbatim) -------------

# RFC 7517 Appendix A.1: elliptic curve public key example.
RFC_7517_A1_EC = {
    "kty": "EC",
    "crv": "P-256",
    "x": "MKBCTNIcKUSDii11ySs3526iDZ8AiTo7Tu6KPAqv7D4",
    "y": "4Etl6SRW2YiLUrN5vfvVHuhp7x8PxltmWWlbbM4IFyM",
    "use": "enc",
    "kid": "1",
}

# RFC 7517 Appendix A.2: octet sequence (symmetric) key example.
RFC_7517_A2_OCT = {
    "kty": "oct",
    "k": "AyM1SysPpbyDfgZld3umj1qzKObwVMkoqQ-EstJQLr_T-1qS0gZH75aKtMN3Yj0iPS4hcgUuTwjAzZr1Z9CAow",
}

# RFC 7517 Appendix A.3: RSA key example, public members only (n and e are
# published test vector values).
RFC_7517_A3_RSA_PUBLIC = {
    "kty": "RSA",
    "n": "0vx7agoebGcQSuuPiLJXZptN9nndrQmbXEps2aiAFbWhM78LhWx4cbbfAAtVT86zwu1RK7aPFFxuhDR1L6tSoc_BJECPebWKRXjBZCiFV4n3oknjhMstn64tZ_2W-5JsGY4Hc5n9yBXArwl93lqt7_RN5w6Cf0h4QyQ5v-65YGjQR0_FDW2QvzqY368QQMicAtaSqzs8KJZgnYb9c7d0zgdAZHzu6qMQvRL5hajrn1n91CbOpbISD08qNLyrdkt-bFTWhAI4vMQFh6WeZu0fM4lFd2NcRwr3XPksINHaQ-G_xBniIqbw0Ls1jF44-csFCur-kEgU8awapJzKnqDKgw",
    "e": "AQAB",
    "alg": "RS256",
    "kid": "2011-04-29",
}

# RFC 8037 section 2: Ed25519 public key example.
RFC_8037_ED25519_PUBLIC = {
    "kty": "OKP",
    "crv": "Ed25519",
    "x": "11qYAYKxCrfVS_7TyWQHOg7hcvPapiMlrwIaaPcHURo",
}

# RFC 7638 section 3.1: worked thumbprint example for the RSA key above.
RFC_7638_THUMBPRINT = "NzbLsXh8uDCcd-6MNwXF4W_7noWXFZAfHkxZsRGC9Xs"


class JwkToolOracleTest(unittest.TestCase):
    """Unit tests against published RFC examples and worked values."""

    def setUp(self):
        self.tool = JwkTool()

    def test_rfc7517_a1_ec_key(self):
        result = self.tool.execute(mode="analyze", jwk=RFC_7517_A1_EC)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["kty"], "EC")
        self.assertTrue(result["recognized"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["strength"]["coordinate_bytes_expected"], 32)
        self.assertEqual(result["strength"]["x_bytes"], 32)
        self.assertEqual(result["strength"]["y_bytes"], 32)
        self.assertEqual(result["strength"]["curve_bits"], 256)
        self.assertEqual(result["strength"]["point_on_curve"], "not_checked (requires field arithmetic; out of scope for this structure tool)")
        meanings = {p["name"]: p["meaning"] for p in result["parameters"]}
        self.assertEqual(meanings["crv"], "Curve (RFC 7517 6.2.1.1)")
        self.assertEqual(meanings["use"], "Public Key Use (RFC 7517 4.2)")
        self.assertEqual(meanings["kid"], "Key ID (RFC 7517 4.5)")
        self.assertEqual(reference_thumbprint(RFC_7517_A1_EC), result["thumbprint"])

    def test_rfc7517_a2_oct_key(self):
        result = self.tool.execute(mode="analyze", jwk=RFC_7517_A2_OCT)
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["contains_private_material"])
        self.assertEqual(result["private_parameters"], ["k"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["strength"]["key_bytes"], 64)
        self.assertEqual(result["strength"]["key_bits"], 512)
        self.assertEqual(result["strength"]["strength_tier"], "non-standard-length")
        codes = {note["code"] for note in result["notes"]}
        self.assertIn("oct_key_non_standard", codes)
        self.assertEqual(reference_thumbprint(RFC_7517_A2_OCT), result["thumbprint"])

    def test_rfc7517_a3_rsa_public_values(self):
        result = self.tool.execute(mode="analyze", jwk=RFC_7517_A3_RSA_PUBLIC)
        self.assertEqual(result["status"], "success")
        self.assertFalse(result["contains_private_material"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["strength"]["modulus_bits"], 2048)
        self.assertEqual(result["strength"]["modulus_bytes"], 256)
        self.assertEqual(result["strength"]["strength_tier"], "2048")
        self.assertEqual(result["strength"]["comparable_security_bits"], 112)
        self.assertIn("NIST SP 800-57", result["strength"]["nist_note"])
        self.assertEqual(result["strength"]["exponent_bits"], 17)
        self.assertEqual(result["strength"]["exponent_value_ok"], True)
        self.assertIn("65537", result["strength"]["exponent_note"])

    def test_rfc8037_ed25519_public_key(self):
        result = self.tool.execute(mode="analyze", jwk=RFC_8037_ED25519_PUBLIC)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["kty"], "OKP")
        self.assertTrue(result["recognized"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["strength"]["crv"], "Ed25519")
        self.assertEqual(result["strength"]["key_bytes_expected"], 32)
        self.assertEqual(result["strength"]["x_bytes"], 32)
        self.assertEqual(reference_thumbprint(RFC_8037_ED25519_PUBLIC), result["thumbprint"])

    def test_rfc7638_worked_example_byte_exact(self):
        """The RFC 7638 section 3.1 worked example must reproduce byte-exact."""
        result = self.tool.execute(mode="thumbprint", jwk=RFC_7517_A3_RSA_PUBLIC)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["thumbprint"], RFC_7638_THUMBPRINT)
        self.assertEqual(reference_thumbprint(RFC_7517_A3_RSA_PUBLIC), RFC_7638_THUMBPRINT)

    def test_rfc_vectors_via_json_text_input(self):
        """RFC keys arrive as JSON text (LLM path) as well as dicts."""
        for key in (RFC_7517_A1_EC, RFC_7517_A2_OCT, RFC_7517_A3_RSA_PUBLIC, RFC_8037_ED25519_PUBLIC):
            result = self.tool.execute(mode="analyze", jwk=json.dumps(key))
            self.assertEqual(result["status"], "success", key["kty"])
            self.assertEqual(result["errors"], [], key["kty"])


class JwkToolSyntheticKeyTest(unittest.TestCase):
    """300 seeded synthetic keys: structure reports and RFC 7638 parity."""

    def setUp(self):
        self.tool = JwkTool()
        rng = random.Random(0xA7517)
        self.keys = []
        for i in range(100):
            bits = (2048, 3072, 4096)[i % 3]
            key = rsa_public_jwk(rng, bits)
            key["kid"] = f"rsa-{i}"
            self.keys.append((key, {"modulus_bits": bits}))
        for i in range(100):
            crv, size = (("P-256", 32), ("P-384", 48), ("P-521", 66), ("P-256K", 32))[i % 4]
            key = ec_public_jwk(rng, crv, size)
            key["kid"] = f"ec-{i}"
            self.keys.append((key, {"coordinate_bytes": size, "curve_bits": {32: 256, 48: 384, 66: 521}[size]}))
        for i in range(50):
            size = (16, 24, 32)[i % 3]
            key = oct_jwk(rng, size)
            self.keys.append((key, {"key_bits": size * 8}))
        for i in range(50):
            crv, size = (("Ed25519", 32), ("X25519", 32), ("Ed448", 57), ("X448", 57))[i % 4]
            key = okp_public_jwk(rng, crv, size)
            self.keys.append((key, {"key_bytes": size}))
        self.assertEqual(len(self.keys), 300)

    def test_structure_and_thumbprint_parity(self):
        for key, expectations in self.keys:
            with self.subTest(kid=key.get("kid"), kty=key["kty"]):
                result = self.tool.execute(mode="analyze", jwk=key)
                self.assertEqual(result["status"], "success")
                self.assertTrue(result["recognized"])
                self.assertEqual(result["errors"], [], key)
                strength = result["strength"]
                if key["kty"] == "RSA":
                    self.assertEqual(strength["modulus_bits"], expectations["modulus_bits"])
                    self.assertIn(strength["strength_tier"], ("2048", "3072", "4096"))
                    self.assertIn("NIST SP 800-57", strength["nist_note"])
                    self.assertEqual(strength["exponent_bits"], 17)
                elif key["kty"] == "EC":
                    self.assertEqual(strength["x_bytes"], expectations["coordinate_bytes"])
                    self.assertEqual(strength["y_bytes"], expectations["coordinate_bytes"])
                    self.assertEqual(strength["curve_bits"], expectations["curve_bits"])
                elif key["kty"] == "oct":
                    self.assertEqual(strength["key_bits"], expectations["key_bits"])
                    self.assertTrue(result["contains_private_material"])
                else:
                    self.assertEqual(strength["x_bytes"], expectations["key_bytes"])
                # RFC 7638 parity against the independent reference implementation.
                self.assertEqual(reference_thumbprint(key), result["thumbprint"])
                thumb = self.tool.execute(mode="thumbprint", jwk=key)
                self.assertEqual(thumb["thumbprint"], result["thumbprint"])

    def test_synthetic_keys_are_not_real_credentials(self):
        """Guard the no-credential-literal rule: synthetic material is seeded random."""
        for key, _ in self.keys:
            if key["kty"] == "RSA":
                decoded = base64.urlsafe_b64decode(key["n"] + "=" * (-len(key["n"]) % 4))
                # A semiprime would be hard to factor; filler moduli are not
                # verified as primes at all, and that is exactly the point.
                self.assertGreater(len(decoded), 200)
            self.assertNotIn("d", key)
            self.assertNotIn("p", key)
            self.assertNotIn("q", key)


class JwkToolMutationTest(unittest.TestCase):
    """Structure mutation battery: 200+ mutated keys must be detected precisely."""

    def setUp(self):
        self.tool = JwkTool()
        rng = random.Random(0xBABE)
        self.rng = rng
        self.base_rsa = rsa_public_jwk(rng, 2048)
        self.base_ec = ec_public_jwk(rng, "P-521", 66)
        self.base_oct = oct_jwk(rng, 32)
        self.base_okp = okp_public_jwk(rng, "Ed448", 57)

    def error_codes(self, result):
        return {error["code"] for error in result.get("errors", [])}

    def test_missing_required_parameters(self):
        cases = []
        for name in ("n", "e"):
            key = dict(self.base_rsa)
            del key[name]
            cases.append((key, name))
        for name in ("crv", "x", "y"):
            key = dict(self.base_ec)
            del key[name]
            cases.append((key, name))
        key = dict(self.base_oct)
        del key["k"]
        cases.append((key, "k"))
        for name in ("crv", "x"):
            key = dict(self.base_okp)
            del key[name]
            cases.append((key, name))
        for key, name in cases:
            with self.subTest(kty=key["kty"], missing=name):
                result = self.tool.execute(mode="analyze", jwk=key)
                self.assertEqual(result["status"], "success")
                self.assertIn("missing_required_parameter", self.error_codes(result))
                self.assertTrue(any(error.get("params") == [name] for error in result["errors"]))
        self.assertEqual(len(cases), 8)

    def test_wrong_coordinate_lengths(self):
        cases = 0
        for crv, size in (("P-256", 32), ("P-384", 48), ("P-521", 66), ("P-256K", 32)):
            for name in ("x", "y"):
                for delta in (-1, 1):
                    key = ec_public_jwk(self.rng, crv, size)
                    if delta > 0:
                        payload = random_bytes(self.rng, size) + bytes([0x42])
                    else:
                        payload = random_bytes(self.rng, size - 1)
                    key[name] = b64u(payload)
                    result = self.tool.execute(mode="analyze", jwk=key)
                    self.assertIn("ec_coordinate_length", self.error_codes(result), (crv, name, delta))
                    self.assertTrue(any(error.get("actual") == size + delta and error.get("expected") == size
                                        for error in result["errors"]))
                    cases += 1
        for crv, size in (("Ed25519", 32), ("Ed448", 57), ("X25519", 32), ("X448", 57)):
            for delta in (-1, 1):
                key = okp_public_jwk(self.rng, crv, size)
                key["x"] = b64u(random_bytes(self.rng, size + delta))
                result = self.tool.execute(mode="analyze", jwk=key)
                self.assertIn("okp_key_length", self.error_codes(result), (crv, delta))
                cases += 1
        # The classic P-521 off-by-one: 64- and 65-byte coordinates are both wrong.
        for wrong in (64, 65):
            key = ec_public_jwk(self.rng, "P-521", 66)
            key["x"] = b64u(random_bytes(self.rng, wrong))
            result = self.tool.execute(mode="analyze", jwk=key)
            self.assertIn("ec_coordinate_length", self.error_codes(result))
            self.assertIn("66 bytes, not 64 or 65", json.dumps(result["errors"]))
        self.assertEqual(cases, 24)

    def test_ec_private_key_length_checked_for_every_curve(self):
        """Regression: the EC private key d must match the coordinate byte
        length (RFC 7518 6.2.2.1) for every supported curve, exactly as OKP
        validates d and EC validates x/y."""
        for crv, size in (("P-256", 32), ("P-384", 48), ("P-521", 66), ("P-256K", 32), ("secp256k1", 32)):
            for delta in (-1, 1):
                key = ec_public_jwk(self.rng, crv, size)
                key["d"] = b64u(random_bytes(self.rng, size + delta))
                result = self.tool.execute(mode="analyze", jwk=key)
                self.assertIn("ec_coordinate_length", self.error_codes(result), (crv, delta))
                entry = next(
                    e for e in result["errors"]
                    if e["code"] == "ec_coordinate_length" and e.get("param") == "d"
                )
                self.assertEqual(entry["actual"], size + delta)
                self.assertEqual(entry["expected"], size)
                self.assertEqual(result["strength"]["d_bytes"], size + delta)
        # A correctly sized d passes with no structural error (private-material warning only).
        key = ec_public_jwk(self.rng, "P-521", 66)
        key["d"] = b64u(random_bytes(self.rng, 66))
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertEqual(self.error_codes(result), set())
        self.assertTrue(result["contains_private_material"])

    def test_invalid_character_not_echoed_for_private_parameters(self):
        """Regression: base64url defects in private parameters must not echo
        the offending character (it is key material); public parameters keep
        the diagnostic character."""
        secret_oct = oct_jwk(self.rng, 32)
        mutated = dict(secret_oct)
        mutated["k"] = secret_oct["k"][:10] + "+" + secret_oct["k"][11:]
        result = self.tool.execute(mode="analyze", jwk=mutated)
        self.assertIn("base64url_invalid_character", self.error_codes(result))
        entry = next(e for e in result["errors"] if e["code"] == "base64url_invalid_character")
        self.assertEqual(entry["param"], "k")
        self.assertEqual(entry["position"], 10)
        self.assertNotIn("'+'", entry["detail"])
        self.assertIn("withheld", entry["detail"])
        rendered = json.dumps(result)
        for fragment in (mutated["k"], secret_oct["k"][:16], secret_oct["k"][-16:]):
            self.assertNotIn(fragment, rendered)
        # EC d: same rule.
        key = ec_public_jwk(self.rng, "P-384", 48)
        d_value = b64u(random_bytes(self.rng, 48))
        key["d"] = d_value[:20] + "/" + d_value[21:]
        result = self.tool.execute(mode="analyze", jwk=key)
        entry = next(e for e in result["errors"] if e["code"] == "base64url_invalid_character")
        self.assertEqual(entry["param"], "d")
        self.assertEqual(entry["position"], 20)
        self.assertNotIn("'/'", entry["detail"])
        self.assertNotIn(d_value, json.dumps(result))
        # Public parameters keep the character for diagnosis.
        key = dict(self.base_rsa)
        key["n"] = key["n"][:5] + "#" + key["n"][6:]
        result = self.tool.execute(mode="analyze", jwk=key)
        entry = next(e for e in result["errors"] if e["code"] == "base64url_invalid_character")
        self.assertIn("'#'", entry["detail"])
        # Padding defects stay diagnosable on private parameters: '=' is
        # structural, not value material, so the message is unchanged.
        key = oct_jwk(self.rng, 32)
        key["k"] += "="
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("base64url_padding_present", self.error_codes(result))
        self.assertIn("padding", json.dumps(result["errors"]))

    def test_bad_base64url_positions(self):
        cases = [
            ("n", "AQ+B", 2, "base64url_invalid_character"),   # '+' is standard base64 only
            ("n", "AQ/B", 2, "base64url_invalid_character"),   # '/' likewise
            ("e", "A#AB", 1, "base64url_invalid_character"),
            ("e", "AQAB=", 4, "base64url_padding_present"),    # '=' padding forbidden
            ("n", "AAAA AAAA", 4, "base64url_invalid_character"),  # whitespace
        ]
        for name, value, position, code in cases:
            with self.subTest(value=value):
                key = dict(self.base_rsa)
                key[name] = value
                result = self.tool.execute(mode="analyze", jwk=key)
                self.assertIn(code, self.error_codes(result))
                entry = next(error for error in result["errors"] if error["code"] == code)
                self.assertEqual(entry["param"], name)
                self.assertEqual(entry["position"], position)
        # length % 4 == 1 is structurally impossible.
        key = dict(self.base_rsa)
        key["e"] = "A"
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("base64url_invalid_length", self.error_codes(result))
        entry = next(error for error in result["errors"] if error["code"] == "base64url_invalid_length")
        self.assertEqual(entry["position"], 0)
        # The same rules apply to every base64url parameter of every kty.
        checked = 0
        for key, names in (
            (self.base_ec, ("x", "y")),
            (self.base_oct, ("k",)),
            (self.base_okp, ("x",)),
        ):
            for name in names:
                mutated = dict(key)
                mutated[name] = mutated[name][:-1] + "+"
                result = self.tool.execute(mode="analyze", jwk=mutated)
                self.assertIn("base64url_invalid_character", self.error_codes(result))
                self.assertEqual(next(e for e in result["errors"] if e["code"] == "base64url_invalid_character")["position"],
                                 len(mutated[name]) - 1)
                checked += 1
        self.assertEqual(checked, 4)

    def test_private_parameters_on_public_keys(self):
        secret_d = b64u(random_bytes(self.rng, 32))
        # d added to an RSA public key.
        key = dict(self.base_rsa)
        key["d"] = b64u(random_bytes(self.rng, 256))
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertTrue(result["contains_private_material"])
        self.assertIn("d", result["private_parameters"])
        warning = next(w for w in result["warnings"] if w["code"] == "private_material_present")
        self.assertEqual(warning["params"], ["d"])
        self.assertEqual(result["errors"], [])
        # d added to EC and OKP public keys.
        for base, size in ((self.base_ec, 66), (self.base_okp, 57)):
            key = dict(base)
            key["d"] = secret_d if size == 32 else b64u(random_bytes(self.rng, size))
            result = self.tool.execute(mode="analyze", jwk=key)
            self.assertTrue(result["contains_private_material"])
            self.assertEqual(result["private_parameters"], ["d"])
        # oct is inherently private.
        result = self.tool.execute(mode="analyze", jwk=self.base_oct)
        self.assertTrue(result["contains_private_material"])
        # Parameter inventory flags private parameters and never carries values.
        flagged = [p for p in result["parameters"] if p.get("private")]
        self.assertEqual([p["name"] for p in flagged], ["k"])
        self.assertNotIn("value", flagged[0])

    def test_rsa_consistency_errors(self):
        # Even modulus.
        key = dict(self.base_rsa)
        even = int.from_bytes(base64.urlsafe_b64decode(key["n"] + "=="), "big") & ~1
        key["n"] = b64u(even.to_bytes(256, "big"))
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("rsa_modulus_even", self.error_codes(result))
        # Below-2048 modulus: reported, not enforced.
        key = rsa_public_jwk(self.rng, 1024)
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertEqual(self.error_codes(result), set())
        self.assertEqual(result["strength"]["strength_tier"], "below-2048")
        warning_codes = {w["code"] for w in result["warnings"]}
        self.assertIn("rsa_modulus_below_2048", warning_codes)
        # e below range, e even, e huge, e = 3.
        for exponent, code in ((b64u((2).to_bytes(2, "big")), "rsa_exponent_range"), (b64u((4).to_bytes(2, "big")), "rsa_exponent_even")):
            key = dict(self.base_rsa)
            key["e"] = exponent
            result = self.tool.execute(mode="analyze", jwk=key)
            self.assertIn(code, self.error_codes(result))
        key = dict(self.base_rsa)
        key["e"] = b64u((2 ** 256).to_bytes(33, "big"))
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("rsa_exponent_range", self.error_codes(result))
        key = dict(self.base_rsa)
        key["e"] = "Aw"  # e = 3
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("rsa_exponent_weak", {w["code"] for w in result["warnings"]})
        self.assertEqual(result["strength"]["exponent_bits"], 2)
        # p without q; CRT parameters without d; malformed oth.
        key = dict(self.base_rsa)
        key["p"] = b64u(random_bytes(self.rng, 128))
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("rsa_prime_pair", self.error_codes(result))
        key = dict(self.base_rsa)
        key["dp"] = b64u(random_bytes(self.rng, 128))
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("rsa_crt_without_d", self.error_codes(result))
        key = dict(self.base_rsa)
        key["oth"] = "not-a-list"
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("oth_type", self.error_codes(result))
        # 3072 and 4096 tiers.
        for bits in (3072, 4096):
            result = self.tool.execute(mode="analyze", jwk=rsa_public_jwk(self.rng, bits))
            self.assertEqual(result["strength"]["strength_tier"], str(bits))

    def test_kty_and_common_parameter_errors(self):
        result = self.tool.execute(mode="analyze", jwk={"n": "AQAB"})
        self.assertIn("kty_required", self.error_codes(result))
        result = self.tool.execute(mode="analyze", jwk={"kty": 42})
        self.assertIn("kty_type", self.error_codes(result))
        result = self.tool.execute(mode="analyze", jwk={"kty": "XYZ", "n": "AQAB", "e": "AQAB"})
        self.assertIn("kty_unknown", self.error_codes(result))
        self.assertFalse(result["recognized"])
        key = dict(self.base_rsa)
        key["use"] = "signing"
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("use_value", self.error_codes(result))
        key = dict(self.base_rsa)
        key["key_ops"] = ["sign", "sign"]
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("key_ops_duplicates", {w["code"] for w in result["warnings"]})
        key = dict(self.base_rsa)
        key["key_ops"] = ["frobnicate"]
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("key_ops_unknown", {w["code"] for w in result["warnings"]})
        key = dict(self.base_rsa)
        key["use"] = "sig"
        key["key_ops"] = ["verify", "encrypt"]
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("use_key_ops_conflict", {w["code"] for w in result["warnings"]})
        key = dict(self.base_rsa)
        key["key_ops"] = "sign"
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("key_ops_type", self.error_codes(result))
        key = dict(self.base_rsa)
        key["n"] = 123
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("param_type", self.error_codes(result))
        # Unknown (extension) parameters are noted by name, never an error.
        key = dict(self.base_rsa)
        key["x-custom"] = "extension"
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["unknown_parameters"], ["x-custom"])
        self.assertIn("unknown_parameters", {n["code"] for n in result["notes"]})

    def test_unknown_curves(self):
        key = ec_public_jwk(self.rng, "P-512", 64)
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("ec_unknown_crv", self.error_codes(result))
        key = okp_public_jwk(self.rng, "Ed1232", 32)
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertIn("okp_unknown_crv", self.error_codes(result))
        # RFC 7638 required members for EC are crv/kty/x/y for any crv value,
        # so an unknown-curve key still yields a well-defined thumbprint.
        key = ec_public_jwk(self.rng, "P-512", 64)
        result = self.tool.execute(mode="thumbprint", jwk=key)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["thumbprint"], reference_thumbprint(key))

    def test_oct_tiers(self):
        for size, tier in ((16, "128-bit"), (24, "192-bit"), (32, "256-bit")):
            result = self.tool.execute(mode="analyze", jwk=oct_jwk(self.rng, size))
            self.assertEqual(result["strength"]["strength_tier"], tier)
        result = self.tool.execute(mode="analyze", jwk=oct_jwk(self.rng, 8))
        self.assertEqual(result["strength"]["strength_tier"], "below-128-bit")
        self.assertIn("oct_key_short", {w["code"] for w in result["warnings"]})

    def test_input_shapes(self):
        result = self.tool.execute(mode="analyze", jwk=None)
        self.assertEqual(result["status"], "error")
        result = self.tool.execute(mode="analyze", jwk="   ")
        self.assertEqual(result["status"], "error")
        result = self.tool.execute(mode="analyze", jwk="{not json")
        self.assertEqual(result["status"], "error")
        self.assertIn("not valid JSON", result["error"])
        result = self.tool.execute(mode="analyze", jwk=["list"])
        self.assertEqual(result["status"], "error")
        result = self.tool.execute(mode="bogus", jwk=self.base_rsa)
        self.assertEqual(result["status"], "error")
        result = self.tool.execute(mode="analyze")
        self.assertEqual(result["status"], "error")
        tool = JwkTool(max_set_keys=0)
        result = tool.execute(mode="analyze", jwk=self.base_rsa)
        self.assertEqual(result["status"], "error")

    def test_public_extract(self):
        rng = random.Random(0x57)
        key = rsa_public_jwk(rng, 2048)
        key.update({
            "d": b64u(random_bytes(rng, 256)),
            "p": b64u(random_bytes(rng, 128)),
            "q": b64u(random_bytes(rng, 128)),
            "dp": b64u(random_bytes(rng, 128)),
            "dq": b64u(random_bytes(rng, 128)),
            "qi": b64u(random_bytes(rng, 128)),
            "kid": "rsa-private",
            "use": "sig",
        })
        result = self.tool.execute(mode="public_extract", jwk=key)
        self.assertEqual(result["status"], "success")
        self.assertEqual(
            sorted(result["private_params_dropped"]),
            ["d", "dp", "dq", "p", "q", "qi"],
        )
        self.assertTrue(result["dropped_private_material"])
        self.assertEqual(sorted(result["public_jwk"]), ["e", "kid", "kty", "n", "use"])
        self.assertEqual(result["public_jwk"]["n"], key["n"])
        self.assertNotIn("d", result["public_jwk"])
        # EC drops only d; OKP drops only d; oct drops k and says why.
        key = ec_public_jwk(rng, "P-256", 32)
        key["d"] = b64u(random_bytes(rng, 32))
        result = self.tool.execute(mode="public_extract", jwk=key)
        self.assertEqual(result["private_params_dropped"], ["d"])
        self.assertEqual(sorted(result["public_jwk"]), ["crv", "kty", "x", "y"])
        key = okp_public_jwk(rng, "X448", 57)
        key["d"] = b64u(random_bytes(rng, 57))
        result = self.tool.execute(mode="public_extract", jwk=key)
        self.assertEqual(result["private_params_dropped"], ["d"])
        key = oct_jwk(rng, 32)
        key["kid"] = "symmetric"
        result = self.tool.execute(mode="public_extract", jwk=key)
        self.assertEqual(result["private_params_dropped"], ["k"])
        self.assertEqual(sorted(result["public_jwk"]), ["kid", "kty"])
        self.assertIn("symmetric", result["note"])
        # No private material: extraction is the identity on public keys.
        result = self.tool.execute(mode="public_extract", jwk=RFC_8037_ED25519_PUBLIC)
        self.assertFalse(result["dropped_private_material"])
        self.assertEqual(result["public_jwk"], RFC_8037_ED25519_PUBLIC)
        # Unknown kty refused.
        result = self.tool.execute(mode="public_extract", jwk={"kty": "XYZ"})
        self.assertEqual(result["status"], "error")

    def test_analyze_set_checks(self):
        shared = ec_public_jwk(self.rng, "P-256", 32)
        shared["kid"] = "dup"
        same_material = dict(shared)
        other_material = ec_public_jwk(self.rng, "P-256", 32)
        other_material["kid"] = "dup"
        distinct = rsa_public_jwk(self.rng, 2048)
        distinct["kid"] = "unique"
        distinct["alg"] = "RS256"
        document = {"keys": [shared, same_material, other_material, distinct, "not-an-object"]}
        result = self.tool.execute(mode="analyze_set", jwk=json.dumps(document))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["keys_count"], 5)
        self.assertEqual(result["keys_analyzed"], 5)
        duplicates = result["set_checks"]["duplicate_kids"]
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]["kid"], "dup")
        self.assertEqual(duplicates[0]["indices"], [0, 1, 2])
        conflicts = result["set_checks"]["thumbprint_conflicts"]
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0]["kid"], "dup")
        self.assertEqual(conflicts[0]["indices"], [0, 1, 2])
        self.assertEqual(len(conflicts[0]["thumbprints"]), 2)
        self.assertIn("thumbprint_conflicts", {w["code"] for w in result["warnings"]})
        self.assertEqual(result["set_checks"]["kty_census"], {"EC": 3, "RSA": 1})
        # The census covers analyzable keys; the non-object member is excluded.
        self.assertEqual(result["set_checks"]["alg_census"], {"(unset)": 3, "RS256": 1})
        self.assertEqual(result["keys"][4]["status"], "error")
        self.assertIn("set_entry_type", {e["code"] for e in result["keys"][4]["errors"]})
        # Same kid, same material: duplicate warning but no conflict.
        result = self.tool.execute(mode="analyze_set", jwk={"keys": [shared, same_material]})
        self.assertEqual(result["set_checks"]["duplicate_kids"][0]["indices"], [0, 1])
        self.assertEqual(result["set_checks"]["thumbprint_conflicts"], [])
        # Shape errors.
        result = self.tool.execute(mode="analyze_set", jwk={"nope": []})
        self.assertEqual(result["status"], "error")
        result = self.tool.execute(mode="analyze_set", jwk={"keys": {}})
        self.assertEqual(result["status"], "error")
        result = self.tool.execute(mode="analyze_set", jwk={"keys": []})
        self.assertEqual(result["status"], "success")
        self.assertIn("set_empty", {w["code"] for w in result["warnings"]})

    def test_mutation_battery_counts(self):
        """Programmatic battery over mutated copies: at least 200 distinct checks."""
        checks = 0
        bases = [self.base_rsa, self.base_ec, self.base_oct, self.base_okp]
        for i in range(200):
            base = bases[i % 4]
            key = dict(base)
            variant = i % 5
            if variant == 0:  # drop a random required parameter
                drop = {"RSA": "n", "EC": "x", "oct": "k", "OKP": "x"}[base["kty"]]
                del key[drop]
                result = self.tool.execute(mode="analyze", jwk=key)
                self.assertIn("missing_required_parameter", self.error_codes(result))
            elif variant == 1:  # corrupt the first material parameter at a shifting position
                name = {"RSA": "n", "EC": "x", "oct": "k", "OKP": "x"}[base["kty"]]
                position = i % len(key[name])
                key[name] = key[name][:position] + "#" + key[name][position + 1:]
                result = self.tool.execute(mode="analyze", jwk=key)
                self.assertIn("base64url_invalid_character", self.error_codes(result))
                entry = next(e for e in result["errors"] if e["code"] == "base64url_invalid_character")
                self.assertEqual(entry["position"], position)
            elif variant == 2:  # append padding
                name = {"RSA": "e", "EC": "y", "oct": "k", "OKP": "x"}[base["kty"]]
                key[name] += "=="
                result = self.tool.execute(mode="analyze", jwk=key)
                self.assertIn("base64url_padding_present", self.error_codes(result))
            elif variant == 3:  # synthetic private parameter on a public key
                name = "d" if base["kty"] in ("RSA", "EC", "OKP") else "k"
                if name not in key:
                    key[name] = b64u(random_bytes(self.rng, 32))
                result = self.tool.execute(mode="analyze", jwk=key)
                self.assertTrue(result["contains_private_material"])
            else:  # wrong-length material
                if base["kty"] == "RSA":
                    key["n"] = b64u(random_bytes(self.rng, 100))
                elif base["kty"] == "EC":
                    key["x"] = b64u(random_bytes(self.rng, 31))
                elif base["kty"] == "oct":
                    key["k"] = b64u(random_bytes(self.rng, 15))
                else:
                    key["x"] = b64u(random_bytes(self.rng, 56))
                result = self.tool.execute(mode="analyze", jwk=key)
                codes = self.error_codes(result) | {w["code"] for w in result["warnings"]}
                self.assertTrue(
                    codes & {"rsa_modulus_below_2048", "ec_coordinate_length", "oct_key_short", "okp_key_length"},
                    result["errors"],
                )
            checks += 1
        self.assertGreaterEqual(checks, 200)


class JwkToolMaskingInvariantTest(unittest.TestCase):
    """Meta-test: outputs over secret-bearing keys never echo key material."""

    def setUp(self):
        self.tool = JwkTool()
        rng = random.Random(0x5EC7E7)
        self.secrets = {}

        rsa_key = rsa_public_jwk(rng, 2048)
        rsa_key.update({
            "d": b64u(random_bytes(rng, 256)),
            "p": b64u(random_bytes(rng, 128)),
            "q": b64u(random_bytes(rng, 128)),
            "kid": "rsa-secret",
        })
        self.secrets.setdefault("RSA", []).extend([rsa_key["d"], rsa_key["p"], rsa_key["q"]])
        self.rsa_key = rsa_key

        ec_key = ec_public_jwk(rng, "P-384", 48)
        ec_key["d"] = b64u(random_bytes(rng, 48))
        self.secrets.setdefault("EC", []).append(ec_key["d"])
        self.ec_key = ec_key

        oct_key = oct_jwk(rng, 32)
        self.secrets.setdefault("oct", []).append(oct_key["k"])
        self.oct_key = oct_key

        okp_key = okp_public_jwk(rng, "X25519", 32)
        okp_key["d"] = b64u(random_bytes(rng, 32))
        self.secrets.setdefault("OKP", []).append(okp_key["d"])
        self.okp_key = okp_key

    def fragments(self, value: str):
        yield value
        if len(value) >= 16:
            yield value[:16]
            yield value[-16:]
            yield value[len(value) // 2 : len(value) // 2 + 16]

    def assert_no_secret_material(self, rendered: str, label: str):
        for kind, values in self.secrets.items():
            for value in values:
                for fragment in self.fragments(value):
                    self.assertNotIn(fragment, rendered, f"{label} leaked {kind} key material")

    def test_analyze_outputs_never_echo_secret_material(self):
        for key in (self.rsa_key, self.ec_key, self.oct_key, self.okp_key):
            for mode in ("analyze", "analyze_set"):
                payload = key if mode == "analyze" else {"keys": [key, key]}
                result = self.tool.execute(mode=mode, jwk=json.dumps(payload))
                self.assertEqual(result["status"], "success")
                rendered = json.dumps(result)
                self.assert_no_secret_material(rendered, mode)
        # Public material is not echoed by analyze either.
        result = self.tool.execute(mode="analyze", jwk=self.rsa_key)
        rendered = json.dumps(result)
        self.assertNotIn(self.rsa_key["n"], rendered)
        self.assertNotIn(self.rsa_key["e"], rendered)
        self.assertNotIn(self.oct_key["k"], rendered)
        self.assertNotIn(self.ec_key["x"], rendered)
        # public_extract drops private values while keeping public ones.
        result = self.tool.execute(mode="public_extract", jwk=self.rsa_key)
        rendered = json.dumps(result)
        for value in (self.rsa_key["d"], self.rsa_key["p"], self.rsa_key["q"]):
            for fragment in self.fragments(value):
                self.assertNotIn(fragment, rendered)
        self.assertEqual(result["public_jwk"]["n"], self.rsa_key["n"])
        self.assertEqual(result["public_jwk"]["e"], self.rsa_key["e"])

    def test_thumbprint_is_a_public_identifier_only(self):
        result = self.tool.execute(mode="thumbprint", jwk=self.oct_key)
        self.assertEqual(result["status"], "success")
        rendered = json.dumps(result)
        self.assertNotIn(self.oct_key["k"], rendered)
        self.assertEqual(result["thumbprint"], reference_thumbprint(self.oct_key))


class JwkToolBoundsTest(unittest.TestCase):
    """Pathological inputs: huge sets and huge parameters stay bounded."""

    def setUp(self):
        self.tool = JwkTool()

    def test_set_at_and_over_the_cap(self):
        rng = random.Random(0x1E5)
        key = ec_public_jwk(rng, "P-256", 32)
        at_cap = {"keys": [dict(key) for _ in range(10_000)]}
        result = self.tool.execute(mode="analyze_set", jwk=at_cap)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["keys_count"], 10_000)
        self.assertEqual(result["keys_analyzed"], 10_000)
        self.assertFalse(result["truncated"])
        over_cap = {"keys": [dict(key) for _ in range(10_001)]}
        result = self.tool.execute(mode="analyze_set", jwk=over_cap)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["keys_count"], 10_001)
        self.assertEqual(result["keys_analyzed"], 10_000)
        self.assertTrue(result["truncated"])
        self.assertIn("set_truncated", {w["code"] for w in result["warnings"]})

    def test_oversized_parameter_is_length_report_only(self):
        huge = "A" * (self.tool.max_param_chars + 1)
        key = {"kty": "RSA", "n": huge, "e": "AQAB"}
        result = self.tool.execute(mode="analyze", jwk=key)
        self.assertEqual(result["status"], "success")
        notes = [n for n in result["notes"] if n.get("mode") == "length_report_only"]
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["param"], "n")
        self.assertEqual(notes[0]["char_length"], self.tool.max_param_chars + 1)
        # No decode happened, so no bogus size/strength claims are made.
        self.assertNotIn("modulus_bits", result.get("strength", {}))
        self.assertNotIn(huge, json.dumps(result))

    def test_input_size_bound(self):
        tool = JwkTool(max_input_chars=200)
        key = {"kty": "RSA", "n": "A" * 5_000, "e": "AQAB"}
        result = tool.execute(mode="analyze", jwk=json.dumps(key))
        self.assertEqual(result["status"], "error")
        self.assertIn("max_input_chars", result["error"])

    def test_output_is_deterministic(self):
        rng = random.Random(0x0DE7)
        keys = {"keys": [rsa_public_jwk(rng, 2048), ec_public_jwk(rng, "P-521", 66), oct_jwk(rng, 32)]}
        first = json.dumps(self.tool.execute(mode="analyze_set", jwk=keys), sort_keys=True)
        second = json.dumps(self.tool.execute(mode="analyze_set", jwk=keys), sort_keys=True)
        self.assertEqual(first, second)


class JwkToolRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped jwk_tool.yaml as a tool component."""

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
        """Verify the shipped yaml resolves to a tool component exposing the JwkTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "JwkTool")

    def test_manager(self):
        """Verify the JwkTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, JwkTool)
        self.assertEqual(tool.input_keys, ["mode", "jwk"])
        self.assertEqual(tool.max_set_keys, 10_000)
        self.assertEqual(tool.max_param_chars, 1_048_576)
        schema = tool.args_model_schema
        self.assertEqual(schema["properties"]["mode"]["enum"], ["analyze", "analyze_set", "thumbprint", "public_extract"])
        self.assertEqual(schema["required"], ["mode", "jwk"])
        self.assertFalse(schema["additionalProperties"])

    def test_package_export(self):
        """Verify the tool is importable from the common_tool package."""
        from agentuniverse.agent.action.tool.common_tool import JwkTool as Exported

        self.assertIs(Exported, JwkTool)


if __name__ == "__main__":
    unittest.main()
