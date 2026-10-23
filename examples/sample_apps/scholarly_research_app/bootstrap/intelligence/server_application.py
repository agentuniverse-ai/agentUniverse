#!/usr/bin/env python3

"""Start the scholarly evidence research application server."""

from pathlib import Path

from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse

APP_ROOT = Path(__file__).resolve().parents[2]


class ServerApplication:
    """Initialize agentUniverse and expose the sample agent over HTTP."""

    @classmethod
    def start(cls) -> None:
        """Start the configured agentUniverse application."""
        AgentUniverse().start(config_path=str(APP_ROOT / "config" / "config.toml"))
        start_web_server()


if __name__ == "__main__":
    ServerApplication.start()
