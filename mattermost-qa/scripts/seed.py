"""테스트 전제 데이터를 만든다 (여러 번 실행해도 결과가 같다 = 멱등).

만드는 것: 관리자, 일반 사용자, 팀, 두 사용자의 팀 가입, 온보딩·튜토리얼 끄기.
UI로 하면 느리고 잘 깨지므로 API로 준비한다. CI에서도 이 스크립트를 그대로 쓴다.

실행: python scripts/seed.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from api.client import MattermostClient  # noqa: E402


def ensure_user(client: MattermostClient, account: config.Account, email: str) -> None:
    resp = client.post("/users", json={"username": account.username, "password": account.password, "email": email})
    if resp.status_code == 201:
        print(f"  사용자 생성: {account.username}")
    elif resp.status_code == 400 and "exists" in resp.text:
        print(f"  사용자 있음: {account.username}")
    else:
        sys.exit(f"사용자 생성 실패 {account.username}: {resp.status_code} {resp.text}")


def main() -> None:
    if not config.ADMIN.password or not config.USER.password:
        sys.exit(".env에 MM_ADMIN_PASSWORD, MM_USER_PASSWORD를 넣어 주세요 (.env.example 참고)")

    admin = MattermostClient()
    # 서버의 첫 번째 사용자는 자동으로 시스템 관리자가 된다.
    # 첫 사용자가 생긴 뒤에는 비로그인 가입이 막히므로(403), 관리자는 "로그인 시도 → 없으면 생성" 순서로 준비한다.
    if admin.login(config.ADMIN.username, config.ADMIN.password).status_code != 200:
        ensure_user(admin, config.ADMIN, "qa-admin@example.com")
        if admin.login(config.ADMIN.username, config.ADMIN.password).status_code != 200:
            sys.exit("관리자 로그인 실패: 비밀번호가 .env와 다른지 확인하세요")
    if "system_admin" not in admin.me().json()["roles"]:
        sys.exit(f"{config.ADMIN.username}이 시스템 관리자가 아닙니다 (서버에 먼저 만든 사용자가 있음)")

    # 나머지 사용자는 관리자 권한으로 만든다.
    ensure_user(admin, config.USER, "qa-user@example.com")

    team = admin.team_by_name(config.TEAM_NAME)
    if team.status_code == 404:
        team = admin.post("/teams", json={"name": config.TEAM_NAME, "display_name": "QA Team", "type": "O"})
        print(f"  팀 생성: {config.TEAM_NAME}")
    team_id = team.json()["id"]

    for account in (config.ADMIN, config.USER):
        user_id = admin.get(f"/users/username/{account.username}").json()["id"]
        r = admin.post(f"/teams/{team_id}/members", json={"team_id": team_id, "user_id": user_id})
        assert r.status_code == 201, r.text
        # 첫 로그인 때 뜨는 온보딩 체크리스트·튜토리얼은 화면을 덮어 클릭을 가로챈다.
        # 테스트 대상이 아니므로 사용자 설정(preferences)으로 미리 꺼 둔다.
        prefs = [
            {"user_id": user_id, "category": "onboarding_task_list", "name": "onboarding_task_list_show", "value": "false"},
            {"user_id": user_id, "category": "onboarding_task_list", "name": "onboarding_task_list_open", "value": "false"},
            {"user_id": user_id, "category": "tutorial_step", "name": user_id, "value": "999"},
            {"user_id": user_id, "category": "recommended_next_steps", "name": "hide", "value": "true"},
        ]
        r = admin.put(f"/users/{user_id}/preferences", json=prefs)
        assert r.status_code == 200, r.text

    # 관리자 첫 로그인 시 나오는 '작업 공간 준비' 마법사를 건너뛴다.
    admin.post("/system/onboarding/complete", json={"organization": "QA", "install_plugins": []})
    print("시드 완료")


if __name__ == "__main__":
    main()
