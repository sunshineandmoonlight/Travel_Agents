# Test Staged Planning API - Group B (Styles)

Write-Host "=== Testing Group B Agents (Style Proposals) ===`n"

# First, get destinations (Group A) to get user portrait
Write-Host "[Step 1/2] Getting destinations and user portrait..."

$body1 = @{
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
    $response1 = Invoke-RestMethod -Uri "http://localhost:8006/api/travel/staged/get-destinations" -Method Post -Body $body1 -ContentType "application/json" -TimeoutSec 60
    Write-Host "  SUCCESS: $($response1.destinations.Count) destinations"

    # Extract first destination for style generation
    $selectedDest = $response1.destinations[0].destination
    $userPortrait = $response1.user_portrait

    Write-Host "  Selected: $selectedDest"
    Write-Host "  User Portrait: $($userPortrait.description)"

    # Now get styles (Group B)
    Write-Host "`n[Step 2/2] Getting style proposals..."

    $body2 = @{
        destination = $selectedDest
        user_requirements = @{
            travel_scope = "domestic"
            days = 5
            user_portrait = $userPortrait
        }
    } | ConvertTo-Json -Depth 10

    $response2 = Invoke-RestMethod -Uri "http://localhost:8006/api/travel/staged/get-styles" -Method Post -Body $body2 -ContentType "application/json" -TimeoutSec 60

    Write-Host "  SUCCESS: $($response2.styles.Count) style proposals"
    Write-Host "`n  Style Proposals:"

    foreach ($style in $response2.styles) {
        Write-Host "`n    [$($style.style_icon)] $($style.style_name)"
        Write-Host "      Cost: $($style.estimated_cost) CNY"
        Write-Host "      Intensity: $($style.intensity_level)/5"
        Write-Host "      Best For: $($style.best_for)"
    }

    Write-Host "`n=== Test Complete ==="

} catch {
    Write-Host "FAILED: $_"
    if ($_.Exception.Response) {
        Write-Host "Response: $($_.Exception.Response | ConvertFrom-Json)"
    }
}
