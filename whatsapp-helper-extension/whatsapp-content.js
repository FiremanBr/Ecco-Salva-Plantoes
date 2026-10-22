// Tenta deixar o próprio WhatsApp Web tratar a rota sem uma navegação completa.
// A interface do WhatsApp é proprietária e pode mudar; se não interceptar o clique,
// o fallback do background continuará funcionando.
chrome.runtime.onMessage.addListener((message) => {
  if (!message || message.type !== "ECOSALVA_NAVIGATE_CHAT" || typeof message.url !== "string") return;
  let target;
  try { target = new URL(message.url); } catch { return; }
  if (target.origin !== location.origin || !target.pathname.startsWith("/send")) return;

  const link = document.createElement("a");
  link.href = target.href;
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  link.remove();
});
