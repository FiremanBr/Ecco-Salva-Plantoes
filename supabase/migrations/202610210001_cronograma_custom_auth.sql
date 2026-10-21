-- Acesso próprio dos coordenadores do Cronograma de Aulas.
-- Executar no SQL Editor do projeto Supabase antes de publicar a nova interface.
-- Não desativa nem altera as políticas RLS atuais; a service role permanece somente na Edge Function.

begin;

create table if not exists public.cronograma_login_usuarios (
  email text primary key check (email = lower(email)),
  nome text not null,
  papel text not null check (papel in ('admin','coordenador')),
  ativo boolean not null default true,
  password_hash text not null,
  password_salt text not null,
  password_iterations integer not null default 310000,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create table if not exists public.cronograma_login_sessoes (
  token_hash text primary key,
  email text not null references public.cronograma_login_usuarios(email) on delete cascade,
  expira_em timestamptz not null,
  criado_em timestamptz not null default now()
);

alter table public.cronograma_login_usuarios enable row level security;
alter table public.cronograma_login_sessoes enable row level security;

revoke all on public.cronograma_login_usuarios from anon, authenticated;
revoke all on public.cronograma_login_sessoes from anon, authenticated;

-- Seed de identidades sem senha: o endpoint de bootstrap cria hashes e senhas
-- via fluxo protegido por CRONOGRAMA_SETUP_SECRET. Não preencher hashes manualmente.
insert into public.cronograma_login_usuarios as current_user(email,nome,papel,ativo,password_hash,password_salt)
values
 ('joseluizpurific@gmail.com','José Luiz','admin',true,'PENDING_SETUP','PENDING_SETUP'),
 ('elisansbrum@gmail.com','Elisandra Dos Santos Brum','coordenador',true,'PENDING_SETUP','PENDING_SETUP'),
 ('caamaier@gmail.com','Claudiomiro Maier Rodrigues','coordenador',true,'PENDING_SETUP','PENDING_SETUP')
on conflict (email) do update set
 nome=excluded.nome,
 papel=excluded.papel,
 ativo=true,
 password_hash=case when current_user.password_hash='PENDING_SETUP' then excluded.password_hash else public.cronograma_login_usuarios.password_hash end,
 password_salt=case when current_user.password_salt='PENDING_SETUP' then excluded.password_salt else public.cronograma_login_usuarios.password_salt end;

-- Mantém os papéis compatíveis com a interface existente (admin/equipe).
insert into public.cronograma_membros(email,nome,papel,ativo)
values
 ('joseluizpurific@gmail.com','José Luiz','admin',true),
 ('elisansbrum@gmail.com','Elisandra Dos Santos Brum','equipe',true),
 ('caamaier@gmail.com','Claudiomiro Maier Rodrigues','equipe',true)
on conflict (email) do update set
 nome=excluded.nome,
 papel=excluded.papel,
 ativo=true;

commit;
