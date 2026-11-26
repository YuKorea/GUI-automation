"""채널(메시지) 화면 Page Object. 로그인 후 처음 도착하는 화면이다."""
import re

from playwright.sync_api import Page, expect


class ChannelPage:
    def __init__(self, page: Page):
        self.page = page
        self.title = page.locator("#channelHeaderTitle")
        self.message_box = page.locator("#post_textbox")
        self.account_menu = page.locator("#userAccountMenuButton")

    def expect_loaded(self, team: str, channel: str = "town-square") -> "ChannelPage":
        expect(self.page).to_have_url(re.compile(rf"/{team}/channels/{channel}$"))
        expect(self.message_box).to_be_visible()
        return self

    def logout(self) -> None:
        self.account_menu.click()
        self.page.get_by_role("menuitem", name="Log out").click()
