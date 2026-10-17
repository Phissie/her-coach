import smtplib
from email.message import EmailMessage
from typing import List

from app.config import settings


async def send_email(to: str, subject: str, body: str, html: str = "") -> bool:
    if not settings.smtp_user or not settings.smtp_password:
        return False

    msg = EmailMessage()
    msg["From"] = f"{settings.email_from_name} <{settings.email_from}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        return True
    except Exception:
        return False


def build_sleep_alert_email(name: str, sleep_hours: float) -> tuple:
    subject = f"🌙 Rough night, {name}?"
    body = (
        f"Hi {name},\n\n"
        f"You logged only {sleep_hours}h of sleep. That's tough.\n\n"
        f"When you're tired, your brain craves quick energy — coffee and sugar. "
        f"Here's what helps right now:\n\n"
        f"• Swap coffee for green tea (l-theanine smooths the crash)\n"
        f"• Craving sugar? Try a date with almond butter — fibre slows the spike\n"
        f"• Move gently — a 5-min walk resets dopamine better than a third coffee\n\n"
        f"Be kind to yourself today. Surviving is winning.\n\n"
        f"— Your Cycle Coach"
    )
    html = (
        f"<h2>🌙 Rough night, {name}?</h2>"
        f"<p>You logged only <strong>{sleep_hours}h</strong> of sleep.</p>"
        f"<h3>What helps right now:</h3>"
        f"<ul>"
        f"<li>Swap coffee for <strong>green tea</strong> — L-theanine smooths the crash</li>"
        f"<li>Craving sugar? Try a <strong>date with almond butter</strong> — fibre slows the spike</li>"
        f"<li>Move gently — a <strong>5-min walk</strong> resets dopamine better than a third coffee</li>"
        f"</ul>"
        f"<p>Be kind to yourself today. 💜</p>"
    )
    return subject, body, html


def build_phase_alert_email(name: str, phase: str) -> tuple:
    phase_labels = {
        "menstrual": "Menstrual Phase — Rest Week",
        "follicular": "Follicular Phase — Build Week",
        "ovulatory": "Ovulatory Phase — Peak Week",
        "luteal": "Luteal Phase — Wind-Down Week",
    }
    tips = {
        "menstrual": "Rest is your workout this week. Gentle walks, iron-rich foods, and grace.",
        "follicular": "Your energy is rising! Great time for strength training and big projects.",
        "ovulatory": "You're at your peak. HIIT, cardio, social plans — you've got this.",
        "luteal": "Energy is dipping. Complex carbs, magnesium, and lower-impact movement. Be patient with yourself.",
    }
    label = phase_labels.get(phase, "Your Cycle")
    tip = tips.get(phase, "")

    subject = f"🔄 {label}"
    body = (
        f"Hi {name},\n\n"
        f"You're entering the **{label}**.\n\n"
        f"{tip}\n\n"
        f"Log a check-in to get personalised coaching.\n\n"
        f"— Your Cycle Coach"
    )
    html = (
        f"<h2>🔄 {label}</h2>"
        f"<p>{tip}</p>"
        f"<p><a href='http://localhost:5173/check-in'>Log a check-in →</a></p>"
    )
    return subject, body, html