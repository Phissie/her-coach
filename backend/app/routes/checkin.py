import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, DailyCheckIn, Notification
from app.schemas import CheckInCreate, CheckInOut
from app.auth import get_current_user
from app.services.email_service import send_email, build_sleep_alert_email, build_phase_alert_email

router = APIRouter(prefix="/checkin", tags=["checkin"])


@router.post("/", response_model=CheckInOut)
def create_checkin(
    payload: CheckInCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    checkin = DailyCheckIn(
        user_id=user.id,
        date=datetime.datetime.utcnow(),
        sleep_hours=payload.sleep_hours,
        energy_level=payload.energy_level,
        mood_level=payload.mood_level,
        cravings=payload.cravings,
        notes=payload.notes,
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    if user.notifications_enabled and payload.sleep_hours is not None and payload.sleep_hours < 6:
        subject, body, html = build_sleep_alert_email(user.name, payload.sleep_hours)
        import asyncio
        try:
            asyncio.create_task(send_email(user.email, subject, body, html))
        except RuntimeError:
            pass
        notif = Notification(
            user_id=user.id,
            type="email",
            title=subject,
            message=body,
        )
        db.add(notif)
        db.commit()

    return CheckInOut.model_validate(checkin)


@router.get("/recent", response_model=list[CheckInOut])
def recent_checkins(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entries = (
        db.query(DailyCheckIn)
        .filter(DailyCheckIn.user_id == user.id)
        .order_by(DailyCheckIn.date.desc())
        .limit(30)
        .all()
    )
    return [CheckInOut.model_validate(e) for e in entries]


@router.get("/latest")
def latest_checkin(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entry = (
        db.query(DailyCheckIn)
        .filter(DailyCheckIn.user_id == user.id)
        .order_by(DailyCheckIn.date.desc())
        .first()
    )
    if not entry:
        return None
    return CheckInOut.model_validate(entry)