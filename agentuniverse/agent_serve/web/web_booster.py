# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/28 10:18
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: web_booster.py

import threading

from .post_fork_queue import POST_FORK_QUEUE

ACTIVATE_OPTIONS = {
    "gunicorn": False,
    "grpc": False
}


def _parse_bind(bind):
    """Parse a host and port from a web server bind value."""
    if not isinstance(bind, str):
        raise ValueError("bind must be a string in 'host:port' format")

    host, separator, port_value = bind.rpartition(':')
    if not separator or not host or not port_value:
        raise ValueError("bind must use 'host:port' format")

    if host.startswith('[') or host.endswith(']'):
        if not (host.startswith('[') and host.endswith(']')):
            raise ValueError("bind contains an invalid bracketed IPv6 address")
        host = host[1:-1]
        if not host:
            raise ValueError("bind host must not be empty")

    try:
        port = int(port_value)
    except ValueError as exception:
        raise ValueError("bind port must be an integer") from exception

    if not 0 <= port <= 65535:
        raise ValueError("bind port must be between 0 and 65535")
    return host, port


def start_web_server(**kwargs):
    """
    Start func of web server, include http server and grpc server. Use Flask
    as default http server.
    The gRPC server is not enabled by default; it needs
    to be configured in the configuration file.
    Accept input arguments to overwrite default config.
    """
    # Start grpc server.
    if ACTIVATE_OPTIONS["grpc"]:
        from .rpc.grpc.grpc_server_booster import start_grpc_server
        grpc_thread = threading.Thread(
            target=start_grpc_server
        )
        grpc_thread.start()

    # Start http server.
    if ACTIVATE_OPTIONS["gunicorn"]:
        from .gunicorn_server import GunicornApplication
        GunicornApplication().update_config(kwargs)
        GunicornApplication().run()
    else:
        from .flask_server import app
        if 'bind' in kwargs:
            host, port = _parse_bind(kwargs['bind'])
        else:
            port = 8888
            host = '0.0.0.0'
        for _func, args, kwargs in POST_FORK_QUEUE:
            _func(*args, **kwargs)
        app.run(port=port, host=host, debug=False)
