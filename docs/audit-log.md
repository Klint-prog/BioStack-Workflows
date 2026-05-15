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
