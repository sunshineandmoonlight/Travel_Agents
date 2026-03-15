# Test Staged Planning API
Write-Host "Testing Staged Planning API..."
Write-Host ""

# Test 1: Test endpoint
Write-Host "[1/3] Testing test endpoint..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8004/api/travel/staged/test" -Method Get
    Write-Host "  SUCCESS: $($response.message)"
    Write-Host "  Version: $($response.version)"
} catch {
    Write-Host "  FAILED: $_"
}

# Test 2: Get destinations
Write-Host "`n[2/3] Testing get-destinations endpoint..."
$body = @{
    travel_scope = "domestic"
    start_date = "2026-04-01"
    days = 5
    adults = 2
    children = 0
    budget = "medium"
    interests = @("历史文化", "美食")
    special_requests = ""
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8004/api/travel/staged/get-destinations" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
    Write-Host "  SUCCESS: $($response.destinations.Count) destinations recommended"
    foreach ($dest in $response.destinations) {
        Write-Host "    - $($dest.destination): $($dest.match_score)%"
    }
} catch {
    Write-Host "  FAILED: $_"
}

Write-Host "`n=== Test Complete ==="
