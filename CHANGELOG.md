# Changelog

Todas as mudanças relevantes do BioStack Workflows serão documentadas neste arquivo.

O formato segue uma organização simples por versão, com foco em rastreabilidade do MVP.

## v0.1.0 — Release público inicial

### Adicionado

- CLI instalável `biostack` baseada em Typer.
- Comandos `biostack version`, `biostack doctor`, `biostack init`, `biostack run` e `biostack report`.
- Template inicial `rnaseq-basic` para criação de projetos BioStack locais.
- Estrutura padrão de projeto com `data/raw`, `data/reference`, `workflows`, `results`, `reports`, `logs` e `config`.
- Runner Nextflow com profiles `local` e `docker`.
- Modo `--dry-run` para auditoria do comando sem exigir Nextflow instalado.
- Geração de logs por execução em `logs/<run_id>.log`.
- Metadados de execução com `run_id`, timestamps, duração, status, parâmetros, versões e comando executado/simulado.
- Checksums SHA256 para arquivos de entrada compatíveis em `data/raw/`.
- Relatórios JSON e HTML em `reports/<run_id>.json` e `reports/<run_id>.html`.
- Regeneração de HTML via `biostack report --run latest` ou `--run <run_id>`.
- Documentação de arquitetura, instalação, demo, relatórios e audit log.
- Exemplo autocontido em `examples/demo-rnaseq`.
- Makefile com targets de instalação, teste, lint, limpeza e demo.
- GitHub Actions com jobs de teste e lint usando Ruff.

### Limitações conhecidas

- O workflow `rnaseq-basic` é demonstrativo e não deve ser tratado como análise científica validada.
- O MVP é local-first e não inclui painel web, Kubernetes, HPC/SLURM, multiusuário ou interpretação biológica por IA.
- A execução real depende de Nextflow e, no profile `docker`, Docker instalados no ambiente do usuário.
