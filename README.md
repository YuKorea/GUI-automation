# gui-automation

Windows 데스크톱 애플리케이션을 위한 Python 기반 GUI 자동화 테스트 프로젝트

> 본 프로젝트는 사내 시스템을 대상으로 작성되었습니다.
> 
> 실제 실행을 위해서는 대상 애플리케이션 및 관련 파일이 필요하며, 해당 파일은 공개되어 있지 않습니다.

---

## 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.10+ |
| UI 자동화 | Pywinauto (UIA backend) |
| 이미지 인식 | PyAutoGUI |
| 테스트 프레임워크 | pytest |
| 프로세스 관리 | psutil |

---

## 주요 기능

- **앱 실행 / 연결** — 실행 중인 프로세스 탐지 및 attach, 미실행 시 EXE 자동 실행
- **메뉴 자동화** — UIA 기반 메뉴 및 서브메뉴 탐색
- **사이드바 탐색** — 사이드바 항목 자동 순회 및 닫기
- **엔터티 생성** — 캔버스 탐지 후 이미지 인식을 통한 엔터티 및 속성 입력
- **관계선 생성** — 다이어그램 관계선 연결 및 속성 입력
- **파일 처리** — 새 프로젝트 생성, 파일 열기, 다른 이름으로 저장, 중복 파일명 처리
- **다이얼로그 제어** — 팝업 및 경고창 자동 감지 및 닫기
- **탭 관리** — 랜덤 이름 기반 새 탭 추가

---

## 프로젝트 구조

```text
gui-automation/
├── conftest.py              # pytest 설정 및 fixture 정의
├── requirements.txt
├── README.md
├── asset/                   # 이미지 인식용 라벨 이미지 (저장소 제외)
│   ├── description_label.png
│   ├── logical_name_label.png
│   └── physical_name_label.png
├── tests/
│   └── test_app.py          # 테스트 케이스
├── utils/
│   ├── __init__.py
│   ├── utils.py             # 메뉴, 사이드바, 파일, 다이얼로그 유틸리티
│   └── entity_actions.py    # 엔터티 및 관계선 액션
└── docs/
    └── demo/                # 데모 영상 (저장소 제외)
```

---

## 테스트 케이스

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
| 9 | test_entity_creation_flow | 엔터티 생성 및 속성 입력 |
| 10 | test_add_entity_and_create_relationship | 관계선 생성 |
| 11 | test_setting_sidebar_navigation | 설정 사이드바 탐색 |
| 12 | test_add_new_tab | 랜덤 이름 기반 새 탭 추가 |
| 13 | test_edit_undo | 실행 취소(Undo) 동작 |

---

## 제한 사항

- 관계선 패널: UIA 미지원으로 좌표 기반 클릭 방식 사용
- 엔터티 패널 필드: 디스플레이 해상도 및 배율에 따라 이미지 인식 결과 차이 발생 가능
- 캔버스 영역: UIA 정보 부족으로 정밀 제어 제한 존재

---

## 설치 및 실행

### 1. 경로 설정 (conftest.py)

환경 변수 방식 권장:

```bash
set APP_EXE_PATH=C:\..\app.exe
set APP_TARGET_FILE=<프로젝트명> - C:\..\sample.project
```

### 2. 설치 및 실행

```bash
# 가상환경 생성
python -m venv venv
venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 테스트 실행
pytest -v -s
```

### 3. 실행 시 주의사항

- 테스트 실행 중 마우스 및 키보드 사용 금지
- Windows 디스플레이 배율 100% 권장
- 원격 데스크톱(RDP) 환경 비권장
- 테스트 중단 시 터미널에서 `Ctrl + C` 입력

---

## 관리자 웹 테스트 (Playwright)

리포지토리 관리자 웹 페이지 테스트를 같은 pytest 스위트에서 실행합니다.

| 화면 | 테스트 수 | 파일 |
|------|------|------|
| 작업자 관리 | 10 | `tests/web/test_worker_crud.py` |
| 그룹 관리 | 7 | `tests/web/test_group_crud.py` |
| 공통코드 관리 | 7 | `tests/web/test_commoncode_crud.py` |

각 테스트는 필요한 데이터를 직접 만들고 끝나면 삭제합니다(테스트 간 상태 공유 없음).

| 항목 | 내용 |
|------|------|
| 위치 | `web/pages/` (페이지 객체), `tests/web/` (테스트) |
| 설정 | `.env.example`을 `.env`로 복사해 `BASE_URL`, `ADMIN_ID`, `ADMIN_PW` 입력 (`.env`는 커밋 제외) |
| 브라우저 설치 | `playwright install chromium` |
| 실패 시 | `debug_screenshots/web/`에 화면 저장 |

```bash
pytest -m web       # 관리자 웹 테스트만
pytest -m desktop   # 데스크톱 앱 테스트만
```

환경변수가 없으면 웹 테스트는 skip 됩니다.

---

## 데모

데모 영상은 `docs/demo/` 경로에 저장되어 있으며 보안 이슈 상 저장소에는 포함되지 않습니다.

---

# desktop-gui-automation

Python-based GUI Automation Test Project for Windows Desktop Application  

> This repository is for portfolio and demonstration purposes only.  
> Actual execution requires the target application and related files, which are not publicly available.

---

## Tech Stack

| Item | Detail |
|------|--------|
| Language | Python 3.10 ~ 3.12 |
| UI Automation | Pywinauto (UIA backend) |
| Image Recognition | PyAutoGUI |
| Test Framework | pytest |
| Process Management | psutil |

---

## Key Features

- **App Launch / Connect** — Running process detection and attach; launches EXE if not running
- **Menu Automation** — UIA-based menu and submenu navigation
- **Sidebar Navigation** — Automated sidebar item traversal and close
- **Entity Creation** — Canvas detection, entity creation, and attribute input via image recognition
- **Relationship Creation** — Diagram relationship linking and property input
- **File Handling** — New project, open, save-as, duplicate filename handling
- **Dialog Control** — Auto-detect and close popups and warning dialogs
- **Tab Management** — Add new tab with random name input

---

## Project Structure

```
desktop-gui-automation/
├── conftest.py              # pytest config, fixture definitions
├── requirements.txt
├── README.md
├── asset/                   # Label images for image recognition (excluded from repo)
│   ├── description_label.png
│   ├── logical_name_label.png
│   └── physical_name_label.png
├── tests/
│   └── test_app.py          # Test cases
├── utils/
│   ├── __init__.py
│   ├── utils.py             # Menu, sidebar, file, dialog utilities
│   └── entity_actions.py    # Entity and relationship actions
└── docs/
    └── demo/                # Demo videos (excluded from repo)
```

---

## Test Cases

| # | Test | Description |
|---|------|-------------|
| 1 | test_open_project | Open recent project |
| 2 | test_view_menu | View menu interactions |
| 3 | test_sidebar_navigation | Sidebar item traversal |
| 4 | test_help_menu | Help menu and popup handling |
| 5 | test_new_project | Create new project |
| 6 | test_open_file | Open file dialog |
| 7 | test_save_as_duplicate | Duplicate filename handling |
| 8 | test_print_dialog | Print dialog open/close |
| 9 | test_entity_creation_flow | Entity creation and attribute input |
| 10 | test_add_entity_and_create_relationship | Relationship creation |
| 11 | test_setting_sidebar_navigation | Settings sidebar traversal |
| 12 | test_add_new_tab | Add new tab with random name |
| 13 | test_edit_undo | Undo action |

---

## Known Limitations

- Relationship panel: No UIA support — coordinate-based click only
- Entity panel fields: Image recognition may vary by display resolution/scale
- Canvas area: Limited UIA information for precise control

---

## Setup & Run

### 1. Path Configuration (conftest.py)

Set via environment variable (recommended):

```bash
set APP_EXE_PATH=C:\..\app.exe
set APP_TARGET_FILE=<ProjectName> - C:\..\sample.project
```

### 2. Install & Run

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -v -s
```

### 3. Notes

- Do not use mouse or keyboard during test execution
- Windows display scale: 100% recommended
- Remote Desktop (RDP) environment: not recommended
- To stop: `Ctrl + C` in terminal

---

## Demo

Demo videos are stored in `docs/demo/` (excluded from repository).
