# Workflow rnaseq-basic

`rnaseq-basic` é o primeiro workflow demonstrativo do BioStack Workflows. Ele existe para validar a integração operacional entre a CLI `biostack run`, Nextflow, perfis locais/Docker, logs e estrutura de projeto.

## O que este pipeline faz

- Procura arquivos FASTQ em `data/raw/`.
- Executa um processo demonstrativo chamado `FASTQC_DEMO`.
- Gera arquivos texto em `results/<run_id>/fastqc/` com metadados mínimos da execução.

## O que este pipeline não faz

Este workflow ainda não é uma análise RNA-seq científica validada. O processo `FASTQC_DEMO` usa `echo` como placeholder auditável no lugar de uma execução real do FastQC. A validação biológica, métricas reais de qualidade, alinhamento, contagem e análise diferencial ficam fora desta fase.

## Execução

Dentro de um projeto criado por `biostack init`:

```bash
biostack run --dry-run
biostack run --dry-run --workflow rnaseq-basic --profile local
```

Para execução real, instale Nextflow. Para o profile `docker`, Docker também precisa estar disponível.

```bash
biostack run --workflow rnaseq-basic --profile local
```

## Dados de teste

Consulte `test-data/README.md` para criar um FASTQ mínimo de demonstração.
