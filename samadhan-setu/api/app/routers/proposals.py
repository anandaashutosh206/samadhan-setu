from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, require_roles

router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.post("", response_model=schemas.ProposalOut, status_code=201)
def create_proposal(
    payload: schemas.ProposalCreate,
    current_user: models.User = Depends(require_roles("UNIVERSITY_ADMIN", "FACULTY_MENTOR")),
    db: Session = Depends(get_db),
):
    challenge = db.get(models.Challenge, payload.challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail={"detail": "Challenge not found", "code": "NOT_FOUND"})
    proposal = models.Proposal(**payload.model_dump())
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return proposal


@router.get("", response_model=list[schemas.ProposalOut])
def list_proposals(
    mine: bool = False,
    challenge_id: str | None = None,
    university_id: str | None = None,
    status_filter: str | None = Query(None, alias="status"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Proposal)
    if challenge_id:
        query = query.filter(models.Proposal.challenge_id == challenge_id)
    if university_id:
        query = query.filter(models.Proposal.university_id == university_id)
    if status_filter:
        query = query.filter(models.Proposal.status == status_filter)
    if mine and current_user.org_name:
        query = query.join(models.University, models.Proposal.university_id == models.University.id).filter(
            models.University.name == current_user.org_name
        )
    return query.order_by(models.Proposal.created_at.desc()).all()


@router.get("/{proposal_id}", response_model=schemas.ProposalOut)
def get_proposal(proposal_id: str, db: Session = Depends(get_db)):
    proposal = db.get(models.Proposal, proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail={"detail": "Proposal not found", "code": "NOT_FOUND"})
    return proposal


@router.patch("/{proposal_id}/status", response_model=schemas.ProposalOut)
def update_proposal_status(
    proposal_id: str,
    payload: schemas.ProposalStatusUpdate,
    current_user: models.User = Depends(require_roles("GOVT_OFFICIAL", "UNIVERSITY_ADMIN")),
    db: Session = Depends(get_db),
):
    proposal = db.get(models.Proposal, proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail={"detail": "Proposal not found", "code": "NOT_FOUND"})
    proposal.status = payload.status

    if payload.status == "APPROVED":
        existing_project = db.query(models.Project).filter(models.Project.proposal_id == proposal.id).first()
        if existing_project is None:
            db.add(models.Project(proposal_id=proposal.id, status="ACTIVE"))
        challenge = db.get(models.Challenge, proposal.challenge_id)
        if challenge:
            challenge.status = "IN_PROGRESS"
        uni = db.get(models.University, proposal.university_id)
        if uni:
            uni.active_project_count += 1

    db.commit()
    db.refresh(proposal)
    return proposal


@router.post("/{proposal_id}/team", response_model=schemas.TeamOut, status_code=201)
def create_team(
    proposal_id: str,
    payload: schemas.TeamCreate,
    current_user: models.User = Depends(require_roles("UNIVERSITY_ADMIN", "FACULTY_MENTOR")),
    db: Session = Depends(get_db),
):
    proposal = db.get(models.Proposal, proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail={"detail": "Proposal not found", "code": "NOT_FOUND"})

    team = models.Team(proposal_id=proposal_id, name=payload.name)
    db.add(team)
    db.flush()

    for m in payload.members:
        db.add(models.TeamMember(team_id=team.id, user_id=m.user_id, role_in_team=m.role_in_team, discipline=m.discipline))

    db.commit()
    db.refresh(team)
    members = db.query(models.TeamMember).filter(models.TeamMember.team_id == team.id).all()
    return schemas.TeamOut(id=team.id, proposal_id=team.proposal_id, name=team.name, members=[schemas.TeamMemberOut.model_validate(m) for m in members])
