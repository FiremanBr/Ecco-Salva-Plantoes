# Cronograma de Aulas — configuração e uso

A interface está em `cronograma-aulas.html`; o esquema do banco está em `supabase-cronograma-aulas.sql`.

## Situação atual

- O projeto Supabase escolhido é `meu-financeiro-extras`, já utilizado pelo sistema financeiro. As tabelas do cronograma usam o prefixo `cronograma_` para separação lógica.
- O esquema SQL foi executado no painel do Supabase; a tabela `cronograma_membros` foi conferida e contém o administrador `joseluizpurific@gmail.com` com `papel = admin` e `ativo = true`.
- A página HTML já contém a URL e a chave pública do projeto `meu-financeiro-extras`.
- A publicação mais recente do GitHub Pages foi confirmada como concluída com sucesso. Ainda é necessário testar o login e as operações na interface.

## Acesso de administrador

1. A conta `joseluizpurific@gmail.com` já existe em Supabase Authentication > Users.
2. A tabela `cronograma_membros` já autoriza esse endereço como administrador.
3. Acesse a página Cronograma de Aulas publicada e entre usando a senha dessa conta no projeto Supabase `meu-financeiro-extras`.

## Cadastro da equipe

Para cada integrante:
1. Crie a conta de autenticação em Supabase > Authentication > Users (ou use uma conta já existente no mesmo projeto).
2. Na plataforma, abra **Equipe e acessos** e cadastre o mesmo e-mail com o perfil apropriado.
3. O integrante acessa a plataforma com esse e-mail e sua senha.

A plataforma não cria usuários de autenticação diretamente, pois isso exigiria uma função segura no servidor. Não compartilhe senhas entre integrantes.

## Perfis

- **Administrador:** gerencia membros, profissionais, municípios, metas e conteúdos; também pode agendar e registrar aulas.
- **Equipe:** consulta cadastros, agenda aulas, registra execução e atualiza observações. Não pode gerenciar cadastros-base nem excluir aulas.

## Regras

- Metas são totais por profissional e município para todo o projeto.
- A plataforma contabiliza aulas agendadas e ministradas; aulas canceladas não consomem a meta.
- A aplicação verifica conflitos de horário e o banco impede sobreposição para o mesmo profissional, inclusive entre municípios.
- O cronograma usa tabelas e políticas próprias. Mesmo assim, como o projeto Supabase é compartilhado com o financeiro, mantenha políticas RLS ativas e nunca coloque uma chave `service_role` ou `secret` no HTML.

## Testes antes de uso real

1. Entrar como administrador.
2. Cadastrar dois municípios, um profissional, uma meta e conteúdos.
3. Agendar uma aula.
4. Tentar agendar o mesmo profissional em horário sobreposto em outro município; o banco deve rejeitar.
5. Marcar execução e conferir a meta.
6. Entrar com conta de equipe e verificar que não consegue alterar cadastros-base.
7. Entrar no segundo dispositivo e confirmar que os dados aparecem.

