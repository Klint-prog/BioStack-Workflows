# Arquitetura inicial

## Objetivo arquitetural

A arquitetura inicial do BioStack Workflows deve ser simples, local-first e auditável. O projeto começa como uma CLI em Python que orquestra validação de ambiente, execução de workflows via Nextflow/Docker e geração de relatórios.

## Componentes previstos para o MVP

```text
+---------------------------+
| Usuário / Terminal        |
+-------------+-------------+
              |
              v
+---------------------------+
| BioStack CLI (Python)     |
| Typer + Rich              |
+-------------+-------------+
              |
      +-------+--------+
      |                |
      v                v
+-------------+   +----------------+
| Config YAML |   | Validação      |
| Pydantic    |   | ambiente       |
+-------------+   +----------------+
      |                |
      +-------+--------+
              |
              v
+---------------------------+
| Nextflow Workflow Engine  |
+-------------+-------------+
              |
              v
+---------------------------+
| Docker / Docker Compose   |
+-------------+-------------+
              |
              v
+---------------------------+
| Execução local            |
| logs, outputs, checksums  |
+-------------+-------------+
              |
              v
+---------------------------+
| Relatórios HTML / JSON    |
| Jinja2 + metadados        |
+---------------------------+
```

## Princípios

- Começar sem painel web.
- Evitar banco de dados no MVP salvo necessidade clara.
- Usar filesystem local como armazenamento inicial.
- Registrar metadados suficientes para auditoria.
- Separar workflow científico de camada de orquestração.
- Manter compatibilidade com Linux/Debian.

## Diretórios iniciais

- `biostack/`: futuro pacote Python.
- `workflows/`: workflows Nextflow.
- `examples/`: exemplos mínimos de uso.
- `tests/`: testes automatizados futuros.
- `docs/`: documentação técnica e decisões de projeto.
