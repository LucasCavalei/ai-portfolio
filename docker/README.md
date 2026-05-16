# Docker — guia para iniciantes

## O que sobe

| Serviço | O quê | Porta no seu PC |
|--------|--------|------------------|
| `mysql` | MySQL 8 (cadastro `clientes`) | `3306` (ou `MYSQL_PORT` no `.env`) |
| `api`  | Backend Flask (chat, RAG) | `5000` |
| `web`  | Frontend React (build) + Nginx | `8080` |

No `.env`, com api e mysql no Compose, use por exemplo  
`ZAP_DATABASE_URL=mysql+pymysql://chatairag:chatairag_secret@mysql:3306/banco_vendas`  
(mesmo usuário, senha e banco que `MYSQL_*` no `.env` / defaults do compose).

Se já tiver MySQL na máquina na porta 3306, defina `MYSQL_PORT=3307` no `.env` para evitar conflito.

O navegador abre `http://localhost:8080`. O Nginx entrega o React e encaminha `/api/*` para a API.

## Como rodar

1. Garanta o arquivo `.env` na **raiz** do projeto (copie de `.env.example`).
2. Suba:
   - Windows (PowerShell): `.\scripts\docker-subir.ps1`
   - Git Bash/Linux/macOS: `bash scripts/docker-subir.sh`
3. Abra `http://localhost:8080`.

Sem script: `docker compose up --build`.

## O que reduz erros comuns no Docker

- O `Dockerfile.api` executa `docker/normalize_requirements.py` antes do `pip install`, para:
  - converter `requirements.txt` de UTF-16 (Windows) para UTF-8;
  - remover a linha `flask-json-provider` (não existe no PyPI).

## Se der erro

- `flask-json-provider` ainda aparece no log: confirme que o build está usando `docker/Dockerfile.api` e `docker/normalize_requirements.py` (pode limpar com `--no-cache`).
- `Docker Engine não está ativo`: abra o **Docker Desktop** e aguarde ficar `Running`.
- Portas ocupadas: ajuste o mapeamento em `docker-compose.yml`.
