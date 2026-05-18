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
    Build an optimized cannabis image prompt for Nano Banana 2 (google:4@3).

    Prompt structure: [Scene description] → [Composition] → [Style] → [Constraints]
    Mirrors content_generator.py — keep both in sync when updating.
    """
    person_types = [
        "man", "woman",
        "African American man", "African American woman",
        "Hispanic man", "Hispanic woman",
        "Asian man", "Asian woman",
        "middle-aged man", "middle-aged woman",
        "young adult man", "young adult woman",
    ]
    selected_person = random.choice(person_types)
    keyword_lower = keyword.lower()

    # Keyword buckets: each maps to (hero_scene, section_scene)
    # Hero: wide cinematic environmental shot | Section: tight detail/texture shot
    activities = {
        "strain": (
            f"close-up of multiple premium cannabis strain samples in small labeled glass jars "
            f"on a wooden dispensary-style counter, rich colors from bright green to deep "
            f"purple, soft warm lighting creating an elegant retail atmosphere",
            f"extreme close-up of a single dense cannabis bud showing complex trichome "
            f"coverage and vivid coloration, orange pistils and purple calyxes in sharp detail, "
            f"shallow depth of field, botanical photography"
        ),
        "review": (
            f"beautifully lit cannabis bud on a dark slate surface surrounded by small "
            f"botanical elements — citrus slice, pine sprig, lavender — editorial flat-lay, "
            f"soft studio lighting, premium lifestyle photography",
            f"extreme close-up of a cannabis bud with visible trichomes, deep green and "
            f"purple coloration, orange pistils, macro photography style, dark background"
        ),
        "profile": (
            f"premium cannabis flower displayed in an open glass jar on a natural wood surface, "
            f"deep green and purple bud with glistening resin visible, soft diffused light, "
            f"clean minimalist product photography aesthetic",
            f"close-up macro shot of cannabis flower trichomes, crystalline resin glands "
            f"in sharp focus, vivid colors, ultra-detailed botanical photography"
        ),
        "best strain": (
            f"elegant flat-lay of five different cannabis strain samples in small glass jars, "
            f"each a different color and texture, arranged on dark wood, soft studio lighting, "
            f"premium cannabis lifestyle photography",
            f"close-up of several cannabis buds side by side showing different colors and "
            f"trichome densities, comparison photography, macro detail, dark background"
        ),
        "top strain": (
            f"curated selection of premium cannabis buds displayed on a wooden board, "
            f"various strains with different hues — greens, purples, and golds — "
            f"soft warm lighting, editorial food photography aesthetic applied to cannabis",
            f"macro close-up of multiple cannabis buds showing diverse trichome patterns "
            f"and bud structures, vivid colors, professional botanical photography"
        ),
        "indica": (
            f"dense, compact indica cannabis buds in deep purple and forest green tones "
            f"displayed on a dark marble surface, soft warm ambient lighting, "
            f"premium strain photography with elegant lifestyle aesthetic",
            f"extreme close-up of a dense indica bud with heavy trichome coverage, "
            f"deep purple coloration, orange pistils curling through crystal-coated calyxes"
        ),
        "sativa": (
            f"elongated sativa cannabis buds in bright lime green and golden tones "
            f"displayed on a light wood surface with soft natural window light, "
            f"airy open bud structure, energetic premium lifestyle photography",
            f"close-up of a sativa bud with long orange pistils and visible trichomes, "
            f"bright green coloration, open fluffy structure, macro botanical photography"
        ),
        "hybrid": (
            f"selection of balanced hybrid cannabis strains displayed in elegant glass "
            f"containers on a modern countertop, mixed green and purple tones, "
            f"clean contemporary lifestyle photography",
            f"macro close-up of a hybrid cannabis bud showing balanced indica and sativa "
            f"bud structure, vivid trichomes, orange and green color mix, dark background"
        ),
        "terpene": (
            f"artistic flat-lay of cannabis buds surrounded by botanicals sharing terpene "
            f"profiles — lavender sprigs, citrus slices, pine needles, black pepper, mango — "
            f"arranged on a dark slate surface, elegant editorial photography",
            f"close-up of cannabis buds alongside terpene-matching botanicals, vivid colors "
            f"and natural textures, soft bokeh background, botanical science aesthetic"
        ),
        "entourage": (
            f"artistic arrangement of cannabis plant components — flower, leaves, and "
            f"botanical extracts in small vials — on a clean white laboratory surface, "
            f"scientific wellness photography, soft diffused light",
            f"close-up of cannabis trichomes and botanical elements, scientific detail "
            f"photography, various plant compounds visible, clean white background"
        ),
        "endocannabinoid": (
            f"clean modern scientific illustration aesthetic: cannabis leaf with soft "
            f"glowing neural network overlay on a dark background, science and wellness "
            f"photography, professional editorial style",
            f"close-up of cannabis plant structure with soft scientific bokeh, "
            f"editorial science photography, clean background, deep green tones"
        ),
        "cannabinoid": (
            f"clean modern cannabis laboratory with glass vials containing cannabis "
            f"extracts in amber and green tones, scientific equipment on the counter, "
            f"researcher in background, professional science photography",
            f"close-up of laboratory cannabis sample vials with amber liquid extracts, "
            f"scientific glassware, clean white lab aesthetic, soft lighting"
        ),
        "thc": (
            f"modern cannabis testing laboratory setting, glass sample vials and scientific "
            f"equipment on a clean white countertop, soft professional lighting, "
            f"science and wellness aesthetic",
            f"close-up of cannabis sample in a glass vial with THC percentage label, "
            f"laboratory setting, clean white background, scientific precision aesthetic"
        ),
        "cbd": (
            f"elegant CBD product collection — tincture bottles, capsules, and hemp flowers — "
            f"arranged on natural wood with soft green leaves, clean wellness photography, "
            f"natural window light, minimalist lifestyle aesthetic",
            f"close-up of a dropper releasing a golden CBD oil drop into a small glass bottle, "
            f"amber liquid catching soft light, hemp leaf blurred softly in background"
        ),
        "lab result": (
            f"{selected_person} reviewing a cannabis certificate of analysis document at a "
            f"clean desk, lab report visible with cannabinoid percentages, professional and "
            f"educational lifestyle photography",
            f"close-up of a cannabis lab results document showing THC, CBD, and terpene "
            f"percentages in clear print, professional document photography"
        ),
        "vaporiz": (
            f"premium dry herb vaporizer on a clean marble surface alongside a small "
            f"glass jar of cannabis flower, minimalist product photography, "
            f"soft diffused lighting, upscale lifestyle aesthetic",
            f"close-up of vaporizer heating chamber with cannabis flower, "
            f"warm product lighting, premium device detail photography"
        ),
        "edible": (
            f"artfully arranged cannabis-infused edibles — gummies, chocolates, and "
            f"mints — displayed on a wooden board with small hemp leaves as garnish, "
            f"soft natural lighting, upscale food photography aesthetic",
            f"close-up of colorful cannabis gummies in a small glass bowl, "
            f"vibrant colors and glossy surface, macro food photography style"
        ),
        "tincture": (
            f"glass tincture bottles with droppers arranged on a natural wood surface "
            f"with hemp flowers and leaves nearby, clean wellness product photography, "
            f"soft natural window light, minimal lifestyle aesthetic",
            f"close-up of a dropper tip with amber tincture liquid ready to dispense, "
            f"natural green background, wellness product macro photography"
        ),
        "concentrat": (
            f"collection of premium cannabis concentrates in small glass containers — "
            f"golden wax, clear shatter, and amber live resin — on a dark slate surface, "
            f"professional product photography with warm studio lighting",
            f"extreme close-up of golden cannabis concentrate showing crystalline "
            f"structure, warm amber tones, macro detail, dark background"
        ),
        "dispensary": (
            f"modern cannabis dispensary interior with illuminated display cases, "
            f"labeled strain jars under soft retail lighting, professional budtender "
            f"helping a customer, welcoming clean retail environment",
            f"close-up of a dispensary display case with labeled cannabis strain jars "
            f"showing strain names and THC percentages, clean glass case, soft lighting"
        ),
        "budtender": (
            f"friendly {selected_person} budtender in a clean cannabis dispensary, "
            f"explaining products to a customer across the counter, professional "
            f"retail setting, welcoming and educational atmosphere",
            f"close-up of a budtender's hands displaying a cannabis product jar with "
            f"label visible, clean dispensary counter, professional retail photography"
        ),
        "anxiety": (
            f"{selected_person} sitting peacefully in a sunlit living room, calm and "
            f"relaxed expression, soft natural light, clean wellness lifestyle photography, "
            f"green plants visible in background, serene home environment",
            f"close-up of hands cradling a warm cup of herbal tea with hemp leaves nearby, "
            f"soft warm lighting, wellness and calm aesthetic, natural tones"
        ),
        "sleep": (
            f"peaceful bedroom scene with soft bedside lamp, person resting comfortably "
            f"in a cozy bed, lavender plant on the nightstand, calm and serene "
            f"wellness photography, warm amber lighting",
            f"close-up of lavender sprigs and a small glass tincture bottle on "
            f"white linen, soft warm ambient light, sleep wellness aesthetic"
        ),
        "pain": (
            f"{selected_person} looking relaxed and comfortable in a modern living space, "
            f"natural light, wellness lifestyle photography, clean and calm home environment, "
            f"subtle cannabis plant element visible in background",
            f"close-up of hands holding a CBD topical cream jar with cannabis leaf design, "
            f"clean product photography, soft natural light, wellness aesthetic"
        ),
        "beginner": (
            f"{selected_person} browsing cannabis products at a modern dispensary, "
            f"curious and engaged expression, friendly budtender explaining options, "
            f"clean well-lit retail environment, educational lifestyle photography",
            f"close-up of a beginner's guide booklet or label next to a cannabis product, "
            f"informational and approachable, clean photography aesthetic"
        ),
        "legal": (
            f"state capitol building exterior under clear blue sky, American flags flying, "
            f"classic government architecture, civic photography aesthetic",
            f"close-up of cannabis legalization text in a state policy document, "
            f"American flag softly blurred in background, civic photography"
        ),
        "grow": (
            f"lush indoor cannabis grow room under warm LED lights, rows of healthy "
            f"cannabis plants in various stages, professional cultivation setup, "
            f"green and vibrant, wide environmental shot",
            f"close-up of cannabis plant leaves and developing buds under grow lights, "
            f"rich green coloration, healthy trichome development, macro cultivation photography"
        ),
        "cultivat": (
            f"outdoor cannabis garden under bright natural sunlight, tall healthy plants "
            f"with large fan leaves, blue sky backdrop, professional cultivation photography",
            f"close-up of a cannabis cola forming on a healthy outdoor plant, "
            f"bright natural light, vivid green and white trichomes, macro botanical photography"
        ),
        "germina": (
            f"cannabis seeds on a damp paper towel showing white taproots beginning to emerge, "
            f"warm soft lighting, close-up macro photography on a clean white surface, "
            f"cultivation how-to aesthetic",
            f"tiny cannabis seedling pushing up through dark moist soil, two cotyledon leaves "
            f"unfurling, water droplets on leaves, shallow depth of field, natural daylight"
        ),
        "harvest": (
            f"cannabis grower carefully trimming mature buds at a clean work station, "
            f"large dense colas with heavy trichome coverage, professional cultivation photography, "
            f"warm indoor lighting",
            f"close-up of freshly harvested cannabis buds covered in mature amber and clear "
            f"trichomes, rich colors, macro harvest photography"
        ),
        "soil": (
            f"rich dark organic cannabis soil in a terracotta pot with a young cannabis plant "
            f"thriving in it, natural daylight, clean cultivation aesthetic",
            f"close-up of dark healthy organic soil showing rich texture and structure, "
            f"cannabis roots visible at the edge, cultivation detail photography"
        ),
    }

    activity_hero, activity_section = None, None
    for key, (hero, section) in activities.items():
        if key in keyword_lower:
            activity_hero, activity_section = hero, section
            break

    if not activity_hero:
        activity_hero = (
            f"premium cannabis flower buds displayed in an open glass jar on a dark wood "
            f"surface, glistening trichomes and vivid green and purple coloration, "
            f"soft warm studio lighting, elegant lifestyle product photography"
        )
        activity_section = (
            f"extreme close-up of a dense cannabis bud with visible crystalline trichomes "
            f"and orange pistils, deep green and purple coloration, shallow depth of field, "
            f"soft bokeh background, macro botanical photography"
        )

    if image_type == "hero":
        prompt = (
            f"Professional editorial photograph: {activity_hero}. "
            f"Soft natural or studio light, warm tones, subtle shadows. "
            f"Wide cinematic composition, shallow depth of field on the subject. "
            f"Vivid saturated colors, ultra-sharp detail, photorealistic. "
            f"No text, no watermarks, no logos, no UI elements."
        )
    else:
        prompt = (
            f"Professional editorial photograph: {activity_section}. "
            f"Soft natural light with gentle bokeh background. "
            f"Tight composition, tack-sharp focus on the subject, rich textures. "
            f"Vivid saturated colors, photorealistic detail. "
            f"No text, no watermarks, no logos."
        )

    aspect_ratio = "16:9" if image_type == "hero" else "4:3"
    print(f"   📷 Keyword match: '{next((k for k in activities if k in keyword_lower), 'fallback')}' | Type: {image_type}")

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
    # Usage: python regenerate_images.py <slug> "<keyword>" [season]
    # Example: python regenerate_images.py blue-dream-strain-effects-review "Blue Dream strain effects and review" evergreen
    if len(sys.argv) < 3:
        print("Usage: python regenerate_images.py <slug> \"<keyword>\" [season]")
        print()
        print("Examples:")
        print('  python regenerate_images.py blue-dream-strain-effects-review "Blue Dream strain effects and review" evergreen')
        print('  python regenerate_images.py how-to-germinate-cannabis-seeds "how to germinate cannabis seeds" spring')
        print('  python regenerate_images.py cannabis-consumption-methods-compared "cannabis consumption methods compared" evergreen')
        sys.exit(1)

    slug = sys.argv[1]
    keyword = sys.argv[2]
    season = sys.argv[3] if len(sys.argv) > 3 else "evergreen"
    article_file = f"site/content/posts/{slug}.md"

    print(f"\n🌱 Regenerating Images for Article")
    print(f"File:    {article_file}")
    print(f"Slug:    {slug}")
    print(f"Keyword: {keyword}")
    print(f"Season:  {season}")
    print()

    if not Path(article_file).exists():
        print(f"⚠️  Warning: {article_file} not found — images will still be generated and saved.")
        print()

    # Generate hero image
    hero_path = generate_image(keyword, slug, season, image_type="hero")

    # Generate section image
    section_path = generate_image(keyword, slug, season, image_type="section")

    print()

    if hero_path:
        if Path(article_file).exists():
            print("📝 Updating article frontmatter...")
            update_markdown_frontmatter(article_file, hero_path, section_path)
            print()

        print("✅ IMAGE REGENERATION COMPLETE!")
        print(f"📄 Article: {article_file}")
        print(f"🖼️  Hero:    {hero_path}")
        if section_path:
            print(f"🖼️  Section: {section_path}")
    else:
        print("❌ Image generation failed")
        sys.exit(1)
