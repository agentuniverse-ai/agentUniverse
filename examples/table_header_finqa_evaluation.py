"""Structural comparison on separately downloaded FinQA public test tables.

python -m examples.table_header_finqa_evaluation /path/to/finqa-test.json
No answer accuracy or official FinQA benchmark score is measured.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from agentuniverse.agent.action.knowledge.doc_processor.recursive_character_text_splitter import RecursiveCharacterTextSplitter
from agentuniverse.agent.action.knowledge.doc_processor.table_header_splitter import TableHeaderSplitter
from agentuniverse.agent.action.knowledge.store.document import Document


def evaluate(path):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != "831dbfb2e785dbc227f895ce3f24046433467aec67b09db2bd6ac7692a8a30dc":
        raise ValueError("Unexpected FinQA public test file SHA256")
    records = json.loads(raw)
    skipped = Counter()
    results = []
    baseline = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=0)
    candidate = TableHeaderSplitter(max_chars=400)
    for record in records:
        table = record.get("table", [])
        if len(table) < 2 or len(table[0]) < 2 or any(len(row) != len(table[0]) for row in table):
            skipped["non_rectangular_or_empty"] += 1
            continue
        if any(not isinstance(cell, str) or any(char in cell for char in "|\n\r`\\") for row in table for cell in row):
            skipped["unsupported_cell_syntax"] += 1
            continue
        lines = ["| " + " | ".join(row) + " |" for row in table]
        header = lines[0]
        source = header + "\n| " + " | ".join(["---"] * len(table[0])) + " |\n" + "\n".join(lines[1:]) + "\n"
        doc = Document(id=record["id"], text=source, metadata={"source": record["id"]})
        variants = {"recursive": baseline.process_docs([doc]), "table_header": candidate.process_docs([doc])}
        row = {"id": record["id"], "rows": len(table)-1, "source_chars": len(source), "methods": {}}
        for name, chunks in variants.items():
            text_lines = [chunk.text.splitlines() for chunk in chunks]
            row["methods"][name] = {
                "chunks": len(chunks),
                "output_chars": sum(len(chunk.text) for chunk in chunks),
                "over_budget_chunks": sum(len(chunk.text) > 400 for chunk in chunks),
                "whole_rows_present": sum(any(line in part for part in text_lines) for line in lines[1:]),
                "rows_with_header": sum(any(line in part and header in part for part in text_lines) for line in lines[1:]),
            }
        actual = [chunk for chunk in variants["table_header"] if chunk.metadata.get("table_chunk", {}).get("kind") == "table"]
        reconstructed = []
        for chunk in actual:
            info = chunk.metadata["table_chunk"]
            reconstructed.extend(chunk.text.splitlines()[2:])
            assert chunk.text.splitlines()[2:] == lines[1:][info["row_start"]:info["row_end"]]
        assert reconstructed == lines[1:], record["id"]
        results.append(row)
    totals = {name: {key: sum(row["methods"][name][key] for row in results)
                     for key in results[0]["methods"][name]} for name in ("recursive", "table_header")}
    return {"dataset": "FinQA public test tables", "sha256": digest, "input_records": len(records),
            "eligible_records": len(results), "excluded": dict(skipped),
            "data_rows": sum(row["rows"] for row in results),
            "protocol": "400 characters; recursive overlap0 vs table soft budget400; all eligible tables; original table cells; no QA labels or tuning",
            "totals": totals, "per_record": results}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    print(json.dumps(evaluate(parser.parse_args().dataset), indent=2))
