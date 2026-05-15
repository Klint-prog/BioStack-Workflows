# Troubleshooting Docker — v0.2.0 Docker Platform Edition

Este guia reúne diagnósticos rápidos para problemas comuns ao subir a plataforma com Docker Compose.

## Verificar estado dos serviços

```bash
docker compose ps
docker compose logs --no-color --tail=100 api worker nginx postgres redis frontend
```

## Build falha no backend ou worker

Verifique:

- Python base disponível;
- `pyproject.toml` válido;
- dependências do extra `[web,dev]` instaláveis;
- contexto Docker sem arquivos excessivos;
- permissões do usuário não-root `biostack`.

Comando recomendado:

```bash
docker compose build --no-cache backend worker
```

## Build falha no frontend

A imagem usa `npm install` para tolerar o lockfile atual do projeto. Se desejar migrar para `npm ci`, atualize antes `frontend/package-lock.json` em sincronia com `package.json`.

```bash
cd frontend
npm install
npm run build
cd ..
docker compose build frontend
```

## API não responde no Nginx

Teste em camadas:

```bash
curl -f http://localhost:8971/api/v1/health
curl -f http://localhost:8969/api/v1/health
docker compose logs --no-color api nginx
```

Se a API direta funciona e o Nginx falha, revise `docker/nginx.conf`.

## Worker não processa runs

Verifique Redis, logs do worker e status dos runs:

```bash
docker compose logs --no-color redis worker
docker compose exec redis redis-cli ping
```

Possíveis causas:

- Redis indisponível;
- variável `BIOSTACK_REDIS_URL` incorreta;
- migrations não aplicadas;
- API criou run mas job não foi enfileirado;
- worker sem acesso ao volume `biostack_workspace`.

## Postgres não fica saudável

```bash
docker compose logs --no-color postgres
docker compose exec postgres pg_isready -U "${POSTGRES_USER:-biostack}" -d "${POSTGRES_DB:-biostack}"
```

Possíveis causas:

- senha alterada após volume já inicializado;
- volume antigo com credenciais diferentes;
- porta local ocupada;
- volume corrompido.

Em desenvolvimento, só use reset destrutivo após backup:

```bash
docker compose down -v
```

## Frontend abre, mas ações falham

Teste a API pela mesma entrada do frontend:

```bash
curl -f http://localhost:8969/api/v1/health
```

Revise:

- `BIOSTACK_CORS_ORIGINS`;
- proxy `/api/` no Nginx;
- logs do navegador;
- logs da API.

## Healthcheck falha após mudança de porta

As portas externas são parametrizadas, mas os healthchecks internos usam as portas internas dos containers. Altere `API_PORT`, `FRONTEND_PORT` ou `PLATFORM_PORT` apenas para portas do host.

Portas externas padrão:

- `PLATFORM_PORT=8969`
- `FRONTEND_PORT=8970`
- `API_PORT=8971`

## Permissões no workspace

Os containers Python rodam como usuário não-root. Se um volume antigo tiver arquivos de root, pode ocorrer erro de escrita. Em desenvolvimento local, recrie o volume após backup ou ajuste permissões por container auxiliar.

## Verificação final de release

```bash
python -m pip install -e '.[web,dev]'
pytest -q
ruff check .
cd frontend && npm install && npm run build
cd ..
docker compose build
docker compose up -d
curl -f http://localhost:8969/api/v1/health
bash scripts/e2e-smoke.sh
docker compose ps
docker compose down
grep -rI 'sk-' . || echo 'OK: sem chaves'
```
