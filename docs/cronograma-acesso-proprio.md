# Acesso próprio — Cronograma de Aulas

## Situação

O arquivo `cronograma-aulas.html` ainda usa Supabase Auth e faz consultas diretamente ao banco. Não é seguro trocar apenas o formulário de login: a autorização precisa ser validada no servidor para cada operação de dados.

## Coordenadores solicitados

- José Luiz — `joseluizpurific@gmail.com` — administrador
- Elisandra Dos Santos Brum — `elisansbrum@gmail.com` — coordenadora
- Claudiomiro Maier Rodrigues — `caamaier@gmail.com` — coordenador

Os instrutores cadastrados na aba Profissionais não devem receber credenciais por padrão.

## Plano técnico obrigatório

1. Criar autenticação própria no servidor, com hashes de senha e sessões revogáveis; nunca guardar senhas em texto puro.
2. Criar um gateway de dados server-side com lista explícita de tabelas/operações autorizadas e validação de papel. A chave service-role fica exclusivamente nos segredos da Edge Function.
3. Migrar todas as operações `sb.from(...)` e `sb.rpc(...)` do frontend para o gateway.
4. Só depois de validar login, permissões, sessão expirada, logout, recuperação de acesso e operações CRUD, publicar a nova versão.
5. Cadastrar os três coordenadores e definir as senhas por um fluxo seguro de configuração, sem compartilhar senhas pelo chat.

## Não fazer

- Não colocar a chave `service_role` no HTML ou no repositório.
- Não desativar as políticas RLS existentes antes de testar a nova arquitetura.
- Não afirmar que os acessos estão ativos antes de publicar e testar a Edge Function.
- Não criar logins para profissionais/instrutores que só precisam constar nos cadastros.

## Dependências de implantação

É necessário acesso ao painel Supabase para configurar os segredos da função e executar a migração SQL, e acesso ao repositório GitHub para publicar a alteração do frontend. Os arquivos de preparação não ativam, por si só, os novos acessos.
