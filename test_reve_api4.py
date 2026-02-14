#!/usr/bin/env python3
"""
Test Reve API - trying to decode the papi key structure
"""
import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

reve_api_key = os.environ.get("REVE_API_KEY")
print(f"Full API Key: {reve_api_key}")

# The key format is: papi.{project_id}.{secret}
# Extract the project ID
parts = reve_api_key.split('.')
if len(parts) >= 2:
    project_id = parts[1]
    print(f"Extracted Project ID: {project_id}")

    # Try endpoints with the project ID
    endpoints = [
        f"https://api.reve.com/{project_id}/generate",
        f"https://api.reve.com/projects/{project_id}/generate",
        f"https://api.reve.com/v1/projects/{project_id}/generate",
        f"https://api.reve.com/p/{project_id}/generate",
    ]

    test_payload = {
        "prompt": "A beautiful lawn",
        "aspect_ratio": "16:9"
    }

    for endpoint in endpoints:
        print(f"\n🔍 Testing: {endpoint}")
        try:
            # Try with x-api-key header
            response = requests.post(
                endpoint,
                headers={
                    "x-api-key": reve_api_key,
                    "Content-Type": "application/json"
                },
                json=test_payload,
                timeout=15
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
                break
            elif response.status_code != 404 and response.status_code != 405:
                print(f"   Response: {response.text[:500]}")
        except Exception as e:
            print(f"   Error: {e}")

# Also try the main generate endpoint without project ID
print("\n" + "="*60)
print("Trying main API endpoints")
print("="*60)

main_endpoints = [
    "https://api.reve.com/generate",
    "https://reve.com/generate",
]

for endpoint in main_endpoints:
    print(f"\n🔍 Testing: {endpoint}")
    for header_name in ["x-api-key", "Authorization"]:
        header_value = reve_api_key if header_name == "x-api-key" else f"Bearer {reve_api_key}"
        print(f"   Header: {header_name}")
        try:
            response = requests.post(
                endpoint,
                headers={
                    header_name: header_value,
                    "Content-Type": "application/json"
                },
                json=test_payload,
                timeout=15
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ SUCCESS!")
                print(f"   Response: {json.dumps(response.json(), indent=2)}")
                break
            elif response.status_code not in [404, 405]:
                print(f"   Response: {response.text[:300]}")
        except Exception as e:
            print(f"   Error: {e}")
