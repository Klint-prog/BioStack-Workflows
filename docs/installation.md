# Instalação

Este guia descreve a instalação local do BioStack Workflows v0.1.0 para uso e desenvolvimento.

## Pré-requisitos mínimos

- Linux, macOS ou ambiente compatível com Python 3.11+.
- Python 3.11 ou superior.
- `pip` atualizado.
- Git, caso a instalação seja feita a partir do repositório.

## Pré-requisitos para execução real de workflows

O MVP funciona em modo de auditoria sem Nextflow por meio de `biostack run --dry-run`. Para executar workflows reais, instale também:

- Nextflow disponível no `PATH`.
- Docker disponível no `PATH` quando usar o profile `docker`.

Valide o ambiente com:

```bash
biostack doctor
```

## Instalação para uso local

Clone o repositório e instale em modo editável:

```bash
git clone https://github.com/Klint-prog/BioStack-Workflows.git
cd BioStack-Workflows
python -m pip install -e .
```

Confirme a instalação:

```bash
biostack --help
biostack version
```

## Instalação para desenvolvimento

Use o extra `dev` para instalar ferramentas de teste e lint:

```bash
python -m pip install -e ".[dev]"
```

Depois rode:

```bash
make test
make lint
```

## Quickstart pós-instalação

```bash
biostack init demo --template rnaseq-basic
cd demo
biostack run --dry-run
biostack report --run latest
```

Arquivos gerados:

- `logs/<run_id>.log`
- `reports/<run_id>.json`
- `reports/<run_id>.html`

## Solução de problemas

### `biostack: command not found`

A instalação editável provavelmente não foi concluída no ambiente Python ativo. Rode novamente:

```bash
python -m pip install -e ".[dev]"
```

Se estiver usando ambiente virtual, ative-o antes de instalar.

### `Nextflow não foi encontrado no PATH`

Use `biostack run --dry-run` para auditar o comando sem executar. Para execução real, instale Nextflow e confirme:

```bash
nextflow -version
```

### Docker ausente

O profile `docker` exige Docker instalado e acessível. Confirme:

```bash
docker --version
```

Para testes rápidos sem container, use o profile `local` quando Nextflow estiver instalado:

```bash
biostack run --workflow rnaseq-basic --profile local
```

### Diretório de projeto já existe

`biostack init` não sobrescreve diretórios por padrão. Use outro nome ou recrie explicitamente:

```bash
biostack init demo --template rnaseq-basic --force
```

### Nenhum input encontrado

O MVP procura arquivos em `data/raw/` com extensões `.fastq`, `.fq`, `.fastq.gz` ou `.fq.gz`. Em `--dry-run`, isso não bloqueia a geração de relatório; apenas registra a lista de checksums como vazia.
