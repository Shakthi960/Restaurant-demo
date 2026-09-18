# Galaxy Restaurants — Backend (FastAPI)

FastAPI application serving the Galaxy Restaurants website pages (Jinja2) and
the public JSON API (Supabase PostgreSQL).

## Setup

```powershell
pip install -r requirements.txt
copy .env.example .env          # then fill in your Supabase values
python scripts\init_db.py        # apply database/supabase/*.sql once
python -m uvicorn main:app --reload
```

Open `http://127.0.0.1:8000`.

## Configuration (`backend/.env`)

| Key | Purpose |
|---|---|
| `SUPABASE_URL` | Project URL, e.g. `https://xxxx.supabase.co` |
| `SUPABASE_SECRET_KEY` | Server-side key (`sb_secret_…`) — bypasses RLS |
| `SUPABASE_PUBLISHABLE_KEY` | Fallback key (`sb_publishable_…`) |
| `DATABASE_URL` | Direct Postgres URL — used by `scripts/init_db.py` only |
| `ADMIN_PASSWORD` | Enables the `/admin` dashboard |
| `WHATSAPP_ACCESS_TOKEN` | Meta Cloud API token (optional; enables WhatsApp) |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp sender number ID (optional) |

Legacy key names (`SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`) are still
accepted by `app/config.py`.

## Routes

Pages (Jinja2, shared navbar/footer from `templates/partials/`):

```
GET  /              home page (signature dishes, locations, gallery)
GET  /menu          full menu grouped by category
GET  /locations     all city locations
GET  /gallery       full gallery grid
GET  /reservations  reservation form (location options from DB)
GET  /contact       contact info + form
```

API (JSON):

```
GET   /api/menu?category=signature
GET   /api/locations
GET   /api/gallery
GET   /api/reviews
POST  /api/reservations   body: { name, phone, location, date, time, guests }
POST  /api/contact        body: { name, email, phone, message }
GET   /healthz
```

`POST /api/reservations` example:

```json
{
  "name": "Nila Rao",
  "phone": "+91 90000 00000",
  "location": "chennai",
  "date": "2026-09-20",
  "time": "19:30",
  "guests": 4
}
```

## Admin dashboard (`/admin`)

Staff-only area to manage reservations, guest reviews and contact messages.
Protected by a password set in `backend/.env`:

```
ADMIN_PASSWORD=choose-a-strong-password
```

- `GET  /admin/login` — login form (wrong password shows an error).
- After login a signed HttpOnly cookie (`galaxy_admin`) authenticates the
  session; `GET/POST /admin/logout` clears it.
- `GET  /admin` — overview with stats, plus tables with actions:
  - reservations: **Confirm** / **Cancel** (pending only)
  - reviews: **Approve** (publishes to the site) / **Delete**
  - contact messages: read-only list
- When `ADMIN_PASSWORD` is unset the admin area is disabled (login page shows
  a hint). Add `SECRET_KEY` to `.env` to keep sessions alive across restarts;
  otherwise it is randomized at startup (sessions invalidate on restart).

Admin pages use their own minimal layout (`templates/admin/`) and do not
include the restaurant navbar, splash, or public CSS.

## Static assets

`frontend/` (CSS, JS, images) is mounted at `/static`, so templates reference
`/static/css/style.css`, `/static/assets/images/….jpg`, etc.

## Deployment

The repo ships a `Dockerfile` (build context = repo root; copies `backend/`,
`frontend/`, `database/`) and a `render.yaml` blueprint for Render.

**Render (one-click):** import the repo, choose *Blueprint* — `render.yaml`
will create the web service. Then set the three env vars in the dashboard:

- `SUPABASE_URL`
- `SUPABASE_SECRET_KEY`
- `SUPABASE_PUBLISHABLE_KEY`
- `ADMIN_PASSWORD` (enables `/admin`)

Health check `/healthz` is used automatically. Any Docker host works too:

```bash
docker build -t galaxy-restaurants .
docker run -p 10000:10000 \
  -e SUPABASE_URL=... -e SUPABASE_SECRET_KEY=... -e SUPABASE_PUBLISHABLE_KEY=... \
  -e ADMIN_PASSWORD=... \
  galaxy-restaurants
```

`backend/.env` is never copied into the image (`.dockerignore`).

## Notes

- **WhatsApp confirmations (Meta Cloud API):** `app/whatsapp.py` sends template
  messages to customers using the phone number already stored on the reservation —
  no schema change. `POST /api/reservations` sends a `booking_received` template;
  confirming a booking in `/admin` sends `booking_confirmed`. Templates must be
  created in WhatsApp Manager (or via `POST /{WABA_ID}/message_templates`) and
  approved by Meta first. Without `WHATSAPP_*` env vars in `.env`, sends are
  no-ops and bookings work as before. Phone numbers are normalized to E.164
  (e.g. `6383149466` → `+916383149466`).
- **Booking history archive:** reservations whose `reservation_date` has
  passed are moved (delete from `reservations` → insert into
  `reservation_history`) by the database trigger `reservations_after_insert`
  and/or `archive_expired_reservations()`. The admin dashboard calls it on
  load and shows a *Booking History* section. For a daily sweep outside of
  inserts, enable `pg_cron` in Supabase and schedule:
  `select cron.schedule('archive-reservations', '0 2 * * *', 'select public.archive_expired_reservations();');`
- Supabase schema + seed live in `../database/supabase/` and are applied with
  `scripts/init_db.py`.
- `scripts/init_db.py` tries the direct DB first; if it isn't reachable on this
  machine it falls back to the Supabase session-pooler across regions.
- If no `.env` is configured the app still boots; data accessors return empty
  lists so pages render without data.