# Cronograma de Aulas — instalação inicial

A interface está em `cronograma-aulas.html`; o esquema e as regras de segurança do banco estão em `supabase-cronograma-aulas.sql`.

## Configuração obrigatória antes do primeiro acesso

1. Abra o projeto Supabase já usado pela plataforma Ecco Salva.
2. Em **SQL Editor**, abra `supabase-cronograma-aulas.sql`.
3. **Antes de executar**, substitua `admin@seu-dominio.com` no INSERT final pelo e-mail real da conta que será administradora, em letras minúsculas.
4. Crie essa conta em **Authentication → Users** (ou use uma conta já existente no mesmo projeto Supabase).
5. Execute o SQL completo. Ele cria tabelas separadas para profissionais, municípios, metas, conteúdos, aulas, registros de execução e membros, com RLS e bloqueio de sobreposição de horário.
6. Acesse a plataforma publicada e entre com o e-mail e a senha dessa conta.
7. Na aba **Equipe e acessos**, autorize os e-mails da equipe e escolha o perfil. Cada integrante também precisa ter uma conta em **Authentication → Users** com o mesmo e-mail.

## Perfis

- **Administrador:** gerencia membros, profissionais, municípios, metas e programas de conteúdo; também pode agendar e registrar aulas.
- **Equipe:** consulta os cadastros, agenda aulas, registra a execução e atualiza observações. Não pode gerenciar cadastros-base nem apagar aulas.

## Regras importantes

- As metas são totais por profissional e município para todo o projeto.
- Agendar ou ministrar uma aula consome uma unidade da meta; cancelar devolve a unidade.
- A plataforma verifica conflitos de horário no navegador e o banco também impede sobreposição para o mesmo profissional, inclusive se duas pessoas tentarem salvar ao mesmo tempo.
- Os registros são compartilhados pelo Supabase. Não limpe os dados nem desative as políticas de segurança para corrigir problemas de acesso.
- A criação de contas de autenticação não é feita diretamente pela página, pois isso exigiria uma função segura no servidor. O administrador cria as contas em Supabase Authentication e depois autoriza os e-mails na plataforma.

## Testes recomendados

1. Criar dois municípios, um profissional, uma meta e dois conteúdos.
2. Agendar uma aula no primeiro município.
3. Tentar agendar o mesmo profissional no mesmo horário no segundo município: deve bloquear.
4. Agendar uma aula em horário diferente: deve aceitar.
5. Registrar a execução e conferir o saldo da meta.
6. Entrar com uma conta de equipe e confirmar que os cadastros-base não podem ser alterados.
