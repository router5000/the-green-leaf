#!/usr/bin/env python3
"""
Cannabis Content Generator with Claude Sonnet + Runware Image
Automated article creation with AI-generated featured images

AI Models:
- Claude 3.5 Sonnet (text generation) - High quality, fast
- Runware Image API (image generation) - Photorealistic quality, dual images per article
"""

import os
import json
import random
from datetime import datetime
from pathlib import Path
import base64
import io
import uuid
from dotenv import load_dotenv
import anthropic
import requests
from PIL import Image
from affiliate_linker import process_article_for_affiliates, generate_affiliate_metadata
from article_qa import quality_assurance_pipeline
from internal_linker import add_internal_links_to_new_article, load_article_index
from youtube_search import find_videos_for_article, format_video_for_frontmatter
from seo_validator import (
    validate_article, fix_article_issues, detect_cannibalization,
    get_cannibalization_recommendation, generate_smart_alt_text
)
from rate_limiter import wait_for_claude, wait_for_runware
from regenerate_images import IMAGE_SIZES, IMAGE_MODEL  # Central source of truth for image settings
from cost_tracker import CostTracker, set_tracker, get_tracker, clear_tracker

# Load environment variables from .env file
load_dotenv()

# Initialize API clients
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"), max_retries=3)

# Initialize Runware API client
runware_api_key = os.environ.get("RUNWARE_API_KEY")
runware_endpoint = "https://api.runware.ai/v1"

if runware_api_key:
    print("✅ Runware API key loaded")
else:
    print("⚠️  Runware API key not found in environment variables")
    runware_api_key = None

# Strain-focused topic bank mirroring keyword_research.py CONTENT_PILLARS
STRAIN_TOPICS = {
    "strain_database": [
        "Blue Dream strain effects and review",
        "OG Kush strain guide and terpenes",
        "Girl Scout Cookies strain profile",
        "Wedding Cake strain effects guide",
        "Gelato strain review and terpenes",
        "Northern Lights strain profile",
        "Granddaddy Purple strain effects",
        "Sour Diesel strain review",
        "Zkittlez strain review and terpenes",
        "Runtz strain effects and lineage",
    ],
    "strain_discovery": [
        "best indica strains for sleep 2026",
        "best strains for anxiety and stress",
        "best sativa strains for energy and focus",
        "high CBD low THC strains guide",
        "strongest THC strains 2026",
        "best strains for creativity and focus",
        "best strains for chronic pain relief",
        "best hybrid strains 2026",
        "top 10 cannabis strains 2026",
    ],
    "cannabis_education": [
        "indica vs sativa vs hybrid explained",
        "cannabis terpenes complete guide",
        "THC vs CBD vs CBN vs CBG explained",
        "entourage effect explained",
        "how to read cannabis lab results",
        "cannabis endocannabinoid system explained",
        "cannabis for beginners complete guide",
        "how to dose cannabis safely",
    ],
    "reviews_culture": [
        "how to choose the right cannabis strain",
        "cannabis consumption methods compared",
        "vaping vs smoking cannabis comparison",
        "cannabis edibles vs smoking onset times",
        "how to read a dispensary menu",
        "cannabis concentrates for beginners",
        "best cannabis vaporizers 2026",
        "how to talk to a budtender",
    ],
}

# High-intent question patterns for strain discovery
QUESTION_PATTERNS = [
    "What strains are best for {effect}",
    "Which strain is better for {use_case}",
    "What does {strain} feel like",
    "How strong is {strain}",
    "What terpenes are in {strain}",
    "What is the difference between {strain1} and {strain2}",
]

STRAIN_EFFECTS = [
    "sleep", "anxiety relief", "focus", "relaxation", "creativity",
    "pain relief", "energy", "mood boost", "appetite", "euphoria"
]

STRAIN_NAMES = [
    "Blue Dream", "OG Kush", "Girl Scout Cookies", "Sour Diesel",
    "Northern Lights", "Gelato", "Wedding Cake", "Granddaddy Purple"
]


def get_current_season():
    """Determine current season based on month"""
    month = datetime.now().month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "winter"


def categorize_article(title: str, keyword: str, tags: list) -> str:
    """Assign a category from the 4 content pillars based on title and keyword."""
    CLUSTERS = [
        # Pillar 1: individual strain profiles (named strains, lineage, terpene profiles)
        ("Strain Database", ["strain profile", "strain guide", "strain review", "lineage", "kush", "haze", "diesel", "cookies", "gelato", "runtz", "zkittlez", "wedding cake", "gorilla glue", "blue dream", "og kush", "northern lights", "granddaddy", "sour diesel", "purple punch", "pineapple express", "white widow", "bubba kush", "mac 1", "do-si-dos", "mimosa", "biscotti"]),
        # Pillar 2: roundups, recommendations, best-of lists
        ("Strain Discovery", ["best strains", "strains for", "top strains", "strains 2026", "best indica", "best sativa", "best hybrid", "high cbd", "high thc", "strongest", "most popular"]),
        # Pillar 3: education, science, compounds, how-it-works
        ("Cannabis Education", ["explained", "what is", "how does", "terpene guide", "cannabinoid", "endocannabinoid", "entourage effect", "indica vs", "sativa vs", "thca vs", "thc vs cbd", "pharmacology", "tolerance", "lab results", "certificate of analysis", "beginners guide", "microdosing"]),
        # Pillar 4: consumption, reviews, consumer decisions, culture
        ("Reviews & Culture", ["how to choose", "consumption methods", "vaping vs", "edibles vs", "dispensary", "budtender", "vaporizer", "concentrates", "live resin", "rosin", "hash", "pre-roll", "tincture", "topical", "tolerance break", "third-party testing", "packaging"]),
        # Supporting: wellness conditions (strain-selection context)
        ("Health & Wellness", ["anxiety", "pain", "sleep", "depression", "ptsd", "inflammation", "medical", "nausea", "migraines", "arthritis"]),
    ]
    title_kw = f"{title} {keyword} {' '.join(tags)}".lower()
    best_score, best_cat = 0, "Strain Discovery"
    for cat, keywords_list in CLUSTERS:
        score = sum(5 for kw in keywords_list if kw in title_kw)
        if score > best_score:
            best_score, best_cat = score, cat
    return best_cat


def build_image_prompt(keyword, season, image_type="hero"):
    """
    Build an optimized prompt for cannabis education images.

    Optimized for Nano Banana 2 (google:4@3) on Runware.
    Prompts are richly descriptive, scene-driven, and photorealistic.

    Prompt structure: [Scene description] → [Composition] → [Style] → [Constraints]

    Args:
        keyword: Target keyword for the article
        season: Current season (kept for API compatibility)
        image_type: "hero" for wide shot (16:9) or "section" for detail (4:3)

    Returns:
        tuple: (prompt_string, aspect_ratio, metadata_dict)
    """
    # Person diversity for representation
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

    # Activity descriptions by keyword theme
    # Each tuple: (hero_scene, section_scene)
    # Hero: wide cinematic environmental shot | Section: tight detail/texture shot
    activities = {
        # Strain profiles and individual strain articles
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
        # Best-of roundups and strain discovery
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
        # Terpenes and science
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
        # THC/CBD/science
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
        # Consumption methods
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
        # Wellness and effects
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
    }

    # Find matching activity or use generic cannabis fallback
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

    # Build prompt optimized for Nano Banana 2 (google:4@3)
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

    metadata = {
        "person_type": selected_person,
        "image_type": image_type,
        "season": season,
        "aspect_ratio": aspect_ratio
    }

    return prompt, aspect_ratio, metadata


def validate_image(image_bytes: bytes, expected_type: str = "hero") -> tuple[bool, str]:
    """
    Validate image is not blank, corrupt, or too small.

    Args:
        image_bytes: Raw image bytes from API response
        expected_type: "hero" or "section" for size expectations

    Returns:
        (is_valid: bool, error_message: str)
    """
    try:
        # Check file size first (too small = likely error)
        if len(image_bytes) < 10000:  # Less than 10KB
            return False, f"Image file too small: {len(image_bytes)} bytes"

        # Check image can be loaded (not corrupt)
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()  # Verify integrity
        image = Image.open(io.BytesIO(image_bytes))  # Re-open after verify

        # Check minimum dimensions
        min_sizes = {
            "hero": (1000, 500),
            "section": (800, 600)
        }
        min_w, min_h = min_sizes.get(expected_type, (500, 500))

        if image.width < min_w or image.height < min_h:
            return False, f"Image too small: {image.width}x{image.height}, minimum {min_w}x{min_h}"

        # Check not blank (pixel variance check)
        grayscale = image.convert("L")
        pixels = list(grayscale.getdata())

        mean = sum(pixels) / len(pixels)
        variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
        std_dev = variance ** 0.5

        if std_dev < 10:  # Very low variance = likely blank or solid color
            return False, f"Image appears blank or uniform (std_dev: {std_dev:.1f})"

        return True, "OK"

    except Exception as e:
        return False, f"Image validation failed: {str(e)}"


def _generate_image_via_runware(prompt: str, width: int, height: int, output_path: Path, image_type: str = "hero", max_retries: int = 2) -> bool:
    """
    Internal helper to generate an image via Runware API with validation and retry.

    Args:
        prompt: The image generation prompt
        width: Image width in pixels
        height: Image height in pixels
        output_path: Path to save the generated image
        image_type: "hero" or "section" for validation sizing
        max_retries: Number of retries on validation failure

    Returns:
        True if successful, False otherwise
    """
    for attempt in range(max_retries + 1):
        try:
            # Generate unique task UUID
            task_uuid = str(uuid.uuid4())

            # Rate limit Runware API calls
            wait_for_runware()

            # Call Runware Image API with Bearer token authentication
            response = requests.post(
                runware_endpoint,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {runware_api_key}"
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

            # Extract results from response (Runware wraps results in 'data' key)
            if isinstance(response_data, dict) and 'data' in response_data:
                results = response_data['data']
            elif isinstance(response_data, list):
                results = response_data
            else:
                results = [response_data]

            # Find the image result (skip authentication response)
            image_result = None
            for result in results:
                if isinstance(result, dict) and result.get("taskType") == "imageInference":
                    image_result = result
                    break

            if not image_result or not image_result.get("imageURL"):
                raise ValueError("No image URL in Runware API response")

            image_url = image_result["imageURL"]

            # Download the image from Runware's URL
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            image_bytes = image_response.content

            # Validate image before saving
            is_valid, validation_msg = validate_image(image_bytes, image_type)
            if not is_valid:
                print(f"   ⚠️  Image validation failed (attempt {attempt + 1}/{max_retries + 1}): {validation_msg}")
                if attempt < max_retries:
                    print(f"   🔄 Retrying image generation...")
                    continue
                else:
                    raise ValueError(f"Image validation failed after {max_retries + 1} attempts: {validation_msg}")

            # Open image with Pillow for optimization
            image = Image.open(io.BytesIO(image_bytes))

            # Convert to RGB if necessary (in case of RGBA)
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')

            # Ensure images directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save as optimized JPEG
            image.save(
                output_path,
                "JPEG",
                quality=85,
                optimize=True,
                progressive=True
            )

            # Log file size
            file_size_kb = os.path.getsize(output_path) / 1024
            print(f"   ✅ Image saved: {output_path} ({file_size_kb:.1f} KB)")

            return True

        except ValueError:
            raise
        except Exception as e:
            if attempt < max_retries:
                print(f"   ⚠️  Generation error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                continue
            raise

    return False


def generate_hero_image(keyword, slug, season):
    """
    Generate a hero image for the article using Runware Image API.

    Returns:
        tuple: (image_path, metadata_dict)
    """
    print(f"🎨 Generating hero image for: {keyword}")

    if runware_api_key is None:
        print("   ⚠️  Runware API not available, using default fallback image")
        return "/images/default-cannabis-hero.jpg", {}

    try:
        prompt, aspect_ratio, image_metadata = build_image_prompt(keyword, season, image_type="hero")
        width, height = IMAGE_SIZES["hero"]
        output_path = Path("site/public/images/articles") / f"{slug}.jpg"

        _generate_image_via_runware(prompt, width, height, output_path, image_type="hero")

        return f"/images/articles/{slug}.jpg", image_metadata

    except Exception as e:
        print(f"   ❌ Image generation failed: {e}")
        print("   Using default fallback image")
        return "/images/default-cannabis-hero.jpg", {}


def generate_section_image(keyword, slug, season, section_title):
    """
    Generate a detail/close-up image for mid-article section using Runware Image API.

    Returns:
        tuple: (image_path, metadata_dict) or (None, {}) if generation fails
    """
    print(f"   🎨 Generating section image for: {section_title}")

    if runware_api_key is None:
        print("   ⚠️  Runware API not available, skipping section image")
        return None, {}

    try:
        prompt, aspect_ratio, image_metadata = build_image_prompt(keyword, season, image_type="section")
        width, height = IMAGE_SIZES["section"]
        output_path = Path("site/public/images/articles") / f"{slug}-section.jpg"

        _generate_image_via_runware(prompt, width, height, output_path, image_type="section")

        return f"/images/articles/{slug}-section.jpg", image_metadata

    except Exception as e:
        print(f"   ❌ Section image generation failed: {e}")
        print("   Continuing without section image")
        return None, {}


def generate_alt_text(keyword, title, image_type="hero", image_prompt=None):
    """
    Generate SEO-friendly alt text for the image.

    Uses the smart alt text generator from seo_validator for better,
    more descriptive alt text that naturally incorporates keywords.
    """
    return generate_smart_alt_text(keyword, title, image_type, image_prompt)


def generate_keyword_ideas(count=5):
    """Generate keyword ideas based on season and patterns"""
    season = get_current_season()
    keywords = []
    
    # Add seasonal topics
    seasonal = random.sample(SEASONAL_TOPICS[season], min(count // 2, len(SEASONAL_TOPICS[season])))
    keywords.extend(seasonal)
    
    # Add question-based keywords
    for _ in range(count - len(keywords)):
        pattern = random.choice(QUESTION_PATTERNS)
        if "{action}" in pattern and "{event}" in pattern:
            keyword = pattern.format(
                action=random.choice(CANNABIS_ACTIONS),
                event=random.choice(["transplanting", "topping", "harvesting"])
            )
        elif "{action}" in pattern:
            keyword = pattern.format(action=random.choice(CANNABIS_ACTIONS))
        elif "{problem}" in pattern:
            keyword = pattern.format(problem=random.choice(CANNABIS_PROBLEMS))
        else:
            keyword = pattern
        keywords.append(keyword)
    
    return keywords


def build_video_highlights_section(insights: dict, video: dict) -> str:
    """
    Build a Video Highlights section from transcript insights.

    Args:
        insights: Dict with key_points, best_quote, pro_tips, etc.
        video: Video metadata dict

    Returns:
        Markdown string for the highlights section
    """
    if not insights:
        return ""

    lines = ["## Expert Video Insights", ""]

    # Add quote if available
    if insights.get("best_quote"):
        lines.append(f"> \"{insights['best_quote']}\"")
        lines.append(f"> — {video.get('channel', 'Video Expert')}")
        lines.append("")

    # Add key points
    key_points = insights.get("key_points", [])
    if key_points:
        lines.append("**Key Takeaways from the Video:**")
        lines.append("")
        for point in key_points[:4]:  # Limit to 4 points
            lines.append(f"- {point}")
        lines.append("")

    # Add pro tips
    pro_tips = insights.get("pro_tips", [])
    if pro_tips:
        lines.append("**Pro Tips:**")
        lines.append("")
        for tip in pro_tips[:3]:  # Limit to 3 tips
            lines.append(f"- {tip}")
        lines.append("")

    return "\n".join(lines)


def check_for_duplicate(keyword: str, threshold: float = 0.7):
    """
    Check if an article with a similar keyword already exists.

    Args:
        keyword: The keyword to check
        threshold: Similarity threshold (0.0 - 1.0)

    Returns:
        Dict with duplicate info if found, None otherwise
    """
    # Normalize keyword for comparison
    keyword_lower = keyword.lower().strip()
    keyword_words = set(keyword_lower.replace('-', ' ').split())

    # Load existing articles
    try:
        articles = load_article_index()
    except Exception:
        return None  # If we can't load articles, skip duplicate check

    for article in articles:
        # Check exact keyword match
        existing_keyword = article.get('keyword', '').lower().strip().strip('"')
        if existing_keyword == keyword_lower:
            return {
                'type': 'exact_keyword',
                'slug': article['slug'],
                'title': article['title'],
                'keyword': existing_keyword
            }

        # Check slug similarity
        slug_words = set(article['slug'].replace('-', ' ').split())
        if keyword_words and slug_words:
            overlap = len(keyword_words & slug_words) / max(len(keyword_words), len(slug_words))
            if overlap >= threshold:
                return {
                    'type': 'similar_slug',
                    'slug': article['slug'],
                    'title': article['title'],
                    'keyword': existing_keyword,
                    'similarity': overlap
                }

        # Check keyword word overlap
        existing_words = set(existing_keyword.replace('-', ' ').split())
        if keyword_words and existing_words:
            overlap = len(keyword_words & existing_words) / max(len(keyword_words), len(existing_words))
            if overlap >= threshold:
                return {
                    'type': 'similar_keyword',
                    'slug': article['slug'],
                    'title': article['title'],
                    'keyword': existing_keyword,
                    'similarity': overlap
                }

    return None


def generate_article(keyword: str, word_count: int = 900, enable_qa: bool = True, skip_duplicate_check: bool = False) -> dict:
    """Generate a complete article with structured content and section for mid-article image"""

    # Check for duplicates before generating
    if not skip_duplicate_check:
        duplicate = check_for_duplicate(keyword)
        if duplicate:
            print(f"\n⚠️  DUPLICATE DETECTED!")
            print(f"   Type: {duplicate['type']}")
            print(f"   Existing article: {duplicate['title']}")
            print(f"   Slug: {duplicate['slug']}")
            if duplicate.get('similarity'):
                print(f"   Similarity: {duplicate['similarity']:.0%}")
            raise ValueError(f"Duplicate article exists: {duplicate['slug']}")

        # Check for keyword cannibalization (similar but not duplicate)
        print("\n🔍 Checking for keyword cannibalization...")
        conflicts = detect_cannibalization(keyword, threshold=0.6)
        if conflicts:
            high_risk = [c for c in conflicts if c['similarity'] >= 0.8]
            if high_risk:
                print(f"\n⚠️  HIGH CANNIBALIZATION RISK!")
                print(get_cannibalization_recommendation(conflicts))
                print("\n   Conflicting articles:")
                for c in conflicts[:3]:
                    print(f"   • {c['slug']} ({int(c['similarity']*100)}% similar)")
                print("\n   Consider updating the existing article instead.")
                print("   Use --force to proceed anyway.\n")
                raise ValueError(f"Keyword cannibalization detected: {conflicts[0]['slug']}")
            else:
                print(f"   ℹ️  Found {len(conflicts)} similar article(s) - moderate risk")
                for c in conflicts[:2]:
                    print(f"      • {c['slug']} ({int(c['similarity']*100)}% similar)")
                print("   Proceeding with distinct content angle...")
        else:
            print("   ✅ No cannibalization detected")

    # Initialize cost tracker for this article
    # Slug will be set after we parse the response, use keyword for now
    slug_estimate = keyword.lower().replace(' ', '-').replace('?', '')[:50]
    cost_tracker = CostTracker(slug_estimate)
    set_tracker(cost_tracker)

    # Detect comparison-style keywords
    comparison_keywords = ["vs", "versus", "comparison", "difference between", "compared to"]
    is_comparison = any(ck in keyword.lower() for ck in comparison_keywords)

    comparison_instruction = """
COMPARISON TABLE (REQUIRED for this topic):
- Include a markdown comparison table with 3-5 rows comparing key attributes
- Use proper markdown table syntax with | separators and --- header row
- Add a clear caption line above the table (bold text describing what's compared)
- Example format:
  **Indica vs Sativa Effects Comparison**
  | Feature | Indica | Sativa |
  |---------|--------|--------|
  | Effects | Relaxing, body | Energizing, cerebral |
  | Best for | Evening, sleep | Daytime, creativity |
""" if is_comparison else ""

    # Detect article type to give content-specific instructions
    kw_lower = keyword.lower()
    is_strain_profile = any(name.lower() in kw_lower for name in [
        "blue dream", "og kush", "girl scout", "gorilla glue", "wedding cake",
        "gelato", "jack herer", "northern lights", "granddaddy purple", "sour diesel",
        "white widow", "ak-47", "amnesia haze", "pineapple express", "purple haze",
        "zkittlez", "runtz", "mac 1", "cereal milk", "ice cream cake", "london pound",
        "sherbet", "biscotti", "do-si-dos", "mimosa", "tropicana", "apple fritter",
        "banana runtz", "durban poison", "trainwreck", "super lemon haze",
        "strawberry cough", "green crack", "skywalker", "bubba kush", "purple punch",
        "chemdawg", "animal cookies", "gary payton"
    ]) or ("strain" in kw_lower and any(w in kw_lower for w in ["profile", "guide", "review", "effects", "lineage"]))

    is_roundup = any(w in kw_lower for w in ["best strains", "top strains", "strains for", "strains 2026", "high cbd", "high thc", "strongest"])

    strain_profile_instruction = """
STRAIN PROFILE REQUIREMENTS (this is a named strain article):
- Include a quick-reference strain card in this format near the top (after Quick Answer):
  **Strain Overview**
  | Attribute | Details |
  |-----------|---------|
  | Type | Indica / Sativa / Hybrid (and approximate split if known) |
  | THC Range | XX–XX% (typical range) |
  | CBD Range | <1% (or actual range) |
  | Top Terpenes | Myrcene, Caryophyllene, Limonene (list top 3) |
  | Lineage | Parent strains |
  | Best For | Top 3 use cases |
- Discuss: origin and genetics, appearance (bud structure, colors, trichomes), aroma and flavor profile, effects (onset, duration, intensity), medical uses, potential side effects, similar strains
- Be specific with percentages and terpene data where known — readers want the numbers
""" if is_strain_profile else ""

    roundup_instruction = """
ROUNDUP/BEST-OF REQUIREMENTS (this is a strain recommendation article):
- Include a comparison table of the top 5-8 recommended strains:
  | Strain | Type | THC% | Best For | Key Terpene |
  |--------|------|------|----------|-------------|
  | Blue Dream | Hybrid | 17–24% | Creativity, focus | Myrcene |
- For each strain in the list, provide: type, THC range, top terpenes, why it fits the use case
- Rank them in a logical order (most recommended first, or by intensity/use case)
- Be specific — readers are choosing a product and need real data to decide
""" if is_roundup else ""

    prompt = f"""You are an expert cannabis strain and education writer for The Green Leaf, a trusted cannabis information site focused on strain discovery, effects, terpenes, and helping consumers make informed choices.

Write a concise, SEO-optimized article for the keyword: "{keyword}"

SITE FOCUS: The Green Leaf covers strain profiles, strain recommendations, cannabis science (terpenes, cannabinoids), and consumer guides. We do NOT cover cultivation, growing techniques, or home growing.

Requirements:
- Target word count: 650-850 words (concise but complete)
- Write in a helpful, authoritative but approachable tone
- Start with a "Quick Answer" section (2-3 sentences directly answering the question)
- Include 3-5 "Key Takeaways" bullet points after the quick answer
- Structure with clear H2 and H3 headings
- Include specific, accurate data: THC/CBD percentages, terpene names, strain lineages
- Write for cannabis consumers, patients, and curious beginners — not cultivators
- IMPORTANT: Use proper markdown list syntax with hyphens (-), NOT bullet characters (•)
- Do NOT make medical claims or recommend cannabis as a treatment for any condition
- Do NOT include cultivation, growing, or harvest advice

GEO OPTIMIZATION (for AI citation):
- Use QUESTION-BASED H2 headings that match how people ask AI assistants
  Examples: "What Does Blue Dream Feel Like?", "Which Strains Are Best for Sleep?", "What's the Difference Between Indica and Sativa?"
- Write direct, factual answers that AI can easily extract and cite
- FAQs and key stats will be rendered separately via structured data — DO NOT include them in article content

Article Structure (IMPORTANT):
1. Title (H1)
2. Quick Answer paragraph (2-3 sentences)
3. Key Takeaways (3-5 bullet points)
4. Introduction paragraph
5. Main content with 3-4 H2 sections (USE QUESTION FORMAT for headings)
6. Conclusion with recommendation or next step for the reader
7. Sources section (REQUIRED) — "## Sources" with 4-6 authoritative references

NOTE: Do NOT include a "## Frequently Asked Questions" section — FAQs go in the JSON output field.
{strain_profile_instruction}{roundup_instruction}{comparison_instruction}

CRITICAL SOURCE REQUIREMENTS:

1. Cite 4-6 DIVERSE, topic-specific credible sources:
   - At least 1 peer-reviewed research source (PubMed, NCBI, Journal of Cannabis Research, Frontiers in Pharmacology)
   - At least 1 cannabis industry or consumer data source (Leafly, Weedmaps, Cannabis Business Times, Headset data)
   - At least 1 science or education source (Project CBD, NORML, American Cannabis Nurses Association, NIH)
   - Additional sources relevant to the specific topic (terpene research, strain databases, etc.)

2. Use CLICKABLE NUMBERED CITATIONS throughout the article text:
   - Format: "This is a fact[[1]](#user-content-fn-1)."
   - Place at the END of sentences, before the period
   - Aim for 8-12 citations distributed naturally across the article

3. End with "## Sources" section using anchor IDs:
   ```
   <a id="user-content-fn-1"></a>
   1. [Organization Name](https://example.org) - Specific resource description
   ```

Example Sources for strain/terpene topics:
## Sources
<a id="user-content-fn-1"></a>
1. [Leafly](https://www.leafly.com) - Cannabis strain database and consumer effects data
<a id="user-content-fn-2"></a>
2. [Project CBD](https://www.projectcbd.org) - Cannabinoid and terpene science research
<a id="user-content-fn-3"></a>
3. [National Institutes of Health](https://www.nih.gov) - Cannabis and cannabinoid clinical research
<a id="user-content-fn-4"></a>
4. [Journal of Cannabis Research](https://jcannabisresearch.biomedcentral.com) - Peer-reviewed cannabis science
<a id="user-content-fn-5"></a>
5. [NORML](https://norml.org) - Cannabis consumer research and policy data

IMPORTANT:
- Use main domain URLs (e.g., https://www.leafly.com) NOT deep links that may 404
- VARY sources by topic — terpene articles → terpene research; strain profiles → strain databases
- DO NOT use inline citation links like "[Leafly](url) says..." — only numbered citations [1]
- Choose sources genuinely relevant to the specific topic

Return the section title you recommend for the mid-article image in the JSON.

Output format (JSON):
{{
    "title": "SEO-optimized title (50-60 chars)",
    "meta_description": "Compelling meta description (150-160 chars)",
    "slug": "url-friendly-slug",
    "content": "Full article in Markdown format (NO FAQ section)",
    "tags": ["relevant", "tags", "for", "article"],
    "estimated_read_time": "X min read",
    "section_image_title": "Title of the H2 section where image should go (2nd main section)",
    "faqs": [
        {{"question": "Common question about the topic?", "answer": "Direct 2-3 sentence answer."}},
        {{"question": "Another relevant question?", "answer": "Clear, factual answer."}},
        {{"question": "Third question users ask?", "answer": "Helpful response."}},
        {{"question": "Fourth question?", "answer": "Concise answer."}}
    ],
    "key_stat": "Single most quotable statistic with specifics (e.g., 'Blue Dream typically tests at 17-24% THC with myrcene as its dominant terpene, accounting for its balanced cerebral and body effects.')",
    "tldr": "One sentence summary of the article (e.g., 'Blue Dream is a sativa-dominant hybrid with 17-24% THC that delivers a balanced euphoric head high with gentle body relaxation, making it ideal for daytime use.')"
}}

Return ONLY valid JSON, no other text."""

    # Rate limit Claude API calls
    wait_for_claude()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    # Log Claude API usage for cost tracking
    cost_tracker.log_claude_usage(message.usage, "claude-sonnet-4-6")

    response_text = message.content[0].text

    # Clean control characters that cause JSON parsing issues
    # Claude Haiku sometimes includes control characters in content
    import re
    def clean_json_string(text):
        # Remove ALL control characters except newline (\n), tab (\t), and carriage return (\r)
        # Using list comprehension for better performance on large texts
        result = []
        for char in text:
            code = ord(char)
            # Keep printable ASCII (32-126), extended ASCII (128-255), and whitespace
            if code >= 32 or char in '\n\t\r':
                result.append(char)
        return ''.join(result)

    # Clean the entire response first (this handles Claude Haiku's control characters)
    response_text = clean_json_string(response_text)

    # Parse JSON response with robust extraction
    try:
        article_data = json.loads(response_text)
    except json.JSONDecodeError as e:
        # If direct parsing fails, try extracting from markdown blocks
        # Note: response_text is already cleaned at this point
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0].strip()
            # Clean again in case extraction reintroduced issues
            json_str = clean_json_string(json_str)
            article_data = json.loads(json_str)
        elif "```" in response_text:
            # Try generic code block
            json_str = response_text.split("```")[1].split("```")[0].strip()
            # Remove language identifier if present
            if json_str.startswith("json\n"):
                json_str = json_str[5:]
            json_str = clean_json_string(json_str)
            article_data = json.loads(json_str)
        elif "{" in response_text and "}" in response_text:
            # Try to extract just the JSON object
            start = response_text.index("{")
            end = response_text.rindex("}") + 1
            json_str = response_text[start:end]
            json_str = clean_json_string(json_str)
            article_data = json.loads(json_str)
        else:
            print(f"   ❌ Raw response (first 500 chars): {repr(response_text[:500])}...")
            raise ValueError("Could not parse article JSON")
    
    # Add metadata
    article_data["keyword"] = keyword
    article_data["generated_at"] = datetime.now().isoformat()
    article_data["season"] = "evergreen"  # Strain/education content is not seasonal
    article_data["category"] = categorize_article(
        article_data.get("title", ""), keyword, article_data.get("tags", [])
    )
    article_data["status"] = "published"
    article_data["word_count"] = len(article_data["content"].split())

    # Update cost tracker with actual slug
    cost_tracker.article_slug = article_data["slug"]

    # Fix markdown list syntax (convert bullet chars to hyphens)
    article_data["content"] = re.sub(r'^• ', '- ', article_data["content"], flags=re.MULTILINE)

    # Generate images
    season = get_current_season()
    slug = article_data["slug"]

    # Generate hero image (16:9 ratio - see IMAGE_SIZES in regenerate_images.py)
    hero_image_path, hero_metadata = generate_hero_image(keyword, slug, season)
    article_data["featured_image"] = hero_image_path
    article_data["featured_image_alt"] = generate_alt_text(keyword, article_data["title"], "hero")
    article_data["hero_image_metadata"] = hero_metadata

    # Generate section image (4:3 ratio - see IMAGE_SIZES in regenerate_images.py)
    section_title = article_data.get("section_image_title", "Main Section")
    section_image_path, section_metadata = generate_section_image(keyword, slug, season, section_title)

    if section_image_path:
        article_data["section_image"] = section_image_path
        article_data["section_image_alt"] = generate_alt_text(keyword, section_title, "section")
        article_data["section_image_metadata"] = section_metadata

        # Insert image markdown into content at the appropriate H2 section
        content = article_data["content"]
        # Find the second H2 heading and insert image BEFORE it (at end of previous section)
        h2_count = 0
        lines = content.split("\n")
        new_lines = []
        image_inserted = False

        for i, line in enumerate(lines):
            # Check if this is the second H2 and we haven't inserted yet
            if line.startswith("## ") and not image_inserted:
                h2_count += 1
                if h2_count == 2:  # Before the second H2
                    new_lines.append("")  # Blank line
                    new_lines.append(f"![{article_data['section_image_alt']}]({section_image_path})")
                    new_lines.append("")  # Blank line
                    image_inserted = True
            new_lines.append(line)

        article_data["content"] = "\n".join(new_lines)
    else:
        article_data["section_image"] = None
        article_data["section_image_alt"] = None

    # Run QA evaluation and refinement pipeline (if enabled)
    if enable_qa:
        article_data = quality_assurance_pipeline(article_data)
    else:
        print("   ⚠️  QA pipeline skipped (disabled)")

    # Add affiliate links to content
    print("   🔗 Adding affiliate links...")
    affiliate_result = process_article_for_affiliates(article_data["content"], max_links=5)
    article_data["content"] = affiliate_result['content']
    article_data["has_affiliate_links"] = affiliate_result['has_affiliates']
    article_data["affiliate_count"] = affiliate_result['link_count']
    if affiliate_result['affiliate_links']:
        article_data["affiliate_links"] = affiliate_result['affiliate_links']
        print(f"   ✅ Inserted {affiliate_result['link_count']} affiliate links")
    else:
        print("   ℹ️  No affiliate link opportunities found")

    # Add internal links to related articles
    print("   🔗 Adding internal links...")
    try:
        linked_content, internal_links = add_internal_links_to_new_article(
            article_data["content"],
            article_data["slug"]
        )
        if internal_links:
            article_data["content"] = linked_content
            article_data["internal_link_count"] = len(internal_links)
            print(f"   ✅ Inserted {len(internal_links)} internal links")
            for link in internal_links:
                print(f"      → {link['anchor_text']} → {link['target_slug']}")
        else:
            print("   ℹ️  No internal link opportunities found")
    except Exception as e:
        print(f"   ⚠️  Internal linking failed: {e}")

    # ============================================
    # SEO VALIDATION & AUTO-FIX
    # ============================================
    print("\n🔍 Running SEO validation...")
    try:
        # Validate the article content
        validation = validate_article(article_data["content"], keyword)

        # Auto-fix any issues found
        if validation.get('link_issues') or validation.get('warnings'):
            fixed_content, fixes = fix_article_issues(article_data["content"])
            if fixes:
                article_data["content"] = fixed_content
                for fix in fixes:
                    print(f"   ✅ {fix}")

        # Report any remaining issues
        critical_issues = [i for i in validation.get('link_issues', [])
                          if i.get('severity') == 'critical']
        if critical_issues:
            print(f"   ⚠️  {len(critical_issues)} critical issue(s) remain - manual review needed")
            for issue in critical_issues:
                print(f"      • {issue['description']}")
        else:
            print("   ✅ SEO validation passed")

        # Store validation metadata
        article_data["seo_validated"] = validation.get('valid', True)

    except Exception as e:
        print(f"   ⚠️  SEO validation error: {e}")
        article_data["seo_validated"] = False

    # ============================================
    # YOUTUBE VIDEO SEARCH
    # ============================================
    print("\n📺 Searching for relevant YouTube videos...")

    try:
        videos = find_videos_for_article(
            keyword=keyword,
            article_title=article_data["title"],
            article_summary=article_data["meta_description"],
            use_curated_only=False,  # Set True to only use curated channels
            min_score=7.0,
            max_videos=2
        )

        if videos:
            # Format for frontmatter
            youtube_videos = [format_video_for_frontmatter(v) for v in videos]

            # Assign positions: first video = hero, second = section
            # Videos are rendered by React components (not shortcodes) to support collapsible insights
            if len(youtube_videos) >= 1:
                youtube_videos[0]["position"] = "hero"
            if len(youtube_videos) >= 2:
                youtube_videos[1]["position"] = "section"

            article_data["youtube"] = youtube_videos
            print(f"   ✅ Found {len(youtube_videos)} relevant video(s)")

            # Log if we have transcript insights (stored in frontmatter for UI rendering)
            videos_with_insights = [v for v in youtube_videos if v.get("insights")]
            if videos_with_insights:
                print(f"   ✅ {len(videos_with_insights)} video(s) have transcript insights (stored in frontmatter)")
        else:
            article_data["youtube"] = []
            print("   ⚠️  No relevant videos found")

    except Exception as e:
        print(f"   ❌ Video search error: {e}")
        article_data["youtube"] = []

    # Save cost tracking data
    cost_tracker.save()
    clear_tracker()

    return article_data


def save_to_notion_format(article: dict, output_dir: str = "drafts"):
    """Save article in a format ready for review"""
    Path(output_dir).mkdir(exist_ok=True)

    # Create markdown file with frontmatter
    filename = f"{article['slug']}.md"
    filepath = Path(output_dir) / filename

    # Build frontmatter with optional section image
    frontmatter_dict = {
        'title': article['title'],
        'meta_description': article['meta_description'],
        'slug': article['slug'],
        'keyword': article['keyword'],
        'featured_image': article.get('featured_image', '/images/default-cannabis-hero.jpg'),
        'featured_image_alt': article.get('featured_image_alt', article['title']),
        'tags': article['tags'],
        'status': 'published',
        'generated_at': article['generated_at'],
        'season': article['season'],
        'category': article.get('category', 'Cannabis Basics'),
        'estimated_read_time': article['estimated_read_time'],
        'word_count': article['word_count']
    }

    # Add section image if it exists
    if article.get('section_image'):
        frontmatter_dict['section_image'] = article['section_image']
        frontmatter_dict['section_image_alt'] = article['section_image_alt']

    # Add YouTube videos if they exist
    if article.get('youtube'):
        frontmatter_dict['youtube'] = article['youtube']

    # Add FAQs for GEO/AI citation (if present)
    if article.get('faqs'):
        frontmatter_dict['faqs'] = article['faqs']

    # Add key stat for quotable callout
    if article.get('key_stat'):
        frontmatter_dict['key_stat'] = article['key_stat']

    # Add TL;DR summary
    if article.get('tldr'):
        frontmatter_dict['tldr'] = article['tldr']

    # Add last_updated (same as generated_at initially)
    frontmatter_dict['last_updated'] = article.get('generated_at', datetime.now().isoformat())

    # Add affiliate link metadata
    if article.get('has_affiliate_links'):
        frontmatter_dict['has_affiliate_links'] = True
        frontmatter_dict['affiliate_count'] = article.get('affiliate_count', 0)

    # Add internal link count
    if article.get('internal_link_count'):
        frontmatter_dict['internal_link_count'] = article['internal_link_count']

    # Add QA metadata
    if article.get('qa_evaluation'):
        frontmatter_dict['qa_score'] = article['qa_evaluation']['scores']['overall']
        frontmatter_dict['qa_passed'] = article.get('qa_passed', False)
        frontmatter_dict['refinement_rounds'] = article.get('refinement_rounds', 0)
        if article.get('needs_manual_review'):
            frontmatter_dict['needs_manual_review'] = True

    # Format frontmatter
    frontmatter = "---\n"
    for key, value in frontmatter_dict.items():
        if key == 'youtube' and isinstance(value, list):
            # Special handling for YouTube videos - proper YAML array format with insights
            frontmatter += "youtube:\n"
            for video in value:
                frontmatter += f'  - id: "{video["id"]}"\n'
                frontmatter += f'    title: "{video["title"].replace(chr(34), chr(39))}"\n'
                frontmatter += f'    channel: "{video["channel"]}"\n'
                frontmatter += f'    position: "{video.get("position", "hero")}"\n'
                # Include transcript insights if available
                if video.get("insights"):
                    frontmatter += f'    insights:\n'
                    insights = video["insights"]
                    if insights.get("best_quote"):
                        # Escape quotes and newlines in the quote
                        quote = insights["best_quote"].replace('"', '\\"').replace('\n', ' ')
                        frontmatter += f'      best_quote: "{quote}"\n'
                    if insights.get("key_points"):
                        frontmatter += f'      key_points:\n'
                        for point in insights["key_points"][:4]:
                            point_clean = point.replace('"', '\\"').replace('\n', ' ')
                            frontmatter += f'        - "{point_clean}"\n'
                    if insights.get("pro_tips"):
                        frontmatter += f'      pro_tips:\n'
                        for tip in insights["pro_tips"][:3]:
                            tip_clean = tip.replace('"', '\\"').replace('\n', ' ')
                            frontmatter += f'        - "{tip_clean}"\n'
        elif key == 'faqs' and isinstance(value, list):
            # Special handling for FAQs - proper YAML array format
            frontmatter += "faqs:\n"
            for faq in value:
                question = faq.get("question", "").replace('"', '\\"').replace('\n', ' ')
                answer = faq.get("answer", "").replace('"', '\\"').replace('\n', ' ')
                frontmatter += f'  - question: "{question}"\n'
                frontmatter += f'    answer: "{answer}"\n'
        elif isinstance(value, list):
            frontmatter += f"{key}: {json.dumps(value)}\n"
        elif isinstance(value, str):
            frontmatter += f'{key}: "{value}"\n'
        else:
            frontmatter += f"{key}: {value}\n"
    frontmatter += "---\n\n"

    with open(filepath, "w") as f:
        f.write(frontmatter)
        f.write(article["content"])

    print(f"✓ Saved draft: {filepath}")
    print(f"  Hero image: {article.get('featured_image', 'N/A')}")
    if article.get('section_image'):
        print(f"  Section image: {article['section_image']}")
    return filepath


def save_article_json(article: dict, output_dir: str = "drafts/json"):
    """Save raw article data as JSON for programmatic access"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    filename = f"{article['slug']}.json"
    filepath = Path(output_dir) / filename
    
    with open(filepath, "w") as f:
        json.dump(article, f, indent=2)
    
    return filepath


def generate_content_batch(count: int = 3, enable_qa: bool = True):
    """Generate a batch of articles based on trending keywords"""
    print(f"\n🌱 Cannabis Content Generator")
    print(f"Season: {get_current_season().upper()}")
    print(f"Generating {count} articles...")
    print(f"QA Pipeline: {'✅ Enabled' if enable_qa else '⚠️ Disabled'}\n")

    keywords = generate_keyword_ideas(count)
    articles = []

    for i, keyword in enumerate(keywords, 1):
        print(f"[{i}/{count}] Generating article for: {keyword}")
        try:
            article = generate_article(keyword, enable_qa=enable_qa)
            save_to_notion_format(article)
            save_article_json(article)
            articles.append(article)
            print(f"    Title: {article['title']}")
            print(f"    Words: {article['word_count']}")
            if enable_qa and article.get('qa_passed'):
                print(f"    QA Score: {article['qa_evaluation']['scores']['overall']:.1f}/10 ✅")
            print()
        except Exception as e:
            print(f"    ❌ Error: {e}\n")
    
    # Save batch summary
    summary = {
        "generated_at": datetime.now().isoformat(),
        "season": get_current_season(),
        "total_articles": len(articles),
        "articles": [
            {
                "title": a["title"],
                "slug": a["slug"],
                "keyword": a["keyword"],
                "status": a["status"]
            }
            for a in articles
        ]
    }
    
    with open("drafts/batch_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Generated {len(articles)} articles")
    print(f"📁 Drafts saved to: ./drafts/")
    print(f"📋 Review and move approved articles to ./content/posts/")
    
    return articles


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate cannabis education content")
    parser.add_argument("--count", type=int, default=3, help="Number of articles to generate")
    parser.add_argument("--keyword", type=str, help="Generate for specific keyword")
    parser.add_argument("--with-qa", action="store_true", default=True, help="Enable QA pipeline (default)")
    parser.add_argument("--no-qa", action="store_true", help="Disable QA pipeline (faster, lower cost)")
    parser.add_argument("--force", action="store_true", help="Skip duplicate check and force generation")
    parser.add_argument("--publish", action="store_true", help="Auto-publish after generation (promote draft, commit, push)")

    args = parser.parse_args()

    # Determine QA setting
    enable_qa = not args.no_qa

    if args.keyword:
        print(f"Generating article for: {args.keyword}")
        article = generate_article(args.keyword, enable_qa=enable_qa, skip_duplicate_check=args.force)
        save_to_notion_format(article)
        save_article_json(article)
        print(f"✅ Generated: {article['title']}")
        if enable_qa and article.get('qa_passed'):
            print(f"   QA Score: {article['qa_evaluation']['scores']['overall']:.1f}/10 ✅")

        if args.publish:
            from auto_publish import auto_publish
            slug = article.get('slug', '')
            print(f"\n📤 Auto-publishing: {slug}")
            success = auto_publish(slug=slug)
            if success:
                print("✅ Published and pushed to remote")
            else:
                print("❌ Auto-publish failed — check logs/auto_publish.log")
    else:
        generate_content_batch(args.count, enable_qa=enable_qa)
