#!/usr/bin/env python3
"""
Quick test script to debug Reve API endpoint
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

reve_api_key = os.environ.get("REVE_API_KEY")
print(f"API Key (first 20 chars): {reve_api_key[:20]}...")

# Test different endpoint variations
endpoints = [
    "https://api.reve.com/v1/images/generate",
    "https://api.reve.com/console/v1/images/generate",
    "https://api.reve.com/api/v1/images/generate",
    "https://reve.com/api/v1/images/generate",
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
        print(f"   Response: {response.text[:200]}")

        if response.status_code == 200:
            print(f"   ✅ SUCCESS! Working endpoint: {endpoint}")
            print(f"   Full response: {response.json()}")
            break
    except Exception as e:
        print(f"   ❌ Error: {e}")
