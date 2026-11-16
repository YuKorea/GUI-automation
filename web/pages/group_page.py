from web.pages.admin_list_page import AdminListPage


class GroupPage(AdminListPage):
    """관리자 페이지 - 그룹 관리 (/group)"""

    PATH = "/group"
    DELETE_BUTTON_INDEX = 1

    def __init__(self, page):
        super().__init__(page)
        self.popup_group_name = self.popup.locator('input[type="text"]').nth(0)
        self.popup_description = self.popup.locator('input[type="text"]').nth(1)
        self.popup_manager = self.popup.locator("input.mud-select-input").nth(0)
        self.popup_worker = self.popup.locator("input.mud-select-input").nth(1)

    def select_dropdown_item(self, input_locator, keyword):
        """드롭다운에 키워드를 입력해 일치하는 항목을 고른다.

        목록이 아이디가 아닌 표시명으로 나오는 경우 등 키워드로 찾지 못하면
        입력을 비우고 목록의 첫 항목을 고른다 (그룹 생성 자체가 목적이므로).
        """
        items = self.page.locator(".mud-list-item-clickable")
        if keyword:
            input_locator.fill(keyword)
            match = items.filter(has_text=keyword).first
            try:
                match.wait_for(state="visible", timeout=3_000)  # 기존: 고정 500ms 대기
                match.click()
                return keyword
            except Exception:
                print(f"Dropdown: '{keyword}' not found, selecting the first item")
        else:
            # 처음부터 빈칸이면 목록 창이 열리지 않는 경우가 있다.
            # 글자를 하나 입력해 목록 창을 연 뒤 아래에서 비우면 전체 목록이 나온다.
            input_locator.fill("a")
            self.page.wait_for_timeout(300)
        # 목록 창이 열려 있으면 투명 덮개(mud-overlay)가 입력칸 클릭을 막으므로
        # 클릭 대신 입력을 비우고 키보드로 목록을 연다.
        input_locator.fill("")
        first = items.first
        for open_list in (
            lambda: None,                                   # 비우기만 해도 전체 목록이 뜨는 경우
            lambda: input_locator.press("ArrowDown"),       # 키보드로 목록 열기
            lambda: input_locator.click(force=True),        # 덮개 무시하고 클릭
        ):
            open_list()
            try:
                first.wait_for(state="visible", timeout=3_000)
                break
            except Exception:
                continue
        first.wait_for(state="visible", timeout=3_000)
        chosen = first.inner_text().strip()
        first.click()
        return chosen

    def fill_add_form(self, name, description, manager, worker):
        self.popup_group_name.fill(name)
        self.popup_description.fill(description)
        self.select_dropdown_item(self.popup_manager, manager)
        self.select_dropdown_item(self.popup_worker, worker)

    def create_group(self, name, description, manager, worker):
        self.open_add_popup()
        self.fill_add_form(name, description, manager, worker)
        self.submit_add_form()
