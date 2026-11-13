import os
import pyautogui
import time
from utils.utils import click_menu_item, click_new_project, bring_to_front

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSET_DIR = os.path.join(BASE_DIR, "asset")
DEBUG_DIR = os.path.join(BASE_DIR, "debug_screenshots")


# ===============================================================
# 0. 공통 유틸리티 (Utilities)
# ===============================================================

def save_failure_screenshot(image_path):
    """현재 화면을 debug_screenshots/에 저장하고 경로를 반환한다.

    image_path는 파일명에 붙일 라벨로 쓰인다(이미지 경로 또는 임의 문자열).
    """
    try:
        os.makedirs(DEBUG_DIR, exist_ok=True)
        label = os.path.splitext(os.path.basename(image_path))[0]
        path = os.path.join(DEBUG_DIR, f"{time.strftime('%Y%m%d_%H%M%S')}_{label}.png")
        pyautogui.screenshot(path)
        print(f"Screenshot saved: {path}")
        return path
    except Exception as e:
        print(f"Screenshot failed: {e}")
        return None


def canvas_relative(canvas, offset_x, offset_y):
    rect = canvas.rectangle()
    x = rect.left + offset_x
    y = rect.top + offset_y
    return (x, y)


def click_and_write(image_path, text, delay=0.3, confidence=0.85):
    try:
        loc = pyautogui.locateCenterOnScreen(
            image=image_path,
            region=None,
            grayscale=False,
            confidence=confidence
        )
    except pyautogui.ImageNotFoundException:
        loc = None
    if loc is None:
        print(f"Image not found: {image_path}")
        save_failure_screenshot(image_path)
        return False
    x, y = loc
    pyautogui.click(x, y)
    time.sleep(delay)
    pyautogui.typewrite(text)
    pyautogui.press('enter')
    time.sleep(delay)
    print(f"Input completed: {text}")
    return True


# ===============================================================
# 1. 캔버스 관련 (Canvas)
# ===============================================================

def find_canvas(main_win):
    candidates = main_win.descendants(control_type="Pane")
    best = None
    max_area = 0
    for c in candidates:
        try:
            rect = c.rectangle()
            area = rect.width() * rect.height()
            if area < 50000:
                continue
            if rect.width() < 300 or rect.height() < 200:
                continue
            if area > max_area:
                max_area = area
                best = c
        except Exception:
            continue
    if best is None:
        raise RuntimeError("Canvas not found.")
    print(f"Canvas found: area={max_area}")
    return best


# ===============================================================
# 2. 엔터티 관련 (Entity)
# ===============================================================

def new_project(main_win):
    click_new_project(main_win)
    print("New project created.")


def create_entity(main_win, coords):
    click_menu_item(main_win, "다이어그램")
    click_menu_item(main_win, "엔터티", invoke=True)
    time.sleep(0.3)
    canvas = find_canvas(main_win)
    canvas.click_input(coords=coords)
    print("Entity created.")
    time.sleep(1)


# ===============================================================
# 3. 엔터티 패널 (Entity Panel)
# ===============================================================

def open_entity_panel(main_win, canvas, coords):
    bring_to_front(main_win)
    canvas.set_focus()
    canvas.double_click_input(coords=coords)
    time.sleep(0.5)
    print("Entity panel opened.")


def fill_field(panel_image_path, text):
    try:
        location = pyautogui.locateOnScreen(panel_image_path, confidence=0.9, grayscale=True)
    except pyautogui.ImageNotFoundException:
        location = None
    if location is None:
        print(f"Label image not found: {panel_image_path}")
        save_failure_screenshot(panel_image_path)
        return False

    input_x = location.left + location.width - 10
    input_y = location.top + (location.height // 2)

    pyautogui.moveTo(input_x, input_y, duration=0.2)
    time.sleep(0.1)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.typewrite(text, interval=0.1)
    print(f"Field filled: {text}")
    return True


def fill_logical_name(logical_image_path):
    return fill_field(logical_image_path, "SAMPLE_ENTITY")


def fill_physical_name(physical_image_path):
    return fill_field(physical_image_path, "TB_SAMPLE")


def fill_description(description_image_path):
    return fill_field(description_image_path, "Temporary entity for automated testing.")


# ===============================================================
# 4. 다이어그램 서브 메뉴 (Diagram Submenu)
# ===============================================================

def click_diagram_submenu(main_win, submenu_name, timeout=8):
    pyautogui.press('esc')
    time.sleep(0.2)

    diagram_menu = main_win.child_window(title="다이어그램", control_type="MenuItem")
    diagram_menu.click_input()
    time.sleep(0.25)

    target_item = None
    start = time.time()
    while time.time() - start < timeout:
        items = main_win.descendants(control_type="MenuItem")
        for item in items:
            if item.window_text().strip() == submenu_name:
                target_item = item
                break
        if target_item:
            break
        time.sleep(0.2)

    if not target_item:
        raise Exception(f"Menu item not found: {submenu_name}")

    try:
        target_item.click_input()
    except Exception:
        time.sleep(0.2)
        target_item.click_input()
    time.sleep(0.3)


# ===============================================================
# 5. 엔터티 생성 흐름
# ===============================================================

def entity_creation_flow(main_win, logical_image_path, physical_image_path, description_image_path):
    new_project(main_win)
    canvas = find_canvas(main_win)
    coords = (200, 200)

    create_entity(main_win, coords)
    open_entity_panel(main_win, canvas, coords)
    time.sleep(1)

    assert fill_logical_name(logical_image_path), "Field input failed: label image not found"
    assert fill_physical_name(physical_image_path), "Field input failed: label image not found"
    assert fill_description(description_image_path), "Field input failed: label image not found"

    attr_start_offset = (150, 120)
    attr_x, attr_y = canvas_relative(canvas, *attr_start_offset)
    time.sleep(0.3)

    pyautogui.doubleClick(attr_x, attr_y)
    time.sleep(0.2)

    attributes = ["1", "SAMPLE_ENTITY", "ID", "email"]
    for attr in attributes:
        pyautogui.hotkey("ctrl", "a")
        time.sleep(0.1)
        pyautogui.typewrite(attr, interval=0.05)
        pyautogui.press("tab")
        time.sleep(0.2)

    pyautogui.press("esc")
    time.sleep(0.5)
    print("Entity attribute input completed.")


# ===============================================================
# 6. 관계선 생성 및 속성 입력
# ===============================================================

def create_relationship_between_entities(main_win, logical_image_path=None,
                                         physical_image_path=None, description_image_path=None):
    logical_image_path = logical_image_path or os.path.join(ASSET_DIR, "logical_label.png")
    physical_image_path = physical_image_path or os.path.join(ASSET_DIR, "physical_label.png")
    description_image_path = description_image_path or os.path.join(ASSET_DIR, "description_label.png")

    canvas = find_canvas(main_win)
    existing_coords = (200, 200)
    new_coords = (450, 200)

    create_entity(main_win, new_coords)
    time.sleep(1)

    click_diagram_submenu(main_win, "식별관계 연결")
    time.sleep(0.5)

    canvas.click_input(coords=existing_coords)
    time.sleep(0.4)
    canvas.click_input(coords=new_coords)
    time.sleep(1)

    bring_to_front(main_win)
    open_relationship_panel(main_win, canvas, existing_coords, new_coords,
                            label_image_path=logical_image_path)

    assert fill_field(logical_image_path, "REL_LOGICAL"), "Field input failed: label image not found"
    assert fill_field(physical_image_path, "REL_PHYSICAL"), "Field input failed: label image not found"
    assert fill_field(description_image_path, "Temporary relationship for automated testing."), "Field input failed: label image not found"
    print("Relationship input completed.")


LEGACY_RELATIONSHIP_SCREEN_POS = (365, 270)  # 창 최대화 기준으로 쓰던 화면 절대좌표
# 엔터티 생성 좌표(박스 왼쪽 위)의 중간점에서 실제 관계선까지의 보정값.
# 최대화 상태에서 캔버스 기준 (365, 247)에 관계선이 있었다: 중간점 (325, 200) + (40, 47)
RELATIONSHIP_LINE_OFFSET = (40, 47)


def _label_on_screen(image_path, confidence=0.9):
    try:
        return pyautogui.locateOnScreen(image_path, confidence=confidence, grayscale=True) is not None
    except pyautogui.ImageNotFoundException:
        return False


def open_relationship_panel(main_win, canvas, start_coords=None, end_coords=None, label_image_path=None):
    """관계선을 더블클릭해 관계 속성 패널을 연다.

    관계선은 UIA로 잡히지 않으므로 두 엔터티의 중간점(캔버스 기준)을 더블클릭한다.
    창 크기/위치가 달라도 동작하도록 캔버스 상대좌표를 쓰고,
    label_image_path가 주어졌는데 패널 라벨이 안 보이면 기존 화면 절대좌표로 재시도한다.
    """
    targets = []
    if start_coords and end_coords:
        mid = ((start_coords[0] + end_coords[0]) // 2 + RELATIONSHIP_LINE_OFFSET[0],
               (start_coords[1] + end_coords[1]) // 2 + RELATIONSHIP_LINE_OFFSET[1])
        targets.append(("canvas relative", canvas_relative(canvas, *mid)))
    targets.append(("legacy screen position", LEGACY_RELATIONSHIP_SCREEN_POS))

    for name, (x, y) in targets:
        pyautogui.moveTo(x, y)
        time.sleep(0.2)
        pyautogui.doubleClick()
        time.sleep(0.8)
        if label_image_path is None or _label_on_screen(label_image_path):
            print(f"Relationship panel opened ({name}: {x}, {y}).")
            return True
        print(f"Relationship panel not detected after clicking {name}: {x}, {y}")
    return False


def fill_entity_properties(logical_img, physical_img, description_img,
                           logical_text, physical_text, description_text):
    click_and_write(logical_img, logical_text)
    click_and_write(physical_img, physical_text)
    click_and_write(description_img, description_text)
    print("Entity properties filled.")


def fill_relationship_properties(logical_img, physical_img, description_img,
                                 logical_text, physical_text, description_text):
    click_and_write(logical_img, logical_text)
    click_and_write(physical_img, physical_text)
    click_and_write(description_img, description_text)
    print("Relationship properties filled.")