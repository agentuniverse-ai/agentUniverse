"""Built-in YAML -> real Configer -> initialized processor -> real Documents.

No regex, configuration parser, component or Document implementation is mocked.
Run in Main's verified full baseline/candidate AU tree and existing AU venv.
"""
from pathlib import Path
import unittest

from agentuniverse.agent.action.knowledge.doc_processor import contract_clause_fragmenter as component_module
from agentuniverse.agent.action.knowledge.doc_processor.contract_clause_fragmenter import ContractClauseFragmenter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def configured_processor():
    path = Path(component_module.__file__).with_suffix(".yaml")
    configer = ComponentConfiger().load_by_configer(Configer(str(path)).load())
    return ContractClauseFragmenter().initialize_by_component_configer(configer)


class ConfiguredContractNumberingTests(unittest.TestCase):
    def assert_fragments(self, lines, identifiers, parents):
        original = Document(id="contract-source", text="\n".join(lines), keywords={"agreement"})
        direct = ContractClauseFragmenter().process_docs([original])
        configured = configured_processor().process_docs([original])
        self.assertEqual([d.metadata["clause_id"] for d in direct], identifiers)
        self.assertEqual([d.metadata["clause_id"] for d in configured], identifiers)
        self.assertEqual([d.text for d in configured], lines)
        self.assertEqual([d.metadata["parent_clause"] for d in configured], parents)
        self.assertEqual([d.metadata["parent_clause"] for d in configured],
                         [d.metadata["parent_clause"] for d in direct])
        self.assertTrue(all(d.metadata["source_document_id"] == original.id for d in configured))
        self.assertTrue(all(d.keywords == {"agreement"} for d in configured))
        self.assertEqual(original.text, "\n".join(lines))
        return configured

    def test_yaml_preserves_existing_nested_numbered_clause_boundaries(self):
        lines = [
            "1. General obligations apply.",
            "1.1 First obligation is due today.",
            "1.1.1 Detailed obligation must be met.",
            "2. Payment terms apply to both parties.",
        ]
        docs = self.assert_fragments(
            lines, ["clause_1", "clause_1.1", "clause_1.1.1", "clause_2"],
            [None, "clause_1", "clause_1.1", None],
        )
        self.assertEqual(docs[0].metadata["children_clauses"], ["clause_1.1"])
        self.assertEqual(docs[1].metadata["children_clauses"], ["clause_1.1.1"])
        self.assertEqual([d.metadata["position"] for d in docs], [0, 1, 2, 3])

    def test_yaml_preserves_existing_numbered_headers_without_final_dots(self):
        self.assert_fragments(
            ["1 General obligations apply.", "1.1 Nested obligations apply.", "2 Payment obligations apply."],
            ["clause_1", "clause_1.1", "clause_2"],
            [None, "clause_1", None],
        )

    def test_existing_dotted_numbered_headers_are_unchanged(self):
        self.assert_fragments(
            ["1. General obligations apply.", "1.1. Nested obligations apply.", "2. Payment obligations apply."],
            ["clause_1", "clause_1.1", "clause_2"],
            [None, "clause_1", None],
        )

    def test_article_section_and_chinese_article_patterns_are_unchanged(self):
        self.assert_fragments(
            ["Article I General obligations.", "Section 1.1 First obligation applies.", "第二条 双方应当遵守本合同约定的付款义务。"],
            ["article_I", "section_1.1", "article_二"],
            [None, "article_I", None],
        )

    def test_unstructured_document_still_uses_original_fallback(self):
        original = Document(id="plain", text="The parties agree to perform their obligations without numbered headings.")
        result = configured_processor().process_docs([original])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].text, original.text)
        self.assertEqual(result[0].metadata["clause_id"], "single_clause")
        self.assertEqual(result[0].metadata["source_document_id"], "plain")


if __name__ == "__main__":
    unittest.main()
