# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2026/10/19
# @FileName: test_pii_reporter.py

import json
import unittest

from agentuniverse.agent.action.knowledge.doc_processor.pii_reporter import PIIReporter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def _cn_id_check_digit(first_17: str) -> str:
    """Compute the GB 11643 check character for a 17-digit prefix."""
    weights = (7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2)
    total = sum(int(d) * w for d, w in zip(first_17, weights))
    return "10X98765432"[total % 11]


def _cn_id(prefix_17: str) -> str:
    """Build a checksum-valid 18-character China resident ID."""
    return prefix_17 + _cn_id_check_digit(prefix_17)


def _cn_id_invalid(prefix_17: str) -> str:
    """Build an 18-character ID whose check character is provably wrong."""
    good = _cn_id_check_digit(prefix_17)
    bad = "X" if good != "X" else "0"
    return prefix_17 + bad


# Fixtures with correct checksums, constructed rather than transcribed.
CN_ID_VALID = _cn_id("11010119900307851")      # ends with '5'
CN_ID_VALID_2 = _cn_id("44030119981228002")    # different region/date/sequence
CN_ID_BAD_CHECKSUM = _cn_id_invalid("11010119900307851")

# Standard Luhn-valid / Luhn-invalid card strings.
CARD_VALID_SPACED = "4111 1111 1111 1111"      # classic Visa test number
CARD_VALID_DASHED = "3782-8224-6310-005"       # 15-digit Amex shape
CARD_VALID_FLAT = "5500005555555559"           # 16-digit contiguous
CARD_LUHN_FAIL = "4111 1111 1111 1112"         # one digit off -> numeric_id

# Standard published test IBANs (mod-97 valid).
IBAN_DE = "DE89 3704 0044 0532 0130 00"
IBAN_GB = "GB33 BUKB 2020 1555 5555 55"
IBAN_FR = "FR14 2004 1010 0505 0001 3M02 606"  # BBAN contains a letter
IBAN_NL_FLAT = "NL91ABNA0417164300"             # contiguous electronic form
IBAN_BAD_CHECK = "DE89 3704 0044 0532 0130 09"  # wrong check digits
IBAN_BAD_LENGTH = "DE89 3704 0044 0532"         # plausible but truncated
IBAN_BAD_COUNTRY = "QQ12 3456 7890 1234 5678"   # unsupported country code


def _doc(text: str, **metadata) -> Document:
    """Build a Document carrying `text` and optional metadata."""
    return Document(text=text, metadata=dict(metadata) or None)


class TestPIIReporter(unittest.TestCase):
    """Comprehensive test suite for PIIReporter."""

    def setUp(self):
        self.reporter = PIIReporter()
        self.query = Query(query_str="pii audit")

    def _create_configer(self, config_dict):
        """Create a ComponentConfiger from a plain dictionary."""
        cfg = Configer()
        cfg.value = config_dict
        configer = ComponentConfiger()
        configer.load_by_configer(cfg)
        return configer

    def _findings(self, text):
        """Run the reporter over one document and return its pii list."""
        doc = _doc(text)
        self.reporter.process_docs([doc], self.query)
        return doc.metadata["pii"], doc.metadata["pii_counts"], \
            doc.metadata["pii_risk"]

    def _kinds(self, text):
        return [f["kind"] for f in self._findings(text)[0]]

    # ========== Initialization tests ==========

    def test_default_configuration(self):
        reporter = PIIReporter()
        self.assertEqual(set(reporter.kinds), {
            "email", "phone", "card", "numeric_id",
            "cn_id", "iban", "passport_candidate"})
        self.assertEqual(reporter.max_findings, 100)
        self.assertEqual(reporter.pii_key, "pii")
        self.assertEqual(reporter.counts_key, "pii_counts")
        self.assertEqual(reporter.risk_key, "pii_risk")

    def test_initialize_by_component_configer(self):
        configer = self._create_configer({
            "name": "pii_reporter",
            "description": "audit pass",
            "kinds": ["email", "iban"],
            "max_findings": 7,
            "pii_key": "audit",
            "counts_key": "audit_counts",
            "risk_key": "audit_risk",
            "metadata": {"type": "DOC_PROCESSOR",
                         "module": "agentuniverse.agent.action.knowledge."
                                   "doc_processor.pii_reporter",
                         "class": "PIIReporter"},
        })
        reporter = PIIReporter()
        reporter._initialize_by_component_configer(configer)
        self.assertEqual(reporter.name, "pii_reporter")
        self.assertEqual(reporter.kinds, ["email", "iban"])
        self.assertEqual(reporter.max_findings, 7)
        self.assertEqual(reporter.pii_key, "audit")
        self.assertEqual(reporter.counts_key, "audit_counts")
        self.assertEqual(reporter.risk_key, "audit_risk")

    def test_invalid_configuration_raises(self):
        # Unknown kind fails eagerly at load time, not silently at runtime.
        base = {"name": "pii_reporter", "description": "audit"}
        configer = self._create_configer(
            dict(base, kinds=["email", "bogus"]))
        with self.assertRaises(ValueError):
            PIIReporter()._initialize_by_component_configer(configer)

        configer = self._create_configer(dict(base, max_findings=0))
        with self.assertRaises(ValueError):
            PIIReporter()._initialize_by_component_configer(configer)

        configer = self._create_configer(dict(base, max_findings="many"))
        with self.assertRaises(ValueError):
            PIIReporter()._initialize_by_component_configer(configer)

        configer = self._create_configer(dict(base, kinds=[]))
        with self.assertRaises(ValueError):
            PIIReporter()._initialize_by_component_configer(configer)

    def test_invalid_attributes_raise_on_process(self):
        # Attributes set directly (not via configer) are validated before
        # any processing happens.
        reporter = PIIReporter()
        reporter.kinds = ["nope"]
        with self.assertRaises(ValueError):
            reporter.process_docs([_doc("hello")], self.query)

        reporter = PIIReporter()
        reporter.max_findings = -1
        with self.assertRaises(ValueError):
            reporter.process_docs([_doc("hello")], self.query)

    # ========== Email tests ==========

    def test_email_detected_masked_and_spanned(self):
        text = "Reach out to john.doe@example.com anytime."
        findings, counts, risk = self._findings(text)
        self.assertEqual(counts, {"email": 1})
        self.assertEqual(risk, "low")
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding["kind"], "email")
        self.assertEqual(finding["text"], "jo***om")
        self.assertEqual(finding["span"],
                         [text.index("john.doe@example.com"),
                          text.index("john.doe@example.com") + 20])
        self.assertEqual(finding["confidence"], "high")
        # Span actually points at the value it claims.
        self.assertEqual(text[finding["span"][0]:finding["span"][1]],
                         "john.doe@example.com")

    def test_multiple_emails_counted(self):
        text = "a@x.io, b@y.org and c@z.net"
        findings, counts, _ = self._findings(text)
        self.assertEqual(counts, {"email": 3})
        self.assertEqual(len(findings), 3)

    # ========== Phone tests ==========

    def test_phone_variants_detected(self):
        for phone in ["13700138000",                      # CN mobile
                      "(555) 123-4567",                   # NANP, parens
                      "555-123-4567",                     # NANP, dashes
                      "555.123.4567",                     # NANP, dots
                      "1-555-123-4567",                   # NANP, leading 1
                      "+86 137 0013 8000",                # intl separated
                      "+441234567890",                    # intl contiguous
                      "+1 202 555 0179"]:                 # intl NANP style
            text = f"call {phone} today"
            findings, counts, _ = self._findings(text)
            self.assertEqual(counts, {"phone": 1}, msg=phone)
            self.assertEqual(findings[0]["span"],
                             [text.index(phone),
                              text.index(phone) + len(phone)], msg=phone)
            self.assertEqual(findings[0]["confidence"], "medium")

    def test_phone_guards_against_dates_and_math(self):
        # Dates, ordinals, versions and arithmetic must not be phones.
        for text in ["meeting on 2023-01-15 went well",
                     "due 12/05/2023 at noon",
                     "released 15.01.2024 worldwide",
                     "the 3rd quarter started",
                     "version 1.2.3 shipped",
                     "Q3 2024 earnings call",
                     "in the year 2024 things changed",
                     "sum 3 +86 137 0013 8000 equals x",
                     "growth = 44 123 456 7890 units",
                     "chapter 12 verse 345678"]:
            self.assertNotIn("phone", self._kinds(text), msg=text)

    def test_phone_arithmetic_guard_only_blocks_operands(self):
        # A '+' directly preceded by a number is addition; the same digits
        # without that context are a phone.
        self.assertNotIn("phone",
                         self._kinds("total 3 +86 137 0013 8000 ok"))
        self.assertIn("phone",
                      self._kinds("total: +86 137 0013 8000 ok"))

    def test_phone_not_confused_with_digit_runs(self):
        # A bare 10-digit run without separators or country code is too
        # ambiguous to report as a phone.
        self.assertNotIn("phone", self._kinds("id 1234567890 end"))

    # ========== Credit card tests ==========

    def test_luhn_valid_card_detected(self):
        for card in [CARD_VALID_SPACED, CARD_VALID_DASHED, CARD_VALID_FLAT]:
            text = f"pay with {card} now"
            findings, counts, risk = self._findings(text)
            self.assertEqual(counts, {"card": 1}, msg=card)
            self.assertEqual(risk, "high")
            self.assertEqual(findings[0]["kind"], "card")
            self.assertEqual(findings[0]["confidence"], "high")
            self.assertEqual(findings[0]["span"],
                             [text.index(card), text.index(card) + len(card)])

    def test_luhn_invalid_run_reported_as_numeric_id(self):
        text = f"bad number {CARD_LUHN_FAIL} here"
        findings, counts, risk = self._findings(text)
        self.assertEqual(counts, {"numeric_id": 1})
        self.assertEqual(risk, "medium")
        self.assertEqual(findings[0]["kind"], "numeric_id")
        self.assertEqual(findings[0]["confidence"], "medium")

    def test_short_and_long_digit_runs_ignored(self):
        # 12 digits and 20 digits are outside the 13-19 card window.
        self.assertEqual(self._kinds("ref 123456789012 end"), [])
        self.assertEqual(
            self._kinds("ref 12345678901234567890 end"), [])

    def test_card_inside_arithmetic_not_numeric_id(self):
        # Luhn-failing runs inherit the arithmetic guard.
        self.assertEqual(self._kinds("x = 1234567890123 + 1"), [])

    # ========== China resident ID tests ==========

    def test_valid_cn_id_detected(self):
        for cn_id in [CN_ID_VALID, CN_ID_VALID_2]:
            text = f"applicant {cn_id} signed"
            findings, counts, risk = self._findings(text)
            self.assertEqual(counts, {"cn_id": 1}, msg=cn_id)
            self.assertEqual(risk, "high")
            self.assertEqual(findings[0]["kind"], "cn_id")
            self.assertEqual(findings[0]["confidence"], "high")
            self.assertEqual(findings[0]["text"], cn_id[:2] + "***" + cn_id[-2:])

    def test_checksum_failing_cn_id_not_reported_as_cn_id(self):
        # Same shape, wrong GB 11643 check character: falls back to the
        # weaker numeric_id reading of the leading digit run.
        text = f"applicant {CN_ID_BAD_CHECKSUM} signed"
        findings, counts, _ = self._findings(text)
        self.assertNotIn("cn_id", counts)
        self.assertEqual(counts, {"numeric_id": 1})
        # Only the 17 pure digits before the check character are
        # card-shaped; the masked text corresponds to that run.
        digit_run = CN_ID_BAD_CHECKSUM[:17]
        self.assertEqual(findings[0]["text"],
                         digit_run[:2] + "***" + digit_run[-2:])

    def test_valid_cn_id_wins_overlap_with_card_shape(self):
        # A valid 18-digit resident ID is also a card-shaped digit run,
        # but only the stronger cn_id finding is reported.
        text = f"id {CN_ID_VALID} end"
        self.assertEqual(self._kinds(text), ["cn_id"])

    def test_cn_id_check_digit_helper(self):
        # The fixture builder itself: known GB 11643 example.
        self.assertEqual(_cn_id_check_digit("11010119900307851"), "5")
        self.assertEqual(CN_ID_VALID, "110101199003078515")
        self.assertNotEqual(CN_ID_VALID[-1], CN_ID_BAD_CHECKSUM[-1])

    # ========== IBAN tests ==========

    def test_valid_ibans_detected(self):
        for iban in [IBAN_DE, IBAN_GB, IBAN_FR, IBAN_NL_FLAT]:
            text = f"transfer to {iban} ok"
            findings, counts, risk = self._findings(text)
            self.assertEqual(counts, {"iban": 1}, msg=iban)
            self.assertEqual(risk, "high")
            self.assertEqual(findings[0]["kind"], "iban")
            self.assertEqual(findings[0]["confidence"], "high")
            self.assertEqual(
                findings[0]["span"],
                [text.index(iban), text.index(iban) + len(iban)], msg=iban)

    def test_invalid_ibans_rejected(self):
        # Wrong check digits, truncated length, unsupported country and
        # lowercase form are all rejected by the mod-97/length checks.
        for iban in [IBAN_BAD_CHECK, IBAN_BAD_LENGTH, IBAN_BAD_COUNTRY,
                     IBAN_DE.lower()]:
            text = f"transfer to {iban} ok"
            self.assertNotIn("iban", self._kinds(text), msg=iban)

    def test_chained_ibans_all_found(self):
        # Space-separated IBANs in a list: the greedy shape must not
        # swallow neighbours, and each validates on its own span.
        text = f"{IBAN_GB} {IBAN_DE} and {IBAN_FR}"
        findings, counts, _ = self._findings(text)
        self.assertEqual(counts, {"iban": 3})
        spans = [tuple(f["span"]) for f in findings]
        self.assertEqual(spans, [(0, len(IBAN_GB)),
                                 (len(IBAN_GB) + 1,
                                  len(IBAN_GB) + 1 + len(IBAN_DE)),
                                 (text.index(IBAN_FR),
                                  text.index(IBAN_FR) + len(IBAN_FR))])

    def test_iban_wins_overlap_with_digit_runs(self):
        # The digit tail of an IBAN is card-shaped; only the iban finding
        # is reported, with the full span.
        text = f"acct {IBAN_DE} end"
        self.assertEqual(self._kinds(text), ["iban"])

    def test_mod97_accepts_and_rejects(self):
        from agentuniverse.agent.action.knowledge.doc_processor \
            .pii_reporter import _iban_ok
        self.assertTrue(_iban_ok(IBAN_DE.replace(" ", "")))
        self.assertTrue(_iban_ok(IBAN_GB.replace(" ", "")))
        # Flip the final check digit -> mod-97 no longer 1.
        self.assertFalse(_iban_ok(IBAN_DE.replace(" ", "")[:-1] + "1"))

    # ========== Passport candidate tests ==========

    def test_passport_candidate_low_confidence(self):
        text = "passport AB123456 issued"
        findings, counts, risk = self._findings(text)
        self.assertEqual(counts, {"passport_candidate": 1})
        self.assertEqual(risk, "low")
        self.assertEqual(findings[0]["kind"], "passport_candidate")
        self.assertEqual(findings[0]["confidence"], "low")
        self.assertEqual(findings[0]["text"], "AB***56")

    def test_passport_shape_guards(self):
        # Trailing letters/digits or lowercase disqualify the candidate.
        for token in ["AB123456C", "ab123456", "AB12345", "AB1234567"]:
            self.assertEqual(self._kinds(f"ref {token} end"), [], msg=token)

    # ========== Masking invariant tests ==========

    def test_metadata_never_contains_full_values(self):
        secrets = ["john.doe@example.com", "4111 1111 1111 1111",
                   CN_ID_VALID, IBAN_GB, "13700138000", "AB123456"]
        text = ("email john.doe@example.com card 4111 1111 1111 1111 id " +
                CN_ID_VALID + " iban " + IBAN_GB +
                " mobile 13700138000 passport AB123456 end")
        doc = _doc(text)
        self.reporter.process_docs([doc], self.query)
        dumped = json.dumps(doc.metadata)
        for secret in secrets:
            self.assertNotIn(secret, dumped, msg=secret)
            self.assertNotIn(secret.replace(" ", ""), dumped, msg=secret)
        # The masked forms ARE present.
        for masked in ["jo***om", "41***11", "11***15", "GB***55",
                       "13***00", "AB***56"]:
            self.assertIn(masked, dumped)

    def test_masking_shape(self):
        from agentuniverse.agent.action.knowledge.doc_processor \
            .pii_reporter import _mask
        self.assertEqual(_mask("abcdefgh"), "ab***gh")
        self.assertEqual(_mask("abcdef"), "ab***ef")
        self.assertEqual(_mask("abcde"), "ab***de")
        self.assertEqual(_mask("abcd"), "***")   # nothing revealed
        self.assertEqual(_mask("ab"), "***")
        self.assertNotIn("cdef", _mask("abcdefgh"))

    def test_spans_point_at_real_values(self):
        text = f"card {CARD_VALID_SPACED} id {CN_ID_VALID}"
        findings, _, _ = self._findings(text)
        for finding in findings:
            start, end = finding["span"]
            raw = text[start:end]
            # The masked text corresponds to the span content.
            self.assertEqual(finding["text"],
                             raw[:2] + "***" + raw[-2:])
            # And the raw value leaked nowhere into metadata.
            self.assertNotIn(raw, json.dumps(findings))

    # ========== Risk level tests ==========

    def test_risk_levels_per_kind(self):
        cases = [
            ("nothing personal here", "none", {}),
            ("mail a@b.co", "low", {"email": 1}),
            ("passport AB123456", "low", {"passport_candidate": 1}),
            ("call 13700138000", "medium", {"phone": 1}),
            ("ref 1234567890123", "medium", {"numeric_id": 1}),
            ("pay 4111111111111111", "high", {"card": 1}),
            (f"id {CN_ID_VALID}", "high", {"cn_id": 1}),
            (f"acct {IBAN_GB}", "high", {"iban": 1}),
        ]
        for text, risk, counts in cases:
            _, got_counts, got_risk = self._findings(text)
            self.assertEqual(got_risk, risk, msg=text)
            self.assertEqual(got_counts, counts, msg=text)

    def test_risk_is_maximum_across_kinds(self):
        text = f"mail a@b.co pay {CARD_VALID_SPACED}"
        _, counts, risk = self._findings(text)
        self.assertEqual(risk, "high")
        self.assertEqual(counts, {"email": 1, "card": 1})

    # ========== Cap behaviour tests ==========

    def test_findings_capped_counts_not(self):
        emails = " ".join(f"user{i}@example.com" for i in range(120))
        doc = _doc(emails)
        self.reporter.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata["pii"]), 100)
        self.assertEqual(doc.metadata["pii_counts"], {"email": 120})
        self.assertEqual(doc.metadata["pii_risk"], "low")

    def test_max_findings_configurable(self):
        emails = " ".join(f"user{i}@example.com" for i in range(10))
        reporter = PIIReporter()
        reporter.max_findings = 3
        doc = _doc(emails)
        reporter.process_docs([doc], self.query)
        self.assertEqual(len(doc.metadata["pii"]), 3)
        self.assertEqual(doc.metadata["pii_counts"], {"email": 10})

    def test_capped_list_keeps_document_order(self):
        text = "first a@b.co then " + CARD_VALID_SPACED + " last c@d.co"
        findings, _, _ = self._findings(text)
        self.assertEqual([f["kind"] for f in findings],
                         ["email", "card", "email"])

    # ========== No-PII / empty documents ==========

    def test_clean_document_risk_none(self):
        text = "Just an ordinary sentence about the weather in Lisbon."
        findings, counts, risk = self._findings(text)
        self.assertEqual(findings, [])
        self.assertEqual(counts, {})
        self.assertEqual(risk, "none")

    def test_empty_and_none_text(self):
        for text in ["", "   "]:
            findings, counts, risk = self._findings(text)
            self.assertEqual((findings, counts, risk), ([], {}, "none"))
        doc = Document(text=None, id="d1", metadata=None)
        self.reporter.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["pii"], [])
        self.assertEqual(doc.metadata["pii_risk"], "none")

    def test_empty_document_list(self):
        self.assertEqual(self.reporter.process_docs([], self.query), [])

    # ========== Text-integrity tests ==========

    def test_text_and_id_never_modified(self):
        text = (f"email john@example.com card {CARD_VALID_SPACED} id "
                f"{CN_ID_VALID} iban {IBAN_GB} phone 13700138000")
        doc = _doc(text, source="intake", rank=3)
        doc_id = doc.id
        self.reporter.process_docs([doc], self.query)
        self.assertEqual(doc.text, text)
        self.assertEqual(doc.id, doc_id)
        # Pre-existing metadata survives alongside the new keys.
        self.assertEqual(doc.metadata["source"], "intake")
        self.assertEqual(doc.metadata["rank"], 3)
        self.assertIn("pii", doc.metadata)

    def test_metadata_mapping_copied_before_mutation(self):
        original = {"source": "wire"}
        doc = _doc("a@b.co", source="wire")
        doc.metadata = original
        self.reporter.process_docs([doc], self.query)
        self.assertIsNot(doc.metadata, original)
        self.assertNotIn("pii", original)

    def test_disabled_keys_stamp_nothing(self):
        reporter = PIIReporter()
        reporter.pii_key = ""
        reporter.counts_key = ""
        reporter.risk_key = ""
        doc = _doc("a@b.co")
        reporter.process_docs([doc], self.query)
        self.assertEqual(doc.metadata, {})

    # ========== Determinism tests ==========

    def test_deterministic_across_runs(self):
        text = (f"card {CARD_VALID_SPACED} bad {CARD_LUHN_FAIL} id "
                f"{CN_ID_VALID} iban {IBAN_GB} mail a@b.co call +86 137 0013 8000")
        doc_a, doc_b = _doc(text), _doc(text)
        self.reporter.process_docs([doc_a], self.query)
        self.reporter.process_docs([doc_b], self.query)
        self.assertEqual(doc_a.metadata, doc_b.metadata)

    # ========== Kind selection tests ==========

    def test_kinds_subset_restricts_detection(self):
        reporter = PIIReporter()
        reporter.kinds = ["email"]
        text = f"mail a@b.co pay {CARD_VALID_SPACED} id {CN_ID_VALID}"
        doc = _doc(text)
        reporter.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["pii_counts"], {"email": 1})
        self.assertEqual(doc.metadata["pii_risk"], "low")

    def test_card_without_numeric_id(self):
        reporter = PIIReporter()
        reporter.kinds = ["card"]
        doc = _doc(f"good {CARD_VALID_SPACED} bad {CARD_LUHN_FAIL}")
        reporter.process_docs([doc], self.query)
        self.assertEqual(doc.metadata["pii_counts"], {"card": 1})

    # ========== Overlap resolution tests ==========

    def test_intl_phone_not_double_reported_as_numeric_id(self):
        # "+1 202 555 0179" is a 13-digit run with the plus; phone wins.
        text = "call +1 202 555 0179 now"
        self.assertEqual(self._kinds(text), ["phone"])

    def test_overlaps_resolve_to_strongest_kind(self):
        # IBAN text contains card/passport-shaped substrings; only the
        # checksum-validated reading survives.
        text = f"{IBAN_GB} {IBAN_NL_FLAT}"
        self.assertEqual(self._kinds(text), ["iban", "iban"])

    # ========== Pipeline-shape tests ==========

    def test_returns_same_documents_in_order(self):
        docs = [_doc("a@b.co"), _doc("clean text"), _doc("13700138000")]
        result = self.reporter.process_docs(docs, self.query)
        self.assertIs(result, docs)
        self.assertEqual([d.text for d in result],
                         ["a@b.co", "clean text", "13700138000"])
        self.assertEqual([d.metadata["pii_risk"] for d in result],
                         ["low", "none", "medium"])


if __name__ == '__main__':
    unittest.main()
