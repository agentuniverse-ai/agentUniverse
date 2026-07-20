# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/8/28 14:29
# @Author  : sunshinesmilelk
# @Email   : ximo.lk@antgroup.com
# @FileName: ssrf_proxy.py
import os
import httpx

SSRF_PROXY_ALL_URL = os.getenv('SSRF_PROXY_ALL_URL', '')
SSRF_PROXY_HTTP_URL = os.getenv('SSRF_PROXY_HTTP_URL', '')
SSRF_PROXY_HTTPS_URL = os.getenv('SSRF_PROXY_HTTPS_URL', '')

proxies = {
    'http://': SSRF_PROXY_HTTP_URL,
    'https://': SSRF_PROXY_HTTPS_URL
} if SSRF_PROXY_HTTP_URL and SSRF_PROXY_HTTPS_URL else None


def make_request(method, url, **kwargs):
    """Issue an HTTP request through the configured SSRF proxy.

    When the caller asks to follow redirects, route through a short-lived
    ``httpx.Client`` so that ``max_redirects`` can bound the chain — the
    top-level ``httpx.request`` does not accept ``max_redirects`` and would
    otherwise follow up to the default of 20, which is large enough for a
    redirect loop to consume a tool call. When redirects are not followed
    (the safe default), the request goes through the top-level helper as
    before.
    """
    kwargs.setdefault("timeout", 20)
    follow_redirects = kwargs.get("follow_redirects", False)
    max_redirects = kwargs.pop("max_redirects", None)
    proxy_kwargs = {}
    if SSRF_PROXY_ALL_URL:
        proxy_kwargs["proxy"] = SSRF_PROXY_ALL_URL
    elif proxies:
        proxy_kwargs["proxies"] = proxies
    if follow_redirects and max_redirects is not None:
        with httpx.Client(follow_redirects=True, max_redirects=max_redirects,
                          **proxy_kwargs) as client:
            return client.request(method=method, url=url, **kwargs)
    if proxy_kwargs:
        kwargs.update(proxy_kwargs)
    return httpx.request(method=method, url=url, **kwargs)


def get(url, **kwargs):
    return make_request('GET', url, **kwargs)


def post(url, **kwargs):
    return make_request('POST', url, **kwargs)


def put(url, **kwargs):
    return make_request('PUT', url, **kwargs)


def patch(url, **kwargs):
    return make_request('PATCH', url, **kwargs)


def delete(url, **kwargs):
    return make_request('DELETE', url, **kwargs)


def head(url, **kwargs):
    return make_request('HEAD', url, **kwargs)
