# Roadmap por fases

## phase_00 — Fundação estratégica e repositório base

Criar documentação, licença, governança, código de conduta, arquitetura inicial, roadmap, audit log, `.gitignore` e estrutura mínima de diretórios.

## phase_01 — Pacote Python e CLI mínima

Criar `pyproject.toml`, pacote `biostack/`, CLI com Typer, comandos iniciais `version` e `doctor`, além de testes básicos.

## phase_02 — Configuração declarativa do projeto

Definir arquivos de configuração YAML, schemas com Pydantic e validação estrutural dos projetos BioStack.

## phase_03 — Criação de projeto BioStack

Implementar comando para inicializar um projeto BioStack com diretórios, arquivos de configuração e exemplos mínimos.

## phase_04 — Integração inicial com Nextflow

Adicionar workflow Nextflow mínimo, validação de presença do Nextflow e execução controlada via CLI.

## phase_05 — Integração com Docker

Padronizar execução containerizada, validar Docker/Docker Compose e documentar requisitos de ambiente.

## phase_06 — Workflow RNA-seq básico

Adicionar pipeline RNA-seq inicial com parâmetros controlados e saídas rastreáveis.

## phase_07 — Relatórios reprodutíveis

Gerar relatórios HTML e JSON com metadados, versões, parâmetros, logs, checksums e resumo de execução.

## phase_08 — CI, empacotamento e preparação comunitária

Adicionar GitHub Actions, checks automatizados, documentação final do MVP, empacotamento e preparação para contribuições externas.
