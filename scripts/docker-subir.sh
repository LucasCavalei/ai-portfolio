#!/usr/bin/env bash
# Subir o projeto com Docker (Git Bash / Linux / macOS)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== Chat AI RAG — Docker =="

if ! docker info >/dev/null 2>&1; then
  echo ""
  echo "ERRO: O Docker não respondeu."
  echo "Abra o Docker Desktop (ou inicie o serviço docker) e tente de novo."
  exit 1
fi

if [[ ! -f "$ROOT/.env" ]]; then
  if [[ -f "$ROOT/.env.example" ]]; then
    cp "$ROOT/.env.example" "$ROOT/.env"
    echo ""
    echo "Criei .env a partir de .env.example"
    echo "Edite .env com suas chaves de API antes de usar o chat."
    echo ""
  else
    echo "ERRO: Falta .env e .env.example na raiz." >&2
    exit 1
  fi
fi

echo "Subindo containers..."
docker compose up --build
