# BioStack Workflows

BioStack Workflows é uma infraestrutura open source para criar, executar, documentar e auditar workflows de bioinformática reprodutíveis.

## Visão

A visão do projeto é oferecer uma camada simples, auditável e extensível para pesquisadores, estudantes, analistas de bioinformática e equipes técnicas que precisam executar pipelines científicos com rastreabilidade operacional.

O projeto começa pequeno: uma CLI em Python capaz de preparar um projeto BioStack, validar o ambiente, executar workflows com Nextflow e Docker, e gerar relatórios reprodutíveis em HTML e JSON.

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
- Jinja2 para geração de relatórios.
- PyYAML para configuração declarativa.
- Nextflow como motor de workflow científico.
- Docker e Docker Compose para reprodutibilidade de ambiente.
- Relatórios HTML e JSON com metadados, versões, parâmetros, logs e checksums.

## Público-alvo

O projeto é pensado inicialmente para:

- Bioinformatas que precisam executar pipelines reprodutíveis.
- Pesquisadores em ciências da vida que usam workflows computacionais.
- Estudantes que querem aprender boas práticas de bioinformática operacional.
- Equipes de infraestrutura científica que precisam padronizar execuções.
- Projetos open source que desejam documentação e auditoria desde o início.

## Escopo do MVP

O MVP deve entregar uma CLI capaz de:

1. Criar a estrutura de um projeto BioStack.
2. Validar se o ambiente possui dependências essenciais.
3. Executar um workflow RNA-seq básico via Nextflow e Docker.
4. Capturar metadados de execução.
5. Registrar versões, parâmetros, logs e checksums.
6. Gerar relatório HTML e JSON.

## Instalação local para desenvolvimento

Pré-requisitos mínimos:

- Python 3.11 ou superior.
- `pip` atualizado.

Instalação em modo editável:

```bash
python -m pip install -e .
```

Com dependências de desenvolvimento:

```bash
python -m pip install -e ".[dev]"
```

Comandos iniciais da CLI:

```bash
biostack --help
biostack version
biostack doctor
```

Criar o primeiro projeto BioStack:

```bash
biostack init demo --template rnaseq-basic
cd demo
cat biostack.yml
```

O comando cria uma estrutura local padronizada com `data/raw`, `data/reference`, `workflows`, `results`, `reports`, `logs`, `config`, `biostack.yml` e `README.md`. Por segurança, uma execução repetida recusa sobrescrever o diretório existente; use `--force` apenas quando quiser recriar o projeto.

Simular a execução do workflow RNA-seq básico:

```bash
cd demo
biostack run --dry-run
biostack run --dry-run --workflow rnaseq-basic --profile local
```

Executar o workflow real, quando Nextflow estiver instalado:

```bash
biostack run --workflow rnaseq-basic --profile local
```

O `--dry-run` mostra o comando Nextflow sem executar e cria um log em `logs/<run_id>.log`, útil para auditoria em ambientes onde Nextflow ainda não está instalado.

Executar testes:

```bash
pytest -q
```

## Fora do escopo inicial

Para manter o MVP realista, o projeto não deve iniciar com:

- Painel web complexo.
- Kubernetes.
- IA interpretando resultados biológicos.
- HPC/SLURM.
- Multiusuário.
- Execução simultânea de muitos workflows.

## Estado atual

Este repositório está na fase 03: CLI instalável com `biostack init` e `biostack run`, incluindo workflow demonstrativo `rnaseq-basic` com Nextflow, perfis `local` e `docker`, dry-run auditável e logs por execução.

## Licença

Este projeto é distribuído sob a licença Apache-2.0. Consulte o arquivo [LICENSE](LICENSE).
