# Validação end-to-end — phase_14

Este documento descreve o fluxo mínimo obrigatório da Docker Platform Edition integrada.

## Pré-requisitos

- Docker e Docker Compose instalados.
- Porta `8080` livre para o reverse proxy Nginx.
- Portas `8000` e `5173` livres se desejar acessar API e frontend diretamente para debug.

## Subir a plataforma

```bash
docker compose up --build -d
```

Validar healthcheck pelo Nginx:

```bash
curl -f http://localhost:8080/api/v1/health
```

## Fluxo pelo navegador

1. Acesse `http://localhost:8080`.
2. Crie um projeto com template `rnaseq-basic`.
3. Dispare um dry-run.
4. Aguarde o worker atualizar a run e gerar relatório.
5. Abra a área de relatórios e visualize o JSON.
6. Use Explain para gerar troubleshooting com provider `mock`.

## Fluxo por script

```bash
bash scripts/e2e-smoke.sh
```

Variáveis opcionais:

```bash
BIOSTACK_E2E_BASE_URL=http://localhost:8080 \
BIOSTACK_E2E_PROJECT_NAME=e2e-smoke \
BIOSTACK_E2E_TEMPLATE=rnaseq-basic \
bash scripts/e2e-smoke.sh
```

## Evidências esperadas

- `curl -f http://localhost:8080/api/v1/health` retorna HTTP 200.
- `POST /api/v1/projects` retorna projeto criado.
- `POST /api/v1/runs` retorna run enfileirada.
- `GET /api/v1/reports?project_name=<nome>` lista o relatório do dry-run após processamento do worker.
- `POST /api/v1/explain` retorna `provider=mock` e aviso contra uso clínico.

## Encerramento

```bash
docker compose logs --no-color api worker
docker compose down
```

Use `docker compose down -v` apenas quando quiser apagar banco, Redis e workspace persistidos.
