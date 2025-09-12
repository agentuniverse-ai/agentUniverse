# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: server_application.py

from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse
from flask_cors import CORS
from agentuniverse.agent_serve.web.flask_server import app as flask_app

class ServerApplication:
    """
    Server application.
    """

    @classmethod
    def start(cls):
        AgentUniverse().start()


        CORS(
            flask_app,
            resources={r"/*": {"origins": ["http://localhost:5173",
        "http://127.0.0.1:5173",
        ]}},
            supports_credentials=True
        )
        start_web_server()


if __name__ == "__main__":
    ServerApplication.start()
