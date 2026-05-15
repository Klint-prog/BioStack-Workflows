# Demo RNA-seq básica

Este exemplo mostra uma configuração mínima do BioStack Workflows para o template `rnaseq-basic`.

O objetivo é demonstrar a camada operacional do MVP:

- configuração declarativa em `biostack.yml`;
- execução simulada com `biostack run --dry-run`;
- geração de logs;
- geração de relatórios JSON e HTML;
- rastreabilidade de versões, parâmetros e checksums.

## Como usar

A partir da raiz do repositório instalado:

```bash
python -m pip install -e ".[dev]"
biostack init demo --template rnaseq-basic
cd demo
biostack run --dry-run
biostack report --run latest
```

Compare o arquivo `biostack.yml` criado com o exemplo deste diretório.

## Dados de entrada

Coloque arquivos FASTQ pequenos em `data/raw/` caso queira testar checksums:

```bash
mkdir -p data/raw
printf '@read1\nACGT\n+\n!!!!\n' > data/raw/sample.fastq
biostack run --dry-run
```

O relatório JSON resultante deve listar `data/raw/sample.fastq` com SHA256 e tamanho em bytes.

## Observação

O workflow `rnaseq-basic` é demonstrativo. Ele valida o fluxo operacional do BioStack, mas não executa uma análise RNA-seq científica completa.
