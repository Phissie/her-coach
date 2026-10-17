import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, CycleEntry
from app.schemas import CycleEntryCreate, CycleEntryOut
from app.auth import get_current_user

router = APIRouter(prefix="/cycle", tags=["cycle"])


@router.post("/log", response_model=CycleEntryOut)
def log_phase(
    payload: CycleEntryCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = CycleEntry(
        user_id=user.id,
        date=datetime.datetime.combine(payload.date, datetime.time()),
        phase=payload.phase.value,
        notes=payload.notes,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return CycleEntryOut.model_validate(entry)


@router.get("/entries", response_model=list[CycleEntryOut])
def list_entries(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entries = (
        db.query(CycleEntry)
        .filter(CycleEntry.user_id == user.id)
        .order_by(CycleEntry.date.desc())
        .all()
    )
    return [CycleEntryOut.model_validate(e) for e in entries]


@router.get("/current")
def current_phase(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = (
        db.query(CycleEntry)
        .filter(CycleEntry.user_id == user.id)
        .order_by(CycleEntry.date.desc())
        .first()
    )
    if not entry:
        return {"phase": None, "message": "No cycle data yet. Log your first phase!"}
    return {"phase": entry.phase.value, "date": entry.date.isoformat(), "notes": entry.notes}