#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/20
# @Author  : agentUniverse contributors
# @FileName: matrix_ops_tool.py

"""2-D numeric matrix operations built purely on the stdlib.

Addresses the *other tools* item of issue #252 (tool plug-in
integration) with a zero-network, zero-dependency matrix utility agents
can call for small linear-algebra plumbing: inspecting shapes, rotating
tables, scaling values, multiplying matrices, computing exact
determinants of integer matrices and flattening 2-D data to 1-D —
without pulling in numpy.

The tool supports seven modes:

* ``info`` — rows, columns, shape, entry count, squareness, symmetry
  within a tolerance, the main diagonal (the first ``min(rows, cols)``
  entries, numpy-style) and its trace.
* ``transpose`` — main-diagonal transpose, or reflection across the
  anti-diagonal when ``anti=True`` (equivalent to rotating 180 degrees
  and then transposing).
* ``rotate`` — clockwise rotation by 90 / 180 / 270 degrees; 270
  clockwise equals 90 counter-clockwise.
* ``scale`` — element-wise scaling, either multiply-by-``scalar``
  (default) or add-``scalar``.
* ``multiply`` — matrix-times-matrix product with dimension
  validation, or element-wise multiplication when ``other`` is a
  single number (the scalar shortcut).
* ``determinant`` — square matrices only, computed by Laplace cofactor
  expansion: exact ``fractions.Fraction`` arithmetic whenever every
  entry is an integer (the result is always an exact integer in that
  case, however large), float arithmetic when any entry is a float,
  and Gaussian elimination with partial pivoting for matrices larger
  than 12x12. Both float paths are documented approximations that may
  differ from the exact determinant.
* ``flatten`` — reduce to a 1-D list in row-major, column-major or
  zigzag order (JPEG-style: anti-diagonals from the top-left, odd ones
  traversed top-to-bottom, even ones bottom-to-top).

The ``matrix`` argument accepts either a JSON 2-D array (a list of
lists of numbers, or a string holding JSON) or row-per-line
whitespace-separated text such as ``"1 2 3\n4 5 6"``. Entries must be
finite numbers; Python booleans are rejected even though ``bool`` is
an ``int`` subclass. Matrices are capped at 100 rows x 100 columns.

Input validation is strict and happens before any computation:
malformed parameters (unknown mode / rotation degrees / flatten order
/ scale type, a non-numeric or non-finite ``scalar``, a negative
``tolerance``, a missing or non-matrix ``matrix``, more than 100
rows) raise a ``ValueError``, mirroring the other common tools.
Errors that depend on the *content being processed* — ragged rows,
empty rows, rows that are not lists, non-numeric / boolean / NaN /
infinity entries, invalid JSON, non-numeric text tokens, more than
100 columns, non-square determinants and mismatched multiplication
dimensions — are returned as a structured ``error`` payload so an
agent can react without catching exceptions. All row and column
indices in error messages are 1-based.
"""

import json
import math
import re
from fractions import Fraction
from typing import Any, ClassVar, Dict, List, Tuple

from pydantic import ConfigDict

from agentuniverse.agent.action.tool.tool import Tool

_INT_TOKEN = re.compile(r"\A[+-]?\d+\Z")
_FLOAT_TOKEN = re.compile(r"\A[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\Z")


class _MatrixContentError(Exception):
    """Internal carrier for content-level failures rendered as payloads."""

    def __init__(self, error_type: str, message: str) -> None:
        super().__init__(message)
        self.error_type = error_type
        self.message = message


class MatrixOpsTool(Tool):
    """2-D numeric matrix operations built purely on the stdlib.

    Attributes:
        max_rows (int): Upper bound on the number of matrix rows.
        max_cols (int): Upper bound on the number of matrix columns.
        max_cofactor_size (int): Largest size computed by cofactor
            expansion; larger matrices fall back to float Gaussian
            elimination.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, protected_namespaces=()
    )

    name: str = "matrix_ops_tool"
    description: str = (
        "Matrix operations tool — pure Python stdlib, no numpy "
        "required. 2-D numeric matrix info: shape, squareness, "
        "symmetry within a tolerance, diagonal and trace "
        "(mode='info'); transpose with an anti-diagonal option "
        "(mode='transpose'); 90/180/270-degree clockwise rotation "
        "(mode='rotate'); element-wise scale by xk or +k "
        "(mode='scale'); matrix x matrix with dimension validation "
        "and a scalar shortcut (mode='multiply'); determinants via "
        "exact Fraction cofactor expansion for integer matrices with "
        "a documented floating-point fallback (mode='determinant'); "
        "and row-major / column-major / zigzag flattening "
        "(mode='flatten'). Input is a JSON 2-D array or row-per-line "
        "whitespace-separated text."
    )

    MODES: ClassVar[tuple] = (
        "info",
        "transpose",
        "rotate",
        "scale",
        "multiply",
        "determinant",
        "flatten",
    )
    ROTATE_DEGREES: ClassVar[tuple] = (90, 180, 270)
    FLATTEN_ORDERS: ClassVar[tuple] = ("row-major", "column-major", "zigzag")
    SCALE_TYPES: ClassVar[tuple] = ("multiply", "add")

    max_rows: ClassVar[int] = 100
    max_cols: ClassVar[int] = 100
    max_cofactor_size: ClassVar[int] = 12
    default_tolerance: ClassVar[float] = 1e-9

    # ------------------------------------------------------------------ #
    # Public entry point
    # ------------------------------------------------------------------ #

    def execute(
        self,
        mode: str,
        matrix: Any = None,
        other: Any = None,
        scalar: Any = None,
        scale_type: Any = None,
        degrees: Any = None,
        order: Any = None,
        anti: Any = None,
        tolerance: Any = None,
    ) -> Dict[str, Any]:
        """Run one matrix operation.

        Args:
            mode (str): One of ``info`` / ``transpose`` / ``rotate`` /
                ``scale`` / ``multiply`` / ``determinant`` /
                ``flatten``.
            matrix (list | tuple | str): The matrix to operate on — a
                2-D array of numbers (list of lists), a string holding
                a JSON 2-D array, or row-per-line whitespace-separated
                text. Required for every mode.
            other (list | tuple | str | number): Multiply mode only —
                the right operand: a matrix in any accepted format or
                a single finite number for the scalar shortcut.
            scalar (number): Scale mode only — a finite number to
                multiply by (default) or add to every entry.
            scale_type (str): Scale mode only — ``multiply`` (default)
                or ``add``.
            degrees (int | str): Rotate mode only — ``90``, ``180`` or
                ``270`` (clockwise).
            order (str): Flatten mode only — ``row-major`` (default),
                ``column-major`` or ``zigzag``.
            anti (bool): Transpose mode only — reflect across the
                anti-diagonal instead of the main diagonal.
            tolerance (number): Info mode only — maximum absolute
                difference allowed between mirrored entries when
                checking symmetry (default 1e-9).

        Returns:
            Dict[str, Any]: The operation result (always a ``result``
                value plus the call context) or a structured ``error``
                payload for content-level failures (ragged rows,
                non-numeric or non-finite entries, invalid text or
                JSON, non-square determinants, dimension mismatches).

        Raises:
            ValueError: If any parameter is malformed (before any
                computation happens).
        """
        if mode not in self.MODES:
            self._invalid(
                f"mode must be one of: {', '.join(self.MODES)} (got {mode!r})"
            )
        # Parameter-level validation happens up front so a malformed
        # selector never reaches the content parser.
        if anti is not None and not isinstance(anti, bool):
            self._invalid(f"anti must be a boolean (got {anti!r})")
        if degrees is not None and not self._valid_degrees(degrees):
            self._invalid(
                "degrees must be one of: "
                f"{', '.join(str(d) for d in self.ROTATE_DEGREES)} "
                f"(clockwise; got {degrees!r})"
            )
        if order is not None and order not in self.FLATTEN_ORDERS:
            self._invalid(
                "order must be one of: "
                f"{', '.join(self.FLATTEN_ORDERS)} (got {order!r})"
            )
        if scale_type is not None and scale_type not in self.SCALE_TYPES:
            self._invalid(
                "scale_type must be one of: "
                f"{', '.join(self.SCALE_TYPES)} (got {scale_type!r})"
            )
        if mode == "scale":
            scalar = self._validate_scalar(scalar)
        if mode == "rotate" and degrees is None:
            self._invalid(
                "degrees is required for rotate mode — one of: "
                f"{', '.join(str(d) for d in self.ROTATE_DEGREES)} "
                "(clockwise)"
            )
        if mode == "info":
            tolerance = self._validate_tolerance(tolerance)
        if mode == "multiply" and other is None:
            self._invalid(
                "other is required for multiply mode — a matrix in any "
                "accepted format or a single number for the scalar "
                "shortcut"
            )

        try:
            clean_matrix = self._parse_matrix(matrix)
            if mode == "info":
                return self._run_info(clean_matrix, tolerance)
            if mode == "transpose":
                return self._run_transpose(clean_matrix, bool(anti))
            if mode == "rotate":
                return self._run_rotate(clean_matrix, int(degrees))
            if mode == "scale":
                return self._run_scale(clean_matrix, scalar, scale_type)
            if mode == "multiply":
                return self._run_multiply(clean_matrix, other)
            if mode == "determinant":
                return self._run_determinant(clean_matrix)
            return self._run_flatten(clean_matrix, order)
        except _MatrixContentError as exc:
            return self._error_result(
                {"mode": mode}, exc.error_type, exc.message
            )

    # ------------------------------------------------------------------ #
    # Input validation (pure — raises before any computation)
    # ------------------------------------------------------------------ #

    @classmethod
    def _invalid(cls, message: str) -> None:
        """Raise the standard input-validation error."""
        raise ValueError(f"matrix_ops_tool: {message}")

    @classmethod
    def _is_number(cls, value: Any) -> bool:
        """True for finite ints / floats — booleans never count."""
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        if isinstance(value, int):
            return True
        return math.isfinite(value)

    @classmethod
    def _valid_degrees(cls, degrees: Any) -> bool:
        """Accept 90 / 180 / 270 as ints or numeric strings."""
        if isinstance(degrees, bool):
            return False
        if isinstance(degrees, int):
            return degrees in cls.ROTATE_DEGREES
        if isinstance(degrees, str) and degrees.strip() in (
            str(d) for d in cls.ROTATE_DEGREES
        ):
            return True
        return False

    @classmethod
    def _validate_scalar(cls, scalar: Any) -> float:
        """Validate the scale-mode ``scalar`` factor."""
        if not cls._is_number(scalar):
            cls._invalid(f"scalar must be a finite number (got {scalar!r})")
        return scalar

    @classmethod
    def _validate_tolerance(cls, tolerance: Any) -> float:
        """Validate the info-mode symmetry ``tolerance``."""
        if tolerance is None:
            return cls.default_tolerance
        if not cls._is_number(tolerance) or tolerance < 0:
            cls._invalid(
                "tolerance must be a non-negative finite number "
                f"(got {tolerance!r})"
            )
        return tolerance

    @staticmethod
    def _fraction_to_float(exact: Fraction) -> float:
        """Convert exactly, mapping beyond-range magnitudes to ±inf."""
        try:
            return float(exact)
        except OverflowError:
            return math.inf if exact > 0 else -math.inf

    @classmethod
    def _to_float(cls, value: Any) -> float:
        """float() that survives ints too large for a double."""
        return cls._fraction_to_float(Fraction(value))

    @classmethod
    def _arith(cls, left: Any, right: Any, op: str) -> Any:
        """Add / subtract / multiply with a huge-int-safe fallback.

        Mixed int/float arithmetic raises OverflowError once the int
        cannot convert to a double; the fallback recomputes the exact
        value with Fractions and maps it to the nearest float (±inf
        when the magnitude exceeds the double range, mirroring pure
        float overflow).
        """
        try:
            if op == "add":
                return left + right
            if op == "sub":
                return left - right
            return left * right
        except OverflowError:
            exact = Fraction(left)
            if op == "add":
                exact += Fraction(right)
            elif op == "sub":
                exact -= Fraction(right)
            else:
                exact *= Fraction(right)
            return cls._fraction_to_float(exact)

    # ------------------------------------------------------------------ #
    # Matrix parsing (content-level failures become structured errors)
    # ------------------------------------------------------------------ #

    @classmethod
    def _parse_matrix(cls, matrix: Any) -> List[List[Any]]:
        """Normalize any accepted input format to a list of row lists.

        Raises ``ValueError`` for parameter-level problems (wrong
        container type, empty input, too many rows) and
        ``_MatrixContentError`` for content-level ones (rows that are
        not lists, empty rows, ragged rows, over-long rows, entries
        that are not finite numbers).
        """
        if matrix is None:
            cls._invalid("matrix is required (got None)")
        if isinstance(matrix, bool) or not isinstance(matrix, (str, list, tuple)):
            cls._invalid(
                "matrix must be a 2-D array of numbers, a JSON array "
                f"string or row-per-line text (got {matrix!r})"
            )
        rows_raw: List[Any]
        if isinstance(matrix, str):
            rows_raw = cls._parse_matrix_text(matrix)
        else:
            rows_raw = list(matrix)
        if not rows_raw:
            cls._invalid("matrix must not be empty (got no rows)")
        if len(rows_raw) > cls.max_rows:
            cls._invalid(
                f"matrix exceeds the {cls.max_rows}-row limit "
                f"(got {len(rows_raw)} rows)"
            )
        return cls._scan_rows(rows_raw)

    @classmethod
    def _parse_matrix_text(cls, text: str) -> List[List[Any]]:
        """Parse a matrix given as text (JSON array or row-per-line)."""
        stripped = text.strip()
        if not stripped:
            cls._invalid("matrix must not be empty (got '')")
        if stripped.startswith(("[", "{")):
            try:
                parsed = json.loads(stripped)
            except ValueError as exc:
                raise _MatrixContentError(
                    "invalid_json",
                    "matrix string looks like JSON but is not valid "
                    f"JSON: {exc} (got {stripped[:64]!r})",
                )
            if not isinstance(parsed, list):
                raise _MatrixContentError(
                    "invalid_json",
                    "matrix string is valid JSON but not a 2-D numeric "
                    f"array (got {type(parsed).__name__}: "
                    f"{repr(parsed)[:60]})",
                )
            return parsed
        lines = [line for line in text.splitlines() if line.strip()]
        if len(lines) > cls.max_rows:
            cls._invalid(
                f"matrix exceeds the {cls.max_rows}-row limit "
                f"(got {len(lines)} rows)"
            )
        rows: List[List[Any]] = []
        for row_index, line in enumerate(lines, start=1):
            row: List[Any] = []
            for token in line.split():
                if _INT_TOKEN.match(token):
                    row.append(int(token))
                elif _FLOAT_TOKEN.match(token):
                    value = float(token)
                    if not math.isfinite(value):
                        raise _MatrixContentError(
                            "non_finite_entry",
                            "text row "
                            f"{row_index} (1-based) contains a value that "
                            f"is not finite (got {token!r})",
                        )
                    row.append(value)
                else:
                    raise _MatrixContentError(
                        "invalid_matrix_text",
                        f"text row {row_index} (1-based), token {token!r} "
                        "is not a numeric value; rows must be "
                        "whitespace-separated integers or decimals "
                        "(e.g. '1 -2.5 3e-2')",
                    )
            rows.append(row)
        return rows

    @classmethod
    def _scan_rows(cls, rows_raw: List[Any]) -> List[List[Any]]:
        """Validate row shapes and entries; return clean rows."""
        cols = None
        clean: List[List[Any]] = []
        for row_index, row in enumerate(rows_raw, start=1):
            if isinstance(row, bool) or not isinstance(row, (list, tuple)):
                raise _MatrixContentError(
                    "invalid_matrix",
                    f"row {row_index} (1-based) must be a list of "
                    f"numbers (got {type(row).__name__}: {repr(row)[:60]})",
                )
            entries = list(row)
            if not entries:
                raise _MatrixContentError(
                    "invalid_matrix",
                    f"row {row_index} (1-based) is empty — every row "
                    "needs at least one column",
                )
            if cols is None:
                cols = len(entries)
                if cols > cls.max_cols:
                    raise _MatrixContentError(
                        "matrix_too_large",
                        f"row {row_index} has {cols} columns; matrices are"
                        f" capped at {cls.max_rows} rows x {cls.max_cols}"
                        " columns",
                    )
            elif len(entries) != cols:
                raise _MatrixContentError(
                    "invalid_matrix",
                    f"ragged matrix: row 1 has {cols} columns but row "
                    f"{row_index} has {len(entries)} (row indices are "
                    "1-based)",
                )
            clean_row: List[Any] = []
            for col_index, value in enumerate(entries, start=1):
                if isinstance(value, bool):
                    raise _MatrixContentError(
                        "non_numeric_entry",
                        f"matrix entry (row {row_index}, col {col_index}, "
                        "1-based) must be a number — booleans are not "
                        f"accepted (got {value!r})",
                    )
                if not isinstance(value, (int, float)):
                    raise _MatrixContentError(
                        "non_numeric_entry",
                        f"matrix entry (row {row_index}, col {col_index}, "
                        "1-based) must be a number (got "
                        f"{type(value).__name__}: {repr(value)[:60]})",
                    )
                if isinstance(value, float) and not math.isfinite(value):
                    raise _MatrixContentError(
                        "non_finite_entry",
                        f"matrix entry (row {row_index}, col {col_index}, "
                        f"1-based) is not finite (got {value!r})",
                    )
                clean_row.append(value)
            clean.append(clean_row)
        return clean

    # ------------------------------------------------------------------ #
    # Mode runners
    # ------------------------------------------------------------------ #

    def _run_info(
        self, mat: List[List[Any]], tolerance: float
    ) -> Dict[str, Any]:
        """Report shape, squareness, symmetry, diagonal and trace."""
        rows, cols = len(mat), len(mat[0])
        symmetric = rows == cols and all(
            abs(self._arith(mat[i][j], mat[j][i], "sub")) <= tolerance
            for i in range(rows)
            for j in range(cols)
        )
        diagonal = [mat[i][i] for i in range(min(rows, cols))]
        trace: Any = 0
        for value in diagonal:
            trace = self._arith(trace, value, "add")
        return {
            "mode": "info",
            "rows": rows,
            "cols": cols,
            "shape": [rows, cols],
            "size": rows * cols,
            "square": rows == cols,
            "symmetric": symmetric,
            "tolerance": tolerance,
            "diagonal": diagonal,
            "trace": trace,
        }

    def _run_transpose(
        self, mat: List[List[Any]], anti: bool
    ) -> Dict[str, Any]:
        """Transpose across the main or the anti diagonal."""
        rows, cols = len(mat), len(mat[0])
        if anti:
            result = [
                [mat[rows - 1 - j][cols - 1 - i] for j in range(rows)]
                for i in range(cols)
            ]
        else:
            result = [
                [mat[r][c] for r in range(rows)] for c in range(cols)
            ]
        return {
            "mode": "transpose",
            "anti": anti,
            "shape": [cols, rows],
            "result": result,
        }

    def _run_rotate(
        self, mat: List[List[Any]], degrees: int
    ) -> Dict[str, Any]:
        """Rotate clockwise by 90 / 180 / 270 degrees."""
        rows, cols = len(mat), len(mat[0])
        if degrees == 90:
            result = [
                [mat[rows - 1 - r][c] for r in range(rows)]
                for c in range(cols)
            ]
        elif degrees == 180:
            result = [row[::-1] for row in mat[::-1]]
        else:  # 270 clockwise == 90 counter-clockwise
            result = [
                [mat[r][cols - 1 - c] for r in range(rows)]
                for c in range(cols)
            ]
        return {
            "mode": "rotate",
            "degrees": degrees,
            "direction": "clockwise",
            "shape": [len(result), len(result[0])],
            "result": result,
        }

    def _run_scale(
        self, mat: List[List[Any]], scalar: Any, scale_type: Any
    ) -> Dict[str, Any]:
        """Scale every entry by xk (default) or +k."""
        if scale_type is None:
            scale_type = "multiply"
        op = "mul" if scale_type == "multiply" else "add"
        result = [
            [self._arith(value, scalar, op) for value in row] for row in mat
        ]
        return {
            "mode": "scale",
            "scale_type": scale_type,
            "scalar": scalar,
            "result": result,
        }

    def _run_multiply(
        self, mat: List[List[Any]], other: Any
    ) -> Dict[str, Any]:
        """Matrix x matrix product, or element-wise x scalar shortcut."""
        a_rows, a_cols = len(mat), len(mat[0])
        if self._is_number(other):
            return {
                "mode": "multiply",
                "kind": "scalar",
                "scalar": other,
                "shape": [a_rows, a_cols],
                "result": [
                    [self._arith(value, other, "mul") for value in row]
                    for row in mat
                ],
            }
        if isinstance(other, bool) or not isinstance(other, (str, list, tuple)):
            self._invalid(
                "other must be a matrix in any accepted format or a "
                f"single finite number (got {other!r})"
            )
        other_matrix = self._parse_matrix(other)
        b_rows, b_cols = len(other_matrix), len(other_matrix[0])
        if a_cols != b_rows:
            return self._error_result(
                {"mode": "multiply", "kind": "matrix"},
                error_type="dimension_mismatch",
                message=(
                    "cannot multiply a "
                    f"{a_rows}x{a_cols} matrix by a {b_rows}x{b_cols} "
                    f"matrix: the left matrix has {a_cols} columns but "
                    f"the right matrix has {b_rows} rows"
                ),
            )
        result: List[List[Any]] = []
        for i in range(a_rows):
            row: List[Any] = []
            for j in range(b_cols):
                try:
                    row.append(
                        sum(
                            mat[i][k] * other_matrix[k][j]
                            for k in range(a_cols)
                        )
                    )
                except OverflowError:
                    row.append(
                        self._fraction_to_float(
                            sum(
                                (
                                    Fraction(mat[i][k])
                                    * Fraction(other_matrix[k][j])
                                    for k in range(a_cols)
                                ),
                                Fraction(0),
                            )
                        )
                    )
            result.append(row)
        return {
            "mode": "multiply",
            "kind": "matrix",
            "a_shape": [a_rows, a_cols],
            "b_shape": [b_rows, b_cols],
            "shape": [a_rows, b_cols],
            "result": result,
        }

    def _run_determinant(self, mat: List[List[Any]]) -> Dict[str, Any]:
        """Determinant of a square matrix (see module docstring)."""
        rows, cols = len(mat), len(mat[0])
        if rows != cols:
            return self._error_result(
                {"mode": "determinant"},
                error_type="not_square",
                message=(
                    "determinant requires a square matrix (got "
                    f"{rows} rows x {cols} columns)"
                ),
            )
        all_int = all(
            isinstance(value, int) for row in mat for value in row
        )
        payload: Dict[str, Any] = {"mode": "determinant", "size": rows}
        if rows <= self.max_cofactor_size and all_int:
            work = [[Fraction(value) for value in row] for row in mat]
            det = self._det_cofactor(work)
            payload["method"] = "cofactor_fraction"
            payload["exact"] = True
            payload["result"] = (
                det.numerator if det.denominator == 1 else str(det)
            )
            payload["value_float"] = self._to_float(det)
        elif rows <= self.max_cofactor_size:
            work = [[self._to_float(value) for value in row] for row in mat]
            det = self._det_cofactor(work)
            payload["method"] = "cofactor_float"
            payload["exact"] = False
            payload["result"] = det
            payload["value_float"] = det
        else:
            det = self._det_gaussian(mat)
            payload["method"] = "gaussian_float"
            payload["exact"] = False
            payload["result"] = det
            payload["value_float"] = det
        if not payload["exact"]:
            payload["note"] = (
                "computed in floating-point arithmetic — the result is "
                "an approximation and may differ from the exact "
                "determinant"
            )
        return payload

    def _run_flatten(
        self, mat: List[List[Any]], order: Any
    ) -> Dict[str, Any]:
        """Flatten to 1-D in row-major, column-major or zigzag order."""
        if order is None:
            order = "row-major"
        rows, cols = len(mat), len(mat[0])
        if order == "row-major":
            flat = [value for row in mat for value in row]
        elif order == "column-major":
            flat = [
                mat[r][c] for c in range(cols) for r in range(rows)
            ]
        else:  # zigzag — JPEG-style anti-diagonal scan
            flat = []
            for s in range(rows + cols - 1):
                lo = max(0, s - cols + 1)
                hi = min(s, rows - 1)
                row_range = range(lo, hi + 1)
                if s % 2 == 0:
                    row_range = reversed(list(row_range))
                for r in row_range:
                    flat.append(mat[r][s - r])
        return {
            "mode": "flatten",
            "order": order,
            "shape": [rows, cols],
            "length": len(flat),
            "result": flat,
        }

    # ------------------------------------------------------------------ #
    # Determinant kernels
    # ------------------------------------------------------------------ #

    @staticmethod
    def _det_cofactor(rows: List[List[Any]]) -> Any:
        """Laplace cofactor expansion with memoized minors.

        Expands along the top row of each submatrix; the memo keyed on
        the tuple of remaining column indices keeps the cost at
        O(2^n * n) instead of the naive O(n!) recursion. ``rows`` must
        already be uniformly int/Fraction or uniformly float.
        """
        n = len(rows)
        memo: Dict[Tuple[int, ...], Any] = {}

        def det_of(cols: Tuple[int, ...]) -> Any:
            if len(cols) == 1:
                return rows[n - 1][cols[0]]
            cached = memo.get(cols)
            if cached is not None:
                return cached
            r = n - len(cols)
            total = rows[r][cols[0]] * det_of(cols[1:])
            for pos in range(1, len(cols)):
                term = rows[r][cols[pos]] * det_of(cols[:pos] + cols[pos + 1:])
                total = total + term if pos % 2 == 0 else total - term
            memo[cols] = total
            return total

        return det_of(tuple(range(n)))

    @classmethod
    def _det_gaussian(cls, rows: List[List[Any]]) -> float:
        """Determinant by Gaussian elimination with partial pivoting."""
        n = len(rows)
        a = [[cls._to_float(value) for value in row] for row in rows]
        det = 1.0
        for i in range(n):
            pivot = i
            best = abs(a[i][i])
            for r in range(i + 1, n):
                if abs(a[r][i]) > best:
                    best = abs(a[r][i])
                    pivot = r
            if best == 0.0:
                return 0.0
            if pivot != i:
                a[i], a[pivot] = a[pivot], a[i]
                det = -det
            det *= a[i][i]
            for r in range(i + 1, n):
                factor = a[r][i] / a[i][i]
                for c in range(i + 1, n):
                    a[r][c] -= factor * a[i][c]
        return det

    # ------------------------------------------------------------------ #
    # Error payloads (structured, returned instead of raising)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _error_result(
        context: Dict[str, Any], error_type: str, message: str
    ) -> Dict[str, Any]:
        """Build a structured error payload."""
        return {
            **context,
            "error": {"type": error_type, "message": str(message)[:500]},
        }
