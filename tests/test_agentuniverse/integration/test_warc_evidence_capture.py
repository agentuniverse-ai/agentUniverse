"""Capture actual loopback HTTP traffic, then read the historical archive offline."""

import http.client
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from agentuniverse.agent.action.knowledge.reader.file.warc_evidence_reader import WarcEvidenceReader

pytest.importorskip("warcio")
from warcio.capture_http import capture_http


def test_real_http_capture_remains_queryable_after_server_stops(tmp_path):
    body = "<h1>Historical experiment</h1><p>alpha 历史结论</p>".encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    path = tmp_path / "captured.warc.gz"
    try:
        with capture_http(str(path)):
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            try:
                connection.request("GET", "/experiment")
                assert connection.getresponse().read() == body
            finally:
                connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    before = path.read_bytes()
    docs, report = WarcEvidenceReader().load_archive(path)
    assert len(docs) == 1
    assert docs[0].text == "Historical experiment\nalpha 历史结论"
    assert docs[0].metadata["warc_evidence"]["target_uri"].endswith("/experiment")
    assert any(item["reason"] == "unsupported_record_type" for item in report["omitted_records"])
    assert path.read_bytes() == before
