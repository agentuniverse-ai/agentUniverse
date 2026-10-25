#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @FileName: tar_reader_demo.py
"""Demonstrate the TAR knowledge reader using only the standard library.

The demo builds a temporary ``.tar.gz`` containing regular files and a nested
``.tar.gz`` member. It then shows direct ``TarReader`` usage, discovery through
``FileReader``, metadata propagation, nested archive metadata and one security
limit. Nothing is written outside a temporary directory.
"""

import io
import tarfile
import tempfile
from pathlib import Path

from agentuniverse.agent.action.knowledge.reader.file.file_reader import FileReader
from agentuniverse.agent.action.knowledge.reader.file.tar_reader import TarReader


def _add_member(archive, name, payload):
    """Add one regular file member to an open TAR archive."""
    if isinstance(payload, str):
        payload = payload.encode("utf-8")
    info = tarfile.TarInfo(name)
    info.size = len(payload)
    archive.addfile(info, io.BytesIO(payload))


def build_sample_archive(root):
    """Create a compressed TAR with plain files and a nested compressed TAR."""
    nested_buffer = io.BytesIO()
    with tarfile.open(fileobj=nested_buffer, mode="w:gz") as nested:
        _add_member(nested, "docs/release_notes.md", "# Release\n\nNested archive member.\n")
        _add_member(nested, "data/metrics.csv", "name,value\nalpha,1\nbeta,2\n")
        _add_member(nested, "code/example.py", "def hello():\n    return 'hello'\n")

    archive_path = root / "sample_archive.tar.gz"
    with tarfile.open(archive_path, mode="w:gz") as archive:
        _add_member(archive, "README.md", "# TAR Reader Demo\n\nTop-level documentation.\n")
        _add_member(archive, "docs/guide.txt", "Use TarReader to ingest TAR archives.\n")
        _add_member(archive, "config/app.json", '{"name": "tar-demo", "enabled": true}\n')
        _add_member(archive, "logs/app.log", "[INFO] archive ready\n")
        _add_member(archive, "archives/nested.tar.gz", nested_buffer.getvalue())
    return archive_path


def print_documents(label, documents):
    """Print a compact view of the documents returned by a reader."""
    print(f"\n{label}: {len(documents)} document(s)")
    for document in documents:
        metadata = document.metadata or {}
        print(
            "  - {name} | depth={depth} | path={path} | {length} chars".format(
                name=metadata.get("file_name", "unknown"),
                depth=metadata.get("archive_depth", 0),
                path=metadata.get("archive_path", ""),
                length=len(document.text),
            )
        )


def demo_direct_reader(archive_path):
    """Read the archive directly through ``TarReader``."""
    documents = TarReader().load_data(archive_path)
    print_documents("TarReader.load_data", documents)
    return documents


def demo_file_reader(archive_path):
    """Show that ``FileReader`` resolves the compound ``.tar.gz`` suffix."""
    documents = FileReader().load_data([archive_path])
    print_documents("FileReader.load_data", documents)
    return documents


def demo_metadata(documents):
    """Show the archive metadata contract shared with the ZIP reader."""
    if not documents:
        print("\nNo documents were returned; metadata demo skipped.")
        return
    document = documents[0]
    print("\nMetadata contract:")
    for key in ("archive_root", "archive_path", "archive_depth", "file_name", "file_path"):
        print(f"  {key}: {document.metadata.get(key)}")


def demo_custom_metadata(archive_path):
    """Pass caller metadata through to every extracted document."""
    documents = TarReader().load_data(
        archive_path,
        ext_info={"tenant": "demo", "source": "tar_reader_demo"},
    )
    for document in documents:
        assert document.metadata["tenant"] == "demo"
        assert document.metadata["source"] == "tar_reader_demo"
    print(f"\nCustom metadata propagated to {len(documents)} document(s).")


def demo_security_limit(archive_path):
    """Demonstrate that an oversized member is rejected before extraction."""
    strict_reader = TarReader(max_file_size=16)
    try:
        strict_reader.load_data(archive_path)
    except ValueError as error:
        print(f"\nSecurity limit enforced: {error}")
    else:
        print("\nSecurity limit was not triggered; check the archive contents.")


def main():
    print("TAR Reader Demo - agentUniverse Knowledge Reader")
    with tempfile.TemporaryDirectory(prefix="tar_reader_demo_") as temp_dir:
        archive_path = build_sample_archive(Path(temp_dir))
        print(f"Created sample archive: {archive_path.name}")

        documents = demo_direct_reader(archive_path)
        demo_file_reader(archive_path)
        demo_metadata(documents)
        demo_custom_metadata(archive_path)
        demo_security_limit(archive_path)

        nested = [doc for doc in documents if doc.metadata.get("archive_depth") == 1]
        print(f"\nNested archive members expanded: {len(nested)}")


if __name__ == "__main__":
    main()
