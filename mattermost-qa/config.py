"""테스트 설정을 한곳에서 읽는다.

값은 .env(로컬) 또는 환경 변수(CI)에서 온다. 코드에 계정 정보를 직접 쓰지 않기 위해서다.
"""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")


@dataclass(frozen=True)
class Account:
    username: str
    password: str


BASE_URL = os.getenv("MM_BASE_URL", "http://localhost:8065").rstrip("/")
API_URL = f"{BASE_URL}/api/v4"
TEAM_NAME = os.getenv("MM_TEAM", "qa-team")

ADMIN = Account(os.getenv("MM_ADMIN_USERNAME", "qa-admin"), os.environ.get("MM_ADMIN_PASSWORD", ""))
USER = Account(os.getenv("MM_USER_USERNAME", "qa-user"), os.environ.get("MM_USER_PASSWORD", ""))

CHROMIUM_PATH = os.getenv("PW_CHROMIUM_PATH") or None
