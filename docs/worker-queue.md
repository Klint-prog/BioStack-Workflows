# Worker com Redis/fila — phase_12

A phase_12 adiciona execução assíncrona simples para runs da API usando Redis 7 como fila baseada em listas. A decisão foi evitar RQ, Dramatiq ou Celery nesta fase para manter o comportamento auditável, pequeno e fácil de revisar.

## Objetivo

O endpoint `POST /api/v1/runs` deixa de executar o workflow diretamente. Ele agora:

1. carrega o projeto no `BIOSTACK_WORKSPACE`;
2. persiste ou atualiza o projeto no PostgreSQL;
3. cria uma linha `Run` com status `QUEUED`;
4. registra eventos em `run_events` e `audit_events`;
5. envia um job JSON para a lista Redis configurada por `BIOSTACK_QUEUE_NAME`.

O worker consome a fila, muda o status para `RUNNING`, chama a lógica existente de execução com `dry_run` quando solicitado, gera logs/relatórios no filesystem e finaliza a execução como `SUCCEEDED` ou `FAILED`.

## Configuração

Variáveis relevantes:

```bash
BIOSTACK_DATABASE_URL=postgresql+psycopg://biostack:biostack@postgres:5432/biostack
BIOSTACK_REDIS_URL=redis://redis:6379/0
BIOSTACK_QUEUE_NAME=biostack:runs
BIOSTACK_WORKSPACE=/workspace
```

## Serviços Docker

A phase_12 adiciona os serviços:

- `redis`: Redis 7 com append-only file habilitado.
- `worker`: processo Python executando `biostack-worker`.

O worker compartilha o volume `biostack_data` com a API para que logs e relatórios sejam gravados no mesmo storage local persistente.

## Fluxo de status

Status usados nesta fase:

- `QUEUED`: run criada pela API e job enviado ao Redis.
- `RUNNING`: worker iniciou o processamento.
- `SUCCEEDED`: execução terminou com sucesso ou dry-run gerou relatório corretamente.
- `FAILED`: execução falhou ou o worker capturou erro operacional.

## Execução manual

```bash
docker compose up -d postgres redis
docker compose run --rm api alembic upgrade head
docker compose up -d worker api
```

Criar projeto e enfileirar dry-run:

```bash
curl -s -X POST http://localhost:8000/api/v1/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"demo-worker","template":"rnaseq-basic"}'

curl -s -X POST http://localhost:8000/api/v1/runs \
  -H 'Content-Type: application/json' \
  -d '{"project_name":"demo-worker","dry_run":true}'
```

A resposta da API retorna `status=QUEUED` e `job_id`. O processamento final ocorre no serviço `worker`.

## Auditoria

A API e o worker registram eventos em duas camadas:

- `run_events`: eventos estruturados do ciclo de vida da run.
- `audit_events`: eventos de auditoria da plataforma, como `run.queued`, `run.running`, `run.succeeded` e `run.failed`.

Logs e relatórios permanecem no filesystem do projeto em `logs/` e `reports/`.

## Segurança e Docker socket

Esta fase não monta `/var/run/docker.sock` no worker. Se uma execução real de Nextflow com profile Docker passar a exigir Docker-in-Docker ou acesso ao socket do host, o risco deve ser revisado antes de habilitar: montar o Docker socket concede ao container capacidade elevada sobre o Docker host e deve ser evitado em ambientes não confiáveis.

## Limites da fase

- Sem frontend React.
- Sem Nginx.
- Sem autenticação robusta.
- Sem orquestração distribuída.
- Sem execução concorrente complexa.
