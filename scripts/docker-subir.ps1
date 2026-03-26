# Subir o projeto com Docker (Windows / PowerShell).
# Checagens antes do compose para evitar erros confusos de iniciante.

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "== Chat AI RAG — Docker ==" -ForegroundColor Cyan

# 1) Docker está rodando? (docker info retorna código ≠ 0 se o engine estiver parado)
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERRO: O Docker não respondeu." -ForegroundColor Red
    Write-Host "Abra o Docker Desktop e espere ficar 'Running', depois rode este script de novo."
    Write-Host "Mensagem típica: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified"
    exit 1
}

# 2) Arquivo .env na raiz (obrigatório para o Compose)
$envFile = Join-Path $Root ".env"
$example = Join-Path $Root ".env.example"
if (-not (Test-Path $envFile)) {
    if (Test-Path $example) {
        Copy-Item $example $envFile
        Write-Host ""
        Write-Host "Criei .env a partir de .env.example" -ForegroundColor Yellow
        Write-Host "Edite o arquivo .env e coloque suas chaves (COHERE, PINECONE, GROQ, etc.) antes de usar o chat."
        Write-Host ""
    } else {
        Write-Host "ERRO: Falta .env e também .env.example na raiz do projeto." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Subindo containers (primeira vez pode demorar)..." -ForegroundColor Green
docker compose up --build
