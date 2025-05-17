import unittest
from unittest.mock import Mock

from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.security.tool.tool_data_masker import FullMaskingStrategy, PartialMaskingStrategy, \
    EmailMaskingStrategy, HashMaskingStrategy, DataMasker, MaskingStrategy


class TestMaskingStrategies(unittest.TestCase):
    def setUp(self):
        self.full_strategy = FullMaskingStrategy()
        self.partial_strategy = PartialMaskingStrategy()
        self.email_strategy = EmailMaskingStrategy()
        self.hash_strategy = HashMaskingStrategy()

    def test_full_masking(self):
        """Test full masking strategy"""
        test_cases = [
            ("password123", "***********"),
            ("hello", "*****"),
            ("", ""),
            ("12345", "*****")
        ]

        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.full_strategy.mask(input_value)
                self.assertEqual(result, expected)

    def test_partial_masking(self):
        """Test partial masking strategy"""
        strategy = PartialMaskingStrategy(visible_start=2, visible_end=2)
        test_cases = [
            ("password123", "pa*******23"),
            ("abcdef", "ab**ef"),
            ("12", "12")  # Too short to mask
        ]

        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = strategy.mask(input_value)
                self.assertEqual(result, expected)

    def test_email_masking(self):
        """Test email masking strategy"""
        test_cases = [
            ("user@example.com", "u**r@example.com"),
            ("ab@example.com", "ab@example.com"),  # Username too short
            ("john.doe@company.com", "j******e@company.com"),
            ("not-an-email", "not-an-email")  # Not an email
        ]

        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.email_strategy.mask(input_value)
                self.assertEqual(result, expected)

    def test_hash_masking(self):
        """Test hash masking strategy"""
        input_value = "sensitive_data"
        result = self.hash_strategy.mask(input_value)

        # Verify it's a valid SHA-256 hash (64 characters, hexadecimal)
        self.assertEqual(len(result), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in result))

        # Verify consistency
        second_result = self.hash_strategy.mask(input_value)
        self.assertEqual(result, second_result)

class TestDataMasker(unittest.TestCase):
    def setUp(self):
        self.masker = DataMasker()

    def test_initialization(self):
        """Test DataMasker initialization"""
        self.assertEqual(self.masker.tool_type, ToolTypeEnum.FUNC)
        self.assertEqual(self.masker.name, "data_masker")
        self.assertIn("text", self.masker.input_keys)

    def test_detect_and_mask_id_card(self):
        """Test ID card detection and masking"""
        test_cases = [
            ("440101199001011234", "440101********1234"),  # Valid ID card
            ("12345678", "12345678"),  # Invalid ID card
        ]

        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.masker.detect_and_mask(input_value)
                self.assertEqual(result, expected)

    def test_detect_and_mask_phone(self):
        """Test phone number detection and masking"""
        test_cases = [
            ("13812345678", "138****5678"),  # Valid phone
            ("12345678", "12345678"),  # Invalid phone
        ]

        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.masker.detect_and_mask(input_value)
                self.assertEqual(result, expected)

    def test_detect_and_mask_bank_card(self):
        """Test bank card detection and masking"""
        test_cases = [
            ("6225887654321234", "6225********1234"),  # Valid bank card
            ("123456", "123456"),  # Invalid bank card
        ]

        for input_value, expected in test_cases:
            with self.subTest(input_value=input_value):
                result = self.masker.detect_and_mask(input_value)
                self.assertEqual(result, expected)

    def test_mask_dict(self):
        """Test dictionary masking"""
        test_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "13812345678"
        }

        fields_to_mask = {
            "name": "full",
            "email": "email",
            "phone": "phone"
        }

        masked_data = self.masker.mask_dict(test_data, fields_to_mask)

        self.assertEqual(masked_data["name"], "*********")  # Full mask
        self.assertEqual(masked_data["email"], "j*******e@example.com")  # Email mask
        self.assertEqual(masked_data["phone"], "138****5678")  # Phone mask

    def test_add_strategy(self):
        """Test adding new masking strategy"""
        class CustomStrategy(MaskingStrategy):
            def mask(self, value: str) -> str:
                return "CUSTOM" + value

        self.masker.add_strategy("custom", CustomStrategy())
        result = self.masker.mask_value("test", "custom")
        self.assertEqual(result, "CUSTOMtest")

    def test_add_pattern(self):
        """Test adding new pattern"""
        self.masker.add_pattern("test_pattern", r"^test\d+$")
        self.assertIn("test_pattern", self.masker.patterns)
        self.assertEqual(self.masker.patterns["test_pattern"], r"^test\d+$")

    def test_execute(self):
        """Test execute method with ToolInput"""
        mock_tool_input = Mock(spec=ToolInput)
        mock_tool_input.to_dict.return_value = {"text": "13812345678"}
        mock_tool_input.get_data.return_value = "13812345678"

        result = self.masker.execute(mock_tool_input)
        self.assertEqual(result, "138****5678")

    def test_invalid_strategy(self):
        """Test handling of invalid masking strategy"""
        with self.assertRaises(ValueError):
            self.masker.mask_value("test", "invalid_strategy")

if __name__ == '__main__':
    unittest.main()