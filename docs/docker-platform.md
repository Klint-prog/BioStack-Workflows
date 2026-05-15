# Docker Platform Edition — v0.2.0

A v0.2.0 Docker Platform Edition integra frontend, API, PostgreSQL, Redis, worker, storage compartilhado e reverse proxy Nginx em um fluxo end-to-end executável com `docker compose up --build`.

A plataforma continua local-first, sem autenticação robusta, sem Kubernetes, sem HPC/SLURM, sem orquestração distribuída e sem interpretação biológica por IA. O provider `mock` permanece como caminho seguro para troubleshooting operacional.

## Serviços disponíveis

O `docker-compose.yml` define seis serviços principais e um serviço auxiliar de backend/CLI:

- `nginx`: reverse proxy público da plataforma em `http://localhost:8969`, roteando `/` para o frontend e `/api/` para a API.
- `frontend`: build React/Vite servido por Nginx interno, ainda acessível diretamente em `http://localhost:8970` para debug.
- `api`: FastAPI versionada em `/api/v1`, ainda acessível diretamente em `http://localhost:8971` para debug, com migrations Alembic aplicadas no startup do container.
- `worker`: consumidor Redis que processa jobs de execução e atualiza runs persistidas.
- `backend`: container auxiliar para comandos CLI e diagnósticos, fora do caminho principal quando configurado por profile.
- `postgres`: PostgreSQL 16 com volume persistente para projetos/runs/eventos.
- `redis`: Redis 7 com AOF e volume persistente para fila/cache local.

`backend`, `api` e `worker` usam o volume `biostack_workspace` montado em `/workspace`; projetos, logs e relatórios HTML/JSON ficam persistidos nesse volume.

## Portas externas padrão

A plataforma usa portas altas por padrão para reduzir conflitos com outros serviços locais:

- `PLATFORM_PORT=8969`: entrada principal via Nginx.
- `FRONTEND_PORT=8970`: frontend direto para debug.
- `API_PORT=8971`: API direta para debug.

As portas internas dos containers continuam as mesmas: API em `8000` e frontend/Nginx em `80`.

## Frontend operacional

O frontend React/Vite é um painel operacional que consome dados reais da API, sem substituir respostas de projetos, runs ou relatórios por mocks.

Fluxo:

```text
Browser -> Nginx -> Frontend React/Vite -> API FastAPI /api/v1 -> PostgreSQL/Redis/Worker -> Workspace compartilhado
```

A UI oferece:

- dashboard com healthcheck, total de projetos, total de runs, total de relatórios e runs por status;
- criação de projeto com validação visual, loading, sucesso e erro;
- listagem de projetos com ações para dry-run, runs e relatórios;
- listagem de runs com badges `QUEUED`, `RUNNING`, `SUCCEEDED` e `FAILED`;
- polling automático enquanto houver run ativa;
- listagem e abertura de relatórios JSON;
- explain mock com aviso obrigatório contra diagnóstico ou interpretação clínica.

Veja [Frontend UX operacional](frontend-ux.md).

## Hardening aplicado na v0.2.0

- Containers Python executam como usuário não-root `biostack`.
- Serviços usam `restart: unless-stopped`.
- Serviços principais têm healthchecks.
- O Compose aplica `security_opt: no-new-privileges:true`.
- Logs Docker têm rotação básica com `max-size=10m` e `max-file=3`.
- Portas são parametrizadas por `.env` local.
- Redis usa limite básico de memória configurável por `REDIS_MAXMEMORY`.
- API possui CORS configurável por `BIOSTACK_CORS_ORIGINS`.
- API e worker usam logging consistente via `BIOSTACK_LOG_LEVEL`.

## Comando principal

```bash
docker compose up --build -d
curl -f http://localhost:8969/api/v1/health
```

Depois acesse `http://localhost:8969` no navegador.

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

O script usa `BIOSTACK_E2E_BASE_URL`, com padrão `http://localhost:8969`, e executa o fluxo obrigatório via API através do Nginx.

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

Não execute reset destrutivo antes de consultar [Backup e restore](backup-restore.md).

## Variáveis principais

Veja `.env.example` para valores seguros de exemplo. As principais variáveis operacionais são:

- `BIOSTACK_LOG_LEVEL`
- `BIOSTACK_CORS_ORIGINS`
- `BIOSTACK_LLM_PROVIDER`
- `BIOSTACK_QUEUE_NAME`
- `REDIS_MAXMEMORY`
- `API_PORT`
- `FRONTEND_PORT`
- `PLATFORM_PORT`

## Documentos operacionais

- [Frontend UX operacional](frontend-ux.md)
- [Segurança operacional](security.md)
- [Performance operacional](performance.md)
- [Backup e restore](backup-restore.md)
- [Troubleshooting Docker](troubleshooting-docker.md)
- [Validação end-to-end](e2e.md)

## Segurança e limites

- `.env.example` contém apenas valores seguros de exemplo.
- Não grave chaves reais no repositório.
- O provider mock é o padrão para explain.
- A API e o frontend são local-first e não devem ser expostos publicamente sem autenticação, TLS e hardening adicional.
- O worker não monta `/var/run/docker.sock`; execução real com Nextflow/Docker exigiria revisão de risco antes de habilitar controle do host Docker.
