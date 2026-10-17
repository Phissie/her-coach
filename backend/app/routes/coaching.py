from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import datetime

from app.database import get_db
from app.models import User, DailyCheckIn, CoachingMessage
from app.schemas import CoachingRequest, CoachingResponse
from app.auth import get_current_user
from app.services.ai_coach import get_coaching
from app.services.cycle_knowledge import CYCLE_KNOWLEDGE

router = APIRouter(prefix="/coach", tags=["coach"])


@router.post("/chat", response_model=CoachingResponse)
async def chat(
    payload: CoachingRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sleep_hours = None
    energy_level = None
    cravings = None

    if payload.check_in_id:
        checkin = (
            db.query(DailyCheckIn)
            .filter(
                DailyCheckIn.id == payload.check_in_id,
                DailyCheckIn.user_id == user.id,
            )
            .first()
        )
        if checkin:
            sleep_hours = checkin.sleep_hours
            energy_level = checkin.energy_level
            cravings = checkin.cravings

    phase = payload.phase.value if payload.phase else None

    advice = await get_coaching(
        user_message=payload.message or "Give me my daily coaching.",
        phase=phase,
        sleep_hours=sleep_hours,
        energy_level=energy_level,
        cravings=cravings,
    )

    msg = CoachingMessage(
        user_id=user.id,
        phase=phase,
        user_message=payload.message,
        coach_response=advice,
    )
    db.add(msg)
    db.commit()

    return CoachingResponse(advice=advice, phase=phase)


@router.get("/phase-info/{phase}")
def phase_info(phase: str):
    info = CYCLE_KNOWLEDGE.get(phase)
    if not info:
        raise HTTPException(status_code=404, detail="Unknown phase")
    return info