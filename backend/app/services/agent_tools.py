"""Tools the coaching agent can call.

Security rule: tools never take a user id from the model. The server binds
the authenticated user and database session into a ToolContext, so the model
can only ever read data that belongs to the person it is coaching.

Everything a tool returns is DATA, not instructions. User-written text
(notes, cravings) is truncated and the system prompt tells the model to treat
it as untrusted.
"""
import datetime
import json
from dataclasses import dataclass, field
from typing import Any, Callable

from sqlalchemy.orm import Session

from app.models import CycleEntry, DailyCheckIn, User
from app.services.cycle_knowledge import CYCLE_KNOWLEDGE

MAX_CHECKIN_DAYS = 30
MAX_TEXT_CHARS = 200


def _utcnow() -> datetime.datetime:
    # Naive UTC, matching how the rest of the app stores timestamps.
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


@dataclass
class ToolContext:
    db: Session
    user: User
    clock: Callable[[], datetime.datetime] = field(default_factory=lambda: _utcnow)

    def now(self) -> datetime.datetime:
        return self.clock()


# ── helpers ──────────────────────────────────────────────────────────────

def _clamp_int(value: Any, low: int, high: int, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(low, min(high, number))


def _short(text: str | None) -> str:
    text = (text or "").strip()
    return text if len(text) <= MAX_TEXT_CHARS else text[:MAX_TEXT_CHARS] + "..."


def estimate_phase(cycle_day: int, cycle_length: int, period_length: int) -> str:
    """Rough phase for a regular cycle. Ovulation is ~14 days before the next period."""
    ovulation_day = max(period_length + 1, cycle_length - 14)
    if cycle_day <= period_length:
        return "menstrual"
    if cycle_day < ovulation_day - 1:
        return "follicular"
    if cycle_day <= ovulation_day + 1:
        return "ovulatory"
    return "luteal"


def _latest_period_start(entries: list[CycleEntry]) -> datetime.date | None:
    """Walk back through consecutive 'menstrual' log entries to find the first day."""
    menstrual = [e for e in entries if e.phase.value == "menstrual"]
    if not menstrual:
        return None
    start = menstrual[0].date.date()
    for entry in menstrual[1:]:
        day = entry.date.date()
        if (start - day).days <= 2:
            start = min(start, day)
        else:
            break
    return start


# ── tools ────────────────────────────────────────────────────────────────

def get_cycle_status(ctx: ToolContext) -> dict:
    entries = (
        ctx.db.query(CycleEntry)
        .filter(CycleEntry.user_id == ctx.user.id)
        .order_by(CycleEntry.date.desc())
        .limit(60)
        .all()
    )
    if not entries:
        return {"status": "no_cycle_data", "message": "The user has not logged any cycle data yet."}

    cycle_length = ctx.user.cycle_length or 28
    period_length = ctx.user.period_length or 5
    latest = entries[0]
    result: dict[str, Any] = {
        "logged_phase": latest.phase.value,
        "logged_on": latest.date.date().isoformat(),
        "cycle_length": cycle_length,
        "period_length": period_length,
    }

    period_start = _latest_period_start(entries)
    if period_start is not None:
        days_since = (ctx.now().date() - period_start).days
        if days_since >= 0:
            cycle_day = days_since % cycle_length + 1
            result.update(
                estimated_period_start=period_start.isoformat(),
                estimated_cycle_day=cycle_day,
                estimated_phase=estimate_phase(cycle_day, cycle_length, period_length),
                estimate_note=(
                    "Estimated from the last logged period assuming a regular cycle. "
                    "It may differ from how the user actually feels."
                ),
            )
    return result


def get_recent_checkins(ctx: ToolContext, days: int = 7) -> dict:
    days = _clamp_int(days, 1, MAX_CHECKIN_DAYS, default=7)
    cutoff = ctx.now() - datetime.timedelta(days=days)
    rows = (
        ctx.db.query(DailyCheckIn)
        .filter(DailyCheckIn.user_id == ctx.user.id, DailyCheckIn.date >= cutoff)
        .order_by(DailyCheckIn.date.desc())
        .limit(MAX_CHECKIN_DAYS)
        .all()
    )
    if not rows:
        return {"days_requested": days, "count": 0, "message": "No check-ins logged in this period."}

    def average(values: list) -> float | None:
        values = [v for v in values if v is not None]
        return round(sum(values) / len(values), 1) if values else None

    return {
        "days_requested": days,
        "count": len(rows),
        "average_sleep_hours": average([r.sleep_hours for r in rows]),
        "average_energy_1_to_5": average([r.energy_level for r in rows]),
        "average_mood_1_to_5": average([r.mood_level for r in rows]),
        "entries": [
            {
                "date": r.date.date().isoformat(),
                "sleep_hours": r.sleep_hours,
                "energy_level": r.energy_level,
                "mood_level": r.mood_level,
                "cravings": _short(r.cravings),
                "notes": _short(r.notes),
            }
            for r in rows
        ],
    }


def get_phase_guidance(ctx: ToolContext, phase: str) -> dict:
    key = str(phase or "").strip().lower()
    info = CYCLE_KNOWLEDGE.get(key)
    if info is None:
        return {"error": f"Unknown phase '{key}'. Use one of: {', '.join(CYCLE_KNOWLEDGE)}."}
    return {"phase": key, **info}


# ── registry ─────────────────────────────────────────────────────────────

TOOL_SPECS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "get_cycle_status",
            "description": (
                "Get the current user's logged cycle phase and an estimate of their "
                "current cycle day and phase. Call this before giving phase-specific advice."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_checkins",
            "description": (
                "Get the current user's recent daily check-ins (sleep, energy, mood, "
                "cravings, notes) with averages. Call this when sleep, energy, mood or "
                "cravings are relevant to the question."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "How many days back to look (1-30). Default 7.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_phase_guidance",
            "description": "Get the coaching knowledge for one cycle phase: energy, exercise, nutrition, cravings, mood.",
            "parameters": {
                "type": "object",
                "properties": {
                    "phase": {
                        "type": "string",
                        "enum": list(CYCLE_KNOWLEDGE),
                    }
                },
                "required": ["phase"],
            },
        },
    },
]

TOOL_FUNCTIONS: dict[str, Callable[..., dict]] = {
    "get_cycle_status": get_cycle_status,
    "get_recent_checkins": get_recent_checkins,
    "get_phase_guidance": get_phase_guidance,
}

ALLOWED_ARGS: dict[str, set[str]] = {
    spec["function"]["name"]: set(spec["function"]["parameters"]["properties"])
    for spec in TOOL_SPECS
}


def execute_tool(name: str, raw_arguments: str | None, ctx: ToolContext) -> str:
    """Run one tool call from the model. Always returns a JSON string, never raises."""
    fn = TOOL_FUNCTIONS.get(name)
    if fn is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        args = json.loads(raw_arguments) if raw_arguments else {}
        if not isinstance(args, dict):
            raise ValueError("arguments must be an object")
    except ValueError:
        return json.dumps({"error": "Tool arguments were not valid JSON."})

    # Drop anything the tool does not declare (e.g. a model-supplied user_id).
    args = {k: v for k, v in args.items() if k in ALLOWED_ARGS[name]}
    try:
        return json.dumps(fn(ctx, **args), default=str)
    except TypeError:
        return json.dumps({"error": "Tool was called with invalid arguments."})
    except Exception:
        return json.dumps({"error": "Tool failed."})