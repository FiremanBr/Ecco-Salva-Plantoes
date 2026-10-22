// Solicita ao roteador SPA do WhatsApp Web a abertura do chat sem clicar em link
// nem fazer navegação completa. A interface é proprietária; o comportamento pode variar.
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!message || message.type !== "ECOSALVA_NAVIGATE_CHAT" || typeof message.url !== "string") return;
  let target;
  try { target = new URL(message.url); } catch { sendResponse({ ok: false, reason: "invalid-url" }); return; }
  if (target.origin !== location.origin || !target.pathname.startsWith("/send")) {
    sendResponse({ ok: false, reason: "invalid-origin-or-path" });
    return;
  }

  try {
    // Atualiza a rota usando a History API, sem acionar uma navegação de documento.
    history.pushState({}, "", target.href);
    window.dispatchEvent(new PopStateEvent("popstate", { state: {} }));
    window.dispatchEvent(new Event("hashchange"));
    sendResponse({ ok: true });
  } catch (error) {
    sendResponse({ ok: false, reason: "spa-navigation-failed" });
  }
  return true;
});
