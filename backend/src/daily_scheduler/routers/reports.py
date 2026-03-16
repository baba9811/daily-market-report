"""Reports router — list and view generated reports."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from daily_scheduler.database import get_db
from daily_scheduler.models.report import Report
from daily_scheduler.schemas.report import ReportDetailOut, ReportOut

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("", response_model=list[ReportOut])
def list_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    report_type: str = Query("all"),
    db: Session = Depends(get_db),
):
    query = db.query(Report)
    if report_type != "all":
        query = query.filter(Report.report_type == report_type)
    query = query.order_by(Report.created_at.desc())
    reports = query.offset((page - 1) * per_page).limit(per_page).all()
    return reports


@router.get("/latest", response_model=ReportDetailOut)
def get_latest_report(db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .filter(Report.report_type == "daily")
        .order_by(Report.created_at.desc())
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="No reports found")
    return report


@router.get("/{report_id}", response_model=ReportDetailOut)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/{report_id}/html", response_class=HTMLResponse)
def get_report_html(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return HTMLResponse(content=report.html_content)
