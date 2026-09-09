from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import require_roles

router = APIRouter(prefix="/collaborations", tags=["collaborations"])


@router.post("", response_model=schemas.CollaborationOut, status_code=201)
def create_collaboration(
    payload: schemas.CollaborationCreate,
    current_user: models.User = Depends(require_roles("INDUSTRY_PARTNER")),
    db: Session = Depends(get_db),
):
    proposal = db.get(models.Proposal, payload.proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail={"detail": "Proposal not found", "code": "NOT_FOUND"})
    industry = db.get(models.Industry, payload.industry_id)
    if industry is None:
        raise HTTPException(status_code=404, detail={"detail": "Industry not found", "code": "NOT_FOUND"})

    collab = models.Collaboration(**payload.model_dump())
    db.add(collab)
    db.commit()
    db.refresh(collab)
    return collab


@router.get("", response_model=list[schemas.CollaborationOut])
def list_collaborations(
    proposal_id: str | None = None,
    industry_id: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Collaboration)
    if proposal_id:
        query = query.filter(models.Collaboration.proposal_id == proposal_id)
    if industry_id:
        query = query.filter(models.Collaboration.industry_id == industry_id)
    return query.order_by(models.Collaboration.created_at.desc()).all()


@router.patch("/{collaboration_id}/status", response_model=schemas.CollaborationOut)
def update_collaboration_status(
    collaboration_id: str,
    payload: schemas.CollaborationStatusUpdate,
    current_user: models.User = Depends(require_roles("INDUSTRY_PARTNER", "GOVT_OFFICIAL", "UNIVERSITY_ADMIN")),
    db: Session = Depends(get_db),
):
    collab = db.get(models.Collaboration, collaboration_id)
    if collab is None:
        raise HTTPException(status_code=404, detail={"detail": "Collaboration not found", "code": "NOT_FOUND"})
    collab.status = payload.status
    db.commit()
    db.refresh(collab)
    return collab
