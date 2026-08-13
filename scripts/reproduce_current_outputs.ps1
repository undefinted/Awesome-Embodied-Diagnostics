param(
  [ValidateSet('verify','p5','public-figures','all')]
  [string]$Target='verify'
)
$ErrorActionPreference='Stop'
$Here=Split-Path -Parent $MyInvocation.MyCommand.Path
$Root=Split-Path -Parent $Here

function Run-Verify { python (Join-Path $Here 'verify_provenance.py') }
function Run-P5 {
  $Generated=Join-Path $Root '06_方法与检索记录\P5_最新复现运行'
  New-Item -ItemType Directory -Path $Generated -Force | Out-Null
  python (Join-Path $Here 'build_p5_comprehensive_public_landscape.py') --output-dir $Generated
  python (Join-Path $Here 'screen_p5_high_recall_candidates.py') --input-dir $Generated --output-dir $Generated
  python (Join-Path $Here 'make_p5_public_visible_available_figure.py') --data (Join-Path $Generated 'p5_precision_title_candidate_counts.csv') --output (Join-Path $Generated 'p5_reproduced.svg')
  Write-Host 'P5 API retrieval is network-dependent and can receive 429 responses; inspect 06_方法与检索记录/P5扩展检索日志_2026-08-13.csv.'
  Write-Host "New run saved to $Generated; the frozen 2026-08-13 release is not overwritten automatically."
}
function Run-PublicFigures {
  Write-Host 'P5/P9/P13 legacy public figures are generated in the GitHub checkout by make_public_presentation_figures.mjs.'
  Write-Host 'Use the repository workflow documented in 06_方法与检索记录/可复现运行说明.md.'
}

switch($Target){
  'verify' { Run-Verify }
  'p5' { Run-P5; Run-Verify }
  'public-figures' { Run-PublicFigures; Run-Verify }
  'all' { Run-P5; Run-PublicFigures; Run-Verify }
}
