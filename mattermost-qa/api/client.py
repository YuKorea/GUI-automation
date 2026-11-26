"""Mattermost REST API v4 클라이언트.

테스트 코드가 URL·헤더를 직접 다루지 않도록 감싼다(UI 쪽의 POM과 같은 역할).
- 메서드는 requests.Response를 그대로 돌려준다. 상태 코드 검증은 테스트가 한다.
  (클라이언트가 예외를 던지면 "401이 나와야 정상"인 부정 테스트를 쓰기 어렵다.)
- 로그인 토큰은 응답 헤더 'Token'으로 오고, 이후 요청은 'Authorization: Bearer <token>'으로 보낸다.
"""
from __future__ import annotations

import requests

import config


class MattermostClient:
    def __init__(self, base_url: str = config.API_URL, timeout: float = 10):
        self.base_url = base_url
        self.timeout = timeout
        self.session = requests.Session()
        self.token: str | None = None

    # ---- 저수준 ----
    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, f"{self.base_url}{path}", **kwargs)

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, **kw):
        return self.request("POST", path, **kw)

    def put(self, path, **kw):
        return self.request("PUT", path, **kw)

    def delete(self, path, **kw):
        return self.request("DELETE", path, **kw)

    # ---- 인증 ----
    def login(self, login_id: str, password: str) -> requests.Response:
        resp = self.post("/users/login", json={"login_id": login_id, "password": password})
        if resp.status_code == 200:
            self.token = resp.headers["Token"]
            self.session.headers["Authorization"] = f"Bearer {self.token}"
        return resp

    def logout(self) -> requests.Response:
        resp = self.post("/users/logout")
        self.session.headers.pop("Authorization", None)
        self.token = None
        return resp

    # ---- 자주 쓰는 호출 ----
    def me(self) -> requests.Response:
        return self.get("/users/me")

    def team_by_name(self, name: str) -> requests.Response:
        return self.get(f"/teams/name/{name}")

    def channel_by_name(self, team_id: str, channel_name: str) -> requests.Response:
        return self.get(f"/teams/{team_id}/channels/name/{channel_name}")

    def create_post(self, channel_id: str, message: str) -> requests.Response:
        return self.post("/posts", json={"channel_id": channel_id, "message": message})
