# gui-automation

Windows 데스크톱 애플리케이션과 관리자 웹 페이지를 함께 검증하는 Python 기반 테스트 자동화 프로젝트

> 본 프로젝트는 사내 시스템을 대상으로 작성되었습니다.
>
> 실제 실행을 위해서는 대상 애플리케이션, 관리자 페이지 접속 정보 및 관련 파일이 필요하며, 해당 정보는 공개되어 있지 않습니다.

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.10+ (3.13에서 검증) |
| 데스크톱 UI 자동화 | Pywinauto (UIA backend) |
| 이미지 인식 | PyAutoGUI + OpenCV |
| 웹 UI 자동화 | Playwright for Python |
| 테스트 프레임워크 | pytest |
| 설정 관리 | python-dotenv (`.env`) |
| 프로세스 관리 | psutil |

---

## 주요 기능

### 데스크톱 앱

- **앱 실행 / 연결** — 실행 중인 프로세스 탐지 및 attach, 미실행 시 EXE 자동 실행
- **창 포커스 관리** — 클릭·이미지 인식 전에 대상 앱을 맨 앞으로 가져옴 (IDE 등 다른 창에 가려지는 문제 방지, 앱 자신의 메뉴·팝업은 유지)
- **메뉴 / 사이드바 / 설정 탐색** — UIA 기반 메뉴, 서브메뉴, 사이드바 항목 순회
- **엔터티 생성** — 캔버스 탐지 후 이미지 인식을 통한 엔터티 및 속성 입력
- **관계선 생성** — 캔버스 기준 좌표로 관계선을 열고 속성 입력 (창 크기·위치가 달라도 동작)
- **결과 검증** — 모델 탐색기 트리를 UIA로 읽어 엔터티·관계 생성 여부를 assert
- **파일 처리** — 새 프로젝트, 파일 열기, 다른 이름으로 저장, 중복 파일명 처리
- **다이얼로그 / 탭** — 팝업 감지 및 닫기, 랜덤 이름 기반 새 탭 추가
- **실패 진단** — 이미지 인식 실패 시 화면 캡처, 탐색기 트리 상태 출력

### 관리자 웹

- **작업자 / 그룹 / 공통코드 CRUD** — 생성, 필수값 검증, 검색, 수정, 삭제
- **공통 페이지 객체** — 로그인, 등록 팝업, 검색 후 행 찾기(여러 페이지 대응), 확인창 처리, 라벨로 입력칸 찾기
- **독립적인 테스트** — 각 테스트가 데이터를 직접 만들고 끝나면 삭제 (테스트 간 상태 공유·고정 계정 의존 없음)
- **실패 진단** — 실패 시 브라우저 화면 캡처, 팝업이 닫히지 않으면 팝업 내용과 입력값 출력

---

## 프로젝트 구조

```text
gui-automation/
├── conftest.py                  # 데스크톱 fixture (앱 실행/연결, 라벨 이미지 경로), .env 로드
├── pytest.ini                   # 마커 등록 (desktop / web)
├── requirements.txt
├── .env.example                 # 설정 형식 (실제 값은 .env, 커밋 제외)
├── asset/                       # 이미지 인식용 라벨 이미지 (실제 이미지는 저장소 제외, 자리표시 파일만 포함)
│   ├── description_label.png
│   ├── logical_label.png
│   └── physical_label.png
├── utils/                       # 데스크톱 자동화
│   ├── utils.py                 # 앱 연결, 창 포커스, 메뉴, 사이드바, 파일, 다이얼로그, 탭
│   ├── entity_actions.py        # 캔버스, 엔터티, 관계선, 이미지 인식
│   └── model_explorer.py        # 모델 탐색기 트리 읽기 (결과 검증)
├── web/                         # 관리자 웹 자동화
│   ├── test_data.py             # 테스트 데이터, 환경변수
│   └── pages/
│       ├── admin_list_page.py   # 목록 화면 공통 페이지 객체
│       ├── login_page.py
│       ├── worker_page.py
│       ├── group_page.py
│       └── commoncode_page.py
└── tests/
    ├── test_app.py              # 데스크톱 테스트 (13)
    └── web/
        ├── conftest.py          # 브라우저 fixture, 실패 시 캡처
        ├── test_worker_crud.py      # 작업자 (10)
        ├── test_group_crud.py       # 그룹 (7)
        └── test_commoncode_crud.py  # 공통코드 (7)
```

---

## 테스트 케이스

### 데스크톱 앱 (13개, `-m desktop`)

| # | 테스트 | 설명 |
|---|------|------|
| 1 | test_open_project | 최근 프로젝트 열기 |
| 2 | test_view_menu | 보기 메뉴 동작 |
| 3 | test_sidebar_navigation | 사이드바 항목 탐색 |
| 4 | test_help_menu | 도움말 메뉴 및 팝업 처리 |
| 5 | test_new_project | 새 프로젝트 생성 |
| 6 | test_open_file | 파일 열기 다이얼로그 |
| 7 | test_save_as_duplicate | 중복 파일명 처리 |
| 8 | test_print_dialog | 인쇄 다이얼로그 열기/닫기 |
| 9 | test_entity_creation_flow | 엔터티 생성 및 속성 입력 → 모델 탐색기에서 생성 확인 |
| 10 | test_add_entity_and_create_relationship | 관계선 생성 및 속성 입력 → 엔터티 2개·관계 1개 이상 확인 |
| 11 | test_setting_sidebar_navigation | 설정 사이드바 탐색 |
| 12 | test_add_new_tab | 랜덤 이름 기반 새 탭 추가 |
| 13 | test_edit_undo | 실행 취소(Undo) 동작 |

### 관리자 웹 (24개, `-m web`)

| 화면 | 테스트 수 | 내용 |
|------|------|------|
| 작업자 관리 | 10 | 팝업 열기/취소, 생성, 아이디 필수값, 검색(존재/없음/초기화), 수정 팝업, 삭제, 승인상태 |
| 그룹 관리 | 7 | 팝업 열기/취소, 생성, 그룹명 필수값, 검색(존재/없음), 삭제 |
| 공통코드 관리 | 7 | 팝업 열기/취소, 생성, 코드 필수값, 검색(존재/없음), 삭제 |

검색 "없음" 테스트는 결과가 0건인지만 보지 않고, 원래 보이던 행이 실제로 사라지는지 확인합니다.

---

## 설치 및 실행

### 1. 설치

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### 2. 설정 (.env)

`.env.example`을 `.env`로 복사한 뒤 실제 값을 입력합니다. `.env`는 `.gitignore`로 제외되어 커밋되지 않습니다.

```bash
copy .env.example .env
```

| 변수 | 용도 |
|------|------|
| `APP_EXE_PATH` | 데스크톱 앱 실행 파일 경로 |
| `APP_TARGET_FILE` | 최근 프로젝트 메뉴에 표시되는 대상 파일 이름 |
| `BASE_URL`, `ADMIN_ID`, `ADMIN_PW` | 관리자 웹 주소와 계정 |
| `GROUP_MEMBER_ID` (선택) | 그룹 담당자 드롭다운에서 고를 이름 (비우면 첫 항목) |
| `EXISTING_CODE_KEYWORD` (선택) | 공통코드 검색에 쓸 기존 키워드 |
| `HEADED` (선택) | `1`이면 브라우저 창을 띄워서 실행 |

웹 설정이 없으면 웹 테스트는 skip 됩니다.

### 3. 실행

```bash
pytest -v               # 전체
pytest -m desktop -v    # 데스크톱 앱 테스트만
pytest -m web -v        # 관리자 웹 테스트만
```

실패 시 화면 캡처는 `debug_screenshots/`(웹은 `debug_screenshots/web/`)에 저장되며 커밋에서 제외됩니다.

### 4. 데스크톱 테스트 실행 시 주의사항

- 테스트 실행 중 마우스 및 키보드 사용 금지
- Windows 디스플레이 배율 100% 권장
- 원격 데스크톱(RDP) 환경 비권장
- 테스트 중단 시 터미널에서 `Ctrl + C` 입력

---

## 제한 사항

- 관계선: UIA 미지원으로 캔버스 기준 좌표를 더블클릭해 속성 패널을 엶 (실패 시 기존 화면 좌표로 재시도)
- 엔터티·관계 속성 패널: 디스플레이 해상도 및 배율에 따라 이미지 인식 결과 차이 발생 가능
- 캔버스 영역: UIA 정보 부족으로 정밀 제어 제한 존재
- 데스크톱 테스트는 하나의 앱 인스턴스를 공유하므로 파일에 적힌 순서대로 실행해야 함

---

## 데모

데모 영상은 `docs/demo/` 경로에 저장되어 있으며 보안 이슈 상 저장소에는 포함되지 않습니다.

---

# gui-automation (English)

Python-based test automation for a Windows desktop application and its admin web page

> This repository is for portfolio and demonstration purposes only.
> Actual execution requires the target application, admin page credentials and related files, which are not publicly available.

---

## Tech Stack

| Item | Detail |
|------|--------|
| Language | Python 3.10+ (verified on 3.13) |
| Desktop UI Automation | Pywinauto (UIA backend) |
| Image Recognition | PyAutoGUI + OpenCV |
| Web UI Automation | Playwright for Python |
| Test Framework | pytest |
| Configuration | python-dotenv (`.env`) |
| Process Management | psutil |

---

## Key Features

### Desktop app

- **App Launch / Connect** — Attach to a running process or launch the EXE
- **Window Focus** — Bring the app to the front before clicks and image search, without closing its own menus or popups
- **Menu / Sidebar / Settings Navigation** — UIA-based traversal
- **Entity Creation** — Canvas detection, entity creation and attribute input via image recognition
- **Relationship Creation** — Opens the relationship panel at a canvas-relative point (independent of window size and position)
- **Result Verification** — Reads the model explorer tree through UIA and asserts that entities and relationships were created
- **File Handling** — New project, open, save-as, duplicate filename handling
- **Dialogs / Tabs** — Popup detection and close, new tab with a random name
- **Failure Diagnostics** — Screenshot on image-recognition failure, explorer tree dump

### Admin web

- **Worker / Group / Common Code CRUD** — Create, required-field validation, search, edit, delete
- **Shared Page Object** — Login, add popup, search-before-row lookup (paging-safe), confirm dialogs, label-based field lookup
- **Independent Tests** — Each test creates and deletes its own data; no shared state or fixed accounts
- **Failure Diagnostics** — Browser screenshot on failure; popup text and input values when a form does not close

---

## Test Cases

| Suite | Count | Marker |
|------|------|------|
| Desktop app | 13 | `pytest -m desktop` |
| Admin web — Worker | 10 | `pytest -m web` |
| Admin web — Group | 7 | `pytest -m web` |
| Admin web — Common Code | 7 | `pytest -m web` |

---

## Setup & Run

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
copy .env.example .env      # then fill in real values (.env is git-ignored)

pytest -v                   # all
pytest -m desktop -v        # desktop app only
pytest -m web -v            # admin web only
```

Web tests are skipped when the web settings are missing. Failure screenshots go to `debug_screenshots/` (git-ignored).

**Desktop test notes:** do not use the mouse or keyboard while tests run; 100% display scale recommended; RDP not recommended; stop with `Ctrl + C`.

---

## Known Limitations

- Relationship line: no UIA support — double-clicks a canvas-relative point (falls back to the previous screen position)
- Property panels: image recognition may vary by display resolution/scale
- Canvas area: limited UIA information for precise control
- Desktop tests share one app instance and must run in file order

---

## Demo

Demo videos are stored in `docs/demo/` (excluded from repository).
