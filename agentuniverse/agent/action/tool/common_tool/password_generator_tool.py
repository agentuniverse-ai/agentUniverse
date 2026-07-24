#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""Password generator tool backed only on the Python standard library.

The tool relies on :mod:`secrets` for cryptographically strong randomness and
:mod:`string` for character pools, so it has zero third-party dependencies. It
exposes three operations: ``generate``, ``generate_batch`` and ``check_strength``.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import math
import string
from typing import Any, Dict, List, Optional

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.base.util.logging.logging_util import LOGGER

# Character pools.
UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
# A conservative, unambiguous symbol set.
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?/"
# Characters that are visually similar and often excluded for readability.
SIMILAR_CHARS = set("Il1O0o") | set("|`'\"")

MIN_LENGTH = 4
MAX_LENGTH = 256
MAX_BATCH = 1000


class PasswordGeneratorTool(Tool):
    """Generate cryptographically strong passwords and rate their strength.

    The tool has three modes selected via the ``mode`` parameter:

    * ``generate``       - create a single password
    * ``generate_batch`` - create several passwords at once
    * ``check_strength`` - score an existing password

    All randomness comes from :mod:`secrets`, making the output safe for use as
    real credentials.
    """

    description: str = (
        "Generate cryptographically strong passwords (secrets-based) and "
        "check password strength. Zero third-party dependencies."
    )

    # Default character-set composition.
    default_length: int = Field(
        default=16, description="Default password length."
    )
    include_uppercase: bool = Field(default=True, description="Include A-Z.")
    include_lowercase: bool = Field(default=True, description="Include a-z.")
    include_digits: bool = Field(default=True, description="Include 0-9.")
    include_symbols: bool = Field(
        default=True, description="Include a curated set of symbols."
    )
    exclude_similar: bool = Field(
        default=False,
        description="Exclude visually similar characters (Il1O0o|`'\").",
    )

    def execute(
        self,
        mode: str = "generate",
        length: Optional[int] = None,
        count: int = 1,
        password: Optional[str] = None,
        include_uppercase: Optional[bool] = None,
        include_lowercase: Optional[bool] = None,
        include_digits: Optional[bool] = None,
        include_symbols: Optional[bool] = None,
        exclude_similar: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Run the requested operation and return a structured result.

        Per-call keyword arguments override the tool's defaults for that
        invocation only.
        """
        try:
            operation = self._mode(mode)
            composition = self._composition(
                include_uppercase,
                include_lowercase,
                include_digits,
                include_symbols,
                exclude_similar,
            )
            if operation == "generate":
                resolved_length = self._resolve_length(length, count=count)
                return self._generate_one(resolved_length, composition)
            if operation == "generate_batch":
                resolved_length = self._resolve_length(length, count=count)
                return self._generate_batch(resolved_length, count, composition)
            return self._check_strength(password)
        except (TypeError, ValueError) as exc:
            LOGGER.error(f"PasswordGeneratorTool validation error: {exc}")
            return self._error("validation_error", str(exc))
        except Exception as exc:
            LOGGER.error(f"PasswordGeneratorTool operation failed: {exc}")
            return self._error("operation_error", f"Password operation failed: {exc}")

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _error(kind: str, message: str) -> Dict[str, Any]:
        return {"status": "error", "error_type": kind, "error": message}

    @staticmethod
    def _mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in {"generate", "generate_batch", "check_strength"}:
            raise ValueError(
                "mode must be generate, generate_batch, or check_strength"
            )
        return mode

    def _composition(
        self,
        upper: Optional[bool],
        lower: Optional[bool],
        digits: Optional[bool],
        symbols: Optional[bool],
        similar: Optional[bool],
    ) -> Dict[str, Any]:
        """Merge per-call overrides with the tool-level defaults."""
        resolved_upper = self.include_uppercase if upper is None else upper
        resolved_lower = self.include_lowercase if lower is None else lower
        resolved_digits = self.include_digits if digits is None else digits
        resolved_symbols = self.include_symbols if symbols is None else symbols
        resolved_similar = self.exclude_similar if similar is None else similar
        for name, val in (
            ("include_uppercase", resolved_upper),
            ("include_lowercase", resolved_lower),
            ("include_digits", resolved_digits),
            ("include_symbols", resolved_symbols),
            ("exclude_similar", resolved_similar),
        ):
            if not isinstance(val, bool):
                raise TypeError(f"{name} must be a boolean")

        pool = ""
        classes: List[str] = []
        if resolved_upper:
            pool += UPPERCASE
            classes.append(UPPERCASE)
        if resolved_lower:
            pool += LOWERCASE
            classes.append(LOWERCASE)
        if resolved_digits:
            pool += DIGITS
            classes.append(DIGITS)
        if resolved_symbols:
            pool += SYMBOLS
            classes.append(SYMBOLS)
        if resolved_similar:
            pool = "".join(c for c in pool if c not in SIMILAR_CHARS)
            classes = [
                "".join(c for c in group if c not in SIMILAR_CHARS)
                for group in classes
            ]
        if not pool:
            raise ValueError(
                "at least one character class must be enabled "
                "(uppercase, lowercase, digits, or symbols)"
            )
        # Drop any class that became empty after similarity filtering.
        classes = [group for group in classes if group]
        return {
            "pool": pool,
            "classes": classes,
            "uppercase": resolved_upper,
            "lowercase": resolved_lower,
            "digits": resolved_digits,
            "symbols": resolved_symbols,
            "exclude_similar": resolved_similar,
        }

    def _resolve_length(self, length: Any, count: int = 1) -> int:
        if length is None:
            resolved = self.default_length
        else:
            if isinstance(length, bool) or not isinstance(length, int):
                raise TypeError("length must be an integer")
            resolved = length
        if resolved < MIN_LENGTH:
            raise ValueError(f"length must be at least {MIN_LENGTH}")
        if resolved > MAX_LENGTH:
            raise ValueError(f"length must be at most {MAX_LENGTH}")
        return resolved

    @staticmethod
    def _validate_count(value: Any) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("count must be an integer")
        if value < 1:
            raise ValueError("count must be at least 1")
        if value > MAX_BATCH:
            raise ValueError(f"count must be at most {MAX_BATCH}")
        return value

    def _generate_one(
        self, length: int, composition: Dict[str, Any]
    ) -> Dict[str, Any]:
        import secrets

        pool: str = composition["pool"]
        classes: List[str] = composition["classes"]
        characters: List[str] = []
        # Guarantee at least one character from every requested class so the
        # password cannot silently drop a category.
        for group in classes:
            characters.append(secrets.choice(group))
        remaining = length - len(characters)
        if remaining < 0:
            # If length < number of classes we fall back to pure sampling.
            characters = []
            remaining = length
        characters.extend(secrets.choice(pool) for _ in range(remaining))
        # Shuffle so the guaranteed characters are not front-loaded.
        for index in range(len(characters) - 1, 0, -1):
            swap = secrets.randbelow(index + 1)
            characters[index], characters[swap] = characters[swap], characters[index]
        password = "".join(characters)
        entropy = self._entropy_bits(len(pool), length)
        return {
            "status": "success",
            "mode": "generate",
            "password": password,
            "length": length,
            "entropy_bits": round(entropy, 2),
            "pool_size": len(pool),
            "composition": {
                "uppercase": composition["uppercase"],
                "lowercase": composition["lowercase"],
                "digits": composition["digits"],
                "symbols": composition["symbols"],
                "exclude_similar": composition["exclude_similar"],
            },
        }

    def _generate_batch(
        self, length: int, count: int, composition: Dict[str, Any]
    ) -> Dict[str, Any]:
        validated = self._validate_count(count)
        passwords: List[Dict[str, Any]] = [
            self._generate_one(length, composition) for _ in range(validated)
        ]
        entropy = passwords[0]["entropy_bits"] if passwords else 0.0
        return {
            "status": "success",
            "mode": "generate_batch",
            "count": validated,
            "passwords": [item["password"] for item in passwords],
            "length": length,
            "entropy_bits": entropy,
            "pool_size": passwords[0]["pool_size"] if passwords else 0,
        }

    def _check_strength(self, value: Any) -> Dict[str, Any]:
        if not isinstance(value, str):
            raise TypeError("password must be a string")
        if not value:
            raise ValueError("password must not be empty")
        length = len(value)
        pool_size = self._estimate_pool_size(value)
        entropy = self._entropy_bits(pool_size, length)
        issues: List[str] = []
        if length < 8:
            issues.append("length < 8")
        if length < 12:
            issues.append("length < 12 (consider 12+ characters)")
        if not any(c.islower() for c in value):
            issues.append("no lowercase letters")
        if not any(c.isupper() for c in value):
            issues.append("no uppercase letters")
        if not any(c.isdigit() for c in value):
            issues.append("no digits")
        if not any(not c.isalnum() for c in value):
            issues.append("no symbols")
        score = self._score(entropy, issues)
        return {
            "status": "success",
            "mode": "check_strength",
            "length": length,
            "pool_size": pool_size,
            "entropy_bits": round(entropy, 2),
            "score": score,
            "rating": self._rating(score),
            "issues": issues,
        }

    @staticmethod
    def _estimate_pool_size(value: str) -> int:
        size = 0
        if any(c.islower() for c in value):
            size += len(LOWERCASE)
        if any(c.isupper() for c in value):
            size += len(UPPERCASE)
        if any(c.isdigit() for c in value):
            size += len(DIGITS)
        if any(not c.isalnum() for c in value):
            size += len(SYMBOLS)
        return size or 1

    @staticmethod
    def _entropy_bits(pool_size: int, length: int) -> float:
        if pool_size <= 1 or length <= 0:
            return 0.0
        return length * math.log2(pool_size)

    @staticmethod
    def _score(entropy: float, issues: List[str]) -> int:
        """Map entropy and issues onto a 0-100 score."""
        if entropy >= 100:
            base = 100
        elif entropy >= 80:
            base = 90
        elif entropy >= 60:
            base = 75
        elif entropy >= 45:
            base = 60
        elif entropy >= 35:
            base = 45
        elif entropy >= 28:
            base = 30
        else:
            base = 15
        penalty = min(len(issues) * 8, 40)
        return max(0, min(100, base - penalty))

    @staticmethod
    def _rating(score: int) -> str:
        if score >= 85:
            return "very strong"
        if score >= 70:
            return "strong"
        if score >= 50:
            return "moderate"
        if score >= 30:
            return "weak"
        return "very weak"
