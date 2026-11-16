import pytest
import logging
import os
from pywinauto.timings import TimeoutError
from utils.utils import start_or_connect_app, get_main_window

# .env가 있으면 환경변수로 읽는다 (경로·계정 등은 코드에 쓰지 않는다)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))
except ImportError:
    pass

# ===============================================================
# 실행 파일 경로 — 환경변수 또는 직접 수정
# ===============================================================
APP_EXE_PATH = os.environ.get(
    "APP_EXE_PATH",
    r"C:\..\app.exe"
)

# ===============================================================
# 테스트 파일 경로 — 환경변수 또는 직접 수정
# ===============================================================
TARGET_FILE = os.environ.get(
    "APP_TARGET_FILE",
    r"<ProjectName> - C:\..\sample.project"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

# ----------------------------------------------------------------------
# Fixture: 메인 윈도우
# ----------------------------------------------------------------------
@pytest.fixture(scope="module")
def app_main_window():
    app = None
    win = None
    try:
        logging.info("Application launch or connect...")
        app = start_or_connect_app(APP_EXE_PATH)
        win = get_main_window(app)
        win.set_focus()
        win.wait("ready", timeout=10)
        logging.info("Application ready.")
    except TimeoutError as e:
        pytest.fail(f"Window wait timeout: {e}")
    except Exception as e:
        pytest.fail(f"Application launch failed: {e}")

    yield win

    try:
        if win is not None:
            logging.info("Closing application...")
            win.set_focus()
            win.type_keys("{ESC}")
            win.close()
            logging.info("Application closed.")
    except Exception as e:
        logging.warning(f"Error during close: {e}")

# ----------------------------------------------------------------------
# Fixture: 이미지 경로 제공
# ----------------------------------------------------------------------
@pytest.fixture(scope="session")
def logical_image_path():
    path = os.path.join(BASE_DIR, "asset", "logical_label.png")
    if not os.path.exists(path):
        pytest.fail(f"Image file not found: {path}")
    return path

@pytest.fixture(scope="session")
def physical_image_path():
    path = os.path.join(BASE_DIR, "asset", "physical_label.png")
    if not os.path.exists(path):
        pytest.fail(f"Image file not found: {path}")
    return path

@pytest.fixture(scope="session")
def description_image_path():
    path = os.path.join(BASE_DIR, "asset", "description_label.png")
    if not os.path.exists(path):
        pytest.fail(f"Image file not found: {path}")
    return path