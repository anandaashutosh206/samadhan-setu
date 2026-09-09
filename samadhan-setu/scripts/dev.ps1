# Starts the API and web dev servers together. Run from the repo root.
$ErrorActionPreference = "Stop"

$apiJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWD\api"
    uvicorn app.main:app --reload --port 8000
}

$webJob = Start-Job -ScriptBlock {
    Set-Location "$using:PWD\web"
    npm run dev
}

Write-Host "API and web dev servers starting as background jobs (Get-Job to inspect, Stop-Job to stop)."
Write-Host "API:  http://localhost:8000/docs"
Write-Host "Web:  http://localhost:3000"

Receive-Job -Job $apiJob, $webJob -Wait
