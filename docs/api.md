# API FastAPI versionada — phase_10

A phase_10 adiciona uma API FastAPI mínima e versionada em `/api/v1` para operações locais do BioStack Workflows.

A API continua local-first e usa filesystem. Ela não adiciona PostgreSQL, Redis, fila, worker assíncrono, autenticação robusta, frontend React ou Nginx.

## Execução local

```bash
python -m pip install -e '.[web,dev]'
uvicorn biostack.api.app:app --host 127.0.0.1 --port 8000
```

## Execução com Docker Compose

```bash
docker compose build
docker compose up -d api
curl -f http://localhost:8000/api/v1/health
docker compose down
```

O workspace usado pela API é definido por `BIOSTACK_WORKSPACE`. No Docker Compose ele aponta para `/workspace`, persistido no volume `biostack_data`.

## Endpoints

### Healthcheck

```http
GET /api/v1/health
```

Resposta:

```json
{"status":"ok"}
```

### Listar projetos

```http
GET /api/v1/projects
```

Lista projetos BioStack detectados no workspace configurado.

### Criar projeto

```http
POST /api/v1/projects
Content-Type: application/json

{
  "name": "demo-api",
  "template": "rnaseq-basic",
  "force": false
}
```

Cria um projeto usando o serviço existente de scaffold da CLI.

### Executar run síncrono

```http
POST /api/v1/runs
Content-Type: application/json

{
  "project_name": "demo-api",
  "dry_run": true
}
```

A fase 10 executa de forma síncrona. O uso recomendado nesta etapa é `dry_run=true`, sem fila e sem worker.

### Listar relatórios

```http
GET /api/v1/reports
GET /api/v1/reports?project_name=demo-api
```

Retorna relatórios JSON gerados nos projetos detectados.

### Consultar relatório

```http
GET /api/v1/reports/demo-api/latest
GET /api/v1/reports/demo-api/run-20260515T000000Z-00000000
```

Retorna o JSON de metadados persistido para um run.

### Explain mock

```http
POST /api/v1/explain
Content-Type: application/json

{
  "project_name": "demo-api",
  "run": "latest",
  "provider": "mock"
}
```

Retorna troubleshooting operacional usando o provider mock. O aviso contra uso clínico continua presente na resposta.

## Limites da fase

- Sem Postgres.
- Sem Redis.
- Sem fila ou worker assíncrono.
- Sem frontend React.
- Sem Nginx.
- Sem autenticação de produção.
- Sem interpretação biológica ou clínica por IA.
