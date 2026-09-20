-- =============================================================================
--   GALAXY RESTAURANTS — Supabase / PostgreSQL schema
--   Run this in the Supabase SQL Editor (or psql) on a fresh project.
--   Tables: dishes, locations, reviews, gallery_images, reservations,
--           contact_messages
--   Server uses the SERVICE ROLE key (bypasses RLS). Anon key is read-only +
--   insert-only on reservations/contact for optional client-side access.
-- =============================================================================

create extension if not exists "pgcrypto";

-- -----------------------------------------------------------------------------
-- Upgrade / migration for existing projects
--   Safe to run at any time: no-ops when the columns already exist.
-- -----------------------------------------------------------------------------
alter table public.reservations
    add column if not exists email text not null default '';
alter table public.reservation_history
    add column if not exists email text not null default '';

-- -----------------------------------------------------------------------------
-- Menu / dishes
-- -----------------------------------------------------------------------------
create table if not exists public.dishes (
    id            uuid primary key default gen_random_uuid(),
    name          text        not null,
    description   text        not null default '',
    price         numeric(10,2) not null,
    region        text        not null default 'North Indian',
    category      text        not null default 'signature',
    image         text        not null default '',
    is_signature  boolean     not null default false,
    sort_order    integer     not null default 0,
    created_at    timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- Locations
-- -----------------------------------------------------------------------------
create table if not exists public.locations (
    id           uuid primary key default gen_random_uuid(),
    slug         text unique not null,
    city         text not null,
    address      text not null,
    hours        text not null default 'Open Daily · 11:30 AM – 11:00 PM',
    phone        text not null default '',
    lat          numeric(10,6),
    lng          numeric(10,6),
    sort_order   integer not null default 0,
    created_at   timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- Gallery
-- -----------------------------------------------------------------------------
create table if not exists public.gallery_images (
    id           uuid primary key default gen_random_uuid(),
    caption      text not null,
    alt          text not null default '',
    image        text not null,
    span_class   text not null default '',
    sort_order   integer not null default 0,
    created_at   timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- Guest reviews
-- -----------------------------------------------------------------------------
create table if not exists public.reviews (
    id           uuid primary key default gen_random_uuid(),
    author       text not null,
    city         text not null default '',
    rating       integer not null default 5 check (rating between 1 and 5),
    review       text not null,
    is_approved  boolean not null default true,
    created_at   timestamptz not null default now()
);

-- -----------------------------------------------------------------------------
-- Table reservations
-- -----------------------------------------------------------------------------
create table if not exists public.reservations (
    id               uuid primary key default gen_random_uuid(),
    name             text not null,
    phone            text not null,
    email            text not null default '',
    location_id      uuid references public.locations (id) on delete set null,
    reservation_date date not null,
    reservation_time time not null,
    guests           integer not null check (guests between 1 and 40),
    status           text not null default 'pending' check (status in ('pending','confirmed','cancelled')),
    created_at       timestamptz not null default now()
);

create index if not exists reservations_date_idx on public.reservations (reservation_date);

-- -----------------------------------------------------------------------------
-- Reservation history (bookings whose date has passed)
-- -----------------------------------------------------------------------------
create table if not exists public.reservation_history (
    id               uuid primary key,
    name             text not null,
    phone            text not null,
    email            text not null default '',
    location_id      uuid references public.locations (id) on delete set null,
    reservation_date date not null,
    reservation_time time not null,
    guests           integer not null,
    status           text not null,
    archived_on      date not null default current_date,
    created_at       timestamptz not null
);

create index if not exists reservation_history_date_idx on public.reservation_history (archived_on);

create or replace function public.archive_expired_reservations()
returns integer
language plpgsql
security definer
set search_path = public
as $$
declare
    moved_count integer;
begin
    insert into public.reservation_history
        (id, name, phone, email, location_id, reservation_date, reservation_time,
         guests, status, archived_on, created_at)
    select id, name, phone, email, location_id, reservation_date, reservation_time,
           guests, status, current_date, created_at
    from public.reservations
    where reservation_date < current_date
    on conflict (id) do nothing;

    with removed as (
        delete from public.reservations r
        where r.reservation_date < current_date
        returning 1
    )
    select count(*) into moved_count from removed;

    return moved_count;
end;
$$;

-- Re-run archive after every insert so the live table never holds past dates.
create or replace function public.reservations_after_insert()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    perform public.archive_expired_reservations();
    return new;
end;
$$;

drop trigger if exists reservations_after_insert_trigger on public.reservations;
create trigger reservations_after_insert_trigger
after insert on public.reservations
for each row execute function public.reservations_after_insert();

-- -----------------------------------------------------------------------------
-- Contact messages
-- -----------------------------------------------------------------------------
create table if not exists public.contact_messages (
    id         uuid primary key default gen_random_uuid(),
    name       text not null,
    email      text not null,
    phone      text not null default '',
    message    text not null,
    created_at timestamptz not null default now()
);

-- =============================================================================
-- Row Level Security
-- =============================================================================

alter table public.dishes            enable row level security;
alter table public.locations         enable row level security;
alter table public.gallery_images    enable row level security;
alter table public.reviews           enable row level security;
alter table public.reservations      enable row level security;
alter table public.contact_messages  enable row level security;
alter table public.reservation_history enable row level security;

-- Public read-only access to catalogue data
create policy "dishes are public to read"
    on public.dishes for select using (true);

create policy "locations are public to read"
    on public.locations for select using (true);

create policy "gallery is public to read"
    on public.gallery_images for select using (true);

create policy "approved reviews are public to read"
    on public.reviews for select using (is_approved);

-- Anyone may submit a reservation / contact message (insert only)
create policy "anyone can book a reservation"
    on public.reservations for insert with check (true);

create policy "anyone can send a contact message"
    on public.contact_messages for insert with check (true);

-- Guests may submit a review; new reviews are hidden until moderated.
create policy "anyone can submit a review"
    on public.reviews for insert
    with check (is_approved = false and rating between 1 and 5);