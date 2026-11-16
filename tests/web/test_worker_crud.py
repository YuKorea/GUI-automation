import pytest
from playwright.sync_api import expect

from web import test_data
from web.pages.worker_page import WorkerPage

pytestmark = pytest.mark.web


@pytest.fixture
def worker_page(page):
    wp = WorkerPage(page)
    wp.goto()
    return wp


@pytest.fixture
def created_worker(worker_page):
    """테스트용 작업자를 만들고, 테스트 후 남아 있으면 삭제한다."""
    worker_id = test_data.unique_worker_id()
    worker_page.create_worker(worker_id)
    yield worker_id
    worker_page.delete_if_exists(worker_id)


# ── 생성 ──

def test_create_popup_opens(worker_page):
    worker_page.open_add_popup()
    expect(worker_page.popup).to_be_visible()
    expect(worker_page.popup_confirm_button).to_be_visible()
    expect(worker_page.popup_cancel_button).to_be_visible()


def test_create_cancel(worker_page):
    worker_page.open_add_popup()
    worker_page.cancel_add_form()
    expect(worker_page.popup).not_to_be_visible()


def test_create_success(worker_page, created_worker):
    expect(worker_page.find(created_worker)).to_have_count(1)


def test_create_requires_id(worker_page):
    worker_page.open_add_popup()
    worker_page.popup_confirm_button.click()
    # 필수값 누락이면 팝업이 닫히지 않아야 한다
    worker_page.page.wait_for_timeout(500)
    expect(worker_page.popup).to_be_visible()


# ── 검색 ──
# 특정 기존 계정에 의존하지 않도록, 테스트가 만든 작업자로 검색한다.

def test_search_existing_keyword(worker_page, created_worker):
    worker_page.search(created_worker)
    expect(worker_page.row(created_worker)).to_have_count(1)


def test_search_not_exist_keyword(worker_page, created_worker):
    # 대상 행이 보이는 상태에서 시작해야 필터링 여부를 확인할 수 있다
    expect(worker_page.find(created_worker)).to_have_count(1)
    worker_page.search(test_data.NOT_EXIST_KEYWORD)
    expect(worker_page.row(created_worker)).to_have_count(0)


def test_search_reset(worker_page, created_worker):
    expect(worker_page.find(created_worker)).to_have_count(1)
    worker_page.search(test_data.NOT_EXIST_KEYWORD)
    expect(worker_page.row(created_worker)).to_have_count(0)
    worker_page.clear_search()
    worker_page.search(created_worker)
    expect(worker_page.row(created_worker)).to_have_count(1)


# ── 수정 ──

def test_edit_popup_opens(worker_page, created_worker):
    worker_page.click_edit_button(created_worker)
    expect(worker_page.popup).to_be_visible()
    expect(worker_page.popup.locator("input").first).to_be_visible()


# ── 삭제 ──

def test_delete_worker(worker_page, created_worker):
    worker_page.delete_worker(created_worker)
    expect(worker_page.row(created_worker)).to_have_count(0)


# ── 승인상태 ──

def test_approval_status(worker_page, created_worker):
    # 관리자 페이지에서 만든 작업자는 바로 승인완료 상태가 된다.
    # 특정 기존 계정에 의존하지 않도록 테스트가 만든 작업자로 확인한다.
    expect(worker_page.approval_status_cell(created_worker)).to_have_text("승인완료")
