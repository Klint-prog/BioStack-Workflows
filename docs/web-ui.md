# Painel web local experimental

A fase 07 adiciona um painel web local simples ao BioStack Workflows. Ele existe para ajudar pesquisadores e revisores a visualizar projetos, execuções e relatórios já gerados pela CLI.

## Escopo

- Interface local com FastAPI e templates Jinja2.
- Comando `biostack web` para iniciar o servidor.
- Rotas `/`, `/projects`, `/reports` e `/reports/{run_id}`.
- Descoberta de projetos BioStack no diretório atual e em subdiretórios imediatos.
- Reuso dos relatórios HTML/JSON existentes.

## Instalação

As dependências web são opcionais:

```bash
python -m pip install -e ".[web]"
```

A CLI principal continua funcionando sem instalar o extra `web`.

## Uso

Dentro do diretório onde estão seus projetos BioStack:

```bash
biostack web --host 127.0.0.1 --port 8000
```

Depois acesse:

```text
http://127.0.0.1:8000/
```

## Limitações e segurança

Este painel é experimental, local e sem autenticação. Não exponha o servidor em redes públicas. A interface não implementa upload, multiusuário, edição de arquivos, autenticação ou autorização.
