"""WhatsApp confirmations via Meta Cloud API.

Sends booking-received and booking-confirmed template messages using the
customer's phone number already stored on the reservation. All functions are
safe to call without credentials — they return False and log a warning so the
app keeps working when WhatsApp is not configured.
"""

import json
import logging
import os
import urllib.request
import urllib.error

logger = logging.getLogger("app.whatsapp")

API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v21.0")
BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
TEMPLATE_LANG = os.getenv("WHATSAPP_TEMPLATE_LANG", "en_US")


def whatsapp_enabled() -> bool:
    return bool(
        os.getenv("WHATSAPP_ACCESS_TOKEN")
        and os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    )


def normalize_phone(phone: str, default_cc: str = "91") -> str:
    digits = "".join(c for c in phone if c.isdigit() or c == "+")
    if digits.startswith("+"):
        return digits
    if len(digits) > 10 and digits.startswith(default_cc):
        return "+" + digits
    if len(digits) == 10:
        return "+" + default_cc + digits
    return "+" + digits if digits else ""


def _send(to_phone: str, template_name: str, params: list[str]) -> bool:
    token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    if not token or not phone_id:
        logger.warning("WhatsApp not configured — skipping message to %s", to_phone)
        return False
    to = normalize_phone(to_phone)
    if not to:
        logger.warning("Invalid phone %s — WhatsApp message skipped", to_phone)
        return False
    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": TEMPLATE_LANG},
            "components": [
                {
                    "type": "body",
                    "parameters": [{"type": "text", "text": p} for p in params],
                }
            ],
        },
    }
    url = f"{BASE_URL}/{phone_id}/messages"
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.load(resp)
            ok = bool(result.get("messages"))
            if ok:
                logger.info("WhatsApp sent to %s (id=%s)", to, result["messages"][0]["id"])
            else:
                logger.warning("WhatsApp API returned unexpected response: %s", result)
            return ok
    except urllib.error.HTTPError as exc:
        logger.warning("WhatsApp to %s failed: %s %s", to, exc.code, exc.read().decode())
        return False
    except Exception as exc:
        logger.warning("WhatsApp to %s failed: %s", to, exc)
        return False


def _city(city: str) -> str:
    return city.title() if city else "Galaxy Restaurants"


def send_received(name: str, phone: str, city: str, date: str, time: str, guests: int, ref: str) -> bool:
    return _send(
        phone,
        "booking_received",
        [name, _city(city), date, time, str(guests), ref],
    )


def send_confirmed(name: str, phone: str, city: str, date: str, time: str, ref: str) -> bool:
    return _send(
        phone,
        "booking_confirmed",
        [name, _city(city), date, time, ref],
    )