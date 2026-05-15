# BioStack Workflows

[![CI](https://github.com/Klint-prog/BioStack-Workflows/actions/workflows/ci.yml/badge.svg)](https://github.com/Klint-prog/BioStack-Workflows/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

BioStack Workflows é uma infraestrutura open source para criar, executar, documentar e auditar workflows de bioinformática reprodutíveis.

## Visão

A visão do projeto é oferecer uma camada simples, auditável e extensível para pesquisadores, estudantes, analistas de bioinformática e equipes técnicas que precisam executar pipelines científicos com rastreabilidade operacional.

O projeto começa pequeno: uma CLI em Python capaz de preparar um projeto BioStack, validar o ambiente, executar workflows com Nextflow e Docker, e gerar relatórios reprodutíveis em HTML e JSON.

## O que existe no v0.1.0

O release público v0.1.0 consolida o MVP local-first:

- CLI instalável com `biostack --help`, `biostack version`, `biostack doctor`, `biostack init`, `biostack run`, `biostack report` e `biostack web`.
- Templates `rnaseq-basic` e `variant-calling-basic` para criar estruturas auditáveis de projeto.
- Execução real ou simulada via Nextflow, com `--dry-run` para ambientes sem Nextflow.
- Relatórios HTML e JSON com metadados, versões, parâmetros, logs e checksums SHA256 dos inputs.
- Painel web local experimental e opcional para visualizar projetos, execuções e relatórios sem substituir a CLI.
- CI com testes automatizados e lint usando Ruff.
- Documentação de instalação, demo, relatórios e painel web local.

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
- FastAPI e Uvicorn como dependências opcionais do painel web local.
- Relatórios HTML e JSON com metadados, versões, parâmetros, logs e checksums.

## Instalação

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

Com dependências de desenvolvimento:

```bash
python -m pip install -e ".[dev]"
```

Com dependências opcionais do painel web local:

```bash
python -m pip install -e ".[web]"
```

Com desenvolvimento e painel web:

```bash
python -m pip install -e ".[web,dev]"
```

Consulte [docs/installation.md](docs/installation.md) para detalhes e solução de problemas.

## Quickstart

```bash
biostack --help
biostack doctor
biostack init demo --template rnaseq-basic
cd demo
biostack run --dry-run
biostack report --run latest
```

O `--dry-run` mostra o comando Nextflow sem executar e cria evidências auditáveis em `logs/` e `reports/`.

Para executar o workflow real, instale Nextflow e Docker e rode:

```bash
biostack run --workflow rnaseq-basic --profile docker
```

## Painel web local experimental

O painel web é opcional, experimental, local e sem autenticação. Ele serve para revisar projetos e relatórios já gerados pela CLI, não para substituir o fluxo de terminal.

```bash
python -m pip install -e ".[web]"
biostack web --host 127.0.0.1 --port 8000
```

Depois acesse `http://127.0.0.1:8000/` em um navegador local. Não exponha esse servidor em redes públicas.

Leia mais em [docs/web-ui.md](docs/web-ui.md).

## Demo

Leia o walkthrough completo em [docs/demo.md](docs/demo.md). Um exemplo autocontido está em [examples/demo-rnaseq](examples/demo-rnaseq).

## Desenvolvimento

```bash
make install
make test
make lint
make demo
```

Os mesmos comandos são usados como referência para validar o release público.

## Público-alvo

O projeto é pensado inicialmente para:

- Bioinformatas que precisam executar pipelines reprodutíveis.
- Pesquisadores em ciências da vida que usam workflows computacionais.
- Estudantes que querem aprender boas práticas de bioinformática operacional.
- Equipes de infraestrutura científica que precisam padronizar execuções.
- Projetos open source que desejam documentação e auditoria desde o início.

## Escopo do MVP

O MVP entrega uma CLI capaz de:

1. Criar a estrutura de um projeto BioStack.
2. Validar se o ambiente possui dependências essenciais.
3. Executar ou simular workflows básicos via Nextflow.
4. Capturar metadados de execução.
5. Registrar versões, parâmetros, logs e checksums.
6. Gerar relatório HTML e JSON.
7. Visualizar projetos e relatórios em painel web local opcional.

## Roadmap

- v0.1.x: estabilização do MVP, documentação e ajustes de empacotamento.
- v0.2.0: segundo template/workflow para provar extensibilidade sem duplicação.
- Futuro: parâmetros mais ricos, exemplos com dados públicos pequenos, integração opcional com armazenamento remoto e melhorias de auditoria.

## Fora do escopo inicial

Para manter o MVP realista, o projeto não deve iniciar com:

- Painel web complexo.
- Kubernetes.
- IA interpretando resultados biológicos.
- HPC/SLURM.
- Multiusuário.
- Execução simultânea de muitos workflows.

## Documentação

- [Arquitetura](docs/architecture.md)
- [Instalação](docs/installation.md)
- [Demo do MVP](docs/demo.md)
- [Relatórios](docs/reports.md)
- [Painel web local](docs/web-ui.md)
- [Audit log](docs/audit-log.md)
- [Changelog](CHANGELOG.md)

## Estado atual

Este repositório está no release público v0.1.0 do MVP: CLI, init, run, report, painel web local opcional, rastreabilidade básica, relatórios HTML/JSON, CI com testes e lint, documentação mínima e exemplo de demo.

## Licença

Este projeto é distribuído sob a licença Apache-2.0. Consulte o arquivo [LICENSE](LICENSE).
