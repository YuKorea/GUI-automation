import pytest


@pytest.fixture(autouse=True)
def skip_landing_page(context):
    """'데스크톱 앱으로 열기 / 브라우저로 보기' 안내 화면을 건너뛴다.

    실제 사용자가 'View in Browser'를 한 번 누르면 localStorage에 남는 값을 미리 넣는 것이다.
    테스트마다 그 화면을 클릭하는 것보다 빠르고, 테스트 대상이 아닌 화면 때문에 실패하지 않는다.
    """
    context.add_init_script("window.localStorage.setItem('__landingPageSeen__', 'true')")
