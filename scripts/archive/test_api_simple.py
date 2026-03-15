"""
Simple API test for travel staging endpoints
"""
import requests
import json

API_BASE_URL = "http://localhost:8005"

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

print("=" * 70)
print("  Testing Travel Agents API")
print("=" * 70)

# Test 1: Get destinations
print("\n[TEST 1] Getting destinations...")
url = f"{API_BASE_URL}/api/travel/staged/get-destinations"
print(f"URL: {url}")
print(f"Data: {json.dumps(TEST_REQUIREMENTS, ensure_ascii=False)}")

try:
    response = requests.post(url, json=TEST_REQUIREMENTS, timeout=60)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print("\n[OK] Request successful!")

        # Show destinations
        if "destinations" in data:
            destinations = data["destinations"]
            print(f"\n[INFO] Found {len(destinations)} destinations:")
            for i, dest in enumerate(destinations[:3], 1):
                print(f"\n  [{i}] {dest.get('destination', 'N/A')}")
                print(f"      Match Score: {dest.get('match_score', 'N/A')}/100")
                print(f"      Budget: {dest.get('estimated_budget', 'N/A')}")
                print(f"      Reason: {dest.get('recommendation_reason', 'N/A')}")
                if 'ai_explanation' in dest:
                    print(f"      [AI] {dest['ai_explanation'][:60]}...")

        # Show user portrait
        if "user_portrait" in data:
            portrait = data["user_portrait"]
            print(f"\n[INFO] User Portrait:")
            print(f"      Travel Type: {portrait.get('travel_type', 'N/A')}")
            print(f"      Pace: {portrait.get('pace_preference', 'N/A')}")

    else:
        print(f"[ERROR] Request failed: {response.text}")

except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "=" * 70)
print("  Test Complete")
print("=" * 70)
