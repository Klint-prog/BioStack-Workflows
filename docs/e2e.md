# Validação end-to-end — v0.2.0

Este documento descreve o fluxo mínimo obrigatório da Docker Platform Edition integrada.

## Pré-requisitos

- Docker e Docker Compose instalados.
- Porta `8969` livre para o reverse proxy Nginx.
- Portas `8971` e `8970` livres se desejar acessar API e frontend diretamente para debug.

## Subir a plataforma

```bash
docker compose up --build -d
```

Validar healthcheck pelo Nginx:

```bash
curl -f http://localhost:8969/api/v1/health
```

## Fluxo pelo navegador

1. Acesse `http://localhost:8969`.
2. Confirme que o cabeçalho exibe `BioStack Workflows · Docker Platform Edition v0.2.0` e não menciona fases antigas.
3. Confirme que o dashboard mostra status da API, total de projetos, total de runs, total de relatórios e runs por status.
4. Crie um projeto com template `rnaseq-basic`.
5. Crie um projeto com template `variant-calling-basic`.
6. Dispare um dry-run em um projeto.
7. Abra a aba Runs e confirme o status visual da execução.
8. Aguarde o worker atualizar a run e gerar relatório.
9. Abra a área de relatórios e visualize o JSON.
10. Use Explain para gerar troubleshooting com provider `mock`.
11. Confirme que o aviso `AVISO: Não usar para diagnóstico ou interpretação clínica.` aparece.

## Fluxo por script

```bash
bash scripts/e2e-smoke.sh
```

Variáveis opcionais:

```bash
BIOSTACK_E2E_BASE_URL=http://localhost:8969 \
BIOSTACK_E2E_PROJECT_NAME=e2e-smoke \
BIOSTACK_E2E_TEMPLATE=rnaseq-basic \
bash scripts/e2e-smoke.sh
```

## Evidências esperadas

- `curl -f http://localhost:8969/api/v1/health` retorna HTTP 200.
- `POST /api/v1/projects` retorna projeto criado.
- `POST /api/v1/runs` retorna run enfileirada.
- `GET /api/v1/runs` lista a run persistida.
- `GET /api/v1/reports?project_name=<nome>` lista o relatório do dry-run após processamento do worker.
- `GET /api/v1/reports/{project_name}/{run_id}` retorna o JSON do relatório.
- `POST /api/v1/explain` retorna `provider=mock` e aviso contra uso clínico.

## Encerramento

```bash
docker compose logs --no-color api worker
docker compose down
```

Use `docker compose down -v` apenas quando quiser apagar banco, Redis e workspace persistidos.
