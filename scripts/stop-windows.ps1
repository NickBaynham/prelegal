#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"
Set-Location "$PSScriptRoot/.."
docker compose down
