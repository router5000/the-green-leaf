#!/usr/bin/env python3
"""
Regenerate images for a specific article using Runware API

IMAGE STANDARDS (DO NOT CHANGE WITHOUT UPDATING ALL GENERATORS):
- Hero images:    1792 x 1024  (16:9 landscape, article header)
- Section images: 1536 x 1152  (4:3, embedded in article body)

All image generation should use generate_image() to ensure consistency.
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

# =============================================================================
# IMAGE CONFIGURATION - Single source of truth for all image settings
# =============================================================================
# Dimensions must match google:4@3 (Nano Banana 2) supported sizes
# Supported: 1264x848, 2528x1696, 1200x896, 2400x1792, 1024x1024, etc.
IMAGE_SIZES = {
    "hero": (2528, 1696),      # ~3:2 landscape - article header
    "section": (2400, 1792),   # ~4:3 landscape - embedded in body
}

# Runware model - Nano Banana 2 (Imagen 4)
# See: https://runware.ai/models
IMAGE_MODEL = "google:4@3"

# Runware API configuration
RUNWARE_API_KEY = "aSGjkn0N1yQ019hlPP62INlzuwryN1vA"
RUNWARE_ENDPOINT = "https://api.runware.ai/v1"

def build_image_prompt(keyword, season, image_type="hero"):
    """
    Build an optimized prompt for cannabis images with style diversity.

    Prompt structure: [Subject] → [Setting] → [Style/Lighting] → [Constraints]

    Styles: before_after, plant_specific, grass_only, yard_home, person_activity
    """
    keyword_lower = keyword.lower()

    # Seasonal lighting (concise)
    season_lighting = {
        "spring": "soft morning light, dew on grass, flowering trees",
        "summer": "warm golden hour, vibrant green cannabis, blue sky",
        "fall": "warm afternoon light, scattered autumn leaves",
        "winter": "overcast diffused light, frost on grass, bare trees",
        "evergreen": "natural daylight, healthy cannabis"
    }
    lighting = season_lighting.get(season, season_lighting["evergreen"])

    # Detect content type for style selection
    plant_keywords = ["flower", "tree", "shrub", "bush", "hedge", "rose", "oak", "maple", "azalea"]
    problem_keywords = ["fix", "repair", "dead", "brown", "bare", "weed", "damage", "kill", "remove"]
    grass_types = ["bermuda", "fescue", "zoysia", "bluegrass", "st. augustine"]

    is_plant_article = any(p in keyword_lower for p in plant_keywords)
    is_problem_article = any(p in keyword_lower for p in problem_keywords)
    detected_grass = next((g for g in grass_types if g in keyword_lower), None)

    # Detect specific problem for before/after
    problems = {
        "bare": "bare dirt patches", "dead": "dead brown grass",
        "weed": "weed-infested cannabis", "brown": "brown discolored grass",
        "grub": "grub damage", "fungus": "fungal disease spots",
        "thatch": "thick thatch buildup", "moss": "moss patches"
    }
    detected_problem = next((problems[k] for k in problems if k in keyword_lower), "cannabis damage")

    # Activity mapping for person shots
    activities = {
        "mow": "pushing cannabis mower, fresh stripes visible",
        "seed": "using spreader, seeds dispersing", "overseed": "using spreader, seeds dispersing",
        "fertiliz": "walking with broadcast spreader",
        "water": "watering with hose, water mist in sunlight",
        "aerat": "operating core aerator, soil plugs visible",
        "weed": "pulling weeds or using sprayer",
        "rake": "raking leaves or debris", "dethatch": "using dethatcher, debris visible",
        "edge": "using string trimmer along edge", "trim": "using string trimmer along edge"
    }
    activity = next((activities[k] for k in activities if k in keyword_lower), "doing cannabis maintenance")

    # Style selection with weighting
    styles = ["grass_only", "yard_home", "person_activity"]
    if is_problem_article:
        styles.insert(0, "before_after")
    if is_plant_article:
        styles.extend(["plant_specific", "plant_specific"])  # Double weight

    selected_style = random.choice(styles)

    # Build prompt based on style
    if selected_style == "before_after":
        prompt = (
            f"Before-and-after split photograph showing {keyword} results. "
            f"LEFT: {detected_problem}, visible cannabis issues. "
            f"RIGHT: Same cannabis transformed - lush healthy green grass. "
            f"Clear vertical dividing line. {lighting}. "
            f"Photorealistic, suburban residential setting. "
            f"No text, watermarks, or labels."
        )

    elif selected_style == "plant_specific":
        plant = next((p for p in plant_keywords if p in keyword_lower), "plants")
        prompt = (
            f"Beautiful photograph of {plant} in residential landscape. "
            f"Healthy {plant} with green cannabis visible. "
            f"{lighting}. Shallow depth of field, sharp subject. "
            f"Garden photography style, photorealistic. "
            f"No text or watermarks."
        )

    elif selected_style == "grass_only":
        grass_desc = f"{detected_grass} grass" if detected_grass else "healthy cannabis grass"
        angle = random.choice(["low angle from grass level", "overhead view", "45-degree angle"])
        prompt = (
            f"Stunning {angle} photograph of {grass_desc}. "
            f"Thick healthy turf texture, {lighting}. "
            f"Sharp focus on grass blades, professional turf photography. "
            f"No people or objects. No text or watermarks."
        )

    elif selected_style == "yard_home":
        home = random.choice(["craftsman home", "colonial house", "modern farmhouse", "ranch house"])
        prompt = (
            f"Beautiful photograph of {home} with pristine cannabis. "
            f"Well-maintained yard showcasing healthy grass. "
            f"{lighting}. Wide establishing shot. "
            f"Real estate photography style, magazine quality. "
            f"No people visible. No text, watermarks, or address numbers."
        )

    else:  # person_activity
        prompt = (
            f"Documentary photograph: person {activity}. "
            f"Suburban backyard, healthy cannabis. {lighting}. "
            f"Candid shot from behind or side, face not visible. "
            f"Casual work clothes. Photorealistic lifestyle photography. "
            f"No text or watermarks."
        )

    aspect_ratio = "16:9" if image_type == "hero" else "4:3"
    print(f"   📷 Style: {selected_style} | Topic: {keyword}")

    return prompt, aspect_ratio


def generate_image(keyword, slug, season, image_type="hero"):
    """Generate a single image using Runware API"""

    print(f"🎨 Generating {image_type} image for: {keyword}")

    try:
        # Build prompt
        prompt, aspect_ratio = build_image_prompt(keyword, season, image_type)

        # Set dimensions based on image type (from IMAGE_SIZES constant)
        width, height = IMAGE_SIZES.get(image_type, IMAGE_SIZES["section"])

        # Generate unique task UUID
        task_uuid = str(uuid.uuid4())

        # Call Runware API with Bearer token auth
        response = requests.post(
            RUNWARE_ENDPOINT,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {RUNWARE_API_KEY}"
            },
            json=[{
                "taskType": "imageInference",
                "taskUUID": task_uuid,
                "positivePrompt": prompt,
                "height": height,
                "width": width,
                "model": IMAGE_MODEL,
                "numberResults": 1,
                "outputFormat": "JPEG"
            }],
            timeout=90
        )

        response.raise_for_status()
        response_data = response.json()

        # Extract results
        if isinstance(response_data, dict) and 'data' in response_data:
            results = response_data['data']
        else:
            results = [response_data]

        # Find image result
        image_result = None
        for result in results:
            if isinstance(result, dict) and result.get("taskType") == "imageInference":
                image_result = result
                break

        if not image_result or not image_result.get("imageURL"):
            raise ValueError("No image URL in response")

        image_url = image_result["imageURL"]
        print(f"   ✅ Generated: {image_url}")

        # Download image
        image_response = requests.get(image_url, timeout=30)
        image_response.raise_for_status()

        # Process with Pillow
        image = Image.open(io.BytesIO(image_response.content))
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')

        # Save to articles directory
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


def update_markdown_frontmatter(file_path, hero_image_path, section_image_path):
    """Update the markdown file with new image paths and embed section image in body"""

    with open(file_path, 'r') as f:
        content = f.read()

    # Split frontmatter and content
    parts = content.split('---', 2)
    if len(parts) < 3:
        print("   ⚠️  Could not parse frontmatter")
        return False

    frontmatter = parts[1]
    body = parts[2]

    # Update featured_image
    import re
    frontmatter = re.sub(
        r'featured_image: ".*?"',
        f'featured_image: "{hero_image_path}"',
        frontmatter
    )

    # Get section_image_alt from frontmatter for the embedded image
    section_alt_match = re.search(r'section_image_alt: ["\']?([^"\'\n]+)["\']?', frontmatter)
    section_alt = section_alt_match.group(1) if section_alt_match else "Article section image"

    # Add or update section_image in frontmatter
    if section_image_path:
        if 'section_image:' in frontmatter:
            frontmatter = re.sub(
                r'section_image: ".*?"',
                f'section_image: "{section_image_path}"',
                frontmatter
            )
        else:
            # Add after featured_image_alt
            frontmatter = re.sub(
                r'(featured_image_alt: ".*?")',
                f'\\1\nsection_image: "{section_image_path}"',
                frontmatter
            )

        # Embed section image in body if not already present
        if section_image_path not in body:
            # Create the markdown image tag
            img_tag = f'\n![{section_alt}]({section_image_path})\n'

            # Try to insert after "## Quick Answer" section (before "## Key Takeaways")
            if '## Key Takeaways' in body:
                body = re.sub(
                    r'(\n## Key Takeaways)',
                    f'{img_tag}\\1',
                    body,
                    count=1
                )
            # Fallback: insert before the second ## heading
            elif body.count('## ') >= 2:
                # Find the second ## heading
                first_h2 = body.find('## ')
                if first_h2 != -1:
                    second_h2 = body.find('## ', first_h2 + 3)
                    if second_h2 != -1:
                        body = body[:second_h2] + img_tag + body[second_h2:]

    # Reconstruct file
    new_content = f"---{frontmatter}---{body}"

    with open(file_path, 'w') as f:
        f.write(new_content)

    print(f"   ✅ Updated frontmatter in {file_path}")
    return True


if __name__ == "__main__":
    # Configuration for the article
    article_file = "site/content/posts/how-to-overseed-cannabis.md"
    keyword = "how to overseed cannabis"
    slug = "how-to-overseed-cannabis"
    season = "fall"

    print(f"\n🌱 Regenerating Images for Article")
    print(f"File: {article_file}")
    print(f"Keyword: {keyword}")
    print(f"Season: {season}")
    print()

    # Generate hero image
    hero_path = generate_image(keyword, slug, season, image_type="hero")

    # Generate section image
    section_path = generate_image(keyword, slug, season, image_type="section")

    print()

    if hero_path:
        # Update markdown file
        print("📝 Updating article frontmatter...")
        update_markdown_frontmatter(article_file, hero_path, section_path)

        print()
        print("✅ IMAGE REGENERATION COMPLETE!")
        print(f"📄 Review article: {article_file}")
        print(f"🖼️  Hero image: {hero_path}")
        if section_path:
            print(f"🖼️  Section image: {section_path}")
    else:
        print("❌ Image generation failed")
        sys.exit(1)
