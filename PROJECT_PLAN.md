# Galaxy Restaurants — Project Plan
**Demo Launch (current) → Full Restaurant Platform**

---

## 1. What is our project?

We are building a premium website for **Galaxy Restaurants**, a modern Indian restaurant chain across Coimbatore and Tiruppur (and expanding). The site gives guests a complete digital experience: menu, locations, reservations, gallery, reviews, and direct contact — all in a luxury "Traditional Heritage + Modern Hospitality" design. We started with a polished demo and a clean architecture that can grow into a full restaurant platform with online ordering, loyalty, multi-branch management, and staff/admin workflows.

## 2. What is our aim?

**Main aim**
To make it effortless for guests to discover the menu, choose a branch, reserve a table, and contact the restaurant — and to give the business the tools to manage everything in one place.

**Business / user goals**
- **For guests:** Browse the menu and prices, find nearby branches, reserve a table in seconds, view gallery moments, and leave reviews — all from any phone.
- **For the restaurant:** Receive reservations and enquiries directly, showcase dishes and interiors with premium 3D-style visuals and photography, publish and moderate reviews, and track engagement from one admin dashboard.
- **For you (as a developer/startup):** Build a strong, reusable restaurant web product — attractive to real restaurant clients, with a clean FastAPI + database core that can be extended into a full chain-management platform.

## 3. Core features (current demo)

### 3.1 Home page
- Full-screen hero with the brand story, tagline "Taste Tradition Together", and two CTAs: **Explore Our Menu** and **Find a Location**.
- Signature Dishes section (name + description).
- Locations section (six cities), Heritage/Craft story band, Gallery preview ("Inside Galaxy"), Reservation form, and Contact block.
- Decorative heritage pattern design (floral + jali motifs) in light ivory/gold on alternating sections for a cohesive, premium theme.

### 3.2 Menu
- Full menu grouped by category with dish name, description, region tag, and price.
- Optional category filter via API (`/api/menu?category=...`).
- Data comes from the database, so menu changes need no code changes.

### 3.3 Locations
- Dedicated pages per city with address, hours, phone, and nearby context.
- "View Location" links from home cards.

### 3.4 Gallery
- Responsive asymmetric gallery grid (wide/tall items) with captions and full **lightbox** preview.

### 3.5 Reservations
- Reservation form with fields for name, phone, location/branch, date, time slot, and guest count.
- Client-side validation, then `POST /api/reservations` → stored in database and shown in the admin dashboard as **pending** (confirm/cancel).

### 3.6 Contact & Reviews
- Contact form (`POST /api/contact`) + phone/email/reservation contact blocks.
- Guest reviews with star ratings; new reviews wait for admin approval before appearing publicly.

### 3.7 Admin dashboard (current demo)
- **Tabbed dashboard** (Stats, Reservations, Booking History, Contact Messages, Reviews) with count badges, charts (by status, by week, by city), and one-place action buttons.
- Approve/delete reviews, confirm/cancel reservations, view booking history and contact messages.
- Secure admin login with rate limiting.

### 3.8 WhatsApp-first communication
- Click-to-chat WhatsApp flows for reservations, enquiries, and admin follow-ups using en_US templates for the WhatsApp Cloud API (prepared for launch).

## 4. Extra / added features — what makes it special

### 4.1 Luxury heritage design language
- Indian-inspired design system: warm ivory + heritage red + antique gold + peacock teal, serif typography, ornamental patterns, splash intro, scroll reveals, and smooth eased animations.
- Real 3D-feel visuals (parallax-style imagery, ornament layers) that make the site feel premium — rarely seen on local restaurant sites.

### 4.2 Connected workflows
- Guest books a table → Admin sees pending reservation → Admin confirms/cancels from the dashboard.
- Guest posts a review → Review waits for moderation → Approved reviews appear on the home page.
- Every workflow is connected end-to-end, not separate pages.

### 4.3 Mobile-first, responsive
- Fully responsive from 1440px down to 375px, with a hamburger drawer, touch-friendly buttons, and mobile-optimised forms — built for how Indian diners actually use phones.

### 4.4 Real data, not a mockup
- All menus, locations, gallery images, reviews, reservations, and contacts are stored in **Supabase (PostgreSQL)** and rendered at request time — demonstrably a real product, not a static template.

### 4.5 Smart alerts / management clarity
- Admin sees pending reservations and review moderation counts at a glance; booking history retains past bookings automatically.

## 5. What makes us different from others?

### 5.1 Versus a normal restaurant website
Normal sites: static menu photos, a phone number, and a basic contact form.
Our site: full digital experience — searchable database-driven menu, live reservations, review system, gallery + lightbox, WhatsApp contact, and a real admin dashboard.

### 5.2 Versus ordering-only platforms (Zomato/Swiggy)
Those platforms list many restaurants but give the business almost no ownership of the brand experience or guest data.
Our site: **brand-first** website owned by the restaurant, with our own reservations, reviews, and leads in our own database.

### 5.3 Unique combination
- Luxury heritage Indian design system.
- Database-driven content (menu/locations/gallery/reviews).
- Live reservation + review + contact workflows.
- WhatsApp-first communication.
- FastAPI backend with clean API — ready to become a full chain-management platform.

## 6. Technology overview

**Frontend**
- HTML / CSS / Vanilla JS (design sources in `frontend/`, served at `/static`).
- Responsive, animated, with lightbox and interaction effects.
- Future: can be ported to React/Next.js for faster, richer interactivity.

**Backend**
- Python **FastAPI** (`backend/`) with Jinja2 server-side templates.
- REST API for menu, locations, gallery, reviews, reservations, and contact.

**Database**
- **Supabase (PostgreSQL)** via `backend/app/db.py`.
- Tables: `dishes`, `locations`, `gallery_images`, `reviews`, `reservations`, `contact_messages`.
- Schema + seed applied with `backend/scripts/init_db.py`.

**Admin**
- `/admin` dashboard: login (rate-limited), tabbed management UI, action buttons for reservations/reviews.

**Integrations**
- WhatsApp Cloud API (click-to-chat templates, en_US first).
- Rate limiting (slowapi), CORS config, health check (`/healthz`).
- Future: online payments (table deposits), Google Form / CRM lead sync, email alerts.

## 7. Phased plan — Demo → Full platform

### Phase 1 — Demo (current, done)
- Home, Menu, Locations, Gallery, Reservation, Contact — all live with real database data.
- Reviews with moderation; reservations with confirm/cancel; contact messages.
- Tabbed admin dashboard with stats + charts.
- Responsive mobile experience (fixed hamburger drawer, pattern design system).
- **Demo goal:** A polished, working site worth showing to real restaurant clients.

### Phase 2 — Full platform
- Menu manager, editable locations, and gallery uploads from the admin panel.
- Online table booking with availability and time-slot management.
- Multi-branch / multi-role staff accounts (manager, cashier, kitchen).
- Order-ahead / takeaway and payment integrations.
- Family/group booking, special-occasion packages.
- More SEO pages, local area pages, and blog content.

### Phase 3 — Advanced / smart features
- Loyalty program and digital memberships.
- Customer analytics dashboards.
- Automated WhatsApp/SMS reminders and follow-ups.
- Reviews outreach and reputation management.
- Delivery-partner integration (if ordered).

## 8. Success metrics

- Number of successful reservations created and confirmed.
- Number of review submissions and approved reviews.
- Number of contact messages / WhatsApp clicks.
- Admin actions taken (confirm/cancel, approve/delete) — proves the dashboard is used.
- **Qualitative:** Guests say "the site feels premium and easy to use"; restaurant partners are interested in adopting it for their brand.
- **Technical:** clean, extensible codebase; every page loads fast on mobile; tests pass; deployable via Render/Docker.

---
© 2026 Galaxy Restaurants. Taste Tradition Together.