"""공통 fixture.

- API 클라이언트: 익명 / 일반 사용자 / 관리자 세 종류. 권한 테스트에서 같은 요청을 역할별로 비교한다.
- 브라우저: pytest-playwright의 기본 fixture(page, context, browser)를 쓰고, 설정만 덮어쓴다.
  → `--browser firefox` 같은 옵션으로 크로스 브라우저를 그대로 돌릴 수 있다.
"""
import pytest
import requests

import config
from api.client import MattermostClient


def pytest_sessionstart(session):
    # 서버가 안 떠 있으면 수십 개 테스트가 각자 타임아웃으로 실패한다. 한 번에 원인을 알려 주고 멈춘다.
    try:
        requests.get(f"{config.API_URL}/system/ping", timeout=5).raise_for_status()
    except requests.RequestException as e:
        pytest.exit(f"Mattermost 서버에 연결할 수 없습니다 ({config.BASE_URL}): {e}", returncode=3)


def _logged_in(account: config.Account) -> MattermostClient:
    client = MattermostClient()
    resp = client.login(account.username, account.password)
    assert resp.status_code == 200, f"{account.username} 로그인 실패. scripts/seed.py를 먼저 실행했나요? {resp.text}"
    return client


@pytest.fixture
def anon_api() -> MattermostClient:
    return MattermostClient()


@pytest.fixture
def user_api() -> MattermostClient:
    return _logged_in(config.USER)


@pytest.fixture(scope="session")
def admin_api() -> MattermostClient:
    # 관리자는 데이터 준비·정리에만 쓰고 상태를 바꾸지 않으므로 세션 동안 하나를 공유한다.
    return _logged_in(config.ADMIN)


# ---- pytest-playwright 설정 덮어쓰기 ----
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args, browser_name):
    if browser_name == "chromium" and config.CHROMIUM_PATH:
        return {**browser_type_launch_args, "executable_path": config.CHROMIUM_PATH}
    return browser_type_launch_args


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "base_url": config.BASE_URL, "viewport": {"width": 1280, "height": 800}}
