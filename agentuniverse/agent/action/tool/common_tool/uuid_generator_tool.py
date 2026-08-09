#!/usr/bin/env python3

"""Bounded UUID generation and validation tool (standard library only)."""

# Validation failures are converted to structured tool responses at the public
# execute boundary, so bespoke exception subclasses would add no useful signal.
# ruff: noqa: TRY003, TRY004

import re
import uuid as _uuid
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool


class UUIDGeneratorTool(Tool):
    """Generate, validate, and extract UUIDs with zero external dependencies.

    The tool relies only on the Python standard-library ``uuid`` module, so it
    imports and runs in any environment. Supported modes:

    * ``generate`` — emit one UUID (``uuid4`` by default; ``uuid3``/``uuid5``
      require a ``namespace``).
    * ``generate_batch`` — emit up to ``count`` UUIDs in a single call.
    * ``validate`` — report whether a candidate string is a well-formed UUID.
    * ``extract`` — pull every well-formed UUID out of an arbitrary string.

    Output formatting is controlled by ``format``: ``string`` (the canonical
    hyphenated form), ``hex`` (32 hex digits with no separators), or ``urn``
    (the ``urn:uuid:...`` form).
    """

    version: int = 4
    namespace: str = "dns"
    name: str = "agentuniverse"
    count: int = 1
    format: str = "string"
    max_batch_size: int = 1_000
    max_extract_chars: int = 100_000

    _NAMESPACES: ClassVar[dict[str, Any]] = {
        "dns": _uuid.NAMESPACE_DNS,
        "url": _uuid.NAMESPACE_URL,
        "oid": _uuid.NAMESPACE_OID,
        "x500": _uuid.NAMESPACE_X500,
    }
    _FORMATS: ClassVar[set[str]] = {"string", "hex", "urn"}
    _VERSIONS: ClassVar[set[int]] = {3, 4, 5}
    _UUID_REGEX: ClassVar[re.Pattern[str]] = re.compile(
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b"
    )

    def execute(
        self,
        mode: str,
        version: int | None = None,
        namespace: str | None = None,
        name: str | None = None,
        count: int | None = None,
        format: str | None = None,
        value: str | None = None,
    ) -> dict[str, Any]:
        """Run a UUID operation.

        Args:
            mode: One of ``generate``, ``generate_batch``, ``validate``,
                or ``extract``.
            version: UUID version (3, 4, or 5). Defaults to the tool-level value.
            namespace: Namespace key (``dns``/``url``/``oid``/``x500``) or a
                UUID string. Required for versions 3 and 5.
            name: Name used by versions 3 and 5. Defaults to the tool-level value.
            count: Number of UUIDs for ``generate_batch``.
            format: Output format — ``string``, ``hex``, or ``urn``.
            value: Candidate UUID (for ``validate``) or text to scan
                (for ``extract``).

        Returns:
            A structured success or error dictionary.
        """
        try:
            self._validate_configuration()
            normalized_mode = self._normalize_mode(mode)
            resolved_version = self._resolve_version(version)
            resolved_format = self._resolve_format(format)
            resolved_namespace = self._resolve_namespace(namespace, resolved_version)
            resolved_name = self._resolve_name(name, resolved_version)

            if normalized_mode == "generate":
                return self._generate(resolved_version, resolved_namespace, resolved_name, resolved_format)
            if normalized_mode == "generate_batch":
                return self._generate_batch(
                    resolved_version,
                    resolved_namespace,
                    resolved_name,
                    resolved_format,
                    count,
                )
            if normalized_mode == "validate":
                if value is None:
                    raise ValueError("value is required for validate mode")
                return self._validate(value)
            return self._extract(value)
        except (TypeError, ValueError) as exc:
            return self._error(mode, "validation_error", str(exc))
        except Exception as exc:  # defensive: any unexpected failure
            return self._error(mode, "operation_error", f"UUID operation failed: {exc}")

    # ------------------------------------------------------------------ public

    @staticmethod
    def _error(mode: Any, kind: str, message: str) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": "error",
            "error_type": kind,
            "error": message,
        }
        if isinstance(mode, str) and mode:
            payload["mode"] = mode.strip().lower()
        return payload

    def _validate_configuration(self) -> None:
        for name in ("max_batch_size", "max_extract_chars"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.version not in self._VERSIONS:
            allowed = ", ".join(str(v) for v in sorted(self._VERSIONS))
            raise ValueError(f"version must be one of {allowed}, got {self.version!r}")
        if self.format not in self._FORMATS:
            allowed = ", ".join(sorted(self._FORMATS))
            raise ValueError(f"format must be one of {allowed}, got {self.format!r}")
        if not isinstance(self.namespace, str) or not self.namespace:
            raise ValueError("namespace must be a non-empty string")
        if not isinstance(self.name, str):
            raise TypeError("name must be a string")
        if isinstance(self.count, bool) or not isinstance(self.count, int) or self.count <= 0:
            raise ValueError("count must be a positive integer")

    @staticmethod
    def _normalize_mode(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        mode = value.strip().lower()
        if mode not in {"generate", "generate_batch", "validate", "extract"}:
            raise ValueError("mode must be generate, generate_batch, validate, or extract")
        return mode

    def _resolve_version(self, version: Any) -> int:
        if version is None:
            return self.version
        if isinstance(version, bool) or not isinstance(version, int):
            raise TypeError("version must be an integer")
        if version not in self._VERSIONS:
            allowed = ", ".join(str(v) for v in sorted(self._VERSIONS))
            raise ValueError(f"version must be one of {allowed}, got {version!r}")
        return version

    def _resolve_format(self, format: Any) -> str:
        if format is None:
            return self.format
        if not isinstance(format, str):
            raise TypeError("format must be a string")
        normalized = format.strip().lower()
        if normalized not in self._FORMATS:
            allowed = ", ".join(sorted(self._FORMATS))
            raise ValueError(f"format must be one of {allowed}, got {format!r}")
        return normalized

    def _resolve_namespace(self, namespace: Any, version: int) -> _uuid.UUID | None:
        if version == 4:
            return None
        candidate = self.namespace if namespace is None else namespace
        if not isinstance(candidate, str) or not candidate:
            raise ValueError(
                f"namespace is required for uuid{version} and must be a non-empty string"
            )
        key = candidate.strip().lower()
        if key in self._NAMESPACES:
            return self._NAMESPACES[key]
        try:
            return _uuid.UUID(candidate)
        except (ValueError, AttributeError, TypeError) as exc:
            known = ", ".join(sorted(self._NAMESPACES))
            raise ValueError(
                f"namespace must be one of {known} or a valid UUID string, "
                f"got {candidate!r}"
            ) from exc

    def _resolve_name(self, name: Any, version: int) -> str | None:
        if version == 4:
            return None
        candidate = self.name if name is None else name
        if not isinstance(candidate, str):
            raise TypeError(f"name is required for uuid{version} and must be a string")
        if candidate == "":
            raise ValueError(f"name is required for uuid{version} and must be a non-empty string")
        return candidate

    # ------------------------------------------------------------- generation

    def _make_uuid(self, version: int, namespace: _uuid.UUID | None, name: str | None) -> _uuid.UUID:
        if version == 4:
            return _uuid.uuid4()
        if version == 3:
            assert namespace is not None and name is not None
            return _uuid.uuid3(namespace, name)
        assert version == 5 and namespace is not None and name is not None
        return _uuid.uuid5(namespace, name)

    @staticmethod
    def _format_uuid(value: _uuid.UUID, fmt: str) -> str:
        if fmt == "hex":
            return value.hex
        if fmt == "urn":
            return value.urn
        return str(value)

    def _generate(
        self,
        version: int,
        namespace: _uuid.UUID | None,
        name: str | None,
        fmt: str,
    ) -> dict[str, Any]:
        generated = self._make_uuid(version, namespace, name)
        payload: dict[str, Any] = {
            "status": "success",
            "uuid": self._format_uuid(generated, fmt),
            "format": fmt,
            "version": version,
        }
        if namespace is not None:
            payload["namespace"] = str(namespace)
        if name is not None:
            payload["name"] = name
        return payload

    def _generate_batch(
        self,
        version: int,
        namespace: _uuid.UUID | None,
        name: str | None,
        fmt: str,
        count: Any,
    ) -> dict[str, Any]:
        if count is None:
            count = self.count
        if isinstance(count, bool) or not isinstance(count, int):
            raise TypeError("count must be an integer")
        if count <= 0:
            raise ValueError("count must be a positive integer")
        if count > self.max_batch_size:
            raise ValueError(
                f"count ({count}) exceeds max_batch_size ({self.max_batch_size})"
            )
        uuids = [self._format_uuid(self._make_uuid(version, namespace, name), fmt) for _ in range(count)]
        payload: dict[str, Any] = {
            "status": "success",
            "uuids": uuids,
            "count": len(uuids),
            "format": fmt,
            "version": version,
        }
        if namespace is not None:
            payload["namespace"] = str(namespace)
        if name is not None:
            payload["name"] = name
        return payload

    # ------------------------------------------------------------- validation

    def _validate(self, value: Any) -> dict[str, Any]:
        if not isinstance(value, str) or not value:
            raise ValueError("value must be a non-empty string")
        normalized = value.strip()
        try:
            parsed = _uuid.UUID(normalized)
        except (ValueError, AttributeError, TypeError):
            parsed = None
        is_valid = parsed is not None and str(parsed) == normalized.lower()
        payload: dict[str, Any] = {
            "status": "success",
            "value": value,
            "valid": is_valid,
        }
        if is_valid and parsed is not None:
            payload["uuid"] = str(parsed)
            payload["hex"] = parsed.hex
            payload["urn"] = parsed.urn
            payload["version"] = parsed.version
            payload["variant"] = self._variant_label(parsed.variant)
        return payload

    @staticmethod
    def _variant_label(variant: Any) -> str:
        if variant == _uuid.RFC_4122:
            return "rfc4122"
        if variant == _uuid.RESERVED_NCS:
            return "reserved_ncs"
        if variant == _uuid.RESERVED_MICROSOFT:
            return "reserved_microsoft"
        if variant == _uuid.RESERVED_FUTURE:
            return "reserved_future"
        return "unknown"

    # --------------------------------------------------------------- extract

    def _extract(self, value: Any) -> dict[str, Any]:
        if value is None:
            raise ValueError("value is required for extract mode")
        if not isinstance(value, str):
            raise TypeError("value must be a string")
        if len(value) > self.max_extract_chars:
            raise ValueError(
                f"value length ({len(value)}) exceeds max_extract_chars "
                f"({self.max_extract_chars})"
            )
        matches = self._UUID_REGEX.findall(value)
        normalized = [m.lower() for m in matches]
        unique: list[str] = []
        seen: set[str] = set()
        for candidate in normalized:
            if candidate not in seen:
                seen.add(candidate)
                unique.append(candidate)
        return {
            "status": "success",
            "uuids": unique,
            "count": len(unique),
            "total_matches": len(normalized),
        }
