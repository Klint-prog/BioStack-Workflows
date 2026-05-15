# Segurança operacional — v0.2.0 Docker Platform Edition

Este documento registra o checklist mínimo de segurança da v0.2.0. A plataforma continua **local-first**, sem autenticação robusta de produção, sem TLS embutido e sem promessa de isolamento multiusuário.

## Princípios da fase

- Não adicionar autenticação complexa, cloud, Kubernetes, HPC/SLURM ou orquestração distribuída.
- Preservar a CLI local existente.
- Manter IA limitada a troubleshooting operacional.
- Não gravar segredos no repositório.
- Reduzir superfície de execução em containers sempre que viável.

## Checklist de container

- Os containers Python `backend`, `api` e `worker` usam usuário não-root `biostack`.
- O Compose aplica `security_opt: no-new-privileges:true` nos serviços principais.
- Logs Docker usam rotação `json-file` com `max-size=10m` e `max-file=3`.
- Serviços principais possuem healthchecks.
- Serviços usam `restart: unless-stopped` para recuperação local simples.
- Portas são parametrizadas por variável de ambiente.

## Docker socket

O Compose **não monta** `/var/run/docker.sock` em nenhum serviço.

Montar o Docker socket dentro de um container concede, na prática, controle elevado sobre o host Docker. Qualquer fase futura que permita execução real de Nextflow com Docker a partir do worker deverá reavaliar explicitamente:

- permissões do usuário;
- escopo de acesso ao host;
- isolamento de diretórios;
- risco de escape operacional;
- necessidade de runner dedicado;
- uso de imagens assinadas ou registry controlado.

## Segredos e variáveis de ambiente

- `.env.example` contém apenas valores seguros de exemplo.
- Não inserir chaves reais em `.env.example`, README, documentação, fixtures ou testes.
- Chaves reais, quando usadas no futuro, devem ser injetadas via ambiente local, secret manager ou mecanismo equivalente.
- A verificação mínima de release inclui `grep -rI 'sk-' . || echo 'OK: sem chaves'`.

## Exposição de portas

Uso local recomendado:

- `8080`: entrada principal via Nginx.
- `8000`: API direta para debug local.
- `5173`: frontend direto para debug local.

Para exposição fora da máquina local, antes é obrigatório adicionar pelo menos:

- TLS;
- autenticação;
- autorização;
- política de CORS restritiva;
- rate limiting;
- logs e retenção auditáveis;
- revisão de backup/restore;
- revisão de privacidade dos dados processados.

## CORS

A API lê `BIOSTACK_CORS_ORIGINS` como lista separada por vírgulas. O padrão local é:

```text
http://localhost:8080,http://localhost:5173
```

Não usar `*` em ambiente compartilhado ou publicado.

## IA operacional

O provider padrão permanece `mock`. A IA do projeto é limitada a explicar logs e falhas técnicas. Ela não deve ser usada para:

- diagnóstico clínico;
- interpretação biológica;
- decisão terapêutica;
- priorização de variantes;
- recomendação médica.

O aviso obrigatório permanece: `AVISO: Não usar para diagnóstico ou interpretação clínica.`

## Dados e volumes

Os volumes persistentes podem conter projetos, logs, relatórios e metadados técnicos. Trate os volumes como dados sensíveis quando houver amostras reais, mesmo que a plataforma atual seja demonstrativa.
