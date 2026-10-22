#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @Author  : agentUniverse contributors
# @FileName: random_data_generator_tool.py

"""Random data generator tool built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency generator for the
synthetic values agents need when fabricating fixtures, seeding demo
environments, or minting opaque tokens: person names, email addresses,
hexadecimal tokens and UUIDs.

The tool is a thin, strictly-validated façade over ``random`` and
``uuid`` and supports four modes:

* ``name`` — random person names drawn from curated built-in pools of
  48 first names and 48 last names. ``style`` selects ``first``,
  ``last`` or ``full`` (``"First Last"``, the default).
* ``email`` — random email addresses built as
  ``first.last##@domain`` (lowercase, two random digits). By default
  the domain is drawn from the RFC 2606 reserved ``example.com`` /
  ``example.org`` / ``example.net`` pool so generated addresses can
  never collide with a real mailbox; an optional validated ``domain``
  argument overrides the pool.
* ``hex`` — random opaque hexadecimal tokens of ``bytes`` random bytes
  (1-256, default 16) with an optional ASCII ``prefix`` such as
  ``tok_``. Tokens are lowercase hex, two characters per byte.
* ``uuid`` — RFC 4122 version 4 UUIDs in the canonical dashed string
  form. Unlike ``uuid.uuid4()`` the bytes are drawn from the tool's
  random source, so they are reproducible under an injected seeded
  generator while remaining unpredictable under the default system
  source.

Every mode accepts ``count`` (1-50, default 1) and reports the Shannon
entropy of one generated value — ``bits = log2(pool size)`` — as
``entropy_bits`` metadata, so callers can reason about collision
resistance (a 16-byte hex token reports 128 bits, a UUID v4 122 bits).

The random source is injectable for deterministic testing: the
``random_gen`` attribute defaults to ``random.SystemRandom`` and tests
substitute ``random.Random(seed)``. Input validation is strict and
happens before any computation: malformed parameters (unknown mode or
style, out-of-bounds ``count`` or ``bytes``, non-string or whitespace
``prefix``, invalid ``domain``) raise a ``ValueError``, mirroring the
other common tools.
"""

import math
import random as random_module
import re
import uuid as uuid_module
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

# Dot-separated hostname labels: alnum / hyphen, 1-63 chars per label,
# no leading or trailing hyphen, at least one dot.
_VALID_DOMAIN = re.compile(
    r"\A(?=.{1,253}\Z)"
    r"[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?"
    r"(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+\Z"
)


class RandomDataGeneratorTool(Tool):
    """Random data generator tool built purely on the stdlib.

    Generates names, emails, hex tokens and UUID v4 values with
    configurable batch size and an entropy estimate, using an
    injectable random source (``random_gen``, default
    ``random.SystemRandom``).
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "random_data_generator_tool"
    description: str = (
        "Random data generator tool — pure Python stdlib, no network "
        "required. Person names from curated pools (mode='name', "
        "style=first/last/full), email addresses on reserved RFC 2606 "
        "example domains or a custom validated domain (mode='email'), "
        "lowercase hex tokens with an optional prefix "
        "(mode='hex', bytes 1-256), and RFC 4122 UUID v4 values "
        "(mode='uuid'). Every mode takes count (1-50) and reports the "
        "Shannon entropy of one value as entropy_bits."
    )

    MODES: ClassVar[tuple] = ("name", "email", "hex", "uuid")
    STYLES: ClassVar[tuple] = ("first", "last", "full")
    # RFC 2606 section 3 reserves exactly these three domains; addresses
    # generated from the pool can never reach a real mailbox.
    DOMAINS: ClassVar[Tuple[str, ...]] = (
        "example.com",
        "example.org",
        "example.net",
    )
    FIRST_NAMES: ClassVar[Tuple[str, ...]] = (
        "Ava", "Liam", "Noah", "Emma", "Olivia", "Sophia", "Mia",
        "Lucas", "Ethan", "Aiden", "Amir", "Ingrid", "Lars", "Mei",
        "Hiro", "Yuki", "Kenji", "Aisha", "Omar", "Fatima", "Yusuf",
        "Layla", "Priya", "Arjun", "Rohan", "Ananya", "Carlos", "Diego",
        "Lucia", "Mateo", "Chloe", "Daniel", "Elena", "Felix", "Grace",
        "Hannah", "Ibrahim", "Jade", "Kwame", "Leila", "Marco", "Nadia",
        "Oscar", "Paula", "Quentin", "Rania", "Sven", "Tara",
    )
    LAST_NAMES: ClassVar[Tuple[str, ...]] = (
        "Anderson", "Bennett", "Carvalho", "Diallo", "Eriksen",
        "Fernandez", "Garcia", "Haddad", "Ivanov", "Jensen", "Kimura",
        "Kowalski", "Lindqvist", "Martinez", "Nakamura", "Novak",
        "Okafor", "Olsen", "Patel", "Petrov", "Quintero", "Rahman",
        "Rossi", "Silva", "Sato", "Schmidt", "Tanaka", "Tan",
        "Thompson", "Ueda", "Valdes", "Vargas", "Watanabe", "Weber",
        "Xu", "Yamamoto", "Yilmaz", "Zhang", "Ali", "Bauer", "Costa",
        "Dubois", "Fischer", "Haruna", "Ito", "Jansen", "Kim", "Larsen",
    )

    # Bounds: batch size, token length, token prefix.
    MAX_COUNT: ClassVar[int] = 50
    MAX_BYTES: ClassVar[int] = 256
    MAX_PREFIX_CHARS: ClassVar[int] = 16
    # A UUID v4 carries 122 random bits (6 bits are version/variant).
    UUID_V4_RANDOM_BITS: ClassVar[int] = 122

    # Injectable random source; replaced at construction time with a
    # random.SystemRandom instance unless the caller supplies one.
    random_gen: Any = None

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        if self.random_gen is None:
            self.random_gen = random_module.SystemRandom()

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        count: Any = None,
        style: Any = None,
        domain: Any = None,
        bytes: Any = None,
        prefix: Any = None,
    ) -> Dict[str, Any]:
        """Generate a batch of random values.

        Args:
            mode (str): One of ``name`` / ``email`` / ``hex`` / ``uuid``.
            count (int | str): How many values to generate, 1-50
                (default 1). A string of digits is accepted.
            style (str): Name mode only — ``first``, ``last`` or
                ``full`` (default, ``"First Last"``),
                case-insensitive.
            domain (str): Email mode only — custom domain such as
                ``corp.example``; validated as a hostname (letters,
                digits, hyphens, dots, at least one dot). Defaults to
                the reserved ``example.com`` / ``example.org`` /
                ``example.net`` pool.
            bytes (int | str): Hex mode only — random bytes per token,
                1-256 (default 16). A string of digits is accepted.
            prefix (str): Hex mode only — short ASCII prefix such as
                ``tok_`` prepended to each token (default empty).

        Returns:
            Dict[str, Any]: A dict with the ``mode``, the effective
                options, ``entropy_bits`` (Shannon entropy of one
                generated value) and the generated values under
                ``result`` (a list of strings of length ``count``).

        Raises:
            ValueError: If any parameter is malformed (before any
                value is generated).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        clean_count = self._validate_count(count)
        if mode == "name":
            return self._run_name(clean_count, style)
        if mode == "email":
            return self._run_email(clean_count, domain)
        if mode == "hex":
            return self._run_hex(clean_count, bytes, prefix)
        return self._run_uuid(clean_count)

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any generation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"random_data_generator_tool: {message}")

    @classmethod
    def _validate_count(cls, count: Any) -> int:
        """Validate the batch size (1-50, digit strings accepted)."""
        return cls._validate_int(
            count, default=1, minimum=1, maximum=cls.MAX_COUNT, label="count"
        )

    @classmethod
    def _validate_int(
        cls, value: Any, default: int, minimum: int, maximum: int, label: str
    ) -> int:
        """Validate an integer option with bounds (digit strings ok)."""
        if value is None:
            return default
        if isinstance(value, bool):
            cls._invalid(
                f"{label} must be an integer between "
                f"{minimum} and {maximum} (got {value!r})"
            )
        if isinstance(value, int):
            number = value
        elif isinstance(value, str) and value.strip().isdigit():
            number = int(value.strip())
        else:
            cls._invalid(
                f"{label} must be an integer between {minimum} and "
                f"{maximum} (got {value!r})"
            )
        if not minimum <= number <= maximum:
            cls._invalid(
                f"{label} must be between {minimum} and {maximum} "
                f"(got {number})"
            )
        return number

    @classmethod
    def _validate_style(cls, style: Any) -> str:
        """Validate the name-mode ``style`` selector."""
        if style is None:
            return "full"
        if isinstance(style, bool) or not isinstance(style, str):
            cls._invalid(
                "style must be one of: "
                f"{', '.join(cls.STYLES)} (got {style!r})"
            )
        clean = style.strip().lower()
        if clean not in cls.STYLES:
            cls._invalid(
                "style must be one of: "
                f"{', '.join(cls.STYLES)} (got {style!r})"
            )
        return clean

    @classmethod
    def _validate_domain(cls, domain: Any) -> str:
        """Validate the email-mode custom ``domain`` (a hostname)."""
        if domain is None:
            return ""
        if isinstance(domain, bool) or not isinstance(domain, str):
            cls._invalid(
                f"domain must be a hostname string such as 'corp.example' "
                f"(got {domain!r})"
            )
        clean = domain.strip().lower()
        if not _VALID_DOMAIN.match(clean):
            cls._invalid(
                "domain must be a valid hostname with at least one dot: "
                "letters, digits and hyphens per label, no leading or "
                "trailing hyphen (e.g. 'corp.example') "
                f"(got {domain[:64]!r})"
            )
        return clean

    @classmethod
    def _validate_prefix(cls, prefix: Any) -> str:
        """Validate the hex-mode token ``prefix``.

        Accepts ``None`` (no prefix) and ASCII printable characters
        other than whitespace; rejects non-ASCII, whitespace and
        prefixes longer than 16 characters.
        """
        if prefix is None:
            return ""
        if isinstance(prefix, bool) or not isinstance(prefix, str):
            cls._invalid(
                f"prefix must be a short ASCII string (got {prefix!r})"
            )
        if len(prefix) > cls.MAX_PREFIX_CHARS:
            cls._invalid(
                "prefix must be at most "
                f"{cls.MAX_PREFIX_CHARS} characters (got {len(prefix)})"
            )
        for char in prefix:
            if not 0x21 <= ord(char) <= 0x7E:
                cls._invalid(
                    "prefix must only contain printable ASCII characters "
                    f"without whitespace (got {prefix!r})"
                )
        return prefix

    # ------------------------------------------------------------------ #
    # name mode
    # ------------------------------------------------------------------ #

    def _run_name(self, count: int, style: Any) -> Dict[str, Any]:
        """Generate person names from the built-in pools."""
        clean_style = self._validate_style(style)
        gen = self.random_gen
        if clean_style == "first":
            values = [gen.choice(self.FIRST_NAMES) for _ in range(count)]
            pool_size = len(self.FIRST_NAMES)
        elif clean_style == "last":
            values = [gen.choice(self.LAST_NAMES) for _ in range(count)]
            pool_size = len(self.LAST_NAMES)
        else:
            values = [
                f"{gen.choice(self.FIRST_NAMES)} "
                f"{gen.choice(self.LAST_NAMES)}"
                for _ in range(count)
            ]
            pool_size = len(self.FIRST_NAMES) * len(self.LAST_NAMES)
        return {
            "mode": "name",
            "style": clean_style,
            "count": count,
            "entropy_bits": round(math.log2(pool_size), 1),
            "result": values,
        }

    # ------------------------------------------------------------------ #
    # email mode
    # ------------------------------------------------------------------ #

    def _run_email(self, count: int, domain: Any) -> Dict[str, Any]:
        """Generate ``first.last##@domain`` email addresses."""
        clean_domain = self._validate_domain(domain)
        gen = self.random_gen
        values: List[str] = []
        for _ in range(count):
            first = gen.choice(self.FIRST_NAMES).lower()
            last = gen.choice(self.LAST_NAMES).lower()
            digits = f"{gen.randrange(100):02d}"
            host = clean_domain or gen.choice(self.DOMAINS)
            values.append(f"{first}.{last}{digits}@{host}")
        pool_size = (
            len(self.FIRST_NAMES)
            * len(self.LAST_NAMES)
            * 100
            * (1 if clean_domain else len(self.DOMAINS))
        )
        result: Dict[str, Any] = {
            "mode": "email",
            "count": count,
            "entropy_bits": round(math.log2(pool_size), 1),
            "result": values,
        }
        if clean_domain:
            result["domain"] = clean_domain
        else:
            result["domain_pool"] = list(self.DOMAINS)
        return result

    # ------------------------------------------------------------------ #
    # hex mode
    # ------------------------------------------------------------------ #

    def _run_hex(self, count: int, nbytes: Any, prefix: Any) -> Dict[str, Any]:
        """Generate lowercase hexadecimal tokens."""
        clean_bytes = self._validate_int(
            nbytes,
            default=16,
            minimum=1,
            maximum=self.MAX_BYTES,
            label="bytes",
        )
        clean_prefix = self._validate_prefix(prefix)
        gen = self.random_gen
        values = [
            clean_prefix + gen.randbytes(clean_bytes).hex()
            for _ in range(count)
        ]
        return {
            "mode": "hex",
            "bytes": clean_bytes,
            "prefix": clean_prefix,
            "count": count,
            "entropy_bits": clean_bytes * 8,
            "result": values,
        }

    # ------------------------------------------------------------------ #
    # uuid mode
    # ------------------------------------------------------------------ #

    def _run_uuid(self, count: int) -> Dict[str, Any]:
        """Generate RFC 4122 UUID v4 values from the random source."""
        gen = self.random_gen
        values = []
        for _ in range(count):
            raw = bytearray(gen.randbytes(16))
            raw[6] = (raw[6] & 0x0F) | 0x40  # version 4
            raw[8] = (raw[8] & 0x3F) | 0x80  # RFC 4122 variant
            values.append(str(uuid_module.UUID(bytes=bytes(raw))))
        return {
            "mode": "uuid",
            "version": 4,
            "count": count,
            "entropy_bits": self.UUID_V4_RANDOM_BITS,
            "result": values,
        }
