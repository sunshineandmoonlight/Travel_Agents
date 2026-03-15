"""
Full workflow test for travel staging API
Tests all 3 stages and saves results to JSON file
"""
import requests
import json
import sys
from datetime import datetime

# Force UTF-8 encoding for output
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_BASE_URL = "http://localhost:8005"
OUTPUT_FILE = "test_results_output.json"

# Test data
TEST_REQUIREMENTS = {
    "travel_scope": "domestic",
    "days": 3,
    "adults": 2,
    "children": 0,
    "budget": "medium",
    "interests": ["历史文化", "美食"],
    "start_date": "2024-04-15"
}

results = {
    "timestamp": datetime.now().isoformat(),
    "test_requirements": TEST_REQUIREMENTS,
    "stages": {}
}

print("=" * 80)
print("  TravelAgents-CN Complete API Integration Test")
print("=" * 80)
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"API: {API_BASE_URL}")
print("=" * 80)

# ============================================================
# Stage 3: Get destinations (Group A)
# ============================================================
print("\n[STAGE 3] Getting destinations (Group A)...")
url = f"{API_BASE_URL}/api/travel/staged/get-destinations"

try:
    response = requests.post(url, json=TEST_REQUIREMENTS, timeout=60)
    if response.status_code == 200:
        data = response.json()
        results["stages"]["stage3"] = data
        print(f"[OK] Status 200 - Found {len(data.get('destinations', []))} destinations")

        # Show first destination details
        destinations = data.get("destinations", [])
        if destinations:
            dest = destinations[0]
            print(f"\n  Top Recommendation: {dest.get('destination', 'N/A')}")
            print(f"  Match Score: {dest.get('match_score', 'N/A')}/100")
            print(f"  Budget: {dest.get('estimated_budget', {}).get('total', 'N/A')} CNY")
            print(f"  Reason: {dest.get('recommendation_reason', 'N/A')[:50]}...")

            # Check for AI explanation (LLM enhancement)
            if 'ai_explanation' in dest:
                print(f"  [AI Enhancement] {dest['ai_explanation'][:50]}...")

        # Show user portrait
        if 'user_portrait' in data:
            portrait = data['user_portrait']
            print(f"\n  User Portrait: {portrait.get('travel_type', 'N/A')} - {portrait.get('pace_preference', 'N/A')}")

        selected_destination = destinations[0].get("destination") if destinations else "成都"
    else:
        print(f"[ERROR] Stage 3 failed: {response.status_code}")
        selected_destination = "成都"
except Exception as e:
    print(f"[ERROR] Stage 3 exception: {e}")
    selected_destination = "成都"

# ============================================================
# Stage 4: Get styles (Group B - Parallel)
# ============================================================
print(f"\n[STAGE 4] Getting styles for '{selected_destination}' (Group B Parallel)...")
url = f"{API_BASE_URL}/api/travel/staged/get-styles"

style_request = {**TEST_REQUIREMENTS, "selected_destination": selected_destination}

try:
    response = requests.post(url, json=style_request, timeout=60)
    if response.status_code == 200:
        data = response.json()
        results["stages"]["stage4"] = data
        print(f"[OK] Status 200 - Found {len(data.get('style_proposals', []))} style proposals")

        # Show style proposals
        proposals = data.get("styles", data.get("style_proposals", []))
        if proposals:
            print(f"\n  Available Styles:")
            for i, prop in enumerate(proposals, 1):
                print(f"    [{i}] {prop.get('style_name', 'N/A')} ({prop.get('style_type', 'N/A')})")
                print(f"        Intensity: {prop.get('intensity_level', 'N/A')}/5")
                print(f"        Cost: {prop.get('estimated_cost', 'N/A')} CNY")

                # Check for LLM description (LLM enhancement)
                if 'llm_description' in prop:
                    desc = prop['llm_description']
                    print(f"        [LLM] {desc[:60]}...")

        selected_style = proposals[0].get("style_type") if proposals else "immersive"
    else:
        print(f"[ERROR] Stage 4 failed: {response.status_code}")
        selected_style = "immersive"
except Exception as e:
    print(f"[ERROR] Stage 4 exception: {e}")
    selected_style = "immersive"

# ============================================================
# Stage 5: Get detailed guide (Group C - Mixed Parallel)
# ============================================================
print(f"\n[STAGE 5] Getting detailed guide (Group C Mixed Parallel)...")
url = f"{API_BASE_URL}/api/travel/staged/generate-guide"

# The endpoint expects a different format
guide_request = {
    "destination": selected_destination,
    "style_type": selected_style,
    "user_requirements": {
        **TEST_REQUIREMENTS,
        "user_portrait": results["stages"].get("stage3", {}).get("user_portrait", {})
    }
}

try:
    response = requests.post(url, json=guide_request, timeout=180)
    if response.status_code == 200:
        data = response.json()
        results["stages"]["stage5"] = data
        print(f"[OK] Status 200 - Guide generated")

        # Show guide components
        if "detailed_guide" in data:
            guide = data["detailed_guide"]

            # C1: Attractions
            if "scheduled_attractions" in guide:
                attractions = guide["scheduled_attractions"]
                days_count = len(attractions)
                print(f"\n  [C1] Attractions Scheduler: {days_count} days planned")

            # C4: Accommodation
            if "accommodation_plan" in guide:
                accom = guide["accommodation_plan"]
                area = accom.get("recommended_area", {})
                print(f"  [C4] Accommodation Advisor: {area.get('area', 'N/A')}")
                if 'ai_explanation' in area:
                    print(f"      [AI] {area['ai_explanation'][:50]}...")

            # C2: Transport
            if "transport_plan" in guide:
                transport = guide["transport_plan"]
                cost = transport.get("total_transport_cost", "N/A")
                print(f"  [C2] Transport Planner: Total {cost} CNY")

            # C3: Dining
            if "dining_plan" in guide:
                dining = guide["dining_plan"]
                meal_cost = dining.get("estimated_meal_cost", {})
                print(f"  [C3] Dining Recommender: {meal_cost.get('per_day', 'N/A')} CNY/day")

            # C5: Guide Content
            if "guide_content" in guide:
                content = guide["guide_content"]
                if content and "guide_content" in content:
                    gc = content["guide_content"]
                    title = gc.get("title", "N/A")
                    content_len = len(gc.get("content", ""))
                    print(f"  [C5] Guide Writer: '{title}' ({content_len} chars)")
    else:
        print(f"[ERROR] Stage 5 failed: {response.status_code}")
except Exception as e:
    print(f"[ERROR] Stage 5 exception: {e}")
    import traceback
    traceback.print_exc()

# ============================================================
# Save results
# ============================================================
print(f"\n[Saving] Results to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("=" * 80)
print("  Test Complete!")
print("=" * 80)
print(f"\nResults saved to: {OUTPUT_FILE}")
print("\n[Summary]")
print(f"  - Stage 3 (Group A): {'OK' if 'stage3' in results['stages'] else 'FAILED'}")
print(f"  - Stage 4 (Group B): {'OK' if 'stage4' in results['stages'] else 'FAILED'}")
print(f"  - Stage 5 (Group C): {'OK' if 'stage5' in results['stages'] else 'FAILED'}")
print("\n[Features Verified]")
print("  - LLM Enhancement (ai_explanation): Check results file")
print("  - Parallel Execution: Timing in server logs")
print("  - Staged Design: User can select at each stage")
