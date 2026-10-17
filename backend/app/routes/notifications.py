from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Notification
from app.schemas import NotificationOut
from app.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationOut])
def list_notifications(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notifs = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.sent_at.desc())
        .limit(50)
        .all()
    )
    return [NotificationOut.model_validate(n) for n in notifs]


@router.post("/{notif_id}/read")
def mark_read(
    notif_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notif = (
        db.query(Notification)
        .filter(Notification.id == notif_id, Notification.user_id == user.id)
        .first()
    )
    if notif:
        import datetime
        notif.read_at = datetime.datetime.utcnow()
        db.commit()
    return {"ok": True}