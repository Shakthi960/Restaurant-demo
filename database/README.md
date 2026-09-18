# Galaxy Restaurants — Database (Supabase PostgreSQL)

Supabase PostgreSQL schema for the Galaxy Restaurants site. **Already applied
to the live project.**

## Files

| File | Purpose |
|---|---|
| `supabase/schema.sql` | Tables: `dishes`, `locations`, `gallery_images`, `reviews`, `reservations`, `contact_messages` + RLS policies |
| `supabase/seed.sql` | Seed data: full menu (18 dishes), 6 city locations, gallery, guest reviews |

## Tables

- **dishes** — name, description, price, region, category (`signature` /
  `starters` / `mains` / `breads` / `desserts`), image path (relative to
  `/static/`), `is_signature`
- **locations** — `slug` (e.g. `chennai`), city, address, hours, phone, lat/lng
- **gallery_images** — caption, alt, image, optional `span_class`
  (`gallery-item--wide` / `gallery-item--tall`)
- **reviews** — author, city, rating, review, `is_approved`
- **reservations** — name, phone, `location_id` → locations, date, time,
  guests, status
- **contact_messages** — name, email, phone, message

RLS: public reads allowed on catalogue tables and approved reviews; inserts
allowed on `reservations` and `contact_messages`. The backend uses the
**secret key**, which bypasses RLS.

## Apply (one-off)

```powershell
python backend\scripts\init_db.py
```

This reads `DATABASE_URL` from `backend\.env`, connects (direct `:5432`, then
session-pooler fallback across regions) and runs `schema.sql` followed by
`seed.sql`. Both files are idempotent-friendly (`IF NOT EXISTS` + plain
inserts) and safe to re-run on a fresh database.