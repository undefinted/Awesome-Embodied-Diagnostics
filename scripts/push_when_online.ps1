$ErrorActionPreference = 'Stop'

$repo = Split-Path $PSScriptRoot -Parent
git -C $repo status --short --branch
git -C $repo push -u origin main

Write-Host 'Push complete. Verify with:'
Write-Host '  gh repo view undefinted/awesome-embodied-diagnostics --web'
