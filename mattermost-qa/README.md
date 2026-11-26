# Mattermost QA Automation

오픈소스 사내 메신저 [Mattermost](https://github.com/mattermost/mattermost)를 대상으로 한 웹 테스트 자동화 프로젝트입니다.
테스트 계획 → 위험 기반 TC 설계 → API 테스트 → E2E 테스트 → CI 순서로 실무 방식 그대로 진행합니다.

| 항목 | 현재 |
|------|------|
| 테스트 | API 10개 + E2E 3개 = 13개, 전체 실행 약 14초 |
| 안정성 | 새 서버에서 시드 후 실행, 3회 연속 실행 결과 동일 |
| 문서 | [테스트 계획서](docs/test-plan.md) (범위, 위험 우선순위, TC 표) |

## 기술 스택

Python 3.13 · pytest · Playwright (pytest-playwright) · requests · jsonschema · Docker

## 구조

```
mattermost-qa/
├── api/client.py        # REST API v4 클라이언트 (토큰 처리, 응답은 그대로 반환)
├── pages/               # Page Object (login, channel)
├── schemas/             # 응답 JSON 스키마 (필드·타입 계약, 비밀번호 노출 금지)
├── scripts/seed.py      # 테스트 데이터 준비 (API, 멱등)
├── tests/
│   ├── api/             # 인증·권한 API 테스트
│   └── e2e/             # 브라우저 UI 테스트
├── docs/test-plan.md
└── conftest.py          # API 클라이언트(익명/사용자/관리자), 브라우저 설정
```

## 실행 방법

```bash
docker run --name mattermost-preview -d -p 8065:8065 mattermost/mattermost-preview
```

```bash
pip install -r requirements.txt
```

```bash
playwright install chromium firefox webkit
```

```bash
cp .env.example .env
```

`.env`의 비밀번호를 원하는 값으로 바꾼 뒤(대문자·숫자·특수문자 포함), 데이터를 준비하고 테스트를 실행합니다.

```bash
python scripts/seed.py
```

```bash
pytest
```

자주 쓰는 옵션:

```bash
pytest -m api
```

```bash
pytest -m smoke --browser firefox --browser webkit
```

```bash
pytest -m e2e --headed --slowmo 300
```

## 설계에서 신경 쓴 점

- **API로 준비하고 UI로 검증**: 사용자·팀은 시드 스크립트가 API로 만듭니다. UI로 데이터를 만들면 느리고, 테스트 대상이 아닌 화면 때문에 실패합니다.
- **대조군이 있는 권한 테스트**: 일반 사용자 403(PERM-01)만 보면 API가 고장 나도 통과할 수 있어, 관리자 200(PERM-02)을 함께 둡니다.
- **스키마 검증**: 값 몇 개만 확인하지 않고, 응답 형식 전체와 "비밀번호 필드가 없어야 함"을 스키마로 검증합니다.
- **TC ID 추적**: 테스트 함수 이름의 `auth_01`, `perm_01`이 계획서 TC ID와 같습니다.
- **서버 미기동 즉시 중단**: 서버가 없으면 테스트 수십 개가 각자 타임아웃되지 않고, 시작 시 한 번에 원인을 알려 줍니다.

## 로드맵

- [x] 1주차: 테스트 계획서, 프로젝트 구조, 인증·권한 API/E2E
- [ ] 2주차: 채널·메시지 E2E
- [ ] 3~4주차: 채널·게시글 CRUD API, 비공개 채널 권한, 파일 업로드, 실시간 반영
- [ ] 5주차: GitHub Actions (PR마다 실행, 3개 브라우저, Allure 리포트를 GitHub Pages에 게시)
- [ ] 6주차: 버그 리포트, 최종 정리

> 테스트는 로컬·CI에 띄운 서버에서만 실행합니다. 운영 중인 Mattermost 서버에는 실행하지 않습니다.
