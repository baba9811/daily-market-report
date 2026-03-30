# 보안 정책

## 취약점 신고

**보안 취약점은 공개 이슈로 등록하지 마세요.**

보안 취약점을 발견하셨다면 [GitHub Security Advisories](https://github.com/baba9811/daily-market-report/security/advisories/new)를 통해 신고해 주세요.

### 포함할 내용

- 취약점 설명
- 재현 절차
- 잠재적 영향
- 수정 제안 (있는 경우)

### 응답 일정

- **확인**: 48시간 이내
- **초기 평가**: 1주 이내
- **수정 또는 완화**: 심각도에 따라 가능한 빨리

## 범위

이 프로젝트의 보안 관심 사항:

- **인증 정보 노출** — API 키, SMTP 비밀번호, 토큰이 로그, API 응답, git 히스토리를 통해 유출
- **인젝션 공격** — SQLAlchemy 쿼리를 통한 SQL 인젝션, Claude CLI 호출을 통한 커맨드 인젝션
- **XSS** — AI가 생성한 콘텐츠를 포함하는 HTML 리포트 렌더링
- **경로 탐색** — 리포트 및 데이터베이스의 파일 읽기/쓰기 작업
- **이메일 인젝션** — 설정 API를 통한 헤더 또는 수신자 조작
- **비인가 접근** — 설정 API의 민감한 구성 노출 또는 변경

## 사용자를 위한 보안 모범 사례

- Gmail [앱 비밀번호](https://myaccount.google.com/apppasswords)를 사용하세요 (메인 비밀번호 사용 금지)
- `.env` 파일을 절대 커밋하지 마세요 (이미 `.gitignore`에 포함)
- 프라이빗 네트워크 또는 localhost에서 실행하세요
- 의존성을 최신으로 유지하세요 (`uv lock --upgrade`, `yarn up`)
