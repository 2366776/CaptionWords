$ErrorActionPreference = 'Stop'

$python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    throw 'Project environment is missing. Run: python -m venv .venv; .\.venv\Scripts\python.exe -m pip install -r requirements.txt'
}

$outputDirectory = Join-Path $PSScriptRoot 'dist'
$workDirectory = Join-Path $PSScriptRoot '.build'
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
New-Item -ItemType Directory -Path $workDirectory -Force | Out-Null
$iconPath = Join-Path $outputDirectory 'CaptionWords.ico'
& $python (Join-Path $PSScriptRoot 'app_icon.py') $iconPath
if ($LASTEXITCODE -ne 0) {
    throw "Application icon generation failed with exit code $LASTEXITCODE"
}

$arguments = @(
    '-m', 'PyInstaller',
    '--noconfirm',
    '--clean',
    '--onefile',
    '--windowed',
    '--name', 'CaptionWords',
    '--icon', $iconPath,
    '--distpath', $outputDirectory,
    '--workpath', $workDirectory,
    '--specpath', $workDirectory,
    '--collect-all', 'uiautomation',
    '--hidden-import', 'comtypes.gen.UIAutomationClient',
    (Join-Path $PSScriptRoot 'caption_words.py')
)

& $python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

$outputPath = Join-Path $outputDirectory 'CaptionWords.exe'
if (-not (Test-Path $outputPath)) {
    throw "Executable was not created: $outputPath"
}
Write-Host "Built $outputPath"