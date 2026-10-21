import requests
from session_manager import SessionManager
from errors import *
from jwt_utils import is_token_valid
from urllib.parse import urljoin

class ApiClient:
    def __init__(self, session_manager: SessionManager, base_url):
        self.manager = session_manager
        self.session = requests.Session()
        self.url = base_url

    def _set_auth_header(self):
        data = self.manager.read_sessions()

        if "token" in data:
            token = data["token"]
        else:
            self.session.headers.pop("Authorization", None)
            return False

        if is_token_valid(token):
            self.session.headers.update({
                "Authorization": f"Bearer {token}"
            })
            return True
        else:
            self.session.headers.pop("Authorization", None)
            return False

    def _request(self, method, endpoint, **kwargs):
        self._set_auth_header()
        url = urljoin(self.url, endpoint)

        try:
            response = self.session.request(method, url, **kwargs)
        except requests.exceptions.ConnectionError as e:
            print(e)
            raise APINotAccessible()

        if response.status_code == 401:
            self.manager.clean_sessions()
            raise UnauthorizedError()

        return response

    def get(self, endpoint, **kwargs):
        return self._request("get", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self._request("post", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._request("delete", endpoint, **kwargs)
