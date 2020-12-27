from collections import Callable
from urllib.parse import urljoin

import requests
from requests import Response
from requests.auth import HTTPBasicAuth


class BaseClient:
    def __init__(self, endpoint: str, user: str, password: str):
        self._password = password
        self._user = user
        self._endpoint = endpoint

    @property
    def _auth(self):
        return HTTPBasicAuth(self._user, self._password)

    def make_url(self, url):
        return urljoin(self._endpoint, url)

    def method_wrapper(self, func: Callable, url: str, *args, **kwargs):
        kwargs["auth"] = self._auth
        return func(self.make_url(url), *args, **kwargs)

    def get(self, url: str, *args, **kwargs) -> Response:
        return self.method_wrapper(requests.get, url, *args, **kwargs)

    def post(self, url: str, *args, **kwargs) -> Response:
        return self.method_wrapper(requests.post, url, *args, **kwargs)

    def put(self, url: str, *args, **kwargs) -> Response:
        return self.method_wrapper(requests.put, url, *args, **kwargs)

    def delete(self, url: str, *args, **kwargs) -> Response:
        return self.method_wrapper(requests.delete, url, *args, **kwargs)

    def patch(self, url: str, *args, **kwargs) -> Response:
        return self.method_wrapper(requests.patch, url, *args, **kwargs)
