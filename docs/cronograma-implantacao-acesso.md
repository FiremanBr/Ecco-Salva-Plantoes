# Implantação do acesso próprio dos coordenadores

Esta alteração está em uma branch separada: `implementacao-acesso-coordenadores`. **Não está ativa no site publicado até que seja revisada, integrada e implantada.**

## Arquivos preparados

- `cronograma-aulas.html`: login e chamadas de dados pelo gateway próprio.
- `supabase/functions/cronograma-access/index.ts`: autenticação e gateway com sessões opacas, expiração de 8 horas e hash PBKDF2-SHA-256 para senhas.
- `supabase/migrations/202610210001_cronograma_custom_auth.sql`: tabelas de login/sessão e lista dos três coordenadores.
- `tools/cronograma-configurar-acessos.html`: formulário local para definir senhas iniciais, sem gravá-las no repositório.

## Implantar

1. Revise a branch e integre-a ao branch que publica o GitHub Pages somente após validar a implementação.
2. No Supabase SQL Editor, execute o conteúdo de `supabase/migrations/202610210001_cronograma_custom_auth.sql`. O schema existente `supabase-cronograma-aulas.sql` deve estar aplicado antes, pois a migração também atualiza `cronograma_membros`.
3. Em Supabase > Edge Functions > Secrets, configure:
   - `SUPABASE_URL` = URL do projeto
   - `SUPABASE_SERVICE_ROLE_KEY` = chave service-role do projeto (segredo; nunca no HTML/repositório)
   - `CRONOGRAMA_SETUP_SECRET` = segredo aleatório longo, gerado por você e mantido privado
4. Publique a função pelo Supabase CLI:
   `supabase functions deploy cronograma-access --no-verify-jwt`
   A função valida os próprios tokens de sessão. O segredo service-role só é lido no servidor.
5. Abra localmente `tools/cronograma-configurar-acessos.html` em um computador confiável e defina uma senha forte e única para cada uma das três contas. A senha mínima é de 12 caracteres.
6. Teste as três contas, sessão expirada, logout, leitura, criação/edição/cancelamento de aula e permissões de administrador/coordenador.
7. Depois de configurar as contas, altere ou remova `CRONOGRAMA_SETUP_SECRET` para impedir reconfigurações não autorizadas. Remova o formulário local quando não for mais necessário.

## Limitações conhecidas a validar antes da produção

- A recuperação automática de senha ainda não está implementada; o botão orienta solicitar redefinição ao administrador.
- Faça testes de segurança, limite de tentativas de login e revisão do CORS antes de uso produtivo.
- Não remova RLS nem altere as políticas antigas como parte desta migração.
- O endpoint de setup só aceita os três e-mails semeados pela migração e exige o segredo de configuração.
