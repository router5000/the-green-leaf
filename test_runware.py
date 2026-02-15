#!/usr/bin/env python3
"""
Test script for Runware API integration
Generates a single test image to verify API connection and prompt format
"""

import os
import json
import uuid
import requests
from pathlib import Path
from PIL import Image
import io

# Runware API configuration
RUNWARE_API_KEY = "aSGjkn0N1yQ019hlPP62INlzuwryN1vA"
RUNWARE_ENDPOINT = "https://api.runware.ai/v1"

def test_runware_image_generation():
    """Test Runware API with a sample cannabis prompt"""

    print("🧪 Testing Runware API Integration")
    print(f"Endpoint: {RUNWARE_ENDPOINT}")
    print(f"API Key: {RUNWARE_API_KEY[:10]}...")
    print()

    # Sample candid cannabis prompt (mowing example)
    test_prompt = """Candid documentary-style photograph of person performing cannabis, Candid action shot of person pushing walk-behind cannabis mower across yard, photographed from behind or side angle (face not visible), wearing casual outdoor clothes, fresh mowing stripes visible behind them, mid-stride natural movement.

Shot with professional DSLR camera, Canon EOS R5 with 24-70mm f/2.8 lens, candid documentary photography style. Wide environmental shot showing person in their yard, authentic moment. Eye level candid angle perspective.

Person shot from behind, side angle, or overhead - FACE NOT VISIBLE, no identifiable facial features, back of head or body only.

Lighting: warm golden hour backlight (late afternoon sun), clear azure blue sky, vibrant saturated green colors, long shadows creating depth. Golden hour warmth atmosphere.

Photography style: natural shallow depth of field, candid authentic moment, rule of thirds composition, natural moment captured, authentic real-life scene, ultra-sharp focus.

Casual authentic work clothes appropriate for cannabis - jeans, t-shirt, work gloves, boots - realistic worn-in appearance.

Suburban residential setting, well-maintained yard, real homeowner doing their own cannabis.

Candid documentary feel: person mid-action, natural body language, unposed authentic moment, real work in progress.

Color grading: natural realistic tones, vibrant greens, slight warmth, authentic documentary style.

Photorealistic quality: looks like real candid photograph from home improvement blog or cannabis guide, genuine moment captured.

Ultra-high resolution, lifestyle photography quality, relatable and aspirational.

IMPORTANT: No faces visible, no identifiable facial features, shot from behind or side angles only.

Absolutely no text, no watermarks, no logos, no graphics, no artificial overlays."""

    print("📝 Prompt:")
    print(test_prompt[:200] + "...")
    print()

    try:
        # Generate unique task UUID
        task_uuid = str(uuid.uuid4())

        print(f"🔑 Task UUID: {task_uuid}")
        print("📤 Sending request to Runware API...")

        # Make API request
        response = requests.post(
            RUNWARE_ENDPOINT,
            headers={
                "Content-Type": "application/json"
            },
            json=[
                {
                    "taskType": "authentication",
                    "apiKey": RUNWARE_API_KEY
                },
                {
                    "taskType": "imageInference",
                    "taskUUID": task_uuid,
                    "positivePrompt": test_prompt,
                    "height": 1024,
                    "width": 1792,
                    "model": "runware:100@1",
                    "steps": 25,
                    "CFGScale": 7.0,
                    "numberResults": 1,
                    "outputType": "URL",
                    "outputFormat": "JPG"
                }
            ],
            timeout=90
        )

        print(f"📥 Response status: {response.status_code}")

        response.raise_for_status()
        response_data = response.json()

        print(f"📦 Raw response type: {type(response_data)}")
        print(f"📦 Raw response: {json.dumps(response_data, indent=2)[:500]}...")
        print()

        # Extract results from response (Runware wraps results in 'data' key)
        if isinstance(response_data, dict) and 'data' in response_data:
            results = response_data['data']
        elif isinstance(response_data, list):
            results = response_data
        else:
            results = [response_data]

        print(f"📦 Processed {len(results)} results")
        print()

        # Display all results
        for i, result in enumerate(results):
            if isinstance(result, dict):
                print(f"Result {i+1}:")
                print(f"  Task Type: {result.get('taskType')}")
                if result.get('taskType') == 'imageInference':
                    print(f"  Image UUID: {result.get('imageUUID')}")
                    print(f"  Image URL: {result.get('imageURL')}")
                    print(f"  Cost: ${result.get('cost', 0)}")
                print()

        # Find the image result
        image_result = None
        for result in results:
            if isinstance(result, dict) and result.get("taskType") == "imageInference":
                image_result = result
                break

        if not image_result:
            print("❌ No image inference result found")
            return False

        if not image_result.get("imageURL"):
            print("❌ No image URL in response")
            return False

        image_url = image_result["imageURL"]
        print(f"✅ Image generated successfully!")
        print(f"🔗 URL: {image_url}")
        print()

        # Download and save the test image
        print("📥 Downloading image...")
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()

        # Save to test directory
        test_dir = Path("test_output")
        test_dir.mkdir(exist_ok=True)

        # Save original
        test_image_path = test_dir / "test_runware_cannabis_mowing.jpg"

        # Open and optimize with Pillow
        image = Image.open(io.BytesIO(image_response.content))
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')

        image.save(
            test_image_path,
            "JPEG",
            quality=85,
            optimize=True,
            progressive=True
        )

        file_size_kb = os.path.getsize(test_image_path) / 1024
        print(f"💾 Image saved: {test_image_path}")
        print(f"📊 File size: {file_size_kb:.1f} KB")
        print(f"📐 Dimensions: {image.size[0]}x{image.size[1]}")
        print()
        print("✅ TEST PASSED - Runware API is working correctly!")
        print(f"👀 View your test image: {test_image_path}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ API Request failed: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_runware_image_generation()
    exit(0 if success else 1)
