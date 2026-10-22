chrome.runtime.onMessage.addListener((message) => {
  if (!message || message.type !== "ECOSALVA_OPEN_WHATSAPP" || typeof message.url !== "string") return;
  let target;
  try { target = new URL(message.url); } catch { return; }
  if (target.origin !== "https://web.whatsapp.com" || !target.pathname.startsWith("/send")) return;

  chrome.tabs.query({ url: "https://web.whatsapp.com/*" }, (tabs) => {
    const existing = tabs.find(tab => Number.isInteger(tab.id));
    if (existing) {
      // Pede à própria interface do WhatsApp para tratar o link, sem forçar tabs.update.
      chrome.tabs.sendMessage(existing.id, { type: "ECOSALVA_OPEN_CHAT_LINK", url: target.href }, () => {
        if (chrome.runtime.lastError) {
          // Se o content script não estiver disponível, não força uma navegação inesperada.
          console.warn("EcoSalva: não foi possível encaminhar o link à interface do WhatsApp.");
        }
      });
      chrome.tabs.update(existing.id, { active: true }, () => {
        if (existing.windowId !== undefined) chrome.windows.update(existing.windowId, { focused: true });
      });
    } else {
      chrome.tabs.create({ url: target.href, active: true });
    }
  });
});
