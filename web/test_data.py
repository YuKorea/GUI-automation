import os
import time

# 계정·URL 등 민감 정보는 .env에서 읽는다 (.env.example 참고).
BASE_URL = os.environ.get("BASE_URL", "")
ADMIN_ID = os.environ.get("ADMIN_ID", "")
ADMIN_PW = os.environ.get("ADMIN_PW", "")


NOT_EXIST_KEYWORD = "zzz_not_exist_xyz"
WORKER_PASSWORD = "Test1234!"
WORKER_NAME = "QA테스트"


def unique_worker_id(prefix="qa"):
    """테스트마다 겹치지 않는 작업자 ID."""
    return f"{prefix}_{int(time.time() * 1000)}"


# 선택: 그룹 관리자/작업자 드롭다운에서 고를 이름. 비어 있으면 목록의 첫 항목을 고른다.
GROUP_MEMBER_ID = os.environ.get("GROUP_MEMBER_ID", "")

# 공통코드 검색에 쓸, 이미 존재하는 코드의 키워드
EXISTING_CODE_KEYWORD = os.environ.get("EXISTING_CODE_KEYWORD", "시스템")


def unique_suffix(length=5):
    """짧은 고유 문자열 (밀리초 타임스탬프 끝자리)."""
    return str(int(time.time() * 1000))[-length:]
