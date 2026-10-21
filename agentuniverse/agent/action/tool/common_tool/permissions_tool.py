#!/usr/bin/env python3
"""Unix file-permission mode math for agents: parse, chmod operand evaluation,
umask application, security review, and chmod command inversion.

Pure bit arithmetic on the 12 mode bits (0o0000-0o7777). The tool never reads
or changes the filesystem and never runs subprocesses at runtime; every mode
input is a value supplied by the caller. Semantics follow POSIX chmod:

- Clauses are applied left to right; each clause is [ugoa]*[+-=][rwxXstugo]*.
- An omitted who means all classes (a) and, unlike open(2) creation masks,
  the process umask is NEVER consulted. (BSD-derived chmod utilities mask
  omitted-who clauses by the umask; this tool follows the POSIX rule.)
- X grants or removes execute only when the target is a directory or some
  execute bit is already set in the mode before the operation started.
  Without is_dir, X degenerates to execute-if-any-execute-present.
- ugo copy sources (=u, =g, =o) are valid only with '=' and copy the class
  bits from the mode as accumulated so far (earlier clauses count); copying
  sets only the nine permission bits of who and never clears setuid/setgid.
- s maps to setuid/setgid for the u/g parts of who (a no-op for who=o),
  t maps to the sticky bit, which is addressed only when who is 'a' or
  omitted; 'o+t' and 'ugo+t' alone are no-ops, as on BSD-derived chmod.
- A u/g/o copy letter must stand alone as the whole permission list, per the
  POSIX grammar; mixing it with other letters ('a=us') is a validation error
  (BSD-derived chmod accepts such lists with sequential-copy semantics).
- '=' sets the listed bits and clears every other bit owned by who,
  including the setuid/setgid bit of an explicitly listed class when s is
  absent from the permission list.
"""

# Public execute() converts validation exceptions into structured tool errors.
# ruff: noqa: TRY003

import re
from typing import Any, ClassVar

from agentuniverse.agent.action.tool.tool import Tool

_CLASSES = (("owner", "u", 6), ("group", "g", 3), ("other", "o", 0))
_BITS = (("read", 4), ("write", 2), ("execute", 1))
_SPECIALS = (("setuid", 0o4000, "u"), ("setgid", 0o2000, "g"), ("sticky", 0o1000, "o"))
_WHO_MASKS = {"u": 0o4700, "g": 0o2070, "o": 0o0007, "a": 0o7777}
_PERM_BITS = {"r": 0o444, "w": 0o222, "x": 0o111, "s": 0o6000, "t": 0o1000}
_OCTAL_RE = re.compile(r"^[0-7]{3,4}$")
_CLAUSE_RE = re.compile(r"^([ugoa]*)([+-=])([rwxXstugo]*)$")

_EXPECTED_CHARS = {
    "read": ("r", "-"),
    "write": ("w", "-"),
    "owner_execute": ("x", "s", "S", "-"),
    "group_execute": ("x", "s", "S", "-"),
    "other_execute": ("x", "t", "T", "-"),
}


def _position_kinds() -> dict[int, tuple[str, str, str]]:
    """Map each of the nine symbolic positions to (class, bit, kind)."""
    kinds: dict[int, tuple[str, str, str]] = {}
    for index, (cls, _, _) in enumerate(_CLASSES):
        for bit_index, (bit, _) in enumerate(_BITS):
            kind = bit if bit != "execute" else f"{cls}_execute"
            kinds[index * 3 + bit_index] = (cls, bit, kind)
    return kinds


_POSITIONS = _position_kinds()


class PermissionsTool(Tool):
    """Deterministic Unix permission-mode arithmetic without filesystem access."""

    max_mode_length: int = 16
    max_operation_length: int = 128
    max_clauses: int = 12

    _EXPECTED_SUID: ClassVar[tuple[str, ...]] = (
        "/usr/bin/passwd",
        "/usr/bin/sudo",
        "/usr/bin/su",
        "/usr/bin/chsh",
        "/usr/bin/chfn",
        "/usr/bin/newgrp",
        "/usr/bin/gpasswd",
        "/usr/bin/crontab",
        "/bin/mount",
        "/bin/umount",
        "/usr/bin/pkexec",
    )
    _EXPECTED_SGID: ClassVar[tuple[str, ...]] = (
        "/usr/bin/wall",
        "/usr/bin/write",
        "/usr/bin/ssh-agent",
    )
    _FIND_HINTS: ClassVar[tuple[dict[str, str], ...]] = (
        {"purpose": "world-writable files", "command": "find <path> -xdev -type f -perm -0002"},
        {"purpose": "world-writable directories without the sticky bit", "command": "find <path> -xdev -type d -perm -0002 ! -perm -1000"},
        {"purpose": "setuid executables", "command": "find <path> -xdev -type f -perm -4000"},
        {"purpose": "setgid executables", "command": "find <path> -xdev -type f -perm -2000"},
        {"purpose": "files executable but not readable", "command": "find <path> -xdev -type f -perm /111 ! -perm -444"},
    )

    def execute(
        self,
        mode: str,
        mode_value: str | int | None = None,
        current_mode: str | int | None = None,
        operation: str | None = None,
        umask: str | int | None = None,
        target_mode: str | int | None = None,
        is_dir: bool = False,
    ) -> dict[str, Any]:
        """Run one of the five permission operations.

        Args:
            mode: operation selector: parse, chmod, umask_apply, review, invert.
            mode_value: permission mode (octal int/str like 754/'0754' or
                symbolic string like 'rwxr-x---'/'rwsr-x--t') for parse,
                umask_apply, review, and invert.
            current_mode: starting permission mode for chmod.
            operation: chmod operand ('u+x,go-w', 'a=rX', '=u', '754').
            umask: file-creation mask (octal like 022 or symbolic like
                'u=rwx,g=rx,o=') for umask_apply.
            target_mode: desired permission mode for invert.
            is_dir: whether the mode describes a directory; governs X and review.
        """
        try:
            selector = self._selector(mode)
            is_dir = self._bool(is_dir, "is_dir")
            if selector == "parse":
                return self._run_parse(mode_value)
            if selector == "chmod":
                return self._run_chmod(current_mode, operation, is_dir)
            if selector == "umask_apply":
                return self._run_umask_apply(mode_value, umask)
            if selector == "review":
                return self._run_review(mode_value, is_dir)
            return self._run_invert(mode_value, target_mode)
        except (TypeError, ValueError) as exc:
            error: dict[str, Any] = {"status": "error", "error_type": "validation_error", "error": str(exc)}
            findings = getattr(exc, "findings", None)
            if findings:
                error["findings"] = list(findings)
            return error

    # ------------------------------------------------------------------
    # Shared validation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _selector(value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("mode must be a string")
        selector = value.strip().lower()
        if selector not in {"parse", "chmod", "umask_apply", "review", "invert"}:
            raise ValueError("mode must be parse, chmod, umask_apply, review, or invert")
        return selector

    @staticmethod
    def _bool(value: Any, name: str) -> bool:
        if not isinstance(value, bool):
            raise TypeError(f"{name} must be a boolean")
        return value

    @staticmethod
    def _text(value: Any, name: str, cap: int) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{name} must be a string")
        text = value.strip()
        if not text:
            raise ValueError(f"{name} must be a non-empty string")
        if len(text) > cap:
            raise ValueError(f"{name} exceeds {cap} characters")
        return text

    def _octal_text(self, value: Any, name: str) -> str:
        """Normalize an octal int/str (754, '754', '0754') to a 3-4 digit string."""
        if isinstance(value, bool):
            raise ValueError(f"{name} must be octal digits, not a boolean")
        if isinstance(value, int):
            if value < 0:
                raise ValueError(f"{name} must not be negative")
            text = str(value)
        elif isinstance(value, str):
            text = value.strip()
        else:
            raise TypeError(f"{name} must be an int or string of octal digits")
        if not _OCTAL_RE.match(text):
            raise ValueError(f"{name} must be 3 or 4 octal digits (e.g. 754, '0754'), got {text!r}")
        return text

    def _parse_mode_value(self, value: Any, name: str) -> tuple[int, list[dict[str, Any]], str]:
        """Parse a permission mode into (mode, findings, input_kind)."""
        if isinstance(value, bool):
            raise ValueError(f"{name} must be a permission mode, not a boolean")
        if isinstance(value, int):
            text = self._octal_text(value, name)
            return int(text, 8), [], "octal"
        text = self._text(value, name, self.max_mode_length)
        if _OCTAL_RE.match(text):
            return int(text, 8), [], "octal"
        if len(text) == 9:
            return self._parse_symbolic(text, name)
        detail = f"{name} must be 3-4 octal digits or a 9-character symbolic mode, got {len(text)} characters"
        error = ValueError(f"{name} must be 3-4 octal digits or a 9-character symbolic mode like 'rwxr-x---', got {text!r}")
        error.findings = [{"issue": "wrong length", "detail": detail}]  # type: ignore[attr-defined]
        raise error

    def _parse_symbolic(self, text: str, name: str) -> tuple[int, list[dict[str, Any]], str]:
        """Decode a 9-character symbolic mode, collecting per-position findings."""
        mode = 0
        findings: list[dict[str, Any]] = []
        special_by_shift = {6: 0o4000, 3: 0o2000, 0: 0o1000}
        for position, char in enumerate(text):
            cls, bit, kind = _POSITIONS[position]
            shift = {"owner": 6, "group": 3, "other": 0}[cls]
            if char not in _EXPECTED_CHARS[kind]:
                findings.append(
                    {
                        "issue": "invalid character",
                        "position": position,
                        "character": char,
                        "class": cls,
                        "bit": bit,
                        "expected": list(_EXPECTED_CHARS[kind]),
                        "action": "treated as no permission for this position",
                    }
                )
                continue
            if char == "-":
                continue
            if char in ("r", "w"):
                mode |= (4 if char == "r" else 2) << shift
            elif char in ("x", "s", "S", "t", "T"):
                if char in ("x", "s", "t"):
                    mode |= 1 << shift
                if char in ("s", "S", "t", "T"):
                    mode |= special_by_shift[shift]
        return mode & 0o7777, findings, "symbolic"

    # ------------------------------------------------------------------
    # Breakdown rendering
    # ------------------------------------------------------------------

    def _breakdown(self, mode: int, findings: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        breakdown: dict[str, Any] = {
            "numeric": mode,
            "octal": format(mode & 0o777, "03o"),
            "octal4": format(mode, "04o"),
        }
        symbolic = []
        symbolic_special = []
        for cls, _, shift in _CLASSES:
            bits = (mode >> shift) & 7
            special_value = {"owner": 0o4000, "group": 0o2000, "other": 0o1000}[cls]
            has_special = bool(mode & special_value)
            for position, (bit, bit_value) in enumerate(_BITS):
                letter = ("r", "w", "x")[position] if bits & bit_value else "-"
                symbolic.append(letter)
                if position == 2 and has_special:
                    if bits & 1:
                        letter = "s" if cls in ("owner", "group") else "t"
                    else:
                        letter = "S" if cls in ("owner", "group") else "T"
                symbolic_special.append(letter)
            breakdown[cls] = {bit: bool(bits & value) for bit, value in _BITS}
        breakdown["symbolic"] = "".join(symbolic)
        breakdown["symbolic_with_special"] = "".join(symbolic_special)
        breakdown["special"] = {name: bool(mode & value) for name, value, _ in _SPECIALS}
        breakdown["value_per_class"] = {cls: (mode >> shift) & 7 for cls, _, shift in _CLASSES}
        breakdown["findings"] = findings if findings is not None else []
        return breakdown

    # ------------------------------------------------------------------
    # parse
    # ------------------------------------------------------------------

    def _run_parse(self, value: Any) -> dict[str, Any]:
        mode, findings, kind = self._parse_mode_value(value, "mode_value")
        result = self._breakdown(mode, findings)
        result.update({"status": "success", "operation": "parse", "input_kind": kind})
        return result

    # ------------------------------------------------------------------
    # chmod operand evaluation
    # ------------------------------------------------------------------

    def _parse_operand(self, value: Any) -> list[str]:
        text = self._text(value, "operation", self.max_operation_length)
        # No whitespace anywhere inside the operand, matching the real chmod
        # grammar: 'u+x, g-w' is invalid exactly as 'u +x' is. Only the
        # uniform outer input strip of _text applies.
        clauses = text.split(",")
        if len(clauses) > self.max_clauses:
            raise ValueError(f"operation accepts at most {self.max_clauses} comma-separated clauses")
        for clause in clauses:
            if not clause:
                raise ValueError("operation contains an empty clause")
            if not _CLAUSE_RE.match(clause):
                raise ValueError(f"invalid chmod clause {clause!r}: expected [ugoa]*[+-=][rwxXstugo]*")
        return clauses

    def _resolve_perm_value(
        self,
        who: str,
        op: str,
        perms: str,
        mode: int,
        x_reference_exec: bool,
        is_dir: bool,
        notes: list[str],
    ) -> tuple[int, int]:
        """Resolve one clause into (who-masked perm bits, '=' clear mask).

        The clear mask is who's own mask, except that copy sources (=u, =g, =o)
        clear only the nine permission bits: copying class bits never touches
        setuid/setgid, matching the real chmod.
        """
        mask = _WHO_MASKS["a"] if not who else 0
        for letter in who:
            mask |= _WHO_MASKS[letter]
        if perms in ("u", "g", "o"):
            if op != "=":
                raise ValueError(f"copy source '{perms}' is valid only with '=' (clause who={who!r}, op={op!r})")
            shift = {"u": 6, "g": 3, "o": 0}[perms]
            bits = (mode >> shift) & 7
            replicated = (bits << 6) | (bits << 3) | bits
            notes.append(f"copy source '={perms}' copies the class bits visible after earlier clauses ({bits:o}); special bits are untouched")
            return replicated & mask, mask & 0o0777
        if len(set(perms)) != len(perms):
            raise ValueError(f"duplicate permission letters in {perms!r}")
        if len(perms) > 1 and any(letter in "ugo" for letter in perms):
            raise ValueError(f"copy letters u/g/o must stand alone as the permission list, got {perms!r}")
        value = 0
        for letter in perms:
            if letter == "X":
                if is_dir or x_reference_exec:
                    value |= 0o111
                continue
            value |= _PERM_BITS[letter]
        value &= mask
        if "X" in perms:
            if is_dir:
                notes.append("X: is_dir=true, so X grants or removes execute for the listed who")
            else:
                notes.append(
                    "X: no is_dir knowledge, so X applies only when an execute bit is already set "
                    "in the mode before the operation (execute-if-any-execute-present)"
                )
        if "s" in perms and not value & 0o6000:
            notes.append("s ignored: who lists neither u nor g, so there is no setuid/setgid target")
        if "t" in perms and not value & 0o1000:
            notes.append("t ignored: the sticky bit is addressed only when who is 'a' or omitted")
        return value, mask

    def _apply_operation(self, current: int, operand: str, is_dir: bool) -> tuple[int, list[dict[str, Any]], list[str]]:
        clauses = self._parse_operand(operand)
        mode = current & 0o7777
        x_reference_exec = bool(current & 0o111)
        changes: list[dict[str, Any]] = []
        notes: list[str] = []
        for clause in clauses:
            match = _CLAUSE_RE.match(clause)
            assert match is not None
            who, op, perms = match.groups()
            if len(set(who)) != len(who):
                raise ValueError(f"duplicate who letters in {who!r}")
            if not who:
                notes.append(
                    "clause omits who: applies to all classes (a); the umask is never consulted "
                    "(chmod is not open(2) creation)"
                )
            if op in ("+", "-") and not perms:
                raise ValueError(f"clause {clause!r} lists no permission after {op!r}; an empty permission list is valid only with '='")
            value, clear_mask = self._resolve_perm_value(who, op, perms, mode, x_reference_exec, is_dir, notes)
            before = mode
            if op == "+":
                mode |= value
            elif op == "-":
                mode &= ~value
            else:
                mode = (mode & ~clear_mask) | value
            changes.append(
                {
                    "clause": clause,
                    "who": who or "a",
                    "op": op,
                    "perms": perms,
                    "perm_bits_before": format(before, "04o"),
                    "perm_bits_after": format(mode, "04o"),
                    "x_condition_met": (is_dir or x_reference_exec) if "X" in perms else None,
                }
            )
        return mode & 0o7777, changes, notes

    def _run_chmod(self, current: Any, operand: Any, is_dir: bool) -> dict[str, Any]:
        start, _, _ = self._parse_mode_value(current, "current_mode")
        text = self._text(operand, "operation", self.max_operation_length)
        if _OCTAL_RE.match(text):
            final = int(text, 8)
            changes = [
                {
                    "clause": text,
                    "who": "a",
                    "op": "=",
                    "perms": format(final & 0o7777, "04o"),
                    "perm_bits_before": format(start, "04o"),
                    "perm_bits_after": format(final, "04o"),
                    "x_condition_met": None,
                }
            ]
            notes = ["numeric operand: the mode is set absolutely (0o0000-0o7777)"]
        else:
            final, changes, notes = self._apply_operation(start, text, is_dir)
        seen: set[str] = set()
        ordered_notes = [note for note in notes if not (note in seen or seen.add(note))]
        return {
            "status": "success",
            "operation": "chmod",
            "is_dir": is_dir,
            "operand": text,
            "current_mode": format(start, "04o"),
            "new_mode": self._breakdown(final),
            "changes": changes,
            "notes": ordered_notes,
        }

    # ------------------------------------------------------------------
    # umask application
    # ------------------------------------------------------------------

    def _resolve_umask(self, value: Any) -> tuple[int, dict[str, Any]]:
        """Resolve an octal or symbolic umask to the 9-bit mask value."""
        info: dict[str, Any] = {}
        if isinstance(value, bool):
            raise ValueError("umask must be octal digits or a symbolic mask, not a boolean")
        if isinstance(value, int) or (isinstance(value, str) and _OCTAL_RE.match(value.strip())):
            text = self._octal_text(value, "umask")
            mask = int(text, 8)
            if mask > 0o777:
                raise ValueError("umask only covers the nine permission bits; special bits are never granted at creation, so they cannot be masked")
            info["umask_kind"] = "octal"
            info["granted_bits"] = format(0o777 & ~mask, "03o")
            return mask, info
        text = self._text(value, "umask", self.max_operation_length)
        # Whitespace inside a symbolic mask is rejected, as by the sh umask
        # builtin; only the uniform outer input strip of _text applies.
        for clause in text.split(","):
            match = _CLAUSE_RE.match(clause)
            if not match:
                raise ValueError(f"invalid umask clause {clause!r}: expected [ugoa]*[+-=][rwx] clauses")
            who, op, perms = match.groups()
            if any(letter in perms for letter in "Xstugo"):
                raise ValueError(f"umask clause {clause!r} may only use the r, w, and x permission letters")
            if op in ("+", "-") and not perms:
                raise ValueError(f"umask clause {clause!r} lists no permission after {op!r}")
        allowed, _, _ = self._apply_operation(0o777, text, False)
        mask = 0o777 & ~allowed
        info["umask_kind"] = "symbolic"
        info["granted_bits"] = format(allowed, "03o")
        info["note"] = (
            "symbolic umask resolved against an all-granted base (equivalent to "
            "sh -c 'umask 0; umask <operand>; umask'); the mask is its complement"
        )
        return mask, info

    def _run_umask_apply(self, mode_value: Any, umask_value: Any) -> dict[str, Any]:
        mode, _, _ = self._parse_mode_value(mode_value, "mode_value")
        mask, info = self._resolve_umask(umask_value)
        result_mode = mode & ~mask & 0o7777
        bits_table = []
        for cls, _, shift in _CLASSES:
            for bit, position in (("read", 2), ("write", 1), ("execute", 0)):
                mode_bit = (mode >> (shift + position)) & 1
                mask_bit = (mask >> (shift + position)) & 1
                bits_table.append(
                    {
                        "class": cls,
                        "bit": bit,
                        "mode_bit": mode_bit,
                        "umask_bit": mask_bit,
                        "result_bit": 1 if mode_bit and not mask_bit else 0,
                    }
                )
        return {
            "status": "success",
            "operation": "umask_apply",
            "mode_octal4": format(mode, "04o"),
            "umask_octal": format(mask, "03o"),
            "umask_kind": info["umask_kind"],
            "granted_bits": info["granted_bits"],
            "explanation": "result = mode & ~umask (the mask clears creation bits; it never adds them)",
            "result": self._breakdown(result_mode),
            "bits": bits_table,
            **({"note": info["note"]} if "note" in info else {}),
        }

    # ------------------------------------------------------------------
    # security review
    # ------------------------------------------------------------------

    def _run_review(self, mode_value: Any, is_dir: bool) -> dict[str, Any]:
        mode, parse_findings, _ = self._parse_mode_value(mode_value, "mode_value")
        owner = (mode >> 6) & 7
        group = (mode >> 3) & 7
        other = mode & 7
        any_exec = bool(mode & 0o111)
        setuid = bool(mode & 0o4000)
        setgid = bool(mode & 0o2000)
        sticky = bool(mode & 0o1000)
        kind = "directory" if is_dir else "file"
        findings: list[dict[str, Any]] = []

        if mode == 0:
            findings.append(
                {
                    "id": "no_permissions",
                    "severity": "medium",
                    "summary": "mode 000 denies every access to every class",
                    "detail": "Only the owner via chmod (and root) can recover access; confirm the lockout is intentional.",
                }
            )
        if other & 2:
            if is_dir and sticky:
                findings.append(
                    {
                        "id": "world_writable_sticky_directory",
                        "severity": "info",
                        "summary": "world-writable directory protected by the sticky bit",
                        "detail": "The sanctioned shared-scratch pattern (as on /tmp): anyone may create entries, but the sticky bit restricts deletion to entry owners.",
                    }
                )
            elif is_dir:
                findings.append(
                    {
                        "id": "world_writable_directory_without_sticky",
                        "severity": "high",
                        "summary": "world-writable directory without the sticky bit",
                        "detail": "Any local user can delete or rename entries owned by others; add the sticky bit (o+t) if the directory must stay world-writable.",
                    }
                )
            else:
                detail = "Any local user can modify the content and, for executables, plant code."
                if sticky:
                    detail += " The sticky bit does not mitigate world-writable files."
                findings.append({"id": "world_writable_file", "severity": "high", "summary": "world-writable file", "detail": detail})
        if group & 2 and any_exec:
            findings.append(
                {
                    "id": "group_writable_executable",
                    "severity": "medium",
                    "summary": "executable that group members can rewrite",
                    "detail": "Anyone in the owning group can replace the code that other users execute; drop g-w unless the group is fully trusted.",
                }
            )
        if setuid:
            if any_exec:
                findings.append(
                    {
                        "id": "setuid_executable",
                        "severity": "medium",
                        "summary": "setuid executable",
                        "detail": "Runs with the file owner's privileges; expected on system binaries such as "
                        + ", ".join(self._EXPECTED_SUID)
                        + ", but investigate anything unexpected.",
                    }
                )
            else:
                findings.append({"id": "setuid_without_execute", "severity": "low", "summary": "setuid bit without any execute bit", "detail": "The bit is set but can never take effect."})
        if setgid:
            if any_exec:
                findings.append(
                    {
                        "id": "setgid_executable",
                        "severity": "medium",
                        "summary": "setgid executable",
                        "detail": "Runs with the owning group's privileges; expected on utilities such as "
                        + ", ".join(self._EXPECTED_SGID)
                        + ", but investigate anything unexpected.",
                    }
                )
            else:
                findings.append({"id": "setgid_without_execute", "severity": "low", "summary": "setgid bit without any execute bit", "detail": "The bit is set but can never take effect."})
        if other & 4:
            findings.append(
                {
                    "id": "world_readable",
                    "severity": "info",
                    "summary": "world-readable content",
                    "detail": "This review inspects mode bits only and never reads content; it cannot tell whether the bytes are sensitive, so confirm that no secrets are exposed.",
                }
            )
        exec_without_read = [cls for cls, bits in (("owner", owner), ("group", group), ("other", other)) if bits & 1 and not bits & 4]
        if exec_without_read:
            if is_dir:
                findings.append(
                    {
                        "id": "traverse_only_directory",
                        "severity": "info",
                        "summary": "directory classes with execute but not read",
                        "detail": f"Classes {', '.join(exec_without_read)} may traverse known entry names but not list them; a deliberate hide-but-reach pattern.",
                    }
                )
            else:
                findings.append(
                    {
                        "id": "execute_without_read",
                        "severity": "low",
                        "summary": "file classes with execute but not read",
                        "detail": f"Classes {', '.join(exec_without_read)} can run but not inspect the file; unusual for files (some tracing and loader setups fail on it).",
                    }
                )
        return {
            "status": "success",
            "operation": "review",
            "is_dir": is_dir,
            "kind": kind,
            "mode": self._breakdown(mode, parse_findings),
            "findings": findings,
            "hints": [dict(hint) for hint in self._FIND_HINTS],
            "hint_note": "find-style commands are read-only suggestions for a user to run elsewhere; this tool never executes them",
        }

    # ------------------------------------------------------------------
    # invert
    # ------------------------------------------------------------------

    @staticmethod
    def _perm_letters(bits: int) -> str:
        return "".join(letter for letter, value in (("r", 4), ("w", 2), ("x", 1)) if bits & value)

    def _run_invert(self, mode_value: Any, target_value: Any) -> dict[str, Any]:
        current, _, _ = self._parse_mode_value(mode_value, "mode_value")
        target, _, _ = self._parse_mode_value(target_value, "target_mode")
        per_class: list[tuple[str, str, str]] = []
        equal_classes: list[str] = []
        for letter, shift in (("u", 6), ("g", 3), ("o", 0)):
            now = (current >> shift) & 7
            want = (target >> shift) & 7
            if now == want:
                continue
            added = want & ~now
            removed = now & ~want
            if added and not removed:
                per_class.append((letter, "+", self._perm_letters(added)))
            elif removed and not added:
                per_class.append((letter, "-", self._perm_letters(removed)))
            else:
                equal_classes.append(letter)
                per_class.append((letter, "=", self._perm_letters(want)))
        clauses = list(per_class)
        # Sticky additions and removals must address who 'a': the sticky bit is
        # only reached when who includes o or a ('o+t' alone is a documented
        # no-op under the who-mask model this tool and BSD chmod share).
        for name, bit, perm_letter, who in (
            ("setuid", 0o4000, "s", "u"),
            ("setgid", 0o2000, "s", "g"),
            ("sticky", 0o1000, "t", "a"),
        ):
            now = bool(current & bit)
            want = bool(target & bit)
            equal_clears = (name == "setuid" and "u" in equal_classes) or (name == "setgid" and "g" in equal_classes)
            if now and not want:
                if not equal_clears:
                    clauses.append((who, "-", perm_letter))
            elif want and not now:
                clauses.append((who, "+", perm_letter))
            elif want and now and equal_clears:
                clauses.append((who, "+", perm_letter))
        grouped: dict[tuple[str, str], list[str]] = {}
        for letter, op, perms in clauses:
            grouped.setdefault((op, perms), []).append(letter)
        command = ",".join("".join(letters) + op + perms for (op, perms), letters in grouped.items())
        changed = current != target
        return {
            "status": "success",
            "operation": "invert",
            "current_octal4": format(current, "04o"),
            "target_octal4": format(target, "04o"),
            "changed": changed,
            "command": command,
            "clauses": ["".join(letters) + op + perms for (op, perms), letters in grouped.items()],
            "target": self._breakdown(target),
            "note": "deterministic simplest form: classes sharing the same op and permissions are merged; = is used only when a class both gains and loses bits",
        }
