from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[schemas.NotificationOut])
def list_notifications(
    unread_only: bool = False,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Notification).filter(models.Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(models.Notification.is_read.is_(False))
    return query.order_by(models.Notification.created_at.desc()).all()


@router.patch("/{notification_id}/read", response_model=schemas.NotificationOut)
def mark_read(
    notification_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    n = db.get(models.Notification, notification_id)
    if n is None or n.user_id != current_user.id:
        raise HTTPException(status_code=404, detail={"detail": "Notification not found", "code": "NOT_FOUND"})
    n.is_read = True
    db.commit()
    db.refresh(n)
    return n


@router.patch("/read-all")
def mark_all_read(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id, models.Notification.is_read.is_(False)
    ).update({"is_read": True})
    db.commit()
    return {"detail": "All notifications marked read"}
