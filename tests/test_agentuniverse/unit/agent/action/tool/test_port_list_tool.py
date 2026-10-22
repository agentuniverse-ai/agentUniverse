import os
import socket
import unittest

from pydantic import ValidationError

from agentuniverse.agent.action.tool.common_tool import port_list_tool as port_module
from agentuniverse.agent.action.tool.common_tool.port_list_tool import PortListTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(port_module.__file__), "port_list_tool.yaml")


class Lcg:
    """Deterministic pseudo-random source for property tests."""

    def __init__(self, seed):
        self.state = seed & 0xFFFFFFFF

    def _next(self):
        self.state = (1103515245 * self.state + 12345) & 0xFFFFFFFF
        return self.state

    def randint(self, low, high):
        return low + self._next() % (high - low + 1)

    def sample(self, population, count):
        pool = list(population)
        picked = []
        for _ in range(min(count, len(pool))):
            picked.append(pool.pop(self._next() % len(pool)))
        return picked

    def shuffle(self, items):
        for index in range(len(items) - 1, 0, -1):
            swap = self._next() % (index + 1)
            items[index], items[swap] = items[swap], items[index]


def reference_canonical(ports):
    """Independent test-side canonicalizer: sort, dedup, merge adjacent runs."""
    merged = []
    for port in sorted(set(ports)):
        if merged and port <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], port))
        else:
            merged.append((port, port))
    return ",".join(f"{a}" if a == b else f"{a}-{b}" for a, b in merged)


class PortListToolTest(unittest.TestCase):
    def setUp(self):
        self.tool = PortListTool()

    def codes(self, result):
        return [finding["code"] for finding in result.get("findings", [])]

    # ------------------------------------------------------------ parse

    def test_parse_basic_vector(self):
        result = self.tool.execute(mode="parse", spec="22,80-90,443")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["canonical"], "22,80-90,443")
        self.assertEqual(
            result["ranges"],
            [
                {"start": 22, "end": 22, "size": 1},
                {"start": 80, "end": 90, "size": 11},
                {"start": 443, "end": 443, "size": 1},
            ],
        )
        self.assertEqual(result["port_count"], 13)
        self.assertEqual(result["findings"], [])

    def test_parse_sorts_merges_and_flags(self):
        result = self.tool.execute(mode="parse", spec="443, 85-95 ,80-90,22,443")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["canonical"], "22,80-95,443")
        self.assertEqual(result["port_count"], 18)
        codes = self.codes(result)
        self.assertIn("duplicate_items", codes)
        self.assertIn("unsorted_input", codes)
        self.assertIn("merged_ranges", codes)

    def test_parse_adjacent_ports_merge(self):
        result = self.tool.execute(mode="parse", spec="80,81,82")
        self.assertEqual(result["canonical"], "80-82")
        self.assertIn("merged_ranges", self.codes(result))

    def test_parse_gap_not_merged(self):
        result = self.tool.execute(mode="parse", spec="79,81")
        self.assertEqual(result["canonical"], "79,81")

    def test_parse_singleton_range_and_leading_zeros(self):
        result = self.tool.execute(mode="parse", spec="80-80,0443")
        self.assertEqual(result["canonical"], "80,443")
        self.assertIn("single_port_range", self.codes(result))
        self.assertIn("leading_zeros", self.codes(result))

    def test_parse_extremes(self):
        result = self.tool.execute(mode="parse", spec="0,65535")
        self.assertEqual(result["canonical"], "0,65535")
        self.assertEqual(result["port_count"], 2)

    def test_parse_mode_case_insensitive(self):
        result = self.tool.execute(mode="PARSE", spec="22,443")
        self.assertEqual(result["status"], "success")

    def test_parse_error_vectors(self):
        vectors = [
            ("70000", "out of range"),
            ("-5", "invalid port list item"),
            ("90-80", "descending range"),
            ("65536-65540", "out of range"),
            ("abc", "invalid port list item"),
            ("22,,80", "empty item"),
            ("22,80,", "empty item"),
            ("80-", "invalid port list item"),
            ("-80", "invalid port list item"),
            ("80--90", "invalid port list item"),
            ("22;80", "invalid port list item"),
            ("22 80", "invalid port list item"),
            ("", "non-empty"),
            ("   ", "non-empty"),
            ("99999", "out of range"),
        ]
        for spec, fragment in vectors:
            with self.subTest(spec=spec):
                result = self.tool.execute(mode="parse", spec=spec)
                self.assertEqual(result["status"], "error", result)
                self.assertEqual(result["error_type"], "validation_error")
                self.assertIn(fragment, result["error"])

    def test_parse_type_errors(self):
        self.assertEqual(self.tool.execute(mode="parse")["error_type"], "validation_error")
        self.assertIn("must be a string", self.tool.execute(mode="parse", spec=80)["error"])
        self.assertIn("mode must be", self.tool.execute(mode="explode", spec="22")["error"])
        self.assertIn("mode must be a string", self.tool.execute(mode=None)["error"])

    # ------------------------------------------------------------ expand

    def test_expand_vector(self):
        result = self.tool.execute(mode="expand", spec="22,80-82")
        self.assertEqual(result["ports"], [22, 80, 81, 82])
        self.assertEqual(result["port_count"], 4)
        self.assertEqual(result["returned"], 4)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["canonical"], "22,80-82")

    def test_expand_truncates_at_cap(self):
        tool = PortListTool(max_expanded_ports=5)
        result = tool.execute(mode="expand", spec="1-10")
        self.assertEqual(result["ports"], [1, 2, 3, 4, 5])
        self.assertEqual(result["returned"], 5)
        self.assertEqual(result["port_count"], 10)
        self.assertTrue(result["truncated"])

    def test_expand_universe(self):
        result = self.tool.execute(mode="expand", spec="65535")
        self.assertEqual(result["ports"], [65535])
        result = self.tool.execute(mode="expand", spec="0-65535")
        self.assertTrue(result["truncated"])
        self.assertEqual(result["port_count"], 65536)
        self.assertEqual(result["returned"], self.tool.max_expanded_ports)

    # ------------------------------------------------------------ compress

    def test_compress_from_spec(self):
        result = self.tool.execute(mode="compress", spec="443,80-82,79,81")
        self.assertEqual(result["canonical"], "79-82,443")
        self.assertEqual(result["port_count"], 5)
        self.assertIn("merged_ranges", self.codes(result))

    def test_compress_from_port_list(self):
        result = self.tool.execute(mode="compress", ports=[443, 22, 23, 24, 25, 80, 443, 22])
        self.assertEqual(result["canonical"], "22-25,80,443")
        self.assertEqual(result["port_count"], 6)
        self.assertIn("duplicate_items", self.codes(result))
        self.assertIn("unsorted_input", self.codes(result))

    def test_compress_rejects_both_sources_and_none(self):
        self.assertIn("not both", self.tool.execute(mode="compress", spec="22", ports=[22])["error"])
        self.assertIn("required", self.tool.execute(mode="compress")["error"])

    def test_compress_port_list_validation(self):
        for ports, fragment in [
            ([], "at least one port"),
            ([True, 22], "must be integers"),
            (["22"], "must be integers"),
            ([70000], "out of range"),
            ([-1], "out of range"),
            (22, "must be a list"),
        ]:
            with self.subTest(ports=ports):
                result = self.tool.execute(mode="compress", ports=ports)
                self.assertEqual(result["error_type"], "validation_error")
                self.assertIn(fragment, result["error"])

    # ------------------------------------------------------------ lookup

    def test_lookup_known_services(self):
        result = self.tool.execute(mode="lookup", spec="22,53,80,443,8080")
        self.assertEqual(result["known_count"], 5)
        self.assertEqual(result["unknown_count"], 0)
        by_port = {row["port"]: row for row in result["results"]}
        self.assertEqual(by_port[22]["name"], "ssh")
        self.assertEqual(by_port[53]["name"], "domain")
        self.assertEqual(by_port[80]["name"], "http")
        self.assertEqual(by_port[443]["name"], "https")
        self.assertEqual(by_port[8080]["name"], "http-alt")

    def test_lookup_unknown_reported_never_guessed(self):
        result = self.tool.execute(mode="lookup", spec="12345,54321")
        self.assertEqual(result["unknown"], [12345, 54321])
        self.assertEqual(result["results"], [
            {"port": 12345, "known": False},
            {"port": 54321, "known": False},
        ])

    def test_lookup_from_port_list(self):
        result = self.tool.execute(mode="lookup", ports=[3306, 5432, 9999])
        names = {row["port"]: row.get("name") for row in result["results"]}
        self.assertEqual(names[3306], "mysql")
        self.assertEqual(names[5432], "postgresql")
        self.assertIn(9999, result["unknown"])

    def test_lookup_cap(self):
        tool = PortListTool(max_lookup_ports=3)
        result = tool.execute(mode="lookup", spec="1-10")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("max_lookup_ports", result["error"])

    def test_lookup_requires_boolean_system_check(self):
        result = self.tool.execute(mode="lookup", spec="22", system_check="yes")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("system_check", result["error"])

    # ------------------------------------------------- getservbyname oracle

    def test_lookup_system_check_agrees_for_stable_services(self):
        # socket.getservbyname is the platform-caveat oracle: every platform
        # carries these classic IANA names, so agreement is required; entries
        # the local database lacks would surface as missing_local_mapping.
        result = self.tool.execute(mode="lookup", spec="21,22,23,25,53,80,443", system_check=True)
        by_port = {row["port"]: row for row in result["results"]}
        for port, name in [(21, "ftp"), (22, "ssh"), (23, "telnet"), (25, "smtp"), (53, "domain"), (80, "http"), (443, "https")]:
            with self.subTest(port=port):
                try:
                    system_port = socket.getservbyname(name, "tcp")
                except OSError:
                    continue  # platform lacks the mapping; caveat applies
                self.assertEqual(system_port, port)
                self.assertEqual(by_port[port]["system_check"]["status"], "agree")
                self.assertEqual(by_port[port]["system_check"]["mapped_port"], port)

    def test_lookup_system_check_statuses_are_informational(self):
        result = self.tool.execute(mode="lookup", spec="465,8080,9418", system_check=True)
        by_port = {row["port"]: row for row in result["results"]}
        for port in (465, 8080, 9418):
            with self.subTest(port=port):
                check = by_port[port]["system_check"]
                # Any platform answer is legal; it must never turn into an error.
                self.assertIn(check["status"], {"agree", "missing_local_mapping", "name_maps_to_other_port"})
                self.assertTrue(check["mapped_port"] is None or isinstance(check["mapped_port"], int))
        self.assertEqual(result["status"], "success")

    def test_lookup_without_system_check_has_no_system_key(self):
        result = self.tool.execute(mode="lookup", spec="22,8080")
        for row in result["results"]:
            self.assertNotIn("system_check", row)

    # ------------------------------------------------------------ algebra

    def test_union_vector(self):
        result = self.tool.execute(mode="union", spec="22,80-90", other_spec="80,443")
        self.assertEqual(result["canonical"], "22,80-90,443")
        self.assertEqual(result["port_count"], 13)
        self.assertEqual(result["ports"], [22, *range(80, 91), 443])

    def test_intersect_vector(self):
        result = self.tool.execute(mode="intersect", spec="22,80-90,443", other_spec="80,85,443,8443")
        self.assertEqual(result["canonical"], "80,85,443")
        self.assertEqual(result["ports"], [80, 85, 443])

    def test_intersect_disjoint_reports_empty(self):
        result = self.tool.execute(mode="intersect", spec="22,80", other_spec="443,8080")
        self.assertEqual(result["canonical"], "")
        self.assertEqual(result["ranges"], [])
        self.assertEqual(result["port_count"], 0)
        self.assertIn("empty_intersection", self.codes(result))

    def test_union_with_ports_side(self):
        result = self.tool.execute(mode="union", ports=[80, 443], other_spec="22,80")
        self.assertEqual(result["canonical"], "22,80,443")

    def test_intersect_with_ports_side(self):
        result = self.tool.execute(mode="intersect", ports=[80, 443, 22], other_spec="22,80-90")
        self.assertEqual(result["canonical"], "22,80")

    def test_algebra_requires_other_spec(self):
        result = self.tool.execute(mode="union", spec="22")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("other_spec", result["error"])

    def test_algebra_propagates_side_errors(self):
        result = self.tool.execute(mode="union", spec="22", other_spec="70000")
        self.assertIn("out of range", result["error"])
        result = self.tool.execute(mode="intersect", spec="22", other_spec="")
        self.assertIn("non-empty", result["error"])

    def test_union_of_full_universe_omits_ports_list(self):
        tool = PortListTool(max_expanded_ports=100)
        result = tool.execute(mode="union", spec="0-400", other_spec="300-65535")
        self.assertEqual(result["port_count"], 65536)
        self.assertNotIn("ports", result)
        self.assertTrue(result["ports_omitted"])
        self.assertEqual(result["canonical"], "0-65535")

    # ------------------------------------------------------ config guards

    def test_spec_length_cap(self):
        tool = PortListTool(max_spec_chars=10)
        result = tool.execute(mode="parse", spec="22,80-90,443,8080")
        self.assertEqual(result["error_type"], "validation_error")
        self.assertIn("max_spec_chars", result["error"])

    def test_range_count_cap(self):
        tool = PortListTool(max_ranges=3)
        result = tool.execute(mode="parse", spec="1,3,5,7")
        self.assertIn("max_ranges", result["error"])

    def test_config_validation(self):
        for kwargs in ({"max_spec_chars": 0}, {"max_expanded_ports": -1}, {"max_ranges": -5}):
            with self.subTest(kwargs=kwargs):
                result = PortListTool(**kwargs).execute(mode="parse", spec="22")
                self.assertEqual(result["error_type"], "validation_error")
                self.assertIn("must be a positive integer", result["error"])

    def test_config_rejects_wrong_types_at_construction(self):
        with self.assertRaises(ValidationError):
            PortListTool(max_lookup_ports="x")

    # -------------------------------------------------------- determinism

    def test_deterministic_output(self):
        first = self.tool.execute(mode="parse", spec="443,80-90,22")
        second = self.tool.execute(mode="parse", spec="443,80-90,22")
        self.assertEqual(first, second)
        self.assertEqual(
            self.tool.execute(mode="union", spec="22", other_spec="80"),
            self.tool.execute(mode="union", spec="22", other_spec="80"),
        )

    # --------------------------------------------------- property battery

    def test_property_round_trip_canonical(self):
        rng = Lcg(20261021)
        for _ in range(200):
            size = rng.randint(1, 40)
            ports = rng.sample(range(0, 1024), size)
            with self.subTest(iteration=_):
                result = self.tool.execute(mode="compress", ports=ports)
                expected = reference_canonical(ports)
                self.assertEqual(result["canonical"], expected)
                self.assertEqual(result["port_count"], len(set(ports)))
                # canonical is idempotent and re-parses to the same set
                reparsed = self.tool.execute(mode="parse", spec=result["canonical"])
                self.assertEqual(reparsed["canonical"], expected)
                self.assertEqual(reparsed["port_count"], len(set(ports)))
                self.assertEqual(reparsed["findings"], [])

    def test_property_mangled_specs_converge(self):
        rng = Lcg(4252)
        for _ in range(200):
            size = rng.randint(1, 25)
            ports = rng.sample(range(0, 600), size)
            # Re-emit the port set as a deliberately mangled spec: singleton
            # tokens and ranges, shuffled, with duplicated and overlapped
            # entries mixed in.  Ranges may mention extra ports, so the
            # expected set is derived by independently expanding every token.
            tokens = [str(p) for p in ports]
            mentioned = set(ports)
            for start in ports[: len(ports) // 2]:
                end = start + rng.randint(0, 4)
                if end <= 65535:
                    tokens.append(f"{start}-{end}")
                    mentioned.update(range(start, end + 1))
            duplicated = tokens + tokens[: max(1, len(tokens) // 3)]
            rng.shuffle(duplicated)
            spec = ",".join(duplicated)
            expected = reference_canonical(mentioned)
            result = self.tool.execute(mode="parse", spec=spec)
            self.assertEqual(result["status"], "success", spec)
            self.assertEqual(result["canonical"], expected, spec)
            self.assertEqual(result["port_count"], len(mentioned), spec)

    def test_property_expansion_matches_set(self):
        rng = Lcg(777001)
        for _ in range(200):
            start = rng.randint(0, 1000)
            end = start + rng.randint(0, 60)
            result = self.tool.execute(mode="expand", spec=f"{start}-{end}")
            self.assertEqual(result["ports"], list(range(start, end + 1)))
            self.assertEqual(result["port_count"], end - start + 1)

    def test_property_set_algebra(self):
        rng = Lcg(31415)
        for _ in range(200):
            left = set(rng.sample(range(0, 300), rng.randint(1, 30)))
            right = set(rng.sample(range(0, 300), rng.randint(1, 30)))
            spec_a = reference_canonical(left)
            spec_b = reference_canonical(right)
            expected_union = reference_canonical(left | right)
            expected_intersection = reference_canonical(left & right)
            union = self.tool.execute(mode="union", spec=spec_a, other_spec=spec_b)
            intersection = self.tool.execute(mode="intersect", spec=spec_a, other_spec=spec_b)
            self.assertEqual(union["canonical"], expected_union)
            self.assertEqual(union["port_count"], len(left | right))
            self.assertEqual(sorted(union["ports"]), sorted(left | right))
            self.assertEqual(intersection["canonical"], expected_intersection)
            self.assertEqual(intersection["port_count"], len(left & right))


class PortListToolRegistrationTest(unittest.TestCase):
    def setUp(self):
        self.config = Configer(path=os.path.abspath(YAML_PATH)).load()
        try:
            self.previous = ApplicationConfigManager().app_configer
        except ValueError:
            self.previous = None

    def tearDown(self):
        ApplicationConfigManager().app_configer = self.previous

    def test_schema(self):
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "PortListTool")

    def test_manager(self):
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, PortListTool)
        self.assertEqual(tool.input_keys, ["mode", "spec"])

    def test_yaml_mirrors_module_defaults(self):
        configer = ToolConfiger().load_by_configer(self.config)
        tool = PortListTool()
        self.assertEqual(configer.name, "port_list_tool")
        self.assertEqual(tool.max_spec_chars, 4096)
        self.assertEqual(tool.max_ranges, 1024)
        self.assertEqual(tool.max_expanded_ports, 8192)
        self.assertEqual(tool.max_lookup_ports, 1024)


if __name__ == "__main__":
    unittest.main()
