# Workflow variant-calling-basic

`variant-calling-basic` é o segundo workflow demonstrativo do BioStack Workflows. Ele existe para provar que a arquitetura de templates e workflows suporta mais de um domínio sem duplicação excessiva.

## O que este pipeline faz

- Procura arquivos BAM, CRAM, VCF ou VCF.GZ em `data/raw/`.
- Usa `data/reference/reference.fa` como referência padrão declarativa.
- Executa um processo demonstrativo chamado `VARIANT_CALLING_DEMO`.
- Gera arquivos texto em `results/<run_id>/variants/` com metadados mínimos da execução.

## O que este pipeline não faz

Este workflow não é um pipeline clínico, diagnóstico ou científico validado para variant calling. Ele não executa alinhamento, recalibração, chamada real de variantes, filtragem, anotação, controle de qualidade clínico, geração de VCF validado ou interpretação biológica.

O processo `VARIANT_CALLING_DEMO` usa `echo` como placeholder auditável. Em produção, essa etapa deveria ser substituída por ferramentas e parâmetros validados, como BWA, Samtools, BCFtools, FreeBayes, GATK ou outras ferramentas adequadas ao protocolo científico.

## Execução

Dentro de um projeto criado por `biostack init`:

```bash
biostack run --dry-run
biostack run --dry-run --workflow variant-calling-basic --profile local
```

Para execução real, instale Nextflow. Para o profile `docker`, Docker também precisa estar disponível.

```bash
biostack run --workflow variant-calling-basic --profile local
```

## Dados de teste

Para uma simulação operacional, coloque arquivos `.bam`, `.cram`, `.vcf` ou `.vcf.gz` em `data/raw/`. O modo `--dry-run` funciona mesmo sem dados reais, pois o objetivo inicial é auditar resolução de workflow, parâmetros, logs e relatórios.
