"""Global RAR budgets using real, stored RAR4 archives (no unrar required)."""
import struct
import zlib

import pytest

from agentuniverse.agent.action.knowledge.reader.file.rar_reader import RarReader


def _header(kind, flags, payload):
    body = struct.pack('<BHH', kind, flags, 7 + len(payload)) + payload
    return struct.pack('<H', zlib.crc32(body) & 0xffff) + body


def _rar(entries):
    archive = b'Rar!\x1a\x07\x00' + _header(0x73, 0, b'\x00' * 6)
    for name, data in entries:
        encoded = name.encode('ascii')
        fields = struct.pack('<LLBLLBBHL', len(data), len(data), 3,
                             zlib.crc32(data), 0, 20, 0x30, len(encoded), 0o100644)
        archive += _header(0x74, 0x8000, fields + encoded) + data
    return archive + _header(0x7b, 0, b'')


@pytest.mark.parametrize('limit, expected', [(2, ['inside.txt']), (3, ['inside.txt', 'after.txt'])])
def test_file_limit_is_shared_with_nested_archive(tmp_path, limit, expected):
    inner = _rar([('inside.txt', b'inside')])
    path = tmp_path / 'outer.rar'
    path.write_bytes(_rar([('nested.rar', inner), ('after.txt', b'after')]))
    docs = RarReader().load_data(path, max_files=limit)
    assert [doc.metadata['file_name'] for doc in docs] == expected


@pytest.mark.parametrize('extra, expected', [(6, ['inside.txt']), (11, ['inside.txt', 'after.txt'])])
def test_byte_limit_is_shared_with_nested_archive(tmp_path, extra, expected):
    inner = _rar([('inside.txt', b'inside')])
    path = tmp_path / 'outer.rar'
    path.write_bytes(_rar([('nested.rar', inner), ('after.txt', b'after')]))
    docs = RarReader().load_data(path, max_total_size=len(inner) + extra)
    assert [doc.metadata['file_name'] for doc in docs] == expected


def test_sibling_archives_share_one_file_budget(tmp_path):
    first = _rar([('first.txt', b'first')])
    second = _rar([('second.txt', b'second')])
    path = tmp_path / 'outer.rar'
    path.write_bytes(_rar([('one.rar', first), ('two.rar', second), ('after.txt', b'after')]))
    docs = RarReader().load_data(path, max_files=3)
    assert [doc.metadata['file_name'] for doc in docs] == ['first.txt']


@pytest.mark.parametrize('limit, expected', [(3, ['deep.txt']), (4, ['deep.txt', 'after.txt'])])
def test_deep_archives_share_budget_and_repeat_loads_reset_it(tmp_path, limit, expected):
    inner = _rar([('deep.txt', b'deep')])
    middle = _rar([('inner.rar', inner)])
    path = tmp_path / 'outer.rar'
    path.write_bytes(_rar([('middle.rar', middle), ('after.txt', b'after')]))
    reader = RarReader()
    for _ in range(2):
        docs = reader.load_data(path, max_files=limit, ext_info={'source': 'test'})
        assert [doc.metadata['file_name'] for doc in docs] == expected
        assert all(doc.metadata['source'] == 'test' for doc in docs)
        assert docs[0].metadata['archive_depth'] == 2


@pytest.mark.parametrize('kwargs', [{'max_files': 0}, {'max_total_size': 0}, {'max_depth': 0}])
def test_limits_prevent_nested_documents(tmp_path, kwargs):
    path = tmp_path / 'outer.rar'
    path.write_bytes(_rar([('nested.rar', _rar([('inside.txt', b'inside')]))]))
    assert RarReader().load_data(path, **kwargs) == []
