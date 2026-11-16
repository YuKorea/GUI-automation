from web.pages.admin_list_page import AdminListPage


class CommonCodePage(AdminListPage):
    """관리자 페이지 - 공통코드 관리 (/commoncode)"""

    PATH = "/commoncode"
    DELETE_BUTTON_INDEX = -1  # 삭제 버튼이 행의 마지막 버튼

    def __init__(self, page):
        super().__init__(page)
        # 기존 TS는 '읽기 전용이 아닌 입력칸' 중 0번째/2번째를 썼는데,
        # 상위코드 칸이 읽기 전용(선택형)이면 2번째가 '설명' 칸이 되어 이름이 비게 된다.
        # 라벨(코드*, 이름*)로 찾는다.
        self.popup_code = self.popup_field("코드")
        self.popup_name = self.popup_field("이름")
        # 공통코드 팝업의 확인 버튼은 이름으로 찾는다 (기존 코드와 동일)
        self.popup_confirm_button = self.popup.get_by_role("button", name="확인")

    def fill_add_form(self, code, name):
        self.popup_code.fill(code)
        self.popup_name.fill(name)

    def create_code(self, code, name):
        self.open_add_popup()
        self.fill_add_form(code, name)
        self.submit_add_form()
