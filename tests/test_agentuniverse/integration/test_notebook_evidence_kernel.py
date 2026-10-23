"""Generate one real local-kernel notebook; the reader itself never executes it."""

import json
import sys

import pytest

from agentuniverse.agent.action.knowledge.reader.file.notebook_evidence_reader import NotebookEvidenceReader

nbformat = pytest.importorskip("nbformat")


def test_locally_executed_notebook_is_still_unverified_cache_to_reader(tmp_path):
    nbclient = pytest.importorskip("nbclient")
    pytest.importorskip("ipykernel")
    from jupyter_client import AsyncKernelManager
    from jupyter_client.kernelspec import KernelSpecManager

    spec = tmp_path / "kernels" / "au-fixture"
    spec.mkdir(parents=True)
    (spec / "kernel.json").write_text(
        json.dumps(
            {
                "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
                "display_name": "agentUniverse isolated test kernel",
                "language": "python",
            }
        ),
        encoding="utf-8",
    )
    manager = AsyncKernelManager(
        kernel_name="au-fixture",
        kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(spec.parent)], ensure_native_kernel=False),
    )
    value = nbformat.v4.new_notebook(
        cells=[
            nbformat.v4.new_markdown_cell("# Controlled local fixture"),
            nbformat.v4.new_code_cell("answer = 7 * 6\nprint('实验 alpha', answer)\nanswer"),
        ]
    )
    # Only this explicit test fixture runs code, in the temporary directory.
    executed = nbclient.NotebookClient(
        value, km=manager, timeout=30, resources={"metadata": {"path": str(tmp_path)}}
    ).execute(cleanup_kc=True)
    path = tmp_path / "executed.ipynb"
    nbformat.write(executed, path)
    original = path.read_bytes()
    docs = NotebookEvidenceReader(include_text_outputs=True).load_data(path)
    outputs = [doc for doc in docs if doc.metadata["notebook_evidence"]["kind"] == "cached_output"]
    assert len(outputs) == 2
    assert outputs[0].text.endswith("实验 alpha 42\n")
    assert outputs[1].text.endswith("42")
    assert all(doc.metadata["notebook_evidence"]["execution_verified"] is False for doc in outputs)
    assert path.read_bytes() == original
