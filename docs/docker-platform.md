# Docker Platform Edition — phase_13

A phase_13 adiciona um frontend separado em React, Vite e TypeScript à Docker Platform Edition, preservando a CLI local-first, a API FastAPI versionada, o PostgreSQL, o Redis e o worker assíncrono criados nas fases anteriores.

Esta fase mantém relatórios, logs e arquivos de projeto no filesystem, grava metadados no PostgreSQL, enfileira execuções pelo Redis e permite operar o fluxo principal pelo navegador. Ela não adiciona autenticação robusta, Kubernetes, execução distribuída ou Nginx externo de reverse proxy para toda a plataforma; o frontend usa Nginx apenas para servir arquivos estáticos e encaminhar `/api` ao serviço `api`.

## Serviços disponíveis

O `docker-compose.yml` define seis serviços:

- `postgres`: banco PostgreSQL 16 com healthcheck via `pg_isready`.
- `redis`: Redis 7 com healthcheck via `redis-cli ping` e persistência AOF simples.
- `backend`: preserva a CLI `biostack` dentro do container.
- `api`: inicia `uvicorn biostack.api.app:app` e expõe a API em `http://localhost:8000/api/v1`.
- `worker`: executa `biostack-worker` e processa jobs de runs vindos do Redis.
- `frontend`: serve o build React/Vite em `http://localhost:5173` e encaminha `/api/` para `api:8000`.

`backend`, `api` e `worker` usam o volume nomeado `biostack_data` montado em `/workspace` para persistir projetos, logs e relatórios. PostgreSQL e Redis usam volumes próprios.

## Build

```bash
docker compose build
```

Ou para validar apenas a interface:

```bash
docker compose build frontend
```

## Subir PostgreSQL/Redis e aplicar migrations

```bash
docker compose up -d postgres redis
docker compose run --rm api alembic upgrade head
```

## Validar a CLI em container

```bash
docker compose run --rm backend biostack --help
docker compose run --rm backend biostack doctor
```

## Subir API, worker e frontend

```bash
docker compose up -d frontend api worker postgres redis
curl -f http://localhost:8000/api/v1/health
docker compose ps
```

Depois acesse `http://localhost:5173` e use a interface para criar projeto, executar dry-run, acompanhar runs, abrir relatórios e executar explain mock.

## Fluxo end-to-end atual em container

O fluxo obrigatório pode ser exercitado pela CLI, pela API com worker ou pelo frontend.

Via API assíncrona:

```bash
docker compose up -d postgres redis
docker compose run --rm api alembic upgrade head
docker compose up -d worker api
curl -f http://localhost:8000/api/v1/health
curl -s -X POST http://localhost:8000/api/v1/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"demo-api","template":"rnaseq-basic"}'
curl -s -X POST http://localhost:8000/api/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{"project_name":"demo-api","dry_run":true}'
curl -s 'http://localhost:8000/api/v1/runs?project_name=demo-api'
curl -s 'http://localhost:8000/api/v1/reports?project_name=demo-api'
curl -s -X POST http://localhost:8000/api/v1/explain \
  -H 'Content-Type: application/json' \
  -d '{"project_name":"demo-api","run":"latest","provider":"mock"}'
docker compose down
```

A criação da run pela API retorna `QUEUED`; o worker atualiza o status para `RUNNING` e depois `SUCCEEDED` ou `FAILED`.

## Testes Docker

```bash
docker compose run --rm backend pytest -q
docker compose run --rm backend ruff check .
docker compose build frontend
docker compose up -d frontend api worker postgres redis
docker compose ps
docker compose down
```

## Frontend

Consulte [docs/frontend.md](frontend.md) para comandos locais de `npm install`, `npm run build` e detalhes do proxy `/api`.

## Segurança

- `.env.example` contém apenas valores de exemplo.
- Não grave chaves reais no repositório.
- Não use `BIOSTACK_LLM_API_KEY` real em arquivos versionados.
- O provider mock continua sendo o caminho padrão seguro para testes de troubleshooting operacional.
- A API e o frontend da phase_13 são local-first, sem autenticação de produção e não devem ser expostos publicamente.
- O worker não monta `/var/run/docker.sock`. Caso isso seja necessário para execução real com Docker/Nextflow, o risco deve ser documentado e revisado porque o socket permite controle elevado do host Docker.
