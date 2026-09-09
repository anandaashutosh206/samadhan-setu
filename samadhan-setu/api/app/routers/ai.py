from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.ai.classifier import get_classifier
from app.ai.dedupe import ExistingChallenge, find_duplicates
from app.ai.keywords import extract_keywords
from app.ai.llm import get_ai_mode
from app.ai.matcher import UniversityCandidate, match_universities
from app.ai.summarizer import summarize
from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/classify", response_model=schemas.AIClassifyResponse)
def classify(payload: schemas.AIClassifyRequest):
    clf = get_classifier()
    text = f"{payload.title} {payload.description}"
    domain, domain_conf, top3 = clf.classify_domain(text)
    severity, sev_conf = clf.classify_severity(text)
    return schemas.AIClassifyResponse(
        domain=domain,
        domain_confidence=domain_conf,
        top_domains=top3,
        severity=severity,
        severity_confidence=sev_conf,
        keywords=extract_keywords(text),
        summary=summarize(payload.description, max_sentences=2),
    )


@router.post("/duplicate-check", response_model=schemas.AIDuplicateCheckResponse)
def duplicate_check(payload: schemas.AIDuplicateCheckRequest, db: Session = Depends(get_db)):
    query = db.query(models.Challenge)
    if payload.exclude_id:
        query = query.filter(models.Challenge.id != payload.exclude_id)
    existing = query.all()
    candidates = [
        ExistingChallenge(id=c.id, title=c.title, description=c.description, district=c.district, lat=c.lat, lng=c.lng)
        for c in existing
    ]
    dups = find_duplicates(
        payload.title,
        payload.description,
        candidates,
        threshold=settings.AI_DEDUPE_THRESHOLD,
        query_district=payload.district,
        query_lat=payload.lat,
        query_lng=payload.lng,
    )
    return schemas.AIDuplicateCheckResponse(
        is_likely_duplicate=len(dups) > 0,
        candidates=[
            schemas.AIDuplicateCandidate(challenge_id=d.challenge_id, title=d.title, similarity=d.similarity, reasons=d.reasons, distance_km=d.distance_km)
            for d in dups
        ],
    )


@router.post("/summarize", response_model=schemas.AISummarizeResponse)
def summarize_text(payload: schemas.AISummarizeRequest):
    return schemas.AISummarizeResponse(summary=summarize(payload.text, payload.max_sentences))


@router.post("/match-universities", response_model=schemas.AIMatchResponse)
def match_universities_endpoint(payload: schemas.AIMatchRequest, db: Session = Depends(get_db)):
    challenge = db.get(models.Challenge, payload.challenge_id)
    if challenge is None:
        return schemas.AIMatchResponse(matches=[])

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
        top_n=payload.top_n,
    )
    return schemas.AIMatchResponse(
        matches=[schemas.MatchUniversityOut(university_id=r.university_id, name=r.name, district=r.district, match_score=r.match_score, match_reasons=r.match_reasons) for r in results]
    )


@router.get("/health", response_model=schemas.AIHealth)
def ai_health():
    clf = get_classifier()
    return schemas.AIHealth(
        status="ok",
        mode=get_ai_mode(),
        classifier_loaded=clf.domain_pipeline is not None,
        training_examples=clf.training_examples,
    )
