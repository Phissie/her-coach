import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, CoachingMessage
from app.schemas import CoachingRequest, CoachingResponse
from app.auth import get_current_user
from app.services.agent_tools import ToolContext
from app.services.ai_coach import run_agent
from app.services.cycle_knowledge import CYCLE_KNOWLEDGE

router = APIRouter(prefix="/coach", tags=["coach"])


@router.post("/chat", response_model=CoachingResponse)
async def chat(
    payload: CoachingRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    phase = payload.phase.value if payload.phase else None
    ctx = ToolContext(db=db, user=user)

    try:
        result = await run_agent(
            user_message=payload.message or "Give me my daily coaching.",
            ctx=ctx,
            phase_hint=phase,
        )
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="The coaching model is unavailable. Please try again.")

    db.add(
        CoachingMessage(
            user_id=user.id,
            check_in_id=payload.check_in_id,
            phase=phase,
            user_message=payload.message,
            coach_response=result.advice,
        )
    )
    db.commit()

    return CoachingResponse(advice=result.advice, phase=phase)


@router.get("/phase-info/{phase}")
def phase_info(phase: str):
    info = CYCLE_KNOWLEDGE.get(phase)
    if not info:
        raise HTTPException(status_code=404, detail="Unknown phase")
    return info