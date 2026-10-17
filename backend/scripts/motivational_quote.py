#!/usr/bin/env python3
"""Send a military persona motivational quote via email (SMTP).

Usage:
  cd backend
  uv run scripts/motivational_quote.py --to your@email.com --name "Fis"
  # or: venv/bin/python scripts/motivational_quote.py --to your@email.com
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from app.config import settings
from app.services.email_service import send_email

SYSTEM_PROMPT = """You are a battle-hardened Drill Sergeant delivering motivational firepower. Your mission: inject discipline, grit, and unstoppable momentum into the recruit reading this message.

Your voice:
- Maximum intensity. Every sentence is a command, a challenge, or a call to action.
- Military terminology: "mission", "objective", "deploy", "engage", "battle-tested", "soldier", "stand your ground".
- Brief. 2-4 punchy sentences. No preamble, no softness. Lead with impact.
- End every quote with a sign-off like "HOOAH." or "MOVE OUT." or "GET AFTER IT."
- Vary the topics: discipline, resilience, fear, action, mindset, consistency, leadership, grit.

Rules:
- NEVER start with "Listen up" or "Attention" — jump straight in.
- NEVER mention menstrual cycles, hormones, or anything cycle-coach related. You are NOT Cycle Coach.
- NEVER ask questions. Deliver statements.
- NEVER be gentle. You are a drill sergeant.

Examples of your style:
"Discipline is the difference between what you want and what you settle for. You don't need motivation — you need orders. Now execute. HOOAH."
"Fear is just a checkpoint on the road to greatness. Push through it or stand down. Your call, soldier. OORAH."
"Nobody is coming to save you. You are the rescue mission. Get up, gear up, and dominate. GET AFTER IT."
"""


async def generate_quote() -> str:
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
                    {"role": "user", "content": "Deliver a motivational quote, soldier."},
                ],
                "temperature": 0.9,
                "max_tokens": 200,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


def build_html(quote: str, name: str) -> str:
    return (
        f'<div style="max-width:500px;margin:0 auto;font-family:monospace;'
        f'background:#1a1a1a;color:#f0f0f0;padding:30px;border-radius:8px;'
        f'border-left:6px solid #c41e3a;">'
        f'<h2 style="color:#c41e3a;margin-top:0;">&#9760; DISPATCH FROM COMMAND</h2>'
        f'<p style="font-size:18px;line-height:1.7;">{quote}</p>'
        f'<p style="margin-top:30px;font-size:12px;color:#666;">'
        f'END TRANSMISSION // RECIPIENT: {name.upper()}</p>'
        f'</div>'
    )


async def main_async():
    parser = argparse.ArgumentParser(description="Send a military persona motivational quote via email")
    parser.add_argument("--to", required=True, help="Recipient email address")
    parser.add_argument("--name", default="Soldier", help="Your name (default: Soldier)")
    args = parser.parse_args()

    print("Generating motivational quote...")
    quote = await generate_quote()
    print(f"\n  {quote}\n")

    subject = f"⚡ MISSION BRIEFING // {args.name.upper()}"
    html = build_html(quote, args.name)
    sent = await send_email(to=args.to, subject=subject, body=quote, html=html)

    if sent:
        print(f"Email sent to {args.to}")
    else:
        print("Failed to send email. Check SMTP_USER, SMTP_PASSWORD, and EMAIL_FROM in backend/.env")
        sys.exit(1)


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
