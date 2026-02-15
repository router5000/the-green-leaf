#!/usr/bin/env python3
"""
Test Reve API with different request structures
"""
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

reve_api_key = os.environ.get("REVE_API_KEY")
print(f"API Key (first 30 chars): {reve_api_key[:30]}...")

console_id = "87b6fcbd-f44a-46e2-b954-6a6d83a0aa30"

# Try the exact endpoint from reve-art.com docs
print("\n" + "="*60)
print("Testing Reve-specific endpoint structures")
print("="*60)

# Test 1: Simple generate endpoint with minimal payload
endpoint = f"https://api.reve.com/console/{console_id}/generate"
print(f"\n🔍 Test 1: {endpoint}")
try:
    response = requests.post(
        endpoint,
        headers={
            "x-api-key": reve_api_key,  # Try x-api-key instead
            "Content-Type": "application/json"
        },
        json={
            "prompt": "A beautiful cannabis",
            "aspectRatio": "16:9"  # Try camelCase
        },
        timeout=15
    )
    print(f"   Status: {response.status_code}")
    if response.status_code != 405:
        print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Try with API key in header different way
endpoint = f"https://api.reve.com/console/{console_id}/generate"
print(f"\n🔍 Test 2: {endpoint} (with x-api-key)")
try:
    response = requests.post(
        endpoint,
        headers={
            "x-api-key": reve_api_key,
            "Content-Type": "application/json"
        },
        json={"prompt": "A beautiful cannabis"},
        timeout=15
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ SUCCESS!")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Try completely different base URL
endpoint = "https://reve.com/api/generate"
print(f"\n🔍 Test 3: {endpoint}")
try:
    response = requests.post(
        endpoint,
        headers={
            "Authorization": f"Bearer {reve_api_key}",
            "Content-Type": "application/json"
        },
        json={"prompt": "A beautiful cannabis"},
        timeout=15
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ SUCCESS!")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
print("Testing if GET works on console endpoint")
print("="*60)

# Test 4: GET request to see if endpoint exists
endpoint = f"https://api.reve.com/console/{console_id}/generate"
print(f"\n🔍 Test 4: GET {endpoint}")
try:
    response = requests.get(
        endpoint,
        headers={"Authorization": f"Bearer {reve_api_key}"},
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:300]}")
except Exception as e:
    print(f"   Error: {e}")
