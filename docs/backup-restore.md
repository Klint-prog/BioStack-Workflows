# Backup e restore — v0.2.0 Docker Platform Edition

Este guia cobre backup e restauração local dos volumes Docker da v0.2.0. Ele é voltado para desenvolvimento, demonstração e auditoria técnica.

## Volumes relevantes

```text
biostack_workspace
biostack_postgres_data
biostack_redis_data
```

- `biostack_workspace`: projetos, logs e relatórios.
- `biostack_postgres_data`: banco PostgreSQL.
- `biostack_redis_data`: dados Redis/AOF da fila local.

## Backup lógico do PostgreSQL

Com a stack em execução:

```bash
docker compose exec postgres pg_dump -U "${POSTGRES_USER:-biostack}" "${POSTGRES_DB:-biostack}" > backups/biostack-postgres.sql
```

Crie o diretório antes:

```bash
mkdir -p backups
```

## Restore lógico do PostgreSQL

Com a stack em execução e o banco acessível:

```bash
cat backups/biostack-postgres.sql | docker compose exec -T postgres psql -U "${POSTGRES_USER:-biostack}" "${POSTGRES_DB:-biostack}"
```

Para restore limpo em ambiente de desenvolvimento, derrube a stack e remova volumes somente se tiver backup validado:

```bash
docker compose down -v
docker compose up -d postgres
cat backups/biostack-postgres.sql | docker compose exec -T postgres psql -U "${POSTGRES_USER:-biostack}" "${POSTGRES_DB:-biostack}"
```

## Backup do workspace

O workspace contém artefatos operacionais. Para exportar o volume:

```bash
mkdir -p backups
docker run --rm \
  -v biostack-workflows_biostack_workspace:/volume:ro \
  -v "$(pwd)/backups:/backup" \
  alpine tar czf /backup/biostack-workspace.tgz -C /volume .
```

O nome real do volume pode variar conforme o diretório do projeto. Confirme com:

```bash
docker volume ls | grep biostack
```

## Restore do workspace

```bash
docker run --rm \
  -v biostack-workflows_biostack_workspace:/volume \
  -v "$(pwd)/backups:/backup:ro" \
  alpine sh -c 'cd /volume && tar xzf /backup/biostack-workspace.tgz'
```

## Backup do Redis

Redis é usado para fila/cache local. Em geral, para desenvolvimento, o PostgreSQL e o workspace são mais importantes. Se necessário, exporte o volume Redis da mesma forma que o workspace.

## Checklist antes de apagar volumes

Antes de executar `docker compose down -v`, confirme:

- backup lógico do Postgres criado;
- backup do workspace criado;
- arquivo de backup abre/lista corretamente;
- nenhum job importante está em execução;
- documentação de versão e commit foi registrada.

## Dados sensíveis

Mesmo em MVP, logs e relatórios podem conter nomes de arquivos, caminhos locais e metadados de execução. Se o projeto processar dados reais, trate backups como material sensível.
