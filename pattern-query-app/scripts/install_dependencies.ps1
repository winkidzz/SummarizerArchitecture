# PowerShell script to install dependencies
# Extends existing requirements.txt approach

Write-Host "Installing dependencies for AI Summarization Reference Architecture..." -ForegroundColor Green

# Check if pip is available
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonCmd = "py"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "ERROR: Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

Write-Host "Using Python: $pythonCmd" -ForegroundColor Yellow

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Cyan
& $pythonCmd -m pip install --upgrade pip

# Install core dependencies
Write-Host "`nInstalling core dependencies..." -ForegroundColor Cyan
& $pythonCmd -m pip install -r requirements.txt

# Verify installations
Write-Host "`nVerifying installations..." -ForegroundColor Cyan
$packages = @("docling", "chromadb", "sentence-transformers", "duckduckgo-search", "ollama")
foreach ($pkg in $packages) {
    $installed = & $pythonCmd -m pip show $pkg 2>$null
    if ($installed) {
        Write-Host "  ✓ $pkg installed" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $pkg not found" -ForegroundColor Yellow
    }
}

Write-Host "`nInstallation complete!" -ForegroundColor Green
Write-Host "Note: Google ADK will need to be installed separately when available." -ForegroundColor Yellow
Write-Host "Note: Ollama service must be running separately (ollama serve)" -ForegroundColor Yellow

