"""Sentence/window offsets, source safety, merge correctness and configuration."""

import importlib
import inspect
from pathlib import Path

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.sentence_window import SentenceWindowExpander, SentenceWindowSplitter
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.config.configer import Configer


def split(text="First condition. Run alpha. It stops safely.", **options):
    return SentenceWindowSplitter(**options).process_docs([Document(text=text, metadata={"source": "manual"})])


@pytest.mark.parametrize("text,expected", [
    ("  First. Second!  Third? ", ["First.", "Second!", "Third?"]),
    ("值为3.14。请检查！可以吗？", ["值为3.14。", "请检查！", "可以吗？"]),
    ('He said "Stop." Then left.', ['He said "Stop."', 'Then left.']),
    ("Dr. Smith checks v1.2. Then proceeds.", ["Dr. Smith checks v1.2.", "Then proceeds."]),
    ("A. Smith visits the U.S. office. Next.", ["A. Smith visits the U.S. office.", "Next."]),
    ("First paragraph\r\n\r\nSecond paragraph", ["First paragraph", "Second paragraph"]),
])
def test_segmentation_preserves_exact_offsets(text, expected):
    result = split(text, window_radius=1)
    assert [doc.text for doc in result] == expected
    for doc in result:
        info = doc.metadata["sentence_window"]
        assert doc.text == text[info["sentence_start"]:info["sentence_end"]]
        assert info["window_text"] == text[info["window_start"]:info["window_end"]]


def test_source_identity_same_sentences_and_same_full_text():
    docs = [Document(text="Identical sentence. Same context.", metadata={"source": source}) for source in ("a", "b")]
    splitter = SentenceWindowSplitter()
    result = splitter.process_docs(docs)
    assert len({doc.id for doc in result}) == 4
    assert len({doc.metadata["sentence_window"]["source_id"] for doc in result}) == 2
    assert [doc.id for doc in splitter.process_docs(docs)] == [doc.id for doc in result]
    expanded = SentenceWindowExpander().process_docs(result)
    assert len(expanded) == 2


@pytest.mark.parametrize("radius,budget", [(0, 2000), (1, 2000), (99, 20), (1, 1)])
def test_window_boundaries_radius_and_oversized_sentence(radius, budget):
    text = "First condition. Run alpha. It stops safely. End."
    result = split(text, window_radius=radius, max_window_chars=budget)
    for index, doc in enumerate(result):
        info = doc.metadata["sentence_window"]
        assert info["sentence_index"] == index
        assert len(info["window_text"]) <= budget or info["window_text"] == doc.text
        assert info["over_budget"] == (len(info["window_text"]) > budget)
        if radius == 0:
            assert info["window_text"] == doc.text


def test_expansion_exact_context_preserves_inputs_and_relabels_scores():
    doc = split()[1]
    doc.embedding = [1.0]
    doc.keywords = {"alpha"}
    doc.metadata.update(relevance_score=0.8, bm25_score=1.2, custom_distance=0.1)
    before = doc.model_dump()
    result = SentenceWindowExpander(score_fields=["relevance_score", "bm25_score", "custom_distance"]).process_docs([doc])[0]
    assert result.text == "First condition. Run alpha. It stops safely."
    assert not result.embedding and not result.keywords
    assert result.id != doc.id
    assert all(key not in result.metadata for key in ["relevance_score", "bm25_score", "custom_distance"])
    match = result.metadata["sentence_window"]["matches"][0]
    assert match["text"] == "Run alpha." and match["scores"] == {"relevance_score": 0.8, "bm25_score": 1.2, "custom_distance": 0.1}
    assert doc.model_dump() == before


@pytest.mark.parametrize("indexes", [[0, 1], [1, 0], [0, 0], [0, 2, 1], [0, 4, 2]])
def test_overlap_containment_duplicate_and_bridge_merges(indexes):
    text = "First. Second. Third. Fourth. Fifth."
    sentences = split(text)
    result = SentenceWindowExpander().process_docs([sentences[i] for i in indexes])
    assert len(result) == 1
    info = result[0].metadata["sentence_window"]
    assert result[0].text == text[info["window_start"]:info["window_end"]]
    assert [match["index"] for match in info["matches"]] == indexes


def test_merge_budget_retains_separate_windows_and_original_rank():
    sentences = split("First. Second. Third. Fourth.")
    plain = Document(text="unrelated plain document")
    result = SentenceWindowExpander(max_window_chars=1).process_docs([sentences[2], plain, sentences[0]])
    assert len(result) == 3 and result[1] is plain
    assert result[0].text == sentences[2].metadata["sentence_window"]["window_text"]
    assert result[2].text == sentences[0].metadata["sentence_window"]["window_text"]
    duplicate = SentenceWindowExpander(max_window_chars=1).process_docs([sentences[0], sentences[0]])
    assert len(duplicate) == 1 and duplicate[0].metadata["sentence_window"]["over_budget"]


@pytest.mark.parametrize("field,value", [
    ("version", True), ("version", 2), ("stage", "expanded"), ("window_start", -1),
    ("window_end", 999), ("window_text", "wrong"), ("sentence_start", True),
    ("source_id", ""), ("source_length", 0),
])
def test_invalid_stored_metadata_fails_explicitly(field, value):
    doc = split()[1]
    doc.metadata["sentence_window"][field] = value
    before = doc.model_dump()
    with pytest.raises(ValueError):
        SentenceWindowExpander().process_docs([doc])
    assert doc.model_dump() == before


def test_missing_metadata_passes_through_but_present_null_and_changed_sentence_fail():
    plain = Document(text="plain")
    assert SentenceWindowExpander().process_docs([plain])[0] is plain
    plain.metadata = {"sentence_window": None}
    with pytest.raises(ValueError):
        SentenceWindowExpander().process_docs([plain])
    doc = split()[1]
    doc.text = "truncated"
    with pytest.raises(ValueError, match="offsets"):
        SentenceWindowExpander().process_docs([doc])


def test_inconsistent_overlap_fails_without_mutating_recalled_hits():
    first, second = split()[:2]
    info = second.metadata["sentence_window"]
    # Change only first-sentence context, not the second sentence's own anchor.
    info["window_text"] = "X" + info["window_text"][1:]
    before = [doc.model_dump() for doc in [first, second]]
    with pytest.raises(ValueError, match="inconsistent"):
        SentenceWindowExpander().process_docs([first, second])
    assert [doc.model_dump() for doc in [first, second]] == before


@pytest.mark.parametrize("cls,options", [
    (SentenceWindowSplitter, {"window_radius": -1}), (SentenceWindowSplitter, {"window_radius": True}),
    (SentenceWindowSplitter, {"max_window_chars": 0}), (SentenceWindowSplitter, {"max_window_chars": "20"}),
    (SentenceWindowExpander, {"max_window_chars": 0}), (SentenceWindowExpander, {"max_window_chars": True}),
    (SentenceWindowExpander, {"score_fields": [""]}), (SentenceWindowExpander, {"score_fields": ["sentence_window"]}),
    (SentenceWindowExpander, {"score_fields": ["score", "score"]}), (SentenceWindowExpander, {"score_fields": [1]}),
])
def test_bad_configuration_constructor_yaml_and_runtime(cls, options):
    with pytest.raises(ValueError):
        cls(**options)
    suffix = "splitter" if cls is SentenceWindowSplitter else "expander"
    path = Path(inspect.getfile(cls)).with_name(f"sentence_window_{suffix}.yaml")
    config = Configer(str(path)).load()
    key, value = next(iter(options.items()))
    config.set(key, value)
    processor = cls()
    with pytest.raises(ValueError):
        processor.initialize_by_component_configer(ComponentConfiger(config).load())
    assert getattr(processor, key) == getattr(cls(), key)
    setattr(processor, key, value)
    with pytest.raises(ValueError):
        processor.process_docs([])


@pytest.mark.parametrize("suffix", ["splitter", "expander"])
def test_real_yaml_resolves_component(suffix):
    path = Path(inspect.getfile(SentenceWindowSplitter)).with_name(f"sentence_window_{suffix}.yaml")
    component = ComponentConfiger(Configer(str(path)).load()).load()
    cls = getattr(importlib.import_module(component.metadata_module), component.metadata_class)
    assert cls().initialize_by_component_configer(component).name == f"sentence_window_{suffix}"


def test_empty_input_and_reserved_metadata():
    for text in (None, "", "   "):
        doc = Document(id="empty", text=text)
        assert SentenceWindowSplitter().process_docs([doc])[0] is doc
    with pytest.raises(ValueError, match="reserved"):
        SentenceWindowSplitter().process_docs([Document(text="Hello.", metadata={"sentence_window": {}})])


def test_rrf_before_expansion_and_budget_after_expansion():
    from agentuniverse.agent.action.knowledge.doc_processor.context_budget_compressor import ContextBudgetCompressor
    from agentuniverse.agent.action.knowledge.doc_processor.reciprocal_rank_fusion_processor import ReciprocalRankFusionProcessor

    sentences = split()
    sentences[1].metadata["channel"] = "A"
    duplicate = sentences[1].model_copy(deep=True)
    duplicate.metadata["channel"] = "B"
    fused = ReciprocalRankFusionProcessor(channel_key="channel").process_docs([sentences[1], duplicate])
    assert len(fused) == 1
    expanded = SentenceWindowExpander().process_docs(fused)
    assert "relevance_score" not in expanded[0].metadata
    assert expanded[0].metadata["sentence_window"]["matches"][0]["scores"]["relevance_score"] > 0
    budgeted = ContextBudgetCompressor(budget=20, counter="char").process_docs(expanded)
    assert sum(len(doc.text) for doc in budgeted) <= 20
    assert budgeted[0].metadata["truncated"] is True
