class LoginPage:
    def __init__(self, page):
        self.page = page
        self.id_input = page.locator('input[type="text"]').first
        self.password_input = page.locator('input[type="password"]')
        self.submit_button = page.get_by_role("button", name="로그인")

    def is_shown(self, timeout=1_000):
        try:
            self.password_input.wait_for(state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    def login(self, user_id, password):
        self.id_input.fill(user_id)
        self.password_input.fill(password)
        self.submit_button.click()
        # 로그인 폼이 사라질 때까지 대기 (기존: 고정 2초 대기)
        self.password_input.wait_for(state="hidden", timeout=10_000)

    def login_if_needed(self, user_id, password):
        if self.is_shown():
            self.login(user_id, password)
