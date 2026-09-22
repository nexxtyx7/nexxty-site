# NEXXTY ONE — GitHub Pages

Versão estática do NEXXTY ONE, sem Python e sem Render.

## Arquivos
- `index.html` — interface
- `style.css` — visual
- `app.js` — CRM + pesquisa + armazenamento local

## Publicar no GitHub Pages
1. Coloque os 3 arquivos na raiz do repositório.
2. Vá em **Settings → Pages**.
3. Em **Build and deployment**, selecione **Deploy from a branch**.
4. Escolha `main` e `/ (root)`.
5. Salve.

## Importante
O GitHub Pages é estático. Os leads ficam salvos no `localStorage` do navegador. A pesquisa usa serviços públicos do OpenStreetMap/Overpass. Não existe banco de dados compartilhado entre dispositivos nesta versão.
