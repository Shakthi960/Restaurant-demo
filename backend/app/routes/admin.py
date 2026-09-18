"""Admin dashboard routes — password-protected, no restaurant branding."""

from collections import Counter, defaultdict
from datetime import date, timedelta

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app import auth, db, whatsapp
from app.templating import templates

router = APIRouter(prefix="/admin")


def _csrf_failed() -> RedirectResponse:
    return RedirectResponse(
        _flash_url("/admin", "Session expired or invalid request. Please try again.", "error"),
        status_code=303,
    )


def _booking_stats(reservations: list) -> dict:
    """Aggregate reservations into status, city and per-day counts."""
    status_counts = Counter(r.get("status", "unknown") for r in reservations)
    city_counts = Counter(r.get("city", "—") for r in reservations)

    today = date.today()
    days = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    per_day = defaultdict(int)
    for r in reservations:
        d = str(r.get("reservation_date", ""))[:10]
        if d:
            per_day[d] += 1
    day_series = [{"label": d.strftime("%a %d"), "date": d.isoformat(), "count": per_day.get(d.isoformat(), 0)} for d in days]

    return {
        "status": [{"status": s, "count": status_counts[s]} for s in ("pending", "confirmed", "cancelled")],
        "cities": [{"city": c, "count": n} for c, n in city_counts.most_common()],
        "week": day_series,
        "max_day": max([p["count"] for p in day_series] or [1]),
        "max_city": max([n for _, n in city_counts.most_common()] or [1]),
    }


def _flash_url(base: str, message: str, msg_type: str = "success") -> str:
    return f"{base}?flash={message}&type={msg_type}"


def _render(request: Request, name: str, ctx: dict) -> HTMLResponse:
    ctx.setdefault("admin_logged_in", auth.is_admin(request))
    ctx.setdefault("flash", request.query_params.get("flash", ""))
    ctx.setdefault("flash_type", request.query_params.get("type", "success"))
    ctx.setdefault("admin_enabled", auth.admin_enabled())
    if "csrf_token" not in ctx:
        ctx["csrf_token"] = auth.new_csrf_token()
    resp = templates.TemplateResponse(request, name, ctx)
    auth.set_csrf_cookie(resp, ctx["csrf_token"])
    return resp


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if auth.is_admin(request):
        return RedirectResponse("/admin", status_code=303)
    return _render(request, "admin/login.html", {})


@router.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, password: str = Form(...)):
    if not auth.admin_enabled():
        return _render(request, "admin/login.html", {"error": "Admin access is not configured."})
    if password != auth.ADMIN_PASSWORD:
        return _render(request, "admin/login.html", {"error": "Invalid password. Please try again."})
    resp = RedirectResponse("/admin", status_code=303)
    auth.create_admin_cookie(resp)
    return resp


@router.api_route("/logout", methods=["GET", "POST"])
def logout():
    resp = RedirectResponse("/admin/login", status_code=303)
    auth.clear_admin_cookie(resp)
    return resp


@router.get("", response_class=HTMLResponse)
def dashboard(request: Request):
    if not auth.admin_enabled():
        return _render(request, "admin/login.html", {"error": "Admin access is not configured. Set ADMIN_PASSWORD in backend/.env."})
    if not auth.is_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    reservations = db.get_all_reservations()
    reviews = db.get_all_reviews()
    contacts = db.get_all_contacts()
    db.archive_expired_reservations()
    history = db.get_reservation_history()
    return _render(request, "admin/dashboard.html", {
        "reservations": reservations,
        "reviews": reviews,
        "contacts": contacts,
        "history": history,
        "stats": _booking_stats(reservations),
        "pending_reservations": sum(1 for r in reservations if r.get("status") == "pending"),
        "pending_reviews": sum(1 for r in reviews if not r.get("is_approved")),
        "new_contacts": len(contacts),
    })


@router.post("/reservations/{reservation_id}/confirm")
def admin_confirm_reservation(reservation_id: str, request: Request, csrf_token: str = Form("")):
    if not auth.is_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    if not auth.csrf_token_valid(request, csrf_token):
        return _csrf_failed()
    ok = db.update_reservation_status(reservation_id, "confirmed")
    if ok:
        res = db.get_reservation(reservation_id)
        if res:
            whatsapp.send_confirmed(
                name=res.get("name", ""),
                phone=res.get("phone", ""),
                city=res.get("city", "—"),
                date=str(res.get("reservation_date", ""))[:10],
                time=str(res.get("reservation_time", ""))[:5],
                ref=str(res.get("id", ""))[:8],
            )
    msg = "Reservation confirmed." if ok else "Failed to confirm reservation."
    tp = "success" if ok else "error"
    return RedirectResponse(_flash_url("/admin", msg, tp), status_code=303)


@router.post("/reservations/{reservation_id}/cancel")
def admin_cancel_reservation(reservation_id: str, request: Request, csrf_token: str = Form("")):
    if not auth.is_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    if not auth.csrf_token_valid(request, csrf_token):
        return _csrf_failed()
    ok = db.update_reservation_status(reservation_id, "cancelled")
    msg = "Reservation cancelled." if ok else "Failed to cancel reservation."
    tp = "success" if ok else "error"
    return RedirectResponse(_flash_url("/admin", msg, tp), status_code=303)


@router.post("/reviews/{review_id}/approve")
def admin_approve_review(review_id: str, request: Request, csrf_token: str = Form("")):
    if not auth.is_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    if not auth.csrf_token_valid(request, csrf_token):
        return _csrf_failed()
    ok = db.approve_review(review_id)
    msg = "Review approved and now visible on the site." if ok else "Failed to approve review."
    tp = "success" if ok else "error"
    return RedirectResponse(_flash_url("/admin", msg, tp), status_code=303)


@router.post("/reviews/{review_id}/delete")
def admin_delete_review(review_id: str, request: Request, csrf_token: str = Form("")):
    if not auth.is_admin(request):
        return RedirectResponse("/admin/login", status_code=303)
    if not auth.csrf_token_valid(request, csrf_token):
        return _csrf_failed()
    ok = db.delete_review(review_id)
    msg = "Review deleted." if ok else "Failed to delete review."
    tp = "success" if ok else "error"
    return RedirectResponse(_flash_url("/admin", msg, tp), status_code=303)