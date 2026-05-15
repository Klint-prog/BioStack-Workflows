# Demo do MVP

Este walkthrough valida o BioStack Workflows v0.1.0 de ponta a ponta usando o modo `--dry-run`, que não exige Nextflow instalado.

## 1. Instalar dependências de desenvolvimento

Na raiz do repositório:

```bash
python -m pip install -e ".[dev]"
```

## 2. Verificar a CLI

```bash
biostack --help
biostack doctor
```

`biostack doctor` mostra Python, sistema operacional, Docker e Nextflow. Docker e Nextflow podem aparecer como ausentes sem impedir o dry-run.

## 3. Criar um projeto de demonstração

```bash
biostack init demo --template rnaseq-basic
cd demo
```

O comando cria uma estrutura local com:

```text
biostack.yml
config/
data/raw/
data/reference/
logs/
reports/
results/
workflows/
```

## 4. Revisar a configuração

```bash
cat biostack.yml
```

A configuração define o template `rnaseq-basic`, o engine `nextflow`, o profile padrão `docker` e os diretórios locais usados pelo MVP.

## 5. Executar uma simulação auditável

```bash
biostack run --dry-run
```

O dry-run não executa Nextflow. Ele constrói o comando que seria executado, cria um `run_id`, grava log e gera relatórios JSON/HTML.

## 6. Regenerar o HTML do relatório mais recente

```bash
biostack report --run latest
```

Esse comando lê o JSON mais recente em `reports/` e renderiza novamente o HTML correspondente.

## 7. Inspecionar evidências

```bash
ls logs
ls reports
```

Arquivos esperados:

- `logs/<run_id>.log`
- `reports/<run_id>.json`
- `reports/<run_id>.html`

O JSON contém metadados estruturados. O HTML é a versão legível para revisão humana.

## 8. Executar via Makefile

Na raiz do repositório também é possível rodar:

```bash
make demo
```

Esse target remove qualquer diretório `demo`, cria um novo projeto, executa `biostack run --dry-run` e regenera o relatório mais recente.

## 9. Execução real com Nextflow

Quando Nextflow estiver instalado:

```bash
cd demo
biostack run --workflow rnaseq-basic --profile local
```

Quando Docker também estiver instalado e funcional:

```bash
biostack run --workflow rnaseq-basic --profile docker
```

## Limite científico da demo

O workflow `rnaseq-basic` do v0.1.0 é um placeholder operacional. Ele demonstra estrutura, orquestração, logs, relatórios e checksums, mas não substitui um pipeline RNA-seq validado para produção científica.
