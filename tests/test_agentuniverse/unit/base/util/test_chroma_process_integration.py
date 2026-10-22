"""Real process and loopback HTTP coverage; no external service or model needed."""

import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import requests

from agentuniverse.base.util import chroma_util
from chromadb.config import Settings

REPOSITORY = Path(chroma_util.__file__).resolve().parents[3]
CREATION_FLAGS = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0


def child_environment():
    """Keep subprocesses on the same checkout and disable telemetry."""
    return {**os.environ, "PYTHONPATH": str(REPOSITORY), "ANONYMIZED_TELEMETRY": "False"}


def test_persistent_collection_survives_independent_process_restart(tmp_path):
    """Read IDs, vectors, documents and metadata without an in-process cache."""
    script = """
import sys
from chromadb.config import Settings
from agentuniverse.base.util.chroma_util import create_chroma_client
client = create_chroma_client(sys.argv[1], Settings(anonymized_telemetry=False))
if sys.argv[2] == 'write':
    collection = client.create_collection('restart_contract', embedding_function=None)
    collection.add(ids=['one'], embeddings=[[1.0, 0.0]], documents=['persisted text'],
                   metadatas=[{'source': 'restart-test'}])
else:
    collection = client.get_collection('restart_contract', embedding_function=None)
    result = collection.get(include=['documents', 'metadatas', 'embeddings'])
    assert result['ids'] == ['one']
    assert result['documents'] == ['persisted text']
    assert result['metadatas'] == [{'source': 'restart-test'}]
    assert result['embeddings'].tolist() == [[1.0, 0.0]]
    assert collection.query(query_embeddings=[[1.0, 0.0]], n_results=1)['ids'] == [['one']]
    collection.delete(ids=['one'])
    assert collection.count() == 0
"""
    for mode in ("write", "read"):
        completed = subprocess.run(
            [sys.executable, "-c", script, str(tmp_path / "persistent"), mode],
            cwd=REPOSITORY,
            env=child_environment(),
            capture_output=True,
            text=True,
            timeout=45,
            creationflags=CREATION_FLAGS,
        )
        assert completed.returncode == 0, completed.stdout + completed.stderr


def test_http_client_round_trip_against_real_loopback_server(tmp_path, monkeypatch):
    """Exercise the factory over HTTP, not a mocked HttpClient constructor."""
    # The test is entirely local and must not depend on a developer's proxy.
    monkeypatch.setenv("NO_PROXY", "*")
    monkeypatch.setenv("no_proxy", "*")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    command = [
        sys.executable,
        "-c",
        "from chromadb.cli.cli import app; app()",
        "run",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--path",
        str(tmp_path / "server"),
    ]
    log_path = tmp_path / "server.log"
    with log_path.open("w+b") as log:
        process = subprocess.Popen(
            command,
            cwd=REPOSITORY,
            env=child_environment(),
            stdout=log,
            stderr=log,
            creationflags=CREATION_FLAGS,
        )
        try:
            url = f"http://127.0.0.1:{port}"
            deadline = time.monotonic() + 30
            with requests.Session() as session:
                session.trust_env = False
                while time.monotonic() < deadline:
                    assert process.poll() is None, log_path.read_text(errors="replace")
                    try:
                        if session.get(url + "/api/v2/heartbeat", timeout=1).status_code == 200:
                            break
                    except requests.RequestException:
                        pass
                    time.sleep(0.1)
                else:
                    raise AssertionError("Chroma did not become ready: " + log_path.read_text(errors="replace"))
            client = chroma_util.create_chroma_client(url, Settings(anonymized_telemetry=False))
            collection = client.create_collection("http_contract", embedding_function=None)
            try:
                collection.add(ids=["one"], embeddings=[[1.0, 0.0]], documents=["HTTP text"])
                reopened = chroma_util.create_chroma_client(url, Settings(anonymized_telemetry=False))
                restored = reopened.get_collection("http_contract", embedding_function=None)
                assert restored.get()["documents"] == ["HTTP text"]
                assert restored.query(query_embeddings=[[1.0, 0.0]], n_results=1)["ids"] == [["one"]]
                restored.delete(ids=["one"])
                assert restored.count() == 0
            finally:
                client.delete_collection("http_contract")
        finally:
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
