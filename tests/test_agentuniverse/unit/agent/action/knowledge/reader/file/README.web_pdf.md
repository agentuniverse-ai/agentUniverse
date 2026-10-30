# Web PDF reader regression tests

Use Python 3.10 or newer. From the repository root, install the package with
its PDF extra and the test runner in a virtual environment:

```sh
python -m venv .venv
# Activate .venv using the command appropriate for your shell.
python -m pip install -e ".[pdf_ext]" pytest==7.4.4
python -m pytest tests/test_agentuniverse/unit/agent/action/knowledge/reader/file/test_web_pdf_reader.py -q
```

The `pdf_ext` extra includes `pdfminer.six`, the parser imported by
`WebPdfReader`. The test module intentionally requires the real dependency;
it does not skip assertions or replace missing dependencies with fake modules.

Verified with Python 3.11, pytest 7.4.4 and pdfminer.six 20260107: 7 passed.
Coverage includes HTTP failure, declared and streamed size limits, an exact
limit response, invalid configuration, and buffer cleanup on parser success
and failure. Responses and parsing calls are mocked, so tests require no
network access and no external PDF files.
