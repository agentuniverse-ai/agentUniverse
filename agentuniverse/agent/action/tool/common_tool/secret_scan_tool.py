#!/usr/bin/env python3
"""Secret and credential detection in text: published vendor formats,
context-gated AWS secrets, JWT structure analysis, URL credentials, and
generic assignment / entropy heuristics -- with ALWAYS-masked output.

The tool accepts arbitrary text and offers four deterministic,
stdlib-only modes (``re`` + ``base64`` + ``math`` are the only engines):

- ``scan``                -- findings ``[{rule, kind, span, preview_MASKED,
  confidence, reasons, line, meta}]`` plus a masked summary
- ``scan_entropy_profile``-- per-line entropy summary for forensic triage
- ``explain_rule``        -- one rule's pattern, source citation, safe
  (synthetic or vendor-documented) positive examples, false-positive notes,
  and the masking applied to its previews
- ``validate_token``      -- format validation of ONE candidate string for
  ONE kind, with checksum notes and safe metadata only

Rule set (every pattern is an equivalent of a rule published in the
open-source rule sets of truffleHog (trufflesecurity/trufflehog) and
gitleaks (gitleaks/gitleaks, rules/gitleaks.toml, MIT licensed),
re-derived here and hand-verified against the vendors' published format
documentation; the source pattern is cited in a comment on each regex and
via ``explain_rule``):

Vendor formats (anchored with boundary lookarounds so over-long or
under-long neighbors never half-match):

- ``aws-access-key-id``   -- 20 chars, prefixes AKIA/ASIA/ABIA/ACCA and
  the A3T+1 form, remainder ``[A-Z0-9]{16}`` (charset has no lowercase --
  verified against the AWS docs example key, prefix ``AKIA`` with a
  20-character uppercase-alphanumeric body).
- ``github-token``        -- ``ghp_``/``gho_``/``ghu_``/``ghs_`` + 36
  alphanumerics, ``ghr_`` + 76, and fine-grained ``github_pat_`` + 22 +
  ``_`` + 59 (the interior underscore is what distinguishes the
  fine-grained form; GitHub publishes no checksum, so this is format-only).
- ``google-api-key``      -- ``AIza`` + exactly 35 of ``[0-9A-Za-z_-]``.
- ``slack-token``         -- ``xox[baprs]-`` + one to four segments of
  10-48 alphanumerics (bot/app/legacy-user/refresh/session prefixes).
- ``stripe-key``          -- ``sk_live_``/``rk_live_``/``pk_live_`` + at
  least 24 alphanumerics (publishable ``pk_live_`` keys are still reported
  but the reason notes their lower sensitivity; ``*_test_`` never matches).
- ``private-key-block``   -- ``-----BEGIN [RSA |EC |OPENSSH |DSA |PGP |
  ENCRYPTED ]PRIVATE KEY[ BLOCK]-----`` through the matching END line.
  Detected with forward-only string pairing (find BEGIN, find the next
  END, require the same label) so a text of many BEGIN markers without
  any END stays linear -- never a ``[\\s\\S]*?`` backtracking scan per
  BEGIN.

Context-gated (the 40-char base64 body of an AWS secret access key is far
too generic to run ungated):

- ``aws-secret-access-key`` -- exactly 40 of ``[A-Za-z0-9/+=]``, reported
  only when a 160-character window on EACH side (the candidate itself is
  excluded from its own gate window, so a body that merely contains the
  letters 'aws' cannot gate itself) contains one of (case-insensitive)
  ``aws``/``amazon``/``secret``/``access key``/``access_key``/
  ``access-key``/``credentials``. This mirrors the truffleHog AWS
  detector, which always pairs the 40-char secret with key material or
  AWS context. All-same-character, near-same-character and all-digit
  strings never match.

Structure-analyzed:

- ``jwt``                 -- ``eyJ`` header and ``eyJ`` payload segments
  in base64url plus an optional empty signature, i.e. the JWS compact
  serialization of RFC 7515/7519 (any JSON object starts with ``{"`` whose
  base64url encoding begins ``eyJ``). The HEADER ONLY is decoded: the
  finding reports ``alg``/``typ``, whether a signature part is present,
  and whether the payload PARSES as JSON -- the payload's contents are
  never decoded into any output, because a JWT can embed secrets in its
  claims. High confidence needs a decodable header AND a signature part;
  unsigned (alg=none style) is medium; a non-decoding header is low.
- ``url-credentials``    -- ``scheme://user:pass@host`` style URLs (the
  RFC 3986 userinfo production before an '@'). The scheme is kept as
  non-secret context in ``meta`` while BOTH userinfo parts are masked
  (a username can itself be a secret). Placeholder URLs such as
  ``https://user:password@example.com`` are suppressed when both parts
  are allowlisted.

Generic (low-noise heuristics):

- ``generic-assignment`` -- ``password|secret|token|api[_-]?key|...``
  followed by ``:``/``=`` and a value of at least 8 non-space characters
  (an optional closing quote after the keyword makes JSON and YAML/INI
  both parse). The value is suppressed when it is an obvious non-secret
  (see the allowlist below); otherwise Shannon entropy over the value's
  own character frequencies decides medium (>= 3.5 bits/char) vs low.
- ``generic-high-entropy`` -- a standalone token of at least 40
  characters that mixes lowercase, uppercase, digits and symbols with
  entropy above 4.5 bits/char. This rule can only ever produce LOW
  confidence findings (random-looking blobs are often encoded, not
  secret).

Allowlist policy (``generic-assignment`` and ``url-credentials`` only):
~200 embedded obvious non-secrets -- 'password', 'changeme', 'xxx',
'hunter2', placeholder shapes like ``YOUR_API_KEY``/``your-api-key-here``,
``${ENV_VAR}``, ``{{var}}``, ``<token>``, ``%VAR%``, ``$VAR``, function
-call references like ``os.getenv(``, repeated-character and filler runs.
Trailing digits are folded away before lookup ('password12345' -> base
word 'password'), so the common family of suffixed examples is covered.
Vendor rules never consult the allowlist: ``sk_live_...`` next to the word
'placeholder' is still a live-format key and must be reported.

Masking policy (invariant, enforced by an oracle test): a preview reveals
at most the first 4 and last 4 characters of the matched secret and never
any 5-character substring of it -- e.g. ``AKIA****MPLE``. AWS/GitHub/
Google/Slack/Stripe/JWT previews use that head+tail form; URL credentials
mask BOTH user and password (``https://****:****@`` -- a username can
itself be a secret) and report the scheme as non-secret context; private
key previews show marker dashes only (``----****----``) with the key TYPE
(a label like 'RSA', not key material) and block length in ``meta``; the
two generic rules reveal nothing but the value's LENGTH (``**** (len 23)``).
``validate_token`` never echoes its input either: ``safe_metadata``
carries a masked preview, the length, and charset-class counts.

Determinism and bounds: no clocks, no randomness, no network; findings
are sorted by (start, end, rule order) and truncated at ``max_findings``
with an explicit ``findings_truncated`` flag; the entropy profile reports
at most ``max_profile_lines`` lines; standalone candidates are capped at
``max_candidates`` with an explicit ``candidate_cap_applied`` flag. All
regexes avoid nested unbounded quantifiers (the ReDoS oracle scans
``'AKIA' + 'A' * 100000``, long ``eyJ....eyJ....`` prefixes, thousands of
BEGIN markers without END, and 1 MB of dense candidate text in bounded
time).
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import base64
import json
import math
import re
from typing import Any

from agentuniverse.agent.action.tool.tool import Tool

_MODES = ("scan", "scan_entropy_profile", "explain_rule", "validate_token")

# ---------------------------------------------------------------------------
# Synthetic example credentials. These are hand-made format illustrations --
# never real secrets. They are assembled at runtime from two fragments so no
# complete credential-format literal appears in this source file (source
# scanners pattern-match such literals and raise false-positive alerts).
# ---------------------------------------------------------------------------
_SYNTH_AWS_DOCS = "AKIA" + "IOSFODNN7EXAMPLE"  # AWS Signature v4 docs example
_SYNTH_AWS_A = "AKIA" + "ABC123DEF456GHIJ"
_SYNTH_AWS_B = "ASIA" + "998877665544XYZQ"
_SYNTH_GOOGLE_A = "AIza" + "SyA1LbZ1234VaD5MNr8ZxjTT6IDy7Qz9Wq0"
_SYNTH_GOOGLE_B = "AIza" + "A0bB1cC2dD3eE4fF5gG6hH7iI8jJ9kK0lL1"
_SYNTH_GITHUB_PAT = "ghp_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
_SYNTH_GITHUB_FINE = (
    "github_pat_"
    + "Ab01Cd02Ef03Gh04Ij05KQ_"
    + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8S9t0U1v2w3X4y5Z6a7B8c9D"
)

# ---------------------------------------------------------------------------
# Detection patterns. Each comment cites the published rule the pattern is
# equivalent to, and what was hand-verified against the vendor's format docs.
# ---------------------------------------------------------------------------

# gitleaks rule "aws-access-token":
#   (?:A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z0-9]{16}
# Verified: 20 chars total, uppercase alphanumerics only; the AWS Signature
# v4 documentation example key (prefix AKIA, 20 chars) matches.
_AWS_KEY_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z0-9]{16}(?![A-Za-z0-9])"
)

# gitleaks rule "github-pat":
#   ghp_[0-9a-zA-Z]{36}|gho_[0-9a-zA-Z]{36}|ghu_[0-9a-zA-Z]{36}|
#   ghs_[0-9a-zA-Z]{36}|ghr_[0-9a-zA-Z]{76}|
#   github_pat_[0-9a-zA-Z]{22}_[0-9a-zA-Z]{59}
# Verified: classic PATs are prefix + 36 (refresh + 76); fine-grained PATs
# carry the underscore between a 22- and a 59-character alphanumeric run.
_GITHUB_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:"
    r"ghp_[A-Za-z0-9]{36}|gho_[A-Za-z0-9]{36}|ghu_[A-Za-z0-9]{36}|"
    r"ghs_[A-Za-z0-9]{36}|ghr_[A-Za-z0-9]{76}|"
    r"github_pat_[A-Za-z0-9]{22}_[A-Za-z0-9]{59}"
    r")(?![A-Za-z0-9])"
)

# gitleaks rule "google-api-key": AIza[0-9A-Za-z\-_]{35}
# Verified: 39 characters total; the tail may include - and _. The trailing
# guard also rejects -/_ so glued over-long runs never half-match.
_GOOGLE_RE = re.compile(r"(?<![A-Za-z0-9])AIza[0-9A-Za-z_-]{35}(?![0-9A-Za-z_-])")

# gitleaks "slack-access-token" family: xox[baprs]- prefixed tokens with
# one to four 10-48 character alphanumeric segments (bot xoxb-, app xoxa-,
# legacy user xoxp-, refresh xoxr-, session xoxs-).
_SLACK_RE = re.compile(
    r"(?<![A-Za-z0-9])xox[baprs]-[0-9A-Za-z]{10,48}(?:-[0-9A-Za-z]{10,48}){0,3}(?![A-Za-z0-9-])"
)

# gitleaks rules "stripe-access-token" (sk_live_) / "stripe-secret-key"
# (sk_live_|rk_live_) plus the publishable pk_live_ shape. 24+ tail.
_STRIPE_RE = re.compile(r"(?<![A-Za-z0-9])[srp]k_live_[0-9A-Za-z]{24,99}(?![A-Za-z0-9])")

# truffleHog AWS detector: a 40-character base64 body paired with key
# material or AWS context. Too generic ungated: only exactly-40 isolated
# runs of [A-Za-z0-9/+=] WITH an aws/amazon/secret/access-key/credentials
# keyword in the surrounding windows (candidate excluded) are reported.
# The gate boundary excludes only alphanumerics, so underscore-joined
# contexts like aws_secret / AWS_SECRET_ACCESS_KEY still gate. '=' is NOT
# a boundary character: KEY=<secret> is the canonical dotenv shape, while
# '/' and '+' only occur inside longer base64 runs and stay boundaries.
_AWS_SECRET_RE = re.compile(r"(?<![A-Za-z0-9/+])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])")
_AWS_SECRET_GATE_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:aws|amazon|secret|access[\s_-]?key|credentials?)(?![A-Za-z0-9])",
    re.IGNORECASE,
)

# gitleaks rule "jwt": eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[...]
# Tightened here: BOTH the header and the payload must start with eyJ (any
# JSON object literal encodes to eyJ..), which is what RFC 7519 compact
# serializations look like; the signature may be empty (alg=none).
_JWT_RE = re.compile(
    r"(?<![A-Za-z0-9_-])eyJ[A-Za-z0-9_-]{8,2048}\.eyJ[A-Za-z0-9_-]{8,2048}"
    r"\.[A-Za-z0-9_-]{0,2048}(?![A-Za-z0-9_-])"
)

# userinfo inside a URL: scheme://user:pass@ -- the RFC 3986 userinfo
# production before an '@'. Components exclude whitespace, '@', ':' and
# quotes so the class negation terminates each part linearly.
_URL_CRED_RE = re.compile(
    r"(?<![A-Za-z0-9+.-])([A-Za-z][A-Za-z0-9+.-]{1,16})://"
    r"([^\s/@:>'\"]{1,64}):([^\s/@:>'\"]{1,128})@"
)

# generic credential assignment. The published shape used across the
# truffleHog/gitleaks keyword rules,
#   (password|secret|token|api_key|apikey)\s*[=:]\s*['"]?(\S{8,})
# extended with the common spellings, an optional closing quote after the
# keyword (JSON) and a value class that stops at quotes/commas/semicolons.
_ASSIGN_RE = re.compile(
    r"(?<![A-Za-z0-9_])("
    r"password|passwd|pwd|secret|secrets|token|tokens|"
    r"api[\-_]?key|apikey|access[\-_]?key|auth[\-_]?token|client[\-_]?secret|"
    r"private[\-_]?key|credential|credentials"
    r")"
    r"[\"']?[ \t]*[:=][ \t]*[\"']?"
    r"([^\s\"',;]{8,256})",
    re.IGNORECASE,
)

# PEM markers (RFC 7468 label grammar). Pairing is forward-only with
# search()+find() so many BEGIN markers without any END stay linear.
_PK_BEGIN_RE = re.compile(
    r"-----BEGIN (?:(RSA|EC|OPENSSH|DSA|PGP|ENCRYPTED) )?PRIVATE KEY( BLOCK)?-----"
)
_PK_END_RE = re.compile(r"-----END ([A-Z0-9 ]*?)PRIVATE KEY( BLOCK)?-----")
_PK_MAX_BLOCKS = 256


def _pk_label(prefix: str | None, block: str | None) -> str:
    """Canonical PEM label, e.g. 'RSA PRIVATE KEY' or 'PRIVATE KEY BLOCK'."""
    head = (prefix or "").strip()
    return (head + " " if head else "") + "PRIVATE KEY" + (" BLOCK" if block else "")

_TOKEN_RUN_RE = re.compile(r"\S+")
_TRIM_EDGES_RE = re.compile(r"^[\(\[\{\"'`]+|[\)\]\}\"'`'.,;:]+$")

# ---------------------------------------------------------------------------
# Allowlist: obvious non-secrets for the generic rules (~200 literal values;
# trailing digits fold away before lookup, so password12345 -> password).
# ---------------------------------------------------------------------------

_COMMON_VALUES = frozenset(
    """
    password passwords passwd pass pwd secret secrets token tokens
    apikey apikeys your-api-key your_api_key access-key access_key
    auth-key auth_key client-secret client_secret private-key private_key
    placeholder placeholders placeholder-password example examples sample
    samples dummy fake notreal not-real redacted removed hidden masked
    test testing testtest testpass testpassword demo dev development
    staging prod production changeme change_me change-me letmein welcome
    admin administrator root user username guest anonymous default none
    null nil undefined nan true false todo fixme tbd xxx xxxx xxxxx xxxxxx
    xxxxxxx xxxxxxxx xxxxxxxxx hunter2 correcthorsebatterystaple qwerty
    qwerty123 qwertyuiop abc123 abcd1234 abcdefgh 0123456789 12345678
    123456789 1234567890 12345678910 password1 password123 password1234
    password12345 password123456 mypassword mypassword123 my-secret
    mysecret secretpassword secret_password thepassword the_password
    newpassword oldpassword temp temporary temp_password supersecret
    topsecret verysecret insecure strongpassword oauth_token access_token
    refresh_token session_token id_token bearer basic your_api_key_here
    your-password your_password your-secret your_secret your-token
    your_token your-password-here insert-here insert_here paste-here
    paste_here replace-me replace_me replace_me_please fill-me-in
    fill_me_in enter-your enter_your enter-your-password somepassword
    somesecret sometoken somepassword123 somepass somekey some_key
    this-is-a-password not-a-secret notasecret no-secret nosecret
    password-here password_here keyhere thekey the_key mykey my_key
    login signin credentials credential auth authorization
    postgres mysql mongodb redis rabbitmq elasticsearch webhook
    localhost example.com test.com foo bar baz foobar bazqux quux corge
    grault garply waldo fred plugh xyzzy sample-token sample_token
    sample-password sample_password demo-token demo_token demo-password
    demo_password fake-token fake_token fake-password fake_password
    dummy-token dummy_token dummy-password dummy_password
    placeholder-token placeholder_token your-openai-api-key
    your_openai_api_key openai_api_key anthropic_api_key xxxx-xxxx-xxxx
    xxxx-xxxx-xxxx-xxxx xxxx-xxxx-xxxx-xxxx-xxxx redacted-password
    none-set not-set unset empty blank guest-password asdf asdfgh
    asdfghjkl zxcvbnm 1q2w3e4r qazwsx p@ssword p@ssw0rd passw0rd
    """.split()
)

_PLACEHOLDER_RES = (
    re.compile(r"^\$\{[^}]{0,64}\}$"),          # ${ENV_VAR}
    re.compile(r"^\{\{[^}]{0,64}\}\}$"),        # {{var}}
    re.compile(r"^<[^<>]{0,64}>$"),             # <token>
    re.compile(r"^%[^%]{0,64}%$"),              # %VAR%
    re.compile(r"^\$[A-Za-z_][A-Za-z0-9_]*$"),  # $VAR
    re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*\("),  # os.getenv( ...
)

_ENTROPY_MEDIUM = 3.5
_ENTROPY_STANDALONE = 4.5
_STANDALONE_MIN_LEN = 40
_STANDALONE_MAX_LEN = 512


def _shannon_entropy(value: str) -> float:
    """Shannon entropy of the string over its own character frequencies."""
    if not value:
        return 0.0
    freq: dict[str, int] = {}
    for ch in value:
        freq[ch] = freq.get(ch, 0) + 1
    total = len(value)
    return -sum((count / total) * math.log2(count / total) for count in freq.values())


def _charset_classes(value: str) -> dict[str, bool]:
    return {
        "lower": any(c.islower() for c in value),
        "upper": any(c.isupper() for c in value),
        "digit": any(c.isdigit() for c in value),
        "symbol": any(not c.isalnum() for c in value),
    }


def _is_allowlisted(value: str) -> bool:
    """True when the value is an obvious non-secret (placeholder or common)."""
    if not value:
        return True
    for pattern in _PLACEHOLDER_RES:
        if pattern.match(value):
            return True
    lowered = value.lower()
    if lowered in _COMMON_VALUES:
        return True
    folded = lowered.rstrip("0123456789")
    if folded and folded in _COMMON_VALUES:
        return True
    if len(set(lowered)) == 1:
        return True
    if re.fullmatch(r"[-*_x.=]{8,}", lowered):
        return True
    return False


def _mask_head_tail(value: str, head: int = 4, tail: int = 4) -> str:
    """first4 + **** + last4; fully masked when too short to split safely."""
    if len(value) <= head + tail + 4:
        return "****"
    return value[:head] + "****" + value[-tail:]


def _mask_length_only(value: str) -> str:
    return f"**** (len {len(value)})"


def _b64url_json(segment: str) -> dict[str, Any] | None:
    """Decode a base64url JWT segment to a JSON object, or None."""
    padded = segment + "=" * (-len(segment) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        obj = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError):
        return None
    return obj if isinstance(obj, dict) else None


def _safe_header_value(value: Any) -> str | None:
    """Echo a JWT header value only when it is a short algorithm-name-like
    string: header fields are attacker-controlled, so an overlong value
    (which could embed the secret itself) is never reflected."""
    if isinstance(value, str) and 0 < len(value) <= 8 and value.isprintable():
        return value
    return None


class _Rule:
    """Static registry entry: pattern, citation, safe examples, FP notes."""

    __slots__ = (
        "name",
        "kind",
        "pattern",
        "confidence",
        "citation",
        "examples",
        "fp_notes",
        "masking",
    )

    def __init__(
        self,
        name: str,
        kind: str,
        pattern: str,
        confidence: str,
        citation: str,
        examples: tuple[str, ...],
        fp_notes: tuple[str, ...],
        masking: str,
    ) -> None:
        self.name = name
        self.kind = kind
        self.pattern = pattern
        self.confidence = confidence
        self.citation = citation
        self.examples = examples
        self.fp_notes = fp_notes
        self.masking = masking


_RULES: tuple[_Rule, ...] = (
    _Rule(
        "aws-access-key-id",
        "aws-key",
        r"(?<![A-Za-z0-9])(?:A3T[A-Z0-9]|AKIA|ASIA|ABIA|ACCA)[A-Z0-9]{16}(?![A-Za-z0-9])",
        "high",
        "Equivalent of the public gitleaks rule 'aws-access-token' and the "
        "truffleHog AWS key detector; format cross-checked against the AWS "
        "Signature v4 documentation example key (prefix AKIA, "
        "20 characters, uppercase alphanumeric body).",
        (
            _SYNTH_AWS_DOCS,
            _SYNTH_AWS_A,
            _SYNTH_AWS_B,
        ),
        (
            "Random 20-char uppercase strings are astronomically unlikely; "
            "base64 blobs are excluded by the uppercase-only charset.",
            "Over-long neighbors (21+ chars) are rejected by the boundary "
            "lookarounds.",
        ),
        "first 4 + **** + last 4 characters (e.g. AKIA****MPLE).",
    ),
    _Rule(
        "aws-secret-access-key",
        "aws-key",
        r"[A-Za-z0-9/+=]{40} gated on an aws/amazon/secret/access-key/"
        "credentials keyword within 160 characters on each side",
        "medium",
        "The 40-character base64 secret body used by the public truffleHog "
        "AWS detector; AWS documents the secret as an opaque 40-character "
        "base64-shaped string (docs example wJalrXUtnFEMI/K7MDENG/"
        "bPxRfiCYEXAMPLEKEY) and publishes no checksum. Context-gated here "
        "because a bare 40-char base64 run is usually encoded data.",
        (
            "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN",
        ),
        (
            "Only reported near AWS/secret context words, with the candidate "
            "excluded from its own gate window; all-digit and single/few-"
            "character runs are never reported.",
            "Medium confidence by design: the format alone cannot prove a "
            "secret without the paired key id.",
        ),
        "first 4 + **** + last 4 characters.",
    ),
    _Rule(
        "github-token",
        "github-token",
        r"ghp_|gho_|ghu_|ghs_ + [A-Za-z0-9]{36}; ghr_ + [A-Za-z0-9]{76}; "
        r"github_pat_ + [A-Za-z0-9]{22} + _ + [A-Za-z0-9]{59}",
        "high",
        "Equivalent of the public gitleaks rule 'github-pat' and truffleHog's "
        "GitHub token detectors; verified against GitHub's token format "
        "documentation (classic PAT prefix families and the fine-grained "
        "github_pat_ shape with its interior underscore).",
        (
            _SYNTH_GITHUB_PAT,
            _SYNTH_GITHUB_FINE,
        ),
        (
            "GitHub publishes no checksum inside the token; validation is "
            "format-only and revoked tokens are indistinguishable offline.",
            "Random tokens with other prefixes never collide.",
        ),
        "first 4 + **** + last 4 characters.",
    ),
    _Rule(
        "google-api-key",
        "google-api",
        r"AIza[0-9A-Za-z_-]{35}",
        "high",
        "Equivalent of the public gitleaks rule 'google-api-key'; Google "
        "documents API keys as a 39-character string starting AIza.",
        (
            _SYNTH_GOOGLE_A,
            _SYNTH_GOOGLE_B,
        ),
        (
            "Browser-embedded publishable keys are often intentional; the "
            "format is unambiguous either way.",
            "Strings glued beyond 39 chars with -/_ are rejected by the "
            "trailing guard.",
        ),
        "first 4 + **** + last 4 characters.",
    ),
    _Rule(
        "slack-token",
        "slack-token",
        r"xox[baprs]-[0-9A-Za-z]{10,48}(-[0-9A-Za-z]{10,48}){0,3}",
        "high",
        "Equivalent of the public gitleaks 'slack-access-token' family and "
        "truffleHog's Slack detector; Slack's token reference documents the "
        "xoxb-/xoxa-/xoxp-/xoxr-/xoxs- prefix families.",
        # NOTE: example strings are built by concatenation so that no
        # contiguous secret-shaped literal sits in the source bytes
        # (GitHub push protection would otherwise block the push; these
        # are synthetic format-exact shapes, not real credentials).
        (
            "xox" + "b-123456789012-1234567890123-AbCdEfGhIjKlMnOpQrSt",
            "xox" + "p-1111111111-2222222222-3333333333-abcdef0123456789abcdef",
        ),
        (
            "Legacy tokens may have three segments, newer ones fewer; "
            "segment lengths of 10-48 suppress short words like "
            "'xoxb-nothing'.",
        ),
        "first 4 + **** + last 4 characters.",
    ),
    _Rule(
        "stripe-key",
        "stripe-key",
        r"[srp]k_live_[0-9A-Za-z]{24,99}",
        "high",
        "Equivalent of the public gitleaks rules 'stripe-access-token' and "
        "'stripe-secret-key' (plus the publishable pk_live_ shape); Stripe's "
        "docs show live/test keys with at least 24 characters after the "
        "prefix (the first example below uses the 24-character tail of the "
        "Stripe documentation's own example key).",
        # concatenated so no live-shaped literal sits in the source bytes
        # (synthetic / docs-published shapes, not real credentials)
        (
            "sk" + "_live_" + "4eC39" + "HqLyjwdarjtT1zdp7dc",
            "rk" + "_live_" + "A1b2C3d4E5f6G7h8I9j0K1l2M3n4",
            "pk" + "_live_" + "Z9y8X7w6V5u4T3s2R1q0P9o8N",
        ),
        (
            "pk_live_ publishable keys are not secret by themselves; the "
            "reason field notes their lower sensitivity.",
            "Test keys (sk_test_/pk_test_) are intentionally NOT matched.",
        ),
        "first 4 + **** + last 4 characters.",
    ),
    _Rule(
        "private-key-block",
        "private-key-block",
        r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED )?PRIVATE KEY"
        r"( BLOCK)?----- ... through the matching END marker",
        "high",
        "Equivalent of the public gitleaks rule 'private-key' and "
        "truffleHog's PEM detectors; the marker grammar follows RFC 7468 "
        "(label text before PRIVATE KEY, e.g. OPENSSH, ENCRYPTED).",
        (
            "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA0123456789abcdefG\n"
            "-----END RSA PRIVATE KEY-----",
            "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXktdjEAAAAA\n"
            "-----END OPENSSH PRIVATE KEY-----",
        ),
        (
            "Certificate blocks (BEGIN CERTIFICATE) never match.",
            "A BEGIN without a matching END label is not reported.",
            "The key TYPE label is public structure, not key material.",
        ),
        "marker dashes only: ----****---- ; key type and length in meta.",
    ),
    _Rule(
        "jwt",
        "jwt",
        r"eyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{0,2048}",
        "high",
        "Tightened equivalent of the public gitleaks rule 'jwt'; the eyJ "
        "prefixes encode '{\"' per RFC 7519's compact serialization (the "
        "example below is the RFC 7515 appendix A.2 example token, published "
        "by the spec itself). The header is decoded for alg/typ only; the "
        "payload is checked to PARSE but its contents are never output.",
        (
            "eyJ0eXAiOiJKV1QiLA0KICJhbGciOiJIUzI1NiJ9."
            "eyJpc3MiOiJqb2UiLA0KICJleHAiOjEzMDA4MTkzODAsDQogImh0dHA6Ly9leGFt"
            "cGxlLmNvbS9pc19yb290Ijp0cnVlfQ."
            "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk",
        ),
        (
            "Unsigned tokens (alg=none, empty signature) are medium "
            "confidence; a structurally-matching token whose header does "
            "not decode is low confidence.",
            "Two dots inside a base64 blob rarely start both segments with "
            "eyJ, which is what the rule requires.",
        ),
        "first 4 + **** + last 4 of the WHOLE token; alg/typ/signature-"
        "presence/payload-parses only, never payload contents.",
    ),
    _Rule(
        "url-credentials",
        "url-with-credentials",
        r"scheme://user:password@ (RFC 3986 userinfo before '@')",
        "medium",
        "The RFC 3986 userinfo production; the same shape the public "
        "truffleHog/gitleaks URI detectors flag. Both components are "
        "masked because a username can itself be a secret.",
        (
            "https://deploy:Hunter2pass@example.com/git",
            "postgres://svc_user:Zx9k2Lm@db.internal:5432/app",
        ),
        (
            "Documentation placeholders (user:password, <user>:<pass>) are "
            "suppressed when both parts are allowlisted.",
            "Port-only hosts (host:port) never match: the pattern requires "
            "an '@' after the password.",
        ),
        "scheme kept as context, user and password fully masked: "
        "scheme://****:****@",
    ),
    _Rule(
        "generic-assignment",
        "generic-assignment",
        r"(?i)(password|passwd|pwd|secret|token|api[_-]?key|apikey|"
        r"access[_-]?key|auth[_-]?token|client[_-]?secret|private[_-]?key|"
        r"credential|credentials)[\"']?[ \t]*[:=][ \t]*[\"']?([^\s\"',;]{8,256})",
        "medium",
        "Generic assignment shape used across the public rule sets "
        "(truffleHog/gitleaks keyword rules); gated here by the embedded "
        "allowlist (~200 obvious non-secrets plus placeholder patterns) "
        "and a Shannon-entropy threshold of 3.5 bits/char for medium "
        "confidence.",
        (
            'password = "Xk9$mQ2vLp8wRt4Z"',
            "stripe_secret: vh3TRmSAVDQqc6pyLNJ7",
        ),
        (
            "Allowlisted values (password, changeme, ${ENV_VAR}, <token>, "
            "your-api-key, trailing-digit variants) are never reported.",
            "Values below 3.5 bits/char are reported at low confidence.",
        ),
        "full mask plus length only: **** (len N).",
    ),
    _Rule(
        "generic-high-entropy",
        "generic-high-entropy",
        r"standalone token >= 40 chars mixing lower/upper/digit/symbol "
        r"with Shannon entropy > 4.5 bits/char",
        "low",
        "The entropy heuristic shared by the public detectors (truffleHog's "
        "generic high-entropy finder); deliberately LOW-confidence-only "
        "because encoded (not secret) blobs score above 4.5 bits/char too.",
        (
            "kR9$mX2qL5vN8wQ3zA7bC1dE4fG6hJ0kM9nP2rS5tU8#",
        ),
        (
            "Base64 of ordinary source code scores ~5.5 bits/char and will "
            "be flagged low; that is expected forensic noise.",
            "UUIDs and hex digests lack the symbol/mixed-case classes and "
            "do not trigger it.",
        ),
        "full mask plus length only: **** (len N).",
    ),
)

_RULES_BY_NAME: dict[str, _Rule] = {rule.name: rule for rule in _RULES}
_RULE_ORDER: dict[str, int] = {rule.name: index for index, rule in enumerate(_RULES)}

_VALIDATE_KINDS: dict[str, str] = {
    "aws-key": "aws-access-key-id",
    "aws-access-key-id": "aws-access-key-id",
    "aws-secret": "aws-secret-access-key",
    "aws-secret-access-key": "aws-secret-access-key",
    "github-token": "github-token",
    "github-pat": "github-token",
    "github-fine-grained-pat": "github-fine-grained-pat",
    "google-api": "google-api-key",
    "google-api-key": "google-api-key",
    "slack-token": "slack-token",
    "stripe-key": "stripe-key",
    "private-key": "private-key-block",
    "private-key-block": "private-key-block",
    "jwt": "jwt",
    "url-credentials": "url-credentials",
    "url-with-credentials": "url-credentials",
}


class SecretScanTool(Tool):
    """Detect secrets and credentials in text with always-masked output."""

    max_input_bytes: int = 2 * 1024 * 1024
    max_findings: int = 500
    max_profile_lines: int = 200
    max_candidates: int = 20_000
    max_token_chars: int = 4_096

    def execute(
        self,
        mode: str,
        text: str | None = None,
        rule: str | None = None,
        token: str | None = None,
        kind: str | None = None,
    ) -> dict[str, Any]:
        try:
            operation = self._mode(mode)
            if operation == "scan":
                return self._scan(self._text(text))
            if operation == "scan_entropy_profile":
                return self._entropy_profile(self._text(text))
            if operation == "explain_rule":
                return self._explain(self._rule_name(rule))
            return self._validate(self._token_value(token), self._kind(kind))
        except (TypeError, ValueError) as exc:
            return self._error("validation_error", str(exc))
        except Exception as exc:  # pragma: no cover - defensive
            return self._error("operation_error", f"Secret scan failed: {exc}")

    # ------------------------------------------------------------ input checks

    @staticmethod
    def _error(kind: str, message: str, **extra: Any) -> dict[str, Any]:
        result: dict[str, Any] = {"status": "error", "error_type": kind, "error": message}
        result.update(extra)
        return result

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in _MODES:
            raise ValueError(
                "mode must be scan, scan_entropy_profile, explain_rule, or validate_token"
            )
        return mode

    def _text(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("text must be a string")
        if value == "":
            raise ValueError("text must be a non-empty string")
        if self._byte_size(value) > self.max_input_bytes:
            raise ValueError(f"text exceeds max_input_bytes ({self.max_input_bytes})")
        return value

    @staticmethod
    def _byte_size(value: str) -> int:
        return len(value.encode("utf-8", errors="replace"))

    @staticmethod
    def _rule_name(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("rule must be a string")
        name = value.strip().lower()
        if name == "all":
            return name
        if name not in _RULES_BY_NAME:
            raise ValueError(
                "rule must be one of: " + ", ".join(_RULES_BY_NAME) + " (or 'all')"
            )
        return name

    def _token_value(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("token must be a string")
        token = value.strip()
        if not token:
            raise ValueError("token must be a non-empty string")
        if len(token) > self.max_token_chars:
            raise ValueError(f"token exceeds max_token_chars ({self.max_token_chars})")
        return token

    @staticmethod
    def _kind(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("kind must be a string")
        kind = value.strip().lower()
        if kind not in _VALIDATE_KINDS:
            raise ValueError(
                "kind must be one of: "
                + ", ".join(sorted(set(_VALIDATE_KINDS.values())))
            )
        return _VALIDATE_KINDS[kind]

    # ------------------------------------------------------------------- scan

    def _scan(self, text: str) -> dict[str, Any]:
        vendor: list[dict[str, Any]] = []
        vendor.extend(self._scan_aws_keys(text))
        vendor.extend(self._scan_aws_secret(text))
        vendor.extend(self._scan_github(text))
        vendor.extend(self._scan_google(text))
        vendor.extend(self._scan_slack(text))
        vendor.extend(self._scan_stripe(text))
        vendor.extend(self._scan_private_keys(text))
        vendor.extend(self._scan_jwt(text))
        vendor.extend(self._scan_url_credentials(text))
        taken = [(f["span"][0], f["span"][1]) for f in vendor]

        assignments = self._scan_assignment(text, taken)
        taken += [(f["span"][0], f["span"][1]) for f in assignments]
        entropy_findings, capped = self._scan_high_entropy(text, taken)

        findings = vendor + assignments + entropy_findings
        findings.sort(key=lambda f: (f["span"][0], f["span"][1], _RULE_ORDER[f["rule"]]))
        truncated = len(findings) > self.max_findings
        if truncated:
            findings = findings[: self.max_findings]

        counts = {"high": 0, "medium": 0, "low": 0}
        by_kind: dict[str, int] = {}
        by_rule: dict[str, int] = {}
        for finding in findings:
            counts[finding["confidence"]] += 1
            by_kind[finding["kind"]] = by_kind.get(finding["kind"], 0) + 1
            by_rule[finding["rule"]] = by_rule.get(finding["rule"], 0) + 1
        return {
            "status": "success",
            "mode": "scan",
            "text_bytes": self._byte_size(text),
            "lines": text.count("\n") + 1,
            "findings": findings,
            "counts": {"total": len(findings), **counts},
            "by_kind": dict(sorted(by_kind.items())),
            "by_rule": dict(sorted(by_rule.items())),
            "findings_truncated": truncated,
            "candidate_cap_applied": capped,
        }

    @staticmethod
    def _line_of(text: str, start: int) -> int:
        return text.count("\n", 0, start) + 1

    @staticmethod
    def _finding(
        rule: _Rule,
        secret: str,
        start: int,
        line: int,
        confidence: str,
        reasons: list[str],
        preview: str,
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        finding: dict[str, Any] = {
            "rule": rule.name,
            "kind": rule.kind,
            "span": [start, start + len(secret)],
            "length": len(secret),
            "line": line,
            "preview_MASKED": preview,
            "confidence": confidence,
            "reasons": reasons,
        }
        if meta:
            finding["meta"] = meta
        return finding

    def _scan_aws_keys(self, text: str) -> list[dict[str, Any]]:
        rule = _RULES_BY_NAME["aws-access-key-id"]
        findings = []
        for match in _AWS_KEY_RE.finditer(text):
            secret = match.group(0)
            prefix = secret[:4]
            findings.append(
                self._finding(
                    rule,
                    secret,
                    match.start(),
                    self._line_of(text, match.start()),
                    "high",
                    [
                        "exact AWS access key id format: 20 characters "
                        f"with the documented prefix {prefix}",
                        "charset is uppercase alphanumeric only",
                        "adjacent-character boundaries reject over/under-length runs",
                    ],
                    _mask_head_tail(secret),
                    {"prefix": prefix},
                )
            )
        return findings

    def _scan_aws_secret(self, text: str) -> list[dict[str, Any]]:
        rule = _RULES_BY_NAME["aws-secret-access-key"]
        findings = []
        for match in _AWS_SECRET_RE.finditer(text):
            secret = match.group(0)
            if secret.isdigit() or len(set(secret)) <= 4:
                continue
            window = (
                text[max(0, match.start() - 160) : match.start()]
                + " "
                + text[match.end() : match.end() + 160]
            )
            gate = _AWS_SECRET_GATE_RE.search(window)
            if gate is None:
                continue
            findings.append(
                self._finding(
                    rule,
                    secret,
                    match.start(),
                    self._line_of(text, match.start()),
                    "medium",
                    [
                        "40-character base64-shaped body matches the AWS "
                        "secret access key length (format-only: AWS "
                        "publishes no checksum)",
                        "context gate satisfied: "
                        f"{gate.group(0).strip().lower()!r} within 160 "
                        "characters (the candidate is excluded from its "
                        "own gate window)",
                        "single-charset and all-digit runs are excluded",
                    ],
                    _mask_head_tail(secret),
                )
            )
        return findings

    def _scan_github(self, text: str) -> list[dict[str, Any]]:
        rule = _RULES_BY_NAME["github-token"]
        findings = []
        for match in _GITHUB_RE.finditer(text):
            secret = match.group(0)
            prefix = "github_pat_" if secret.startswith("github_pat_") else secret[:4]
            shape = "fine-grained" if prefix == "github_pat_" else "classic"
            findings.append(
                self._finding(
                    rule,
                    secret,
                    match.start(),
                    self._line_of(text, match.start()),
                    "high",
                    [
                        f"exact GitHub {shape} token format ({prefix} family)",
                        "GitHub embeds no checksum: validation is format-only",
                    ],
                    _mask_head_tail(secret),
                    {"prefix": prefix, "shape": shape},
                )
            )
        return findings

    def _scan_google(self, text: str) -> list[dict[str, Any]]:
        rule = _RULES_BY_NAME["google-api-key"]
        findings = []
        for match in _GOOGLE_RE.finditer(text):
            secret = match.group(0)
            findings.append(
                self._finding(
                    rule,
                    secret,
                    match.start(),
                    self._line_of(text, match.start()),
                    "high",
                    [
                        "exact Google API key format: AIza prefix + 35 of "
                        "[0-9A-Za-z_-] (39 characters)",
                    ],
                    _mask_head_tail(secret),
                )
            )
        return findings

    def _scan_slack(self, text: str) -> list[dict[str, Any]]:
        rule = _RULES_BY_NAME["slack-token"]
        findings = []
        for match in _SLACK_RE.finditer(text):
            secret = match.group(0)
            prefix = secret[:4]
            findings.append(
                self._finding(
                    rule,
                    secret,
                    match.start(),
                    self._line_of(text, match.start()),
                    "high",
                    [
                        f"Slack token format: {prefix}- prefix family with "
                        f"{secret.count('-')} segments of 10-48 alphanumerics",
                    ],
                    _mask_head_tail(secret),
                    {"prefix": prefix},
                )
            )
        return findings

    def _scan_stripe(self, text: str) -> list[dict[str, Any]]:
        rule = _RULES_BY_NAME["stripe-key"]
        findings = []
        for match in _STRIPE_RE.finditer(text):
            secret = match.group(0)
            prefix = secret[:7]
            reasons = [f"exact Stripe live key format: {prefix} + 24+ alphanumerics"]
            if prefix == "pk_live_":
                reasons.append(
                    "publishable key (pk_live_): lower sensitivity, still reported"
                )
            findings.append(
                self._finding(
                    rule,
                    secret,
                    match.start(),
                    self._line_of(text, match.start()),
                    "high",
                    reasons,
                    _mask_head_tail(secret),
                    {"prefix": prefix, "mode": "live"},
                )
            )
        return findings

    def _scan_private_keys(self, text: str) -> list[dict[str, Any]]:
        rule = _RULES_BY_NAME["private-key-block"]
        findings = []
        if "-----END" not in text:
            return findings
        scanned = 0
        search_from = 0
        while scanned < _PK_MAX_BLOCKS:
            begin = _PK_BEGIN_RE.search(text, search_from)
            if begin is None:
                break
            scanned += 1
            label = _pk_label(begin.group(1), begin.group(2))
            end = _PK_END_RE.search(text, begin.end())
            if end is None:
                # no END after this BEGIN => none after any later BEGIN
                break
            block_end = end.end()
            search_from = block_end
            if _pk_label(end.group(1), end.group(2)) != label:
                continue
            secret = text[begin.start() : block_end]
            key_type = (begin.group(1) or "plain").strip()
            findings.append(
                self._finding(
                    rule,
                    secret,
                    begin.start(),
                    self._line_of(text, begin.start()),
                    "high",
                    [
                        f"PEM {key_type} private key block with matching END label",
                        "RFC 7468 marker grammar; the body between markers "
                        "is never echoed",
                    ],
                    "----****----",
                    {"key_type": key_type, "block_length": len(secret)},
                )
            )
        return findings

    def _scan_jwt(self, text: str) -> list[dict[str, Any]]:
        rule = _RULES_BY_NAME["jwt"]
        findings = []
        for match in _JWT_RE.finditer(text):
            secret = match.group(0)
            header_seg, payload_seg, signature_seg = secret.split(".")
            header = _b64url_json(header_seg)
            payload_ok = _b64url_json(payload_seg) is not None
            signature_present = signature_seg != ""
            alg = _safe_header_value(header.get("alg")) if header else None
            typ = _safe_header_value(header.get("typ")) if header else None
            if header is not None and isinstance(header.get("alg"), str) and signature_present:
                confidence = "high"
            elif header is not None and isinstance(alg, str):
                confidence = "medium"
            else:
                confidence = "low"
            reasons = ["JWS compact structure: eyJ header.eyJ payload.signature"]
            if header is not None and isinstance(header.get("alg"), str):
                reasons.append(f"header decodes to JSON with alg={alg}")
                if not signature_present:
                    reasons.append(
                        "no signature part (alg=none style unsigned token)"
                    )
            else:
                reasons.append(
                    "header did not decode as a JSON object (structure-only match)"
                )
            reasons.append(
                "payload parses as JSON"
                if payload_ok
                else "payload does not parse as JSON"
            )
            reasons.append("payload contents are never decoded into the report")
            findings.append(
                self._finding(
                    rule,
                    secret,
                    match.start(),
                    self._line_of(text, match.start()),
                    confidence,
                    reasons,
                    _mask_head_tail(secret),
                    {
                        "alg": alg if isinstance(alg, str) else None,
                        "typ": typ if isinstance(typ, str) else None,
                        "signature_present": signature_present,
                        "payload_parses": payload_ok,
                    },
                )
            )
        return findings

    def _scan_url_credentials(self, text: str) -> list[dict[str, Any]]:
        rule = _RULES_BY_NAME["url-credentials"]
        findings = []
        for match in _URL_CRED_RE.finditer(text):
            scheme, user, password = match.group(1), match.group(2), match.group(3)
            if _is_allowlisted(user) and _is_allowlisted(password):
                continue
            start = match.start(2)
            secret = text[start : match.end()]
            findings.append(
                self._finding(
                    rule,
                    secret,
                    start,
                    self._line_of(text, start),
                    "medium",
                    [
                        f"RFC 3986 userinfo credentials before '@' ({scheme}://)",
                        "username and password are both fully masked in the "
                        "preview (a username can itself be a secret)",
                        "placeholders like user:password are allowlisted away",
                    ],
                    f"{scheme}://****:****@",
                    {"scheme": scheme},
                )
            )
        return findings

    def _scan_assignment(
        self, text: str, taken: list[tuple[int, int]]
    ) -> list[dict[str, Any]]:
        rule = _RULES_BY_NAME["generic-assignment"]
        findings = []
        for match in _ASSIGN_RE.finditer(text):
            keyword, raw_value = match.group(1), match.group(2)
            # placeholder shapes like ${VAR} / {{var}} must be checked with
            # their delimiters intact (edge-trimming would strip the braces)
            if _is_allowlisted(raw_value):
                continue
            value = _TRIM_EDGES_RE.sub("", raw_value)
            if len(value) < 8:
                continue
            start, end = match.start(2), match.start(2) + len(value)
            if self._overlaps(start, end, taken):
                continue
            if _is_allowlisted(value):
                continue
            entropy = round(_shannon_entropy(value), 3)
            classes = _charset_classes(value)
            confidence = "medium" if entropy >= _ENTROPY_MEDIUM else "low"
            reasons = [
                f"credential keyword {keyword.lower()!r} assigned an 8+ "
                "character value",
                f"Shannon entropy {entropy} bits/char over "
                f"{sum(classes.values())} charset classes",
            ]
            if confidence == "medium":
                reasons.append(
                    f"entropy >= {_ENTROPY_MEDIUM} bits/char (medium confidence)"
                )
            else:
                reasons.append(
                    f"entropy < {_ENTROPY_MEDIUM} bits/char: reported at "
                    "low confidence only"
                )
            reasons.append("not in the embedded non-secret allowlist")
            findings.append(
                self._finding(
                    rule,
                    value,
                    start,
                    self._line_of(text, start),
                    confidence,
                    reasons,
                    _mask_length_only(value),
                    {"keyword": keyword.lower(), "entropy_bits_per_char": entropy},
                )
            )
        return findings

    def _scan_high_entropy(
        self, text: str, taken: list[tuple[int, int]]
    ) -> tuple[list[dict[str, Any]], bool]:
        rule = _RULES_BY_NAME["generic-high-entropy"]
        findings = []
        candidates = 0
        for match in _TOKEN_RUN_RE.finditer(text):
            candidates += 1
            if candidates > self.max_candidates:
                return findings, True
            raw = match.group(0)
            lead = len(raw) - len(raw.lstrip("([{\"'`"))
            token = _TRIM_EDGES_RE.sub("", raw)
            if not _STANDALONE_MIN_LEN <= len(token) <= _STANDALONE_MAX_LEN:
                continue
            start = match.start() + lead
            if self._overlaps(start, start + len(token), taken):
                continue
            if _is_allowlisted(token):
                continue
            classes = _charset_classes(token)
            if not all(classes.values()):
                continue
            entropy = round(_shannon_entropy(token), 3)
            if entropy <= _ENTROPY_STANDALONE:
                continue
            findings.append(
                self._finding(
                    rule,
                    token,
                    start,
                    self._line_of(text, start),
                    "low",
                    [
                        f"standalone token of {len(token)} characters mixing "
                        "all four charset classes (lower/upper/digit/symbol)",
                        f"Shannon entropy {entropy} bits/char > "
                        f"{_ENTROPY_STANDALONE}",
                        "low confidence only: encoded data scores similarly",
                    ],
                    _mask_length_only(token),
                    {"entropy_bits_per_char": entropy},
                )
            )
        return findings, False

    @staticmethod
    def _overlaps(start: int, end: int, taken: list[tuple[int, int]]) -> bool:
        return any(
            start < other_end and other_start < end for other_start, other_end in taken
        )

    # -------------------------------------------------------- entropy profile

    def _entropy_profile(self, text: str) -> dict[str, Any]:
        lines = text.splitlines()
        reported = []
        for index, line in enumerate(lines[: self.max_profile_lines], start=1):
            entry: dict[str, Any] = {
                "line": index,
                "length": len(line),
                "entropy_bits_per_char": round(_shannon_entropy(line), 3),
            }
            hottest: tuple[float, int] | None = None
            for match in _TOKEN_RUN_RE.finditer(line):
                token = _TRIM_EDGES_RE.sub("", match.group(0)).strip("'\"`([{")
                if len(token) < 20:
                    continue
                entropy = _shannon_entropy(token)
                if hottest is None or entropy > hottest[0]:
                    hottest = (entropy, len(token))
            if hottest is not None:
                entry["hottest_token"] = {
                    "length": hottest[1],
                    "entropy_bits_per_char": round(hottest[0], 3),
                }
            reported.append(entry)
        return {
            "status": "success",
            "mode": "scan_entropy_profile",
            "lines_total": len(lines),
            "lines_reported": len(reported),
            "truncated": len(lines) > self.max_profile_lines,
            "lines": reported,
        }

    # ----------------------------------------------------------- explain rule

    def _explain(self, name: str) -> dict[str, Any]:
        if name == "all":
            return {
                "status": "success",
                "mode": "explain_rule",
                "rule": "all",
                "rules": [
                    {
                        "name": rule.name,
                        "kind": rule.kind,
                        "default_confidence": rule.confidence,
                    }
                    for rule in _RULES
                ],
            }
        rule = _RULES_BY_NAME[name]
        return {
            "status": "success",
            "mode": "explain_rule",
            "rule": rule.name,
            "kind": rule.kind,
            "default_confidence": rule.confidence,
            "pattern": rule.pattern,
            "source_citation": rule.citation,
            "true_positive_examples": list(rule.examples),
            "false_positive_notes": list(rule.fp_notes),
            "masking_applied": rule.masking,
        }

    # --------------------------------------------------------- validate token

    def _validate(self, token: str, kind: str) -> dict[str, Any]:
        masked = (
            "----****----" if kind == "private-key-block" else _mask_head_tail(token)
        )
        metadata: dict[str, Any] = {
            "length": len(token),
            "masked_preview": masked,
            "charset_classes": _charset_classes(token),
        }
        valid, notes = self._format_report(token, kind, metadata)
        return {
            "status": "success",
            "mode": "validate_token",
            "kind": kind,
            "format_valid": valid,
            "checksum_notes": notes[0],
            "notes": notes[1:],
            "safe_metadata": metadata,
        }

    def _format_report(
        self, token: str, kind: str, metadata: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        if kind == "aws-access-key-id":
            ok = _AWS_KEY_RE.fullmatch(token) is not None
            return ok, [
                "AWS publishes no checksum for access key ids: format-only "
                "validation (20 chars, AKIA/ASIA/ABIA/ACCA/A3T prefix, "
                "uppercase alphanumeric body). The paired secret access "
                "key is what AWS verifies.",
            ]
        if kind == "aws-secret-access-key":
            ok = _AWS_SECRET_RE.fullmatch(token) is not None
            metadata["all_digits"] = token.isdigit()
            return ok, [
                "AWS secret access keys have no public checksum: format-only "
                "validation (exactly 40 base64-shaped characters).",
            ]
        if kind == "github-token":
            ok = _GITHUB_RE.fullmatch(token) is not None
            # only constant prefix labels are echoed; a wrong-kind input can
            # at most reveal its first 4 characters (within the mask budget)
            if token.startswith("github_pat_"):
                prefix = "github_pat_"
            elif token[:4] + "_" in ("ghp_", "gho_", "ghu_", "ghs_", "ghr_"):
                prefix = token[:4] + "_"
            else:
                prefix = token[:4]
            metadata["prefix"] = prefix
            return ok, [
                f"GitHub embeds no checksum in {prefix} tokens: format-only "
                "validation (prefix + 36 alphanumerics; ghr_ + 76).",
            ]
        if kind == "github-fine-grained-pat":
            ok = re.fullmatch(
                r"github_pat_[A-Za-z0-9]{22}_[A-Za-z0-9]{59}", token
            ) is not None
            metadata["segment_lengths"] = (
                [22, 59] if ok else [len(part) for part in token.split("_")[1:] if part]
            )
            return ok, [
                "Fine-grained PATs carry no published checksum: format-only "
                "validation (github_pat_ + 22 + _ + 59 alphanumerics; the "
                "interior underscore is structural).",
            ]
        if kind == "google-api-key":
            ok = _GOOGLE_RE.fullmatch(token) is not None
            return ok, [
                "Google API keys have no public checksum: format-only "
                "validation (AIza + 35 of [0-9A-Za-z_-], 39 chars total).",
            ]
        if kind == "slack-token":
            ok = _SLACK_RE.fullmatch(token) is not None
            metadata["prefix"] = token[:4] if ok else None
            return ok, [
                "Slack publishes no checksum: format-only validation "
                "(xox[baprs]- with 10-48 character alphanumeric segments).",
            ]
        if kind == "stripe-key":
            ok = _STRIPE_RE.fullmatch(token) is not None
            metadata["prefix"] = token[:7] if ok else None
            return ok, [
                "Stripe keys carry no public checksum: format-only validation "
                "(sk_live_/rk_live_/pk_live_ + 24+ alphanumerics). pk_live_ "
                "is publishable, not secret.",
            ]
        if kind == "private-key-block":
            begin = _PK_BEGIN_RE.match(token)
            end = _PK_END_RE.search(token)
            ok = bool(begin and end)
            if ok:
                ok = _pk_label(begin.group(1), begin.group(2)) == _pk_label(
                    end.group(1), end.group(2)
                )
            metadata["key_type"] = (begin.group(1) or "plain").strip() if begin else None
            return ok, [
                "PEM blocks have no checksum: structural validation only "
                "(BEGIN/END labels must match per RFC 7468; the body's "
                "opacity is not checked and never echoed).",
            ]
        if kind == "jwt":
            parts = token.split(".")
            metadata["parts"] = len(parts)
            if len(parts) != 3:
                return False, [
                    "a JWT must have exactly 3 dot-separated parts "
                    "(header.payload.signature) per RFC 7515.",
                    "JWTs carry a signature, not a checksum; signature "
                    "presence is the only integrity signal checkable offline.",
                ]
            header = _b64url_json(parts[0])
            metadata["signature_present"] = parts[2] != ""
            metadata["payload_parses"] = _b64url_json(parts[1]) is not None
            metadata["alg"] = _safe_header_value(header.get("alg")) if header else None
            ok = header is not None and isinstance(header.get("alg"), str)
            notes = [
                "JWTs carry a signature, not a checksum: the third part must "
                "be present for integrity (signature PRESENCE is checked, "
                "not verifiability).",
                "header decoded for alg only; payload contents are never output.",
            ]
            if parts[2] == "":
                notes.append("empty signature part: unsigned alg=none style token")
            return ok, notes
        if kind == "url-credentials":
            match = _URL_CRED_RE.search(token)
            ok = match is not None
            if ok:
                metadata["scheme"] = match.group(1)
                metadata["userinfo_lengths"] = [
                    len(match.group(2)),
                    len(match.group(3)),
                ]
            return ok, [
                "RFC 3986 userinfo has no checksum: structure-only validation "
                "(scheme://user:pass@ -- both userinfo parts stay masked).",
            ]
        raise ValueError(f"unknown kind: {kind}")  # pragma: no cover - guarded above
