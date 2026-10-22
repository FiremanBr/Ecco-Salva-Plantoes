chrome.runtime.onMessage.addListener((message) => {
  if (!message || message.type !== "ECOSALVA_OPEN_WHATSAPP" || typeof message.url !== "string") return;
  let target;
  try { target = new URL(message.url); } catch { return; }
  if (target.origin !== "https://web.whatsapp.com" || !target.pathname.startsWith("/send")) return;

  chrome.tabs.query({ url: "https://web.whatsapp.com/*" }, (tabs) => {
    const existing = tabs.find(tab => Number.isInteger(tab.id));
    if (existing) {
      // Mantém a aba e a sessão. A navegação é solicitada ao conteúdo do WhatsApp,
      // em vez de atualizar a URL da aba pelo Chrome.
      chrome.tabs.sendMessage(existing.id, { type: "ECOSALVA_NAVIGATE_CHAT", url: target.href }, () => {
        if (chrome.runtime.lastError) {
          // Fallback quando o content script ainda não estiver disponível.
          chrome.tabs.update(existing.id, { url: target.href, active: true });
        } else {
          chrome.tabs.update(existing.id, { active: true });
        }
        if (existing.windowId !== undefined) chrome.windows.update(existing.windowId, { focused: true });
      });
    } else {
      chrome.tabs.create({ url: target.href, active: true });
    }
  });
});
