#!/usr/bin/env python3
"""
Test Reve API with /v1/image/create endpoint
"""
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

reve_api_key = os.environ.get("REVE_API_KEY")
print(f"API Key (first 30 chars): {reve_api_key[:30]}...")

endpoint = "https://api.reve.com/v1/image/create"

# Try different payload structures
payloads = [
    {
        "prompt": "A beautiful lawn",
        "aspect_ratio": "16:9"
    },
    {
        "prompt": "A beautiful lawn",
        "aspectRatio": "16:9"
    },
    {
        "prompt": "A beautiful lawn"
    }
]

# Try different header combinations
header_configs = [
    {"Authorization": f"Bearer {reve_api_key}", "Content-Type": "application/json"},
    {"x-api-key": reve_api_key, "Content-Type": "application/json"},
    {"api-key": reve_api_key, "Content-Type": "application/json"},
]

for i, payload in enumerate(payloads):
    for j, headers in enumerate(header_configs):
        print(f"\n🔍 Test {i+1}.{j+1}: Payload variant {i+1}, Header variant {j+1}")
        print(f"   Endpoint: {endpoint}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        print(f"   Headers: {list(headers.keys())}")

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                result = response.json()
                print(f"   Response: {json.dumps(result, indent=2)}")
                print("\n" + "="*60)
                print("WORKING CONFIGURATION FOUND!")
                print(f"Endpoint: {endpoint}")
                print(f"Payload: {json.dumps(payload, indent=2)}")
                print(f"Headers: {json.dumps({k: v if k != 'Authorization' and k != 'x-api-key' else '***' for k, v in headers.items()}, indent=2)}")
                print("="*60)
                exit(0)
            elif response.status_code in [400, 401, 403]:
                print(f"   Response: {response.text[:500]}")
            elif response.status_code not in [404, 405]:
                print(f"   Response: {response.text[:300]}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

print("\n❌ No working configuration found")
