"""CLI for the auditable financial research sample."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from examples.sample_apps.financial_research_app.application import FinancialResearchApplication
from examples.sample_apps.financial_research_app.workspace import FinancialResearchWorkspace


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default="financial-research.db")
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--ingest", type=Path, action="append", default=[])
    parser.add_argument("--question", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--config", type=Path,
        help="Optional agentUniverse config.toml; resolves processors from the registry.",
    )
    parser.add_argument(
        "--work-pattern", help="Optional registered work-pattern name, for example peer_work_pattern.",
    )
    args = parser.parse_args(argv)

    workspace = FinancialResearchWorkspace(args.db)
    if args.config:
        from agentuniverse.base.agentuniverse import AgentUniverse

        AgentUniverse().start(config_path=str(args.config), core_mode=True)
        application = FinancialResearchApplication.from_registry(
            workspace, work_pattern_name=args.work_pattern,
        )
    else:
        application = FinancialResearchApplication.with_native_defaults(workspace)

    for path in args.ingest:
        application.ingest(
            args.tenant, path.name, path.read_text(encoding="utf-8"),
            metadata={"path": str(path)},
        )
    report = application.research(
        args.tenant, args.question, top_k=args.top_k,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
