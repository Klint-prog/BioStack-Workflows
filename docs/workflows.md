# Workflows disponíveis

## rnaseq-basic

`rnaseq-basic` é o workflow inicial do BioStack Workflows para validar a execução operacional com Nextflow.

### Objetivo da fase atual

A fase 03 não entrega uma análise RNA-seq científica completa. Ela entrega a base auditável para execução:

- resolução do workflow configurado em `biostack.yml`;
- montagem segura do comando Nextflow como lista de argumentos;
- suporte aos profiles `local` e `docker`;
- modo `--dry-run` sem dependência de Nextflow instalado;
- criação de logs em `logs/<run_id>.log`.

### Comandos

```bash
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
