#!/usr/bin/env python3

"""Run one interactive query through the scholarly research agent."""

from pathlib import Path

from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

APP_ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    """Initialize the app and run a user-provided research question."""
    AgentUniverse().start(config_path=str(APP_ROOT / "config" / "config.toml"), core_mode=True)
    agent = AgentManager().get_instance_obj("scholarly_research_agent")
    question = input("Research question / 研究问题: ").strip()
    if not question:
        print("A research question is required. / 请输入研究问题。")
        return
    result = agent.run(input=question)
    print(result.get("output", result))


if __name__ == "__main__":
    main()
