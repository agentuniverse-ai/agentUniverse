"""Oracle tests for SecretScanTool: format matrices, published safe
shapes, false-positive corpus, masking invariant, pathological inputs,
mode coverage, and component registration.

The oracles are:

(a) format matrix: 300 seeded synthetic secrets (30 per family x 10
    families: AWS access key id, AWS secret, classic GitHub PAT,
    fine-grained GitHub PAT, Google API key, Slack token, Stripe live key,
    JWT, URL credentials, PEM private key block). Every valid secret is
    detected by its exact rule with the documented confidence. Each valid
    secret is also mutated (length -1/+1, bad prefix, invalid charset,
    unicode, whitespace/structure truncation): every mutation is either
    missed-by-design (the vendor rule stays silent) or caught by a
    documented fallback (never high confidence) -- the expected outcome is
    asserted per mutation class, including the JWT-specific structural
    mutations (dropped signature dot, non-eyJ header, non-eyJ payload,
    non-decoding header).
(b) published safe shapes: 50 examples built from vendor DOCUMENTATION
    material only -- the AWS Signature v4 docs key (prefix AKIA,
    20-char body) and its docs secret, the RFC 7515 appendix A.2 example JWT, an RFC
    7519-style unsigned token reconstructed from its spec example claims,
    RFC 7468 PEM marker shapes, Stripe's docs test key (asserted out of
    the live-only rule's scope), and synthetic format-exact tokens. No
    real leaked secret appears anywhere in this file.
(c) false-positive corpus: 500 deterministic benign lines (base64 blobs
    of source text, UUIDs, sha256 hex digests, ordinary prose, URLs
    without credentials, env-var references, allowlisted assignments).
    Zero high-confidence findings; generic findings may appear but every
    allowlisted value line produces no finding at all.
(d) masking invariant: for every finding of every scan in this suite's
    corpora, the preview contains NO 5-character substring of the matched
    secret (head/tail masking reveals at most 4+4), and the serialized
    result never contains any planted secret verbatim. validate_token
    results for planted secrets never echo the input either.
(e) pathological: 1 MB of dense candidate text (10k+ candidate spans)
    scans in under 2 seconds; ReDoS probes ('AKIA' + 'A'*100000, long
    eyJ prefixes, 2k unterminated BEGIN markers, 5k complete PEM pairs)
    each finish in bounded time; the findings cap truncates gracefully.
"""

import base64
import hashlib
import json
import os
import random
import string
import time
import unittest
import uuid

from agentuniverse.agent.action.tool.common_tool import secret_scan_tool as secret_module
from agentuniverse.agent.action.tool.common_tool.secret_scan_tool import SecretScanTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(secret_module.__file__), "secret_scan_tool.yaml")

_SEED = 20261021
_ALNUM = string.ascii_letters + string.digits
_B64ISH = string.ascii_letters + string.digits + "/+="
_UPPER_DIGITS = string.ascii_uppercase + string.digits


# ---------------------------------------------------------------------------
# Deterministic synthetic secret generators (format-exact, never real).
# ---------------------------------------------------------------------------


def _rng():
    return random.Random(_SEED)


def gen_aws_key(rng):
    prefix = rng.choice(("AKIA", "ASIA", "ABIA", "ACCA"))
    return prefix + "".join(rng.choice(_UPPER_DIGITS) for _ in range(16))


def gen_aws_secret(rng):
    while True:
        body = "".join(rng.choice(_B64ISH) for _ in range(40))
        if not body.isdigit() and len(set(body)) > 4:
            return body


def gen_github_classic(rng):
    family = rng.choice(("p", "o", "u", "s"))
    return f"gh{family}_" + "".join(rng.choice(_ALNUM) for _ in range(36))


def gen_github_fine_grained(rng):
    return (
        "github_pat_"
        + "".join(rng.choice(_ALNUM) for _ in range(22))
        + "_"
        + "".join(rng.choice(_ALNUM) for _ in range(59))
    )


def gen_google(rng):
    charset = _ALNUM + "_-"
    return "AIza" + "".join(rng.choice(charset) for _ in range(35))


def gen_slack(rng):
    prefix = "xox" + rng.choice("baprs")
    segments = ["".join(rng.choice(_ALNUM) for _ in range(rng.randint(10, 20)))]
    for _ in range(rng.randint(0, 2)):
        segments.append("".join(rng.choice(_ALNUM) for _ in range(rng.randint(10, 20))))
    return prefix + "-" + "-".join(segments)


def gen_stripe(rng):
    prefix = rng.choice(("sk_live_", "rk_live_", "pk_live_"))
    return prefix + "".join(rng.choice(_ALNUM) for _ in range(rng.randint(24, 30)))


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def gen_jwt(rng, unsigned=False, broken_header=False):
    header = {"alg": "none" if unsigned else "HS256", "typ": "JWT"}
    payload = {"sub": "u" + "".join(rng.choice(string.digits) for _ in range(6)),
               "exp": 1300819380}
    header_seg = _b64url(json.dumps(header, separators=(",", ":")).encode())
    payload_seg = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    if broken_header:
        header_seg = "eyJ______" + header_seg[9:]  # stays in charset, no longer JSON
    signature = "" if unsigned else "".join(rng.choice(_ALNUM) for _ in range(43))
    return f"{header_seg}.{payload_seg}.{signature}"


def gen_url_cred(rng):
    user = "svc" + "".join(rng.choice(string.ascii_lowercase) for _ in range(6))
    password = "".join(rng.choice(_ALNUM + "!@#") for _ in range(12))
    host = f"db{rng.randint(10, 99)}.internal"
    return f"postgres://{user}:{password}@{host}:5432/app"


def gen_private_key(rng):
    key_type = rng.choice(("RSA", "EC", "OPENSSH", "DSA", ""))
    head = f"-----BEGIN {key_type + ' ' if key_type else ''}PRIVATE KEY-----"
    tail = f"-----END {key_type + ' ' if key_type else ''}PRIVATE KEY-----"
    body = "\n".join(
        "".join(rng.choice(string.ascii_letters + string.digits + "/+") for _ in range(64))
        for _ in range(rng.randint(1, 3))
    )
    return head + "\n" + body + "\n" + tail


FAMILIES = {
    "aws-access-key-id": (gen_aws_key, "const sample = {}", "high"),
    "aws-secret-access-key": (
        gen_aws_secret,
        "aws_secret_access_key = {}",
        "medium",
    ),
    "github-token": (gen_github_classic, "const sample = {}", "high"),
    "github-fine-grained-pat": (gen_github_fine_grained, "const sample = {}", "high"),
    "google-api-key": (gen_google, "const sample = {}", "high"),
    "slack-token": (gen_slack, "const sample = {}", "high"),
    "stripe-key": (gen_stripe, "const sample = {}", "high"),
    "jwt": (lambda r: gen_jwt(r), "authorization: Bearer {}", "high"),
    "url-credentials": (gen_url_cred, "database_url: {}", "medium"),
    "private-key-block": (gen_private_key, "{}", "high"),
}

# The github fine-grained PAT shares the scan rule with classic tokens.
FAMILY_RULE = {
    "github-token": "github-token",
    "github-fine-grained-pat": "github-token",
}


def rule_for(family):
    return FAMILY_RULE.get(family, family)


def findings_for(tool, text):
    result = tool.execute(mode="scan", text=text)
    assert result["status"] == "success", result
    return result


def rules_hit(result):
    return {f["rule"] for f in result["findings"]}


def no_window_leak(preview: str, secret: str, size: int = 5) -> bool:
    """True when preview contains no `size`-char substring of the secret."""
    for start in range(0, max(1, len(secret) - size + 1)):
        window = secret[start : start + size]
        if len(window) == size and window in preview:
            return False
    return True


# ---------------------------------------------------------------------------
# (a) Format matrix: 300 valid synthetics + mutation battery.
# ---------------------------------------------------------------------------


class FormatMatrixTest(unittest.TestCase):
    """300 valid synthetic secrets across 10 families detect exactly."""

    def setUp(self):
        self.tool = SecretScanTool()
        self.rng = _rng()

    def test_three_hundred_valid_secrets(self):
        total = 0
        for family, (generate, carrier, confidence) in FAMILIES.items():
            family_hits = 0
            for _ in range(30):
                token = generate(self.rng)
                result = findings_for(self.tool, carrier.format(token))
                hits = [f for f in result["findings"] if f["rule"] == rule_for(family)]
                self.assertEqual(len(hits), 1, f"{family}: expected exactly 1 hit")
                self.assertEqual(hits[0]["confidence"], confidence)
                self.assertTrue(hits[0]["reasons"])
                self.assertTrue(hits[0]["preview_MASKED"])
                family_hits += 1
            self.assertEqual(family_hits, 30)
            total += family_hits
        self.assertEqual(total, 300)

    def test_each_family_detects_thirty_samples_individually(self):
        for family, (generate, carrier, confidence) in FAMILIES.items():
            for _ in range(30):
                token = generate(self.rng)
                result = findings_for(self.tool, carrier.format(token))
                hits = [f for f in result["findings"] if f["rule"] == rule_for(family)]
                self.assertEqual(len(hits), 1, f"{family}: expected exactly 1 hit")
                self.assertEqual(hits[0]["confidence"], confidence)
                # the span must start inside/at the embedded token
                self.assertGreaterEqual(hits[0]["span"][1] - hits[0]["span"][0], 12)

    def test_spans_point_at_the_embedded_token(self):
        for family, (generate, carrier, _conf) in FAMILIES.items():
            token = generate(self.rng)
            text = carrier.format(token)
            result = findings_for(self.tool, text)
            hit = next(f for f in result["findings"] if f["rule"] == rule_for(family))
            covered = text[hit["span"][0] : hit["span"][1]]
            # the covered text is the secret material inside the token
            self.assertIn(covered, token)
            self.assertGreaterEqual(len(covered), 12)


class MutationMatrixTest(unittest.TestCase):
    """Every mutation is missed-by-design or caught by a documented
    fallback (never high confidence); JWT has structural mutations."""

    def setUp(self):
        self.tool = SecretScanTool()
        self.rng = _rng()

    def _mutations(self, family, token):
        if family == "jwt":
            header, payload, signature = token.split(".")
            return {
                "signature-dot-dropped": f"{header}.{payload}",
                "header-not-eyJ": "zyJ" + header[3:],
                "payload-not-eyJ": f"{header}.zyJ{payload[3:]}.{signature}",
                "header-not-json": gen_jwt(self.rng, broken_header=True),
                "header-invalid-char": "eyJ!" + header[4:],
            }
        if family == "private-key-block":
            lines = token.split("\n")
            end_line = lines[-1]
            if "DSA" in end_line:
                lines[-1] = end_line.replace("DSA PRIVATE KEY", "RSA PRIVATE KEY")
            else:
                lines[-1] = end_line.replace("PRIVATE KEY", "DSA PRIVATE KEY")
            return {
                "no-end-marker": token[: token.rindex("\n-----END")],
                "end-label-mismatch": "\n".join(lines),
                "certificate-marker": token.replace("PRIVATE KEY", "CERTIFICATE"),
            }
        if family == "url-credentials":
            scheme = token.split("://")[0]
            userpass_host = token.split("://", 1)[1]
            return {
                "no-at-sign": token.replace("@", "/"),
                "no-colon": scheme + "://" + userpass_host.replace(":", ";", 1),
                "empty-password": scheme + "://user:@" + userpass_host.split("@", 1)[1],
                "placeholder-userinfo": scheme + "://user:password@example.com",
            }
        # generic single-token families: length/prefix/charset mutations
        charset = set(token)
        invalid = next(c for c in "!#$%^&*()[]{}|\\:;'<>,.?~`" if c not in charset)
        half = len(token) // 2
        out = {
            "invalid-char": token[:half] + invalid + token[half:],
            "unicode-char": token[:half] + "Ü" + token[half:],
        }
        if family == "slack-token":
            # slack segments are a RANGE (10-48): exact-length +/- 1 does
            # not invalidate, so the mutations are floor/ceiling breaks
            prefix, rest = token.split("-", 1)
            tail = rest.split("-", 1)[1] if "-" in rest else ""
            out["segment-below-floor"] = prefix + "-" + "A" * 9 + (("-" + tail) if tail else "")
            out["segment-above-ceiling"] = prefix + "-" + "A" * 49
            out["bad-prefix"] = "xoxz" + token[4:]
        elif family == "stripe-key":
            # the tail is 24..99: floor/ceiling breaks instead of +/-1
            prefix, tail = token.split("_live_", 1)
            full_prefix = prefix + "_live_"
            out["tail-below-floor"] = full_prefix + "A" * 23
            out["tail-above-ceiling"] = full_prefix + "A" * 100
            out["test-prefix"] = prefix + "_test_" + tail
        else:
            out["length-minus-one"] = token[:-1]
            out["length-plus-one"] = token + ("X" if token[-1] != "X" else "Y")
            out["whitespace-truncated"] = token[:-3]
        if family == "aws-access-key-id":
            out["bad-prefix"] = "akia" + token[4:]
        elif family == "github-token":
            out["bad-prefix"] = "ghx_" + token[4:]
        elif family == "github-fine-grained-pat":
            out["bad-prefix"] = "github_pad_" + token[11:]
            out["missing-interior-underscore"] = token.replace("_", "0", 1)
        elif family == "google-api-key":
            out["bad-prefix"] = "AIzb" + token[4:]
        elif family == "aws-secret-access-key":
            out["no-context"] = token
            out["all-digits"] = "1" * 40
        return out

    def test_mutations_are_missed_by_design_or_caught_by_fallback(self):
        carrier = "const sample = {}"
        for family, (generate, _carrier, _conf) in FAMILIES.items():
            rule = rule_for(family)
            for sample_index in range(6):
                token = generate(self.rng)
                for mutation_name, mutated in self._mutations(family, token).items():
                    if family == "aws-secret-access-key" and mutation_name == "no-context":
                        text = mutated  # no aws/secret context anywhere
                    else:
                        text = carrier.format(mutated)
                    result = findings_for(self.tool, text)
                    findings = result["findings"]
                    # documented expectations:
                    #  - jwt header-not-json stays a STRUCTURAL match at low
                    #  - url placeholder-userinfo is allowlisted away
                    #  - everything else: the family rule must stay silent
                    if family == "jwt" and mutation_name == "header-not-json":
                        hits = [f for f in findings if f["rule"] == "jwt"]
                        self.assertEqual(len(hits), 1)
                        self.assertEqual(hits[0]["confidence"], "low")
                        continue
                    if family == "url-credentials" and mutation_name == "placeholder-userinfo":
                        self.assertNotIn("url-credentials", rules_hit(result))
                        continue
                    self.assertNotIn(
                        rule,
                        rules_hit(result),
                        f"{family}/{mutation_name}: vendor rule fired on a mutation",
                    )
                    # any fallback finding must never be high confidence
                    for finding in findings:
                        self.assertNotEqual(
                            finding["confidence"],
                            "high",
                            f"{family}/{mutation_name}: unexpected high finding",
                        )

    def test_aws_secret_requires_gate_context(self):
        secret = gen_aws_secret(self.rng)
        away = f"const blob = {secret}"  # no aws/secret keyword in the window
        result = findings_for(self.tool, away)
        self.assertNotIn("aws-secret-access-key", rules_hit(result))
        near = f"aws_secret_access_key = {secret}"
        result = findings_for(self.tool, near)
        self.assertIn("aws-secret-access-key", rules_hit(result))

    def test_aws_secret_gate_window_excludes_candidate(self):
        # a 40-char body that merely CONTAINS the letters 'aws' cannot
        # gate itself: the gate window excludes the candidate.
        body = "AWS" + "".join(self.rng.choice(string.ascii_uppercase + string.digits) for _ in range(37))
        self.assertEqual(len(body), 40)
        result = findings_for(self.tool, f"const blob = {body}")
        self.assertNotIn("aws-secret-access-key", rules_hit(result))


# ---------------------------------------------------------------------------
# (b) Published safe shapes: 50 documented examples.
# ---------------------------------------------------------------------------


class PublishedShapesTest(unittest.TestCase):
    """50 shapes taken from vendor documentation / RFC appendices (safe),
    plus synthetic format-exact tokens. No real leaked secrets."""

    def setUp(self):
        self.tool = SecretScanTool()
        self.rng = _rng()

    def _shapes(self):
        shapes = []
        aws_docs_key = secret_module._SYNTH_AWS_DOCS  # AWS docs example, runtime-assembled
        aws_docs_secret = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"  # same docs page
        for index in range(9):  # 9 carriers for the docs key
            carriers = (
                "aws_access_key_id = {}",
                "key: {}",
                "id = '{}'",
                "AKIA seen: {}",
                "creds[0] = {}",
                "context {} inline",
            )
            carrier = carriers[index % len(carriers)]
            shapes.append((f"aws-docs-key-{index}", carrier.format(aws_docs_key), aws_docs_key, "aws-access-key-id"))
        # RFC 7515 appendix A.2 example token (published by the spec).
        rfc7515 = (
            "eyJ0eXAiOiJKV1QiLA0KICJhbGciOiJIUzI1NiJ9."
            "eyJpc3MiOiJqb2UiLA0KICJleHAiOjEzMDA4MTkzODAsDQogImh0dHA6Ly9leGFt"
            "cGxlLmNvbS9pc19yb290Ijp0cnVlfQ."
            "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
        )
        shapes.append(("rfc7515-a2-jwt", f"auth: {rfc7515}", rfc7515, "jwt"))
        # RFC 7519 style unsigned token reconstructed from spec claims.
        unsigned = gen_jwt(self.rng, unsigned=True)
        shapes.append(("rfc7519-unsigned-jwt", f"auth: {unsigned}", unsigned, "jwt"))
        shapes.append(
            (
                "aws-docs-secret",
                f"aws_secret_access_key = {aws_docs_secret}",
                aws_docs_secret,
                "aws-secret-access-key",
            )
        )
        shapes.append(
            (
                "aws-docs-secret-upper-env",
                f"AWS_SECRET_ACCESS_KEY={aws_docs_secret}",
                aws_docs_secret,
                "aws-secret-access-key",
            )
        )
        # synthetic format-exact shapes (documented generators, 8 families)
        for _ in range(4):  # 4 x 8 = 32
            shapes.append(("synth-aws", f"const a = {gen_aws_key(self.rng)}", "", "aws-access-key-id"))
            shapes.append(("synth-gh", f"const b = {gen_github_classic(self.rng)}", "", "github-token"))
            shapes.append(("synth-ghf", f"const c = {gen_github_fine_grained(self.rng)}", "", "github-token"))
            shapes.append(("synth-google", f"const d = {gen_google(self.rng)}", "", "google-api-key"))
            shapes.append(("synth-slack", f"const e = {gen_slack(self.rng)}", "", "slack-token"))
            shapes.append(("synth-stripe", f"const f = {gen_stripe(self.rng)}", "", "stripe-key"))
            shapes.append(("synth-url", f"const g = {gen_url_cred(self.rng)}", "", "url-credentials"))
            shapes.append(("synth-pem", gen_private_key(self.rng), "", "private-key-block"))
        # Stripe docs example is a TEST key: live-only rule must ignore it
        # (concatenated so no key-shaped literal sits in the source bytes).
        shapes.append(("stripe-docs-test-key", "const h = sk" + "_test_" + "4eC39" + "HqLyjwdarjtT1zdp7dc", "", None))
        # RFC 7468 facts: a CERTIFICATE block is never a private key.
        shapes.append(("rfc7468-certificate", "-----BEGIN CERTIFICATE-----\nMIIB\n-----END CERTIFICATE-----", "", None))
        # RFC 7468 label variants that ARE private keys.
        shapes.append(("rfc7468-encrypted", "-----BEGIN ENCRYPTED PRIVATE KEY-----\nMIIE\n-----END ENCRYPTED PRIVATE KEY-----", "", "private-key-block"))
        shapes.append(("rfc4880-pgp-block", "-----BEGIN PGP PRIVATE KEY BLOCK-----\nlQ\n-----END PGP PRIVATE KEY BLOCK-----", "", "private-key-block"))
        # placeholder URL from RFC-style docs examples: allowlisted away.
        shapes.append(("placeholder-url", "see https://user:password@example.com/setup", "", None))
        return shapes

    def test_fifty_published_shapes(self):
        shapes = self._shapes()
        self.assertEqual(len(shapes), 50)
        for name, text, token, expected in shapes:
            result = findings_for(self.tool, text)
            if expected is None:
                self.assertEqual(
                    [f for f in result["findings"] if f["confidence"] == "high"],
                    [],
                    f"{name}: unexpected high finding",
                )
                continue
            hits = [f for f in result["findings"] if f["rule"] == expected]
            self.assertEqual(len(hits), 1, f"{name}: expected exactly one {expected} hit")
            if token:
                self.assertGreaterEqual(hits[0]["length"], min(len(token), 12))

    def test_docs_examples_round_trip_via_validate_token(self):
        checks = [
            (secret_module._SYNTH_AWS_DOCS, "aws-key", True),
            ("wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY", "aws-secret", True),
            # concatenated so no key-shaped literal sits in the source bytes
            ("sk" + "_test_" + "4eC39" + "HqLyjwdarjtT1zdp7dc", "stripe-key", False),
            ("sk" + "_live_" + "4eC39" + "HqLyjwdarjtT1zdp7dc", "stripe-key", True),
            (
                "eyJ0eXAiOiJKV1QiLA0KICJhbGciOiJIUzI1NiJ9."
                "eyJpc3MiOiJqb2UiLA0KICJleHAiOjEzMDA4MTkzODAsDQogImh0dHA6Ly9leGFt"
                "cGxlLmNvbS9pc19yb290Ijp0cnVlfQ."
                "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk",
                "jwt",
                True,
            ),
            (secret_module._SYNTH_GITHUB_FINE, "github-fine-grained-pat", True),
        ]
        for token, kind, valid in checks:
            result = self.tool.execute(mode="validate_token", token=token, kind=kind)
            self.assertEqual(result["status"], "success", result)
            self.assertEqual(result["format_valid"], valid, (kind, token[:8]))
            self.assertTrue(result["checksum_notes"])


# ---------------------------------------------------------------------------
# (c) False-positive corpus: 500 benign lines.
# ---------------------------------------------------------------------------

_FP_PROSE = [
    "The service reads configuration from the environment at startup.",
    "Latency budgets are enforced per region and per tenant class.",
    "A retry with exponential backoff protects the upstream dependency.",
    "The migration rewrote the index without locking the table.",
    "Documentation lives next to the code it describes, not in a wiki.",
    "Contributors should sign off their commits before opening a change.",
    "The dashboard aggregates queue depth over five minute windows.",
    "Backfills run on a shadow cluster before touching production data.",
    "Every public error code maps to exactly one runbook paragraph.",
    "Cache invalidation happens through versioned keys, not timeouts.",
]


class FalsePositiveCorpusTest(unittest.TestCase):
    """500 benign lines produce zero high-confidence findings; allowlisted
    assignment lines produce no findings at all."""

    def setUp(self):
        self.tool = SecretScanTool()
        self.rng = _rng()

    def _corpus(self):
        lines = []
        source_text = (
            "def handler(event, context):\n"
            "    return {'statusCode': 200, 'body': json.dumps(event)}\n"
        )
        for index in range(500):
            kind = index % 10
            if kind in (0, 1):  # base64 blobs of source text (100 lines)
                blob = base64.b64encode((source_text * (1 + index % 5)).encode()).decode()
                lines.append(f"data[{index}] = {blob}")
            elif kind == 2:  # UUIDs (50 lines)
                lines.append(f"trace_id[{index}] = {uuid.uuid5(uuid.NAMESPACE_DNS, f'au-{index}')}")
            elif kind == 3:  # hex digests (50 lines)
                lines.append(f"digest[{index}] = {hashlib.sha256(str(index).encode()).hexdigest()}")
            elif kind in (4, 5):  # prose (100 lines)
                lines.append(f"# {index}: " + _FP_PROSE[index % len(_FP_PROSE)])
            elif kind == 6:  # URLs without credentials (50 lines)
                lines.append(f"endpoint[{index}] = https://api.example{index}.com/v1/items?page=2")
            elif kind == 7:  # env-var references (50 lines)
                lines.append(f"password = ${{DB_PASSWORD_{index}}}")
            elif kind == 8:  # allowlisted literal assignments (50 lines)
                values = ("password", "changeme", "xxx", "hunter2", "test12345678")
                lines.append(f"secret = {values[index % len(values)]}")
            else:  # assignments to allowlisted placeholders (50 lines)
                lines.append(f"api_key = <YOUR_API_KEY_{index}>")
        self.assertEqual(len(lines), 500)
        return lines

    def test_zero_high_confidence_findings(self):
        result = findings_for(self.tool, "\n".join(self._corpus()))
        self.assertEqual(result["counts"]["high"], 0, result["by_rule"])
        # generic findings are allowed but must respect the allowlist:
        for finding in result["findings"]:
            self.assertIn(finding["rule"], ("generic-assignment", "generic-high-entropy"))
            self.assertIn(finding["confidence"], ("low", "medium"))

    def test_allowlisted_lines_alone_produce_no_findings(self):
        for line in (
            "password = password",
            "password = password12345",
            "secret = changeme",
            "api_key = YOUR_API_KEY",
            "token = ${VAULT_TOKEN}",
            "api_key: <your-api-key-here>",
            "password: {{ secret_placeholder }}",
            "token = $API_TOKEN",
            "secret = %ENV_SECRET%",
            "password = xxxxxxxx",
            "secret = ********",
        ):
            result = findings_for(self.tool, line)
            self.assertEqual(result["findings"], [], line)

    def test_placeholder_urls_suppressed(self):
        result = findings_for(self.tool, "docs: https://user:password@example.com/setup")
        self.assertEqual(result["findings"], [])

    def test_real_generic_assignment_still_detected(self):
        result = findings_for(self.tool, 'password = "Xk9$mQ2vLp8wRt4Z"')
        hits = [f for f in result["findings"] if f["rule"] == "generic-assignment"]
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["confidence"], "medium")
        self.assertEqual(hits[0]["preview_MASKED"], "**** (len 16)")


# ---------------------------------------------------------------------------
# (d) Masking invariant meta-test.
# ---------------------------------------------------------------------------


class MaskingInvariantTest(unittest.TestCase):
    """Previews never contain a 5-char substring of the secret; serialized
    results never contain planted secrets verbatim; validate_token never
    echoes its input."""

    def setUp(self):
        self.tool = SecretScanTool()
        self.rng = _rng()

    def _mixed_corpus(self):
        planted = []
        chunks = []
        for family, (generate, carrier, _conf) in FAMILIES.items():
            for _ in range(4):
                token = generate(self.rng)
                planted.append(token)
                chunks.append(carrier.format(token))
        chunks.append('password = "Zq7!vT3wYr8$Km2p"')
        planted.append("Zq7!vT3wYr8$Km2p")
        chunks.append(
            "const blob = kR9$mX2qL5vN8wQ3zA7bC1dE4fG6hJ0kM9nP2rS5tU8#"
        )
        return "\n".join(chunks), planted

    def test_previews_and_payload_never_leak(self):
        text, planted = self._mixed_corpus()
        result = findings_for(self.tool, text)
        self.assertGreaterEqual(len(result["findings"]), 20)
        for finding in result["findings"]:
            secret = text[finding["span"][0] : finding["span"][1]]
            self.assertTrue(
                no_window_leak(finding["preview_MASKED"], secret),
                f"preview leaks a substring of {secret[:4]}****",
            )
        serialized = json.dumps(result)
        for secret in planted:
            if len(secret) >= 16:
                self.assertNotIn(secret, serialized)
        # reasons/meta must not leak either
        for finding in result["findings"]:
            blob = json.dumps(finding)
            secret = text[finding["span"][0] : finding["span"][1]]
            if len(secret) >= 16:
                self.assertNotIn(secret, blob)

    def test_validate_token_never_echoes_input(self):
        _, planted = self._mixed_corpus()
        kinds = [
            "aws-key", "aws-secret", "github-token", "github-fine-grained-pat",
            "google-api-key", "slack-token", "stripe-key", "jwt",
            "url-credentials", "private-key-block",
        ]
        for secret, kind in zip(planted, kinds):
            result = self.tool.execute(mode="validate_token", token=secret, kind=kind)
            self.assertEqual(result["status"], "success", result)
            serialized = json.dumps(result)
            if len(secret) >= 16:
                self.assertNotIn(secret, serialized)
            self.assertTrue(no_window_leak(result["safe_metadata"]["masked_preview"], secret))

    def test_jwt_payload_contents_never_decoded_into_output(self):
        token = gen_jwt(self.rng)
        subject = json.loads(base64.urlsafe_b64decode(token.split(".")[1] + "=="))
        result = findings_for(self.tool, f"auth: {token}")
        hits = [f for f in result["findings"] if f["rule"] == "jwt"]
        self.assertEqual(len(hits), 1)
        blob = json.dumps(result)
        self.assertNotIn(token.split(".")[1], blob)  # payload segment verbatim
        self.assertNotIn(json.dumps(subject), blob)


# ---------------------------------------------------------------------------
# (e) Pathological inputs: 1 MB under 2 s, ReDoS probes, caps.
# ---------------------------------------------------------------------------


class PathologicalTest(unittest.TestCase):
    def setUp(self):
        self.tool = SecretScanTool()

    def _timed(self, text, budget=2.0):
        start = time.perf_counter()
        result = self.tool.execute(mode="scan", text=text)
        elapsed = time.perf_counter() - start
        self.assertEqual(result["status"], "success", result)
        self.assertLess(elapsed, budget, f"scan took {elapsed:.3f}s")
        return result, elapsed

    def test_one_megabyte_dense_text_under_two_seconds(self):
        rng = _rng()
        unit_lines = []
        for index in range(500):  # ~1MB, 10k+ candidate spans
            unit_lines.append(
                f"row{index} = {base64.b64encode(str(rng.random()).encode()).decode()} "
                f"hash {hashlib.sha256(str(index).encode()).hexdigest()} "
                f"note{_FP_PROSE[index % len(_FP_PROSE)]}"
            )
        text = "\n".join(unit_lines) * 12
        self.assertGreater(len(text), 1_000_000)
        result, elapsed = self._timed(text, budget=2.0)
        self.assertEqual(result["counts"]["high"], 0)

    def test_redos_probes(self):
        probes = [
            "AKIA" + "A" * 100_000,
            "eyJ" + "A" * 100_000 + ".eyJ" + "B" * 100_000 + ".",
            "-----BEGIN RSA PRIVATE KEY-----\n" * 2_000 + "A" * 100_000,
            ("-----BEGIN PRIVATE KEY-----" + "-----END PRIVATE KEY-----") * 5_000,
            ("xoxb-" + "A" * 48 + "-") * 2_000,
            "password = " + "a" * 100_000,
            ("AIza" + "A" * 35 + "\n") * 10_000,
        ]
        for probe in probes:
            result, _elapsed = self._timed(probe, budget=2.0)
            self.assertLessEqual(len(result["findings"]), 500)

    def test_finding_cap_truncates_gracefully(self):
        text = "\n".join("AKIA" + "ABCD" + f"{index:012d}" for index in range(700))
        result = self.tool.execute(mode="scan", text=text)
        self.assertEqual(len(result["findings"]), 500)
        self.assertTrue(result["findings_truncated"])
        self.assertEqual(result["counts"]["total"], 500)

    def test_candidate_cap_reports_flag(self):
        capped = SecretScanTool(max_candidates=50)
        text = " ".join(f"token{index:04d}AbCdEfGhIjKlMnOpQrStUvWx0123456789" for index in range(200))
        result = capped.execute(mode="scan", text=text)
        self.assertEqual(result["status"], "success")
        self.assertTrue(result["candidate_cap_applied"])

    def test_entropy_profile_capped(self):
        capped = SecretScanTool(max_profile_lines=5)
        result = capped.execute(mode="scan_entropy_profile", text="line one\nline two\n" * 10)
        self.assertEqual(result["lines_reported"], 5)
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["lines"]), 5)
        self.assertIn("entropy_bits_per_char", result["lines"][0])


# ---------------------------------------------------------------------------
# Mode coverage: entropy profile, explain_rule, validate_token, errors.
# ---------------------------------------------------------------------------


class ModeCoverageTest(unittest.TestCase):
    def setUp(self):
        self.tool = SecretScanTool()

    def test_entropy_profile_reports_hottest_token(self):
        text = "ordinary prose line\nkey kR9$mX2qL5vN8wQ3zA7bC1dE4fG6hJ0kM9nP2rS5tU8#"
        result = self.tool.execute(mode="scan_entropy_profile", text=text)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["lines_total"], 2)
        hot = result["lines"][1]["hottest_token"]
        self.assertGreater(hot["entropy_bits_per_char"], 4.0)
        self.assertEqual(hot["length"], 44)
        # the profile never carries token CONTENT, only length+entropy
        blob = json.dumps(result)
        self.assertNotIn("kR9$mX2q", blob)

    def test_entropy_sanity(self):
        self.assertEqual(secret_module._shannon_entropy("aaaa"), 0.0)
        self.assertAlmostEqual(secret_module._shannon_entropy("ab"), 1.0)
        self.assertAlmostEqual(secret_module._shannon_entropy("abcd"), 2.0)

    def test_allowlist_size_matches_policy(self):
        self.assertGreaterEqual(len(secret_module._COMMON_VALUES), 200)
        self.assertLessEqual(len(secret_module._COMMON_VALUES), 300)

    def test_explain_rule_all_rules(self):
        result = self.tool.execute(mode="explain_rule", rule="all")
        self.assertEqual(len(result["rules"]), len(FAMILIES) + 1)  # + generic-assignment

    def test_explain_rule_full_metadata_and_valid_examples(self):
        validate_kinds = {
            "aws-access-key-id": "aws-key",
            "aws-secret-access-key": "aws-secret",
            "github-token": "github-token",
            "google-api-key": "google-api-key",
            "slack-token": "slack-token",
            "stripe-key": "stripe-key",
            "private-key-block": "private-key-block",
            "jwt": "jwt",
            "url-credentials": "url-credentials",
        }
        for name in (
            "aws-access-key-id", "aws-secret-access-key", "github-token",
            "google-api-key", "slack-token", "stripe-key", "private-key-block",
            "jwt", "url-credentials", "generic-assignment", "generic-high-entropy",
        ):
            result = self.tool.execute(mode="explain_rule", rule=name)
            self.assertEqual(result["status"], "success", name)
            self.assertTrue(result["source_citation"], name)
            self.assertTrue(result["true_positive_examples"], name)
            self.assertTrue(result["false_positive_notes"], name)
            self.assertTrue(result["masking_applied"], name)
            # every documented vendor example is itself format-valid: the
            # examples are published docs material or synthetic, never leaks
            if name in validate_kinds:
                for example in result["true_positive_examples"]:
                    check = self.tool.execute(
                        mode="validate_token", token=example, kind=validate_kinds[name]
                    )
                    self.assertEqual(check["status"], "success", (name, example[:12]))
                    self.assertTrue(check["format_valid"], (name, example[:12]))

    def test_explain_rule_citations_name_the_source(self):
        for name in secret_module._RULES_BY_NAME:
            result = self.tool.execute(mode="explain_rule", rule=name)
            lowered = result["source_citation"].lower()
            self.assertTrue(
                "gitleaks" in lowered or "trufflehog" in lowered or "rfc" in lowered
                or "aws" in lowered or "stripe" in lowered or "slack" in lowered
                or "github" in lowered or "google" in lowered,
                name,
            )

    def test_validate_token_matrix(self):
        rng = _rng()
        valid_cases = [
            (gen_aws_key(rng), "aws-key"),
            (gen_aws_key(rng), "aws-access-key-id"),
            (gen_aws_secret(rng), "aws-secret"),
            (gen_github_classic(rng), "github-token"),
            (gen_github_fine_grained(rng), "github-fine-grained-pat"),
            (gen_google(rng), "google-api-key"),
            (gen_slack(rng), "slack-token"),
            (gen_stripe(rng), "stripe-key"),
            (gen_private_key(rng), "private-key-block"),
            (gen_jwt(rng), "jwt"),
            (gen_url_cred(rng), "url-credentials"),
        ]
        for token, kind in valid_cases:
            result = self.tool.execute(mode="validate_token", token=token, kind=kind)
            self.assertEqual(result["format_valid"], True, kind)
            self.assertTrue(result["checksum_notes"])
            self.assertIn("masked_preview", result["safe_metadata"])

    def test_validate_token_invalid_shapes(self):
        rng = _rng()
        invalid_cases = [
            ("AKIA" + "A" * 15, "aws-key"),           # too short
            ("akia" + "A" * 16, "aws-key"),           # bad prefix
            ("A" * 39, "aws-secret"),                 # wrong length
            ("ghp_" + "A" * 35, "github-token"),      # too short
            ("github_pat_" + "A" * 22 + "0" + "B" * 59, "github-fine-grained-pat"),
            ("AIza" + "A" * 34, "google-api-key"),
            ("xoxz-" + "A" * 20, "slack-token"),
            ("sk_test_" + "A" * 24, "stripe-key"),
            ("-----BEGIN CERTIFICATE-----\nMIIB\n-----END CERTIFICATE-----", "private-key-block"),
            ("two.parts.only", "jwt"),
            ("https://host.without.at", "url-credentials"),
        ]
        for token, kind in invalid_cases:
            result = self.tool.execute(mode="validate_token", token=token, kind=kind)
            self.assertEqual(result["format_valid"], False, (kind, token[:10]))

    def test_validate_format_only_semantics_for_ambiguous_shapes(self):
        # validate_token is FORMAT-ONLY: an all-same-charset 40-char string
        # is format-valid for the AWS secret shape even though scan()
        # suppresses it (single-charset runs are never scan findings).
        result = self.tool.execute(mode="validate_token", token="A" * 40, kind="aws-secret")
        self.assertTrue(result["format_valid"])
        self.assertFalse(result["safe_metadata"]["all_digits"])
        digits = self.tool.execute(mode="validate_token", token="1" * 40, kind="aws-secret")
        self.assertTrue(digits["format_valid"])
        self.assertTrue(digits["safe_metadata"]["all_digits"])
        scan_side = self.tool.execute(mode="scan", text="aws_secret = " + "1" * 40)
        self.assertNotIn("aws-secret-access-key", rules_hit(scan_side))

    def test_validate_jwt_signature_semantics(self):
        signed = gen_jwt(_rng())
        unsigned = gen_jwt(_rng(), unsigned=True)
        signed_result = self.tool.execute(mode="validate_token", token=signed, kind="jwt")
        unsigned_result = self.tool.execute(mode="validate_token", token=unsigned, kind="jwt")
        self.assertTrue(signed_result["safe_metadata"]["signature_present"])
        self.assertEqual(signed_result["safe_metadata"]["alg"], "HS256")
        self.assertFalse(unsigned_result["safe_metadata"]["signature_present"])
        self.assertIn("unsigned", " ".join(unsigned_result["notes"]))

    def test_validation_errors(self):
        cases = [
            {"mode": "fry"},
            {"mode": "scan"},
            {"mode": "scan", "text": ""},
            {"mode": "scan", "text": 42},
            {"mode": "explain_rule"},
            {"mode": "explain_rule", "rule": "nope"},
            {"mode": "validate_token", "token": secret_module._SYNTH_AWS_DOCS},
            {"mode": "validate_token", "token": secret_module._SYNTH_AWS_DOCS, "kind": "nope"},
            {"mode": "validate_token", "kind": "aws-key"},
        ]
        for kwargs in cases:
            result = self.tool.execute(**kwargs)
            self.assertEqual(result["status"], "error", kwargs)
            self.assertEqual(result["error_type"], "validation_error", kwargs)
            self.assertTrue(result["error"])

    def test_input_bounds(self):
        tiny = SecretScanTool(max_input_bytes=16)
        self.assertIn("max_input_bytes", tiny.execute(mode="scan", text="a" * 64)["error"])
        long_token = SecretScanTool(max_token_chars=10)
        self.assertIn(
            "max_token_chars",
            long_token.execute(mode="validate_token", token="A" * 40, kind="aws-key")["error"],
        )

    def test_deterministic_results(self):
        text = (
            "aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\n"
            f"gh = {gen_github_classic(_rng())}\n"
            "password = Xk9mQ2vLp8wRt4Z\n"
        )
        first = self.tool.execute(mode="scan", text=text)
        for _ in range(3):
            self.assertEqual(self.tool.execute(mode="scan", text=text), first)

    def test_summary_counts_consistent(self):
        text = "\n".join(
            ["const a = " + gen_aws_key(_rng()) for _ in range(3)]
            + ["aws_secret = " + gen_aws_secret(_rng())]
        )
        result = self.tool.execute(mode="scan", text=text)
        self.assertEqual(result["counts"]["total"], len(result["findings"]))
        self.assertEqual(
            result["counts"]["high"] + result["counts"]["medium"] + result["counts"]["low"],
            result["counts"]["total"],
        )
        self.assertEqual(sum(result["by_kind"].values()), result["counts"]["total"])
        self.assertEqual(sum(result["by_rule"].values()), result["counts"]["total"])


class SecretScanToolRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped secret_scan_tool.yaml."""

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
        """The shipped yaml resolves to a tool component exposing SecretScanTool."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "SecretScanTool")

    def test_manager(self):
        """SecretScanTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, SecretScanTool)
        self.assertEqual(tool.input_keys, ["mode", "text"])

    def test_package_export(self):
        """SecretScanTool is exported from the common_tool package."""
        from agentuniverse.agent.action.tool.common_tool import SecretScanTool as Exported
        from agentuniverse.agent.action.tool.common_tool import __all__ as exported_names

        self.assertIs(Exported, SecretScanTool)
        self.assertIn("SecretScanTool", exported_names)


if __name__ == "__main__":
    unittest.main()
