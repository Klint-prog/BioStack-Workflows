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
