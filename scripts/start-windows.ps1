#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot/.."
docker compose up -d --build
Write-Host "Backend:  http://localhost:8000"
Write-Host "Frontend: http://localhost:3000"
