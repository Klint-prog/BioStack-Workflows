# Audit log complementar — phase_13

## phase_13 — Frontend React/Vite

- Decisão: adicionar `frontend/` com React, Vite e TypeScript para operar o fluxo principal sem alterar profundamente backend, banco ou worker.
- Decisão: usar chamadas relativas para `/api/v1`; no desenvolvimento local o Vite faz proxy para `localhost:8000`, e no container o Nginx do frontend encaminha `/api/` para `api:8000`.
- Decisão: criar um endpoint incremental `GET /api/v1/runs` para listar runs persistidas e alimentar a tabela de status do frontend.
- Decisão: manter visual simples e funcional, com páginas Dashboard, Projects, Runs, Reports e Explain, sem design system complexo.
- Decisão: manter explain limitado ao provider `mock` na interface e preservar o aviso contra diagnóstico ou interpretação clínica.
- Observação: Nginx externo/reverse proxy consolidado da plataforma permanece preparado para phase_14; nesta fase há apenas Nginx interno do container frontend para arquivos estáticos e proxy `/api`.
