// Tenta deixar o próprio WhatsApp Web tratar o clique no link, para que o roteador
// interno abra a conversa sem uma navegação completa. A interface pode mudar com atualizações.
chrome.runtime.onMessage.addListener((message) => {
  if (!message || message.type !== "ECOSALVA_OPEN_CHAT_LINK" || typeof message.url !== "string") return;
  let target;
  try { target = new URL(message.url); } catch { return; }
  if (target.origin !== location.origin || !target.pathname.startsWith("/send")) return;

  const link = document.createElement("a");
  link.href = target.href;
  link.style.display = "none";
  link.rel = "noopener";
  document.body.appendChild(link);
  link.click();
  link.remove();
});
