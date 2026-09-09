from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, require_roles
from app.services.notifications import notify

router = APIRouter(prefix="/routing", tags=["routing"])


@router.post("/assign", response_model=schemas.RoutingOut, status_code=201)
def assign_routing(
    payload: schemas.RoutingAssignRequest,
    current_user: models.User = Depends(require_roles("GOVT_OFFICIAL")),
    db: Session = Depends(get_db),
):
    challenge = db.get(models.Challenge, payload.challenge_id)
    if challenge is None:
        raise HTTPException(status_code=404, detail={"detail": "Challenge not found", "code": "NOT_FOUND"})
    uni = db.get(models.University, payload.university_id)
    if uni is None:
        raise HTTPException(status_code=404, detail={"detail": "University not found", "code": "NOT_FOUND"})

    routing = models.Routing(
        challenge_id=payload.challenge_id,
        university_id=payload.university_id,
        match_score=payload.match_score,
        match_reasons=payload.match_reasons,
        status="OFFERED",
    )
    db.add(routing)
    challenge.status = "ROUTED"

    admins = db.query(models.User).filter(models.User.role == "UNIVERSITY_ADMIN", models.User.org_name == uni.name).all()
    for admin in admins:
        notify(db, admin.id, "New challenge routed to your university", f"'{challenge.title}' has been routed to {uni.name} for review.", type_="routing", link=f"/challenges/{challenge.id}")

    db.commit()
    db.refresh(routing)
    return routing


@router.post("/{routing_id}/accept", response_model=schemas.RoutingOut)
def accept_routing(
    routing_id: str,
    current_user: models.User = Depends(require_roles("UNIVERSITY_ADMIN")),
    db: Session = Depends(get_db),
):
    routing = db.get(models.Routing, routing_id)
    if routing is None:
        raise HTTPException(status_code=404, detail={"detail": "Routing not found", "code": "NOT_FOUND"})
    routing.status = "ACCEPTED"
    challenge = db.get(models.Challenge, routing.challenge_id)
    if challenge:
        challenge.status = "ASSIGNED"
    db.commit()
    db.refresh(routing)
    return routing


@router.post("/{routing_id}/decline", response_model=schemas.RoutingOut)
def decline_routing(
    routing_id: str,
    current_user: models.User = Depends(require_roles("UNIVERSITY_ADMIN")),
    db: Session = Depends(get_db),
):
    routing = db.get(models.Routing, routing_id)
    if routing is None:
        raise HTTPException(status_code=404, detail={"detail": "Routing not found", "code": "NOT_FOUND"})
    routing.status = "DECLINED"
    db.commit()
    db.refresh(routing)
    return routing
