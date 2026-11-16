import os
import time

import pytest

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
except ImportError:
    pass

from playwright.sync_api import sync_playwright, expect

from web import test_data

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCREENSHOT_DIR = os.path.join(ROOT_DIR, "debug_screenshots", "web")

expect.set_options(timeout=5_000)


def _normalize_base_url(url):
    """BASE_URL 형식을 검사하고, 스킴이 빠졌으면 http://를 붙인다."""
    url = url.strip().strip('"').strip("'")
    if "<" in url or ">" in url:
        pytest.skip(f"BASE_URL에 예시 값이 남아 있습니다: {url} (.env에 실제 주소 입력)")
    if not url.startswith(("http://", "https://")):
        print(f"\nBASE_URL에 http://가 없어 자동으로 추가합니다: {url}")
        url = "http://" + url
    return url.rstrip("/")


def _require_env():
    # load_dotenv 이후 값을 다시 읽는다
    missing = [k for k in ("BASE_URL", "ADMIN_ID", "ADMIN_PW") if not os.environ.get(k)]
    if missing:
        pytest.skip(f"웹 테스트 환경변수 없음: {', '.join(missing)} (.env.example 참고)")
    test_data.BASE_URL = _normalize_base_url(os.environ["BASE_URL"])
    test_data.ADMIN_ID = os.environ["ADMIN_ID"]
    test_data.ADMIN_PW = os.environ["ADMIN_PW"]


@pytest.fixture(scope="session")
def browser():
    _require_env()
    headed = os.environ.get("HEADED", "0") == "1"
    with sync_playwright() as p:
        # 선택: 설치된 다른 Chromium을 쓰려면 BROWSER_EXECUTABLE_PATH 지정
        executable = os.environ.get("BROWSER_EXECUTABLE_PATH") or None
        browser = p.chromium.launch(headless=not headed, executable_path=executable)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(base_url=test_data.BASE_URL, locale="ko-KR")
    page = context.new_page()
    yield page
    context.close()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """웹 테스트 실패 시 브라우저 화면을 debug_screenshots/web/에 저장.

    fixture에서 데이터를 만들다 실패한 경우(setup)도 캡처한다.
    """
    outcome = yield
    report = outcome.get_result()
    if report.when not in ("setup", "call") or not report.failed:
        return
    page = item.funcargs.get("page")
    if page is None:
        return
    try:
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        path = os.path.join(SCREENSHOT_DIR, f"{time.strftime('%Y%m%d_%H%M%S')}_{item.name}_{report.when}.png")
        page.screenshot(path=path, full_page=True)
        print(f"\nScreenshot saved: {path}")
    except Exception as e:
        print(f"\nScreenshot failed: {e}")
