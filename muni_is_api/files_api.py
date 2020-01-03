import requests
import logging

from muni_is_api import entities, utils

from requests.auth import HTTPBasicAuth
from typing import Dict

log = logging.getLogger(__name__)


class FilesApiClient:
    """
    Documentation: https://is.muni.cz/napoveda/technicka/spravce_souboru_api
    """
    def __init__(self, domain: str, uco: str, password: str,
                 fail: bool = False):
        self._domain = domain
        self._auth = (uco, password)
        self._session = None
        self._fail = fail

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
            self._session.auth = HTTPBasicAuth(*self._auth)
        return self._session

    @property
    def api_url(self) -> str:
        return f"https://{self.domain}/auth/dok/fmgr_api"

    @property
    def for_url(self, url: str) -> 'FilesApiWrapper':
        return FilesApiWrapper(self, url)

    def get_metadata(self, params: Dict = None, **kwargs) -> requests.Response:
        return utils.make_get_request(
            session=self.session,
            url=self.api_url,
            params=(params if params is not None else {}),
            fail=self._fail
        )


class FilesApiWrapper:
    def __init__(self, client: 'FilesApiClient', url: str):
        self._client = client
        self._url = url

    @property
    def url(self) -> str:
        return self._url

    def metadata(self, tree: bool = False) -> 'entities.NodeMetadata':
        query = {'url': self.url}
        if tree:
            query['strom'] = 1
        resp = self._client.get_metadata(query)
        return entities.NodeMetadata(content=utils.serialize(resp))
