# Frontend React/Vite — phase_13

A phase_13 adiciona um frontend separado em React, Vite e TypeScript para operar o fluxo principal da Docker Platform Edition sem substituir a CLI local-first.

## Escopo

A interface cobre apenas o fluxo operacional mínimo:

1. criar projeto pela API `/api/v1/projects`;
2. enfileirar dry-run pela API `/api/v1/runs`;
3. listar runs e status;
4. listar relatórios e abrir metadados JSON;
5. executar explain mock para troubleshooting operacional.

Não há autenticação robusta, multiusuário, interpretação biológica por IA ou design avançado nesta fase.

## Desenvolvimento local

```bash
cd frontend
npm install
npm run build
npm run dev
```

Durante `npm run dev`, o Vite faz proxy de `/api` para `http://localhost:8000`.

## Execução em container

```bash
docker compose build frontend
docker compose up -d frontend api worker postgres redis
```

Acesse `http://localhost:5173`. O Nginx do container serve os arquivos estáticos e encaminha `/api/` para o serviço `api:8000` dentro da rede Compose.

## Observações de segurança

- A interface é local-first e não deve ser exposta publicamente.
- O provider mock continua sendo o caminho padrão para explain.
- Chaves reais de LLM não devem ser colocadas no frontend nem em arquivos versionados.
