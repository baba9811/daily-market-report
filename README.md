<div align="center">

# 📈 Daily Scheduler

**AI-powered daily news & trading report system with self-improving retrospective**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab.svg)](https://www.python.org)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com)
[![Claude](https://img.shields.io/badge/Powered_by-Claude_Code-cc785c.svg)](https://claude.ai)

매일 아침 AI가 전 세계 뉴스를 분석하고,<br/>
한국 + 미국 시장의 트레이딩 추천 리포트를 생성하여 이메일로 발송합니다.<br/>
과거 추천 성과를 추적하며 **스스로 학습하고 개선**하는 시스템입니다.

[Quick Start](#-quick-start) · [Features](#-features) · [Architecture](#-architecture) · [Dashboard](#-dashboard) · [Contributing](#contributing)

</div>

---

## ✨ Features

- **🤖 AI 리포트 생성** — Claude Code CLI (opus, `--effort max`)가 실시간 뉴스를 검색하고, 인과관계 분석 기반의 트레이딩 리포트를 생성
- **📊 실시간 시세 기반** — yfinance로 주요 지수/환율/원자재를 사전 수집하여 정확한 가격 기반 추천
- **🔗 인과관계 분석** — 뉴스 → 직접 영향 → 파생 효과 → 투자 기회의 Causal Chain 분석
- **📊 듀얼 마켓** — 한국 (KOSPI/KOSDAQ) + 미국 (NYSE/NASDAQ) 주식 추천
- **📧 자동 이메일** — 설정 시간(기본 7:30 KST)에 프로페셔널 HTML 리포트를 이메일로 발송
- **🔄 자기 개선 회고** — 과거 추천 성과를 추적하고, 성공/실패 패턴을 분석하여 다음 추천에 반영
- **📈 웹 대시보드** — 성과 차트, 추천 이력, 주간 회고를 시각적으로 확인
- **⏰ 통합 스케줄러** — `make dev`로 백엔드+프론트엔드+스케줄러 한번에 실행, Ctrl+C로 전체 종료
- **🔒 시크릿 안전 관리** — API 키, 비밀번호는 `.env`에만 저장, 절대 커밋되지 않음

## 🏗 Architecture

```mermaid
graph TB
    subgraph Scheduler
        L[macOS launchd] -->|SCHEDULE_TIME| S[run_daily.sh]
    end

    subgraph Backend["Backend (Python + FastAPI)"]
        S --> O[Orchestrator]
        O --> CK[Check Recommendations<br/>expiry + target/stop]
        O --> UP[Update Prices<br/>yfinance]
        O --> RT[Build Retrospective<br/>성과 추적]
        O --> MD[Fetch Market Data<br/>지수/환율/원자재]
        O --> PB[Prompt Builder<br/>Jinja2]
        O --> C[Claude CLI<br/>opus + effort max<br/>뉴스 수집 + 분석]
        O --> PR[Parser<br/>추천 추출]
        O --> E[Email<br/>Gmail SMTP]
        UP --> DB[(SQLite)]
        RT --> DB
        PR --> DB
    end

    subgraph Frontend["Frontend (Next.js + Tailwind)"]
        D[Dashboard]
        RP[Reports]
        PF[Performance]
        RS[Retrospective]
        ST[Settings]
    end

    DB --> Frontend
    Frontend -->|API| Backend
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Node.js 20+ & [Yarn Berry](https://yarnpkg.com/)
- [Claude Code CLI](https://claude.ai/code)
- Gmail account with [App Password](https://myaccount.google.com/apppasswords)

### 1. Clone & Configure

```bash
git clone https://github.com/your-username/daily-scheduler.git
cd daily-scheduler

# Copy environment template and fill in your credentials
cp .env.example .env
```

Edit `.env` with your settings:

```bash
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_TO=["recipient@email.com"]
SCHEDULE_TIME=07:30               # HH:MM in KST
```

### 2. Setup

```bash
make setup
```

This will:
- Install Python dependencies (`uv sync`)
- Install frontend dependencies (`yarn install`)
- Initialize the database

### 3. Run

```bash
# Start everything (backend + frontend + scheduler)
make dev
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
# Scheduler: loaded into launchd
# Ctrl+C stops all three

# Or run the pipeline once manually
make run
```

### 4. Scheduler Management

```bash
make scheduler-install    # Install & load launchd scheduler
make scheduler-status     # Show scheduler status
make scheduler-start      # Manually trigger now
make scheduler-stop       # Unload scheduler
make scheduler-uninstall  # Unload & remove plist
```

To change the schedule time, edit `SCHEDULE_TIME` in `.env` and run `make scheduler-install`.

## 📊 Dashboard

The web dashboard provides:

| Page | Description |
|------|-------------|
| **Dashboard** | 오늘의 리포트 요약, 활성 추천, 주요 지표 |
| **Reports** | 과거 일일/주간 리포트 열람 |
| **Performance** | 승률, P&L 차트, 섹터별 성과 분석 |
| **Retrospective** | 주간 종합 회고, 전략 조정 제안 |
| **Settings** | 이메일, Claude, 스케줄러 설정 관리 |

## 📁 Project Structure

```
daily-scheduler/
├── backend/                 # Python backend (FastAPI + Hexagonal Architecture)
│   ├── src/daily_scheduler/
│   │   ├── domain/          # Entities, Ports (interfaces)
│   │   ├── application/     # Use cases (pipeline, retrospective, market data)
│   │   ├── infrastructure/  # Adapters (yfinance, Claude CLI, SMTP, SQLAlchemy)
│   │   ├── entrypoints/     # API routes, CLI commands
│   │   ├── templates/       # Jinja2 prompt templates
│   │   └── constants.py     # Tunable constants (timeouts, expiry, etc.)
│   └── pyproject.toml       # uv project config
├── frontend/                # Next.js (App Router + Tailwind + Recharts)
│   └── src/app/             # Pages: dashboard, reports, performance, etc.
├── scheduler/               # macOS launchd configuration
│   ├── install.sh           # Reads SCHEDULE_TIME from .env, auto TZ conversion
│   ├── run_daily.sh         # Pipeline execution wrapper
│   └── com.dailyscheduler.report.plist  # launchd template
├── .env.example             # Environment template (committed)
├── Makefile                 # Convenience commands
└── DISCLAIMER.md            # Financial data disclaimer
```

## 🔄 How the Retrospective Works

The self-improvement loop:

```
1. 매일 아침: 과거 추천 종목의 현재가를 조회
2. 목표가/손절가 도달 여부 자동 체크
3. 30일 승률, 섹터별 성과, 전략별 비교 통계 생성
4. 실시간 시세(지수/환율/원자재) 수집
5. 이 데이터를 Claude 프롬프트에 주입
6. Claude가 뉴스 검색 → 인과관계 분석 → 파생효과 분석 → 추천 생성
7. 새 추천 → 다음날 성과 추적 → 피드백 루프 반복
```

**주간 회고 (매주 월요일)**:
- 전주 전체 추천 성과 종합 분석
- 섹터별/전략별 승률 비교
- 전략 조정 제안 및 교훈 도출

## ⚙️ Configuration

### Environment Variables (`.env`) — secrets & environment-specific

| Variable | Description | Default |
|----------|-------------|---------|
| `SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USER` | Gmail address | — |
| `SMTP_PASSWORD` | Gmail app password | — |
| `EMAIL_TO` | Recipient(s) as JSON array | — |
| `CLAUDE_CLI_PATH` | Path to claude binary | `claude` |
| `CLAUDE_MODEL` | Claude model to use | `opus` |
| `REPORT_LANGUAGE` | Report language (ko, en, ja) | `ko` |
| `TIMEZONE` | IANA timezone | `Asia/Seoul` |
| `SCHEDULE_TIME` | Daily run time in KST (HH:MM) | `07:30` |
| `DATABASE_URL` | SQLite database path | `sqlite:///data/daily_scheduler.db` |

### Application Constants (`constants.py`) — tunable defaults

| Constant | Description | Default |
|----------|-------------|---------|
| `CLAUDE_TIMEOUT_SECONDS` | Claude CLI call timeout | `600` |
| `CLAUDE_RETRY_COUNT` | Number of retry attempts | `2` |
| `DAY_TRADE_EXPIRY_DAYS` | DAY trade auto-expiry | `1` |
| `SWING_TRADE_EXPIRY_DAYS` | SWING trade auto-expiry | `14` |
| `RETROSPECTIVE_LOOKBACK_DAYS` | Retrospective analysis period | `30` |

## 🛡 Disclaimer

> **이 소프트웨어는 교육 및 연구 목적으로만 제공됩니다.**
> AI가 생성한 트레이딩 추천은 투자 조언이 아니며, 금융 손실에 대한 책임은 사용자에게 있습니다.
> 자세한 내용은 [DISCLAIMER.md](DISCLAIMER.md)를 참조하세요.

Financial data is sourced via [yfinance](https://github.com/ranaroussi/yfinance). Users must comply with [Yahoo Finance Terms of Service](https://legal.yahoo.com/us/en/yahoo/terms/product-atos/apitnc/index.html).

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the [Apache License 2.0](LICENSE).

---

<div align="center">
  <sub>Built with Claude Code · FastAPI · Next.js · yfinance</sub>
</div>
