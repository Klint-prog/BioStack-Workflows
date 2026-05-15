# Docker Platform Edition — phase_12

A phase_12 adiciona Redis 7 e worker assíncrono à Docker Platform Edition, preservando a CLI local-first e a persistência PostgreSQL criada na phase_11.

Esta fase mantém relatórios, logs e arquivos de projeto no filesystem, grava metadados no PostgreSQL e passa a enfileirar execuções criadas pela API. Ela não adiciona frontend React, Nginx, autenticação robusta, Kubernetes ou execução distribuída.

## Serviços disponíveis

O `docker-compose.yml` define cinco serviços:

- `postgres`: banco PostgreSQL 16 com healthcheck via `pg_isready`.
- `redis`: Redis 7 com healthcheck via `redis-cli ping` e persistência AOF simples.
- `backend`: preserva a CLI `biostack` dentro do container.
- `api`: inicia `uvicorn biostack.api.app:app` e expõe a API em `http://localhost:8000/api/v1`.
- `worker`: executa `biostack-worker` e processa jobs de runs vindos do Redis.

`backend`, `api` e `worker` usam o volume nomeado `biostack_data` montado em `/workspace` para persistir projetos, logs e relatórios. PostgreSQL e Redis usam volumes próprios.

## Build

```bash
docker compose build
```

Ou pelo Makefile, se disponível:

```bash
make docker-build
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

## Subir API e worker

```bash
docker compose up -d worker api
curl -f http://localhost:8000/api/v1/health
docker compose ps
docker compose down
```

## Fluxo end-to-end atual em container

O fluxo obrigatório pode ser exercitado pela CLI ou pela API com worker.

Via CLI:

```bash
docker compose run --rm backend sh -lc '
  rm -rf demo && \
  biostack init demo --template rnaseq-basic && \
  cd demo && \
  biostack run --dry-run && \
  biostack report --run latest && \
  biostack explain --run latest --provider mock
'
```

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
docker compose run --rm backend biostack --help
```

## Encerrar e limpar containers

```bash
docker compose down
```

Ou:

```bash
make docker-down
```

## Segurança

- `.env.example` contém apenas valores de exemplo.
- Não grave chaves reais no repositório.
- Não use `BIOSTACK_LLM_API_KEY` real em arquivos versionados.
- O provider mock continua sendo o caminho padrão seguro para testes de troubleshooting operacional.
- A API da phase_12 é local-first, sem autenticação de produção e não deve ser exposta publicamente.
- O worker não monta `/var/run/docker.sock`. Caso isso seja necessário para execução real com Docker/Nextflow, o risco deve ser documentado e revisado porque o socket permite controle elevado do host Docker.
