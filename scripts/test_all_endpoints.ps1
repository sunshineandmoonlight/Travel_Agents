# Test All Travel Planning API Endpoints
$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "=== Testing All Travel Planning Endpoints ===`n"

# Test 1: CORS Test
Write-Host "[1/4] Testing CORS endpoint..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8004/api/travel/plans/test" -Method Get
    Write-Host "  ✅ CORS Test: $($response.success)"
} catch {
    Write-Host "  ❌ CORS Test failed: $_"
}

# Test 2: Simple Test
Write-Host "`n[2/4] Testing simple test endpoint..."
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8004/api/travel/plans/test-simple" -Method Post -Body "{}" -Headers $headers
    Write-Host "  ✅ Simple Test: $($response.success)"
    Write-Host "     Message: $($response.message)"
} catch {
    Write-Host "  ❌ Simple Test failed: $_"
}

# Test 3: Generate Plans
Write-Host "`n[3/4] Testing generate plans endpoint..."
$body = @{
    destination = "成都"
    days = 4
    adults = 2
    children = 1
    budget = "medium"
    styles = @("美食", "休闲")
    special_requests = ""
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8004/api/travel/plans/ai/generate-plans" -Method Post -Body $body -Headers $headers -TimeoutSec 60
    Write-Host "  ✅ Generate Plans: $($response.success)"
    Write-Host "     Destination: $($response.destination)"
    Write-Host "     Plans: $($response.plans.Count) generated"
    Write-Host "     Agents: $($response.metadata.agents_used.Count) agents used"
} catch {
    Write-Host "  ❌ Generate Plans failed: $_"
}

# Test 4: Generate Guide
Write-Host "`n[4/4] Testing generate guide endpoint..."
$guideBody = @{
    selected_plan = @{
        name = "舒适品质游"
        days = 4
        budget = "medium"
        destination = "成都"
        description = "舒适型成都4日游"
    }
    requirements = "为4天的成都旅行生成详细攻略"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8004/api/travel/plans/ai/generate-guide" -Method Post -Body $guideBody -Headers $headers -TimeoutSec 60
    Write-Host "  ✅ Generate Guide: $($response.success)"
    if ($response.guide) {
        Write-Host "     Sections: $($response.guide.sections.Count)"
    }
} catch {
    Write-Host "  ❌ Generate Guide failed: $_"
}

Write-Host "`n=== All Tests Complete ==="
