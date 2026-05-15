# Persistência PostgreSQL — phase_11

A phase_11 adiciona uma camada de persistência para a Docker Platform Edition do BioStack Workflows.

A CLI continua local-first e funcional sem banco. A API versionada em `/api/v1` passa a gravar metadados operacionais no banco, preservando relatórios HTML/JSON e logs no filesystem do projeto.

## Banco alvo

- PostgreSQL 16 em container `postgres:16-alpine`.
- SQLAlchemy 2.x para modelos e sessões.
- Psycopg 3 como driver PostgreSQL.
- Alembic para migrations.

## Variável de ambiente

```bash
BIOSTACK_DATABASE_URL=postgresql+psycopg://biostack:biostack@postgres:5432/biostack
```

Para testes locais sem Postgres, a camada suporta SQLite temporário.

## Modelos persistentes

A primeira migration cria:

- `projects`: projetos BioStack criados pela API ou sincronizados a partir do scaffold de filesystem.
- `runs`: execuções de workflow persistidas após `run_workflow` gerar log e relatórios.
- `run_events`: eventos estruturados de ciclo de vida da execução.
- `run_files`: arquivos relevantes da execução, incluindo log e relatórios.
- `audit_events`: trilha de auditoria para ações da plataforma.

## Fluxo da API

1. `POST /api/v1/projects` cria o projeto no filesystem usando o scaffolder existente.
2. A API grava ou atualiza o registro em `projects`.
3. `POST /api/v1/runs` executa o dry-run síncrono existente.
4. Logs e relatórios continuam sendo gravados no filesystem do projeto.
5. A API grava `runs`, `run_events`, `run_files` e `audit_events` no banco.

## Migrations

```bash
alembic upgrade head
```

No Docker Compose:

```bash
docker compose up -d postgres
docker compose run --rm api alembic upgrade head
```

## Limites desta fase

- Sem Redis.
- Sem worker assíncrono.
- Sem frontend React.
- Sem Nginx.
- Sem autenticação robusta de produção.
- Sem interpretação biológica ou clínica por IA.

## Decisão operacional

A API depende do schema já migrado. Em produção e no Compose, use Alembic antes de operar a API. Nos testes, o schema SQLite é criado explicitamente para manter os testes rápidos e isolados.
