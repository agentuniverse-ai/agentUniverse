"""Notion child blocks must be exported in document order with bounded traversal."""
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from agentuniverse.agent.action.knowledge.reader.cloud.notion_reader import NotionReader


def block(identifier, text='', kind='paragraph', children=False):
    return {'id': identifier, 'type': kind, 'has_children': children,
            kind: {'rich_text': [{'plain_text': text}]}}


def client_for(pages):
    listing = Mock(side_effect=lambda **kw: pages[(kw['block_id'], kw.get('start_cursor'))])
    return SimpleNamespace(blocks=SimpleNamespace(children=SimpleNamespace(list=listing))), listing


def page(*blocks, cursor=None):
    return {'results': list(blocks), 'has_more': cursor is not None, 'next_cursor': cursor}


def test_nested_blocks_and_pagination_preserve_depth_first_order():
    client, listing = client_for({
        ('root', None): page(block('toggle', 'Overview', 'toggle', True), cursor='next'),
        ('toggle', None): page(block('first', 'Revenue rose 35%'), cursor='child-next'),
        ('toggle', 'child-next'): page(block('list', 'Details', 'bulleted_list_item', True)),
        ('list', None): page(block('deep', 'Profit doubled')),
        ('root', 'next'): page(block('last', 'Conclusion')),
    })
    assert NotionReader()._export_page(client, 'root') == [
        'Overview', 'Revenue rose 35%', 'Details', 'Profit doubled', 'Conclusion',
    ]
    assert [(c.kwargs['block_id'], c.kwargs['start_cursor']) for c in listing.call_args_list] == [
        ('root', None), ('toggle', None), ('toggle', 'child-next'), ('list', None), ('root', 'next'),
    ]


def test_containers_without_text_still_export_descendants():
    client, _ = client_for({
        ('root', None): page(block('columns', kind='column_list', children=True)),
        ('columns', None): page(block('column', kind='column', children=True)),
        ('column', None): page(block('value', 'Inside column')),
    })
    assert NotionReader()._export_page(client, 'root') == ['Inside column']


def test_depth_limit_raises_instead_of_returning_partial_document():
    client, _ = client_for({
        ('root', None): page(block('one', 'one', children=True)),
        ('one', None): page(block('two', 'two', children=True)),
    })
    with patch.object(NotionReader, 'MAX_BLOCK_DEPTH', 1):
        with pytest.raises(ValueError, match='depth'):
            NotionReader()._export_page(client, 'root')


def test_block_count_limit_applies_across_pages_and_descendants():
    client, _ = client_for({
        ('root', None): page(block('one', 'one', children=True)),
        ('one', None): page(block('two', 'two'), block('three', 'three')),
    })
    with patch.object(NotionReader, 'MAX_BLOCKS', 2):
        with pytest.raises(ValueError, match='block count'):
            NotionReader()._export_page(client, 'root')


def test_repeated_cursor_is_rejected():
    client, listing = client_for({
        ('root', None): page(block('one', 'one'), cursor='same'),
        ('root', 'same'): page(block('two', 'two'), cursor='same'),
    })
    original = listing.side_effect

    def bounded_response(**kwargs):
        if listing.call_count > 2:
            raise RuntimeError('Repeated pagination was not stopped')
        return original(**kwargs)

    listing.side_effect = bounded_response
    with pytest.raises(ValueError, match='cursor'):
        NotionReader()._export_page(client, 'root')
    assert listing.call_count == 2


def test_child_api_errors_propagate():
    client, listing = client_for({('root', None): page(block('child', 'header', children=True))})
    first = listing.side_effect

    def unavailable_child(**kwargs):
        if kwargs['block_id'] == 'root':
            return first(**kwargs)
        raise RuntimeError('unavailable')

    listing.side_effect = unavailable_child
    with pytest.raises(RuntimeError, match='unavailable'):
        NotionReader()._export_page(client, 'root')


def test_pagination_limit_bounds_empty_pages_with_unique_cursors():
    client, listing = client_for({
        ('root', None): page(cursor='one'),
        ('root', 'one'): page(cursor='two'),
    })
    with patch.object(NotionReader, 'MAX_BLOCK_PAGES', 2):
        with pytest.raises(ValueError, match='pagination limit'):
            NotionReader()._export_page(client, 'root')
    assert listing.call_count == 2


def test_leaf_page_does_not_request_children():
    client, listing = client_for({('root', None): page(block('one', 'Leaf'))})
    assert NotionReader()._export_page(client, 'root') == ['Leaf']
    assert listing.call_count == 1
