-- Newsletter / email list signups from homepage CTA
create table if not exists public.newsletter_subscribers (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  source text not null default 'homepage_cta',
  created_at timestamptz not null default now(),
  constraint newsletter_subscribers_email_key unique (email)
);

create index if not exists newsletter_subscribers_created_at_idx
  on public.newsletter_subscribers (created_at desc);

alter table public.newsletter_subscribers enable row level security;

-- Public can insert only (anon key from site form). No public read/update/delete.
drop policy if exists "Allow anon insert newsletter_subscribers" on public.newsletter_subscribers;
create policy "Allow anon insert newsletter_subscribers"
  on public.newsletter_subscribers
  for insert
  to anon, authenticated
  with check (
    email is not null
    and char_length(email) <= 320
    and email ~* '^[^@\s]+@[^@\s]+\.[^@\s]+$'
  );

-- Optional: service role / dashboard full access remains via bypassing RLS
