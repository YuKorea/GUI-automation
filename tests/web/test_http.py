"""HTTP·보안 관점 테스트.

이 관리자 웹은 Blazor Server 구조라 화면 동작이 REST API가 아니라 웹소켓(/_blazor)으로
처리된다. 그래서 테스트할 업무 API 대신, HTTP 계층에서 확인할 수 있는 것을 검증한다:
페이지 응답, Blazor 연결 준비 엔드포인트, 오류 처리, 인증 우회, HTTPS, 보안 헤더.
(통신 구조는 tools/capture_network.py로 확인)
"""
import time

import pytest
from playwright.sync_api import expect

from web import test_data
from web.pages.login_page import LoginPage

pytestmark = pytest.mark.web

PROTECTED_PAGES = ["/worker", "/group", "/commoncode"]


# ── 페이지 응답 ──

def test_page_responds_with_html_quickly(api):
    start = time.monotonic()
    resp = api.get("/worker")
    elapsed = time.monotonic() - start
    assert resp.status == 200
    assert "text/html" in resp.headers.get("content-type", "")
    assert elapsed < 3.0, f"응답 시간 {elapsed:.2f}s (기준 3s)"


def test_unknown_path_is_not_server_error(api):
    resp = api.get("/zzz-not-exist-page")
    assert resp.status < 500, f"없는 경로에서 서버 오류: {resp.status}"


# ── Blazor 연결 준비 엔드포인트 ──

def test_blazor_negotiate_offers_websocket(api):
    resp = api.post("/_blazor/negotiate?negotiateVersion=1")
    assert resp.status == 200
    body = resp.json()
    assert body.get("connectionToken") or body.get("connectionId"), body
    transports = [t.get("transport") for t in body.get("availableTransports", [])]
    assert "WebSockets" in transports, transports


def test_blazor_negotiate_rejects_get(api):
    resp = api.get("/_blazor/negotiate?negotiateVersion=1")
    assert 400 <= resp.status < 500, f"GET이 허용됨: {resp.status}"


# ── 인증 우회 ──

@pytest.mark.parametrize("path", PROTECTED_PAGES)
def test_protected_page_requires_login(page, path):
    """로그인하지 않은 새 브라우저로 관리 화면 주소에 바로 들어가면 목록이 아니라 로그인 화면이 나와야 한다."""
    page.goto(path)
    login = LoginPage(page)
    expect(login.password_input).to_be_visible(timeout=10_000)
    expect(page.get_by_role("table")).to_have_count(0)


# ── HTTPS ──

def test_http_redirects_to_https(playwright_instance):
    if not test_data.BASE_URL.startswith("https://"):
        pytest.skip("BASE_URL이 https가 아님")
    http_url = "http://" + test_data.BASE_URL[len("https://"):]
    ctx = playwright_instance.request.new_context()
    try:
        try:
            resp = ctx.get(http_url + "/worker", max_redirects=0)
        except Exception as e:  # http 포트가 닫혀 있으면 평문으로는 접속 자체가 안 됨
            pytest.skip(f"http 포트 응답 없음: {e}")
        assert resp.status in (301, 302, 307, 308), f"리다이렉트 없음: {resp.status}"
        assert resp.headers.get("location", "").startswith("https://")
    finally:
        ctx.dispose()


# ── 보안 헤더 ──

def _headers(api):
    return {k.lower(): v for k, v in api.get("/worker").headers.items()}


def test_header_x_content_type_options(api):
    assert _headers(api).get("x-content-type-options", "").lower() == "nosniff"


def test_header_clickjacking_protection(api):
    h = _headers(api)
    csp = h.get("content-security-policy", "")
    assert "x-frame-options" in h or "frame-ancestors" in csp, "X-Frame-Options / CSP frame-ancestors 없음"


def test_header_hsts(api):
    if not test_data.BASE_URL.startswith("https://"):
        pytest.skip("HSTS는 https에서만 의미가 있음")
    assert "strict-transport-security" in _headers(api)
