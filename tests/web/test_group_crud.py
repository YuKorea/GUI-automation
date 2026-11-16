import pytest
from playwright.sync_api import expect

from web import test_data
from web.pages.group_page import GroupPage

pytestmark = pytest.mark.web


@pytest.fixture
def group_page(page):
    gp = GroupPage(page)
    gp.goto()
    return gp


@pytest.fixture
def created_group(group_page):
    """테스트용 그룹을 만들고, 테스트 후 남아 있으면 삭제한다."""
    suffix = test_data.unique_suffix()
    name = f"qa_group_{suffix}"
    group_page.create_group(
        name=name,
        description=f"qa_desc_{suffix}",
        manager=test_data.GROUP_MEMBER_ID,
        worker=test_data.GROUP_MEMBER_ID,
    )
    yield name
    group_page.delete_if_exists(name)


# ── 생성 ──

def test_create_popup_opens(group_page):
    group_page.open_add_popup()
    expect(group_page.popup).to_be_visible()
    expect(group_page.popup_group_name).to_be_visible()
    expect(group_page.popup_confirm_button).to_be_visible()
    expect(group_page.popup_cancel_button).to_be_visible()


def test_create_cancel(group_page):
    group_page.open_add_popup()
    group_page.cancel_add_form()
    expect(group_page.popup).not_to_be_visible()


def test_create_success(group_page, created_group):
    expect(group_page.find(created_group)).to_have_count(1)


def test_create_requires_name(group_page):
    group_page.open_add_popup()
    group_page.popup_confirm_button.click()
    # 필수값 누락이면 팝업이 닫히지 않아야 한다
    group_page.page.wait_for_timeout(500)
    expect(group_page.popup).to_be_visible()


# ── 검색 ──
# 기존 TS 테스트는 특정 계정 이름으로 검색했는데, 그 계정이 사라지면 깨진다.
# 테스트가 직접 만든 그룹으로 검색해 데이터 의존을 없앤다.

def test_search_existing_keyword(group_page, created_group):
    group_page.search(created_group)
    expect(group_page.row(created_group)).to_have_count(1)


def test_search_not_exist_keyword(group_page, created_group):
    expect(group_page.find(created_group)).to_have_count(1)
    group_page.search(test_data.NOT_EXIST_KEYWORD)
    expect(group_page.row(created_group)).to_have_count(0)


# ── 삭제 ──

def test_delete_group(group_page, created_group):
    group_page.delete(created_group)
    expect(group_page.row(created_group)).to_have_count(0)
