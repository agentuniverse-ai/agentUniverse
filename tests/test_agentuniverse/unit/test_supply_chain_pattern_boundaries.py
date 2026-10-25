"""Pattern extraction must respect line and configured role boundaries."""

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.supply_chain_entity_extractor import SupplyChainEntityExtractor
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize(
    "label,role",
    [
        ("supplier", "supplier"),
        ("retailer", "retailer"),
        ("customer", "customer"),
        ("logistics provider", "logistics_provider"),
    ],
)
@pytest.mark.parametrize("separator", ["\n", "\r\n", "\n\n"])
def test_labeled_company_name_does_not_absorb_next_line(label, role, separator):
    extractor = SupplyChainEntityExtractor(use_llm=False, entity_types=[role], extract_attributes=False)
    text = f"{label}: Acme{separator}Annual Report"
    result = extractor.process_docs([Document(text=text)])[0]
    assert [(item["name"], item["type"]) for item in result.metadata["entities"]] == [("Acme", role)]


@pytest.mark.parametrize(
    "verb,role", [("supplies", "supplier"), ("manufactures", "manufacturer"), ("distributes", "distributor")]
)
def test_disabled_role_does_not_hide_allowed_role_during_deduplication(verb, role):
    extractor = SupplyChainEntityExtractor(use_llm=False, entity_types=[role], extract_attributes=False)
    result = extractor.process_docs([Document(text=f"Acme Corp {verb} components.")])[0]
    assert ("Acme Corp", role) in {(item["name"], item["type"]) for item in result.metadata["entities"]}


@pytest.mark.parametrize("threshold,expected", [(0.75, 1), (0.7501, 0)])
def test_pattern_confidence_boundary_is_inclusive(threshold, expected):
    extractor = SupplyChainEntityExtractor(use_llm=False, confidence_threshold=threshold, extract_attributes=False)
    result = extractor.process_docs([Document(text="Acme Supplier")])[0]
    assert len(result.metadata["entities"]) == expected
