"""로그인 화면 Page Object.

선택자는 Mattermost가 테스트용으로 넣어 둔 id / data-testid를 우선 쓴다.
CSS 클래스나 문구는 디자인·번역이 바뀌면 깨지기 쉽기 때문이다.
"""
from playwright.sync_api import Page, expect


class LoginPage:
    PATH = "/login"

    def __init__(self, page: Page):
        self.page = page
        self.login_id = page.locator("#input_loginId")
        self.password = page.locator("#input_password-input")
        self.submit = page.locator("#saveSetting")
        # 로그인 실패 메시지는 폼 위의 알림 배너에 뜬다.
        self.error_banner = page.locator(".AlertBanner__title")

    def open(self) -> "LoginPage":
        self.page.goto(self.PATH)
        expect(self.login_id).to_be_visible()
        return self

    def login(self, username: str, password: str) -> None:
        self.login_id.fill(username)
        self.password.fill(password)
        self.submit.click()
