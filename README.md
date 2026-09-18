# Galaxy Restaurants — Website

Premium Indian restaurant chain website.
**Tagline:** Taste Tradition Together

---

## Project Structure

```
Restaurant_demo/
├── frontend/              # Design sources (served by FastAPI at /static)
│   ├── index.html         # Redirect stub → live homepage at /
│   ├── css/
│   │   ├── style.css        # Design system & base styles
│   │   ├── animations.css   # Entrance & reveal animations
│   │   ├── pages.css        # Interior page styles (Menu, Galleries, Contact…)
│   │   └── responsive.css   # 1440 → 375 responsive rules
│   ├── js/
│   │   ├── main.js            # Shared helpers + splash + eased scroll
│   │   ├── navigation.js      # Header, drawer, scroll-spy, smooth scroll
│   │   ├── animations.js      # Hero + IntersectionObserver reveals
│   │   ├── reservation.js     # Form validation + POST /api/reservations
│   │   └── contact.js         # Contact form + POST /api/contact
│   └── assets/               # images, patterns, decorative art
├── backend/               # FastAPI app (pages + API)
│   ├── main.py            # App entry: routes, /static mount, /healthz
│   ├── .env               # Supabase credentials (never committed)
│   ├── .env.example
│   ├── requirements.txt
│   ├── app/
│   │   ├── config.py         # Env config
│   │   ├── db.py             # Supabase client + data accessors
│   │   ├── schemas.py        # Pydantic models
│   │   ├── templating.py     # Shared Jinja2Templates
│   │   └── routes/
│   │       ├── pages.py      # /, /menu, /locations, /gallery, /reservations, /contact
│   │       └── api.py        # /api/* endpoints
│   ├── scripts/
│   │   └── init_db.py        # Applies database/supabase/*.sql
│   └── templates/
│       ├── base.html           # Layout: head, splash, header, footer, scripts
│       ├── home.html           # Homepage (dynamic data from Supabase)
│       ├── menu.html           # Full menu grouped by category
│       ├── locations.html      # All city locations
│       ├── gallery.html        # Full gallery grid
│       ├── reservation.html    # Reservation form
│       ├── contact.html        # Contact info + form
│       └── partials/
│           ├── header.html     # Shared navbar
│           └── footer.html     # Shared footer
└── database/
    └── supabase/
        ├── schema.sql          # Tables: dishes, locations, gallery_images,
        │                       #   reviews, reservations, contact_messages
        └── seed.sql            # Seed data (menu, cities, gallery, reviews)
```

## Run the site (FastAPI)

```powershell
# 1. Install backend deps (dev extras cover scripts\init_db.py + tests)
pip install -r backend\requirements.txt -r backend\requirements-dev.txt

# 2. Configure credentials  (copy .env.example → backend\.env)
#    SUPABASE_URL, SUPABASE_SECRET_KEY, SUPABASE_PUBLISHABLE_KEY, DATABASE_URL

# 3. Apply schema + seed once
python backend\scripts\init_db.py

# 4. Start the server
python -m uvicorn main:app --reload       # from backend/
# → http://127.0.0.1:8000
```

Every page shares the same navbar/footer via `templates/partials/header.html`
and `footer.html`, included by every page through `templates/base.html`.
Menu, locations and gallery content come from Supabase at request time.

> `frontend/index.html` is only a redirect stub to the live homepage and is
> kept for legacy bookmarks. The FastAPI routes are the source of truth.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/menu` | Dishes (optional `?category=` filter) |
| GET | `/api/locations` | City locations |
| GET | `/api/gallery` | Gallery images |
| GET | `/api/reviews` | Approved guest reviews |
| POST | `/api/reservations` | Create a table reservation |
| POST | `/api/contact` | Submit a contact message |
| GET | `/healthz` | Health check |

---

© 2026 Galaxy Restaurants. Taste Tradition Together.