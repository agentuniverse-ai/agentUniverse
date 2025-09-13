# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/23 18:10
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: gunicorn_server.py

import tomli
from gunicorn.app.base import BaseApplication

from .flask_server import app
from .post_fork_queue import POST_FORK_QUEUE
from ...base.annotation.singleton import singleton
from ...base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.tracing.au_trace_manager import AuTraceManager

DEFAULT_GUNICORN_CONFIG = {
    'bind': '127.0.0.1:8888',
    'workers': 5,
    'backlog': 2048,
    'worker_class': 'gthread',
    'threads': 4,
    'timeout': 60,
    'keepalive': 10
}


# Execute all func in the queue after fork chile process.
def post_fork(server, worker):
    for _func, args, kwargs in POST_FORK_QUEUE:
        _func(*args, **kwargs)


class ContextVarResetMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        finally:
            FrameworkContextManager().clear_all_contexts()
            AuTraceManager().reset_trace()
@singleton
class GunicornApplication(BaseApplication):
    """Use gunicorn to wrap the flask web server."""
    def __init__(self, config_path: str = None):
        self.options = {}
        if config_path:
            self.__load_config_from_file(config_path)
        else:
            self.default_config = None
        self.application = app
        self.application.wsgi_app = ContextVarResetMiddleware(self.application.wsgi_app)

        super().__init__()

    def load_config(self):
        """Check the config file first, use default config while config file
        not exist, then overwrite parts which in options."""
        if not self.default_config:
            config = DEFAULT_GUNICORN_CONFIG
        else:
            config = self.default_config
        for key, value in config.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

        # The priority of the passed arguments supersedes that of config file.
        for key, value in self.options.items():
            if key in self.cfg.settings and value is not None:
                self.cfg.set(key.lower(), value)

        # Set post fork.
        self.cfg.set('post_fork', post_fork)

    def update_config(self, options: dict):
        self.options = options
        self.load_config()

    def load(self):
        return self.application

    def __load_config_from_file(self, config_path: str):
        """Load gunicorn config file."""
        try:
            with open(config_path, 'rb') as f:
                config = tomli.load(f)["GUNICORN_CONFIG"]
        except (FileNotFoundError, TypeError):
            print("can't find gunicorn config file, use default config")
            return
        except (tomli.TOMLDecodeError, KeyError):
            print("gunicorn config file isn't a valid toml, "
                  "use default config.")
            return

        self.default_config = {
            key: value for key, value in config.items()
        }