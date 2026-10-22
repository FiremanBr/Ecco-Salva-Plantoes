// Ponte entre o cronograma EcoSalva e a extensão.
// A página envia somente URLs de envio do WhatsApp Web.
window.addEventListener("message", (event) => {
  if (event.source !== window || !event.data || event.data.type !== "ECOSALVA_OPEN_WHATSAPP") return;
  const url = event.data.url;
  if (typeof url !== "string") return;
  let parsed;
  try { parsed = new URL(url); } catch { return; }
  if (parsed.origin !== "https://web.whatsapp.com" || !parsed.pathname.startsWith("/send")) return;
  chrome.runtime.sendMessage({ type: "ECOSALVA_OPEN_WHATSAPP", url: parsed.href });
});
