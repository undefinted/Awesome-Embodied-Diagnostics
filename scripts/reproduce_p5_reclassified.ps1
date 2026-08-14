param(
  [string]$PythonExe = 'python',
  [string]$NodeExe = 'node',
  [switch]$Rasterize,
  [switch]$BuildWorkbook
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Data = Join-Path $Root 'data\presentation'
$Figures = Join-Path $Root 'figures\public_evidence'
$Validation = Join-Path $Root 'outputs\p5_reclassification\validation_2026-08-14.json'

& $PythonExe (Join-Path $Root 'scripts\reclassify_p5_active_observation.py') `
  --records (Join-Path $Data 'p5_public_visible_available_records_2026-08-13.csv') `
  --output-dir $Data
if ($LASTEXITCODE -ne 0) { throw 'reclassify_p5_active_observation.py failed' }

& $PythonExe (Join-Path $Root 'scripts\reclassify_p5_public_projects.py') `
  --projects (Join-Path $Data 'p5_public_projects_2026-08-13.csv') `
  --output (Join-Path $Data 'p5_reclassified_public_projects_2026-08-14.csv')
if ($LASTEXITCODE -ne 0) { throw 'reclassify_p5_public_projects.py failed' }

& $PythonExe (Join-Path $Root 'scripts\validate_p5_reclassification.py') `
  --records (Join-Path $Data 'p5_reclassified_unique_records_2026-08-14.csv') `
  --counts (Join-Path $Data 'p5_reclassified_task_counts_2026-08-14.csv') `
  --matrix (Join-Path $Data 'p5_task_modality_matrix_2026-08-14.csv') `
  --projects (Join-Path $Data 'p5_reclassified_public_projects_2026-08-14.csv') `
  --qc (Join-Path $Data 'p5_reclassification_qc_2026-08-14.json') `
  --output $Validation
if ($LASTEXITCODE -ne 0) { throw 'validate_p5_reclassification.py failed' }

& $NodeExe (Join-Path $Root 'scripts\make_p5_reclassified_figures.mjs') `
  --counts (Join-Path $Data 'p5_reclassified_task_counts_2026-08-14.csv') `
  --matrix (Join-Path $Data 'p5_task_modality_matrix_2026-08-14.csv') `
  --qc (Join-Path $Data 'p5_reclassification_qc_2026-08-14.json') `
  --projects (Join-Path $Data 'p5_reclassified_public_projects_2026-08-14.csv') `
  --output-dir $Figures
if ($LASTEXITCODE -ne 0) { throw 'make_p5_reclassified_figures.mjs failed' }

if ($Rasterize) {
  & $NodeExe (Join-Path $Root 'scripts\rasterize_svg.mjs') `
    (Join-Path $Figures 'p5_reclassified_clinical_tasks.svg') `
    (Join-Path $Figures 'p5_reclassified_clinical_tasks.png') 180
  if ($LASTEXITCODE -ne 0) { throw 'rasterize main P5 SVG failed' }
  & $NodeExe (Join-Path $Root 'scripts\rasterize_svg.mjs') `
    (Join-Path $Figures 'p5_task_modality_matrix.svg') `
    (Join-Path $Figures 'p5_task_modality_matrix.png') 180
  if ($LASTEXITCODE -ne 0) { throw 'rasterize P5 modality SVG failed' }
}

if ($BuildWorkbook) {
  & $NodeExe (Join-Path $Root 'scripts\workbooks\build_p5_reclassified_workbook.mjs') `
    --repo $Root `
    --output (Join-Path $Root 'outputs\p5_reclassification\p5_active_observation_reclassified_2026-08-14.xlsx')
  if ($LASTEXITCODE -ne 0) { throw 'build P5 workbook failed' }
}

Write-Host 'P5 reclassification complete. Inspect validation_2026-08-14.json before use.'
