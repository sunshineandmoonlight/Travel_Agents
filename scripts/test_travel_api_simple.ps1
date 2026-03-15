# Test Travel Planning API
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    destination = "西安"
    days = 5
    adults = 2
    children = 0
    budget = "medium"
    styles = @("历史文化", "美食")
    special_requests = ""
} | ConvertTo-Json

Write-Host "Testing Travel Planning API..."
Write-Host "Request: $body"

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8004/api/travel/plans/ai/generate-plans" -Method Post -Body $body -Headers $headers -TimeoutSec 60
    Write-Host "Success!"
    Write-Host "Plans generated: $($response.plans.Count)"
    Write-Host "Destination: $($response.destination)"
    if ($response.agent_analyses) {
        Write-Host "Agent analyses available: YES"
    }
} catch {
    Write-Host "Error: $_"
    Write-Host "StatusCode: $($_.Exception.Response.StatusCode.value__)"
    Write-Host "Response: $($_.Exception.Response.GetResponseStream())"
}
