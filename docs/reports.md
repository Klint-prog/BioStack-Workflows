# Relatórios de execução

A Fase 04 adiciona relatórios auditáveis para cada execução do BioStack Workflows.

## Arquivos gerados

Cada chamada de `biostack run`, incluindo `--dry-run`, gera dois arquivos em `reports/`:

- `reports/<run_id>.json`: metadata estruturada da execução.
- `reports/<run_id>.html`: relatório legível renderizado via Jinja2.

O mesmo `run_id` também é usado para o log consolidado em `logs/<run_id>.log` e para o diretório de resultados em `results/<run_id>/`.

## Campos principais do JSON

O JSON registra:

- `run_id`: identificador único com timestamp UTC e sufixo aleatório.
- `started_at` e `finished_at`: timestamps UTC da execução.
- `duration_seconds`: duração calculada entre início e fim.
- `workflow` e `profile`: workflow e profile usados no comando Nextflow.
- `command`: lista de argumentos executados ou simulados.
- `status`: `SUCCEEDED` ou `FAILED`.
- `dry_run`: indica se a execução foi apenas simulação.
- `parameters`: parâmetros operacionais usados pelo runner, como input, outdir e run_id.
- `versions`: versões de BioStack, Python, sistema operacional, Docker e Nextflow quando disponíveis.
- `input_checksums`: checksums SHA256 dos arquivos de entrada detectados.
- `log_path` e `log_text`: caminho e conteúdo consolidado do log.
- `error`: mensagem de erro quando a execução falha.

## Checksums SHA256

Os checksums são calculados por streaming em blocos para evitar carregar arquivos grandes inteiros em memória. No MVP, a coleta padrão busca arquivos em `data/raw/` com extensões:

- `.fastq`
- `.fq`
- `.fastq.gz`
- `.fq.gz`

Arquivos não correspondentes são ignorados. Quando nenhum input compatível é encontrado, o relatório registra uma lista vazia e o HTML informa que não houve arquivo de entrada compatível.

## Comando de relatório

Para regenerar o HTML do relatório mais recente:

```bash
biostack report --run latest
```

Para regenerar o HTML de uma execução específica:

```bash
biostack report --run <run_id>
```

A resolução de `latest` é determinística: o BioStack lê os JSONs em `reports/`, ordena pelo `started_at` registrado no metadata e usa o nome do arquivo como desempate.

## Falhas

Quando a execução real falha por ausência do Nextflow ou retorno diferente de zero, o BioStack registra `status: FAILED`, preserva logs e ainda grava os relatórios JSON/HTML. Erros anteriores ao carregamento do projeto, como ausência de `biostack.yml`, continuam sendo reportados diretamente no terminal porque ainda não há diretório de projeto validado onde salvar evidências.
