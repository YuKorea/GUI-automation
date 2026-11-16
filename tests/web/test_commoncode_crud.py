import pytest
from playwright.sync_api import expect

from web import test_data
from web.pages.commoncode_page import CommonCodePage

pytestmark = pytest.mark.web


@pytest.fixture
def code_page(page):
    cp = CommonCodePage(page)
    cp.goto()
    return cp


@pytest.fixture
def created_code(code_page):
    """테스트용 공통코드를 만들고, 테스트 후 남아 있으면 삭제한다."""
    code = "qa" + test_data.unique_suffix(4)  # 기존 TS와 같은 짧은 형식
    code_page.create_code(code=code, name="qa_test_code")
    yield code
    code_page.delete_if_exists(code)


# ── 생성 ──

def test_create_popup_opens(code_page):
    code_page.open_add_popup()
    expect(code_page.popup).to_be_visible()
    expect(code_page.popup_code).to_be_visible()
    expect(code_page.popup_name).to_be_visible()
    expect(code_page.popup_confirm_button).to_be_visible()
    expect(code_page.popup_cancel_button).to_be_visible()


def test_create_cancel(code_page):
    code_page.open_add_popup()
    code_page.cancel_add_form()
    expect(code_page.popup).not_to_be_visible()


def test_create_success(code_page, created_code):
    expect(code_page.find(created_code)).to_have_count(1)


def test_create_requires_code(code_page):
    code_page.open_add_popup()
    code_page.popup_confirm_button.click()
    # 필수값 누락이면 팝업이 닫히지 않아야 한다
    code_page.page.wait_for_timeout(500)
    expect(code_page.popup).to_be_visible()


# ── 검색 ──

def test_search_existing_keyword(code_page):
    code_page.search(test_data.EXISTING_CODE_KEYWORD)
    expect(code_page.row(test_data.EXISTING_CODE_KEYWORD).first).to_be_visible()


def test_search_not_exist_keyword(code_page):
    # 기존 코드가 보이는 상태에서 시작해야 필터링 여부를 확인할 수 있다
    keyword = test_data.EXISTING_CODE_KEYWORD
    code_page.search(keyword)
    expect(code_page.row(keyword).first).to_be_visible()
    code_page.search(test_data.NOT_EXIST_KEYWORD)
    expect(code_page.row(keyword)).to_have_count(0)


# ── 삭제 ──

def test_delete_code(code_page, created_code):
    code_page.delete(created_code)
    expect(code_page.row(created_code)).to_have_count(0)
