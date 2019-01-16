import logging

log = logging.getLogger(__name__)


def url_base(stub_params):
    url = f"https://{stub_params['domain']}/export/pb_blok_api?"
    url += f"klic={stub_params['token']};" \
        f"fakulta={stub_params['faculty_id']};" \
        f"kod={stub_params['course_code']}"
    return url


def gen_url(stub_params: dict, other: str = ""):
    url = url_base(stub_params) + other
    log.debug(f"[GEN] URL: {url}")
    return url
