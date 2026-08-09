import unittest

from agentuniverse.agent.action.knowledge.store.document import Document


class TestDocument(unittest.TestCase):

    def test_as_langchain_list_handles_empty_metadata(self):
        langchain_docs = Document.as_langchain_list([
            Document(text="plain text", metadata=None)
        ])

        self.assertEqual(len(langchain_docs), 1)
        self.assertEqual(langchain_docs[0].metadata, {})
        self.assertEqual(langchain_docs[0].page_content, "plain text")


if __name__ == "__main__":
    unittest.main()
