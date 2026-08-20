import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const API_URL = "https://southamerica-east1-no-api-br.cloudfunctions.net/apiMedicamentos/v1/medicamentos";

Deno.serve(async (req) => {
  const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
  };

  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: cors });
  }

  try {
    const url = new URL(req.url);
    const nome = (url.searchParams.get("nome") || "").trim();
    const registro = (url.searchParams.get("registro") || "").trim();

    if (!nome && !registro) {
      return new Response(JSON.stringify({ error: "Informe nome ou registro ANVISA." }), {
        status: 400,
        headers: { ...cors, "Content-Type": "application/json" },
      });
    }

    const apiKey = Deno.env.get("MEDICAMENTOS_API_KEY");
    if (!apiKey) {
      return new Response(JSON.stringify({
        error: "MEDICAMENTOS_API_KEY não configurada no Supabase.",
        setup_required: true,
      }), {
        status: 503,
        headers: { ...cors, "Content-Type": "application/json" },
      });
    }

    const params = new URLSearchParams();
    if (nome) params.set("nome", nome);
    if (registro) params.set("registro", registro);

    const upstream = await fetch(`${API_URL}?${params.toString()}`, {
      method: "GET",
      headers: {
        "X-API-Key": apiKey,
        "Accept": "application/json",
      },
    });

    const text = await upstream.text();
    let body: unknown;
    try {
      body = JSON.parse(text);
    } catch {
      body = { error: "Resposta inválida da API de medicamentos.", raw: text.slice(0, 500) };
    }

    return new Response(JSON.stringify(body), {
      status: upstream.status,
      headers: {
        ...cors,
        "Content-Type": "application/json",
        "Cache-Control": "private, max-age=300",
      },
    });
  } catch (error) {
    return new Response(JSON.stringify({
      error: error instanceof Error ? error.message : String(error),
    }), {
      status: 500,
      headers: { ...cors, "Content-Type": "application/json" },
    });
  }
});
