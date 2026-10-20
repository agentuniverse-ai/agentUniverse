"""Known-answer, tamper, and discipline tests for AuSecHmacTool (au-sec #1).

Frozen digests were machine-printed from the stdlib reference (hmac, hashlib)
before the test was written; V1/V2 additionally match RFC 4231 test cases 2/1.
"""

import hmac as hmac_stdlib
import unittest

from agentuniverse.agent.action.tool.common_tool.au_sec_hmac_tool import AuSecHmacTool

V1_JEFE = "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"
V2_RFC4231C1 = "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"
V3_OURKEY_A = "5102b3cb547ef4d94bd56f443cc86bd20f8e1d40c4930923de58ed1437a5af2d"
V4_OURKEY_B = "b7b54fb6b52725b34c89ed1fa6d905319239a9c6a97113a170eaf8e88f9ab4c4"


class AuSecHmacToolTest(unittest.TestCase):
    def _tool(self):
        return AuSecHmacTool()

    def test_sign_matches_rfc4231_vectors(self):
        got = self._tool().execute(action="sign", key="Jefe", message="what do ya want for nothing?")
        self.assertEqual(got["digest"], V1_JEFE)
        got = self._tool().execute(action="sign", key="\x0b" * 20, message="Hi There")
        self.assertEqual(got["digest"], V2_RFC4231C1)

    def test_sign_matches_frozen_ourkey_answers(self):
        tool = self._tool()
        self.assertEqual(tool.execute(action="sign", key="yue-sec-key", message="yue-sec-message")["digest"], V3_OURKEY_A)
        self.assertEqual(tool.execute(action="sign", key="yue-sec-key", message="tampered-message")["digest"], V4_OURKEY_B)

    def test_sign_matches_stdlib_reference_on_bounded_long_message(self):
        got = self._tool().execute(action="sign", key="k", message="x" * 4096)
        want = hmac_stdlib.new(b"k", b"x" * 4096, "sha256").hexdigest()
        self.assertEqual(got["digest"], want)

    def test_verify_valid_and_tampered(self):
        tool = self._tool()
        got = tool.execute(action="verify", key="yue-sec-key", message="yue-sec-message", signature=V3_OURKEY_A)
        self.assertTrue(got["valid"])
        got = tool.execute(action="verify", key="yue-sec-key", message="tampered-message", signature=V3_OURKEY_A)
        self.assertFalse(got["valid"])

    def test_compare_constant_time_discipline(self):
        tool = self._tool()
        got = tool.execute(action="compare", signature=V3_OURKEY_A, other=V3_OURKEY_A)
        self.assertTrue(got["equal"])
        got = tool.execute(action="compare", signature=V3_OURKEY_A, other=V4_OURKEY_B)
        self.assertFalse(got["equal"])

    def test_info_reports_actions_and_bounds(self):
        got = self._tool().execute(action="info")
        self.assertEqual(got["action"], "info")
        self.assertEqual(got["algorithm"], "hmac-sha256")
        self.assertIn("sign", got["actions"])
        self.assertIn("bounds", got)

    def test_bounds_discipline(self):
        with self.assertRaises(ValueError) as caught:
            self._tool().execute(action="sign", key="a" * 4097, message="m")
        self.assertIn("4097", str(caught.exception))

    def test_unknown_action_discipline(self):
        with self.assertRaises(ValueError) as caught:
            self._tool().execute(action="nope")
        self.assertIn("nope", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
