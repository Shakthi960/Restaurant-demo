"""Optional email confirmations via SMTP.

Mirrors app/whatsapp.py: all functions are safe to call without credentials —
they return False and log a warning so the app keeps working when SMTP is
not configured.
"""

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger("app.email")


def email_enabled() -> bool:
    return bool(os.getenv("SMTP_HOST") and os.getenv("MAIL_FROM"))


def send_confirmed(name: str, to_email: str, city: str, date: str, time: str, ref: str) -> bool:
    host = os.getenv("SMTP_HOST", "")
    from_addr = os.getenv("MAIL_FROM", "")
    if not host or not from_addr or not to_email:
        logger.warning("SMTP not configured or missing recipient — skipping email")
        return False

    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")

    subject = "Your table is confirmed — Galaxy Restaurants"
    body = (
        f"Dear {name},\n\n"
        f"Good news — your table booking has been confirmed!\n\n"
        f"Restaurant : Galaxy Restaurants — {city}\n"
        f"Date       : {date}\n"
        f"Time       : {time}\n"
        f"Booking no.: {ref}\n\n"
        "We look forward to hosting you. Please contact us at "
        "+91 63831 49466 or care@galaxyrestaurants.in to make any changes.\n\n"
        "Warm regards,\nGalaxy Restaurants\nTaste Tradition Together"
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            if user and password:
                server.login(user, password)
            server.send_message(msg)
        logger.info("Email confirmation sent to %s", to_email)
        return True
    except Exception as exc:
        logger.warning("Email to %s failed: %s", to_email, exc)
        return False