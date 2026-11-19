import unittest

from agentuniverse.agent.action.knowledge.store.document import Document


class TestDocumentLangchainMetadataCopy(unittest.TestCase):
    """Test LangChain document metadata conversion behavior."""

    def test_as_langchain_copies_metadata(self):
        metadata = {"source": "origin"}
        document = Document(text="plain text", metadata=metadata)

        langchain_document = document.as_langchain()
        langchain_document.metadata["source"] = "changed"

        self.assertEqual(document.metadata["source"], "origin")
        self.assertEqual(metadata["source"], "origin")


if __name__ == "__main__":
    unittest.main()
