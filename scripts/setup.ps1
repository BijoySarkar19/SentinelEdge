# SentinelEdge Windows 11 PowerShell Setup
Write-Host "Setting up SentinelEdge Development Environment..." -ForegroundColor Cyan

# Check Python
python --version
node --version
docker --version

Write-Host "Creating Virtual Environments..." -ForegroundColor Green
python -m venv backend/.venv
python -m venv edge/.venv

Write-Host "Installing dependencies..." -ForegroundColor Green
./backend/.venv/Scripts/pip install -e "./backend[dev]"
./edge/.venv/Scripts/pip install -e "./edge"

cd frontend
npm install
cd ..

Copy-Item .env.example .env -Force
Write-Host "SentinelEdge Environment Successfully Initialized!" -ForegroundColor Green
