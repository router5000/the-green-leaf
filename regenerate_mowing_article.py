#!/usr/bin/env python3
"""
Regenerate images and add sources for lawn-mowing-tips article
"""

import os
import sys
import json
import uuid
import requests
from pathlib import Path
from PIL import Image
import io
import random

# Runware API configuration
RUNWARE_API_KEY = "aSGjkn0N1yQ019hlPP62INlzuwryN1vA"
RUNWARE_ENDPOINT = "https://api.runware.ai/v1"

def build_image_prompt(keyword, season, image_type="hero"):
    """Build optimized prompt for lawn mowing images"""

    angles = ["eye level candid angle", "low angle from grass perspective", "slightly overhead documentary style"]
    moods = ["early morning dew", "golden hour warmth", "bright midday clarity", "soft evening light"]
    compositions = ["rule of thirds composition", "candid off-center framing", "environmental portrait style"]

    camera_specs = "Shot with professional DSLR camera, Canon EOS R5 with 24-70mm f/2.8 lens, candid documentary photography style"

    selected_angle = random.choice(angles)
    selected_mood = random.choice(moods)
    selected_composition = random.choice(compositions)

    photo_techniques = f"natural shallow depth of field, candid authentic moment, {selected_composition}"

    season_lighting = {
        "spring": "soft diffused morning sunlight filtering through clouds, fresh dew drops catching light on grass blades, pink cherry blossoms or white dogwood trees blooming in background",
        "summer": "warm golden hour backlight (late afternoon sun), clear azure blue sky, vibrant saturated green colors, long shadows creating depth",
        "fall": "warm directional autumn afternoon light at 45-degree angle, orange and red maple leaves scattered on ground, crisp clear air, warm color temperature",
        "winter": "overcast soft natural light, subtle frost highlighting grass blade edges, bare tree silhouettes in background, cool color temperature"
    }

    # Lawn mowing specific activities
    if image_type == "hero":
        activity = "Candid action shot of person pushing walk-behind lawn mower across yard, photographed from behind or side angle (face not visible), wearing casual outdoor clothes, fresh mowing stripes visible behind them, mid-stride natural movement"
        base = "Candid documentary-style photograph of person performing lawn care"
        composition = "Wide environmental shot showing person in their yard, authentic moment"
    else:
        activity = "Close-up of person's hands on mower handle, showing grip and control, freshly cut grass being discharged, focus on the hands-on lawn care action"
        base = "Close-up candid photograph of hands-on lawn care work"
        composition = "Tight framing on hands and task, showing authentic effort"

    prompt_parts = [
        f"{base}, {activity}.",
        f"{camera_specs}. {composition}. {selected_angle} perspective.",
        f"Person shot from behind, side angle, or overhead - FACE NOT VISIBLE, no identifiable facial features, back of head or body only.",
        f"Lighting: {season_lighting.get(season, 'natural diffused daylight, soft shadows')}. {selected_mood} atmosphere.",
        f"Photography style: {photo_techniques}, natural moment captured, authentic real-life scene, ultra-sharp focus.",
        "Casual authentic work clothes appropriate for lawn care - jeans, t-shirt, work gloves, boots - realistic worn-in appearance.",
        "Suburban residential setting, well-maintained yard, real homeowner doing their own lawn care.",
        "Candid documentary feel: person mid-action, natural body language, unposed authentic moment, real work in progress.",
        "Color grading: natural realistic tones, vibrant greens, slight warmth, authentic documentary style.",
        "Photorealistic quality: looks like real candid photograph from home improvement blog or lawn care guide, genuine moment captured.",
        "Ultra-high resolution, lifestyle photography quality, relatable and aspirational.",
        "IMPORTANT: No faces visible, no identifiable facial features, shot from behind or side angles only.",
        "Absolutely no text, no watermarks, no logos, no graphics, no artificial overlays."
    ]

    prompt = "\n".join([p for p in prompt_parts if p]).strip()
    aspect_ratio = "16:9" if image_type == "hero" else "4:3"

    return prompt, aspect_ratio


def generate_image(keyword, slug, season, image_type="hero"):
    """Generate a single image using Runware API"""

    print(f"🎨 Generating {image_type} image for: {keyword}")

    try:
        prompt, aspect_ratio = build_image_prompt(keyword, season, image_type)

        if image_type == "hero":
            width, height = 1792, 1024
        else:
            width, height = 1536, 1152

        task_uuid = str(uuid.uuid4())

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
                    "positivePrompt": prompt,
                    "height": height,
                    "width": width,
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

        response.raise_for_status()
        response_data = response.json()

        if isinstance(response_data, dict) and 'data' in response_data:
            results = response_data['data']
        else:
            results = [response_data]

        image_result = None
        for result in results:
            if isinstance(result, dict) and result.get("taskType") == "imageInference":
                image_result = result
                break

        if not image_result or not image_result.get("imageURL"):
            raise ValueError("No image URL in response")

        image_url = image_result["imageURL"]
        print(f"   ✅ Generated: {image_url}")

        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()

        image = Image.open(io.BytesIO(image_response.content))
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')

        images_dir = Path("site/public/images/articles")
        images_dir.mkdir(parents=True, exist_ok=True)

        if image_type == "hero":
            image_path = images_dir / f"{slug}.jpg"
            web_path = f"/images/articles/{slug}.jpg"
        else:
            image_path = images_dir / f"{slug}-section.jpg"
            web_path = f"/images/articles/{slug}-section.jpg"

        image.save(
            image_path,
            "JPEG",
            quality=85,
            optimize=True,
            progressive=True
        )

        file_size_kb = os.path.getsize(image_path) / 1024
        print(f"   💾 Saved: {image_path} ({file_size_kb:.1f} KB)")

        return web_path

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return None


if __name__ == "__main__":
    article_file = "site/content/posts/lawn-mowing-tips.md"
    keyword = "lawn mowing tips"
    slug = "lawn-mowing-tips"
    season = "fall"

    print(f"\n🌱 Regenerating Images for Lawn Mowing Tips Article")
    print(f"File: {article_file}")
    print(f"Keyword: {keyword}")
    print(f"Season: {season}")
    print()

    # Generate hero image
    hero_path = generate_image(keyword, slug, season, image_type="hero")

    # Generate section image
    section_path = generate_image(keyword, slug, season, image_type="section")

    print()

    if hero_path and section_path:
        print("✅ IMAGE GENERATION COMPLETE!")
        print(f"🖼️  Hero image: {hero_path}")
        print(f"🖼️  Section image: {section_path}")
        print()
        print("Next steps will update the article...")
    else:
        print("❌ Image generation failed")
        sys.exit(1)
