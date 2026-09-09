import math
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas
from app.ai.classifier import get_classifier
from app.ai.dedupe import ExistingChallenge, find_duplicates
from app.ai.keywords import extract_keywords
from app.ai.matcher import UniversityCandidate, match_universities
from app.ai.prioritiser import compute_priority
from app.ai.summarizer import summarize
from app.config import settings
from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import CHALLENGE_STATUSES

router = APIRouter(prefix="/challenges", tags=["challenges"])

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
ALLOWED_MIME_PREFIXES = ("image/", "application/pdf")


def _save_upload(file: UploadFile, challenge_id: str) -> models.Attachment:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if file.content_type is None or not any(file.content_type.startswith(p) for p in ALLOWED_MIME_PREFIXES):
        raise HTTPException(status_code=422, detail={"detail": "Unsupported file type", "code": "BAD_MIME"})

    contents = file.file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_UPLOAD_MB:
        raise HTTPException(status_code=422, detail={"detail": "File too large", "code": "FILE_TOO_LARGE"})

    ext = Path(file.filename or "upload").suffix
    stored_name = f"{uuid.uuid4()}{ext}"
    (UPLOAD_DIR / stored_name).write_bytes(contents)

    return models.Attachment(
        challenge_id=challenge_id,
        file_name=file.filename or stored_name,
        stored_name=stored_name,
        mime_type=file.content_type,
        size_bytes=len(contents),
        url=f"/uploads/{stored_name}",
    )


def _run_ai_triage(db: Session, challenge: models.Challenge) -> None:
    """Runs classification, keyword extraction, summarization, dedupe check,
    and priority scoring on a freshly created challenge, then persists."""
    clf = get_classifier()
    text = f"{challenge.title} {challenge.description}"

    domain, domain_conf, _top3 = clf.classify_domain(text)
    severity, _sev_conf = clf.classify_severity(text)

    challenge.domain = domain
    challenge.severity = severity
    challenge.ai_confidence = domain_conf
    challenge.ai_keywords = extract_keywords(text)
    challenge.ai_summary = summarize(challenge.description, max_sentences=2)

    existing = (
        db.query(models.Challenge)
        .filter(models.Challenge.id != challenge.id, models.Challenge.status != "REJECTED")
        .all()
    )
    candidates = [
        ExistingChallenge(id=c.id, title=c.title, description=c.description, district=c.district, lat=c.lat, lng=c.lng)
        for c in existing
    ]
    dups = find_duplicates(
        challenge.title,
        challenge.description,
        candidates,
        threshold=settings.AI_DEDUPE_THRESHOLD,
        query_district=challenge.district,
        query_lat=challenge.lat,
        query_lng=challenge.lng,
    )
    if dups:
        challenge.duplicate_of_id = dups[0].challenge_id

    cluster_size = len(dups)
    priority = compute_priority(
        severity=challenge.severity,
        domain=challenge.domain,
        district=challenge.district,
        beneficiaries_estimate=challenge.beneficiaries_estimate,
        upvote_count=challenge.upvote_count,
        duplicate_cluster_size=cluster_size,
        created_at=challenge.created_at,
    )
    challenge.priority_score = priority.score
    challenge.status = "AI_TRIAGED"


@router.post("", response_model=schemas.ChallengeOut, status_code=status.HTTP_201_CREATED)
def create_challenge(
    title: str = Form(..., min_length=5, max_length=200),
    description: str = Form(..., min_length=20),
    district: str = Form(...),
    block: str | None = Form(None),
    village: str | None = Form(None),
    lat: float | None = Form(None),
    lng: float | None = Form(None),
    beneficiaries_estimate: int = Form(0),
    files: list[UploadFile] = File(default=[]),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    challenge = models.Challenge(
        title=title,
        description=description,
        domain="public_administration",  # placeholder until AI triage runs below
        district=district,
        block=block,
        village=village,
        lat=lat,
        lng=lng,
        beneficiaries_estimate=beneficiaries_estimate,
        submitted_by_id=current_user.id,
    )
    db.add(challenge)
    db.flush()

    for f in files:
        if f.filename:
            db.add(_save_upload(f, challenge.id))

    _run_ai_triage(db, challenge)

    db.commit()
    db.refresh(challenge)
    return challenge


@router.get("", response_model=schemas.ChallengeListOut)
def list_challenges(
    q: str | None = None,
    domain: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    district: str | None = None,
    severity: str | None = None,
    sort: str = Query("recent", pattern="^(recent|priority|upvotes)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(models.Challenge)

    if q:
        like = f"%{q}%"
        query = query.filter(or_(models.Challenge.title.ilike(like), models.Challenge.description.ilike(like)))
    if domain:
        query = query.filter(models.Challenge.domain == domain)
    if status_filter:
        query = query.filter(models.Challenge.status == status_filter)
    if district:
        query = query.filter(models.Challenge.district == district)
    if severity:
        query = query.filter(models.Challenge.severity == severity)

    if sort == "priority":
        query = query.order_by(models.Challenge.priority_score.desc())
    elif sort == "upvotes":
        query = query.order_by(models.Challenge.upvote_count.desc())
    else:
        query = query.order_by(models.Challenge.created_at.desc())

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    pages = math.ceil(total / page_size) if total else 0

    return schemas.ChallengeListOut(items=items, total=total, page=page, page_size=page_size, pages=pages)


@router.get("/map", response_model=list[schemas.ChallengeMapPoint])
def challenges_map(db: Session = Depends(get_db)):
    rows = (
        db.query(models.Challenge)
        .filter(models.Challenge.lat.isnot(None), models.Challenge.lng.isnot(None))
        .all()
    )
    return [
        schemas.ChallengeMapPoint(
            id=c.id, title=c.title, domain=c.domain, severity=c.severity, status=c.status, lat=c.lat, lng=c.lng
        )
        for c in rows
    ]


def _get_or_404(db: Session, challenge_id: str) -> models.Challenge:
    challenge = db.get(models.Challenge, challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail={"detail": "Challenge not found", "code": "NOT_FOUND"})
    return challenge


@router.get("/{challenge_id}", response_model=schemas.ChallengeOut)
def get_challenge(challenge_id: str, db: Session = Depends(get_db)):
    return _get_or_404(db, challenge_id)


@router.patch("/{challenge_id}/status", response_model=schemas.ChallengeOut)
def update_status(
    challenge_id: str,
    payload: schemas.ChallengeStatusUpdate,
    current_user: models.User = Depends(require_roles("GOVT_OFFICIAL", "UNIVERSITY_ADMIN")),
    db: Session = Depends(get_db),
):
    challenge = _get_or_404(db, challenge_id)
    if payload.status not in CHALLENGE_STATUSES:
        raise HTTPException(status_code=422, detail={"detail": "Invalid status", "code": "BAD_STATUS"})
    challenge.status = payload.status
    db.add(models.AuditLog(actor_id=current_user.id, action="status_change", entity_type="challenge", entity_id=challenge.id, meta={"new_status": payload.status, "reason": payload.reason}))
    db.commit()
    db.refresh(challenge)
    return challenge


@router.post("/{challenge_id}/validate", response_model=schemas.ChallengeOut)
def validate_challenge(
    challenge_id: str,
    current_user: models.User = Depends(require_roles("GOVT_OFFICIAL")),
    db: Session = Depends(get_db),
):
    challenge = _get_or_404(db, challenge_id)
    challenge.status = "VALIDATED"
    db.add(models.AuditLog(actor_id=current_user.id, action="validate", entity_type="challenge", entity_id=challenge.id, meta={}))
    db.commit()
    db.refresh(challenge)
    return challenge


@router.post("/{challenge_id}/upvote", response_model=schemas.ChallengeOut)
def toggle_upvote(
    challenge_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    challenge = _get_or_404(db, challenge_id)
    existing = (
        db.query(models.Upvote)
        .filter(models.Upvote.challenge_id == challenge_id, models.Upvote.user_id == current_user.id)
        .first()
    )
    if existing:
        db.delete(existing)
        challenge.upvote_count = max(0, challenge.upvote_count - 1)
    else:
        db.add(models.Upvote(challenge_id=challenge_id, user_id=current_user.id))
        challenge.upvote_count += 1

    db.commit()
    db.refresh(challenge)
    return challenge


@router.get("/{challenge_id}/similar", response_model=list[schemas.AIDuplicateCandidate])
def similar_challenges(challenge_id: str, db: Session = Depends(get_db)):
    challenge = _get_or_404(db, challenge_id)
    existing = db.query(models.Challenge).filter(models.Challenge.id != challenge_id).all()
    candidates = [
        ExistingChallenge(id=c.id, title=c.title, description=c.description, district=c.district, lat=c.lat, lng=c.lng)
        for c in existing
    ]
    dups = find_duplicates(
        challenge.title,
        challenge.description,
        candidates,
        threshold=0.35,
        query_district=challenge.district,
        query_lat=challenge.lat,
        query_lng=challenge.lng,
    )
    return [schemas.AIDuplicateCandidate(challenge_id=d.challenge_id, title=d.title, similarity=d.similarity, reasons=d.reasons, distance_km=d.distance_km) for d in dups]


@router.get("/{challenge_id}/routing-suggestions", response_model=schemas.AIMatchResponse)
def routing_suggestions(challenge_id: str, top_n: int = 5, db: Session = Depends(get_db)):
    challenge = _get_or_404(db, challenge_id)
    universities = db.query(models.University).all()
    candidates = [
        UniversityCandidate(
            id=u.id, name=u.name, district=u.district, disciplines=u.disciplines, research_areas=u.research_areas,
            has_incubation=u.has_incubation, naac_grade=u.naac_grade, lat=u.lat, lng=u.lng,
            capacity_score=u.capacity_score, active_project_count=u.active_project_count,
        )
        for u in universities
    ]
    results = match_universities(
        challenge_text=f"{challenge.title} {challenge.description}",
        domain=challenge.domain,
        district=challenge.district,
        lat=challenge.lat,
        lng=challenge.lng,
        universities=candidates,
        top_n=top_n,
    )
    return schemas.AIMatchResponse(
        matches=[schemas.MatchUniversityOut(university_id=r.university_id, name=r.name, district=r.district, match_score=r.match_score, match_reasons=r.match_reasons) for r in results]
    )
