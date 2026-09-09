from sqlalchemy.orm import Session

from app import models


def notify(db: Session, user_id: str, title: str, body: str, type_: str = "general", link: str | None = None) -> models.Notification:
    n = models.Notification(user_id=user_id, title=title, body=body, type=type_, link=link)
    db.add(n)
    db.flush()
    return n
