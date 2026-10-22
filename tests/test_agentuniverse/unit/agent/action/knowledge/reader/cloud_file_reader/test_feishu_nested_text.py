"""Extract each nested Feishu text block once without launching a browser."""

from bs4 import BeautifulSoup
import pytest

from agentuniverse.agent.action.knowledge.reader.cloud_file_reader.feishu_reader import PublicFeishuReader


@pytest.mark.parametrize('container', ['<div class="doc-content">', '<div>'])
def test_nested_paragraphs_are_not_repeated(container):
    reader = object.__new__(PublicFeishuReader)
    soup = BeautifulSoup(
        f'<body>{container}<div><p>First paragraph.</p>'
        '<p>Second paragraph.</p></div></div></body>', 'html.parser')
    assert reader._parse_content(soup) == 'First paragraph.\nSecond paragraph.'


def test_inline_spans_and_direct_text_are_preserved_once():
    reader = object.__new__(PublicFeishuReader)
    soup = BeautifulSoup(
        '<body><div class="doc-content"><div>Before '
        '<span>inline <b>text</b></span><p>A paragraph.</p>'
        'After text.</div></div></body>', 'html.parser')
    assert reader._parse_content(soup) == 'Before inline text\nA paragraph.\nAfter text.'


def test_repeated_blocks_still_deduplicated_in_order():
    reader = object.__new__(PublicFeishuReader)
    soup = BeautifulSoup(
        '<body><div class="doc-content"><p>First paragraph.</p>'
        '<p>First paragraph.</p><p>Last paragraph.</p></div></body>',
        'html.parser')
    assert reader._parse_content(soup) == 'First paragraph.\nLast paragraph.'
