# Performance operacional — v0.2.0 Docker Platform Edition

A v0.2.0 prioriza previsibilidade local e rastreabilidade, não throughput massivo. Esta documentação define limites práticos e pontos de ajuste para execução em Docker Compose.

## Escopo de performance

A plataforma foi estabilizada para o fluxo obrigatório:

1. criar projeto;
2. executar dry-run;
3. gerar relatório;
4. visualizar no painel;
5. explicar logs com IA mock.

Não é objetivo desta versão executar muitos workflows simultâneos, orquestrar clusters, usar Kubernetes, HPC/SLURM ou distribuição multiworker complexa.

## Volumes

Volumes persistentes:

- `biostack_workspace`: projetos, logs e relatórios HTML/JSON.
- `biostack_postgres_data`: dados relacionais da API.
- `biostack_redis_data`: AOF e dados transitórios do Redis.

Recomendações:

- Manter `biostack_workspace` em disco local rápido durante desenvolvimento.
- Evitar armazenar datasets grandes no volume padrão da plataforma durante o MVP.
- Fazer limpeza periódica de logs e relatórios antigos em ambientes de teste.
- Usar backup antes de `docker compose down -v`.

## Worker e fila

A v0.2.0 usa uma fila simples com Redis list. O worker processa jobs de forma simples e previsível.

Recomendações:

- Começar com um worker.
- Evitar iniciar múltiplos workers até haver controle de concorrência, locks e política clara para execução real.
- Preferir dry-run para validação de UI/API.
- Tratar execução real com Nextflow/Docker como assunto de fase futura por causa do risco do Docker socket.

## Redis

O Compose define Redis com AOF e limite básico de memória via `REDIS_MAXMEMORY`, padrão `256mb`, usando `allkeys-lru`.

Ajuste em `.env` local quando necessário:

```text
REDIS_MAXMEMORY=512mb
```

## Logs

O Compose limita logs Docker com:

```yaml
logging:
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"
```

Isso evita crescimento indefinido em ambiente local. Para ambientes compartilhados, integrar agregação externa de logs em fase futura.

## API e frontend

- A API roda com Uvicorn em um processo simples.
- O frontend é servido por Nginx estático.
- O Nginx principal roteia `/api/` para API e `/` para frontend.

Sinais de gargalo:

- healthcheck intermitente;
- worker com jobs presos em `QUEUED`;
- Postgres reiniciando;
- Redis atingindo limite de memória;
- crescimento excessivo de `biostack_workspace`.

## Limites conhecidos

- Sem autoscaling.
- Sem balanceador multi-instância.
- Sem limitação por usuário.
- Sem gerenciamento avançado de concorrência.
- Sem retenção automática de artefatos.
- Sem cache científico de resultados.

Esses limites são intencionais para manter a v0.2.0 auditável e simples.
