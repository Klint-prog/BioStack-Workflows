# Dados mínimos de teste

Crie um arquivo FASTQ pequeno dentro de `data/raw/` do projeto BioStack:

```bash
cat > data/raw/sample_R1.fastq <<'FASTQ'
@sample-read-1
ACGTACGTACGT
+
FFFFFFFFFFFF
FASTQ
```

Depois execute uma simulação:

```bash
biostack run --dry-run --workflow rnaseq-basic --profile local
```

E, se Nextflow estiver instalado:

```bash
biostack run --workflow rnaseq-basic --profile local
```

Este dataset é apenas demonstrativo e não representa uma análise RNA-seq real.
