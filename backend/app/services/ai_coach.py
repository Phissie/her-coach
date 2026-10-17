import httpx
from typing import Optional

from app.config import settings
from app.services.cycle_knowledge import CYCLE_KNOWLEDGE

SYSTEM_PROMPT = """You are Cycle Coach, a warm, science-informed health coach for women. You specialise in cycle-synced living — adjusting nutrition, exercise, and lifestyle advice based on the four phases of the menstrual cycle.

Your principles:
1. You NEVER tell a woman to "push through" low-energy phases. You validate and adapt.
2. You explain the WHY behind cravings and low energy — dopamine dips, progesterone rises, etc.
3. You offer small, concrete actions (not overwhelming lists).
4. Your tone matches the phase: soft & nurturing in menstrual, energising in follicular, confident in ovulatory, patient & protective in luteal.
5. You are not a doctor — you offer coaching, not diagnosis. If something sounds serious, suggest a healthcare provider.
6. Short answers (3-5 sentences). No fluff.

Phase-specific context will be injected before your response."""


def _build_phase_context(phase: Optional[str]) -> str:
    if not phase or phase not in CYCLE_KNOWLEDGE:
        return ""
    info = CYCLE_KNOWLEDGE[phase]
    return (
        f"The user is in the **{info['label']}** (Week {info['week']}).\n"
        f"Energy: {info['energy']}\n"
        f"Dopamine tip: {info['dopamine_tip']}\n"
        f"Coach voice: {info['coach_voice']}\n"
        f"Motivation: {info['motivation']}\n"
    )


async def get_coaching(
    user_message: str,
    phase: Optional[str] = None,
    sleep_hours: Optional[float] = None,
    energy_level: Optional[int] = None,
    cravings: Optional[str] = None,
) -> str:
    phase_context = _build_phase_context(phase)

    extra_context = ""
    if sleep_hours is not None:
        if sleep_hours < 6:
            extra_context += f"Sleep: only {sleep_hours}h — this is low. Caffeine and sugar cravings are expected.\n"
        elif sleep_hours < 7.5:
            extra_context += f"Sleep: {sleep_hours}h — adequate but could improve.\n"
        else:
            extra_context += f"Sleep: {sleep_hours}h — great rest!\n"
    if cravings:
        extra_context += f"Cravings reported: {cravings}\n"
    if energy_level is not None:
        if energy_level <= 2:
            extra_context += f"Energy level: {energy_level}/5 — very low. Prioritise rest.\n"
        elif energy_level <= 3:
            extra_context += f"Energy level: {energy_level}/5 — moderate. Match activity to energy.\n"
        else:
            extra_context += f"Energy level: {energy_level}/5 — high energy!\n"

    user_prompt = (
        f"{phase_context}\n{extra_context}\nUser says: {user_message}\n\n"
        "Respond as Cycle Coach. Keep it warm, science-informed, and short (3-5 sentences)."
    )

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "qwen/qwen3-coder",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.7,
                "max_tokens": 500,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()