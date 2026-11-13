import os
import re
import psutil
import random
import string
from pywinauto.keyboard import send_keys
import time
from pywinauto.application import Application
from pywinauto import Desktop


# ===============================================================
# 1. 앱 실행 / 연결 (App Launch / Connection)
# ===============================================================

def start_or_connect_app(exe_path: str):
    for proc in psutil.process_iter(['name', 'exe']):
        if proc.info['exe'] and exe_path.lower() in proc.info['exe'].lower():
            return Application(backend="uia").connect(path=proc.info['exe'])
    if not os.path.exists(exe_path):
        raise FileNotFoundError(f"EXE not found: {exe_path}")
    app = Application(backend="uia").start(exe_path)
    time.sleep(3)
    return app


def _is_foreground(main_win):
    """맨 앞 창이 메인 창이거나 같은 프로세스의 창(메뉴 팝업, 다이얼로그 등)이면 True."""
    import win32gui
    import win32process
    fg = win32gui.GetForegroundWindow()
    if fg == main_win.handle:
        return True
    _, fg_pid = win32process.GetWindowThreadProcessId(fg)
    return fg_pid == main_win.process_id()


def bring_to_front(main_win, retries=3):
    """메인 창을 화면 맨 앞으로 가져온다.

    클릭(click_input)과 이미지 인식(pyautogui)은 실제 화면 기준으로 동작하므로
    다른 창(예: IDE)이 앞에 있으면 엉뚱한 곳을 클릭하거나 라벨을 찾지 못한다.
    Windows는 백그라운드 프로세스의 포커스 요청을 막을 수 있어,
    set_focus가 통하지 않으면 최소화 후 복원으로 강제한다.
    """
    try:
        # 이미 앱 창(메뉴 팝업 포함)이 앞에 있으면 건드리지 않는다.
        # 여기서 최소화/복원하면 열려 있는 메뉴가 닫힌다.
        if _is_foreground(main_win):
            return True
    except Exception:
        pass

    for _ in range(retries):
        try:
            main_win.set_focus()
            time.sleep(0.2)
            if _is_foreground(main_win):
                return True
        except Exception:
            pass
        try:
            main_win.minimize()
            time.sleep(0.3)
            main_win.restore()
            time.sleep(0.5)
        except Exception:
            pass
    print("Warning: main window could not be brought to front.")
    return False


def get_main_window(app):
    win = app.window(title_re=".*")
    win.wait("visible enabled ready", timeout=20)
    return win


# ===============================================================
# 2. 메뉴 / 사이드바 상호작용 (Menu / Sidebar Interaction)
# ===============================================================

def click_menu_item(main_win, title, invoke=False, timeout=10):
    bring_to_front(main_win)
    try:
        menu_item = main_win.child_window(title=title, control_type="MenuItem")
        menu_item.wait("visible enabled ready", timeout=timeout)
    except Exception:
        menu_item = main_win.child_window(title_re=f".*{re.escape(title)}.*", control_type="MenuItem")
        menu_item.wait("visible enabled ready", timeout=timeout)

    if invoke:
        menu_item.invoke()
    else:
        menu_item.click_input()
    time.sleep(0.5)


def click_help_submenu(main_win, submenu_title):
    bring_to_front(main_win)
    desktop = Desktop(backend="uia")

    try:
        panel = main_win.child_window(control_type="Pane", title_re=r".*정보.*|.*매뉴얼.*|.*업데이트.*")
        if panel.exists(timeout=1):
            panel.click_input(coords=(10, 10))
            panel.wait_not("visible", timeout=5)
            time.sleep(1)
            main_win.type_keys("{ESC}")
            time.sleep(1)
    except Exception:
        pass

    click_menu_item(main_win, "도움말")
    time.sleep(1)

    try:
        click_menu_item(main_win, submenu_title, invoke=True)
    except Exception:
        click_menu_item(main_win, "도움말")
        time.sleep(1)
        click_menu_item(main_win, submenu_title, invoke=True)

    time.sleep(2)

    try:
        panel = main_win.child_window(title_re=f".*{re.escape(submenu_title)}.*", control_type="Pane")
        if panel.exists(timeout=2):
            panel.click_input(coords=(10, 10))
            panel.wait_not("visible", timeout=5)
            time.sleep(0.5)
            main_win.type_keys("{ESC}")
    except Exception:
        pass

    bring_to_front(main_win)
    time.sleep(1)


# ===============================================================
# 2.3 사이드바 (Sidebar)
# ===============================================================

def open_sidebar_panel(main_win):
    btn = main_win.child_window(title_re=".*열기.*", control_type="Button")
    btn.wait("visible enabled ready", timeout=10)
    btn.click_input()
    time.sleep(0.5)


def click_sidebar_item(main_win, title):
    for ctl_type in ["ListItem", "TreeItem", "Pane"]:
        item = main_win.child_window(title=title, control_type=ctl_type)
        if item.exists(timeout=1):
            item.wait("visible enabled ready")
            item.click_input()
            time.sleep(0.5)
            return
    raise RuntimeError(f"Sidebar item not found: {title}")


def close_sidebar_panel(main_win, last_item_title="ERD 창고"):
    try:
        click_sidebar_item(main_win, last_item_title)
        time.sleep(0.5)
    except Exception as e:
        raise RuntimeError(f"Sidebar close failed: {e}")


# ===============================================================
# 3. 프로젝트 / 파일 처리 (Project / File Handling)
# ===============================================================

def click_new_project(main_win):
    click_menu_item(main_win, "파일")
    click_menu_item(main_win, "새로 만들기", invoke=True)
    time.sleep(1)


def click_open_project_menu(main_win):
    bring_to_front(main_win)
    click_menu_item(main_win, "파일")
    click_menu_item(main_win, "열기", invoke=True)
    time.sleep(1.5)


def click_open_project(main_win, filename):
    bring_to_front(main_win)
    click_menu_item(main_win, "파일")
    click_menu_item(main_win, "열기...", invoke=True)
    time.sleep(2)

    try:
        open_win = main_win.child_window(title="열기", control_type="Window")
        open_win.wait("visible enabled ready", timeout=5)
    except Exception:
        desktop = Desktop(backend="uia")
        open_win = desktop.window(title_re=r".*열기.*")
        open_win.wait("visible enabled ready", timeout=5)

    open_win.set_focus()
    time.sleep(1)

    filename_box = None
    for title in ["파일 이름(N):", "파일 이름:", "File name:", "File name"]:
        try:
            box = open_win.child_window(title=title, control_type="Edit")
            if box.exists(timeout=1):
                filename_box = box
                break
        except Exception:
            continue

    if not filename_box:
        edits = open_win.descendants(control_type="Edit")
        if edits:
            filename_box = edits[-1]
        else:
            raise RuntimeError("File name input not found.")

    filename_box.set_focus()
    filename_box.type_keys(filename, with_spaces=True)
    time.sleep(0.5)
    filename_box.type_keys("{ENTER}")
    print(f"File opened: {filename}")
    time.sleep(3)


def open_project_file(main_win, target_file):
    item = main_win.child_window(title=target_file, control_type="MenuItem")
    item.wait("visible enabled ready", timeout=10)
    item.click_input()
    time.sleep(1)


def generate_filename(extension="project"):
    rand_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{rand_str}.{extension}"


def save_as_file(main_win, filename):
    bring_to_front(main_win)
    click_menu_item(main_win, "파일")
    click_menu_item(main_win, "다른 이름으로 저장...", invoke=True)
    time.sleep(1)

    try:
        save_win = main_win.child_window(title="다른 이름으로 저장", control_type="Window")
        save_win.wait("visible enabled ready", timeout=5)
    except Exception:
        desktop = Desktop(backend="uia")
        save_win = desktop.window(title_re=r".*다른 이름으로 저장.*")
        save_win.wait("visible enabled ready", timeout=5)

    save_win.set_focus()
    time.sleep(0.5)

    filename_box = None
    for title in ["파일 이름(N):", "파일 이름:", "File name:", "File name"]:
        try:
            box = save_win.child_window(title=title, control_type="Edit")
            if box.exists(timeout=1):
                filename_box = box
                break
        except Exception:
            continue
    if not filename_box:
        edits = save_win.descendants(control_type="Edit")
        if edits:
            filename_box = edits[0]
        else:
            raise RuntimeError("File name input not found.")

    filename_box.set_focus()
    filename_box.type_keys(filename, with_spaces=True)
    time.sleep(0.3)
    filename_box.type_keys("{ENTER}")
    time.sleep(0.8)

    try:
        save_dialog = main_win.child_window(title="다른 이름으로 저장", control_type="Window")
        save_dialog.wait("visible", timeout=3)
        confirm = save_dialog.child_window(title="다른 이름으로 저장 확인", control_type="Window")
        confirm.wait("visible", timeout=3)
        no_btn = confirm.child_window(title="아니요(N)", control_type="Button")
        no_btn.wait("enabled ready visible", timeout=3)
        no_btn.click_input()
        time.sleep(0.5)
        filename_box.set_focus()
        filename_box.type_keys("{HOME}{DEL 50}")
        time.sleep(0.3)
        random_filename = generate_filename()
        filename_box.type_keys(random_filename, with_spaces=True)
        time.sleep(0.2)
        filename_box.type_keys("{ENTER}")
        print(f"Saved with random filename: {random_filename}")
        return random_filename
    except Exception:
        return filename


# ===============================================================
# 4. 다이얼로그 / 팝업 제어 (Dialog / Popup Control)
# ===============================================================

def close_license_dialog(main_win):
    desktop = Desktop(backend="uia")
    panel = desktop.window(title_re=r".*라이선스 정보.*")
    if panel.exists(timeout=2):
        panel.type_keys("{ESC}")
        time.sleep(0.3)


def close_window_by_title_re(title_re_list, timeout=5):
    desktop = Desktop(backend="uia")
    for title_re in title_re_list:
        try:
            win = desktop.window(title_re=title_re)
            if win.exists(timeout=timeout):
                win.close()
                time.sleep(0.5)
                return True
        except Exception:
            continue
    return False


def open_print_dialog_and_close(main_win):
    try:
        bring_to_front(main_win)
        click_menu_item(main_win, "파일")
        click_menu_item(main_win, "인쇄...", invoke=True)
        time.sleep(1)
        desktop = Desktop(backend="uia")
        print_win = desktop.window(title_re=r".*인쇄.*")
        if print_win.exists(timeout=3):
            print_win.set_focus()
            try:
                close_btn = print_win.child_window(title_re=r"닫기|취소", control_type="Button")
                if close_btn.exists(timeout=2):
                    close_btn.click_input()
            except Exception:
                print_win.type_keys("{ESC}")
            time.sleep(0.5)
    except Exception as e:
        print(f"Print dialog error: {e}")


def navigate_setting_sidebar(main_win, items=None):
    if items is None:
        items = ["전체", "프로젝트", "DBMS 연결", "모델 디자이너", "리포지토리", "테마"]

    open_sidebar_panel(main_win)
    click_sidebar_item(main_win, "작업 기록")
    click_sidebar_item(main_win, "설정")
    time.sleep(1.5)

    for item in items:
        click_setting_sidebar_item(main_win, item)

    close_sidebar_panel_esc(main_win)


def click_setting_sidebar_item(main_win, title):
    try:
        setting_text = main_win.child_window(title="설정", control_type="Text")
        setting_parent = setting_text.parent()
    except Exception:
        raise RuntimeError("Setting panel not found.")

    list_ctrls = setting_parent.children(control_type="List")
    for list_ctrl in list_ctrls:
        for item in list_ctrl.children(control_type="ListItem"):
            text_ctrls = item.children(control_type="Text")
            if any(txt.window_text() == title for txt in text_ctrls):
                item.click_input()
                time.sleep(0.3)
                print(f"Clicked: {title}")
                return

    raise RuntimeError(f"Setting item not found: {title}")


def close_sidebar_panel_esc(main_win):
    send_keys('{ESC}')
    time.sleep(0.3)


def random_tab_name(prefix="Tab"):
    suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    return f"{prefix}_{suffix}"


def add_new_tab_and_confirm(main_win):
    print("1. Click Add Tab button")
    main_win.child_window(auto_id="AddButton", control_type="Button").click_input()
    time.sleep(0.3)

    print("2. Searching popup...")
    desktop = Desktop(backend="uia")
    popup = None
    ok_btn = None
    text_edit = None

    for _ in range(10):
        try:
            popup_candidate = desktop.window(control_type="Window", found_index=0)
            ok_btn_candidate = popup_candidate.child_window(title="확인", control_type="Button")
            text_edit_candidate = popup_candidate.child_window(auto_id="inputTextBox", control_type="Edit")
            if ok_btn_candidate.exists() and text_edit_candidate.exists():
                popup = popup_candidate
                ok_btn = ok_btn_candidate
                text_edit = text_edit_candidate
                print("Popup detected.")
                break
        except Exception:
            pass
        time.sleep(0.5)

    if popup is None or ok_btn is None or text_edit is None:
        raise RuntimeError("Popup or input field not found.")

    tab_name = random_tab_name()
    print(f"3. Input tab name: {tab_name}")

    text_edit.click_input()
    time.sleep(0.2)
    text_edit.type_keys(tab_name, with_spaces=True)
    ok_btn.click_input()
    print("4. Confirmed.")

    return tab_name