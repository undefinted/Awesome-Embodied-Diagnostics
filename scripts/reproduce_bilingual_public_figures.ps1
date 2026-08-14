param(
  [string]$Node = "node",
  [string]$Python = "python"
)
$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
$repoData = Join-Path $repo "data\presentation"
if (Test-Path -LiteralPath $repoData) {
  $dataDir = $repoData
  $figureDir = Join-Path $repo "figures\public_evidence"
} else {
  $dataDir = Join-Path $repo "02_当前主数据"
  $figureDir = Join-Path $repo "03_PPT图表"
}
& $Python (Join-Path $PSScriptRoot "make_english_public_figures.py") --data-dir $dataDir --output-dir $figureDir
$raster = Join-Path $PSScriptRoot "rasterize_svg.mjs"
Get-ChildItem -LiteralPath $figureDir -Filter "*_en.svg" | ForEach-Object {
  & $Node $raster $_.FullName ($_.FullName -replace '\.svg$', '.png') 180
}
& $Python (Join-Path $PSScriptRoot "validate_bilingual_figures.py") --figure-dir $figureDir
