-- Controle Financeiro José Luiz: armazenamento sincronizado por usuário
-- Execute no Supabase SQL Editor do projeto Ecco Salva antes de publicar a versão integrada.
-- Cada usuário autenticado só pode ler e alterar seu próprio estado financeiro.

create table if not exists public.financeiro_jose_state (
  user_id uuid primary key references auth.users(id) on delete cascade,
  state jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.financeiro_jose_state enable row level security;

drop policy if exists "financeiro_jose_select_own" on public.financeiro_jose_state;
create policy "financeiro_jose_select_own"
on public.financeiro_jose_state
for select
to authenticated
using (auth.uid() = user_id);

drop policy if exists "financeiro_jose_insert_own" on public.financeiro_jose_state;
create policy "financeiro_jose_insert_own"
on public.financeiro_jose_state
for insert
to authenticated
with check (auth.uid() = user_id);

drop policy if exists "financeiro_jose_update_own" on public.financeiro_jose_state;
create policy "financeiro_jose_update_own"
on public.financeiro_jose_state
for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

grant select, insert, update on public.financeiro_jose_state to authenticated;
