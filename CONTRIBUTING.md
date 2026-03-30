# 기여 가이드

기여해 주셔서 감사합니다! 이 문서에서는 개발 환경 설정, 코드 컨벤션, PR 프로세스를 안내합니다.

## 개발 환경 설정

### 사전 요구사항

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python 패키지 매니저)
- Node.js 20+
- [Yarn Berry](https://yarnpkg.com/) (v4+)
- [Claude Code CLI](https://claude.ai/code)

### 설치

```bash
git clone https://github.com/baba9811/daily-market-report.git
cd daily-market-report
cp .env.example .env    # 인증 정보 입력
make setup              # 전체 의존성 설치 + DB 초기화
```

### 개발 서버

```bash
# 전체 실행 (백엔드 + 프론트엔드 + 스케줄러)
make dev                # macOS
make dev-linux          # Linux / WSL2

# 개별 실행
make dev-backend        # 백엔드 (자동 리로드)
make dev-frontend       # 프론트엔드 (Next.js dev server)
```

## 아키텍처

백엔드는 **헥사고날 아키텍처** (Ports & Adapters)를 따릅니다. 도메인 로직은 프레임워크 의존성이 없습니다.

```
backend/src/daily_scheduler/
├── domain/              # 엔티티, 포트(인터페이스) — 순수 비즈니스 로직
│   ├── entities/        # 데이터 클래스 (Recommendation, Report, Price)
│   └── ports/           # 추상 인터페이스 (경계)
├── application/         # 유스케이스 — 오케스트레이션 레이어
│   ├── use_cases/       # 파이프라인, 회고, 시장 데이터, 종목 스크리닝
│   └── dto/             # API 레이어용 데이터 전송 객체
├── infrastructure/      # 어댑터 — 외부 서비스 구현체
│   └── adapters/        # yfinance, Claude CLI, SMTP, SQLAlchemy, Jinja2
├── entrypoints/         # 인바운드 어댑터
│   ├── api/routes/      # FastAPI 라우트 핸들러
│   └── cli/             # Typer CLI 커맨드
├── templates/           # Jinja2 프롬프트 템플릿
└── constants.py         # 튜닝 가능한 상수 (타임아웃, 만료, 재시도)
```

```
frontend/src/
├── app/                 # Next.js 15 App Router 페이지
│   ├── page.tsx         # 대시보드
│   ├── reports/         # 리포트 목록 + 상세
│   ├── performance/     # P&L 차트, 섹터 분석
│   ├── retrospective/   # 주간 회고
│   └── settings/        # 설정 관리
├── components/          # 재사용 가능한 React 컴포넌트
└── types/               # OpenAPI에서 자동 생성된 TypeScript 타입
```

**아키텍처 규칙:**
- `domain/`은 `infrastructure/`나 `entrypoints/`를 절대 import하지 않음
- `application/`은 포트(인터페이스)만 사용, 구체 어댑터 직접 참조 금지
- 모든 외부 호출은 포트를 통해야 함

## 개발 방법론

**Schema-Driven Design + Test-Driven Development** (SDD + TDD)를 따릅니다:

1. **스키마 먼저 정의** — 도메인 엔티티 → 포트 → DTO → API 스키마 → 프론트엔드 타입
2. **테스트 먼저 작성** — Red → Green → Refactor 사이클
3. **품질 검사 실행** — 커밋 전 반드시 `make test`

## 테스트 & 코드 품질

```bash
make test       # pytest + pyrefly + pylint + typecheck + oxlint
make lint       # ruff + pyrefly + pylint + ESLint + oxlint
make format     # Python (ruff) + TypeScript 자동 포맷
```

| 도구 | 범위 | 용도 |
|------|------|------|
| **ruff** | Python | 린팅 + 포맷팅 (line-length 100) |
| **pyrefly** | Python | 타입 체킹 |
| **pylint** | Python | 코드 품질 (10.00/10 필수, 무관용) |
| **mypy** | Python | 엄격 타입 체킹 |
| **ESLint** | TypeScript | Next.js 린트 규칙 |
| **oxlint** | TypeScript | 추가 버그 탐지 |
| **TypeScript** | Frontend | strict 모드 |
| **pytest** | Backend | 단위 테스트 (in-memory SQLite) + 통합 테스트 |
| **Playwright** | Frontend | E2E 브라우저 테스트 |

**참고:** pylint은 GPL v2 라이선스이며 개발 전용 도구로만 사용됩니다. 프로덕션 배포물에는 포함되지 않습니다. 모든 프로덕션 의존성은 Apache 2.0 호환입니다.

### 통합 테스트 실행

통합 테스트는 실제 외부 서비스(SMTP, yfinance, Claude CLI)를 검증합니다:

```bash
uv run pytest tests/ --integration
```

### 프론트엔드 타입 재생성

API 스키마가 변경되면 OpenAPI에서 TypeScript 타입을 재생성하세요:

```bash
make generate-types
```

## 가이드라인

1. **모든 로직에 테스트 필수** — 유스케이스, 어댑터, 유틸리티 모두
2. **헥사고날 경계 준수** — 도메인은 인프라를 import하지 않음
3. **코드는 영어로 작성** — 주석, 변수명, UI 문자열 (리포트 언어는 별도)
4. **시크릿 금지** — API 키, 비밀번호, `.env` 파일 절대 커밋 금지
5. **Conventional Commits** — `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`
6. **단순하게 유지** — 과도한 엔지니어링 지양, 단순한 해결책 선호

## PR 프로세스

1. 저장소를 Fork
2. 피처 브랜치 생성 (`git checkout -b feat/amazing-feature`)
3. 변경사항 구현
4. 품질 검사 통과 확인: `make test && make lint`
5. Conventional Commits 형식으로 커밋
6. Fork에 Push 후 Pull Request 생성
7. PR 템플릿 작성

## 라이선스

기여하시면 해당 기여분은 [Apache License 2.0](LICENSE) 하에 라이선스됨에 동의하는 것입니다.
