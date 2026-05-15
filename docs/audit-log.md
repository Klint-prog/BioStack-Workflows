# Audit log

Este arquivo registra decisões, correções e inconsistências relevantes ao longo do desenvolvimento do BioStack Workflows.

## phase_00 — Fundação estratégica e repositório base

- Decisão: iniciar o projeto com foco em documentação, licença, governança e estrutura mínima.
- Decisão: não implementar código Python nesta fase.
- Decisão: manter o MVP restrito a CLI, Nextflow, Docker e relatórios reprodutíveis.
- Decisão: usar Apache-2.0 como licença inicial.
- Observação: banco de dados não será usado no MVP inicial salvo necessidade técnica posterior.

## phase_01 — Pacote Python e CLI mínima

- Decisão: criar pacote Python instalável via `pyproject.toml` usando Setuptools como backend de build para maximizar compatibilidade em CI e ambientes locais.
- Decisão: centralizar a versão em `biostack/__init__.py` e expor `biostack version` via Typer.
- Decisão: implementar `biostack doctor` como diagnóstico tolerante, sem falhar quando Docker ou Nextflow não estão instalados.
- Decisão: manter a detecção de ambiente em `biostack/core/system.py` para separar CLI de lógica de sistema.
- Decisão: adicionar CI mínimo com GitHub Actions executando `pytest -q` em Python 3.11.

## phase_02 — Inicialização de projetos BioStack

- Decisão: implementar `biostack init` como comando direto da CLI principal para manter a experiência `biostack init <name> --template rnaseq-basic` simples.
- Decisão: validar `biostack.yml` com Pydantic imediatamente após renderizar o template, garantindo que o projeto recém-criado já nasça auditável.
- Decisão: limitar o template inicial a `rnaseq-basic`, deixando claro que ele prepara estrutura e metadados, mas ainda não executa pipeline científico de produção.
- Decisão: proteger sobrescrita recusando diretórios existentes sem `--force`; quando `--force` é usado, o diretório do projeto é recriado integralmente.
- Decisão: registrar templates Jinja2 como package data para manter o comando funcional também após instalação do pacote.

## phase_03 — Workflow RNA-seq básico com Nextflow

- Decisão: implementar `biostack run` como comando direto da CLI principal, mantendo a experiência `biostack run --dry-run` simples dentro do projeto criado por `biostack init`.
- Decisão: construir o comando Nextflow como lista de argumentos em `biostack/core/runner.py`, evitando interpolação insegura de shell.
- Decisão: fazer `--dry-run` criar log em `logs/<run_id>.log` e exibir o comando sem exigir Nextflow instalado, permitindo auditoria em ambientes incompletos.
- Decisão: resolver workflows primeiro em `workflows/<nome>` dentro do projeto e depois em `workflows/<nome>` do repositório/pacote em modo editável.
- Decisão: criar `rnaseq-basic` como pipeline demonstrativo com `FASTQC_DEMO` usando `echo`, documentando explicitamente que ainda não é análise científica validada.
- Decisão: tratar ausência de Nextflow com mensagem amigável e sem traceback bruto para o usuário final.

## phase_04 — Rastreabilidade, metadados e relatórios

- Decisão: mover a geração de `run_id` para `biostack/core/metadata.py`, mantendo o formato ordenável com timestamp UTC e sufixo aleatório.
- Decisão: cada execução com projeto carregado gera JSON e HTML em `reports/<run_id>.*`, inclusive `--dry-run`, ausência de Nextflow e retorno Nextflow diferente de zero.
- Decisão: preservar logs consolidados no JSON para auditoria, mantendo o arquivo original em `logs/<run_id>.log` como evidência operacional.
- Decisão: calcular checksums SHA256 por streaming e limitar a coleta inicial aos arquivos de entrada compatíveis em `data/raw/` para evitar varreduras amplas no MVP.
- Decisão: resolver `biostack report --run latest` de forma determinística lendo `started_at` dos JSONs e usando o nome do arquivo como desempate.
- Observação: erros antes de identificar um projeto BioStack válido, como ausência de `biostack.yml`, não geram relatório porque ainda não há configuração confiável de armazenamento.

## phase_05 — Release público v0.1.0

- Decisão: não adicionar funcionalidades novas nesta fase; a fase consolida instalação, documentação, exemplo público, Makefile, CI e apresentação do MVP.
- Decisão: manter `version = "0.1.0"` no `pyproject.toml` e `__version__ = "0.1.0"` no pacote para alinhar release e CLI.
- Decisão: adicionar Ruff ao extra `dev` e ao CI como verificação separada de lint, preservando o job de testes.
- Decisão: criar o extra `web` vazio como preparação declarativa, sem implementar painel web ou dependências futuras.
- Decisão: documentar o workflow `rnaseq-basic` como demonstração operacional, não como pipeline científico validado.
- Decisão: criar `Makefile` com targets mínimos (`install`, `test`, `lint`, `clean`, `demo`) para padronizar revisão humana e CI local.
- Observação: há conflito textual no JSON da fase: uma tarefa pede criar/enviar tag, mas `github_push_requirement.extra_steps` diz que a IA não cria tags diretamente. Foi adotada a regra mais restritiva: a PR prepara o release e a tag `v0.1.0` fica pendente para o humano após aprovação e merge.

## phase_06 — Segundo workflow: variant-calling básico

- Decisão: adicionar `variant-calling-basic` como segundo workflow demonstrativo para provar reusabilidade da arquitetura sem introduzir pipeline clínico completo.
- Decisão: manter o scaffold genérico existente em `biostack/templates/`, pois `biostack.yml.j2` e `project_README.md.j2` já recebem `template` por contexto e não exigem duplicação por workflow.
- Decisão: ampliar a validação Pydantic com um alias `TemplateName` contendo `rnaseq-basic` e `variant-calling-basic`, mantendo `SUPPORTED_TEMPLATES` como fonte simples para validação do scaffolder.
- Decisão: documentar explicitamente que `variant-calling-basic` não realiza alinhamento, chamada real de variantes, anotação, controle de qualidade clínico ou interpretação biológica.
- Decisão: criar testes focados em ambos os templates para evitar regressão no `rnaseq-basic` ao adicionar novos workflows.
- Observação: a verificação `git tag | grep v0.1.0` foi tentada via ref `v0.1.0` no GitHub e retornou `No commit found for the ref v0.1.0`; a inconsistência já havia sido prevista na phase_05 como pendência humana de tag.

## phase_07 — Painel web local simples

- Decisão: implementar o painel como extra opcional `web`, preservando o funcionamento da CLI sem FastAPI/Uvicorn instalados.
- Decisão: manter a interface local, simples e sem autenticação, evitando falsa sensação de segurança e escopo multiusuário.
- Decisão: reaproveitar relatórios HTML/JSON existentes em `reports/`, sem duplicar a camada de geração de relatórios.
- Decisão: descobrir projetos apenas no diretório atual e subdiretórios imediatos para evitar varreduras amplas no filesystem.
- Decisão: usar FastAPI + Jinja2 e manter HTMX fora do caminho crítico, sem React/Webpack/frontend pesado.

## phase_08 — IA operacional e troubleshooting

- Decisão: adicionar IA apenas como camada opcional de troubleshooting técnico sobre logs e metadados, sem interpretação biológica ou clínica.
- Decisão: exibir o aviso `AVISO: Não usar para diagnóstico ou interpretação clínica.` em toda execução de `biostack explain`, inclusive em falhas amigáveis.
- Decisão: criar uma interface abstrata `LLMProvider` e um provider `mock` determinístico para testes sem rede, sem chave de API e sem dependência externa.
- Decisão: manter a configuração de provider real por variável de ambiente `BIOSTACK_LLM_API_KEY`, sem gravar chaves no repositório.
- Decisão: limitar logs enviados ao prompt aos últimos 12.000 caracteres, preservando simplicidade e reduzindo risco de prompts excessivos no MVP.
- Observação: o provider real `env` valida a presença de chave, mas a chamada externa concreta permanece fora do MVP inicial; o projeto segue funcional sem IA.

## phase_09 — Docker base e Compose

- Decisão: criar a primeira base Docker da v0.2.0 como container de backend/CLI, sem API nova, banco, fila, worker, frontend ou reverse proxy.
- Decisão: usar `python:3.11-slim` e instalar o pacote em modo editável com extras `[web,dev]` para manter compatibilidade com os testes e com o painel local já existente.
- Decisão: montar o volume nomeado `biostack_data` em `/workspace`, preservando projetos, logs e relatórios gerados dentro do container.
- Decisão: manter o serviço Compose com o nome `backend`, alinhado aos comandos mínimos da fase (`docker compose run --rm backend ...`).
- Decisão: adicionar `.env.example` sem segredos reais e `.dockerignore` para reduzir contexto de build e evitar envio acidental de ambientes locais.
- Observação: Postgres, Redis, worker, API FastAPI versionada, frontend React e Nginx permanecem explicitamente fora desta fase.

## phase_10 — API FastAPI versionada

- Decisão: criar a API mínima em `/api/v1`, preservando a CLI e o painel web local existentes.
- Decisão: usar `BIOSTACK_WORKSPACE` como raiz de filesystem da API, com descoberta limitada ao workspace e subdiretórios imediatos.
- Decisão: reaproveitar `create_project`, `run_workflow`, geração de relatórios e provider mock existentes, evitando duplicar regra de negócio da CLI.
- Decisão: manter execução de runs síncrona e recomendada como dry-run nesta fase; fila, worker e Redis permanecem fora do escopo.
- Decisão: adicionar serviço Compose `api` com Uvicorn e preservar o serviço `backend` para validação da CLI.
- Observação: PostgreSQL, Redis, worker assíncrono, frontend React, Nginx e autenticação robusta permanecem explicitamente fora desta fase.

## phase_11 — PostgreSQL e modelos persistentes

- Decisão: adicionar PostgreSQL 16 ao Compose com healthcheck e volume próprio, sem introduzir Redis, worker assíncrono, frontend React ou Nginx.
- Decisão: manter a CLI local-first sem exigir banco; a persistência entra pela API e por helpers de banco isolados em `biostack/db`.
- Decisão: usar SQLAlchemy 2.x, Psycopg 3 e Alembic; testes usam SQLite temporário para viabilizar execução rápida sem serviço externo.
- Decisão: persistir `Project`, `Run`, `RunEvent`, `RunFile` e `AuditEvent`, preservando relatórios HTML/JSON e logs no filesystem.
- Decisão: exigir migrations via Alembic antes de operar a API em Compose; testes criam schema explicitamente para isolamento.
- Observação: a migration e os modelos usam tipos portáveis para JSON/UUID, mapeando JSONB/UUID no PostgreSQL e JSON/CHAR em SQLite.

## phase_12 — Worker com Redis/fila

- Decisão: usar uma fila mínima baseada em Redis lists (`LPUSH`/`BRPOP`) em vez de RQ, Dramatiq ou Celery para manter a implementação simples, auditável e sem orquestração distribuída.
- Decisão: `POST /api/v1/runs` agora cria `Run` com status `QUEUED`, registra eventos e enfileira um job; a execução real fica a cargo do serviço `worker`.
- Decisão: o worker atualiza o ciclo `QUEUED` → `RUNNING` → `SUCCEEDED`/`FAILED`, preservando logs e relatórios no filesystem compartilhado.
- Decisão: a CLI continua usando o fluxo síncrono existente via `run_workflow`; a função `run_workflow_with_run_id` foi adicionada para o worker preservar o `run_id` já registrado no banco.
- Decisão: o Compose adiciona Redis 7 e serviço `worker`, sem frontend React, sem Nginx e sem autenticação robusta nesta fase.
- Observação: o worker não monta Docker socket. Se execução real com Nextflow/Docker exigir `/var/run/docker.sock`, o risco deve ser reavaliado porque isso concede controle elevado sobre o host Docker.

## phase_15 — Hardening, performance e documentação

- Decisão: tratar esta fase como finalização da v0.2.0 Docker Platform Edition, sem adicionar cloud, Kubernetes, autenticação complexa, HPC/SLURM, Apptainer, RBAC ou multiusuário avançado.
- Decisão: preservar a CLI atual e atuar de forma incremental sobre Dockerfiles, Compose, logging, CORS e documentação operacional.
- Decisão: executar containers Python (`backend`, `api`, `worker`) como usuário não-root `biostack`, mantendo `/workspace` gravável pelo serviço.
- Decisão: aplicar hardening básico no Compose com healthchecks adicionais, `restart: unless-stopped`, `no-new-privileges`, rotação de logs e portas parametrizadas.
- Decisão: manter o Docker socket fora dos containers e documentar o risco explicitamente em `docs/security.md`.
- Decisão: configurar CORS por `BIOSTACK_CORS_ORIGINS`, evitando wildcard como padrão.
- Decisão: configurar logging previsível para API e worker via `BIOSTACK_LOG_LEVEL`.
- Decisão: documentar backup/restore, troubleshooting Docker, performance e checklist de segurança como critérios de release.
- Observação: o ambiente de execução da IA não conseguiu clonar o repositório por falha de DNS externo; as alterações e PR foram feitas via conector GitHub. Testes que exigem Docker/local checkout devem ser validados pelo humano ou CI.

## phase_16 — UX operacional real da plataforma

- Decisão: atuar de forma incremental no frontend React/Vite, sem alterar schema de banco, autenticação, RBAC, Kubernetes, cloud, HPC/SLURM, Apptainer ou pipelines científicos pesados.
- Decisão: usar apenas endpoints reais já existentes: `/api/v1/health`, `/api/v1/projects`, `/api/v1/runs`, `/api/v1/reports` e `/api/v1/explain`.
- Decisão: remover rótulos antigos da UI e apresentar a interface como `BioStack Workflows · Docker Platform Edition v0.2.0`.
- Decisão: adicionar dashboard operacional com healthcheck, totais reais, runs por status, última execução e última atualização.
- Decisão: melhorar criação e listagem de projetos com validação visual, loading, sucesso, erro, seleção ativa e ações operacionais.
- Decisão: adicionar polling simples no frontend a cada 8 segundos enquanto houver run `QUEUED` ou `RUNNING`.
- Decisão: listar relatórios e abrir JSON pela API; quando `html_path` existir, exibir o caminho como metadado sem inventar endpoint estático.
- Decisão: manter Explain no provider `mock` por padrão e exibir aviso obrigatório contra diagnóstico ou interpretação clínica.
- Observação: o ambiente de execução da IA não conseguiu clonar o repositório por falha de DNS externo; as alterações e PR foram feitas via conector GitHub. Testes locais Docker/frontend devem ser validados pelo humano ou CI.
