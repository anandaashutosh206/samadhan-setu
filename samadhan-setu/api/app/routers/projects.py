from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user, require_roles

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[schemas.ProjectOut])
def list_projects(status_filter: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Project)
    if status_filter:
        query = query.filter(models.Project.status == status_filter)
    return query.all()


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail={"detail": "Project not found", "code": "NOT_FOUND"})
    return project


@router.patch("/{project_id}/progress", response_model=schemas.ProjectOut)
def update_progress(
    project_id: str,
    payload: schemas.ProjectProgressUpdate,
    current_user: models.User = Depends(require_roles("UNIVERSITY_ADMIN", "FACULTY_MENTOR", "GOVT_OFFICIAL")),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail={"detail": "Project not found", "code": "NOT_FOUND"})
    project.progress_percent = payload.progress_percent
    if payload.deployment_status:
        project.deployment_status = payload.deployment_status
    if project.progress_percent >= 100:
        project.status = "COMPLETED"
    db.commit()
    db.refresh(project)
    return project


@router.post("/{project_id}/impact-metrics", response_model=schemas.ProjectOut)
def post_impact_metrics(
    project_id: str,
    payload: schemas.ImpactMetricsUpdate,
    current_user: models.User = Depends(require_roles("UNIVERSITY_ADMIN", "FACULTY_MENTOR", "GOVT_OFFICIAL")),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail={"detail": "Project not found", "code": "NOT_FOUND"})
    merged = dict(project.impact_metrics or {})
    merged.update(payload.metrics)
    project.impact_metrics = merged
    db.commit()
    db.refresh(project)
    return project


@router.post("/{project_id}/milestones", response_model=schemas.MilestoneOut, status_code=201)
def create_milestone(
    project_id: str,
    payload: schemas.MilestoneCreate,
    current_user: models.User = Depends(require_roles("UNIVERSITY_ADMIN", "FACULTY_MENTOR")),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail={"detail": "Project not found", "code": "NOT_FOUND"})
    milestone = models.Milestone(project_id=project_id, **payload.model_dump())
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone


@router.get("/{project_id}/milestones", response_model=list[schemas.MilestoneOut])
def list_milestones(project_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.Milestone)
        .filter(models.Milestone.project_id == project_id)
        .order_by(models.Milestone.order)
        .all()
    )


@router.patch("/milestones/{milestone_id}/status", response_model=schemas.MilestoneOut)
def update_milestone_status(
    milestone_id: str,
    payload: schemas.MilestoneStatusUpdate,
    current_user: models.User = Depends(require_roles("UNIVERSITY_ADMIN", "FACULTY_MENTOR")),
    db: Session = Depends(get_db),
):
    milestone = db.get(models.Milestone, milestone_id)
    if milestone is None:
        raise HTTPException(status_code=404, detail={"detail": "Milestone not found", "code": "NOT_FOUND"})
    milestone.status = payload.status
    if payload.deliverable_url:
        milestone.deliverable_url = payload.deliverable_url
    db.commit()
    db.refresh(milestone)
    return milestone


@router.post("/milestones/{milestone_id}/approve", response_model=schemas.MilestoneOut)
def approve_milestone(
    milestone_id: str,
    current_user: models.User = Depends(require_roles("GOVT_OFFICIAL", "UNIVERSITY_ADMIN")),
    db: Session = Depends(get_db),
):
    milestone = db.get(models.Milestone, milestone_id)
    if milestone is None:
        raise HTTPException(status_code=404, detail={"detail": "Milestone not found", "code": "NOT_FOUND"})
    milestone.status = "APPROVED"
    milestone.approved_by_id = current_user.id
    db.commit()
    db.refresh(milestone)
    return milestone
