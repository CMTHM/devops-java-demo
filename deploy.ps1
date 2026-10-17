# Build, push a new tag, then start that tag.
# Compose reads DOCKERHUB_USER from .env. This script only sets the new tag.
# Usage, from this folder: .\deploy.ps1
$env:IMAGE_TAG = Get-Date -Format "yyyyMMdd-HHmmss"

docker compose build app
docker compose push app
docker compose up -d --no-build

Write-Host "Deployed $($env:IMAGE_TAG)"
