import uuid

import requests
from loguru import logger

from app.state.tt import bb

__all__ = ["get", "post", "clear_cookies", "reset_session"]

proxies = {
  "http": None,
  "https": None,
}
session = requests.Session()
default_timeout = 60


def get(url, **kwargs):
    response = requests.Response()
    response.status_code = 499
    if "timeout" not in kwargs:
        kwargs["timeout"] = default_timeout

    trace_id = bb.trace_id #str(uuid.uuid4())
    headers = kwargs['headers'] if "headers" in kwargs else {}
    headers['traceId'] = trace_id
    kwargs['headers'] = headers

    try:
        logger.info("[{}] http:get:req [url:{}, kwargs:{}]", trace_id, url, kwargs)
        response = session.get(url, proxies=proxies, **kwargs)
        logger.info("[{}] http:get:rsp [code:{}, time:{}, content:{}]", trace_id, response.status_code,
                    response.elapsed.total_seconds(), response.text)
    except requests.RequestException as e:
        logger.error("[{}] http:get:err {}", trace_id, e)
        response.reason = str(e)
    return response


def post(url, data=None, json=None, **kwargs):
    response = requests.Response()
    response.status_code = 499
    if "timeout" not in kwargs:
        kwargs["timeout"] = default_timeout

    trace_id = bb.trace_id #str(uuid.uuid4())
    headers = kwargs['headers'] if "headers" in kwargs else {}
    headers['traceId'] = trace_id
    kwargs['headers'] = headers

    try:
        logger.info("[{}] http:post:req [url:{}, data:{}, json:{}, kwargs:{}]", trace_id, url, data, json, kwargs)
        response = session.post(url, data=data, json=json, proxies=proxies, **kwargs)
        logger.info("[{}] http:post:rsp [code:{}, time:{}, content:{}]", trace_id, response.status_code,
                    response.elapsed.total_seconds(), response.text)
    except requests.RequestException as e:
        logger.error("[{}] http:post:err {}", trace_id, e)
        response.reason = str(e)
    return response


def clear_cookies():
    session.cookies.clear()


def reset_session():
    global session
    session = requests.Session()
