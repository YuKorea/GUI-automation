import time
from utils import entity_actions
from utils.model_explorer import get_entity_names, get_relationship_names, has_entity
from utils.utils import (
    click_menu_item,
    open_project_file,
    open_sidebar_panel,
    click_sidebar_item,
    click_help_submenu,
    close_window_by_title_re,
    close_sidebar_panel,
    click_new_project,
    save_as_file,
    open_print_dialog_and_close,
    click_open_project,
    navigate_setting_sidebar,
    add_new_tab_and_confirm
)
from conftest import TARGET_FILE


# ===============================================================
# 테스트 케이스 (Test Cases)
# ===============================================================

def test_open_project(app_main_window):
    click_menu_item(app_main_window, "파일")
    click_menu_item(app_main_window, "최근에 사용한 프로젝트")
    open_project_file(app_main_window, TARGET_FILE)


def test_view_menu(app_main_window):
    click_menu_item(app_main_window, "보기")
    click_menu_item(app_main_window, "물리 모델")
    click_menu_item(app_main_window, "보기")
    click_menu_item(app_main_window, "확대", invoke=True)
    click_menu_item(app_main_window, "보기")
    click_menu_item(app_main_window, "축소", invoke=True)


def test_sidebar_navigation(app_main_window):
    open_sidebar_panel(app_main_window)
    click_sidebar_item(app_main_window, "모델 탐색")
    for item in ["도메인 관리", "용어 관리", "ERD 창고"]:
        click_sidebar_item(app_main_window, item)
    close_sidebar_panel(app_main_window)


def test_help_menu(app_main_window):
    click_help_submenu(app_main_window, "사용자 매뉴얼")
    close_window_by_title_re([r".*매뉴얼.*", r".*UserManual.*", r".*PDF.*"])
    click_help_submenu(app_main_window, "정보")
    close_window_by_title_re([r".*정보.*"])
    click_help_submenu(app_main_window, "업데이트 확인")
    close_window_by_title_re([r".*업데이트.*"])
    click_help_submenu(app_main_window, "라이선스 정보")
    time.sleep(0.5)
    app_main_window.type_keys("{ESC}")


def test_new_project(app_main_window):
    click_new_project(app_main_window)
    time.sleep(2)
    entities = get_entity_names(app_main_window)
    assert entities == [], f"New project should have no entities: {entities}"


def test_open_file(app_main_window):
    click_open_project(app_main_window, filename="sample.project")
    time.sleep(2)


def test_save_as_duplicate(app_main_window):
    saved_filename = save_as_file(app_main_window, filename="sample.project")
    print(f"Save as test completed: {saved_filename}")


def test_print_dialog(app_main_window):
    open_print_dialog_and_close(app_main_window)


# ===============================================================
# 엔터티 액션 테스트 (Entity Action Tests)
# ===============================================================

def test_entity_creation_flow(app_main_window, logical_image_path, physical_image_path, description_image_path):
    entity_actions.entity_creation_flow(
        app_main_window, logical_image_path, physical_image_path, description_image_path
    )
    assert has_entity(app_main_window, "SAMPLE_ENTITY", "TB_SAMPLE"), \
        f"Entity not found in model explorer: {get_entity_names(app_main_window)}"


def test_add_entity_and_create_relationship(app_main_window):
    entity_actions.create_relationship_between_entities(app_main_window)
    entities = get_entity_names(app_main_window)
    assert len(entities) >= 2, f"Expected at least 2 entities: {entities}"
    relationships = get_relationship_names(app_main_window)
    assert len(relationships) >= 1, "Relationship not found in model explorer."


# ===============================================================
# 설정 사이드바 테스트 (Settings Sidebar Tests)
# ===============================================================

def test_setting_sidebar_navigation(app_main_window):
    navigate_setting_sidebar(app_main_window)


def test_add_new_tab(app_main_window):
    tab_name = add_new_tab_and_confirm(app_main_window)
    print(f"Tab created: {tab_name}")


def test_edit_undo(app_main_window):
    click_menu_item(app_main_window, "편집")
    click_menu_item(app_main_window, "실행 취소")