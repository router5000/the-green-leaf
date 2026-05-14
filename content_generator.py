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

# Seasonal cannabis topics (outdoor growing calendar)
SEASONAL_TOPICS = {
    "spring": [
        "how to germinate cannabis seeds",
        "cannabis seedling care guide",
        "when to transplant cannabis outdoors",
        "best cannabis strains for outdoor growing",
        "feminized vs autoflower seeds explained",
    ],
    "summer": [
        "cannabis vegetative stage nutrients guide",
        "how to top cannabis plants",
        "low stress training LST cannabis guide",
        "how to identify cannabis nutrient deficiencies",
        "cannabis pH and EC guide",
        "spider mites on cannabis treatment",
        "SCROG method for cannabis explained",
    ],
    "fall": [
        "when to harvest cannabis plants",
        "how to read cannabis trichomes for harvest",
        "how to dry cannabis buds properly",
        "cannabis curing guide for beginners",
        "wet trimming vs dry trimming cannabis",
    ],
    "winter": [
        "indoor cannabis growing guide for beginners",
        "best LED grow lights for cannabis 2026",
        "cannabis grow tent setup guide",
        "hydroponic cannabis growing DWC guide",
        "autoflower cannabis grow guide",
        "cannabis VPD chart explained",
        "cannabis light cycle for flowering",
    ]
}

# High-intent question patterns (People Also Ask style)
QUESTION_PATTERNS = [
    "How often should I {action} my cannabis plants",
    "What is the best time to {action}",
    "Why are my cannabis plants {problem}",
    "How to fix {problem} in cannabis plants",
    "Should I {action} before or after {event}",
    "What causes {problem} in cannabis",
    "How long does it take to {action}",
]

CANNABIS_ACTIONS = [
    "water", "feed nutrients", "top", "harvest", "flush",
    "transplant", "train", "cure", "defoliate"
]

CANNABIS_PROBLEMS = [
    "turning yellow", "showing nutrient deficiency", "wilting",
    "not flowering", "getting light burn", "growing slowly", "curling leaves"
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
    """Assign a cannabis category based on title, keyword, and tags."""
    CLUSTERS = [
        ("Growing Techniques", ["grow", "growing", "germinate", "seedling", "transplant", "train", "top", "fim", "scrog", "lst", "sog", "defoliat", "clone", "autoflower", "hydroponic", "nutrient", "harvest", "cure", "dry", "trim"]),
        ("Strains & Effects", ["strain", "indica", "sativa", "hybrid", "terpene", "effect", "review", "kush", "haze", "diesel", "cookies", "gelato", "og ", "purple", "blue dream"]),
        ("Cannabis Science", ["cannabinoid", "thc", "cbd", "cbn", "cbg", "terpene", "endocannabinoid", "pharmacology", "thca", "extraction", "entourage"]),
        ("Health & Wellness", ["anxiety", "pain", "sleep", "medical", "wellness", "health", "dose", "dosage", "ptsd", "inflammation", "nausea", "microdose"]),
        ("Legal & Policy", ["legal", "law", "state", "dispensary", "possession", "license", "legalization", "policy", "regulation", "expunge"]),
        ("Products & Consumption", ["vaporizer", "vape", "edible", "tincture", "concentrate", "dab", "pipe", "joint", "bong", "consume", "smoke", "product"]),
    ]
    title_kw = f"{title} {keyword}".lower()
    best_score, best_cat = 0, "Cannabis Basics"
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
        "germinate": (
            f"cannabis seeds arranged on a damp paper towel inside a clear plastic container, "
            f"small white taproots just beginning to emerge from the dark seeds, "
            f"warm wooden surface in soft background, natural light from a nearby window",
            f"extreme macro close-up of a cannabis seed with a white taproot curling out, "
            f"water droplets glistening on the seed surface, shallow depth of field, "
            f"dark rich texture against a clean white paper towel"
        ),
        "seedling": (
            f"healthy cannabis seedling in a small black nursery pot, two bright green cotyledon "
            f"leaves fully spread with a tiny serrated first true leaf emerging between them, "
            f"sitting on a wooden grow bench under warm LED light, clean grow room background",
            f"close-up of cannabis seedling cotyledons and first true leaf, vivid lime green "
            f"color, fine leaf texture visible, shallow focus with soft bokeh background"
        ),
        "transplant": (
            f"{selected_person} carefully transferring a cannabis plant from a small pot into a "
            f"large fabric pot filled with dark rich soil, healthy green plant held gently, "
            f"clean indoor grow space with other plants visible in background",
            f"close-up of gloved hands pressing dark rich soil around the base of a cannabis "
            f"plant being transplanted, roots just visible at the soil edge, natural tones"
        ),
        "harvest": (
            f"{selected_person} carefully inspecting a large mature cannabis plant with dense "
            f"resin-coated buds, using a jeweler's loupe to examine trichomes, bright grow "
            f"lights illuminating the plant from above, professional indoor grow room",
            f"extreme close-up of dense cannabis trichomes under magnification, cloudy and "
            f"amber resin glands catching light, purple and green bud structure visible beneath"
        ),
        "trichome": (
            f"professional macro photograph of cannabis bud trichomes, crystal-clear stalked "
            f"capitate trichomes densely covering a deep green and purple bud surface, "
            f"resin glands reflecting light, ultra-sharp botanical photography",
            f"extreme macro of individual cannabis trichomes, translucent and milky-white "
            f"stalked capitate glands in perfect focus, orange pistils blurred softly behind"
        ),
        "trim": (
            f"{selected_person} carefully hand-trimming a freshly harvested cannabis bud with "
            f"small bonsai scissors, resin-coated fingers, trimming tray beneath collecting "
            f"sugar leaves, warm studio lighting, clean professional setting",
            f"close-up of scissors trimming a dense cannabis bud, sticky resin on the blades, "
            f"vivid green and orange bud texture in sharp detail, dark background"
        ),
        "dry": (
            f"cannabis buds hanging upside down on drying lines in a dark controlled room, "
            f"many branches evenly spaced, temperature and humidity gauge on the wall, "
            f"soft warm ambient light revealing the bud structure and color",
            f"close-up of cannabis buds hanging to dry, individual calyxes and orange pistils "
            f"visible, trichomes catching the low ambient light, dark background"
        ),
        "cure": (
            f"rows of wide-mouth mason jars filled with cured cannabis buds on wooden shelves, "
            f"lids slightly ajar for burping, hygrometer reading visible inside one jar, "
            f"warm natural lighting, rustic wooden background, artisanal aesthetic",
            f"close-up of a mason jar filled with perfectly cured cannabis buds, deep green "
            f"and purple colors, orange pistils, trichomes visible through the glass"
        ),
        "grow tent": (
            f"interior of a professional home cannabis grow tent, multiple healthy plants in "
            f"fabric pots under bright full-spectrum LED lights, reflective mylar walls, "
            f"carbon filter and fan system visible, lush green canopy",
            f"close-up of cannabis plant canopy under LED grow lights, multiple bud sites "
            f"developing, rich green fan leaves, grow light spectrum reflected on leaf surfaces"
        ),
        "hydroponic": (
            f"cannabis plants growing in a DWC hydroponic system, roots visible through "
            f"transparent reservoir walls, healthy white root mass in nutrient solution, "
            f"clean modern grow room setup with LED lights above",
            f"close-up of healthy white cannabis roots submerged in clear nutrient solution "
            f"in a hydroponic reservoir, air bubbles rising from an air stone below"
        ),
        "training": (
            f"{selected_person} carefully bending a cannabis branch and securing it with a "
            f"soft wire tie to a bamboo stake, LST training in progress, healthy green plant "
            f"in a fabric pot, indoor grow tent environment",
            f"close-up of cannabis branches bent and secured with training wire, multiple "
            f"bud sites exposed to light, healthy green growth visible at each node"
        ),
        "top": (
            f"{selected_person} using small scissors to top a cannabis plant at the main stem, "
            f"removing the apical tip between two nodes, healthy green plant with multiple "
            f"side branches, fabric pot in an indoor grow space",
            f"close-up of a topped cannabis plant showing two new main colas growing from "
            f"the cut site, fresh green growth emerging, healthy leaf texture"
        ),
        "nutrient": (
            f"selection of cannabis nutrient bottles and supplements arranged neatly on a "
            f"wooden shelf, measuring cups and pH meter on the counter, clean grow room "
            f"workspace with a plant in the background",
            f"close-up of nutrient solution being measured into a graduated cylinder, "
            f"amber liquid against a clean white background, scientific precision aesthetic"
        ),
        "strain": (
            f"close-up of multiple cannabis strain samples displayed in small glass jars on "
            f"a wooden dispensary-style counter, different colors from bright green to deep "
            f"purple, soft warm lighting creating an elegant retail atmosphere",
            f"extreme close-up of a single dense cannabis bud showing complex trichome "
            f"coverage and vivid coloration, orange pistils and purple calyxes in sharp detail"
        ),
        "terpene": (
            f"artistic flat-lay of cannabis buds surrounded by botanicals that share terpene "
            f"profiles — lavender sprigs, citrus slices, pine needles, black pepper — "
            f"arranged on a dark slate surface, elegant editorial photography",
            f"close-up of cannabis buds with terpene-rich botanicals alongside, vivid colors "
            f"and natural textures, soft bokeh background, botanical science aesthetic"
        ),
        "thc": (
            f"clean modern cannabis laboratory setting with cannabis samples in glass vials, "
            f"testing equipment and microscopes, scientist in white coat with gloves examining "
            f"sample, professional scientific photography",
            f"close-up of laboratory cannabis testing equipment, glass vials with green plant "
            f"extract, scientific instruments in background, clean white lab aesthetic"
        ),
        "cbd": (
            f"elegant CBD oil tincture bottles with dropper caps arranged on a natural wood "
            f"surface with hemp leaves and flowers nearby, soft natural window light, "
            f"clean minimalist wellness product photography",
            f"close-up of a dropper releasing a golden CBD oil drop, amber liquid catching "
            f"light, hemp leaf blurred softly in the background"
        ),
        "edible": (
            f"artfully arranged cannabis-infused edibles on a wooden board — gummies, "
            f"chocolates, and baked goods — with small cannabis leaves as garnish, "
            f"soft natural lighting, food photography aesthetic, appetizing and tasteful",
            f"close-up of colorful cannabis gummies arranged in a small glass bowl, "
            f"vibrant colors and glossy surface, macro food photography style"
        ),
        "vaporiz": (
            f"elegant dry herb vaporizer device on a clean marble surface alongside a small "
            f"glass jar of dried cannabis flower, minimalist product photography, "
            f"soft diffused lighting, premium lifestyle aesthetic",
            f"close-up of a vaporizer mouthpiece with a small amount of cannabis vapor "
            f"rising, clean background, soft focus product photography"
        ),
        "dispensary": (
            f"modern cannabis dispensary interior with well-lit display cases showing "
            f"labeled jars of cannabis products, clean retail environment, "
            f"professional budtender behind the counter helping a customer",
            f"close-up of dispensary display case with labeled cannabis strain jars, "
            f"clean glass case, soft retail lighting, various strains visible"
        ),
        "legal": (
            f"state capitol building exterior under clear blue sky, American flag and state "
            f"flag flying, steps leading to the entrance, classic government architecture, "
            f"civic and political photography aesthetic",
            f"close-up of a state ballot measure document with cannabis legalization text, "
            f"American flag in the background, civic policy photography"
        ),
        "anxiety": (
            f"{selected_person} sitting in a peaceful meditation pose on a yoga mat near a "
            f"large window with natural light, calm and relaxed expression, small plant "
            f"and wellness items nearby, soft natural lifestyle photography",
            f"close-up of hands holding a small CBD tincture bottle with hemp leaves nearby, "
            f"soft warm lighting, wellness and calm aesthetic, natural tones"
        ),
        "sleep": (
            f"peaceful bedroom scene at night with soft bedside lamp lighting, a person "
            f"resting comfortably in bed, small nightstand with a CBD oil bottle and "
            f"lavender plant, calm and serene wellness photography",
            f"close-up of a CBD oil tincture and lavender sprigs on a white linen surface, "
            f"soft warm ambient light, sleep wellness product photography aesthetic"
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
            f"beautiful mature cannabis plant with dense resin-coated buds in an indoor "
            f"grow room, full-spectrum LED lights illuminating the lush green canopy, "
            f"professional cultivation environment"
        )
        activity_section = (
            f"close-up of a dense cannabis bud with visible trichomes and orange pistils, "
            f"deep green and purple coloration, shallow depth of field, "
            f"soft bokeh background, botanical photography"
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

    prompt = f"""You are an expert cannabis education content writer for The Green Leaf, a trusted cannabis education site. Write a concise, SEO-optimized article for the keyword: "{keyword}"

Requirements:
- Target word count: 600-750 words (concise and focused)
- Write in a helpful, authoritative but friendly tone
- Start with a "Quick Answer" section (2-3 sentences directly answering the question)
- Include 3-5 "Key Takeaways" bullet points after the quick answer
- Structure with clear H2 and H3 headings
- Include practical, accurate, evidence-based information
- Write for cannabis enthusiasts, patients, and curious beginners — not industry insiders
- Keep sections concise — avoid over-explaining
- IMPORTANT: Use proper markdown list syntax with hyphens (-), NOT bullet characters (•)
- Do NOT make medical claims or recommend cannabis as a treatment for any condition
- Keep all content educational and informational

GEO OPTIMIZATION (for AI citation):
- Use QUESTION-BASED H2 headings that match how people ask AI assistants
  Examples: "How Long Does It Take to Cure?", "What's the Difference Between Indica and Sativa?", "Why Are My Cannabis Leaves Turning Yellow?"
- Write direct, factual answers that AI can easily extract and cite
- FAQs and key stats will be rendered separately via structured data - DO NOT include them in the article content

Article Structure (IMPORTANT):
1. Title (H1)
2. Quick Answer paragraph (2-3 sentences)
3. Key Takeaways (3-5 bullet points)
4. Introduction paragraph
5. Main content with 3-4 H2 sections (USE QUESTION FORMAT for headings)
6. Conclusion with actionable next steps
7. Sources section (REQUIRED) - Add "## Sources" with 3-5 authoritative references

NOTE: Do NOT include a "## Frequently Asked Questions" section in the article content.
FAQs are provided separately in the JSON output and will be rendered with structured schema markup.

The SECOND H2 section should be the most visual/actionable section (this is where we'll insert a detail image).
For example: "Step-by-Step Guide", "How It Works", "The Process", "What to Look For", etc.
{comparison_instruction}

CRITICAL SOURCE REQUIREMENTS:

1. Research and cite 4-6 DIVERSE, topic-specific credible sources:
   - At least 1 peer-reviewed research source (PubMed, NCBI, Journal of Cannabis Research, etc.)
   - At least 1 government or regulatory source (NIH, FDA, state health departments, NORML legislative data)
   - At least 1 cannabis industry or education publication (Leafly Research, Project CBD, Cannabis Business Times)
   - At least 1 additional credible source relevant to the specific topic

2. Use CLICKABLE NUMBERED CITATIONS throughout the article text when referencing information
   - Citations should be clickable markdown links that jump to the Sources section
   - Format: "This is a fact[[1]](#user-content-fn-1)."
   - Multiple citations: "This combines several facts[[1]](#user-content-fn-1)[[2]](#user-content-fn-2)."
   - Place citation links at the END of sentences, before the period
   - Use citations naturally throughout the article (aim for 8-12 citations distributed across sections)

3. End article with "## Sources" section with anchor IDs for each source:
   Format with anchor IDs:
   ```
   <a id="user-content-fn-1"></a>
   1. [Organization Name](https://example.org) - Specific resource description
   ```

Example Sources section:
## Sources
<a id="user-content-fn-1"></a>
1. [National Institutes of Health](https://www.nih.gov) - Cannabis and cannabinoid research database
<a id="user-content-fn-2"></a>
2. [NORML](https://norml.org) - Cannabis law reform and state policy resources
<a id="user-content-fn-3"></a>
3. [Project CBD](https://www.projectcbd.org) - Cannabinoid science and clinical research
<a id="user-content-fn-4"></a>
4. [Leafly](https://www.leafly.com) - Cannabis strain data and consumer research
<a id="user-content-fn-5"></a>
5. [Journal of Cannabis Research](https://jcannabisresearch.biomedcentral.com) - Peer-reviewed cannabis science

IMPORTANT:
- Use main domain URLs (e.g., https://www.nih.gov) NOT deep links that might 404
- VARY sources by topic — don't use the same sources every time
- DO NOT use inline citation links like "[NIH](url) research shows..." — only numbered citations
- Keep paragraphs clean — only use numbered citations [1], [2], etc.
- Choose sources actually relevant to the specific topic being discussed

Return the section title you recommend for the mid-article image in the JSON.

Output format (JSON):
{{
    "title": "SEO-optimized title (50-60 chars)",
    "meta_description": "Compelling meta description (150-160 chars)",
    "slug": "url-friendly-slug",
    "content": "Full article in Markdown format (NO FAQ section - FAQs go in separate field below)",
    "tags": ["relevant", "tags", "for", "article"],
    "estimated_read_time": "X min read",
    "section_image_title": "Title of the H2 section where image should go (2nd main section)",
    "faqs": [
        {{"question": "Common question about the topic?", "answer": "Direct 2-3 sentence answer."}},
        {{"question": "Another relevant question?", "answer": "Clear, factual answer."}},
        {{"question": "Third question users ask?", "answer": "Helpful response."}},
        {{"question": "Fourth question if applicable?", "answer": "Concise answer."}}
    ],
    "key_stat": "Single most quotable statistic with specific numbers (e.g., 'Cannabis plants typically take 8-11 weeks to flower indoors depending on strain genetics')",
    "tldr": "One sentence summary of the article's main point (e.g., 'Harvest cannabis when 70-90% of trichomes have turned milky white for peak THC potency.')"
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
    article_data["season"] = get_current_season()
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
