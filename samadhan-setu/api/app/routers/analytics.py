from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=schemas.AnalyticsOverview)
def overview(db: Session = Depends(get_db)):
    total_challenges = db.query(models.Challenge).count()
    total_universities = db.query(models.University).count()
    total_industries = db.query(models.Industry).count()
    total_proposals = db.query(models.Proposal).count()
    total_projects = db.query(models.Project).count()
    total_beneficiaries = db.query(func.coalesce(func.sum(models.Challenge.beneficiaries_estimate), 0)).scalar() or 0

    status_rows = db.query(models.Challenge.status, func.count(models.Challenge.id)).group_by(models.Challenge.status).all()
    challenges_by_status = {status: count for status, count in status_rows}

    return schemas.AnalyticsOverview(
        total_challenges=total_challenges,
        total_universities=total_universities,
        total_industries=total_industries,
        total_proposals=total_proposals,
        total_projects=total_projects,
        total_beneficiaries=int(total_beneficiaries),
        challenges_by_status=challenges_by_status,
    )


@router.get("/by-domain", response_model=list[schemas.DomainCount])
def by_domain(db: Session = Depends(get_db)):
    rows = db.query(models.Challenge.domain, func.count(models.Challenge.id)).group_by(models.Challenge.domain).all()
    return [schemas.DomainCount(domain=d, count=c) for d, c in rows]


@router.get("/by-district", response_model=list[schemas.DistrictCount])
def by_district(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Challenge.district, func.count(models.Challenge.id), func.avg(models.Challenge.priority_score))
        .group_by(models.Challenge.district)
        .all()
    )
    return [schemas.DistrictCount(district=d, count=c, avg_priority=round(float(a or 0), 2)) for d, c, a in rows]


FUNNEL_ORDER = [
    "SUBMITTED", "AI_TRIAGED", "UNDER_REVIEW", "VALIDATED", "ROUTED",
    "ASSIGNED", "IN_PROGRESS", "PILOT", "IMPLEMENTED", "CLOSED",
]


@router.get("/funnel", response_model=list[schemas.FunnelStage])
def funnel(db: Session = Depends(get_db)):
    rows = dict(db.query(models.Challenge.status, func.count(models.Challenge.id)).group_by(models.Challenge.status).all())
    # Funnel counts are cumulative: a challenge that reached IN_PROGRESS also
    # passed through every earlier stage, so later stages sum their own status
    # plus every subsequent stage's status.
    result = []
    for i, stage in enumerate(FUNNEL_ORDER):
        cumulative = sum(rows.get(s, 0) for s in FUNNEL_ORDER[i:])
        result.append(schemas.FunnelStage(stage=stage, count=cumulative))
    return result


@router.get("/timeseries", response_model=list[schemas.TimeseriesPoint])
def timeseries(months: int = 6, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    buckets: dict[str, dict[str, int]] = {}
    for i in range(months - 1, -1, -1):
        year = now.year
        month = now.month - i
        while month <= 0:
            month += 12
            year -= 1
        label = f"{year}-{month:02d}"
        buckets[label] = {"submitted": 0, "resolved": 0}

    challenges = db.query(models.Challenge).all()
    for c in challenges:
        created = c.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        label = f"{created.year}-{created.month:02d}"
        if label in buckets:
            buckets[label]["submitted"] += 1
            if c.status in ("IMPLEMENTED", "CLOSED"):
                buckets[label]["resolved"] += 1

    return [schemas.TimeseriesPoint(period=period, submitted=v["submitted"], resolved=v["resolved"]) for period, v in buckets.items()]


@router.get("/leaderboard", response_model=list[schemas.LeaderboardEntry])
def leaderboard(db: Session = Depends(get_db)):
    universities = db.query(models.University).all()
    entries = []
    for uni in universities:
        proposals = db.query(models.Proposal).filter(models.Proposal.university_id == uni.id).all()
        projects_count = (
            db.query(models.Project)
            .join(models.Proposal, models.Project.proposal_id == models.Proposal.id)
            .filter(models.Proposal.university_id == uni.id)
            .count()
        )
        avg_score = sum(p.score for p in proposals) / len(proposals) if proposals else 0.0
        entries.append(
            schemas.LeaderboardEntry(
                university_id=uni.id, name=uni.name, proposals_count=len(proposals),
                projects_count=projects_count, avg_score=round(avg_score, 2),
            )
        )
    entries.sort(key=lambda e: (e.projects_count, e.avg_score), reverse=True)
    return entries


@router.get("/outcomes", response_model=schemas.OutcomesSummary)
def outcomes(db: Session = Depends(get_db)):
    patents_filed = db.query(models.IPRecord).filter(models.IPRecord.type == "PATENT").count()
    pilots_deployed = db.query(models.Project).filter(models.Project.deployment_status.in_(["PILOT", "DEPLOYED"])).count()
    startups_spawned = (
        db.query(models.Collaboration)
        .join(models.Industry, models.Collaboration.industry_id == models.Industry.id)
        .filter(models.Industry.type == "STARTUP", models.Collaboration.status == "COMPLETED")
        .count()
    )
    total_beneficiaries = db.query(func.coalesce(func.sum(models.Challenge.beneficiaries_estimate), 0)).filter(
        models.Challenge.status.in_(["IMPLEMENTED", "CLOSED"])
    ).scalar() or 0

    return schemas.OutcomesSummary(
        patents_filed=patents_filed,
        startups_spawned=startups_spawned,
        pilots_deployed=pilots_deployed,
        total_beneficiaries_impacted=int(total_beneficiaries),
    )
