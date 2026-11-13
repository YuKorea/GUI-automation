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


def _all_trees(main_win):
    try:
        return [t for t in main_win.descendants(control_type="Tree")
                if t.element_info.automation_id == TREE_AUTO_ID]
    except Exception:
        return []


def _screen_area(tree):
    try:
        if not tree.is_visible():
            return 0
        r = tree.rectangle()
        return max(r.width(), 0) * max(r.height(), 0)
    except Exception:
        return 0


def _visible_tree(main_win):
    """현재 화면에 실제로 보이는 모델 탐색기 트리를 반환한다.

    프로젝트를 탭으로 여러 개 열면 다른 탭의 트리가 UIA에 남아 있고
    is_visible도 True일 수 있다. 화면상 크기가 있는 트리 중
    가장 나중(최근 탭)의 것을 고른다.
    """
    best = None
    for t in _all_trees(main_win):
        if _screen_area(t) > 0:
            best = t
    return best


def describe_trees(main_win):
    """디버그용: 모든 탐색기 트리의 상태와 앞부분 항목을 문자열로 반환한다."""
    lines = []
    for i, t in enumerate(_all_trees(main_win)):
        try:
            visible = t.is_visible()
            rect = t.rectangle()
            names = [_item_text(it) for it in t.descendants(control_type="TreeItem")][:8]
        except Exception as e:
            lines.append(f"tree[{i}] error: {e}")
            continue
        lines.append(f"tree[{i}] visible={visible} rect={rect} items={names}")
    return "\n".join(lines) or "no explorer tree found"


def _tree_visible(main_win):
    return _visible_tree(main_win) is not None


_state = {"sidebar_opened": False}


def open_model_explorer(main_win):
    """모델 탐색 패널을 연다. 이미 보이면 아무것도 하지 않고 False를 반환한다.

    사이드바 항목과 열기 버튼은 클릭할 때마다 열림/닫힘이 토글되고, 패널이 숨겨져도
    트리 요소는 UIA에 남아 있으므로 exists가 아닌 is_visible로 판단한다.
    여기서 연 것은 close_model_explorer에서 원래대로 되돌린다.
    """
    if _tree_visible(main_win):
        return False

    _state["sidebar_opened"] = False
    menu_item = main_win.child_window(title=EXPLORER_MENU, control_type="ListItem")
    try:
        menu_visible = menu_item.exists(timeout=1) and menu_item.is_visible()
    except Exception:
        menu_visible = False
    if not menu_visible:
        print("Model explorer: opening sidebar")
        open_sidebar_panel(main_win)
        _state["sidebar_opened"] = True

    for _ in range(2):
        click_sidebar_item(main_win, EXPLORER_MENU)
        time.sleep(1)
        if _tree_visible(main_win):
            return True

    raise RuntimeError("Model explorer tree did not become visible.")


def close_model_explorer(main_win):
    """open_model_explorer가 바꾼 사이드바 상태를 원래대로 되돌린다."""
    if _tree_visible(main_win):
        click_sidebar_item(main_win, EXPLORER_MENU)
        time.sleep(0.5)
    if _state["sidebar_opened"]:
        print("Model explorer: closing sidebar")
        try:
            open_sidebar_panel(main_win)  # 열기 버튼은 토글
        except Exception as e:
            print(f"Model explorer: sidebar restore failed: {e}")
        _state["sidebar_opened"] = False


def _item_text(item):
    texts = [t.window_text() for t in item.descendants(control_type="Text")]
    return texts[0].strip() if texts else ""


def _read_items(main_win):
    tree = _visible_tree(main_win)
    if tree is None:
        raise RuntimeError("Model explorer tree is not visible.")
    items = tree.descendants(control_type="TreeItem")
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
