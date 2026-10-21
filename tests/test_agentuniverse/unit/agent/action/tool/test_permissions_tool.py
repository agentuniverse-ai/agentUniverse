"""Oracle-backed tests for PermissionsTool.

Ground truth comes from the real system: os.chmod/os.stat/st_mode for mode
representations, the operating system's POSIX chmod via subprocess for operand
evaluation (run with umask 0 so who-omitted clauses mean 'a' on every
platform), and os.umask round-trips for mask application. Subprocesses appear
only in these tests; the tool itself is stdlib-only and never spawns processes.
"""

import os
import random
import shutil
import stat as stat_module
import subprocess
import tempfile
import unittest

from agentuniverse.agent.action.tool.common_tool import permissions_tool as permissions_module
from agentuniverse.agent.action.tool.common_tool.permissions_tool import PermissionsTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(permissions_module.__file__), "permissions_tool.yaml")
CHMOD_BIN = "/bin/chmod"
WHO_CHOICES = ["", "u", "g", "o", "ug", "go", "uo", "ugo", "a"]
PERM_ORDER = "rwxXst"


def real_chmod(path, operand):
    """Apply a chmod operand with umask 0 and return the resulting 12-bit mode."""
    previous = os.umask(0)
    try:
        result = subprocess.run([CHMOD_BIN, operand, path], capture_output=True, text=True)
    finally:
        os.umask(previous)
    if result.returncode != 0:
        raise AssertionError(f"real chmod rejected operand {operand!r}: {result.stderr.strip()}")
    return os.stat(path).st_mode & 0o7777


def setgid_capable(directory):
    """Report whether this user may set the setgid bit inside directory."""
    probe = os.path.join(directory, "capability-probe")
    with open(probe, "w") as stream:
        stream.write("x")
    try:
        os.chmod(probe, 0o2755)
        return True
    except PermissionError:
        return False


class PermissionsToolTestBase(unittest.TestCase):
    """Shared fixtures: a temp directory and one fresh file per oracle case."""

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.mkdtemp(prefix="permissions-tool-")
        cls.capable = setgid_capable(cls.directory)
        cls.counter = 0

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.directory, ignore_errors=True)

    @classmethod
    def fixture(cls, mode, as_dir=False):
        """Create a fresh fixture with the given mode and return (path, mode)."""
        cls.counter += 1
        if not cls.capable:
            mode &= ~0o2000
        path = os.path.join(cls.directory, f"fixture-{cls.counter}" + (".d" if as_dir else ""))
        if as_dir:
            os.mkdir(path)
        else:
            with open(path, "w") as stream:
                stream.write("x")
        os.chmod(path, mode)
        return path, os.stat(path).st_mode & 0o7777


class ParseOracleTest(PermissionsToolTestBase):
    """50 seeded octal/symbolic conversions verified against os.chmod/os.stat."""

    def setUp(self):
        self.tool = PermissionsTool()
        rng = random.Random(252)
        plain = random.Random(252).sample(range(0o1000), 30)
        special_pool = [m for m in range(0o10000) if m & 0o7000]
        special = rng.sample(special_pool, 20)
        self.modes = plain + special

    def test_octal_to_symbolic_matches_filesystem(self):
        """For every mode: os.chmod it and compare stat.filemode with the tool."""
        for mode in self.modes:
            with self.subTest(mode=oct(mode)):
                path, actual = self.fixture(mode)
                result = self.tool.execute(mode="parse", mode_value=format(mode, "04o"))
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["input_kind"], "octal")
                self.assertEqual(result["numeric"], actual)
                self.assertEqual(result["octal4"], format(actual, "04o"))
                # stat.filemode is the operating system's own symbolic rendering.
                self.assertEqual(result["symbolic_with_special"], stat_module.filemode(os.stat(path).st_mode)[1:])
                self.assertEqual(result["octal"], format(actual & 0o777, "03o"))

    def test_symbolic_round_trip_through_bits(self):
        """Parsing the rendered symbolic string reproduces the exact bits."""
        for mode in self.modes:
            with self.subTest(mode=oct(mode)):
                _, actual = self.fixture(mode)
                symbolic = stat_module.filemode(0o100000 | actual)[1:]
                result = self.tool.execute(mode="parse", mode_value=symbolic)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["input_kind"], "symbolic")
                self.assertEqual(result["numeric"], actual)
                self.assertEqual(result["symbolic_with_special"], symbolic)
                self.assertEqual(
                    result["value_per_class"],
                    {"owner": (actual >> 6) & 7, "group": (actual >> 3) & 7, "other": actual & 7},
                )
                self.assertEqual(result["findings"], [])
                # Re-applying the derived bits through the real chmod is a no-op.
                path, _ = self.fixture(actual)
                self.assertEqual(real_chmod(path, format(actual, "04o")), actual)

    def test_octal_input_shapes_agree(self):
        """int 754, '754', and '0754' describe the same mode."""
        for value in (754, "754", "0754"):
            result = self.tool.execute(mode="parse", mode_value=value)
            self.assertEqual(result["numeric"], 0o754)
            self.assertEqual(result["symbolic"], "rwxr-xr--")

    def test_class_and_special_flags(self):
        """Per-class flags and special flags decode the 12 bits faithfully."""
        result = self.tool.execute(mode="parse", mode_value="rwsr-x--T")
        self.assertEqual(result["numeric"], 0o5750)
        self.assertEqual(result["special"], {"setuid": True, "setgid": False, "sticky": True})
        self.assertEqual(result["owner"], {"read": True, "write": True, "execute": True})
        self.assertEqual(result["group"], {"read": True, "write": False, "execute": True})
        self.assertEqual(result["other"], {"read": False, "write": False, "execute": False})
        self.assertEqual(result["symbolic"], "rwxr-x---")

    def test_invalid_characters_reported_per_position(self):
        """Invalid characters are treated as no permission and reported."""
        result = self.tool.execute(mode="parse", mode_value="rwzr-x--q")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["numeric"], 0o650)
        positions = {finding["position"]: finding for finding in result["findings"]}
        self.assertEqual(set(positions), {2, 8})
        self.assertEqual(positions[2]["character"], "z")
        self.assertEqual(positions[2]["class"], "owner")
        self.assertEqual(positions[2]["bit"], "execute")
        self.assertEqual(positions[8]["character"], "q")

    def test_wrong_length_reports_finding(self):
        """A wrong-length symbolic mode fails validation and reports the finding."""
        result = self.tool.execute(mode="parse", mode_value="rwxr-x--")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["findings"][0]["issue"], "wrong length")

    def test_parse_examples(self):
        """Documented examples parse as expected."""
        result = self.tool.execute(mode="parse", mode_value="rwxr-x---")
        self.assertEqual(result["octal"], "750")
        self.assertEqual(result["octal4"], "0750")
        result = self.tool.execute(mode="parse", mode_value="rwsr-x--t")
        self.assertEqual(result["octal4"], "5751")
        self.assertEqual(result["symbolic_with_special"], "rwsr-x--t")


class ChmodOracleTest(PermissionsToolTestBase):
    """300 seeded chmod operands evaluated against the real chmod binary.

    The oracle subprocess runs under umask 0 so a who-omitted clause means
    'all classes' on both BSD-derived and GNU chmod (POSIX: chmod never
    consults the umask; historical BSD utilities mask who-omitted clauses by
    the invoking shell's umask). X with '-' is excluded from the generator
    because BSD-derived chmod (macOS) evaluates '-X' as '+X', which contradicts
    both POSIX and GNU; the tool follows POSIX and the divergence is pinned in
    ChmodEdgeSemanticsTest.
    """

    def setUp(self):
        self.tool = PermissionsTool()

    @staticmethod
    def random_operand(rng):
        clauses = []
        for _ in range(rng.randint(1, 3)):
            who = rng.choice(WHO_CHOICES)
            op = rng.choice("+-=")
            if op == "=" and rng.random() < 0.2:
                perms = rng.choice("ugo")
            else:
                pool = "rwx" + ("X" if op == "+" else "") + ("st" if who in ("", "a") else "")
                perms = "".join(sorted(rng.sample(pool, rng.randint(1, len(pool))), key=PERM_ORDER.index))
            clauses.append(who + op + perms)
        return ",".join(clauses)

    def test_300_seeded_operations_match_real_chmod(self):
        """Every generated operand agrees with /bin/chmod bit for bit."""
        rng = random.Random(2527)
        count = 0
        while count < 300:
            operand = self.random_operand(rng)
            current = rng.randrange(0o10000)
            if not self.capable:
                current &= ~0o2000
                if "s" in operand:
                    continue
            with self.subTest(operand=operand, current=format(current, "04o")):
                path, actual_current = self.fixture(current)
                expected = real_chmod(path, operand)
                result = self.tool.execute(
                    mode="chmod",
                    current_mode=format(actual_current, "04o"),
                    operation=operand,
                )
                self.assertEqual(result["status"], "success", result)
                self.assertEqual(result["new_mode"]["numeric"], expected)
                # Per-clause change chain starts at the current mode and lands
                # on the final mode, advancing clause by clause.
                changes = result["changes"]
                self.assertEqual(int(changes[0]["perm_bits_before"], 8), actual_current)
                for previous, following in zip(changes, changes[1:]):
                    self.assertEqual(previous["perm_bits_after"], following["perm_bits_before"])
                self.assertEqual(int(changes[-1]["perm_bits_after"], 8), expected)
            count += 1

    def test_numeric_operand_is_absolute(self):
        """A numeric operand sets the mode absolutely, including specials."""
        path, current = self.fixture(0o644)
        expected = real_chmod(path, "4755")
        result = self.tool.execute(mode="chmod", current_mode=format(current, "04o"), operation="4755")
        self.assertEqual(result["new_mode"]["numeric"], expected)
        self.assertEqual(expected, 0o4755)


class ChmodEdgeSemanticsTest(PermissionsToolTestBase):
    """Hand-pinned semantic edges, each verified against the real chmod."""

    def setUp(self):
        self.tool = PermissionsTool()

    def verify(self, operand, current, is_dir=False):
        path, actual_current = self.fixture(current, as_dir=is_dir)
        expected = real_chmod(path, operand)
        result = self.tool.execute(
            mode="chmod",
            current_mode=format(actual_current, "04o"),
            operation=operand,
            is_dir=is_dir,
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(
            result["new_mode"]["numeric"],
            expected,
            f"operand {operand!r} from {actual_current:04o} (is_dir={is_dir})",
        )
        return result

    def test_x_references_the_pre_operation_mode(self):
        """X is refused when no execute bit is set before the operation."""
        self.verify("u+x,g+X", 0o644)
        self.verify("g+X", 0o644)
        self.verify("a+X", 0o755)
        self.verify("o+X", 0o700)

    def test_x_on_directories_always_applies(self):
        """On directories X behaves like x for every clause and class."""
        self.verify("g+X", 0o640, is_dir=True)
        self.verify("u+x,g+X", 0o644, is_dir=True)
        self.verify("a=rX", 0o644, is_dir=True)
        self.verify("a=rX", 0o640, is_dir=True)

    def test_copy_sources_copy_accumulated_class_bits(self):
        """=u/=g/=o copy the class bits as modified by earlier clauses."""
        self.verify("u+x,go=u", 0o640)
        self.verify("go=u", 0o640)
        self.verify("g=u", 0o640)
        self.verify("o=g", 0o640)
        self.verify("ug=o", 0o640)
        self.verify("u=g,o=g", 0o640)

    def test_equals_resets_and_clears_specials(self):
        """'=' clears unspecified bits and class-owned special bits."""
        self.verify("a=rw", 0o4755)
        self.verify("u=rw", 0o4755)
        self.verify("u=", 0o4755)
        self.verify("go=", 0o754)
        self.verify("a=", 0o755)
        self.verify("o=", 0o644)
        self.verify("a=rws", 0o644)

    def test_special_bit_addressing(self):
        """s maps to setuid/setgid per who and t to the sticky bit."""
        self.verify("u+s", 0o755)
        self.verify("g+s", 0o755)
        self.verify("+s", 0o755)
        self.verify("ug+s", 0o755)
        self.verify("+t", 0o755)
        self.verify("a+t", 0o755)
        self.verify("a-s", 0o4755)
        self.verify("u-s", 0o4755)
        self.verify("g-s", 0o2755)
        # s/t addressed to a who that owns no such bit are documented no-ops.
        result = self.verify("o+s", 0o755)
        self.assertTrue(any("s ignored" in note for note in result["notes"]))
        result = self.verify("u+t", 0o755)
        self.assertTrue(any("t ignored" in note for note in result["notes"]))

    def test_sticky_bit_requires_who_a(self):
        """The sticky bit is addressed only when who is 'a' or omitted.

        The real BSD-derived chmod treats 'o+t', 'go+t', and 'ugo+t' as no-ops
        (and 'ugo=' keeps the sticky bit while 'a=' clears it); the tool
        mirrors that exact distinction, verified against the binary.
        """
        for operand, current in (("o+t", 0o755), ("go+t", 0o755), ("ugo+t", 0o755), ("u+t", 0o755), ("o-t", 0o1775), ("ugo-t", 0o1777)):
            result = self.verify(operand, current)
            self.assertEqual(result["new_mode"]["numeric"] & 0o1000, current & 0o1000, operand)
        self.verify("a+t", 0o755)
        self.verify("ugo=", 0o1777)  # real chmod keeps the sticky bit here; a= clears it
        self.verify("ugo=rw", 0o1777)
        result = self.tool.execute(mode="chmod", current_mode="0755", operation="o+t")
        self.assertTrue(any("sticky bit is addressed only when who is 'a' or omitted" in note for note in result["notes"]))

    def test_copy_letters_must_stand_alone(self):
        """u/g/o mixed into a longer permission list is rejected per POSIX.

        POSIX and GNU chmod allow a copy letter only as the entire permission
        list; BSD-derived chmod (macOS) instead accepts mixed lists such as
        'a=us' with sequential-copy semantics. Like the pinned '-X' case, the
        tool follows the POSIX grammar: these operands are structured
        validation errors, never an uncaught KeyError.
        """
        for bad in ("a=us", "+ru", "=ug", "u=xu", "u+rwxo", "a=rtu", "g=Xu", "a=uo", "=ou", "u=gr"):
            with self.subTest(operand=bad):
                result = self.tool.execute(mode="chmod", current_mode="0644", operation=bad)
                self.assertEqual(result["status"], "error", bad)
                self.assertEqual(result["error_type"], "validation_error")
                self.assertIn("copy letters u/g/o must stand alone", result["error"])

    def test_no_whitespace_inside_operand(self):
        """Whitespace inside an operand or symbolic umask is invalid grammar.

        The real chmod binary rejects 'u+x, g-w' and ' u+x '; the sh umask
        builtin rejects 'u=rwx, g='. The tool accepts only the uniform outer
        input strip and rejects any interior whitespace.
        """
        for bad in ("u+x, g-w", "u +x", "u+x ,g-w", " u+x , g-w ", "u+x,\tg-w"):
            with self.subTest(operand=bad):
                path, _ = self.fixture(0o644)
                rejected = subprocess.run([CHMOD_BIN, bad, path], capture_output=True, text=True)
                self.assertNotEqual(rejected.returncode, 0, f"real chmod accepted {bad!r}")
                result = self.tool.execute(mode="chmod", current_mode="0644", operation=bad)
                self.assertEqual(result["status"], "error", bad)
        for bad in ("u=rwx, g=", "u=rx ,o=", "a= rx"):
            result = self.tool.execute(mode="umask_apply", mode_value="0666", umask=bad)
            self.assertEqual(result["status"], "error", bad)
        trimmed = self.tool.execute(mode="chmod", current_mode="0644", operation="  u+x,go-w  ")
        self.assertEqual(trimmed["status"], "success")
        self.assertEqual(trimmed["new_mode"]["numeric"], 0o744)

    def test_multi_clause_ordering(self):
        """Clauses apply strictly left to right."""
        self.verify("u+x,g-w,o+r", 0o640)
        self.verify("g-w,o-r", 0o666)
        self.verify("+x", 0o644)

    def test_x_with_minus_follows_posix(self):
        """a-X removes execute from a 755 file per POSIX and GNU chmod.

        BSD-derived chmod (as on macOS) evaluates '-X' as '+X' instead; the
        tool intentionally follows the POSIX rule, so this case is asserted
        against the POSIX answer rather than the local binary.
        """
        result = self.tool.execute(mode="chmod", current_mode="0755", operation="a-X")
        self.assertEqual(result["new_mode"]["numeric"], 0o644)
        self.assertEqual(result["changes"][0]["x_condition_met"], True)

    def test_who_omission_never_consults_umask(self):
        """A who-omitted clause applies to all classes regardless of umask.

        POSIX chmod ignores the umask entirely (unlike open(2) creation); the
        oracle subprocess therefore runs with umask 0, under which BSD-derived
        chmod agrees with POSIX for who-omitted clauses.
        """
        result = self.tool.execute(mode="chmod", current_mode="0644", operation="=rw")
        self.assertEqual(result["new_mode"]["numeric"], 0o666)
        self.assertTrue(any("umask is never consulted" in note for note in result["notes"]))
        self.assertEqual(result["changes"][0]["who"], "a")

    def test_is_dir_false_x_note(self):
        """Without is_dir the X note documents the reduced rule."""
        result = self.tool.execute(mode="chmod", current_mode="0644", operation="a+X")
        self.assertTrue(any("execute-if-any-execute-present" in note for note in result["notes"]))
        self.assertEqual(result["new_mode"]["numeric"], 0o644)


class UmaskOracleTest(PermissionsToolTestBase):
    """umask application verified with os.umask round-trips and the umask tool."""

    def setUp(self):
        self.tool = PermissionsTool()

    def test_octal_umask_creation_oracle(self):
        """Files created under each mask get exactly mode & ~umask."""
        rng = random.Random(2522)
        for mask in rng.sample(range(0o777), 12):
            with self.subTest(umask=format(mask, "03o")):
                previous = os.umask(mask)
                try:
                    path = os.path.join(self.directory, f"umask-{mask:o}")
                    with open(path, "w") as stream:
                        stream.write("x")
                    created = os.stat(path).st_mode & 0o777
                finally:
                    restored = os.umask(previous)
                self.assertEqual(restored, mask)  # set/restore round trip
                self.assertEqual(created, 0o666 & ~mask)
                result = self.tool.execute(mode="umask_apply", mode_value="0666", umask=format(mask, "03o"))
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["result"]["numeric"], created)

    def test_symbolic_umask_matches_umask_command(self):
        """Symbolic masks resolve exactly like sh's umask builtin from base 0."""
        rng = random.Random(2523)
        for _ in range(15):
            who = rng.choice(WHO_CHOICES)
            op = rng.choice("+-=")
            # The umask builtin parses a leading '-' as an option flag, so
            # keep at least one who letter for removals when probing via sh.
            if op == "-" and not who:
                who = "g"
            perms = "".join(sorted(rng.sample("rwx", rng.randint(1, 3))))
            operand = f"{who}{op}{perms}"
            with self.subTest(operand=operand):
                shell = subprocess.run(
                    ["/bin/sh", "-c", f"umask 0; umask '{operand}'; umask"],
                    capture_output=True,
                    text=True,
                )
                expected = int(shell.stdout.strip(), 8)
                result = self.tool.execute(mode="umask_apply", mode_value="0666", umask=operand)
                self.assertEqual(result["status"], "success", result)
                self.assertEqual(int(result["umask_octal"], 8), expected)
                self.assertEqual(result["result"]["numeric"], 0o666 & ~expected)

    def test_bits_table(self):
        """The bits table explains mode & ~umask bit by bit."""
        result = self.tool.execute(mode="umask_apply", mode_value="0666", umask="022")
        table = {(row["class"], row["bit"]): row for row in result["bits"]}
        self.assertEqual(len(table), 9)
        # umask 022 denies group-w and other-w; everything else passes through.
        self.assertEqual((table[("owner", "read")]["mode_bit"], table[("owner", "read")]["umask_bit"]), (1, 0))
        self.assertEqual(table[("group", "write")]["result_bit"], 0)
        self.assertEqual(table[("other", "write")]["result_bit"], 0)
        self.assertEqual(table[("other", "read")]["result_bit"], 1)
        self.assertEqual(result["result"]["octal"], "644")
        self.assertEqual(result["explanation"], "result = mode & ~umask (the mask clears creation bits; it never adds them)")


class ReviewMatrixTest(PermissionsToolTestBase):
    """Hand-derived security matrix for the bit-level review."""

    def setUp(self):
        self.tool = PermissionsTool()

    def assert_findings(self, mode_value, is_dir, expected):
        result = self.tool.execute(mode="review", mode_value=mode_value, is_dir=is_dir)
        self.assertEqual(result["status"], "success")
        actual = {finding["id"]: finding["severity"] for finding in result["findings"]}
        self.assertEqual(actual, expected, f"mode {mode_value} is_dir={is_dir}")

    def test_matrix(self):
        """Each review case yields exactly the hand-derived findings."""
        matrix = [
            ("777", False, {"world_writable_file": "high", "group_writable_executable": "medium", "world_readable": "info"}),
            ("777", True, {"world_writable_directory_without_sticky": "high", "group_writable_executable": "medium", "world_readable": "info"}),
            ("1777", True, {"world_writable_sticky_directory": "info", "group_writable_executable": "medium", "world_readable": "info"}),
            ("1777", False, {"world_writable_file": "high", "group_writable_executable": "medium", "world_readable": "info"}),
            ("002", False, {"world_writable_file": "high"}),
            ("664", False, {"world_readable": "info"}),
            ("775", False, {"group_writable_executable": "medium", "world_readable": "info"}),
            ("4755", False, {"setuid_executable": "medium", "world_readable": "info"}),
            ("4600", False, {"setuid_without_execute": "low"}),
            ("2755", False, {"setgid_executable": "medium", "world_readable": "info"}),
            ("2044", False, {"setgid_without_execute": "low", "world_readable": "info"}),
            ("000", False, {"no_permissions": "medium"}),
            ("111", False, {"execute_without_read": "low"}),
            ("111", True, {"traverse_only_directory": "info"}),
            ("600", False, {}),
            ("2666", False, {"world_writable_file": "high", "setgid_without_execute": "low", "world_readable": "info"}),
        ]
        for mode_value, is_dir, expected in matrix:
            with self.subTest(mode=mode_value, is_dir=is_dir):
                self.assert_findings(mode_value, is_dir, expected)

    def test_expected_suid_context_and_hints(self):
        """setuid findings cite the classic binaries; hints are read-only text."""
        result = self.tool.execute(mode="review", mode_value="4755")
        detail = next(f for f in result["findings"] if f["id"] == "setuid_executable")["detail"]
        self.assertIn("/usr/bin/passwd", detail)
        self.assertIn("/usr/bin/sudo", detail)
        for hint in result["hints"]:
            self.assertTrue(hint["command"].startswith("find <path>"))
            self.assertNotIn(";", hint["command"])
            self.assertNotIn("|", hint["command"])
        self.assertIn("never executes", result["hint_note"])

    def test_world_readable_states_no_content_assumption(self):
        """The world-readable finding documents that content is never read."""
        result = self.tool.execute(mode="review", mode_value="644")
        finding = next(f for f in result["findings"] if f["id"] == "world_readable")
        self.assertIn("never reads content", finding["detail"])


class InvertRoundTripTest(PermissionsToolTestBase):
    """Generated invert commands reproduce the intended change on real chmod."""

    def setUp(self):
        self.tool = PermissionsTool()

    def apply_command(self, command, current):
        path, actual_current = self.fixture(current)
        return real_chmod(path, command)

    def test_50_seeded_round_trips(self):
        """Every suggested command, applied by the real chmod, hits the target."""
        rng = random.Random(2525)
        for index in range(50):
            current = rng.randrange(0o10000)
            target = rng.randrange(0o10000)
            if not self.capable:
                current &= ~0o2000
                target &= ~0o2000
            with self.subTest(index=index, current=format(current, "04o"), target=format(target, "04o")):
                result = self.tool.execute(
                    mode="invert",
                    mode_value=format(current, "04o"),
                    target_mode=format(target, "04o"),
                )
                self.assertEqual(result["status"], "success")
                if current == target:
                    self.assertFalse(result["changed"])
                    continue
                self.assertTrue(result["changed"])
                command = result["command"]
                self.assertTrue(command)
                self.assertEqual(self.apply_command(command, current), target)

    def test_hand_cases(self):
        """Deterministic simplest-form commands for representative diffs."""
        cases = [
            (0o644, 0o600, "go-r"),
            (0o666, 0o640, "g-w,o-rw"),
            (0o000, 0o644, "u+rw,go+r"),
            (0o755, 0o4755, "u+s"),
            (0o4755, 0o0755, "u-s"),
            (0o644, 0o751, "ug+x,o=x"),
            (0o4755, 0o4640, "ug-x,o-rx"),
        ]
        for current, target, command in cases:
            with self.subTest(current=format(current, "04o"), target=format(target, "04o")):
                result = self.tool.execute(
                    mode="invert", mode_value=format(current, "04o"), target_mode=format(target, "04o")
                )
                self.assertEqual(result["command"], command)
                self.assertEqual(self.apply_command(command, current), target)

    def test_deterministic_and_stable_for_no_change(self):
        """Identical inputs give identical output; equal modes need no command."""
        first = self.tool.execute(mode="invert", mode_value="0644", target_mode="0600")
        second = self.tool.execute(mode="invert", mode_value="0644", target_mode="0600")
        self.assertEqual(first["command"], second["command"])
        same = self.tool.execute(mode="invert", mode_value="0755", target_mode="0755")
        self.assertFalse(same["changed"])
        self.assertEqual(same["command"], "")


class PermissionsValidationTest(unittest.TestCase):
    """Strict validation, caps, and structured errors."""

    def setUp(self):
        self.tool = PermissionsTool()

    def test_invalid_selector(self):
        self.assertEqual(self.tool.execute(mode="chown")["status"], "error")
        self.assertEqual(self.tool.execute(mode=123)["status"], "error")

    def test_mode_value_shapes(self):
        for bad in ("rwxr-x--", "rwx", 8, 987, -755, True, "7548", ""):
            result = self.tool.execute(mode="parse", mode_value=bad)
            self.assertEqual(result["status"], "error", bad)

    def test_operation_grammar(self):
        for bad in ("u!", "x", "u++x", "g+u", "u+", "uu+x", ",u+x", "u+x,", "s", "t", "u+x,,g-w"):
            result = self.tool.execute(mode="chmod", current_mode="644", operation=bad)
            self.assertEqual(result["status"], "error", bad)

    def test_operation_caps(self):
        long_operand = ",".join(["u+x"] * 13)
        self.assertEqual(self.tool.execute(mode="chmod", current_mode="644", operation=long_operand)["status"], "error")
        oversized = "u" * 129 + "+x"
        self.assertEqual(self.tool.execute(mode="chmod", current_mode="644", operation=oversized)["status"], "error")
        self.tool.max_mode_length = 2
        self.assertEqual(self.tool.execute(mode="parse", mode_value="644")["status"], "error")
        self.tool.max_mode_length = 16

    def test_missing_required_arguments(self):
        self.assertEqual(self.tool.execute(mode="parse")["status"], "error")
        self.assertEqual(self.tool.execute(mode="chmod", current_mode="644")["status"], "error")
        self.assertEqual(self.tool.execute(mode="umask_apply", mode_value="644")["status"], "error")
        self.assertEqual(self.tool.execute(mode="invert", mode_value="644")["status"], "error")

    def test_umask_rejects_special_bits_and_copy(self):
        for bad in ("7777", 4095, 0o7777, "u+s", "a=X", "g=u", "u+r,s"):
            result = self.tool.execute(mode="umask_apply", mode_value="644", umask=bad)
            self.assertEqual(result["status"], "error", bad)

    def test_is_dir_must_be_boolean(self):
        self.assertEqual(self.tool.execute(mode="review", mode_value="644", is_dir=1)["status"], "error")
        self.assertEqual(self.tool.execute(mode="review", mode_value="644", is_dir="yes")["status"], "error")

    def test_deterministic_output(self):
        first = self.tool.execute(mode="chmod", current_mode="0644", operation="u+x,go-w")
        second = self.tool.execute(mode="chmod", current_mode="0644", operation="u+x,go-w")
        self.assertEqual(first, second)


class PermissionsRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped permissions_tool.yaml."""

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
        """Verify the shipped yaml resolves to a tool component exposing PermissionsTool."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "PermissionsTool")

    def test_manager(self):
        """Verify the PermissionsTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, PermissionsTool)
        self.assertEqual(tool.input_keys, ["mode"])

    def test_package_export(self):
        """PermissionsTool is exported from the common_tool package."""
        from agentuniverse.agent.action.tool.common_tool import PermissionsTool as Exported

        self.assertIs(Exported, PermissionsTool)


if __name__ == "__main__":
    unittest.main()
