# Test Travel Planning API - Detailed
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

Write-Host "=== Testing Travel Planning API (Detailed) ===`n"

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8004/api/travel/plans/ai/generate-plans" -Method Post -Body $body -Headers $headers -TimeoutSec 60

    Write-Host "✅ Success!"
    Write-Host "`n=== Basic Info ==="
    Write-Host "Destination: $($response.destination)"
    Write-Host "Days: $($response.days)"
    Write-Host "Plans: $($response.plans.Count)"

    Write-Host "`n=== Agent Analyses ==="
    if ($response.agent_analyses) {
        Write-Host "Destination: $($response.agent_analyses.destination.agent_name)"
        Write-Host "  - $($response.agent_analyses.destination.summary)"
        Write-Host "Attractions: $($response.agent_analyses.attractions.agent_name)"
        Write-Host "  - $($response.agent_analyses.attractions.summary)"
        Write-Host "Weather: $($response.agent_analyses.weather.agent_name)"
        Write-Host "  - $($response.agent_analyses.weather.summary)"
        Write-Host "Budget: $($response.agent_analyses.budget.agent_name)"
        Write-Host "  - $($response.agent_analyses.budget.summary)"
        Write-Host "Itinerary: $($response.agent_analyses.itinerary.agent_name)"
        Write-Host "  - $($response.agent_analyses.itinerary.summary)"
    }

    Write-Host "`n=== Plans ==="
    foreach ($plan in $response.plans) {
        Write-Host "`nPlan: $($plan.name)"
        Write-Host "  Budget: $($plan.budget)"
        Write-Host "  Highlights: $($plan.highlights -join ', ')"
        Write-Host "  Days: $($plan.itinerary.Count)"
    }

    Write-Host "`n=== Metadata ==="
    Write-Host "Generated: $($response.metadata.generated_at)"
    Write-Host "LLM Provider: $($response.metadata.llm_provider)"
    Write-Host "Agents: $($response.metadata.agents_used -join ', ')"

} catch {
    Write-Host "❌ Error: $_"
}
