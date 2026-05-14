# Contribuindo com o BioStack Workflows

Obrigado pelo interesse em contribuir.

## Escopo inicial

O projeto está organizado por fases. Contribuições devem respeitar a fase ativa e evitar implementação antecipada de funcionalidades futuras.

## Regras simples

1. Abra uma issue ou discussão antes de mudanças grandes.
2. Mantenha a solução simples, auditável e compatível com Linux/Debian.
3. Não adicione dependências sem justificativa técnica.
4. Inclua testes quando houver código ou comportamento executável.
5. Documente decisões relevantes em `docs/audit-log.md`.
6. Preserve o foco do MVP: CLI, Nextflow, Docker e relatórios reprodutíveis.

## Padrão de commits

Use mensagens claras, preferencialmente seguindo o formato:

```text
feat(scope): descrição curta
fix(scope): descrição curta
docs(scope): descrição curta
chore(scope): descrição curta
```

## Pull requests

Um pull request deve conter:

- Resumo do que foi alterado.
- Lista de arquivos principais.
- Comandos de teste executados.
- Resultado real dos testes.
- Pendências ou limitações conhecidas.
