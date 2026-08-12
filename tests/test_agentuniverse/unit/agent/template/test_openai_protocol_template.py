import unittest

from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate


class ConcreteOpenAIProtocolTemplate(OpenAIProtocolTemplate):
    def input_keys(self):
        return []

    def output_keys(self):
        return []

    def parse_input(self, input_object, agent_input):
        return agent_input

    def parse_result(self, agent_result):
        return agent_result


class OpenAIProtocolTemplateTest(unittest.TestCase):
    def setUp(self):
        self.template = ConcreteOpenAIProtocolTemplate()

    def test_parse_input_concatenates_all_text_blocks(self):
        request = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "hello"},
                        {"type": "text", "text": " world"},
                    ],
                }
            ],
            "stream": False,
        }

        result = self.template.parse_openai_agent_input(request)

        self.assertEqual(result["input"], "hello world")

    def test_convert_history_concatenates_text_without_mutating_messages(self):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "first"},
                    {"type": "text", "text": " message"},
                ],
            },
            {"role": "assistant", "content": "reply"},
        ]

        converted, _ = self.template.convert_message(messages)

        self.assertEqual(converted[0].content, "first message")
        self.assertIsInstance(messages[0]["content"], list)
        self.assertNotIn("type", messages[0])


if __name__ == "__main__":
    unittest.main()
