# !/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
Monitor utility for agentuniverse_product.
This module provides a context manager for handling monitor initialization and cleanup.
"""

from contextlib import contextmanager
from agentuniverse.base.util.monitor.monitor import Monitor


@contextmanager
def monitor_context():
    """
    Context manager for monitor initialization and cleanup.
    
    This context manager handles:
    1. Initializing the invocation chain and token usage
    2. Yielding control to the caller
    3. Cleaning up the invocation chain and token usage
    
    Usage:
        with monitor_context():
            # Your code here
            pass
            
        # Monitor will be automatically cleaned up
    """
    # Initialize the invocation chain and token usage of the monitor module
    Monitor.init_invocation_chain_bak()
    Monitor.init_token_usage()
    
    try:
        yield
    finally:
        # Clear invocation chain and token usage
        Monitor.clear_invocation_chain()
        Monitor.clear_token_usage()


def get_monitor_data():
    """
    Get monitor data including invocation chain and token usage.
    
    Returns:
        tuple: (invocation_chain, token_usage)
    """
    invocation_chain = Monitor.get_invocation_chain_bak()
    token_usage = Monitor.get_token_usage()
    return invocation_chain, token_usage