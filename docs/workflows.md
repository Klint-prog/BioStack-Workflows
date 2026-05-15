# Workflows disponíveis

O BioStack Workflows passa a manter mais de um workflow demonstrativo para validar a reutilização da arquitetura de templates, configuração, execução Nextflow e geração de evidências auditáveis.

## rnaseq-basic

`rnaseq-basic` é o workflow inicial do BioStack Workflows para validar a execução operacional com Nextflow.

### Objetivo

A fase 03 não entrega uma análise RNA-seq científica completa. Ela entrega a base auditável para execução:

- resolução do workflow configurado em `biostack.yml`;
- montagem segura do comando Nextflow como lista de argumentos;
- suporte aos profiles `local` e `docker`;
- modo `--dry-run` sem dependência de Nextflow instalado;
- criação de logs em `logs/<run_id>.log`.

### Comandos

```bash
biostack init demo-rna --template rnaseq-basic
cd demo-rna
biostack run --dry-run
biostack run --dry-run --workflow rnaseq-basic --profile local
```

Para execução real:

```bash
biostack run --workflow rnaseq-basic --profile local
```

Se Nextflow não estiver instalado, o comando real retorna uma mensagem amigável orientando o uso de `--dry-run`.

### Limite científico

O processo `FASTQC_DEMO` usa `echo` como placeholder. Ele serve para testar orquestração, logs e reprodutibilidade operacional. Não deve ser usado como evidência de controle de qualidade real de RNA-seq.

## variant-calling-basic

`variant-calling-basic` é o segundo workflow demonstrativo do BioStack Workflows. Ele foi adicionado para provar que a arquitetura suporta múltiplos domínios de workflow sem transformar o MVP em uma plataforma clínica completa.

### Objetivo

Este workflow valida:

- criação de projeto com `biostack init <nome> --template variant-calling-basic`;
- validação Pydantic do novo template em `biostack.yml`;
- resolução do workflow `workflows/variant-calling-basic`;
- compatibilidade com os profiles `local` e `docker`;
- documentação explícita de limites científicos e clínicos.

### Comandos

```bash
biostack init demo-vc --template variant-calling-basic
cd demo-vc
biostack run --dry-run
biostack run --dry-run --workflow variant-calling-basic --profile local
```

Para execução real:

```bash
biostack run --workflow variant-calling-basic --profile local
```

### Dados esperados

O workflow demonstrativo procura arquivos `.bam`, `.cram`, `.vcf` ou `.vcf.gz` em `data/raw/` e usa `data/reference/reference.fa` como referência padrão declarativa.

### Limite científico e clínico

`variant-calling-basic` não é pipeline clínico, diagnóstico ou científico validado. Ele não executa alinhamento real, chamada real de variantes, filtragem, anotação, controle de qualidade clínico nem interpretação biológica. O processo `VARIANT_CALLING_DEMO` usa `echo` como placeholder auditável e deve ser substituído por etapas validadas em qualquer uso científico ou operacional real.
