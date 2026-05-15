# BioStack Workflows

[![CI](https://github.com/Klint-prog/BioStack-Workflows/actions/workflows/ci.yml/badge.svg)](https://github.com/Klint-prog/BioStack-Workflows/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

BioStack Workflows é uma infraestrutura open source para criar, executar, documentar e auditar workflows de bioinformática reprodutíveis.

## Visão

A visão do projeto é oferecer uma camada simples, auditável e extensível para pesquisadores, estudantes, analistas de bioinformática e equipes técnicas que precisam executar pipelines científicos com rastreabilidade operacional.

O projeto começou como uma CLI local-first em Python e agora inclui a v0.2.0 Docker Platform Edition: API FastAPI, PostgreSQL, Redis, worker, frontend React/Vite e Nginx em Docker Compose, preservando a CLI.

## O que existe no v0.2.0

O release v0.2.0 consolida a Docker Platform Edition:

- CLI instalável com `biostack --help`, `biostack version`, `biostack doctor`, `biostack init`, `biostack run`, `biostack report`, `biostack web` e `biostack explain`.
- Templates `rnaseq-basic` e `variant-calling-basic` para criar estruturas auditáveis de projeto.
- Execução real ou simulada via Nextflow, com `--dry-run` para ambientes sem Nextflow.
- Relatórios HTML e JSON com metadados, versões, parâmetros, logs e checksums SHA256 dos inputs.
- API FastAPI versionada em `/api/v1`.
- Persistência PostgreSQL com migrations Alembic.
- Redis 7 para fila local simples.
- Worker assíncrono para processamento de runs.
- Frontend React/Vite separado.
- Reverse proxy Nginx em `http://localhost:8969`.
- Healthchecks, restart policies, rotação básica de logs e containers Python não-root.
- IA operacional opcional para troubleshooting técnico de logs e metadados, sem interpretação biológica ou clínica.
- CI com testes automatizados, lint Ruff e build frontend.

## Problema

Workflows de bioinformática frequentemente dependem de múltiplas ferramentas, parâmetros, versões, arquivos intermediários, containers e logs. Sem uma camada organizada de execução e auditoria, torna-se difícil responder perguntas básicas:

- Qual versão de cada ferramenta foi usada?
- Quais parâmetros foram aplicados?
- Quais arquivos foram processados?
- Os resultados podem ser reproduzidos por outra pessoa?
- Existe relatório técnico rastreável para revisão posterior?

## Solução proposta

BioStack Workflows organiza a execução de pipelines usando uma combinação de:

- Python 3.11+ para a CLI e lógica de orquestração inicial.
- Typer para comandos de terminal claros.
- Pydantic para validação de configurações e metadados.
- Rich para saída legível no terminal.
- Jinja2 para geração de relatórios e templates simples.
- PyYAML para configuração declarativa.
- Nextflow como motor de workflow científico.
- Docker e Docker Compose para reprodutibilidade de ambiente.
- FastAPI e Uvicorn para API versionada.
- SQLAlchemy, Psycopg e Alembic para persistência PostgreSQL.
- React, Vite e TypeScript para frontend separado.
- Redis 7 para fila simples do worker.
- Nginx para reverse proxy local da plataforma.
- Interface abstrata de provider LLM para troubleshooting operacional opcional.
- Relatórios HTML e JSON com metadados, versões, parâmetros, logs e checksums.

## Instalação local da CLI

Pré-requisitos mínimos:

- Python 3.11 ou superior.
- `pip` atualizado.

Pré-requisitos para execução real de workflows:

- Nextflow instalado e disponível no `PATH`.
- Docker instalado quando o profile `docker` for usado.

Instalação em modo editável:

```bash
python -m pip install -e .
```

Com dependências de desenvolvimento e web:

```bash
python -m pip install -e ".[web,dev]"
```

Consulte [docs/installation.md](docs/installation.md) para detalhes e solução de problemas.

## Quickstart CLI

```bash
biostack --help
biostack doctor
biostack init demo --template rnaseq-basic
cd demo
biostack run --dry-run
biostack report --run latest
biostack explain --run latest --provider mock
```

O `--dry-run` mostra o comando Nextflow sem executar e cria evidências auditáveis em `logs/` e `reports/`.

Para executar o workflow real, instale Nextflow e Docker e rode:

```bash
biostack run --workflow rnaseq-basic --profile docker
```

## Docker Platform Edition

A v0.2.0 Docker Platform Edition possui backend/CLI em container, API FastAPI versionada em `/api/v1`, persistência PostgreSQL, Redis, worker assíncrono, frontend React/Vite e reverse proxy Nginx.

```bash
docker compose up --build -d
curl -f http://localhost:8969/api/v1/health
bash scripts/e2e-smoke.sh
docker compose down
```

Acesse `http://localhost:8969` para criar projeto, executar dry-run, acompanhar runs, abrir relatórios e explicar logs com IA mock.

Portas externas padrão da plataforma Docker:

- `8969`: entrada principal via Nginx.
- `8970`: frontend direto para debug.
- `8971`: API direta para debug.

Leia mais em [docs/docker-platform.md](docs/docker-platform.md), [docs/e2e.md](docs/e2e.md), [docs/database.md](docs/database.md) e [docs/api.md](docs/api.md).

## Hardening operacional da v0.2.0

- Containers Python rodam como usuário não-root.
- Serviços principais têm healthchecks.
- Compose usa `restart: unless-stopped`.
- Logs Docker têm rotação básica.
- `BIOSTACK_CORS_ORIGINS` controla CORS da API.
- `BIOSTACK_LOG_LEVEL` controla logging de API e worker.
- O Docker socket não é montado por padrão.
- Segredos reais não devem ser gravados no repositório.

Consulte [docs/security.md](docs/security.md), [docs/performance.md](docs/performance.md), [docs/backup-restore.md](docs/backup-restore.md) e [docs/troubleshooting-docker.md](docs/troubleshooting-docker.md).

## API FastAPI versionada

A API local-first expõe healthcheck, projetos, runs assíncronos via worker, relatórios e explain mock em `/api/v1`.

```bash
python -m pip install -e ".[web,dev]"
uvicorn biostack.api.app:app --host 127.0.0.1 --port 8971
curl -f http://127.0.0.1:8971/api/v1/health
```

Leia mais em [docs/api.md](docs/api.md).

## Painel web local experimental

O painel web é opcional, experimental, local e sem autenticação. Ele serve para revisar projetos e relatórios já gerados pela CLI, não para substituir o fluxo de terminal.

```bash
python -m pip install -e ".[web]"
biostack web --host 127.0.0.1 --port 8972
```

Depois acesse `http://127.0.0.1:8972/` em um navegador local. Não exponha esse servidor em redes públicas.

Leia mais em [docs/web-ui.md](docs/web-ui.md).

## IA operacional e troubleshooting

O comando `biostack explain` resume logs, explica falhas técnicas e sugere próximos passos operacionais a partir de metadados e logs de um run.

```bash
biostack explain --run latest --provider mock
```

Aviso obrigatório exibido em toda execução:

```text
AVISO: Não usar para diagnóstico ou interpretação clínica.
```

O provider `mock` é determinístico e usado em testes. O provider `env` exige a variável `BIOSTACK_LLM_API_KEY`, mas o MVP ainda não implementa chamadas externas reais.

Leia mais em [docs/ai-troubleshooting.md](docs/ai-troubleshooting.md).

## Demo

Leia o walkthrough completo em [docs/demo.md](docs/demo.md). Um exemplo autocontido está em [examples/demo-rnaseq](examples/demo-rnaseq).

## Desenvolvimento

```bash
make install
make test
make lint
make demo
```

Validação completa de release Docker:

```bash
python -m pip install -e '.[web,dev]'
pytest -q
ruff check .
cd frontend && npm install && npm run build
cd ..
docker compose build
docker compose up -d
curl -f http://localhost:8969/api/v1/health
bash scripts/e2e-smoke.sh
docker compose ps
docker compose down
grep -rI 'sk-' . || echo 'OK: sem chaves'
```

## Público-alvo

O projeto é pensado inicialmente para:

- Bioinformatas que precisam executar pipelines reprodutíveis.
- Pesquisadores em ciências da vida que usam workflows computacionais.
- Estudantes que querem aprender boas práticas de bioinformática operacional.
- Equipes de infraestrutura científica que precisam padronizar execuções.
- Projetos open source que desejam documentação e auditoria desde o início.

## Escopo atual

A v0.2.0 entrega:

1. Criar a estrutura de um projeto BioStack.
2. Validar se o ambiente possui dependências essenciais.
3. Executar ou simular workflows básicos via Nextflow.
4. Capturar metadados de execução.
5. Registrar versões, parâmetros, logs e checksums.
6. Gerar relatório HTML e JSON.
7. Visualizar projetos e relatórios em painel web local e frontend Docker.
8. Persistir projetos/runs/eventos em PostgreSQL.
9. Processar jobs por worker Redis simples.
10. Explicar falhas operacionais com IA opcional limitada a troubleshooting técnico.

## Roadmap

- v0.1.x: MVP local-first com CLI, relatórios, painel local e IA operacional mock.
- v0.2.0: Docker Platform Edition com backend/API, banco, fila, worker, frontend separado, reverse proxy, hardening e documentação operacional.
- Futuro: autenticação, cloud, registry de imagens, HPC/SLURM, Apptainer, observabilidade avançada, multiusuário, RBAC e institucionalização.

## Fora do escopo atual

Para manter a plataforma realista, a v0.2.0 não inclui:

- Kubernetes.
- HPC/SLURM.
- Apptainer.
- Autenticação robusta.
- Multiusuário avançado.
- RBAC.
- IA interpretando resultados biológicos.
- Diagnóstico clínico.
- Execução distribuída ou simultânea complexa de muitos workflows.

## Documentação

- [Arquitetura](docs/architecture.md)
- [Instalação](docs/installation.md)
- [Demo do MVP](docs/demo.md)
- [Relatórios](docs/reports.md)
- [Painel web local](docs/web-ui.md)
- [API FastAPI versionada](docs/api.md)
- [Persistência PostgreSQL](docs/database.md)
- [IA operacional e troubleshooting](docs/ai-troubleshooting.md)
- [Docker Platform Edition](docs/docker-platform.md)
- [Validação end-to-end](docs/e2e.md)
- [Segurança operacional](docs/security.md)
- [Performance operacional](docs/performance.md)
- [Backup e restore](docs/backup-restore.md)
- [Troubleshooting Docker](docs/troubleshooting-docker.md)
- [Audit log](docs/audit-log.md)
- [Changelog](CHANGELOG.md)

## Estado atual

Este repositório está preparando o release v0.2.0 Docker Platform Edition: CLI preservada, API, banco, fila, worker, frontend, Nginx, hardening operacional, documentação de segurança/performance/backup/troubleshooting e fluxo end-to-end obrigatório.

## Licença

Este projeto é distribuído sob a licença Apache-2.0. Consulte o arquivo [LICENSE](LICENSE).
