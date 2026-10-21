-- Plataforma Cronograma de Aulas — schema seguro para Supabase
-- Execute este arquivo inteiro no SQL Editor do projeto Supabase usado pela plataforma.
-- Antes de liberar a equipe: crie a conta do administrador em Authentication > Users,
-- substitua o e-mail abaixo pelo e-mail exato e execute o INSERT final deste arquivo.

create extension if not exists btree_gist;

create table if not exists public.cronograma_membros (
  email text primary key,
  nome text not null default '',
  papel text not null default 'equipe' check (papel in ('admin','equipe')),
  ativo boolean not null default true,
  criado_em timestamptz not null default now(),
  constraint cronograma_membros_email_lower check (email = lower(email))
);

create table if not exists public.cronograma_municipios (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  ativo boolean not null default true,
  criado_em timestamptz not null default now()
);
create unique index if not exists cronograma_municipios_nome_lower on public.cronograma_municipios (lower(nome));

create table if not exists public.cronograma_profissionais (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  area text not null default '',
  email text not null default '',
  telefone text not null default '',
  ativo boolean not null default true,
  criado_em timestamptz not null default now()
);
create index if not exists cronograma_profissionais_nome on public.cronograma_profissionais (lower(nome));

create table if not exists public.cronograma_metas (
  id uuid primary key default gen_random_uuid(),
  profissional_id uuid not null references public.cronograma_profissionais(id) on delete restrict,
  municipio_id uuid not null references public.cronograma_municipios(id) on delete restrict,
  total_aulas integer not null check (total_aulas >= 0),
  periodo text not null default 'Projeto',
  observacoes text not null default '',
  criado_em timestamptz not null default now(),
  unique (profissional_id, municipio_id)
);

create table if not exists public.cronograma_conteudos (
  id uuid primary key default gen_random_uuid(),
  profissional_id uuid not null references public.cronograma_profissionais(id) on delete cascade,
  titulo text not null,
  descricao text not null default '',
  ordem integer not null default 1,
  ativo boolean not null default true,
  criado_em timestamptz not null default now()
);
create index if not exists cronograma_conteudos_profissional on public.cronograma_conteudos (profissional_id, ordem);

create table if not exists public.cronograma_aulas (
  id uuid primary key default gen_random_uuid(),
  profissional_id uuid not null references public.cronograma_profissionais(id) on delete restrict,
  municipio_id uuid not null references public.cronograma_municipios(id) on delete restrict,
  data_aula date not null,
  hora_inicio time not null,
  hora_fim time not null,
  titulo text not null default '',
  status text not null default 'agendada' check (status in ('agendada','ministrada','cancelada')),
  observacoes text not null default '',
  criado_por text not null default lower(auth.jwt()->>'email'),
  atualizado_por text not null default lower(auth.jwt()->>'email'),
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now(),
  check (hora_fim > hora_inicio)
);

-- Impede conflitos reais no banco, inclusive se dois usuários tentarem agendar ao mesmo tempo.
do $$
begin
  if not exists (
    select 1 from pg_constraint where conname = 'cronograma_sem_sobreposicao_profissional'
  ) then
    alter table public.cronograma_aulas
      add constraint cronograma_sem_sobreposicao_profissional
      exclude using gist (
        profissional_id with =,
        tsrange(data_aula + hora_inicio, data_aula + hora_fim, '[)') with &&
      ) where (status <> 'cancelada');
  end if;
end $$;

create table if not exists public.cronograma_aula_conteudos (
  id uuid primary key default gen_random_uuid(),
  aula_id uuid not null references public.cronograma_aulas(id) on delete cascade,
  conteudo_id uuid references public.cronograma_conteudos(id) on delete set null,
  titulo_snapshot text not null,
  situacao text not null default 'pendente' check (situacao in ('pendente','parcial','ministrado')),
  observacao text not null default '',
  criado_em timestamptz not null default now(),
  unique (aula_id, conteudo_id)
);
create index if not exists cronograma_aula_conteudos_aula on public.cronograma_aula_conteudos (aula_id);

create or replace function public.cronograma_is_member()
returns boolean language sql stable security definer set search_path = public, pg_temp
as $$
  select exists (
    select 1 from public.cronograma_membros m
    where m.email = lower(coalesce(auth.jwt()->>'email','')) and m.ativo = true
  );
$$;

create or replace function public.cronograma_is_admin()
returns boolean language sql stable security definer set search_path = public, pg_temp
as $$
  select exists (
    select 1 from public.cronograma_membros m
    where m.email = lower(coalesce(auth.jwt()->>'email','')) and m.ativo = true and m.papel = 'admin'
  );
$$;

create or replace function public.cronograma_set_updated()
returns trigger language plpgsql set search_path = public, pg_temp
as $$
begin
  new.atualizado_em = now();
  new.atualizado_por = lower(coalesce(auth.jwt()->>'email',''));
  return new;
end;
$$;
drop trigger if exists cronograma_aulas_updated on public.cronograma_aulas;
create trigger cronograma_aulas_updated before update on public.cronograma_aulas
for each row execute function public.cronograma_set_updated();

alter table public.cronograma_membros enable row level security;
alter table public.cronograma_municipios enable row level security;
alter table public.cronograma_profissionais enable row level security;
alter table public.cronograma_metas enable row level security;
alter table public.cronograma_conteudos enable row level security;
alter table public.cronograma_aulas enable row level security;
alter table public.cronograma_aula_conteudos enable row level security;

-- Membros: somente administradores gerenciam acessos; usuários autorizados veem a lista.
drop policy if exists cronograma_membros_select on public.cronograma_membros;
create policy cronograma_membros_select on public.cronograma_membros for select to authenticated
using (public.cronograma_is_member());
drop policy if exists cronograma_membros_admin_all on public.cronograma_membros;
create policy cronograma_membros_admin_all on public.cronograma_membros for all to authenticated
using (public.cronograma_is_admin()) with check (public.cronograma_is_admin());

-- Cadastros-base: equipe consulta; apenas administrador cria, altera ou exclui.
do $$
declare t text;
begin
  foreach t in array array['cronograma_municipios','cronograma_profissionais','cronograma_metas','cronograma_conteudos'] loop
    execute format('drop policy if exists %I on public.%I', t||'_member_select', t);
    execute format('create policy %I on public.%I for select to authenticated using (public.cronograma_is_member())', t||'_member_select', t);
    execute format('drop policy if exists %I on public.%I', t||'_admin_insert', t);
    execute format('create policy %I on public.%I for insert to authenticated with check (public.cronograma_is_admin())', t||'_admin_insert', t);
    execute format('drop policy if exists %I on public.%I', t||'_admin_update', t);
    execute format('create policy %I on public.%I for update to authenticated using (public.cronograma_is_admin()) with check (public.cronograma_is_admin())', t||'_admin_update', t);
    execute format('drop policy if exists %I on public.%I', t||'_admin_delete', t);
    execute format('create policy %I on public.%I for delete to authenticated using (public.cronograma_is_admin())', t||'_admin_delete', t);
  end loop;
end $$;

-- A equipe pode agendar, atualizar situação e registrar execução. Só admin exclui aulas.
drop policy if exists cronograma_aulas_member_select on public.cronograma_aulas;
create policy cronograma_aulas_member_select on public.cronograma_aulas for select to authenticated
using (public.cronograma_is_member());
drop policy if exists cronograma_aulas_member_insert on public.cronograma_aulas;
create policy cronograma_aulas_member_insert on public.cronograma_aulas for insert to authenticated
with check (public.cronograma_is_member() and lower(criado_por) = lower(coalesce(auth.jwt()->>'email','')));
drop policy if exists cronograma_aulas_member_update on public.cronograma_aulas;
create policy cronograma_aulas_member_update on public.cronograma_aulas for update to authenticated
using (public.cronograma_is_member()) with check (public.cronograma_is_member());
drop policy if exists cronograma_aulas_admin_delete on public.cronograma_aulas;
create policy cronograma_aulas_admin_delete on public.cronograma_aulas for delete to authenticated
using (public.cronograma_is_admin());

drop policy if exists cronograma_aula_conteudos_member_select on public.cronograma_aula_conteudos;
create policy cronograma_aula_conteudos_member_select on public.cronograma_aula_conteudos for select to authenticated
using (public.cronograma_is_member());
drop policy if exists cronograma_aula_conteudos_member_insert on public.cronograma_aula_conteudos;
create policy cronograma_aula_conteudos_member_insert on public.cronograma_aula_conteudos for insert to authenticated
with check (public.cronograma_is_member());
drop policy if exists cronograma_aula_conteudos_member_update on public.cronograma_aula_conteudos;
create policy cronograma_aula_conteudos_member_update on public.cronograma_aula_conteudos for update to authenticated
using (public.cronograma_is_member()) with check (public.cronograma_is_member());
drop policy if exists cronograma_aula_conteudos_admin_delete on public.cronograma_aula_conteudos;
create policy cronograma_aula_conteudos_admin_delete on public.cronograma_aula_conteudos for delete to authenticated
using (public.cronograma_is_admin());

grant usage on schema public to authenticated;
grant select, insert, update, delete on public.cronograma_membros, public.cronograma_municipios, public.cronograma_profissionais, public.cronograma_metas, public.cronograma_conteudos, public.cronograma_aulas, public.cronograma_aula_conteudos to authenticated;
grant execute on function public.cronograma_is_member() to authenticated;
grant execute on function public.cronograma_is_admin() to authenticated;

-- CONFIGURAÇÃO INICIAL OBRIGATÓRIA:
-- 1) Crie primeiro a conta do administrador em Supabase > Authentication > Users.
-- 2) O e-mail do administrador já está configurado como joseluizpurific@gmail.com.
-- 3) Execute este INSERT; depois o administrador poderá cadastrar a equipe dentro da plataforma.
insert into public.cronograma_membros (email, nome, papel, ativo)
values ('joseluizpurific@gmail.com', 'José Luiz', 'admin', true)
on conflict (email) do update set papel = 'admin', ativo = true;
