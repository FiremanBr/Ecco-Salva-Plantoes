# Extensão EcoSalva — Reutilizar WhatsApp Web

Esta extensão encaminha o pedido do cronograma para a aba já aberta do WhatsApp Web.

## Instalação ou atualização

1. Baixe o ZIP do repositório e extraia.
2. Abra `chrome://extensions`.
3. Na extensão EcoSalva, clique em **Recarregar** (ícone de atualização). Se o arquivo foi baixado novamente em outra pasta, use **Carregar sem compactação** e selecione a pasta `whatsapp-helper-extension`.
4. Recarregue a página do cronograma EcoSalva.
5. Deixe o WhatsApp Web conectado e teste o botão.

## Observação

A extensão tenta fazer o WhatsApp tratar a rota dentro da aba existente. O WhatsApp Web é uma aplicação proprietária e não oferece uma API pública documentada para abrir conversas dentro da aplicação sem navegação; por isso, o comportamento deve ser validado no Chrome. Se o WhatsApp ainda mostrar recarregamento completo, essa abordagem não foi suficiente.

A extensão só aceita URLs do domínio `web.whatsapp.com` e caminho `/send`. Não lê conversas nem mensagens recebidas.
