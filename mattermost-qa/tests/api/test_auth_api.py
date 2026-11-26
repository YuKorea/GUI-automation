"""인증·권한 API 테스트 (테스트 계획서의 AUTH-*, PERM-* 항목).

각 테스트 이름 앞의 ID는 docs/test-plan.md의 TC ID와 같다. 리포트에서 계획서로 바로 추적할 수 있다.
"""
import pytest
from jsonschema import Draft202012Validator, FormatChecker

import config
from schemas.user import ERROR, USER

pytestmark = pytest.mark.api


def assert_schema(body: dict, schema: dict) -> None:
    # FormatChecker를 넣어야 "format": "email" 같은 형식 검사가 실제로 동작한다.
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(body), key=str)
    assert not errors, "스키마 불일치:\n" + "\n".join(f"- {list(e.path)}: {e.message}" for e in errors)


@pytest.mark.smoke
def test_auth_01_login_success_returns_token_and_user(anon_api):
    resp = anon_api.login(config.USER.username, config.USER.password)

    assert resp.status_code == 200
    assert resp.headers.get("Token"), "세션 토큰이 Token 헤더로 와야 한다"
    body = resp.json()
    assert_schema(body, USER)
    assert body["username"] == config.USER.username
    assert "system_admin" not in body["roles"]


@pytest.mark.parametrize(
    "login_id, password",
    [
        pytest.param(config.USER.username, "wrong-password", id="wrong-password"),
        pytest.param("no-such-user-xyz", "whatever-1A!", id="unknown-user"),
        pytest.param(config.USER.username, "", id="empty-password"),
    ],
)
def test_auth_02_login_failure_returns_401_without_token(anon_api, login_id, password):
    resp = anon_api.login(login_id, password)

    assert resp.status_code in (400, 401)
    assert "Token" not in resp.headers
    assert_schema(resp.json(), ERROR)


def test_auth_03_login_error_does_not_reveal_which_field_was_wrong(anon_api):
    """계정 열거(user enumeration) 방지: '없는 사용자'와 '틀린 비밀번호'의 응답이 같아야 한다."""
    wrong_pw = anon_api.login(config.USER.username, "wrong-password")
    no_user = anon_api.login("no-such-user-xyz", "wrong-password")

    assert wrong_pw.status_code == no_user.status_code
    assert wrong_pw.json()["message"] == no_user.json()["message"]


def test_auth_04_protected_api_requires_token(anon_api):
    resp = anon_api.me()

    assert resp.status_code == 401
    assert_schema(resp.json(), ERROR)


def test_auth_05_token_is_invalid_after_logout(user_api):
    token = user_api.token
    assert user_api.logout().status_code == 200

    # 로그아웃 후 옛 토큰을 다시 넣어 본다. 서버에서 세션이 폐기됐는지 확인하는 것이 핵심이다.
    resp = user_api.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_perm_01_regular_user_cannot_call_admin_api(user_api):
    """일반 사용자가 시스템 설정(관리자 전용)을 읽으려 하면 403이어야 한다."""
    resp = user_api.get("/config")

    assert resp.status_code == 403
    assert_schema(resp.json(), ERROR)


def test_perm_02_admin_can_call_admin_api(admin_api):
    # PERM-01과 같은 요청을 관리자로 보내 비교한다. 이게 없으면 403이 '권한' 때문인지 'API 고장' 때문인지 구분할 수 없다.
    assert admin_api.get("/config").status_code == 200


def test_perm_03_anonymous_signup_is_blocked_after_first_user(anon_api):
    """초대 없는 공개 가입이 막혀 있어야 한다 (시드 작성 중 확인한 서버 동작을 회귀 테스트로 고정)."""
    resp = anon_api.post(
        "/users", json={"username": "drive-by-user", "password": "Passw0rd-123!", "email": "drive-by@example.com"}
    )

    assert resp.status_code == 403
    assert resp.json()["id"] == "api.user.create_user.no_open_server"
