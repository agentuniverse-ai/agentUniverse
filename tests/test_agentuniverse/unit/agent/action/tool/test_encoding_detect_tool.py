import os
import random
import unittest

from agentuniverse.agent.action.tool.common_tool import encoding_detect_tool as encoding_module
from agentuniverse.agent.action.tool.common_tool.encoding_detect_tool import EncodingDetectTool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.application_configer.app_configer import AppConfiger
from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.component_configer.configers.tool_configer import ToolConfiger
from agentuniverse.base.config.configer import Configer

YAML_PATH = os.path.join(os.path.dirname(encoding_module.__file__), "encoding_detect_tool.yaml")

try:
    import chardet

    HAS_CHARDET = True
except ImportError:  # pragma: no cover - oracle is optional in constrained environments
    HAS_CHARDET = False

try:
    import charset_normalizer

    HAS_CHARSET_NORMALIZER = True
except ImportError:  # pragma: no cover - oracle is optional in constrained environments
    HAS_CHARSET_NORMALIZER = False

# Real multilingual sample text in five scripts (English, French accented
# Latin, Russian Cyrillic, Chinese CJK, and emoji-heavy text with ZWJ and
# flag sequences). Public sample sentences only.
SAMPLE_TEXTS = [
    "The quick brown fox jumps over the lazy dog. Pack my box with five dozen liquor jugs.",
    "À côté de l'église, le garçon naïve résumé — provoquant l'été éphémère",
    "Съешь же ещё этих мягких французских булок, да выпей чаю. Привет мир!",
    "人工智能正在改变世界。天地玄黄，宇宙洪荒。编码检测是必要的。",  # noqa: RUF001

    "Party! 🎉🚀💯 Family 👨‍👩‍👧‍👦 Flags 🇺🇳🇯🇵 zero width‍joiner ✨✨ done",
]

BOM_EXPECTATIONS = {
    b"\xef\xbb\xbf": ("utf-8", 3),
    b"\xff\xfe": ("utf-16-le", 2),
    b"\xfe\xff": ("utf-16-be", 2),
    b"\xff\xfe\x00\x00": ("utf-32-le", 4),
    b"\x00\x00\xfe\xff": ("utf-32-be", 4),
    b"\x2b\x2f\x76\x38": ("utf-7", 0),
    b"\xf7\x64\x4c": ("utf-1", 0),
}


def latin1_view(data):
    """Convert raw bytes to the tool's latin-1 escape-contract payload text."""
    return data.decode("latin-1")


class EncodingDetectToolTest(unittest.TestCase):
    """Unit tests for EncodingDetectTool input contract, caps, and modes."""

    def setUp(self):
        """Create a default-configured tool for every test."""
        self.tool = EncodingDetectTool()

    def test_detect_utf8_text(self):
        """Verify detect returns ranked candidates and a utf-8 winner for multilingual utf-8."""
        payload = "héllo wörld 日本語 🎉".encode("utf-8")  # noqa: UP012
        result = self.tool.execute(mode="detect", payload=latin1_view(payload))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["winner"], "utf-8")
        self.assertFalse(result["bom"]["found"])
        confidences = [item["confidence"] for item in result["candidates"]]
        self.assertEqual(confidences, sorted(confidences, reverse=True))
        top = result["candidates"][0]
        self.assertEqual(top["encoding"], "utf-8")
        self.assertIn("structural:utf-8-valid", top["evidence"])
        self.assertTrue(all(0.0 <= item["confidence"] <= 1.0 for item in result["candidates"]))

    def test_bom_table_exact(self):
        """Verify the BOM table names and consumed offsets byte for byte."""
        for signature, (name, consumed) in BOM_EXPECTATIONS.items():
            result = self.tool.execute(mode="detect", payload=latin1_view(signature + b"rest-of-payload"))
            bom = result["bom"]
            self.assertTrue(bom["found"], signature)
            self.assertEqual(bom["name"], name)
            self.assertEqual(bom["offset_consumed"], consumed)

    def test_bom_wins_over_declared(self):
        """Verify a BOM payload declared as something else reports the conflict and keeps the BOM winner."""
        payload = "中文测试".encode("utf-16")
        result = self.tool.execute(mode="detect", payload=latin1_view(payload), declared="utf-8")
        self.assertEqual(result["winner"], "utf-16-le")
        self.assertTrue(result["declared_conflict"])

    def test_declared_match_adds_evidence(self):
        """Verify a matching declaration attaches declared evidence instead of a conflict."""
        payload = "héllo".encode("utf-8")  # noqa: UP012
        result = self.tool.execute(mode="detect", payload=latin1_view(payload), declared="utf-8")
        self.assertFalse(result["declared_conflict"])
        top = result["candidates"][0]
        self.assertEqual(top["encoding"], "utf-8")
        self.assertIn("declared", top["evidence"])

    def test_hex_payload_contract(self):
        """Verify hex input decodes to exact bytes and mirrors the payload path."""
        data = "日本".encode("utf-8")  # noqa: UP012
        via_hex = self.tool.execute(mode="detect", hex=data.hex())
        via_payload = self.tool.execute(mode="detect", payload=latin1_view(data))
        self.assertEqual(via_hex["winner"], via_payload["winner"])
        self.assertEqual(via_hex["length"], len(data))
        spaced = self.tool.execute(mode="detect", hex=" ".join(data[i : i + 2].hex() for i in range(0, len(data), 2)))
        self.assertEqual(spaced["length"], len(data))

    def test_latin1_escape_contract(self):
        """Verify non-latin-1 payload text is rejected with the contract explanation."""
        result = self.tool.execute(mode="detect", payload="plain unicode 日本")
        self.assertEqual(result["status"], "error")
        self.assertIn("latin-1 escape contract", result["error"])

    def test_input_contract_errors(self):
        """Verify payload/hex exclusivity and mode validation."""
        self.assertEqual(self.tool.execute(mode="detect")["error_type"], "validation_error")
        self.assertIn("exactly one", self.tool.execute(mode="detect", payload="a", hex="41")["error"])
        self.assertIn("mode must be", self.tool.execute(mode="bogus", payload="a")["error"])
        self.assertEqual(self.tool.execute(mode="detect", payload=None, hex=None)["error_type"], "validation_error")

    def test_mode_parameter_rejection(self):
        """Verify parameters are rejected for modes that do not accept them."""
        self.assertIn("not accepted by mode", self.tool.execute(mode="validate_utf8", payload="a", declared="utf-8")["error"])
        self.assertIn("not accepted by mode", self.tool.execute(mode="detect", payload="a", target="utf-8")["error"])
        self.assertIn("requires a target", self.tool.execute(mode="repair_preview", payload="a")["error"])
        self.assertIn("not recognized", self.tool.execute(mode="repair_preview", payload="a", target="not-a-codec")["error"])

    def test_validate_utf8_mode_reasons(self):
        """Verify validate_utf8 reports capped errors with reason labels and a total count."""
        result = self.tool.execute(mode="validate_utf8", payload="ok\xc3\x28also\xf0\x9f\x28\x80\xed\xa0\x80end")
        self.assertFalse(result["valid"])
        reasons = [item["reason"] for item in result["errors"]]
        self.assertTrue(any("invalid continuation" in reason for reason in reasons))
        self.assertTrue(any("surrogate" in reason for reason in reasons))
        self.assertTrue(all(set(item) == {"offset", "byte", "reason"} for item in result["errors"]))

    def test_validate_utf8_error_cap(self):
        """Verify the error list is capped while the total count stays exact."""
        payload = bytes(range(0x80, 0xC0)) * 4  # every byte is a stray continuation
        result = self.tool.execute(mode="validate_utf8", payload=latin1_view(payload))
        self.assertGreater(result["error_count"], self.tool.max_errors)
        self.assertEqual(len(result["errors"]), self.tool.max_errors)
        self.assertTrue(result["errors_truncated"])

    def test_utf16_and_utf32_validation_fields(self):
        """Verify utf-16 and utf-32 structural errors carry offsets and reasons."""
        odd = self.tool.execute(mode="detect", payload=latin1_view(b"A\x00\x00"))["validation"]
        self.assertFalse(odd["utf-16-le"]["valid"])
        self.assertIn("odd-length", odd["utf-16-le"]["error"]["reason"])
        surrogate = self.tool.execute(mode="detect", payload=latin1_view("\U00010000".encode("utf-16-le")[:2]))["validation"]
        self.assertFalse(surrogate["utf-16-le"]["valid"])
        self.assertIn("surrogate", surrogate["utf-16-le"]["error"]["reason"])
        above = self.tool.execute(mode="detect", payload=latin1_view((0x110000).to_bytes(4, "little")))["validation"]
        self.assertFalse(above["utf-32-le"]["valid"])
        self.assertIn("above U+10FFFF", above["utf-32-le"]["error"]["reason"])

    def test_diagnose_findings(self):
        """Verify diagnose reports the mojibake signature, repair preview, and census findings."""
        original = "Café naïve — résumé “quotes”"
        mangled = original.encode("utf-8").decode("latin-1").encode("utf-8")
        result = self.tool.execute(mode="diagnose", payload=latin1_view(mangled))
        self.assertEqual(result["status"], "success")
        codes = [item["finding"] for item in result["findings"]]
        self.assertIn("mojibake_utf8_read_as_latin1", codes)
        self.assertIn("control_char_census", codes)
        self.assertIn("line_ending_census", codes)
        mojibake = next(item for item in result["findings"] if item["finding"] == "mojibake_utf8_read_as_latin1")
        self.assertEqual(mojibake["repair_preview"]["text"], original)

    def test_diagnose_bom_declared_mismatch(self):
        """Verify BOM-vs-declared mismatch flags the document author error."""
        payload = "hello".encode("utf-16")
        result = self.tool.execute(mode="diagnose", payload=latin1_view(payload), declared="utf-8")
        mismatch = next(item for item in result["findings"] if item["finding"] == "bom_vs_declared_mismatch")
        self.assertIn("BOM wins", mismatch["detail"])

    def test_diagnose_null_and_cp1252_hints(self):
        """Verify the null-ratio hint and the low-confidence cp1252/latin-1 note."""
        result = self.tool.execute(mode="diagnose", payload=latin1_view("latin text".encode("utf-16-le")))
        codes = [item["finding"] for item in result["findings"]]
        self.assertIn("null_byte_ratio", codes)
        result = self.tool.execute(mode="diagnose", payload=latin1_view("smart “quotes”".encode("cp1252")))
        note = next(item for item in result["findings"] if item["finding"] == "high_0x80_ratio_disambiguation")
        self.assertEqual(note["confidence"], "low")

    def test_diagnose_invalid_for_declared_offsets(self):
        """Verify invalid-for-declared findings carry the exact first error offset."""
        data = b"ok\xc3\x28bad"
        result = self.tool.execute(mode="diagnose", payload=latin1_view(data), declared="utf-8")
        invalid = next(item for item in result["findings"] if item["finding"] == "invalid_for_declared")
        self.assertEqual(invalid["first_error"]["offset"], 2)

    def test_line_census_counts(self):
        """Verify line-ending census decodes each way and counts CRLF/CR/LF."""
        text = "windows\r\nunix\noldmac\rmixed\r\n\n"
        result = self.tool.execute(mode="diagnose", payload=latin1_view(text.encode("utf-8")))
        census = next(item for item in result["findings"] if item["finding"] == "line_ending_census")
        self.assertEqual(census["by_decoding"]["utf-8"], {"crlf": 2, "cr": 1, "lf": 2})

    def test_repair_preview_mode(self):
        """Verify repair_preview decodes with bounded U+FFFD accounting."""
        result = self.tool.execute(mode="repair_preview", payload=latin1_view(b"good\xc3\x28bad\x80"), target="utf-8")
        self.assertEqual(result["target"], "utf-8")
        self.assertEqual(result["replacement_count"], 2)
        self.assertEqual(len(result["replacement_positions"]), 2)
        self.assertIn("\ufffd", result["preview"]["text"])
        clean = self.tool.execute(mode="repair_preview", payload="abc", target="utf-8")
        self.assertEqual(clean["replacement_count"], 0)

    def test_preview_is_capped(self):
        """Verify previews respect max_preview_chars."""
        long_text = "x" * 5000
        result = self.tool.execute(mode="repair_preview", payload=long_text, target="utf-8")
        self.assertEqual(len(result["preview"]["text"]), self.tool.max_preview_chars)
        self.assertTrue(result["preview"]["truncated"])
        self.assertEqual(result["preview"]["total_chars"], 5000)

    def test_config_validation_and_caps(self):
        """Verify misconfigured caps are rejected and payloads above the cap are refused."""
        self.assertIn("max_errors", EncodingDetectTool(max_errors=0).execute(mode="detect", payload="a")["error"])
        bounded = EncodingDetectTool(max_payload_bytes=8)
        self.assertIn("exceeds max_payload_bytes", bounded.execute(mode="detect", payload="123456789")["error"])
        self.assertIn("exceeds max_payload_bytes", bounded.execute(mode="detect", hex="41" * 10)["error"])

    def test_determinism_repeat_calls(self):
        """Verify identical inputs produce identical outputs across repeated calls."""
        payload = latin1_view("mixed 日本 text with — dashes".encode("utf-8"))  # noqa: UP012
        first = self.tool.execute(mode="diagnose", payload=payload)
        for _ in range(3):
            self.assertEqual(self.tool.execute(mode="diagnose", payload=payload), first)

    def test_empty_and_single_bytes(self):
        """Verify edge payloads return structured results, not exceptions."""
        empty = self.tool.execute(mode="detect", payload="")
        self.assertEqual(empty["winner"], "unknown")
        self.assertEqual(empty["candidates"], [])
        for byte in (b"\x00", b"\x41", b"\x80", b"\xff"):
            result = self.tool.execute(mode="detect", payload=latin1_view(byte))
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["length"], 1)


@unittest.skipUnless(HAS_CHARDET and HAS_CHARSET_NORMALIZER, "chardet and charset-normalizer oracles are not installed")
class EncodingDetectOracleBattery(unittest.TestCase):
    """Differential battery of 400 seeded payloads against codecs and detector oracles.

    Structural verdicts (utf-8 valid/invalid with the first error offset,
    utf-16/32 parity, and the BOM table) must match the stdlib codecs module
    exactly. Heuristic winners must be exact on the deterministic classes and
    explicitly low-confidence on the ambiguous latin-1/windows-1252 class,
    where the oracles themselves struggle.
    """

    @classmethod
    def setUpClass(cls):
        """Build the seeded 400-payload battery once for the whole class."""
        rng = random.Random(20261024)  # noqa: S311 - seeded deterministic fixtures
        cls.tool = EncodingDetectTool()
        cls.payloads = []
        for index, text in enumerate(SAMPLE_TEXTS):
            for repeat in (1, 3):
                body = text * repeat
                cls.payloads.append((body.encode("utf-8"), "utf-8"))
                cls.payloads.append((body.encode("utf-16"), "utf-16-bom"))
                cls.payloads.append((body.encode("utf-16-le"), "utf-16-le"))
                cls.payloads.append((body.encode("utf-16-be"), "utf-16-be"))
                cls.payloads.append((body.encode("utf-32"), "utf-32-bom"))
                cls.payloads.append((body.encode("utf-32-le"), "utf-32-le"))
                if index in (0, 1):
                    cls.payloads.append((body.encode("ascii", "ignore"), "ascii"))
                    cls.payloads.append((body.encode("latin-1", "ignore"), "latin-1"))
                    cls.payloads.append((body.encode("cp1252", "ignore"), "cp1252"))
                    if index == 1:
                        mangled = body.encode("utf-8").decode("latin-1").encode("utf-8")
                        cls.payloads.append((mangled, "mojibake"))
        cls.payloads.append((b"", "empty"))
        for byte in (0x00, 0x41, 0x80, 0xC3, 0xFF):
            cls.payloads.append((bytes([byte]), "single"))
        for _ in range(60):
            cls.payloads.append((bytes(rng.randrange(256) for _ in range(rng.randrange(1, 60))), "binary"))
        big = (SAMPLE_TEXTS[3] * 30000).encode("utf-8")[:1_000_000]
        while True:
            try:
                big.decode("utf-8")
                break
            except UnicodeDecodeError:
                big = big[:-1]
        cls.payloads.append((big, "utf-8"))
        cls.payloads.append((big.decode("utf-8").encode("utf-16")[:1_000_000], "utf-16-bom"))
        while len(cls.payloads) < 400:
            cls.payloads.append((bytes(rng.randrange(256) for _ in range(rng.randrange(1, 40))), "binary"))
        cls.results = [cls.tool.execute(mode="detect", payload=latin1_view(data)) for data, _ in cls.payloads]

    def test_utf8_verdicts_and_offsets_match_codecs_exactly(self):
        """Verify every payload's utf-8 verdict and first error offset equal the codec exception."""
        checked = 0
        for (data, _), result in zip(self.payloads, self.results, strict=True):
            expected_error = None
            try:
                data.decode("utf-8")
            except UnicodeDecodeError as exc:
                expected_error = exc.start
            validation = result["validation"]["utf-8"]
            if expected_error is None:
                self.assertTrue(validation["valid"], data[:16].hex())
                self.assertIsNone(validation["error"])
            else:
                self.assertFalse(validation["valid"], data[:16].hex())
                self.assertEqual(validation["error"]["offset"], expected_error, data[:16].hex())
            checked += 1
        self.assertGreater(checked, 300)

    def test_utf16_utf32_parity_with_codecs(self):
        """Verify utf-16/32 structural verdicts match strict codec decoding for every payload."""
        for (data, _), result in zip(self.payloads, self.results, strict=True):
            for encoding in ("utf-16-le", "utf-16-be", "utf-32-le", "utf-32-be"):
                try:
                    data.decode(encoding)
                    codec_valid = True
                except UnicodeDecodeError:
                    codec_valid = False
                self.assertEqual(result["validation"][encoding]["valid"], codec_valid, (encoding, data[:16].hex()))

    def test_bom_detection_matches_table(self):
        """Verify BOM sniffing equals the fixed signature table on every payload."""
        for (data, truth), result in zip(self.payloads, self.results, strict=True):
            bom = result["bom"]
            if data.startswith(b"\xef\xbb\xbf"):
                self.assertEqual((bom["name"], bom["offset_consumed"]), ("utf-8", 3))
            elif data.startswith(b"\xff\xfe\x00\x00"):
                self.assertEqual((bom["name"], bom["offset_consumed"]), ("utf-32-le", 4))
            elif data.startswith(b"\x00\x00\xfe\xff"):
                self.assertEqual((bom["name"], bom["offset_consumed"]), ("utf-32-be", 4))
            elif data.startswith(b"\xff\xfe"):
                self.assertEqual((bom["name"], bom["offset_consumed"]), ("utf-16-le", 2))
            elif data.startswith(b"\xfe\xff"):
                self.assertEqual((bom["name"], bom["offset_consumed"]), ("utf-16-be", 2))
            elif truth != "binary":
                self.assertFalse(bom["found"], data[:8].hex())

    def test_deterministic_classes_winner_is_structural_truth(self):
        """Verify winners are exact on BOM, ascii, utf-8, and null-patterned utf-16/32 classes."""
        deterministic = {
            "utf-8-bom": "utf-8",
            "utf-16-bom": "utf-16-le",
            "utf-32-bom": "utf-32-le",
            "utf-16-le": "utf-16-le",
            "utf-16-be": "utf-16-be",
            "utf-32-le": "utf-32-le",
            "utf-8": "utf-8",
            "ascii": "ascii",
            "empty": "unknown",
        }
        checked = 0
        for (data, truth), result in zip(self.payloads, self.results, strict=True):
            if truth not in deterministic:
                continue
            expected = deterministic[truth]
            if expected == "utf-8" and all(byte < 0x80 for byte in data):
                expected = "ascii"
            null_ratio = sum(1 for byte in data if byte == 0) / max(len(data), 1)
            if truth in {"utf-16-le", "utf-16-be"} and null_ratio < 0.25:
                # utf-16 without NUL padding and without a BOM has no
                # deterministic evidence; it belongs to the ambiguous bucket
                continue
            self.assertEqual(result["winner"], expected, (truth, data[:16].hex()))
            checked += 1
        self.assertGreater(checked, 45)

    def test_ambiguous_class_is_low_confidence_with_both_candidates(self):
        """Verify latin-1/windows-1252 payloads stay below 0.7 confidence with both listed when ambiguous."""
        # cp1252 smart quotes carry 0x80-0x9F bytes, so both readings are live options
        smart = "He said “don’t” — it’s a naïve café… €100".encode("cp1252")  # noqa: RUF001
        result = self.tool.execute(mode="detect", payload=latin1_view(smart))
        names = {item["encoding"] for item in result["candidates"]}
        self.assertIn("latin-1", names)
        self.assertIn("windows-1252", names)
        self.assertLess(result["candidates"][0]["confidence"], 0.7)
        chardet_result = chardet.detect(smart)
        self.assertTrue(
            chardet_result["encoding"] != "cp1252" or chardet_result["confidence"] < 0.7,
            f"oracle unexpectedly confident on cp1252: {chardet_result}",
        )
        # latin-1 accents above 0x9F only: structurally consistent single 8-bit reading
        accents = "À côté de l'église, le garçon café naïve résumé".encode("latin-1")
        result = self.tool.execute(mode="detect", payload=latin1_view(accents))
        self.assertEqual(result["winner"], "latin-1")
        self.assertLess(result["candidates"][0]["confidence"], 0.7)
        chardet_result = chardet.detect(accents)
        self.assertTrue(
            chardet_result["encoding"] != "latin-1" or chardet_result["confidence"] < 0.7,
            f"oracle unexpectedly confident on latin-1: {chardet_result}",
        )

    def test_agreement_rates_are_reported(self):
        """Report (not pin) heuristic agreement with chardet and charset-normalizer."""
        def normalize(name):
            if name is None:
                return None
            name = name.lower().replace("_", "-")
            aliases = {
                "utf-16": "utf-16-le",
                "utf-16le": "utf-16-le",
                "utf-16be": "utf-16-be",
                "utf-32": "utf-32-le",
                "utf8": "utf-8",
                "windows-1252": "windows-1252",
                "cp1252": "windows-1252",
            }
            return aliases.get(name, name)

        tool_hits = chardet_hits = normalizer_hits = total = 0
        for (data, truth), result in zip(self.payloads, self.results, strict=True):
            if truth in {"empty", "single", "binary", "mojibake"} or len(data) > 100_000:
                continue
            expected = {"utf-16-bom": "utf-16-le", "utf-32-bom": "utf-32-le", "cp1252": "windows-1252"}.get(truth, truth)
            if expected == "utf-8" and all(byte < 0x80 for byte in data):
                expected = "ascii"
            total += 1
            if result["winner"] == expected:
                tool_hits += 1
            if normalize(chardet.detect(data)["encoding"]) == expected:
                chardet_hits += 1
            best = charset_normalizer.from_bytes(data).best()
            if best is not None and normalize(best.encoding) == expected:
                normalizer_hits += 1
        rates = {
            "tool": tool_hits / total,
            "chardet": chardet_hits / total,
            "charset_normalizer": normalizer_hits / total,
        }
        print(
            f"\nagreement rates over {total} labeled payloads: "
            f"tool={rates['tool']:.1%} chardet={rates['chardet']:.1%} charset_normalizer={rates['charset_normalizer']:.1%}"
        )
        self.assertGreater(total, 70)


class MojibakeBattery(unittest.TestCase):
    """Repair battery: 100 real-text utf-8 payloads mangled through latin-1 chains."""

    @classmethod
    def setUpClass(cls):
        """Build the 100-payload mojibake battery once from non-ASCII text."""
        rng = random.Random(20261025)  # noqa: S311 - seeded deterministic fixtures
        cls.tool = EncodingDetectTool()
        non_ascii = [text for text in SAMPLE_TEXTS if any(ord(char) > 127 for char in text)]
        cls.cases = []
        index = 0
        while len(cls.cases) < 100:
            text = non_ascii[index % len(non_ascii)]
            index += 1
            start = rng.randrange(0, max(1, len(text) // 2))
            snippet = text[start:]
            if not any(ord(char) > 127 for char in snippet):
                snippet = text
            once = snippet.encode("utf-8").decode("latin-1").encode("utf-8")
            twice = once.decode("latin-1").encode("utf-8")
            cls.cases.append((snippet, once, twice))

    def test_one_level_mojibake_round_trip(self):
        """Verify one-level mangled payloads recover the original text exactly."""
        recovered = 0
        for original, once, _ in self.cases:
            result = self.tool.execute(mode="diagnose", payload=latin1_view(once))
            finding = next((item for item in result["findings"] if item["finding"] == "mojibake_utf8_read_as_latin1"), None)
            self.assertIsNotNone(finding, original[:20])
            self.assertEqual(finding["repair_preview"]["text"], original)
            self.assertEqual(finding["repair_preview"]["text"].encode("utf-8").decode("utf-8"), original)
            recovered += 1
        self.assertEqual(recovered, len(self.cases))

    def test_two_level_mojibake_flagged_best_effort(self):
        """Verify two-level mangled payloads are flagged and repaired best-effort."""
        flagged = 0
        recovered = 0
        for original, _, twice in self.cases:
            result = self.tool.execute(mode="diagnose", payload=latin1_view(twice))
            finding = next((item for item in result["findings"] if item["finding"] == "mojibake_utf8_read_as_latin1"), None)
            self.assertIsNotNone(finding, original[:20])
            if finding["levels"] > 1:
                flagged += 1
            if finding["repair_preview"]["text"] == original:
                recovered += 1
        print(f"\ntwo-level mojibake: flagged={flagged}/{len(self.cases)} recovered={recovered}/{len(self.cases)}")
        self.assertEqual(flagged, len(self.cases))
        self.assertGreaterEqual(recovered / len(self.cases), 0.9)

    def test_clean_text_has_no_double_mojibake_finding(self):
        """Verify plain multilingual utf-8 text stays at info severity and never flags double encoding."""
        for text in SAMPLE_TEXTS:
            result = self.tool.execute(mode="diagnose", payload=latin1_view(text.encode("utf-8")))
            codes = [item["finding"] for item in result["findings"]]
            self.assertNotIn("double_mojibake", codes)
            finding = next((item for item in result["findings"] if item["finding"] == "mojibake_utf8_read_as_latin1"), None)
            if finding is not None:
                self.assertEqual(finding["severity"], "info")
                self.assertEqual(finding["levels"], 1)
                self.assertEqual(finding["repair_preview"]["text"], text)


class ValidateUtf8OffsetBattery(unittest.TestCase):
    """Offset battery: 300 mutated payloads checked against decode exception positions."""

    @classmethod
    def setUpClass(cls):
        """Build the 300 mutated payloads once."""
        rng = random.Random(20261026)  # noqa: S311 - seeded deterministic fixtures
        cls.tool = EncodingDetectTool()
        cls.cases = []
        for index in range(300):
            text = (SAMPLE_TEXTS[index % len(SAMPLE_TEXTS)] * 2).encode("utf-8")
            data = bytearray(text)
            mutations = rng.randrange(0, 4)
            for _ in range(mutations):
                position = rng.randrange(len(data))
                data[position] = rng.choice([0x00, 0x28, 0x7F, 0x80, 0xBF, 0xC0, 0xC1, 0xE0, 0xED, 0xF0, 0xF4, 0xF5, 0xFE, 0xFF])
            if rng.randrange(5) == 0:
                data = data[: rng.randrange(1, len(data))]
            cls.cases.append(bytes(data))

    def test_offsets_match_exception_starts(self):
        """Verify the valid flag and first error offset equal the stdlib exception."""
        mismatches = []
        for data in self.cases:
            expected_start = None
            try:
                data.decode("utf-8")
            except UnicodeDecodeError as exc:
                expected_start = exc.start
            result = self.tool.execute(mode="validate_utf8", payload=latin1_view(data))
            if expected_start is None:
                if not result["valid"]:
                    mismatches.append((data.hex(), "false invalid"))
            else:
                if result["valid"]:
                    mismatches.append((data.hex(), "false valid"))
                elif result["errors"][0]["offset"] != expected_start:
                    mismatches.append((data.hex(), expected_start, result["errors"][0]["offset"]))
        self.assertEqual(mismatches, [])

    def test_error_offsets_are_monotonic(self):
        """Verify reported error offsets are strictly increasing and within the payload."""
        for data in self.cases:
            result = self.tool.execute(mode="validate_utf8", payload=latin1_view(data))
            offsets = [item["offset"] for item in result["errors"]]
            self.assertEqual(offsets, sorted(offsets))
            self.assertTrue(all(0 <= offset < len(data) for offset in offsets))


class EncodingDetectRegistrationTest(unittest.TestCase):
    """Unit tests for registering the shipped encoding_detect_tool.yaml as a tool component."""

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
        """Verify the shipped yaml resolves to a tool component exposing the EncodingDetectTool class."""
        component = ComponentConfiger().load_by_configer(self.config)
        self.assertEqual(component.get_component_config_type(), ComponentEnum.TOOL.value)
        self.assertEqual(component.metadata_class, "EncodingDetectTool")

    def test_manager(self):
        """Verify the EncodingDetectTool is resolvable and correctly configured via ToolManager."""
        configer = ToolConfiger().load_by_configer(self.config)
        app = AppConfiger()
        app.tool_configer_map = {configer.name: configer}
        ApplicationConfigManager().app_configer = app
        tool = ToolManager().get_instance_obj(configer.name)
        self.assertIsInstance(tool, EncodingDetectTool)
        self.assertEqual(tool.input_keys, ["mode"])


if __name__ == "__main__":
    unittest.main()
