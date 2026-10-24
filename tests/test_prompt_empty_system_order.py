"""Real model -> assembly -> ChatPrompt -> LangChain, without component mocks.

Run in Main's complete baseline/candidate AU source tree with its existing venv.
No provider/model methods, network services or token-processing functions run.
"""
import unittest

from agentuniverse.base.util.prompt_util import generate_chat_template, generate_template
from agentuniverse.prompt.chat_prompt import ChatPrompt
from agentuniverse.prompt.prompt_model import AgentPromptModel


class EmptySystemAssemblyTests(unittest.TestCase):
    def test_existing_empty_system_field_moves_before_human_and_renders(self):
        for field in ("introduction", "target"):
            with self.subTest(field=field):
                model = AgentPromptModel(**{field: "", "instruction": "Ask {query}"})
                order = ["instruction", field]
                messages = generate_chat_template(model, order)
                self.assertEqual([(m.type, m.content) for m in messages],
                                 [("system", ""), ("human", "Ask {query}")])
                chat = ChatPrompt().build_prompt(model, order)
                rendered = chat.as_langchain().format_messages(query="你好")
                self.assertEqual([(m.type, m.content) for m in rendered],
                                 [("system", ""), ("human", "Ask 你好")])
                self.assertEqual(order, ["instruction", field])
                self.assertEqual(getattr(model, field), "")

    def test_default_order_keeps_empty_system_content(self):
        model = AgentPromptModel(introduction="", instruction="Question")
        chat = ChatPrompt().build_prompt(model, ["introduction", "target", "instruction"])
        self.assertEqual([(m.type, m.content) for m in chat.as_langchain().format_messages()],
                         [("system", ""), ("human", "Question")])

    def test_nonempty_system_merge_keeps_selected_order_and_placeholders(self):
        model = AgentPromptModel(introduction="Intro {name}", target="Goal", instruction="Ask {query}")
        order = ["instruction", "target", "introduction"]
        chat = ChatPrompt().build_prompt(model, order)
        rendered = chat.as_langchain().format_messages(name="Alice", query="why")
        self.assertEqual([(m.type, m.content) for m in rendered],
                         [("system", "Goal\nIntro Alice"), ("human", "Ask why")])

    def test_none_system_fields_do_not_create_system_message(self):
        model = AgentPromptModel(instruction="Ask {query}")
        order = ["target", "instruction", "introduction"]
        messages = generate_chat_template(model, order)
        self.assertEqual([(m.type, m.content) for m in messages], [("human", "Ask {query}")])
        rendered = ChatPrompt().build_prompt(model, order).as_langchain().format_messages(query="why")
        self.assertEqual([(m.type, m.content) for m in rendered], [("human", "Ask why")])

    def test_empty_model_and_empty_order_still_produce_no_messages(self):
        self.assertEqual(generate_chat_template(AgentPromptModel(), ["introduction", "target", "instruction"]), [])
        self.assertEqual(generate_chat_template(AgentPromptModel(introduction="value"), []), [])

    def test_plain_template_keeps_order_and_empty_vs_none_behavior(self):
        model = AgentPromptModel(introduction="", instruction="Ask {query}")
        self.assertEqual(generate_template(model, ["instruction", "introduction", "target"]), "Ask {query}\n")
        self.assertEqual(generate_template(AgentPromptModel(), ["instruction", "introduction"]), "")


if __name__ == "__main__":
    unittest.main()
