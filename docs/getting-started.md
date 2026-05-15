# Getting started

Este guia mostra como criar o primeiro projeto local com BioStack Workflows.

## 1. Instalar o pacote em modo editável

```bash
python -m pip install -e ".[dev]"
```

## 2. Verificar a CLI

```bash
biostack --help
biostack version
biostack doctor
```

## 3. Criar um projeto RNA-seq básico

```bash
biostack init demo --template rnaseq-basic
```

O comando cria o diretório `demo/` com:

```text
demo/
├── biostack.yml
├── README.md
├── config/
├── data/
│   ├── raw/
│   └── reference/
├── logs/
├── reports/
├── results/
└── workflows/
```

## 4. Validar a configuração gerada

O arquivo `demo/biostack.yml` é renderizado via Jinja2 e validado por Pydantic durante a criação do projeto. Se a validação falhar, o comando retorna erro.

## 5. Proteção contra sobrescrita

Uma segunda execução sem `--force` é recusada:

```bash
biostack init demo --template rnaseq-basic
```

Para recriar o diretório conscientemente:

```bash
biostack init demo --template rnaseq-basic --force
```

Use `--force` com cuidado, pois ele remove e recria o diretório do projeto informado.
