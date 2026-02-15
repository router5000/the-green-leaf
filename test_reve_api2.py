#!/usr/bin/env python3
"""
Test Reve API with console ID from the docs URL
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

reve_api_key = os.environ.get("REVE_API_KEY")
print(f"API Key (first 20 chars): {reve_api_key[:20]}...")

# The docs URL was: https://api.reve.com/console/87b6fcbd-f44a-46e2-b954-6a6d83a0aa30/docs
# This suggests the console ID might be part of the endpoint
console_id = "87b6fcbd-f44a-46e2-b954-6a6d83a0aa30"

endpoints = [
    f"https://api.reve.com/console/{console_id}/v1/images/generate",
    f"https://api.reve.com/console/{console_id}/images/generate",
    f"https://api.reve.com/console/{console_id}/generate",
    "https://api.reve.com/generate",
    "https://api.reve.com/images/generate",
]

test_payload = {
    "prompt": "A beautiful cannabis",
    "aspect_ratio": "16:9"
}

headers = {
    "Authorization": f"Bearer {reve_api_key}",
    "Content-Type": "application/json"
}

for endpoint in endpoints:
    print(f"\n🔍 Testing: {endpoint}")
    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=test_payload,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:300]}")

        if response.status_code == 200:
            print(f"   ✅ SUCCESS! Working endpoint: {endpoint}")
            print(f"   Full response: {response.json()}")
            break
    except Exception as e:
        print(f"   ❌ Error: {e}")
