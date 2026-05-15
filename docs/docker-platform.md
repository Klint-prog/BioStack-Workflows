# Docker Platform Edition — base da phase_09

A phase_09 inicia a transição do BioStack Workflows para a v0.2.0 Docker Platform Edition sem alterar o MVP local-first.

Esta fase dockeriza apenas o backend/CLI atual. Ela não adiciona API versionada, PostgreSQL, Redis, worker com fila, frontend React ou reverse proxy Nginx. Esses componentes pertencem a fases futuras.

## Serviços disponíveis

O `docker-compose.yml` define apenas o serviço `backend`, com a CLI `biostack` instalada dentro do container.

O volume nomeado `biostack_data` é montado em `/workspace` para persistir projetos, logs e relatórios criados durante os testes em container.

## Build

```bash
docker compose build
```

Ou pelo Makefile:

```bash
make docker-build
```

## Subir serviço base

```bash
docker compose up
```

Ou:

```bash
make docker-up
```

Como o objetivo da fase é validar a CLI, o comando padrão do container exibe `biostack --help`.

## Shell no container

```bash
docker compose run --rm backend sh
```

Ou:

```bash
make docker-shell
```

## Validar a CLI em container

```bash
docker compose run --rm backend biostack --help
docker compose run --rm backend biostack doctor
```

## Fluxo end-to-end atual em container

O fluxo obrigatório do MVP continua baseado na CLI:

```bash
docker compose run --rm backend sh -lc '
  rm -rf demo && \
  biostack init demo --template rnaseq-basic && \
  cd demo && \
  biostack run --dry-run && \
  biostack report --run latest && \
  biostack explain --run latest --provider mock
'
```

Para visualizar pelo painel local dentro do container em fases futuras será necessário expor porta e revisar o modo de execução. Nesta fase, a validação principal é CLI e geração de artefatos no volume `/workspace`.

## Testes Docker

```bash
make docker-test
```

Esse target executa:

```bash
docker compose run --rm backend pytest -q
docker compose run --rm backend ruff check .
docker compose run --rm backend biostack --help
docker compose run --rm backend biostack doctor
```

## Encerrar e limpar containers

```bash
docker compose down
```

Ou:

```bash
make docker-down
```

## Segurança

- `.env.example` contém apenas valores de exemplo.
- Não grave chaves reais no repositório.
- Não use `BIOSTACK_LLM_API_KEY` real em arquivos versionados.
- O provider mock continua sendo o caminho padrão seguro para testes de troubleshooting operacional.
