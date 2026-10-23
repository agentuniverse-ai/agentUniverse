"""Academic fragments must own independent source metadata snapshots."""
from copy import deepcopy

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.academic_paper_fragmenter import AcademicPaperFragmenter
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('detect_sections', [False, True])
@pytest.mark.parametrize('mutation_target', ['source', 'fragment'])
def test_nested_source_metadata_is_independent(detect_sections, mutation_target):
    source = Document(
        text='Introduction\nWe propose a robust method for evidence retrieval.\n\n'
             'Our contribution improves accuracy across several datasets.',
        metadata={'provenance': {'labels': ['original'], 'details': {'version': 1}}},
        keywords={'paper'},
    )
    snapshot = deepcopy(source.metadata)
    fragments = AcademicPaperFragmenter(detect_sections=detect_sections).process_docs([source])
    assert len(fragments) == 2
    assert all(doc.metadata['original_metadata'] == snapshot for doc in fragments)
    if mutation_target == 'source':
        source.metadata['provenance']['labels'].append('changed')
        source.metadata['provenance']['details']['version'] = 2
        assert all(doc.metadata['original_metadata'] == snapshot for doc in fragments)
    else:
        fragments[0].metadata['original_metadata']['provenance']['labels'].append('changed')
        fragments[0].metadata['original_metadata']['provenance']['details']['version'] = 2
        assert source.metadata == snapshot
        assert fragments[1].metadata['original_metadata'] == snapshot
    assert all(doc.metadata['source_document_id'] == source.id for doc in fragments)
    assert source.keywords == {'paper'}


@pytest.mark.parametrize('metadata', [None, {}])
def test_empty_source_metadata_still_omitted(metadata):
    doc = Document(text='This paragraph contains enough text for argument extraction.', metadata=metadata)
    fragments = AcademicPaperFragmenter().process_docs([doc])
    assert len(fragments) == 1
    assert 'original_metadata' not in fragments[0].metadata
