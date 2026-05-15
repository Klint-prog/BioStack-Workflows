# Docker Platform Edition — phase_10

A phase_10 adiciona uma API FastAPI mínima e versionada à base Docker criada na phase_09, sem alterar o MVP local-first nem substituir a CLI.

Esta fase mantém filesystem local como persistência. Ela não adiciona PostgreSQL, Redis, fila, worker assíncrono, frontend React ou reverse proxy Nginx. Esses componentes pertencem a fases futuras.

## Serviços disponíveis

O `docker-compose.yml` define dois serviços:

- `backend`: preserva a CLI `biostack` dentro do container.
- `api`: inicia `uvicorn biostack.api.app:app` e expõe a API em `http://localhost:8000/api/v1`.

Ambos usam o volume nomeado `biostack_data` montado em `/workspace` para persistir projetos, logs e relatórios.

## Build

```bash
docker compose build
```

Ou pelo Makefile:

```bash
make docker-build
```

## Validar a CLI em container

```bash
docker compose run --rm backend biostack --help
docker compose run --rm backend biostack doctor
```

## Subir a API

```bash
docker compose up -d api
curl -f http://localhost:8000/api/v1/health
docker compose down
```

## Fluxo end-to-end atual em container

O fluxo obrigatório pode ser exercitado pela CLI ou pela API.

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

Via API:

```bash
docker compose up -d api
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
- A API da phase_10 é local-first, sem autenticação de produção e não deve ser exposta publicamente.
