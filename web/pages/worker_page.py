from playwright.sync_api import expect

from web.pages.admin_list_page import AdminListPage
from web import test_data


class WorkerPage(AdminListPage):
    """관리자 페이지 - 작업자 관리 (/worker)"""

    PATH = "/worker"
    DELETE_BUTTON_INDEX = 1

    def __init__(self, page):
        super().__init__(page)
        self.popup_id_input = self.popup.locator("input").nth(0)
        self.popup_password_input = self.popup.locator("input").nth(1)
        self.popup_name_input = self.popup.locator('input[type="text"]').nth(1)
        self.popup_check_button = self.popup.locator("button.mud-button-outlined-default").first

    def fill_add_form(self, worker_id, password, name=None):
        self.popup_id_input.fill(worker_id)
        self.popup_check_button.click()  # 아이디 확인 버튼
        # 확인 결과가 비동기로 반영되는 동안 짧게 대기 (기존 코드와 동일)
        self.page.wait_for_timeout(500)
        self.popup_password_input.fill(password)
        if name:
            self.popup_name_input.fill(name)

    def create_worker(self, worker_id, password=test_data.WORKER_PASSWORD, name=test_data.WORKER_NAME):
        self.open_add_popup()
        self.fill_add_form(worker_id, password, name)
        self.submit_add_form()

    def click_edit_button(self, worker_id):
        self.find(worker_id).get_by_role("button").first.click()
        self.popup.wait_for(state="visible", timeout=5_000)

    def delete_worker(self, worker_id):
        self.delete(worker_id)

    def approval_status_cell(self, worker_id):
        row = self.find(worker_id)
        expect(row).to_have_count(1)
        return row.get_by_role("cell").nth(2)
