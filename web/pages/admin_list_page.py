import re

from playwright.sync_api import expect

from web.pages.login_page import LoginPage
from web import test_data


class AdminListPage:
    """관리자 페이지 공통: 목록 표 + 검색창 + 추가 버튼 + 등록 팝업 + 확인창.

    작업자/그룹/공통코드 페이지가 같은 MudBlazor 구성을 쓰므로 공통 동작을 여기 둔다.
    하위 클래스는 PATH와 팝업 입력칸, 행 버튼 위치만 정의한다.
    """

    PATH = "/"
    DELETE_BUTTON_INDEX = 1  # 행 안 버튼 중 삭제 버튼 위치 (-1이면 마지막)

    def __init__(self, page):
        self.page = page
        self.add_button = page.locator("button.mud-icon-button.mud-button-outlined-secondary")
        self.search_input = page.get_by_role("textbox").first
        self.table = page.get_by_role("table")
        self.popup = page.get_by_role("dialog")
        self.popup_confirm_button = self.popup.locator("button.mud-button-filled-primary")
        self.popup_cancel_button = self.popup.get_by_role("button", name="취소")

    # ── 이동 ──
    def goto(self):
        self.page.goto(self.PATH)
        LoginPage(self.page).login_if_needed(test_data.ADMIN_ID, test_data.ADMIN_PW)
        self.table.wait_for(state="visible", timeout=15_000)

    # ── 팝업 ──
    def open_add_popup(self):
        self.add_button.click()
        self.popup.wait_for(state="visible", timeout=5_000)

    def submit_add_form(self):
        self.popup_confirm_button.click()
        try:
            self.popup.wait_for(state="hidden", timeout=5_000)
        except Exception:
            raise AssertionError(
                "확인 버튼을 눌렀지만 팝업이 닫히지 않았습니다.\n" + self.describe_popup()
            ) from None

    def describe_popup(self):
        """디버그용: 열려 있는 팝업의 글자, 입력칸 값, 버튼 목록."""
        lines = []
        try:
            dialog = self.page.get_by_role("dialog").last
            text = dialog.inner_text().strip()
            lines.append("[팝업 내용]\n" + text)
            inputs = dialog.locator("input")
            for i in range(inputs.count()):
                el = inputs.nth(i)
                lines.append(
                    f"input[{i}] type={el.get_attribute('type')} "
                    f"readonly={el.get_attribute('readonly') is not None} "
                    f"value={el.input_value()!r} "
                    f"aria-invalid={el.get_attribute('aria-invalid')}"
                )
            buttons = dialog.get_by_role("button")
            names = [buttons.nth(i).inner_text().strip() for i in range(buttons.count())]
            lines.append(f"buttons={names}")
        except Exception as e:
            lines.append(f"(팝업 정보를 읽지 못함: {e})")
        return "\n".join(lines)

    def cancel_add_form(self):
        self.popup_cancel_button.click()
        self.popup.wait_for(state="hidden", timeout=5_000)

    def popup_field(self, label):
        """팝업 안에서 라벨 글자로 입력칸을 찾는다 (예: '코드' → '코드*' 칸).

        몇 번째 입력칸인지 세는 방식은 칸 구성이 바뀌거나 읽기 전용 칸이 섞이면
        엉뚱한 칸을 가리키므로, MudBlazor 입력 컨테이너의 라벨로 찾는다.
        """
        label_re = re.compile(rf"^\s*{re.escape(label)}\s*\*?\s*$")
        container = self.popup.locator(".mud-input-control").filter(
            has=self.page.locator("label").filter(has_text=label_re)
        )
        return container.locator("input, textarea").first

    # ── 검색 ──
    def search(self, keyword):
        self.search_input.fill(keyword)

    def clear_search(self):
        self.search_input.clear()

    # ── 행 ──
    def row(self, text):
        return self.table.get_by_role("row").filter(has_text=text)

    def find(self, text):
        """검색으로 목록을 좁힌 뒤 해당 행을 반환한다.

        목록이 여러 페이지면 첫 페이지에 없는 항목은 행을 찾을 수 없으므로
        행을 다루기 전에는 항상 검색한다.
        """
        self.search(text)
        return self.row(text)

    def confirm_dialog(self, timeout=3_000):
        """삭제 등에서 뜨는 확인창의 확인 버튼을 누른다. 확인창이 없으면 False.

        MudDialog는 role=dialog 요소가 여러 개 잡힐 수 있어 마지막(가장 위) 것을 쓰고,
        버튼은 이름(확인/삭제/예/OK) → 강조 버튼 클래스 순으로 찾는다.
        """
        dialog = self.page.get_by_role("dialog").last
        try:
            dialog.wait_for(state="visible", timeout=timeout)
        except Exception:
            return False
        by_name = dialog.get_by_role("button", name=re.compile(r"^\s*(확인|삭제|예|OK)\s*$"))
        if by_name.count() > 0:
            by_name.last.click()
        else:
            dialog.locator("button.mud-button-filled-primary, button.mud-button-filled-error").last.click()
        return True

    def delete(self, text):
        buttons = self.find(text).locator("button")
        button = buttons.last if self.DELETE_BUTTON_INDEX == -1 else buttons.nth(self.DELETE_BUTTON_INDEX)
        button.click()
        if not self.confirm_dialog():
            print("Delete: no confirm dialog appeared")
        expect(self.row(text)).to_have_count(0)

    def delete_if_exists(self, text):
        """테스트 정리용: 남은 팝업을 닫고, 항목이 있으면 삭제한다."""
        try:
            self.page.keyboard.press("Escape")
            if self.find(text).count() > 0:
                self.delete(text)
        except Exception as e:
            print(f"Cleanup failed for {text}: {e}")
