"""관리자 웹의 실제 HTTP 통신을 기록해 API 테스트 대상을 찾는다.

로그인 → 작업자 목록 → 검색만 수행한다 (데이터를 만들거나 지우지 않음).
실행:  python tools/capture_network.py
결과:  debug_screenshots/network_log.txt  (호스트 주소는 <BASE_URL>로 가려서 저장)
"""
import os
import sys
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))

BASE_URL = os.environ["BASE_URL"].rstrip("/")
if not BASE_URL.startswith(("http://", "https://")):
    BASE_URL = "http://" + BASE_URL
ADMIN_ID = os.environ["ADMIN_ID"]
ADMIN_PW = os.environ["ADMIN_PW"]

STATIC = (".js", ".css", ".png", ".jpg", ".svg", ".woff", ".woff2", ".ttf", ".ico", ".map")
lines = []


def mask(url):
    return url.replace(BASE_URL, "<BASE_URL>")


def on_response(resp):
    req = resp.request
    path = urlparse(req.url).path
    if path.endswith(STATIC):
        return
    ctype = resp.headers.get("content-type", "")
    lines.append(f"{req.method:6} {resp.status} {req.resource_type:9} {ctype[:40]:40} {mask(req.url)}")


def on_ws(ws):
    lines.append(f"WEBSOCKET               {mask(ws.url)}")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=os.environ.get("HEADED", "0") != "1",
                                executable_path=os.environ.get("BROWSER_EXECUTABLE_PATH") or None)
    page = browser.new_context(base_url=BASE_URL).new_page()
    page.on("response", on_response)
    page.on("websocket", on_ws)

    lines.append("== 1. 첫 접속 ==")
    page.goto("/worker")
    page.wait_for_timeout(2000)
    if page.locator('input[type="password"]').is_visible():
        lines.append("== 2. 로그인 ==")
        page.locator('input[type="text"]').first.fill(ADMIN_ID)
        page.locator('input[type="password"]').fill(ADMIN_PW)
        page.get_by_role("button", name="로그인").click()
        page.wait_for_timeout(3000)
    lines.append("== 3. 작업자 목록 ==")
    page.get_by_role("table").wait_for(timeout=15000)
    page.wait_for_timeout(1500)
    lines.append("== 4. 검색 ==")
    page.get_by_role("textbox").first.fill("zzz_not_exist_xyz")
    page.wait_for_timeout(2000)
    browser.close()

out_dir = os.path.join(ROOT, "debug_screenshots")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "network_log.txt")
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("\n".join(lines))
print(f"\n저장: {out}")
