chrome.runtime.onMessage.addListener((message) => {
  if (!message || message.type !== "ECOSALVA_OPEN_WHATSAPP" || typeof message.url !== "string") return;
  let target;
  try { target = new URL(message.url); } catch { return; }
  if (target.origin !== "https://web.whatsapp.com" || !target.pathname.startsWith("/send")) return;

  chrome.tabs.query({ url: "https://web.whatsapp.com/*" }, (tabs) => {
    const existing = tabs.find(tab => Number.isInteger(tab.id));
    if (existing) {
      // Navegação normal para o link oficial, reutilizando a aba já aberta.
      // Não simula eventos da SPA: isso pode deixar o WhatsApp preso carregando.
      chrome.tabs.update(existing.id, { url: target.href, active: true }, () => {
        if (existing.windowId !== undefined) chrome.windows.update(existing.windowId, { focused: true });
      });
    } else {
      chrome.tabs.create({ url: target.href, active: true });
    }
  });
});
