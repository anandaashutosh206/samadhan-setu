from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("", response_model=schemas.CommentOut, status_code=201)
def create_comment(
    payload: schemas.CommentCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = models.Comment(
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        user_id=current_user.id,
        body=payload.body,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("", response_model=list[schemas.CommentOut])
def list_comments(
    entity_type: str = Query(...),
    entity_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Comment)
        .filter(models.Comment.entity_type == entity_type, models.Comment.entity_id == entity_id)
        .order_by(models.Comment.created_at)
        .all()
    )
