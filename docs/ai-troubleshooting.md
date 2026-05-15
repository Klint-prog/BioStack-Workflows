# IA operacional e troubleshooting

A fase 08 adiciona suporte opcional de IA ao BioStack Workflows para auxiliar na leitura de logs, metadados de execução e erros técnicos.

## Escopo permitido

O comando `biostack explain` existe para troubleshooting operacional. Ele pode ajudar a:

- resumir logs de execução;
- explicar erros técnicos relacionados a CLI, Nextflow, Docker, filesystem, configuração e ambiente;
- sugerir próximos passos operacionais verificáveis;
- orientar revisão de arquivos em `logs/` e `reports/`.

## Fora do escopo

A IA operacional não deve ser usada para:

- diagnóstico clínico;
- interpretação clínica;
- interpretação biológica de resultados;
- recomendação médica, terapêutica ou laboratorial;
- validação científica dos dados processados.

Aviso exibido pelo comando:

```text
AVISO: Não usar para diagnóstico ou interpretação clínica.
```

## Uso com provider mock

O provider `mock` é determinístico, não chama APIs externas e é usado pelos testes automatizados.

```bash
biostack explain --run latest --provider mock
```

Também é possível apontar para um run específico:

```bash
biostack explain --run run-YYYYMMDDTHHMMSSZ-xxxxxx --provider mock
```

## Configuração de provider real

O MVP define a fronteira de configuração por variável de ambiente, sem gravar chaves no repositório:

```bash
export BIOSTACK_LLM_API_KEY="<sua-chave>"
biostack explain --run latest --provider env
```

Nesta fase, o provider real ainda não faz chamada externa. A implementação concreta pode ser adicionada depois, preservando a interface `LLMProvider`.

## Segurança operacional

- Nunca grave chaves de API em arquivos do projeto.
- Use secrets do ambiente, shell ou CI quando necessário.
- O comando limita a leitura do log aos últimos 12.000 caracteres para evitar prompts excessivos.
- O conteúdo enviado ao provider vem dos relatórios JSON e logs locais do run.
- O projeto continua funcionando sem IA; `run`, `report` e `web` não dependem de provider externo.

## Testes relacionados

```bash
pytest -q tests/test_ai_provider.py tests/test_explain.py
biostack explain --run latest --provider mock
grep -rI 'sk-' . || echo 'OK: sem chaves'
```
