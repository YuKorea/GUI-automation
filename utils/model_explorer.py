import time
from utils.utils import open_sidebar_panel, click_sidebar_item


# ===============================================================
# 모델 탐색기 (Model Explorer) — 테스트 결과 검증용
#
# 트리 항목은 UIA상 평면(flat) 목록으로 노출된다.
#   새로운 모델 / 주제영역 / 메인 / 엔터티 / <엔터티들> / 관계 / <관계들> / 기타 / ...
# 따라서 그룹 라벨 사이에 있는 항목을 해당 그룹의 하위 항목으로 본다.
# 항목 이름은 TreeItem 자체가 아니라 내부 Text 요소에 들어 있다.
# ===============================================================

EXPLORER_MENU = "모델 탐색"
TREE_AUTO_ID = "explorerTreeView"
GROUP_LABELS = ("엔터티", "관계", "기타")

EXPAND_COLLAPSED = 0


def _tree(main_win):
    return main_win.child_window(auto_id=TREE_AUTO_ID, control_type="Tree")


def _tree_visible(main_win):
    tree = _tree(main_win)
    try:
        return tree.exists(timeout=0.5) and tree.is_visible()
    except Exception:
        return False


def open_model_explorer(main_win):
    """모델 탐색 패널을 연다. 이미 보이면 아무것도 하지 않는다.

    사이드바 항목은 클릭할 때마다 열림/닫힘이 토글되고, 패널이 숨겨져도
    트리 요소는 UIA에 남아 있으므로 exists가 아닌 is_visible로 판단한다.
    """
    if _tree_visible(main_win):
        return False

    menu_item = main_win.child_window(title=EXPLORER_MENU, control_type="ListItem")
    if not menu_item.exists(timeout=1):
        open_sidebar_panel(main_win)

    for _ in range(2):
        click_sidebar_item(main_win, EXPLORER_MENU)
        time.sleep(1)
        if _tree_visible(main_win):
            return True

    raise RuntimeError("Model explorer tree did not become visible.")


def close_model_explorer(main_win):
    if _tree_visible(main_win):
        click_sidebar_item(main_win, EXPLORER_MENU)
        time.sleep(0.5)


def _item_text(item):
    texts = [t.window_text() for t in item.descendants(control_type="Text")]
    return texts[0].strip() if texts else ""


def _read_items(main_win):
    items = _tree(main_win).descendants(control_type="TreeItem")
    result = []
    for item in items:
        name = _item_text(item)
        if name in GROUP_LABELS:
            try:
                if item.get_expand_state() == EXPAND_COLLAPSED:
                    item.expand()
                    time.sleep(0.5)
                    return None  # 펼친 뒤 목록이 바뀌므로 다시 읽는다
            except Exception:
                pass
        result.append(name)
    return result


def get_group_items(main_win, group, keep_open=False):
    """모델 탐색기에서 그룹('엔터티'/'관계'/'기타')의 하위 항목 이름 목록을 반환한다.
    프로젝트 내 모든 모델의 항목이 포함된다.

    keep_open=False면 원래 패널이 닫혀 있었을 때 다시 닫아서
    캔버스 좌표 기반 테스트에 영향을 주지 않도록 한다.
    """
    if group not in GROUP_LABELS:
        raise ValueError(f"Unknown group: {group}")

    opened = open_model_explorer(main_win)
    try:
        names = None
        for _ in range(20):  # 접힌 그룹을 하나씩 펼치며 다시 읽는다
            names = _read_items(main_win)
            if names is not None:
                break
        if names is None:
            raise RuntimeError("Model explorer items could not be read.")

        # 프로젝트에 모델이 여러 개면 같은 그룹 라벨이 여러 번 나오므로 모두 합친다.
        result = []
        current = None
        for name in names:
            if name in GROUP_LABELS:
                current = name
            elif current == group:
                result.append(name)
        return result
    finally:
        if opened and not keep_open:
            close_model_explorer(main_win)


def get_entity_names(main_win, keep_open=False):
    return get_group_items(main_win, "엔터티", keep_open)


def get_relationship_names(main_win, keep_open=False):
    return get_group_items(main_win, "관계", keep_open)


def has_entity(main_win, *candidates):
    """후보 이름 중 하나라도 엔터티 목록에 있으면 True (대소문자 무시).

    논리/물리 보기 모드에 따라 트리에 표시되는 이름이 달라질 수 있어
    논리명과 물리명을 함께 넘길 수 있게 했다.
    """
    names = {n.lower() for n in get_entity_names(main_win)}
    return any(c.lower() in names for c in candidates)
