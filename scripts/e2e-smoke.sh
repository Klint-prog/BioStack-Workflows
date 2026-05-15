#!/usr/bin/env sh
set -eu

BASE_URL="${BIOSTACK_E2E_BASE_URL:-http://localhost:8969}"
PROJECT_NAME="${BIOSTACK_E2E_PROJECT_NAME:-e2e-smoke}"
TEMPLATE="${BIOSTACK_E2E_TEMPLATE:-rnaseq-basic}"

printf '==> Healthcheck via Nginx: %s/api/v1/health\n' "$BASE_URL"
curl -fsS "$BASE_URL/api/v1/health"
printf '\n'

printf '==> Criando projeto: %s\n' "$PROJECT_NAME"
curl -fsS -X POST "$BASE_URL/api/v1/projects" \
  -H 'Content-Type: application/json' \
  -d "{\"name\":\"$PROJECT_NAME\",\"template\":\"$TEMPLATE\",\"force\":true}"
printf '\n'

printf '==> Disparando dry-run assíncrono\n'
RUN_RESPONSE=$(curl -fsS -X POST "$BASE_URL/api/v1/runs" \
  -H 'Content-Type: application/json' \
  -d "{\"project_name\":\"$PROJECT_NAME\",\"dry_run\":true}")
printf '%s\n' "$RUN_RESPONSE"
RUN_ID=$(printf '%s' "$RUN_RESPONSE" | python -c 'import json,sys; print(json.load(sys.stdin)["run_id"])')

printf '==> Aguardando worker gerar relatório do run %s\n' "$RUN_ID"
ATTEMPTS="${BIOSTACK_E2E_ATTEMPTS:-30}"
SLEEP_SECONDS="${BIOSTACK_E2E_SLEEP_SECONDS:-1}"
FOUND_REPORT=0
for attempt in $(seq 1 "$ATTEMPTS"); do
  REPORTS=$(curl -fsS "$BASE_URL/api/v1/reports?project_name=$PROJECT_NAME")
  if printf '%s' "$REPORTS" | grep -q "$RUN_ID"; then
    FOUND_REPORT=1
    printf 'Relatório encontrado na tentativa %s.\n' "$attempt"
    break
  fi
  sleep "$SLEEP_SECONDS"
done

if [ "$FOUND_REPORT" -ne 1 ]; then
  printf 'ERRO: relatório não encontrado para run %s.\n' "$RUN_ID" >&2
  curl -fsS "$BASE_URL/api/v1/runs?project_name=$PROJECT_NAME" >&2 || true
  exit 1
fi

printf '==> Consultando run persistido\n'
curl -fsS "$BASE_URL/api/v1/runs?project_name=$PROJECT_NAME"
printf '\n'

printf '==> Consultando relatório JSON\n'
curl -fsS "$BASE_URL/api/v1/reports/$PROJECT_NAME/$RUN_ID"
printf '\n'

printf '==> Explicando logs com provider mock\n'
curl -fsS -X POST "$BASE_URL/api/v1/explain" \
  -H 'Content-Type: application/json' \
  -d "{\"project_name\":\"$PROJECT_NAME\",\"run\":\"$RUN_ID\",\"provider\":\"mock\"}"
printf '\n'

printf 'OK: fluxo e2e concluído via %s\n' "$BASE_URL"
