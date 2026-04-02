"""Dependency injection — factory functions that wire adapters."""

from __future__ import annotations

from sqlalchemy.orm import Session

from daily_scheduler.application.use_cases.build_retrospective import (
    BuildRetrospective,
)
from daily_scheduler.application.use_cases.check_recommendations import (
    CheckRecommendations,
)
from daily_scheduler.application.use_cases.run_daily_pipeline import (
    RunDailyPipeline,
)
from daily_scheduler.application.use_cases.run_news_pipeline import (
    RunNewsBriefingPipeline,
)
from daily_scheduler.application.use_cases.run_weekly_pipeline import (
    RunWeeklyPipeline,
)
from daily_scheduler.application.use_cases.update_prices import (
    UpdatePrices,
)
from daily_scheduler.config import get_settings
from daily_scheduler.infrastructure.adapters.claude.claude_provider import (
    ClaudeNewsProvider,
)
from daily_scheduler.infrastructure.adapters.email.smtp_sender import (
    SmtpEmailSender,
)
from daily_scheduler.infrastructure.adapters.finance.yfinance_provider import (
    YFinanceProvider,
)
from daily_scheduler.infrastructure.adapters.persistence.price_repository import (
    SQLAlchemyPriceRepository,
)
from daily_scheduler.infrastructure.adapters.persistence.recommendation_repository import (
    SQLAlchemyRecommendationRepository,
)
from daily_scheduler.infrastructure.adapters.persistence.report_repository import (
    SQLAlchemyReportRepository,
)
from daily_scheduler.infrastructure.adapters.persistence.retrospective_repository import (
    SQLAlchemyRetrospectiveRepository,
)
from daily_scheduler.infrastructure.adapters.template.renderer import (
    Jinja2ReportRenderer,
)


def get_retro_repo(
    db: Session,
) -> SQLAlchemyRetrospectiveRepository:
    """Create a retrospective repository."""
    return SQLAlchemyRetrospectiveRepository(db)


def get_report_repo(
    db: Session,
) -> SQLAlchemyReportRepository:
    """Create a report repository."""
    return SQLAlchemyReportRepository(db)


def get_rec_repo(
    db: Session,
) -> SQLAlchemyRecommendationRepository:
    """Create a recommendation repository."""
    return SQLAlchemyRecommendationRepository(db)


def get_price_repo(
    db: Session,
) -> SQLAlchemyPriceRepository:
    """Create a price repository."""
    return SQLAlchemyPriceRepository(db)


def get_finance_provider() -> YFinanceProvider:
    """Create a finance provider."""
    return YFinanceProvider()


def get_news_provider() -> ClaudeNewsProvider:
    """Create a news provider."""
    return ClaudeNewsProvider(get_settings())


def get_email_sender() -> SmtpEmailSender:
    """Create an email sender."""
    return SmtpEmailSender(get_settings())


def get_renderer() -> Jinja2ReportRenderer:
    """Create a report renderer."""
    return Jinja2ReportRenderer()


def get_daily_pipeline(db: Session) -> RunDailyPipeline:
    """Wire all adapters into the daily pipeline use case."""
    return RunDailyPipeline(
        report_repo=get_report_repo(db),
        rec_repo=get_rec_repo(db),
        retro_repo=get_retro_repo(db),
        price_repo=get_price_repo(db),
        finance=get_finance_provider(),
        news=get_news_provider(),
        email=get_email_sender(),
        renderer=get_renderer(),
    )


def get_weekly_pipeline(
    db: Session,
) -> RunWeeklyPipeline:
    """Wire all adapters into the weekly pipeline use case."""
    return RunWeeklyPipeline(
        report_repo=get_report_repo(db),
        rec_repo=get_rec_repo(db),
        news=get_news_provider(),
        email=get_email_sender(),
    )


def get_update_prices(db: Session) -> UpdatePrices:
    """Wire adapters into the update prices use case."""
    return UpdatePrices(
        rec_repo=get_rec_repo(db),
        price_repo=get_price_repo(db),
        finance=get_finance_provider(),
    )


def get_check_recommendations(
    db: Session,
) -> CheckRecommendations:
    """Wire adapters into the check recommendations use case."""
    return CheckRecommendations(
        rec_repo=get_rec_repo(db),
        finance=get_finance_provider(),
    )


def get_news_pipeline(db: Session) -> RunNewsBriefingPipeline:
    """Wire adapters into the Korean news briefing pipeline use case."""
    news_provider = get_news_provider()
    return RunNewsBriefingPipeline(
        report_repo=get_report_repo(db),
        generate_briefing=news_provider.generate_news_briefing,
        email=get_email_sender(),
        report_type="news",
        email_subject_label="Korean News Briefing",
        html_filename_suffix="news",
    )


def get_global_news_pipeline(db: Session) -> RunNewsBriefingPipeline:
    """Wire adapters into the global news briefing pipeline use case."""
    news_provider = get_news_provider()
    return RunNewsBriefingPipeline(
        report_repo=get_report_repo(db),
        generate_briefing=news_provider.generate_global_news_briefing,
        email=get_email_sender(),
        report_type="global_news",
        email_subject_label="Global News Briefing",
        html_filename_suffix="global_news",
    )


def get_build_retrospective(
    db: Session,
) -> BuildRetrospective:
    """Wire adapters into the build retrospective use case."""
    return BuildRetrospective(
        rec_repo=get_rec_repo(db),
    )
