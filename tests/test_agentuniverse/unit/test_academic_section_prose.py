"""Ensure academic section detection does not discard body sentences."""

import pytest

from agentuniverse.agent.action.knowledge.doc_processor.academic_paper_fragmenter import AcademicPaperFragmenter
from agentuniverse.agent.action.knowledge.store.document import Document


@pytest.mark.parametrize('sentence', [
    'RESULTS SHOW A CLEAR IMPROVEMENT!',
    'Results demonstrate a significant improvement over all prior approaches.',
    'Methods used in this study include several independent validation steps.',
    'Conclusion quality depends on careful analysis of independent observations.',
    '实验结果表明该方法能够在多个独立数据集上显著提高检索质量。',
])
def test_body_sentence_is_preserved_in_its_section(sentence):
    processor = AcademicPaperFragmenter(skip_on_error=False)
    document = Document(text=(
        'Introduction\n'
        'We propose a method for robust retrieval in large collections.\n'
        f'{sentence}\n'
        'The evaluation uses a public benchmark with independent trials.'
    ))

    fragments = processor.process_docs([document])

    assert sentence in '\n'.join(fragment.text for fragment in fragments)
    assert all(fragment.metadata['section'] == 'introduction'
               for fragment in fragments)


@pytest.mark.parametrize('heading,section', [
    ('Abstract:', 'abstract'), ('Methods', 'methods'),
    ('3. Methods', 'methods'), ('摘 要：', 'abstract'),
])
def test_standalone_headings_still_detected(heading, section):
    processor = AcademicPaperFragmenter()
    sections = processor._identify_sections(
        f'{heading}\nA sufficiently long paragraph describing the research approach.')
    assert [item.name for item in sections] == [section]


def test_custom_prefix_pattern_keeps_configured_behavior():
    processor = AcademicPaperFragmenter(section_patterns={'custom': r'^Overview:'})
    sections = processor._identify_sections(
        'Overview: specialized study\nA sufficiently long paragraph about the study.')
    assert [item.name for item in sections] == ['custom']
