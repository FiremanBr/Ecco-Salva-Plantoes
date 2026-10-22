chrome.runtime.onMessage.addListener((message) => {
  if (!message || message.type !== "ECOSALVA_OPEN_WHATSAPP" || typeof message.url !== "string") return;
  let target;
  try { target = new URL(message.url); } catch { return; }
  if (target.origin !== "https://web.whatsapp.com" || !target.pathname.startsWith("/send")) return;

  chrome.tabs.query({ url: "https://web.whatsapp.com/*" }, (tabs) => {
    const existing = tabs.find(tab => Number.isInteger(tab.id));
    if (existing) {
      // Não altere a URL da aba como fallback: isso recarregaria o WhatsApp.
      chrome.tabs.sendMessage(existing.id, { type: "ECOSALVA_NAVIGATE_CHAT", url: target.href }, () => {
        // Mesmo que o content script não esteja disponível, apenas foca a aba.
        // O usuário pode recarregar a aba manualmente para injetar a extensão.
        chrome.tabs.update(existing.id, { active: true });
        if (existing.windowId !== undefined) chrome.windows.update(existing.windowId, { focused: true });
      });
    } else {
      // Só abre uma aba nova quando não existe nenhuma aba do WhatsApp Web.
      chrome.tabs.create({ url: target.href, active: true });
    }
  });
});
