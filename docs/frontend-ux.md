# Frontend UX operacional — phase_16

A interface React/Vite da Docker Platform Edition v0.2.0 foi organizada como painel operacional local-first. Ela não usa dados mockados para projetos, runs ou relatórios: os dados exibidos vêm da API versionada em `/api/v1`.

## Entrada principal

Acesse a plataforma pelo reverse proxy Nginx:

```bash
docker compose up --build -d
curl -f http://localhost:8969/api/v1/health
```

Navegador:

```text
http://localhost:8969
```

Portas preservadas:

- `8969`: Nginx e entrada principal da plataforma.
- `8970`: frontend direto para debug.
- `8971`: API direta para debug.

## Fluxo de arquitetura

```text
Browser -> Nginx -> Frontend React/Vite -> API FastAPI /api/v1 -> PostgreSQL/Redis/Worker -> Workspace compartilhado
```

O frontend é servido pelo Nginx e consome a API por caminho relativo `/api/v1`, mantendo o fluxo principal em `http://localhost:8969`.

## Abas da interface

### Dashboard

Exibe dados reais coletados da API:

- status da API por `GET /api/v1/health`;
- total de projetos por `GET /api/v1/projects`;
- total de runs por `GET /api/v1/runs`;
- total de relatórios por `GET /api/v1/reports`;
- contagem de runs por status (`QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`);
- última execução registrada;
- timestamp da última atualização da interface.

### Projetos

Permite criar projetos com validação visual de nome obrigatório, descrição dos templates disponíveis e opção `recriar se existir`.

Endpoint usado:

```http
POST /api/v1/projects
```

Payload principal:

```json
{
  "name": "demo-api",
  "template": "rnaseq-basic",
  "force": false
}
```

A listagem usa cards operacionais com nome, template, workflow, caminho, quantidade de relatórios e ações para selecionar, executar dry-run, ver runs e ver relatórios.

### Runs

Lista execuções reais vindas de:

```http
GET /api/v1/runs
GET /api/v1/runs?project_name=<nome>
```

Campos apresentados:

- `run_id`;
- projeto;
- status com badge visual;
- workflow e profile;
- indicação de dry-run;
- return code quando disponível;
- datas de criação/atualização;
- caminhos de log, relatório JSON e relatório HTML.

Quando há run `QUEUED` ou `RUNNING`, a interface atualiza automaticamente a cada 8 segundos.

### Relatórios

Lista relatórios reais de:

```http
GET /api/v1/reports
GET /api/v1/reports?project_name=<nome>
GET /api/v1/reports/{project_name}/{run_id}
```

O JSON é aberto dentro da interface em bloco formatado. Quando a API informa `html_path`, o painel mostra que há HTML disponível, mas não tenta inventar um endpoint público de arquivo estático. Enquanto não houver rota dedicada para servir HTML, o caminho é exibido como metadado operacional.

### Explain operacional

Executa troubleshooting técnico com provider `mock` por padrão:

```http
POST /api/v1/explain
```

Payload principal:

```json
{
  "project_name": "demo-api",
  "run": "run-...",
  "provider": "mock"
}
```

A interface exibe o aviso obrigatório:

```text
AVISO: Não usar para diagnóstico ou interpretação clínica.
```

## Estados de loading, sucesso e erro

- Botões de criação e refresh exibem estado de carregamento.
- Falhas da API aparecem como mensagens visíveis na UI.
- A interface oferece botão de tentar novamente quando uma chamada falha.
- Criação de projeto e dry-run exibem mensagens de sucesso.

## Validação manual no navegador

1. Abrir `http://localhost:8969`.
2. Confirmar que não há texto `phase_13` no cabeçalho.
3. Confirmar que o dashboard mostra status da API e contadores reais.
4. Criar projeto `rnaseq-basic`.
5. Criar projeto `variant-calling-basic`.
6. Executar dry-run em um projeto.
7. Confirmar que a run aparece em Runs com badge de status.
8. Aguardar status final do worker.
9. Confirmar que o relatório aparece em Reports.
10. Abrir o relatório JSON na interface.
11. Executar Explain mock para uma run.
12. Confirmar que o aviso contra diagnóstico/interpretação clínica aparece.

## Limites mantidos

Esta fase não adiciona autenticação, RBAC, multiusuário, Kubernetes, cloud deploy, HPC/SLURM, Apptainer, upload científico complexo ou interpretação biológica/clínica por IA.
