import requests

from defusedxml.lxml import RestrictedElement, fromstring
from typing import Dict, Optional

import logging

log = logging.getLogger(__name__)


def serialize(response: requests.Response) -> Optional[RestrictedElement]:
    """Serialize xml response to the dict
    Args:
        response(requests.Response): XML response
    Returns(Dict): Serialized dictionary
    """
    return fromstring(response.content) if response.ok else None


def params_serialize(params: Dict) -> str:
    """Serializes params to an url
    Args:
        params(Dict): dictionary of params

    Returns(str): path url

    """

    builder = ""
    for (key, val) in params.items():
        if isinstance(val, list) or isinstance(val, tuple):
            builder += _params_iter(key, val) + ";"
        else:
            builder += f"{key}={val};"
    return builder


def _params_iter(name, col):
    return ";".join([f"{name}={value}" for value in col])


def make_get_request(session: requests.Session, url: str,
                     params: Dict, fail=False) -> Optional[requests.Response]:
    serialized = params_serialize(params)
    log.debug(f"[REQ] New: {url} : {serialized}")
    res = session.get(url, params=serialized)

    if res.ok:
        log.debug(f"[RES] Response[{res.status_code}]: {res.content}")
    else:
        content = res.content
        log.error(f"[RES] Response[{res.status_code}]: {content} - "
                  f"\"{content.decode('utf-8')}\"")
        if fail:
            from muni_is_api import errors
            raise errors.ISApiError(message=content.decode('utf-8'))
    return res
