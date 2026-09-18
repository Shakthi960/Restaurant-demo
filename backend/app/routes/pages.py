"""HTML page routes (Jinja2 templates)."""

from fastapi import APIRouter, Request

from app import db, templating

templates = templating.templates
router = APIRouter()

# UI labels and the order they appear on the /menu page.
MENU_CATEGORIES = [
    ("signature", "Signature Dishes"),
    ("starters", "Starters"),
    ("mains", "Mains & Curries"),
    ("breads", "Breads & Rice"),
    ("desserts", "Desserts"),
]


def _group_dishes(dishes: list) -> list:
    """Return categories in display order, each with its dishes."""
    grouped = []
    for key, label in MENU_CATEGORIES:
        items = [d for d in dishes if d.get("category") == key]
        if items:
            grouped.append({"label": label, "dishes": items})
    return grouped


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {
        "active_page": "home",
        "dishes": db.get_dishes(signature_only=True),
        "locations": db.get_locations(),
        "gallery_images": db.get_gallery_images(),
        "reviews": db.get_reviews(),
    })


@router.get("/about")
def about(request: Request):
    return templates.TemplateResponse(request, "about.html", {
        "active_page": "about",
        "reviews": db.get_reviews(),
        "locations": db.get_locations(),
    })


@router.get("/menu")
def menu(request: Request):
    return templates.TemplateResponse(request, "menu.html", {
        "active_page": "menu",
        "categories": _group_dishes(db.get_dishes()),
    })


@router.get("/locations")
def locations(request: Request):
    return templates.TemplateResponse(request, "locations.html", {
        "active_page": "locations",
        "locations": db.get_locations(),
    })


@router.get("/gallery")
def gallery(request: Request):
    return templates.TemplateResponse(request, "gallery.html", {
        "active_page": "gallery",
        "gallery_images": db.get_gallery_images(),
    })


@router.get("/reservations")
def reservations(request: Request):
    return templates.TemplateResponse(request, "reservation.html", {
        "active_page": "reservations",
        "locations": db.get_locations(),
    })


@router.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse(request, "contact.html", {
        "active_page": "contact",
        "locations": db.get_locations(),
    })