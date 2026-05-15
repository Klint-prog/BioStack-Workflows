# Docker Platform Edition — phase_14

A phase_14 integra frontend, API, PostgreSQL, Redis, worker, storage compartilhado e reverse proxy Nginx em um fluxo end-to-end executável com `docker compose up --build`.

A plataforma continua local-first, sem autenticação robusta, sem Kubernetes, sem HPC/SLURM, sem orquestração distribuída e sem interpretação biológica por IA. O provider `mock` permanece como caminho seguro para troubleshooting operacional.

## Serviços disponíveis

O `docker-compose.yml` define seis serviços principais:

- `nginx`: reverse proxy público da plataforma em `http://localhost:8080`, roteando `/` para o frontend e `/api/` para a API.
- `frontend`: build React/Vite servido por Nginx interno, ainda acessível diretamente em `http://localhost:5173` para debug.
- `api`: FastAPI versionada em `/api/v1`, com migrations Alembic aplicadas no startup do container.
- `worker`: consumidor Redis que processa jobs de execução e atualiza runs persistidas.
- `postgres`: PostgreSQL 16 com volume persistente para projetos/runs/eventos.
- `redis`: Redis 7 com AOF e volume persistente para fila/cache local.

`backend`, `api` e `worker` usam o volume `biostack_workspace` montado em `/workspace`; projetos, logs e relatórios HTML/JSON ficam persistidos nesse volume.

## Comando principal

```bash
docker compose up --build -d
curl -f http://localhost:8080/api/v1/health
```

Depois acesse `http://localhost:8080` no navegador.

## Fluxo obrigatório

Pela interface ou via HTTP, valide:

1. criar projeto;
2. executar dry-run;
3. aguardar worker gerar relatório;
4. visualizar runs e relatórios no painel;
5. explicar logs com IA mock.

## Smoke test HTTP

```bash
bash scripts/e2e-smoke.sh
```

O script usa `BIOSTACK_E2E_BASE_URL`, com padrão `http://localhost:8080`, e executa o fluxo obrigatório via API através do Nginx.

## Comandos úteis

```bash
docker compose build
docker compose up -d postgres redis api worker frontend nginx
docker compose ps
docker compose logs --no-color api worker
docker compose down
```

Para resetar dados persistidos durante desenvolvimento local:

```bash
docker compose down -v
```

## Segurança e limites

- `.env.example` contém apenas valores seguros de exemplo.
- Não grave chaves reais no repositório.
- O provider mock é o padrão para explain.
- A API e o frontend são local-first e não devem ser expostos publicamente sem autenticação, TLS e hardening.
- O worker não monta `/var/run/docker.sock`; execução real com Nextflow/Docker exigiria revisão de risco antes de habilitar controle do host Docker.
