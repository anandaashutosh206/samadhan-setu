import hashlib
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.deps import require_roles

router = APIRouter(prefix="/ip", tags=["ip"])

GENESIS_HASH = "0" * 64


def _compute_hash(payload: dict, prev_hash: str) -> str:
    canonical = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256((canonical + prev_hash).encode("utf-8")).hexdigest()


@router.post("", response_model=schemas.IPRecordOut, status_code=201)
def create_ip_record(
    payload: schemas.IPRecordCreate,
    current_user: models.User = Depends(require_roles("UNIVERSITY_ADMIN", "FACULTY_MENTOR", "GOVT_OFFICIAL")),
    db: Session = Depends(get_db),
):
    project = db.get(models.Project, payload.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail={"detail": "Project not found", "code": "NOT_FOUND"})

    last_record = (
        db.query(models.IPRecord)
        .filter(models.IPRecord.project_id == payload.project_id)
        .order_by(models.IPRecord.filed_on.desc())
        .first()
    )
    # Chain is global (not per-project) for a single tamper-evident ledger.
    last_global = db.query(models.IPRecord).order_by(models.IPRecord.filed_on.desc()).first()
    prev_hash = last_global.ledger_hash if last_global else GENESIS_HASH

    record_payload = {
        "project_id": payload.project_id,
        "type": payload.type,
        "title": payload.title,
        "app_number": payload.app_number,
        "status": payload.status,
    }
    ledger_hash = _compute_hash(record_payload, prev_hash)

    record = models.IPRecord(
        project_id=payload.project_id,
        type=payload.type,
        title=payload.title,
        app_number=payload.app_number,
        status=payload.status,
        prev_hash=prev_hash,
        ledger_hash=ledger_hash,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/verify-chain", response_model=schemas.IPChainVerification)
def verify_chain(db: Session = Depends(get_db)):
    records = db.query(models.IPRecord).order_by(models.IPRecord.filed_on).all()
    prev_hash = GENESIS_HASH
    for record in records:
        payload = {
            "project_id": record.project_id,
            "type": record.type,
            "title": record.title,
            "app_number": record.app_number,
            "status": record.status,
        }
        expected_hash = _compute_hash(payload, prev_hash)
        if record.prev_hash != prev_hash or record.ledger_hash != expected_hash:
            return schemas.IPChainVerification(valid=False, total_records=len(records), broken_at=record.id)
        prev_hash = record.ledger_hash

    return schemas.IPChainVerification(valid=True, total_records=len(records), broken_at=None)


@router.get("/{project_id}", response_model=list[schemas.IPRecordOut])
def list_ip_records(project_id: str, db: Session = Depends(get_db)):
    return (
        db.query(models.IPRecord)
        .filter(models.IPRecord.project_id == project_id)
        .order_by(models.IPRecord.filed_on)
        .all()
    )
