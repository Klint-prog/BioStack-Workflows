# Changelog

Todas as mudanças relevantes do BioStack Workflows serão documentadas neste arquivo.

O formato segue uma organização simples por versão, com foco em rastreabilidade do MVP.

## Não lançado

### Observações

- Sem mudanças pendentes após a preparação do release v0.2.0 nesta fase.

## v0.2.0 — Docker Platform Edition

### Adicionado

- Docker Platform Edition com backend/CLI, API FastAPI versionada, PostgreSQL 16, Redis 7, worker assíncrono, frontend React/Vite e reverse proxy Nginx.
- Fluxo end-to-end obrigatório: criar projeto, executar dry-run, gerar relatório, visualizar no painel e explicar logs com IA mock.
- Persistência relacional de projetos, runs, eventos e arquivos usando SQLAlchemy, Psycopg e Alembic.
- Fila Redis simples para execução assíncrona por worker.
- Script `scripts/e2e-smoke.sh` para validação HTTP via Nginx.
- Healthchecks para serviços principais.
- Logging consistente para API e worker via `BIOSTACK_LOG_LEVEL`.
- CORS configurável via `BIOSTACK_CORS_ORIGINS`.
- Documentação de segurança operacional, performance, backup/restore e troubleshooting Docker.

### Alterado

- README atualizado para apresentar a v0.2.0 Docker Platform Edition.
- `docker-compose.yml` usa imagens marcadas como `v0.2.0`, restart policies, rotação básica de logs, `no-new-privileges` e portas parametrizadas.
- Containers Python `backend`, `api` e `worker` executam como usuário não-root `biostack`.
- Frontend Docker usa `npm ci` para build reprodutível baseado no lockfile.
- CI passa a validar também o build do frontend.

### Segurança

- O Docker socket não é montado por padrão.
- `.env.example` continua sem segredos reais.
- IA permanece restrita a troubleshooting operacional e provider mock por padrão.
- O aviso `AVISO: Não usar para diagnóstico ou interpretação clínica.` permanece obrigatório.

### Limitações conhecidas

- Plataforma local-first, sem autenticação robusta de produção.
- Sem Kubernetes, HPC/SLURM, Apptainer, RBAC ou multiusuário avançado.
- Sem interpretação biológica ou clínica por IA.
- Execução simultânea complexa de muitos workflows permanece fora do escopo.

## v0.1.0 — Release público inicial

### Adicionado

- CLI instalável `biostack` baseada em Typer.
- Comandos `biostack version`, `biostack doctor`, `biostack init`, `biostack run` e `biostack report`.
- Template inicial `rnaseq-basic` para criação de projetos BioStack locais.
- Estrutura padrão de projeto com `data/raw`, `data/reference`, `workflows`, `results`, `reports`, `logs` e `config`.
- Runner Nextflow com profiles `local` e `docker`.
- Modo `--dry-run` para auditoria do comando sem exigir Nextflow instalado.
- Geração de logs por execução em `logs/<run_id>.log`.
- Metadados de execução com `run_id`, timestamps, duração, status, parâmetros, versões e comando executado/simulado.
- Checksums SHA256 para arquivos de entrada compatíveis em `data/raw/`.
- Relatórios JSON e HTML em `reports/<run_id>.json` e `reports/<run_id>.html`.
- Regeneração de HTML via `biostack report --run latest` ou `--run <run_id>`.
- Documentação de arquitetura, instalação, demo, relatórios e audit log.
- Exemplo autocontido em `examples/demo-rnaseq`.
- Makefile com targets de instalação, teste, lint, limpeza e demo.
- GitHub Actions com jobs de teste e lint usando Ruff.

### Limitações conhecidas

- O workflow `rnaseq-basic` é demonstrativo e não deve ser tratado como análise científica validada.
- O MVP é local-first e não inclui painel web complexo, Kubernetes, HPC/SLURM, multiusuário ou interpretação biológica por IA.
- A execução real depende de Nextflow e, no profile `docker`, Docker instalados no ambiente do usuário.
