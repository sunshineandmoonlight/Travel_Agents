# Test Staged Planning API - Full Test
$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "=== Testing Staged Planning API on Port 8005 ===`n"

# Test 1: Test endpoint
Write-Host "[1/2] Testing test endpoint..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8005/api/travel/staged/test" -Method Get
    Write-Host "  SUCCESS: $($response.message)"
    Write-Host "  Version: $($response.version)"
} catch {
    Write-Host "  FAILED: $_"
}

# Test 2: Get destinations (Group A agents)
Write-Host "`n[2/2] Testing get-destinations (Group A Agents)..."
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

Write-Host "  Request: $body"

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8005/api/travel/staged/get-destinations" -Method Post -Body $body -Headers $headers -TimeoutSec 60
    Write-Host "  SUCCESS: $($response.destinations.Count) destinations recommended"
    Write-Host "  User Portrait: $($response.user_portrait.description)"
    Write-Host "`n  Top 4 Destinations:"
    foreach ($dest in $response.destinations) {
        Write-Host "    [$($dest.destination)] Match: $($dest.match_score)% - Budget: $($dest.estimated_budget.per_person) CNY/person"
        Write-Host "       Reason: $($dest.recommendation_reason)"
    }
    Write-Host "`n  Agent Analysis: $($response.agent_analysis.agents -join ', ')"
} catch {
    Write-Host "  FAILED: $_"
    Write-Host "  Response: $($_.Exception.Response | ConvertFrom-Json)"
}

Write-Host "`n=== Test Complete ==="
