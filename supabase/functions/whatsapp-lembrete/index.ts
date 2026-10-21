import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const reply = (status: number, body: Record<string, unknown>) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return reply(405, { error: "Método não permitido." });
  const authHeader = req.headers.get("Authorization");
  if (!authHeader) return reply(401, { error: "Faça login novamente." });

  const url = Deno.env.get("SUPABASE_URL");
  const anon = Deno.env.get("SUPABASE_ANON_KEY");
  const token = Deno.env.get("WHATSAPP_ACCESS_TOKEN");
  const phoneId = Deno.env.get("WHATSAPP_PHONE_NUMBER_ID");
  const template = Deno.env.get("WHATSAPP_TEMPLATE_NAME") || "lembrete_aula";
  const language = Deno.env.get("WHATSAPP_TEMPLATE_LANG") || "pt_BR";
  if (!url || !anon || !token || !phoneId) return reply(503, { error: "Integração ainda não configurada: faltam secrets da WhatsApp Cloud API." });

  const db = createClient(url, anon, { global: { headers: { Authorization: authHeader } }, auth: { persistSession: false } });
  const { data: auth, error: authError } = await db.auth.getUser();
  if (authError || !auth.user?.email) return reply(401, { error: "Sessão inválida." });
  const { data: member } = await db.from("cronograma_membros").select("ativo").eq("email", auth.user.email.toLowerCase()).maybeSingle();
  if (!member?.ativo) return reply(403, { error: "Usuário não autorizado." });

  let input: { lessonId?: string };
  try { input = await req.json(); } catch { return reply(400, { error: "Solicitação inválida." }); }
  if (!input.lessonId) return reply(400, { error: "Informe a aula." });
  const { data: lesson } = await db.from("cronograma_aulas").select("id,profissional_id,municipio_id,data_aula,hora_inicio,hora_fim,titulo,status").eq("id", input.lessonId).maybeSingle();
  if (!lesson) return reply(404, { error: "Aula não encontrada ou sem permissão." });
  if (lesson.status !== "agendada") return reply(400, { error: "Só é possível avisar sobre aulas agendadas." });

  const [profResult, cityResult, topicsResult] = await Promise.all([
    db.from("cronograma_profissionais").select("nome,telefone,ativo").eq("id", lesson.profissional_id).maybeSingle(),
    db.from("cronograma_municipios").select("nome").eq("id", lesson.municipio_id).maybeSingle(),
    db.from("cronograma_aula_conteudos").select("titulo_snapshot").eq("aula_id", lesson.id),
  ]);
  const prof = profResult.data, city = cityResult.data, topics = topicsResult.data || [];
  if (!prof?.ativo || !prof.telefone) return reply(400, { error: "Profissional inativo ou sem telefone cadastrado." });
  const digits = String(prof.telefone).replace(/\D/g, "");
  const to = digits.startsWith("55") ? digits : "55" + digits;
  if (digits.length < 10 || digits.length > 13) return reply(400, { error: "Telefone inválido. Cadastre DDD e número." });

  const date = String(lesson.data_aula).split("-").reverse().join("/");
  const time = String(lesson.hora_inicio).slice(0, 5) + " às " + String(lesson.hora_fim).slice(0, 5);
  const topic = topics.map((t: { titulo_snapshot: string }) => t.titulo_snapshot).join(", ") || lesson.titulo || "Conteúdo conforme programação";
  // Template aprovado deve ter 5 variáveis no corpo: nome, data, horário, município, conteúdo.
  const parameters = [prof.nome, date, time, city?.nome || "A confirmar", topic].map((value) => ({ type: "text", text: String(value).slice(0, 900) }));
  const response = await fetch("https://graph.facebook.com/v22.0/" + phoneId + "/messages", {
    method: "POST",
    headers: { Authorization: "Bearer " + token, "Content-Type": "application/json" },
    body: JSON.stringify({ messaging_product: "whatsapp", recipient_type: "individual", to, type: "template", template: { name: template, language: { code: language }, components: [{ type: "body", parameters }] } }),
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) {
    console.error("WhatsApp Cloud API error", response.status, result);
    return reply(502, { error: result?.error?.message || "WhatsApp recusou a mensagem. Confira credenciais e template aprovado.", code: result?.error?.code || null });
  }
  return reply(200, { success: true, message: "Mensagem aceita pela API do WhatsApp.", messageId: result?.messages?.[0]?.id || null });
});