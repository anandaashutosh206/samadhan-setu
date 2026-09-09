from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import require_roles

router = APIRouter(tags=["universities", "industries"])


# ---------- Universities ----------
@router.get("/universities", response_model=list[schemas.UniversityOut])
def list_universities(
    district: str | None = None,
    has_incubation: bool | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.University)
    if district:
        query = query.filter(models.University.district == district)
    if has_incubation is not None:
        query = query.filter(models.University.has_incubation == has_incubation)
    if q:
        query = query.filter(models.University.name.ilike(f"%{q}%"))
    return query.order_by(models.University.name).all()


@router.get("/universities/{university_id}", response_model=schemas.UniversityOut)
def get_university(university_id: str, db: Session = Depends(get_db)):
    uni = db.get(models.University, university_id)
    if uni is None:
        raise HTTPException(status_code=404, detail={"detail": "University not found", "code": "NOT_FOUND"})
    return uni


@router.post("/universities", response_model=schemas.UniversityOut, status_code=status.HTTP_201_CREATED)
def create_university(
    payload: schemas.UniversityCreate,
    _admin=Depends(require_roles("GOVT_OFFICIAL", "SUPER_ADMIN")),
    db: Session = Depends(get_db),
):
    existing = db.query(models.University).filter(models.University.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail={"detail": "University code already exists", "code": "CODE_TAKEN"})
    uni = models.University(**payload.model_dump())
    db.add(uni)
    db.commit()
    db.refresh(uni)
    return uni


@router.get("/universities/{university_id}/dashboard")
def university_dashboard(university_id: str, db: Session = Depends(get_db)):
    uni = db.get(models.University, university_id)
    if uni is None:
        raise HTTPException(status_code=404, detail={"detail": "University not found", "code": "NOT_FOUND"})

    proposals = db.query(models.Proposal).filter(models.Proposal.university_id == university_id).all()
    routings = db.query(models.Routing).filter(models.Routing.university_id == university_id).all()
    project_count = (
        db.query(models.Project)
        .join(models.Proposal, models.Project.proposal_id == models.Proposal.id)
        .filter(models.Proposal.university_id == university_id)
        .count()
    )
    return {
        "university": schemas.UniversityOut.model_validate(uni),
        "total_proposals": len(proposals),
        "total_routings_suggested": len(routings),
        "total_active_projects": project_count,
        "proposal_status_breakdown": _count_by(proposals, "status"),
    }


# ---------- Industries ----------
@router.get("/industries", response_model=list[schemas.IndustryOut])
def list_industries(
    sector: str | None = None,
    type: str | None = None,
    district: str | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Industry)
    if sector:
        query = query.filter(models.Industry.sector == sector)
    if type:
        query = query.filter(models.Industry.type == type)
    if district:
        query = query.filter(models.Industry.district == district)
    if q:
        query = query.filter(models.Industry.name.ilike(f"%{q}%"))
    return query.order_by(models.Industry.name).all()


@router.get("/industries/{industry_id}", response_model=schemas.IndustryOut)
def get_industry(industry_id: str, db: Session = Depends(get_db)):
    industry = db.get(models.Industry, industry_id)
    if industry is None:
        raise HTTPException(status_code=404, detail={"detail": "Industry not found", "code": "NOT_FOUND"})
    return industry


@router.post("/industries", response_model=schemas.IndustryOut, status_code=status.HTTP_201_CREATED)
def create_industry(
    payload: schemas.IndustryCreate,
    _admin=Depends(require_roles("GOVT_OFFICIAL", "SUPER_ADMIN", "INDUSTRY_PARTNER")),
    db: Session = Depends(get_db),
):
    industry = models.Industry(**payload.model_dump())
    db.add(industry)
    db.commit()
    db.refresh(industry)
    return industry


@router.get("/industries/{industry_id}/dashboard")
def industry_dashboard(industry_id: str, db: Session = Depends(get_db)):
    industry = db.get(models.Industry, industry_id)
    if industry is None:
        raise HTTPException(status_code=404, detail={"detail": "Industry not found", "code": "NOT_FOUND"})
    collaborations = db.query(models.Collaboration).filter(models.Collaboration.industry_id == industry_id).all()
    return {
        "industry": schemas.IndustryOut.model_validate(industry),
        "total_collaborations": len(collaborations),
        "collaboration_status_breakdown": _count_by(collaborations, "status"),
        "collaboration_type_breakdown": _count_by(collaborations, "type"),
    }


def _count_by(rows: list, attr: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in rows:
        key = getattr(r, attr)
        counts[key] = counts.get(key, 0) + 1
    return counts
