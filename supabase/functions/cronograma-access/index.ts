// Supabase Edge Function: cronograma-access
// Deploy with --no-verify-jwt; this function validates its own opaque session tokens.
// Required secrets: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, CRONOGRAMA_SETUP_SECRET.
// Never expose these secrets in the browser or commit them to GitHub.
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const SETUP_SECRET = Deno.env.get("CRONOGRAMA_SETUP_SECRET")!;
const db = createClient(URL, SERVICE_KEY, { auth: { persistSession: false } });
const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-setup-secret",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Content-Type": "application/json",
};
const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status, headers: cors });
const encoder = new TextEncoder();
const b64 = (bytes: Uint8Array) => btoa(String.fromCharCode(...bytes));
const unb64 = (s: string) => Uint8Array.from(atob(s), c => c.charCodeAt(0));
const randomBytes = (n: number) => crypto.getRandomValues(new Uint8Array(n));
const hex = (b: Uint8Array) => [...b].map(x => x.toString(16).padStart(2, "0")).join("");
async function sha256(s: string) {
  return hex(new Uint8Array(await crypto.subtle.digest("SHA-256", encoder.encode(s))));
}
async function passwordHash(password: string, salt: string, iterations = 310000) {
  const key = await crypto.subtle.importKey("raw", encoder.encode(password), "PBKDF2", false, ["deriveBits"]);
  const bits = await crypto.subtle.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt: unb64(salt), iterations }, key, 256);
  return b64(new Uint8Array(bits));
}
async function tokenUser(req: Request) {
  const token = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
  if (!token) return null;
  const hash = await sha256(token);
  const { data: session } = await db.from("cronograma_login_sessoes").select("email,expira_em").eq("token_hash", hash).maybeSingle();
  if (!session || new Date(session.expira_em) <= new Date()) return null;
  const { data: user } = await db.from("cronograma_login_usuarios").select("email,nome,ativo").eq("email", session.email).maybeSingle();
  if (!user?.ativo) return null;
  const { data: member } = await db.from("cronograma_membros").select("email,nome,papel,ativo").eq("email", session.email).maybeSingle();
  if (!member?.ativo) return null;
  return { email: user.email, nome: member.nome || user.nome, papel: member.papel };
}
const tables = new Set(["cronograma_membros","cronograma_municipios","cronograma_profissionais","cronograma_metas","cronograma_conteudos","cronograma_aulas","cronograma_aula_conteudos"]);
const adminOnly = new Set(["cronograma_municipios","cronograma_profissionais","cronograma_metas","cronograma_conteudos","cronograma_membros"]);
function safeFilter(q: any, filters: any[] = []) {
  for (const f of filters) {
    if (!f || !/^[a-z_]+$/.test(f.column) || !["eq","neq","lt","lte","gt","gte","is","in"].includes(f.op)) throw new Error("Filtro inválido.");
    q = q[f.op](f.column, f.value);
  }
  return q;
}
Deno.serve(async req => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "Método não permitido." }, 405);
  try {
    const body = await req.json();
    if (body.action === "setup") {
      if (!SETUP_SECRET || req.headers.get("x-setup-secret") !== SETUP_SECRET) return json({ error: "Não autorizado." }, 401);
      const email = String(body.email || "").trim().toLowerCase();
      const password = String(body.password || "");
      if (password.length < 12 || !email) return json({ error: "Use senha com pelo menos 12 caracteres." }, 400);
      const { data: existing } = await db.from("cronograma_login_usuarios").select("email,papel,ativo").eq("email", email).maybeSingle();
      if (!existing) return json({ error: "E-mail não previsto na lista de coordenadores." }, 403);
      const salt = b64(randomBytes(16));
      const hash = await passwordHash(password, salt);
      const { error } = await db.from("cronograma_login_usuarios").update({ password_hash: hash, password_salt: salt, password_iterations: 310000, atualizado_em: new Date().toISOString() }).eq("email", email);
      if (error) throw error;
      return json({ ok: true, email });
    }
    if (body.action === "login") {
      const email = String(body.email || "").trim().toLowerCase();
      const password = String(body.password || "");
      const { data: user } = await db.from("cronograma_login_usuarios").select("*").eq("email", email).maybeSingle();
      if (!user?.ativo || user.password_hash === "PENDING_SETUP") return json({ error: "E-mail ou senha inválidos; a conta pode ainda não estar configurada." }, 401);
      const actual = await passwordHash(password, user.password_salt, user.password_iterations);
      if (actual !== user.password_hash) return json({ error: "E-mail ou senha inválidos." }, 401);
      const token = b64(randomBytes(32));
      const tokenHash = await sha256(token);
      const expira = new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString();
      const { error } = await db.from("cronograma_login_sessoes").insert({ token_hash: tokenHash, email, expira_em: expira });
      if (error) throw error;
      return json({ token, user: { email, nome: user.nome, papel: user.papel }, expiresAt: expira });
    }
    if (body.action === "logout") {
      const token = (req.headers.get("authorization") || "").replace(/^Bearer\s+/i, "");
      if (token) await db.from("cronograma_login_sessoes").delete().eq("token_hash", await sha256(token));
      return json({ ok: true });
    }
    const user = await tokenUser(req);
    if (!user) return json({ error: "Sessão inválida ou expirada. Entre novamente." }, 401);
    if (body.action === "me") return json({ user });
    if (body.action !== "query" || !tables.has(body.table)) return json({ error: "Operação inválida." }, 400);
    const table = body.table;
    const op = body.op;
    if (adminOnly.has(table) && user.papel !== "admin" && op !== "select") return json({ error: "Somente administrador pode alterar este cadastro." }, 403);
    if (table === "cronograma_membros" && user.papel !== "admin" && op !== "select") return json({ error: "Acesso negado." }, 403);
    let q: any = db.from(table);
    if (op === "select") {
      q = q.select(body.columns || "*");
      q = safeFilter(q, body.filters);
      if (body.order) q = q.order(body.order.column, { ascending: body.order.ascending !== false });
      if (body.single === "maybe") q = q.maybeSingle();
      else if (body.single === "one") q = q.single();
    } else if (op === "insert") {
      q = q.insert(body.values);
      if (body.returning) q = q.select(body.returning);
      if (body.single === "one") q = q.single();
    } else if (op === "upsert") {
      q = q.upsert(body.values, { onConflict: body.onConflict || "email" });
    } else if (op === "update" || op === "delete") {
      q = op === "update" ? q.update(body.values) : q.delete();
      q = safeFilter(q, body.filters);
      if (body.returning) q = q.select(body.returning);
      if (body.single === "one") q = q.single();
    } else return json({ error: "Operação inválida." }, 400);
    const { data, error } = await q;
    if (error) return json({ error: error.message, code: error.code }, 400);
    return json({ data });
  } catch (e) {
    return json({ error: e instanceof Error ? e.message : "Erro interno." }, 400);
  }
});
