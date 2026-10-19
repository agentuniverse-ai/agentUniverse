#!/usr/bin/env python3

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: domain_validator_tool.py

"""Domain (hostname / TLD) inspection tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency domain inspector an
agent can call before dialing, caching or ranking a host. It complements
URL *structure* parsing with hostname *semantics*: it does not split
schemes, paths or query strings — it validates and explains the host
name itself.

Three modes are supported:

* ``validate`` — run the RFC 1035/1034 oriented hostname checks against
  one hostname and return a verdict with the full list of reasons:

  - overall length at most 253 characters (the DNS wire limit, boundary
    tested on both sides);
  - every label between 1 and 63 characters;
  - labels only contain ASCII letters, digits and hyphens (the LDH
    rule). Underscores are rejected by default; with
    ``allow_underscores=True`` they are accepted leniently and reported
    as a warning instead of an error, because many internal hostnames
    (e.g. SRV-style ``_sip._tcp`` names) carry them even though they are
    not RFC-compliant hostnames;
  - no leading or trailing hyphen in any label;
  - no empty label (double dot, leading dot);
  - at least one dot — a single-label name such as ``localhost`` is only
    accepted with ``allow_single_label=True`` (downgraded to a warning).
    A single-label name that *carries* the trailing root dot
    (``localhost.``) is already explicitly fully qualified per RFC 1035,
    so it passes without the flag;
  - the top-level label is alphabetic and at least two characters long
    (so ``example.123`` and ``example.c`` are rejected).

  IP literals (``192.168.1.1``, ``::1``) are detected first and routed
  to a dedicated ``ip_literal`` verdict that notes the input is an IP
  address, not a domain name, instead of pouring them through the label
  rules.
* ``info`` — describe one hostname: registered-domain guess (last two
  labels), TLD (last label), subdomain count, label count, and
  punycode/IDNA conversion in both directions using the stdlib
  ``encodings.idna`` codec — an ``xn--`` label is decoded to its Unicode
  form, and a non-ASCII hostname is encoded to its ACE form, with any
  ``UnicodeError`` caught and reported instead of raised.
* ``tld_lookup`` — classify a TLD (given bare, or extracted as the last
  label of a hostname) against a built-in table of ~120 well-known
  TLDs: the classic generic TLDs (com/org/net/...), a broad set of
  country codes (cn/us/uk/jp/...), and popular new gTLDs
  (xyz/online/site/...). The verdict is ``known``/``unknown`` with the
  category ``generic``/``country``/``new_gtld``. The table is indicative
  and deliberately NOT exhaustive — an ``unknown`` verdict means "not in
  the built-in list", never "not delegated".

Input validation is strict and happens before any computation: a wrong
``mode``, a non-string or empty ``hostname``, non-boolean flag options,
whitespace, or input that still carries URL syntax (``scheme://``,
``/path``, ``?query``, ``#fragment``, ``@`` or a ``host:port`` colon)
raises a ``ValueError`` with a hint to pass only the host part. A
single trailing dot (the fully-qualified root form) is stripped and
reported back via ``trailing_dot_stripped`` instead of being treated as
an empty label. Hostnames are case-insensitive, so input is normalized
to lowercase first (this also makes the stdlib IDNA codec accept
uppercase ``XN--`` labels). Errors that depend on the *content being
inspected* (an invalid punycode label, a label that grows past 63 bytes
when converted to ACE) are returned as structured notes inside the
result so an agent can react without catching exceptions.
"""

import encodings.idna  # noqa: F401  — registers the 'idna' codec
import ipaddress
import re
from typing import Any, ClassVar

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# LDH rule: ASCII letters, digits, hyphen.
_LDH_LABEL = re.compile(r"\A[a-z0-9-]+\Z")
_ALPHABETIC = re.compile(r"\A[a-z]+\Z")

# Well-known classic generic TLDs.
GENERIC_TLDS: tuple = (
    "com", "org", "net", "edu", "gov",
    "io", "ai", "dev", "app", "co", "me", "info", "biz",
)
# Popular new gTLDs.
NEW_GTLDS: tuple = ("xyz", "online", "site", "shop", "top", "tech", "cloud")
# A broad (not exhaustive) set of country-code TLDs. ``uk`` is the
# widely used exceptional reservation of GB, ``eu`` is included as a
# ccTLD-style code.
COUNTRY_CODE_TLDS: tuple = (
    "ae", "ar", "at", "au", "ba", "be", "bg", "bh", "br", "by",
    "ca", "ch", "cl", "cn", "cr", "cy", "cz", "de", "dk", "dz",
    "ec", "ee", "eg", "es", "et", "fi", "fr", "gb", "ge", "gh",
    "gr", "hk", "hn", "hr", "hu", "id", "ie", "il", "in", "iq",
    "is", "it", "jo", "jp", "ke", "kr", "kw", "kz", "la", "lb",
    "li", "lt", "lu", "lv", "ma", "md", "mg", "mk", "mn", "mt",
    "mu", "mx", "my", "ng", "ni", "nl", "no", "nz", "om", "pa",
    "pe", "ph", "pk", "pl", "pt", "py", "qa", "ro", "rs", "ru",
    "sa", "se", "sg", "si", "sk", "th", "tn", "tr", "tw", "ua",
    "uk", "us", "uy", "uz", "ve", "vn", "ye", "za", "zw", "eu",
)

_TLD_NOTE = (
    "Known-TLD table is indicative (about 120 common entries) and NOT "
    "exhaustive; 'unknown' means 'not in the built-in list', not 'not "
    "delegated'."
)

MAX_HOSTNAME_CHARS = 2048
MAX_DNS_NAME_CHARS = 253
MAX_LABEL_CHARS = 63


def _build_tld_table() -> dict:
    table: dict[str, str] = {}
    for tld in GENERIC_TLDS:
        table[tld] = "generic"
    for tld in COUNTRY_CODE_TLDS:
        table[tld] = "country"
    for tld in NEW_GTLDS:
        table[tld] = "new_gtld"
    return table


class DomainValidatorTool(Tool):
    """Hostname / TLD inspection tool built purely on the stdlib.

    Attributes:
        max_hostname_chars (int): Upper bound on the ``hostname`` input
            length; longer inputs are rejected before any work. The DNS
            253-character limit is a validation *finding*, not a
            parameter error, and is reported by the ``validate`` mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "domain_validator_tool"
    description: str = (
        "Domain validator tool — pure Python stdlib, no network "
        "required. Validates a hostname against RFC-style rules "
        "(mode='validate': length <=253, labels 1-63 LDH charset, no "
        "leading/trailing hyphen, no empty label, dot required for "
        "FQDN, alphabetic TLD >=2 chars; IP literals get a dedicated "
        "ip_literal verdict), describes a hostname with a "
        "registered-domain guess, TLD, subdomain count and stdlib "
        "punycode/IDNA conversion in both directions (mode='info'), "
        "and classifies a TLD as known/unknown with category "
        "generic/country/new-gtld against a built-in indicative table "
        "(mode='tld_lookup')."
    )

    MODES: ClassVar[tuple] = ("validate", "info", "tld_lookup")
    KNOWN_TLDS: ClassVar[dict[str, str]] = _build_tld_table()

    max_hostname_chars: int = MAX_HOSTNAME_CHARS

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        hostname: Any = None,
        allow_single_label: Any = None,
        allow_underscores: Any = None,
    ) -> dict[str, Any]:
        """Run one domain inspection.

        Args:
            mode (str): One of ``validate`` / ``info`` / ``tld_lookup``.
            hostname (str): The host name to inspect. For ``validate``
                and ``info`` this must be the bare host (no scheme, no
                path, no port); a single trailing root dot is stripped
                and reported. For ``tld_lookup`` either a bare TLD
                (``com``) or a hostname whose last label is used.
            allow_single_label (bool): Validate mode only — accept
                single-label hostnames such as ``localhost`` with a
                warning instead of rejecting them. Defaults to False.
            allow_underscores (bool): Validate mode only — accept
                underscores in labels leniently (warning instead of
                error). Defaults to False.

        Returns:
            Dict[str, Any]: The inspection result. ``validate`` returns
            a ``verdict`` (``valid`` / ``invalid`` / ``ip_literal``)
            with ``reasons`` (errors) and ``warnings``; ``info`` returns
            the registered-domain guess, TLD, subdomain count and a
            punycode block; ``tld_lookup`` returns the known/unknown
            verdict and category. Content-level failures (invalid
            punycode) are reported inside the result, not raised.

        Raises:
            ValueError: If any parameter is malformed — unknown mode,
                non-string or empty hostname, URL syntax (scheme, path,
                query, fragment, userinfo, port) passed instead of a
                bare host, embedded whitespace, non-boolean flag
                options, or oversized input.
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_single = self._validate_flag(
            allow_single_label, "allow_single_label"
        )
        clean_underscores = self._validate_flag(
            allow_underscores, "allow_underscores"
        )
        clean_host = self._normalize_hostname(hostname)

        if mode == "tld_lookup":
            return self._run_tld_lookup(clean_host)
        if mode == "info":
            return self._run_info(clean_host)
        return self._run_validate(
            clean_host, allow_single_label=clean_single,
            allow_underscores=clean_underscores,
        )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"domain_validator_tool: {message}")

    @classmethod
    def _validate_flag(cls, value: Any, name: str) -> bool:
        """Validate a boolean option (None means the default, False)."""
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        cls._invalid(f"{name} must be a boolean or None (got {value!r})")

    @classmethod
    def _normalize_hostname(cls, hostname: Any) -> str:
        """Validate raw input syntax and normalize it.

        Rejects URL syntax (scheme, path, query, fragment, userinfo,
        port) with a hint, rejects embedded whitespace, strips and
        reports a single trailing root dot (the caller reads the flag
        from the returned context), lowercases the rest (DNS names are
        case-insensitive) and enforces the sanity size cap.
        """
        if (
            hostname is None
            or isinstance(hostname, bool)
            or not isinstance(hostname, str)
        ):
            cls._invalid(f"hostname must be a non-empty string (got {hostname!r})")
        if not hostname:
            cls._invalid("hostname must be a non-empty string (got '')")
        if len(hostname) > MAX_HOSTNAME_CHARS:
            cls._invalid(
                f"hostname exceeds the {MAX_HOSTNAME_CHARS:,}-character "
                f"limit (got {len(hostname):,} characters)"
            )
        for char in hostname:
            if char.isspace():
                cls._invalid(
                    "hostname must not contain whitespace — pass only "
                    f"the host part (got {hostname[:64]!r})"
                )
        if "://" in hostname:
            cls._invalid(
                "hostname must be the bare host without the scheme — pass "
                f"'{hostname.split('://', 1)[1].split('/', 1)[0].lower()}' "
                f"instead of '{hostname[:64]}' (strip 'scheme://', or use a "
                "URL parser first)"
            )
        for char in "/?#@":
            if char in hostname:
                cls._invalid(
                    f"hostname contains {char!r} — this looks like a URL "
                    "path/query/fragment or userinfo, not a host name; "
                    "pass only the host part"
                )
        # A colon means host:port or a raw IPv6 literal. Raw IPv6 is
        # routed to the ip_literal verdict, so keep it through the
        # ipaddress probe below; anything else with a colon is rejected.
        if ":" in hostname and not cls._parse_ip(hostname):
            cls._invalid(
                "hostname contains ':' — this looks like a 'host:port' "
                "pair or a URL; pass only the host part (IPv6 literals "
                "are accepted without brackets)"
            )
        # DNS names are case-insensitive; lowering here also lets the
        # stdlib IDNA codec recognize uppercase 'XN--' labels.
        return hostname.lower()

    # ------------------------------------------------------------------ #
    # Shared helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _parse_ip(hostname: str):
        """Return the ipaddress object if the input is an IP literal."""
        try:
            return ipaddress.ip_address(hostname)
        except ValueError:
            return None

    @classmethod
    def _strip_root_dot(cls, hostname: str) -> tuple:
        """Strip one trailing root dot, reporting whether it was there."""
        if hostname.endswith("."):
            return hostname[:-1], True
        return hostname, False

    @classmethod
    def _ace_form(cls, hostname: str) -> tuple:
        """Return (ascii_form, punycode_block) for any hostname.

        ``ascii_form`` is the input when it is already pure ASCII and
        the ACE encoding otherwise. The punycode block always has the
        same shape; conversion failures are caught and reported as a
        note (``error``) instead of raised.
        """
        block: dict[str, Any] = {
            "applicable": False,
            "has_ace_label": False,
            "ace_form": None,
            "unicode_form": None,
            "error": None,
        }
        if hostname.isascii():
            ascii_form = hostname
            block["ace_form"] = hostname
            labels = hostname.split(".")
            if any(
                label.lower().startswith("xn--") for label in labels
            ):
                block["applicable"] = True
                block["has_ace_label"] = True
                try:
                    block["unicode_form"] = ascii_form.encode(
                        "ascii"
                    ).decode("idna")
                except UnicodeError as exc:
                    block["error"] = (
                        "punycode (xn--) label could not be decoded by "
                        f"the stdlib IDNA codec: {exc}"
                    )
            return ascii_form, block

        block["applicable"] = True
        block["unicode_form"] = hostname
        try:
            ascii_form = hostname.encode("idna").decode("ascii")
        except UnicodeError as exc:
            block["error"] = (
                "hostname could not be encoded to its ACE (xn--) form "
                f"by the stdlib IDNA codec: {exc}"
            )
            return hostname, block
        block["ace_form"] = ascii_form
        if any(label.startswith("xn--") for label in ascii_form.split(".")):
            block["has_ace_label"] = True
        return ascii_form, block

    @staticmethod
    def _describe_labels(ascii_form: str) -> dict:
        """Summarize label structure of an ASCII hostname."""
        labels = ascii_form.split(".")
        count = len(labels)
        tld = labels[-1] if count >= 2 else None
        registered = ".".join(labels[-2:]) if count >= 2 else labels[0]
        subdomains = count - 2 if count > 2 else 0
        return {
            "labels": count,
            "registered_domain": registered,
            "tld": tld,
            "subdomain_count": subdomains,
        }

    # ------------------------------------------------------------------ #
    # validate mode
    # ------------------------------------------------------------------ #

    def _run_validate(
        self,
        hostname: str,
        allow_single_label: bool,
        allow_underscores: bool,
    ) -> dict[str, Any]:
        """Run all hostname checks and collect the verdict."""
        host, trailing_dot = self._strip_root_dot(hostname)
        context: dict[str, Any] = {
            "mode": "validate",
            "hostname": host,
            "trailing_dot_stripped": trailing_dot,
        }
        ip = self._parse_ip(host)
        if ip is not None:
            return {
                **context,
                "verdict": "ip_literal",
                "is_ip_literal": True,
                "reasons": [
                    f"input is an IPv{ip.version} address literal "
                    f"({host}), not a domain name — DNS hostname rules "
                    "do not apply; use an IP-oriented tool instead"
                ],
                "warnings": [],
            }

        reasons: list = []
        warnings: list = []
        if len(host) > MAX_DNS_NAME_CHARS:
            reasons.append(
                f"overall length is {len(host)} characters, exceeding the "
                f"{MAX_DNS_NAME_CHARS}-character DNS limit"
            )
        labels = host.split(".")
        # A stripped trailing root dot means the input *did* carry a
        # dot: RFC 1035 marks such a name explicitly fully qualified
        # even when it has only one label, so the single-label check
        # only applies to names that never contained a dot at all.
        if len(labels) == 1 and not trailing_dot:
            message = (
                f"single-label hostname {host!r} has no dot and is not a "
                "fully qualified domain name"
            )
            if allow_single_label:
                warnings.append(
                    message
                    + " — accepted leniently (allow_single_label=True)"
                )
            else:
                reasons.append(
                    message
                    + " (pass allow_single_label=True to accept names "
                    "like 'localhost')"
                )
        for index, label in enumerate(labels, start=1):
            if not label:
                reasons.append(f"label {index} is empty (double dot)")
                continue
            if len(label) > MAX_LABEL_CHARS:
                reasons.append(
                    f"label {index} ({label[:32]!r}...) is {len(label)} "
                    f"characters long, exceeding the {MAX_LABEL_CHARS}-"
                    "character limit"
                )
            if not label.isascii():
                offenders = sorted({c for c in label if not c.isascii()})
                reasons.append(
                    f"label {index} contains non-ASCII characters "
                    f"({''.join(offenders)[:16]!r}) — hostnames on the "
                    "wire are ASCII; use info mode to convert to the "
                    "ACE (xn--) form"
                )
            elif not _LDH_LABEL.match(label):
                offenders = sorted(
                    {c for c in label if not _LDH_LABEL.match(c)}
                )
                if "_" in offenders:
                    message = (
                        f"label {index} ({label[:32]!r}) contains an "
                        "underscore, which is not allowed in RFC 1035 "
                        "hostnames (allowed: letters, digits, hyphen)"
                    )
                    if allow_underscores:
                        warnings.append(
                            message
                            + " — accepted leniently "
                            "(allow_underscores=True)"
                        )
                    else:
                        reasons.append(
                            message
                            + " (pass allow_underscores=True to accept "
                            "it leniently)"
                        )
                    non_underscore = [c for c in offenders if c != "_"]
                    if non_underscore:
                        reasons.append(
                            f"label {index} ({label[:32]!r}) contains "
                            f"disallowed characters "
                            f"({''.join(non_underscore)[:16]!r}); "
                            "allowed: letters, digits, hyphen"
                        )
                else:
                    reasons.append(
                        f"label {index} ({label[:32]!r}) contains "
                        f"disallowed characters "
                        f"({''.join(offenders)[:16]!r}); allowed: "
                        "letters, digits, hyphen"
                    )
            if label.startswith("-") or label.endswith("-"):
                reasons.append(
                    f"label {index} ({label[:32]!r}) starts or ends "
                    "with a hyphen"
                )
        tld = labels[-1] if len(labels) >= 2 else None
        if tld:
            if not tld.isascii():
                pass  # already reported by the charset check above
            elif not _ALPHABETIC.match(tld):
                reasons.append(
                    f"top-level label {tld!r} is not purely alphabetic "
                    "— TLDs consist of letters only (a numeric last "
                    "label usually means the input is an IP-style "
                    "address, and an 'xn--' last label is an "
                    "internationalized TLD best inspected with info "
                    "mode)"
                )
            elif len(tld) < 2:
                reasons.append(
                    f"top-level label {tld!r} is only {len(tld)} "
                    "character long — TLDs are at least two"
                )
        return {
            **context,
            "verdict": "valid" if not reasons else "invalid",
            "is_ip_literal": False,
            "reasons": reasons,
            "warnings": warnings,
        }

    # ------------------------------------------------------------------ #
    # info mode
    # ------------------------------------------------------------------ #

    def _run_info(self, hostname: str) -> dict[str, Any]:
        """Describe the label structure and punycode forms of a host."""
        host, trailing_dot = self._strip_root_dot(hostname)
        context: dict[str, Any] = {
            "mode": "info",
            "hostname": host,
            "trailing_dot_stripped": trailing_dot,
        }
        ip = self._parse_ip(host)
        if ip is not None:
            return {
                **context,
                "is_ip_literal": True,
                "ip_version": ip.version,
                "labels": None,
                "registered_domain": None,
                "tld": None,
                "subdomain_count": 0,
                "punycode": {
                    "applicable": False,
                    "has_ace_label": False,
                    "ace_form": None,
                    "unicode_form": None,
                    "error": None,
                },
                "note": (
                    f"input is an IPv{ip.version} address literal, not a "
                    "domain name — no domain structure to describe"
                ),
            }
        ascii_form, punycode = self._ace_form(host)
        return {
            **context,
            "is_ip_literal": False,
            **self._describe_labels(ascii_form),
            "punycode": punycode,
        }

    # ------------------------------------------------------------------ #
    # tld_lookup mode
    # ------------------------------------------------------------------ #

    def _run_tld_lookup(self, hostname: str) -> dict[str, Any]:
        """Classify the TLD against the built-in indicative table."""
        host, trailing_dot = self._strip_root_dot(hostname)
        # Accept a bare TLD or a hostname; the last label is the TLD.
        labels = [label for label in host.split(".") if label]
        if not labels:
            self._invalid(
                "hostname must contain at least one non-empty label for "
                "tld_lookup"
            )
        tld = labels[-1]
        category = self.KNOWN_TLDS.get(tld)
        if category is not None:
            verdict, resolved = "known", category
        else:
            verdict, resolved = "unknown", "unknown"
        return {
            "mode": "tld_lookup",
            "tld": tld,
            "verdict": verdict,
            "category": resolved,
            "note": _TLD_NOTE,
        }
