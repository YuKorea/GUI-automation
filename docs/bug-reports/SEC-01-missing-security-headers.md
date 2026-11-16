# SEC-01 관리자 웹 응답에 보안 헤더 2종 누락

| 항목 | 내용 |
|------|------|
| 분류 | 보안 / 설정 |
| 심각도 | Medium |
| 우선순위 | P2 (다음 배포에 포함 권장) |
| 대상 | 리포지토리 관리자 웹 — 모든 HTML 응답 |
| 발견 방법 | 자동화 테스트 `tests/web/test_http.py` (HTTP·보안 테스트 추가 중 발견) |
| 재현율 | 100% (항상) |
| 상태 | 개발팀 전달, 자동화 테스트에 알려진 결함(xfail)으로 등록 |

> 서버 주소·버전 등 환경 정보는 공개 저장소이므로 생략했습니다.

## 요약

관리자 웹의 HTML 응답에 `X-Content-Type-Options`와 클릭재킹 방지 헤더(`X-Frame-Options` 또는 CSP `frame-ancestors`)가 없습니다. 같은 응답에 HSTS는 설정되어 있어, 헤더 정책 일부만 적용된 상태로 보입니다.

## 재현 절차

1. 로그인하지 않은 상태에서 관리자 웹의 `/worker`를 요청합니다.
   ```bash
   curl -sI https://<admin-host>/worker
   ```
2. 응답 헤더를 확인합니다.

## 기대 결과

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY            (또는 Content-Security-Policy: frame-ancestors 'none')
```

## 실제 결과

| 헤더 | 결과 |
|------|------|
| `X-Content-Type-Options` | **없음** |
| `X-Frame-Options` | **없음** |
| `Content-Security-Policy` | **없음** (`frame-ancestors` 없음) |
| `Strict-Transport-Security` | 있음 (정상) |
| http → https 리다이렉트 | 정상 |

## 영향

- **클릭재킹:** 외부 사이트가 관리자 화면을 투명한 iframe으로 겹쳐 띄워, 로그인한 관리자가 작업자 삭제·권한 변경 같은 버튼을 의도치 않게 누르게 만들 수 있습니다. 관리자 화면은 작업자·그룹을 바꾸는 권한을 가지므로 영향이 큽니다.
- **MIME 스니핑:** 브라우저가 응답 형식을 추측해 처리하면, 텍스트로 내려간 내용이 스크립트로 해석될 여지가 생깁니다.

## 수정 제안

웹 서버(리버스 프록시) 또는 애플리케이션 미들웨어에서 모든 응답에 헤더를 추가합니다.

```text
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: frame-ancestors 'none'
```

관리자 화면을 다른 화면에 iframe으로 넣어 쓰는 기능이 있다면 `DENY` 대신 `SAMEORIGIN`으로 정해야 하므로, 적용 전에 확인이 필요합니다.

## 확인 방법

수정 후 `pytest -v tests/web/test_http.py`를 실행하면 두 테스트가 XPASS로 실패 보고됩니다. 이때 `KNOWN_SEC_01` 표시를 제거하면 일반 회귀 테스트로 전환됩니다.
