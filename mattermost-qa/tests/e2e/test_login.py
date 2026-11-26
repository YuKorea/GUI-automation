"""로그인 E2E (AUTH-E2E-*). API 테스트가 서버 규칙을, E2E는 사용자가 실제로 보는 화면을 검증한다."""
import re

import pytest
from playwright.sync_api import expect

import config
from pages.channel_page import ChannelPage
from pages.login_page import LoginPage

pytestmark = pytest.mark.e2e


@pytest.mark.smoke
def test_auth_e2e_01_user_logs_in_and_lands_on_default_channel(page):
    LoginPage(page).open().login(config.USER.username, config.USER.password)

    ChannelPage(page).expect_loaded(team=config.TEAM_NAME)


def test_auth_e2e_02_wrong_password_shows_error_and_stays_on_login(page):
    login = LoginPage(page).open()
    login.login(config.USER.username, "wrong-password")

    expect(login.error_banner).to_have_text("The email/username or password is invalid.")
    expect(page).to_have_url(re.compile(r"/login"))
    # 실패 후에도 입력한 아이디는 남아 있어야 재시도가 편하다 (사용성 확인).
    expect(login.login_id).to_have_value(config.USER.username)


def test_auth_e2e_03_logout_then_protected_page_redirects_to_login(page):
    LoginPage(page).open().login(config.USER.username, config.USER.password)
    channel = ChannelPage(page).expect_loaded(team=config.TEAM_NAME)

    channel.logout()
    expect(page).to_have_url(re.compile(r"/login"))

    # 로그아웃 후 채널 주소로 직접 들어가도 로그인 화면으로 돌아가야 한다.
    page.goto(f"/{config.TEAM_NAME}/channels/town-square")
    expect(page).to_have_url(re.compile(r"/login"))
