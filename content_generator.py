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
import time
from datetime import datetime
from pathlib import Path
import base64
import io
import uuid
from dotenv import load_dotenv
import anthropic
import requests
from PIL import Image, ImageStat
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
# Explicit per-request timeout so a slow/hung call fails fast instead of
# silently eating the weekly_content_pipeline subprocess budget with no
# diagnostic trace (previously fell back to the SDK's ~10 min default).
CLAUDE_CALL_TIMEOUT = 90.0
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"), max_retries=2)

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
    """Assign a category matching the six Topics page clusters."""
    CLUSTERS = [
        # Matches Topics page: strains-genetics
        ("strains-genetics", [
            "strain profile", "strain guide", "strain review", "strain effects", "strain overview",
            "strain breakdown", "lineage", "genetics", "phenotype", "terpene",
            "kush", "haze", "diesel", "cookies", "gelato", "runtz", "zkittlez",
            "wedding cake", "gorilla glue", "blue dream", "og kush", "northern lights",
            "granddaddy", "sour diesel", "purple punch", "pineapple express", "white widow",
            "bubba kush", "mac 1", "do-si-dos", "mimosa", "biscotti",
            "best strains", "strains for", "top strains", "best indica", "best sativa",
            "best hybrid", "high thc", "strongest strains", "most popular strains",
            "indica vs sativa", "hybrid strain",
        ]),
        # Matches Topics page: growing-cultivation
        ("growing-cultivation", [
            "grow", "cultivat", "indoor growing", "outdoor growing", "hydroponic",
            "soil mix", "nutrients", "lighting", "flowering", "vegetative",
            "harvest", "germinate", "germination", "seed", "clone", "grow tent",
            "yield", "pruning", "training", "lst", "scrog", "topping", "fimming",
            "compost", "grow medium", "ph level", "irrigation", "autoflower",
        ]),
        # Matches Topics page: consumption-methods
        ("consumption-methods", [
            "consumption methods", "how to smoke", "how to vape", "vaping vs",
            "edibles vs", "how to use", "how to consume",
            "vaporizer", "vape", "edible", "tincture", "topical", "dab", "dabbing",
            "concentrate", "pre-roll", "joint", "blunt", "bong", "pipe",
            "hash", "rosin", "live resin", "budtender", "dispensary menu",
            "tolerance break", "third-party testing", "packaging",
        ]),
        # Matches Topics page: health-wellness
        ("health-wellness", [
            "anxiety", "pain relief", "sleep", "depression", "ptsd",
            "inflammation", "medical cannabis", "nausea", "migraines", "arthritis",
            "wellness", "therapeutic", "health benefits", "cbd benefits",
            "cancer", "seizure", "epilepsy", "chronic pain", "insomnia",
            "stress relief", "mental health",
        ]),
        # Matches Topics page: legal-industry
        ("legal-industry", [
            "legal", "legalization", "law", "regulat", "licens",
            "dispens", "federal", "legislat", "policy", "bill", "vote",
            "decriminalize", "possession limit", "adult-use", "medical marijuana program",
            "cannabis industry", "market", "hemp", "farm bill",
        ]),
        # Matches Topics page: culture-lifestyle
        ("culture-lifestyle", [
            "histor", "recipe", "cannabis recipe", "cook", "event", "festival",
            "travel", "accessor", "culture", "lifestyle", "celebrity",
            "art", "music", "movie", "documentary", "etiquette", "paraphernalia",
            "cannabis culture", "social", "community",
        ]),
    ]
    title_kw = f"{title} {keyword} {' '.join(tags)}".lower()
    best_score, best_cat = 0, "strains-genetics"
    for cat, keywords_list in CLUSTERS:
        score = sum(5 for kw in keywords_list if kw in title_kw)
        if score > best_score:
            best_score, best_cat = score, cat
    return best_cat


# Randomized photographic variation attributes.
# Even when two articles share the same keyword theme (and therefore the same
# base scene), these give each generated image a distinct angle, light, framing
# and color grade so images no longer look near-identical. See IMAGE_VARIATION_GUIDE.md.
_VARIATION_ANGLES = {
    "hero": [
        "an eye-level perspective",
        "a low three-quarter angle",
        "a slightly elevated 45-degree angle",
        "a wide establishing angle",
        "a gentle overhead flat-lay angle",
    ],
    "section": [
        "a straight-on macro angle",
        "a top-down macro angle",
        "a 45-degree macro angle",
        "a raking side-lit macro angle",
    ],
}
_VARIATION_LIGHTING = [
    "warm golden-hour light",
    "cool soft morning light",
    "bright airy high-key lighting",
    "moody low-key lighting with deep shadows",
    "soft diffused overcast light",
    "dramatic directional side light",
]
_VARIATION_COMPOSITION = {
    "hero": [
        "a rule-of-thirds composition",
        "a centered symmetrical composition",
        "an off-center composition with negative space",
        "a layered composition with foreground depth",
    ],
    "section": [
        "a tightly centered crop",
        "an off-center crop with soft negative space",
        "a diagonal composition",
    ],
}
_VARIATION_PALETTE = [
    "a rich warm color grade",
    "cool muted tones",
    "a vibrant saturated palette",
    "earthy natural tones",
]


def _variation_clause(image_type="hero"):
    """
    Return a randomized photographic-variation sentence to append to a prompt.

    Randomizing angle, lighting, composition and color grade per request is what
    keeps images from looking identical when many articles share the same base
    scene template.
    """
    key = "hero" if image_type == "hero" else "section"
    angle = random.choice(_VARIATION_ANGLES[key])
    lighting = random.choice(_VARIATION_LIGHTING)
    composition = random.choice(_VARIATION_COMPOSITION[key])
    palette = random.choice(_VARIATION_PALETTE)
    return f"Shot from {angle} in {lighting}, {composition}, {palette}."


# ── Deterministic variant selection ──────────────────────────────────────────
def _slug_hash(slug: str) -> int:
    """Deterministic hash of slug for stable variant selection."""
    import hashlib as _hl
    return int(_hl.md5(slug.encode()).hexdigest(), 16)


def _pick_variant(variants, slug, image_type):
    """Deterministically select a variant by hashing slug + image_type."""
    h = _slug_hash(f"{slug}:{image_type}")
    return variants[h % len(variants)]


def _extract_subject(keyword, title):
    """Extract article-specific subject text for prompt differentiation."""
    words = (title or keyword).split()
    subject_parts = []
    for word in words:
        clean = word.strip(",.;:()[]")
        if clean and clean[0].isupper() and len(clean) > 2 and clean.lower() not in (
            "the", "and", "for", "with", "how", "what", "why", "when", "where",
            "best", "top", "complete", "guide", "review", "explained", "2024", "2025", "2026",
        ):
            subject_parts.append(clean)
    if subject_parts:
        return " ".join(subject_parts[:4]).lower()
    return keyword.lower()


def _log_prompt(slug, bucket, prompt, image_type):
    """Log prompt to .logs/image_prompts.jsonl for uniqueness tracking."""
    from datetime import datetime
    log_path = Path(".logs/image_prompts.jsonl")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "slug": slug,
        "bucket": bucket,
        "image_type": image_type,
        "prompt": prompt,
    }
    with open(log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _check_prompt_uniqueness(slug, prompt):
    """Check if exact prompt was already used for a different slug.
    If so, append a differentiating detail from the slug."""
    log_path = Path(".logs/image_prompts.jsonl")
    if not log_path.exists():
        return prompt
    existing_slugs = set()
    for line in log_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
            if entry.get("prompt") == prompt:
                existing_slugs.add(entry.get("slug", ""))
        except json.JSONDecodeError:
            continue
    if existing_slugs and slug not in existing_slugs:
        detail = slug.replace("-", " ").split(":")[0].strip()
        prompt = f"{prompt} Distinctive subject context: {detail}."
    return prompt


# Trigger aliases: maps additional keyword substrings to existing bucket keys
# so articles like "what is rosin vs resin" match the concentrat bucket
# even though "concentrat" is not in the keyword.
_TRIGGER_ALIASES = {
    "testing": "lab result", "third-party": "lab result", "third party": "lab result",
    "certificate": "lab result",
    "rosin": "concentrat", "resin": "concentrat", "shatter": "concentrat",
    "wax": "concentrat", "hash": "concentrat", "dab": "concentrat",
    "vape": "vaporiz", "vaping": "vaporiz",
    "gummy": "edible", "gummies": "edible", "chocolate": "edible",
    "cream": "topical", "lotion": "topical", "salve": "topical", "balm": "topical",
    "smoke": "consumption", "joint": "consumption", "blunt": "consumption",
    "pipe": "consumption", "bong": "consumption", "pre-roll": "consumption",
    "seed": "germinat", "seedling": "germinat", "clone": "germinat",
    "cultivat": "grow",
    "nutrient": "soil", "compost": "soil",
    "insomnia": "sleep", "inflammation": "pain", "arthritis": "pain",
    "stress": "anxiety", "law": "legal", "regulat": "legal", "federal": "legal",
    "legislat": "legal", "decriminal": "legal",
    "cbn": "cannabinoid", "cbg": "cannabinoid",
    "tolerance": "consumption",
}


# Fallback scenes for unmatched keywords — 5 varied options
_FALLBACK_SCENES = [
    {
        "hero": "premium cannabis flower buds displayed in an open glass jar on a dark wood surface, glistening trichomes and vivid green and purple coloration, soft warm studio lighting, elegant lifestyle product photography",
        "section": "extreme close-up of a dense cannabis bud with visible crystalline trichomes and orange pistils, deep green and purple coloration, shallow depth of field, soft bokeh background, macro botanical photography",
    },
    {
        "hero": "artistic overhead of cannabis culture — flower, rolling papers, and a small glass jar — arranged on a textured linen surface, soft natural daylight, editorial lifestyle photography",
        "section": "macro of cannabis trichomes catching warm afternoon light, amber and clear resin heads glistening, dark background, botanical macro photography",
    },
    {
        "hero": "cannabis flower resting on a piece of dark slate with water droplets nearby, moody studio lighting, premium botanical product photography, dark elegant aesthetic",
        "section": "extreme macro of a cannabis calyx with emerging pistils, frosty trichome coverage, dark background with a single warm light source, botanical detail photography",
    },
    {
        "hero": "modern minimalist cannabis display — a single perfect bud on a white ceramic dish, soft diffused natural light, clean Scandinavian aesthetic, premium product photography",
        "section": "top-down macro of a cannabis bud showing its full structure, even soft lighting, shallow depth of field on the outer trichomes, clean botanical photography",
    },
    {
        "hero": "cannabis plant in natural sunlight with focus on a single cola, green leaves fanning out, blue sky softly blurred in background, outdoor botanical photography",
        "section": "macro of a cannabis sugar leaf coated in resin, backlit by natural sunlight, trichomes glowing like frost, botanical macro photography, green natural background",
    },
]


def build_image_prompt(keyword, season, image_type="hero", slug="", title=""):
    """
    Build an optimized prompt for cannabis education images.

    Merged system combining:
    - A (origin/main a3d3f29): _variation_clause randomization, longest-match
      bucket selection, random seed per Runware call
    - B (image-diversity-refresh): 2-3 scene variants per bucket with deterministic
      slug-hash selection, article-specific subject injection, 5 varied fallback
      scenes, prompt uniqueness logging + collision guard, distinct hero/section
      composition instruction

    Args:
        keyword: Target keyword for the article
        season: Current season (kept for API compatibility)
        image_type: "hero" for wide shot (16:9) or "section" for detail (4:3)
        slug: Article slug (for deterministic variant selection + uniqueness log)
        title: Article title (for extracting article-specific subject text)

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

    # Activity descriptions by keyword theme.
    # Each key maps to {"hero": [2-3 variants], "section": [2-3 variants]}.
    # Hero: wide cinematic environmental shot | Section: tight detail/texture shot.
    # When slug is provided, a variant is selected deterministically via slug hash
    # so the same article always gets the same scene variant while different
    # articles in the same bucket get different variants.
    activities = {
        # Strain profiles and individual strain articles
        "strain": {
            "hero": [
                "close-up of multiple premium cannabis strain samples in small labeled glass jars on a wooden dispensary-style counter, rich colors from bright green to deep purple, soft warm lighting creating an elegant retail atmosphere",
                "artisanal cannabis flower displayed on a rustic wooden board with botanical name tags, diverse bud colors and textures, soft warm studio lighting, editorial product photography",
                "cannabis strain collection in clear glass vials on a dark slate surface, each vial showing different colored flower, dramatic side lighting, premium connoisseur aesthetic",
            ],
            "section": [
                "extreme close-up of a single dense cannabis bud showing complex trichome coverage and vivid coloration, orange pistils and purple calyxes in sharp detail, shallow depth of field, botanical photography",
                "side-lit macro shot of cannabis flower surface, crystalline resin glands glistening, deep green and amber tones, ultra-detailed texture photography from a low angle",
                "top-down macro of a halved cannabis bud revealing interior structure, dense trichome forest visible, warm backlighting creating a glowing rim effect on the flower edges",
            ],
        },
        "review": {
            "hero": [
                "beautifully lit cannabis bud on a dark slate surface surrounded by small botanical elements — citrus slice, pine sprig, and lavender — editorial flat-lay, soft studio lighting, premium lifestyle photography",
                "single cannabis flower resting on a textured ceramic dish with small botanical accents, dramatic rim lighting from the left, dark moody background, editorial review aesthetic",
                "cannabis bud held delicately between fingertips against a soft-focus natural background, warm golden-hour light, intimate review-style product photography",
            ],
            "section": [
                "extreme close-up of a cannabis bud with visible trichomes, deep green and purple coloration, orange pistils, macro photography style, dark background",
                "macro detail of cannabis flower calyx showing individual trichome stalks, sharp focus on resin heads, cool-toned ring light, scientific botanical photography",
                "angled macro of a cannabis bud cross-section, revealing dense internal structure and resin coverage, dramatic side lighting highlighting texture and depth",
            ],
        },
        "profile": {
            "hero": [
                "premium cannabis flower displayed in an open glass jar on a natural wood surface, deep green and purple bud with glistening resin visible, soft diffused light, clean minimalist product photography aesthetic",
                "cannabis strain showcased on a pedestal of smooth river stones, single perfect bud, dramatic spotlight, dark background, museum-quality botanical display",
                "cannabis flower arrangement on a linen cloth with a magnifying glass and tweezers nearby, suggesting connoisseur inspection, soft natural window light, editorial profile aesthetic",
            ],
            "section": [
                "close-up macro shot of cannabis flower trichomes, crystalline resin glands in sharp focus, vivid colors, ultra-detailed botanical photography",
                "extreme macro of a single trichome cluster on a cannabis calyx, amber resin heads in sharp focus, dark background, electron-microscope-inspired botanical aesthetic",
                "macro of cannabis flower pistils emerging from a calyx, orange and white hairs in sharp detail, shallow depth of field, warm backlighting",
            ],
        },
        # Best-of roundups and strain discovery
        "best strain": {
            "hero": [
                "elegant flat-lay of five different cannabis strain samples in small glass jars, each a different color and texture, arranged on dark wood, soft studio lighting, premium cannabis lifestyle photography",
                "curated selection of premium cannabis buds displayed on a wooden board, various strains with different hues — greens, purples, and golds — soft warm lighting, editorial food photography aesthetic applied to cannabis",
                "comparison display of cannabis strains in a row of identical glass jars on a marble counter, each labeled, professional product photography, clean bright lighting",
            ],
            "section": [
                "close-up of several cannabis buds side by side showing different colors and trichome densities, comparison photography, macro detail, dark background",
                "macro of two cannabis buds of different strains placed side by side for comparison, one purple indica and one green sativa, sharp detail on both, soft gradient background",
                "top-down macro of a strain comparison grid, four small buds arranged in quadrants showing color and structure differences, even studio lighting, editorial comparison aesthetic",
            ],
        },
        "top strain": {
            "hero": [
                "curated selection of premium cannabis buds displayed on a wooden board, various strains with different hues — greens, purples, and golds — soft warm lighting, editorial food photography aesthetic applied to cannabis",
                "premium cannabis strains arranged in glass jars on a dark wood shelf, warm spot lighting, each jar labeled with strain name, professional dispensary photography",
                "assortment of top-shelf cannabis flower samples on a marble slab, diverse colors and bud structures, bright clean studio lighting, editorial review aesthetic",
            ],
            "section": [
                "macro close-up of multiple cannabis buds showing diverse trichome patterns and bud structures, vivid colors, professional botanical photography",
                "extreme macro comparing trichome density across two different strain buds side by side, scientific comparison photography, dark background",
                "top-down macro of three cannabis buds of different colors — green, purple, and gold — arranged in a triangle, even studio lighting, comparison detail photography",
            ],
        },
        "indica": {
            "hero": [
                "dense, compact indica cannabis buds in deep purple and forest green tones displayed on a dark marble surface, soft warm ambient lighting, premium strain photography with elegant lifestyle aesthetic",
                "heavy indica cannabis cola resting on a velvet cloth, deep purple hues with thick resin coating, moody candlelit atmosphere, luxurious strain photography",
                "indica cannabis flower in a ceramic bowl on a dark wooden nightstand, warm lamp light, cozy evening atmosphere, wellness lifestyle photography",
            ],
            "section": [
                "extreme close-up of a dense indica bud with heavy trichome coverage, deep purple coloration, orange pistils curling through crystal-coated calyxes",
                "macro of an indica bud's dense structure, compact calyxes pressed tightly together, purple and green coloration under warm light, shallow depth of field",
                "side-lit macro of indica flower showing thick resin layer, deep purple anthocyanins visible, frosty trichome blanket, dark moody background",
            ],
        },
        "sativa": {
            "hero": [
                "elongated sativa cannabis buds in bright lime green and golden tones displayed on a light wood surface with soft natural window light, airy open bud structure, energetic premium lifestyle photography",
                "tall sativa cannabis colas standing upright in a glass vase, bright green and gold coloration, sunlit room with tropical plants in background, vibrant energetic aesthetic",
                "sativa cannabis flower on a white marble surface with citrus fruits nearby, bright airy natural light, clean fresh product photography suggesting energy and focus",
            ],
            "section": [
                "close-up of a sativa bud with long orange pistils and visible trichomes, bright green coloration, open fluffy structure, macro botanical photography",
                "macro of sativa flower's elongated calyx structure, visible internodal spacing, bright lime green with golden resin, backlit to show translucent pistils",
                "top-down macro of a sativa bud showing its open, airy structure, bright green with orange pistils radiating outward, soft diffused daylight",
            ],
        },
        "hybrid": {
            "hero": [
                "selection of balanced hybrid cannabis strains displayed in elegant glass containers on a modern countertop, mixed green and purple tones, clean contemporary lifestyle photography",
                "hybrid cannabis flower on a minimalist concrete surface with both warm and cool light sources, suggesting balanced indica-sativa effects, architectural product photography",
                "cannabis buds with mixed green and purple coloration arranged in a zen-garden style composition, raked sand pattern, soft natural light, balanced aesthetic",
            ],
            "section": [
                "macro close-up of a hybrid cannabis bud showing balanced indica and sativa bud structure, vivid trichomes, orange and green color mix, dark background",
                "macro of a hybrid cannabis flower showing both compact and airy structural elements, mixed purple and green coloration, even studio lighting, botanical detail photography",
                "cross-section macro of a hybrid bud revealing both dense and open calyx structures, dual warm and cool lighting suggesting balanced effects, shallow depth of field",
            ],
        },
        # Terpenes and science
        "terpene": {
            "hero": [
                "artistic flat-lay of cannabis buds surrounded by botanicals sharing terpene profiles — lavender sprigs, citrus slices, pine needles, black pepper, mango — arranged on a dark slate surface, elegant editorial photography",
                "cannabis flower alongside a molecular model and fresh botanicals on a laboratory bench, soft scientific lighting, educational wellness photography aesthetic",
                "artistic arrangement of cannabis and companion botanicals — hops, mango, lemon, pine — on a rustic wooden table, natural daylight, botanical science flat-lay",
            ],
            "section": [
                "close-up of cannabis buds alongside terpene-matching botanicals, vivid colors and natural textures, soft bokeh background, botanical science aesthetic",
                "macro of a cannabis trichome gland alongside a cross-section of a citrus peel, comparing natural oil structures, scientific botanical photography, clean white background",
                "extreme macro of cannabis resin glands with visible terpene oil droplets on the surface, amber and clear heads, dark field lighting, scientific detail photography",
            ],
        },
        "entourage": {
            "hero": [
                "artistic arrangement of cannabis plant components — flower, leaves, and botanical extracts in small vials — on a clean white laboratory surface, scientific wellness photography, soft diffused light",
                "cannabis flower, concentrate, and tincture bottle arranged in a triangular composition on a marble surface, representing the entourage effect concept, soft studio lighting, wellness editorial aesthetic",
                "artistic overhead of cannabis flower surrounded by molecular structure diagrams drawn on kraft paper, soft natural light, educational science photography",
            ],
            "section": [
                "close-up of cannabis trichomes and botanical elements, scientific detail photography, various plant compounds visible, clean white background",
                "macro of cannabis resin alongside botanical essential oils in small glass dishes, comparing textures and colors, scientific wellness photography, soft diffused light",
                "extreme macro of a trichome head releasing resin, with soft-focus botanical compounds in the background, scientific photography aesthetic, dark background",
            ],
        },
        "endocannabinoid": {
            "hero": [
                "clean modern scientific illustration aesthetic: cannabis leaf with soft glowing neural network overlay on a dark background, science and wellness photography, professional editorial style",
                "abstract scientific visualization of the human body with glowing points where cannabinoid receptors are concentrated, cannabis leaf silhouette overlay, dark blue background, medical illustration aesthetic",
                "artistic composition of a cannabis leaf and a human brain model on a dark surface, connected by soft glowing lines suggesting the endocannabinoid system, professional science photography",
            ],
            "section": [
                "close-up of cannabis plant structure with soft scientific bokeh, editorial science photography, clean background, deep green tones",
                "macro of a cannabis trichome with a soft overlay of a cell membrane receptor, scientific illustration meets photography, dark background with blue accent lighting",
                "extreme macro of cannabis resin glands with a soft-focus diagram of a neuron in the background, scientific educational photography, cool blue tones",
            ],
        },
        "cannabinoid": {
            "hero": [
                "clean modern cannabis laboratory with glass vials containing cannabis extracts in amber and green tones, scientific equipment on the counter, researcher in background, professional science photography",
                "molecular model of a cannabinoid molecule displayed alongside cannabis flower on a clean white surface, soft scientific lighting, educational product photography",
                "row of labeled laboratory vials containing different cannabinoid extracts, amber and clear liquids, clean white lab bench, professional scientific photography",
            ],
            "section": [
                "close-up of laboratory cannabis sample vials with amber liquid extracts, scientific glassware, clean white lab aesthetic, soft lighting",
                "macro of a cannabinoid molecular model with cannabis flower softly blurred in the background, scientific educational photography, clean white surface",
                "extreme close-up of a laboratory pipette dispensing a golden cannabinoid extract into a vial, scientific precision aesthetic, clean white background, soft lighting",
            ],
        },
        # THC/CBD/science
        "thc": {
            "hero": [
                "modern cannabis testing laboratory setting, glass sample vials and scientific equipment on a clean white countertop, soft professional lighting, science and wellness aesthetic",
                "cannabis flower alongside a THC molecule model on a dark slate surface, dramatic side lighting, scientific product photography, educational aesthetic",
                "cannabis potency testing display with flower samples and percentage labels, professional laboratory setting, clean bright lighting, educational science photography",
            ],
            "section": [
                "close-up of cannabis sample in a glass vial with a THC percentage label, laboratory setting, clean white background, scientific precision aesthetic",
                "macro of a THC crystal structure model alongside a cannabis trichome, scientific comparison photography, dark background with cool lighting",
                "extreme macro of cannabis trichome heads appearing as THC-rich resin glands, amber and clear droplets in sharp focus, dark field scientific photography",
            ],
        },
        "cbd": {
            "hero": [
                "elegant CBD product collection — tincture bottles, capsules, and hemp flowers — arranged on natural wood with soft green leaves, clean wellness photography, natural window light, minimalist lifestyle aesthetic",
                "CBD hemp flower displayed alongside tincture bottles on a white marble surface, soft diffused natural light, clean wellness product photography, spa-like aesthetic",
                "artisanal CBD products — oils, balms, and dried hemp flower — arranged on a linen cloth with fresh hemp leaves, soft natural daylight, organic wellness lifestyle photography",
            ],
            "section": [
                "close-up of a dropper releasing a golden CBD oil drop into a small glass bottle, amber liquid catching soft light, hemp leaf blurred softly in background",
                "macro of CBD hemp flower showing delicate trichome coverage, bright green and golden tones, soft natural light, organic botanical photography",
                "extreme close-up of a CBD tincture bottle label and dropper, golden oil visible inside, clean white background, wellness product macro photography",
            ],
        },
        "lab result": {
            "hero": [
                f"{selected_person} reviewing a cannabis certificate of analysis document at a clean desk, lab report visible with cannabinoid percentages, professional and educational lifestyle photography",
                "laboratory technician in a clean white coat reviewing cannabis test results on a tablet, modern lab background, professional science photography, bright lighting",
                "cannabis testing laboratory with analytical equipment, sample vials, and a printed lab report on the counter, professional educational photography, clean environment",
            ],
            "section": [
                "close-up of a cannabis lab results document showing THC, CBD, and terpene percentages in clear print, professional document photography",
                "macro of a cannabis certificate of analysis with cannabinoid bars and numbers visible, magnifying glass overlay, professional document photography, clean desk surface",
                "extreme close-up of HPLC testing equipment screen showing cannabinoid peaks, scientific instrument photography, dark background with green screen glow",
            ],
        },
        # Consumption methods
        "vaporiz": {
            "hero": [
                "premium dry herb vaporizer on a clean marble surface alongside a small glass jar of cannabis flower, minimalist product photography, soft diffused lighting, upscale lifestyle aesthetic",
                "modern vaporizer device with a gentle wisp of vapor rising, cannabis flower nearby, dark background with dramatic lighting, premium tech product photography",
                "vaporizer and cannabis flower arranged on a wooden tray with a small brush and grinder, lifestyle product flat-lay, warm natural lighting, connoisseur aesthetic",
            ],
            "section": [
                "close-up of vaporizer heating chamber with cannabis flower, warm product lighting, premium device detail photography",
                "macro of vapor rising from a device mouthpiece against a dark background, soft backlighting making the vapor visible, premium product photography",
                "extreme close-up of ground cannabis flower in a vaporizer chamber, even warm lighting showing texture and grind consistency, product detail photography",
            ],
        },
        "edible": {
            "hero": [
                "artfully arranged cannabis-infused edibles — gummies, chocolates, and mints — displayed on a wooden board with small hemp leaves as garnish, soft natural lighting, upscale food photography aesthetic",
                "cannabis-infused chocolate bar broken into pieces on a marble surface, cocoa and hemp leaves nearby, dramatic food photography lighting, premium confectionery aesthetic",
                "colorful cannabis gummies in small glass jars arranged on a pastel surface, bright cheerful food photography, soft daylight, wellness lifestyle aesthetic",
            ],
            "section": [
                "close-up of colorful cannabis gummies in a small glass bowl, vibrant colors and glossy surface, macro food photography style",
                "macro of a cannabis-infused chocolate truffle cross-section showing rich texture, soft warm lighting, premium confectionery photography, dark background",
                "extreme close-up of a single cannabis gummy showing its crystalline sugar coating and translucent interior, macro food photography, bright even lighting",
            ],
        },
        "tincture": {
            "hero": [
                "glass tincture bottles with droppers arranged on a natural wood surface with hemp flowers and leaves nearby, clean wellness product photography, soft natural window light, minimal lifestyle aesthetic",
                "single tincture bottle with golden oil on a white pedestal, dramatic studio lighting, minimalist wellness product photography, spa-like aesthetic",
                "tincture bottle being filled with a dropper, golden oil catching the light, hemp leaves in the background, wellness lifestyle photography, soft natural light",
            ],
            "section": [
                "close-up of a dropper tip with amber tincture liquid ready to dispense, natural green background, wellness product macro photography",
                "macro of a single drop of golden tincture oil falling from a dropper, frozen in motion, dark background with warm backlight, product detail photography",
                "extreme close-up of a tincture bottle's glass texture with golden oil visible inside, soft rim lighting, minimalist wellness product photography",
            ],
        },
        "concentrat": {
            "hero": [
                "collection of premium cannabis concentrates in small glass containers — golden wax, clear shatter, and amber live resin — on a dark slate surface, professional product photography with warm studio lighting",
                "cannabis concentrate displayed on a dab tool with a golden translucent shard of shatter, dark dramatic background, warm backlighting, premium connoisseur product photography",
                "artisanal cannabis hash and rosin arranged on parchment paper with a press nearby, rustic workshop aesthetic, warm natural lighting, craft concentrate photography",
            ],
            "section": [
                "extreme close-up of golden cannabis concentrate showing crystalline structure, warm amber tones, macro detail, dark background",
                "macro of rosin being pressed from cannabis flower, golden oil emerging under heat and pressure, scientific process photography, warm lighting",
                "extreme close-up of cannabis shatter showing its translucent golden amber quality, light passing through the material, dark background, connoisseur macro photography",
            ],
        },
        "dispensary": {
            "hero": [
                "modern cannabis dispensary interior with illuminated display cases, labeled strain jars under soft retail lighting, professional budtender helping a customer, welcoming clean retail environment",
                "cannabis dispensary counter with neatly arranged product jars, digital menu board in the background, warm retail lighting, professional commercial photography",
                "exterior of a modern cannabis dispensary storefront with clean signage and large windows, evening lighting, urban retail photography aesthetic",
            ],
            "section": [
                "close-up of a dispensary display case with labeled cannabis strain jars showing strain names and THC percentages, clean glass case, soft lighting",
                "macro of a cannabis product jar label on a dispensary shelf, professional retail photography, shallow depth of field with soft retail background",
                "close-up of a digital dispensary menu screen showing strain names and prices, modern retail photography, clean environment",
            ],
        },
        "budtender": {
            "hero": [
                f"friendly {selected_person} budtender in a clean cannabis dispensary, explaining products to a customer across the counter, professional retail setting, welcoming and educational atmosphere",
                "budtender's hands carefully weighing cannabis flower on a digital scale, clean dispensary counter, professional retail photography, soft warm lighting",
                "budtender holding up a cannabis flower jar to show a customer, bright dispensary interior, lifestyle retail photography, welcoming atmosphere",
            ],
            "section": [
                "close-up of a budtender's hands displaying a cannabis product jar with label visible, clean dispensary counter, professional retail photography",
                "macro of a budtender's hands breaking apart a cannabis bud to show its structure, professional retail setting, soft natural lighting",
                "close-up of a budtender pointing to different cannabis strain jars on a shelf, professional retail photography, shallow depth of field",
            ],
        },
        # Wellness and effects
        "anxiety": {
            "hero": [
                f"{selected_person} sitting peacefully in a sunlit living room, calm and relaxed expression, soft natural light, clean wellness lifestyle photography, green plants visible in background, serene home environment",
                "peaceful meditation corner with a cannabis plant, soft cushions, and warm tea, calm wellness environment, soft diffused natural light, spa-like aesthetic",
                f"person sitting on a park bench in a lush garden looking calm and relaxed, soft golden-hour light, wellness lifestyle photography, natural serene environment",
            ],
            "section": [
                "close-up of hands cradling a warm cup of herbal tea with hemp leaves nearby, soft warm lighting, wellness and calm aesthetic, natural tones",
                "macro of a single cannabis leaf resting on a smooth stone in a zen garden, soft natural light, tranquility and wellness aesthetic, shallow depth of field",
                "close-up of a person's hands resting peacefully on their lap in soft natural light, calm wellness lifestyle photography, warm natural tones",
            ],
        },
        "sleep": {
            "hero": [
                "peaceful bedroom scene with soft bedside lamp, person resting comfortably in a cozy bed, lavender plant on the nightstand, calm and serene wellness photography, warm amber lighting",
                "cozy reading nook with a warm blanket, cup of herbal tea, and a small cannabis tincture bottle on the side table, soft warm evening lighting, sleep wellness aesthetic",
                "tranquil nighttime scene with a moonlit window, soft bedding, and lavender sprigs on a nightstand, calm sleep wellness photography, cool blue and warm amber tones",
            ],
            "section": [
                "close-up of lavender sprigs and a small glass tincture bottle on white linen, soft warm ambient light, sleep wellness aesthetic",
                "macro of a cannabis indica flower resting on a soft pillow, warm amber lighting, sleep and relaxation wellness photography, shallow depth of field",
                "close-up of a dropper dispensing golden CBD oil onto a spoon, soft warm bedside lamp lighting, sleep wellness product photography",
            ],
        },
        "pain": {
            "hero": [
                f"{selected_person} looking relaxed and comfortable in a modern living space, natural light, wellness lifestyle photography, clean and calm home environment, subtle cannabis plant element visible in background",
                "person receiving a gentle hand massage with CBD topical, spa-like environment, soft warm lighting, wellness and relief lifestyle photography",
                "peaceful home office with ergonomic chair, person stretching comfortably, warm afternoon light, wellness and relief lifestyle photography",
            ],
            "section": [
                "close-up of hands holding a CBD topical cream jar with cannabis leaf design, clean product photography, soft natural light, wellness aesthetic",
                "macro of a CBD balm being applied to skin, showing the cream's texture, wellness product photography, soft natural lighting, clean aesthetic",
                "close-up of a person's hands resting on their lower back in a gentle stretch, warm soft lighting, wellness and pain relief lifestyle photography",
            ],
        },
        "beginner": {
            "hero": [
                f"{selected_person} browsing cannabis products at a modern dispensary, curious and engaged expression, friendly budtender explaining options, clean well-lit retail environment, educational lifestyle photography",
                "cannabis education setup with a notebook, pen, and various cannabis products arranged on a clean desk, soft natural light, educational lifestyle photography",
                "beginner-friendly cannabis products — pre-rolls, low-dose edibles, and a tincture — arranged on a white surface with a guide booklet, clean educational product photography",
            ],
            "section": [
                "close-up of a beginner's guide booklet or label next to a cannabis product, informational and approachable, clean photography aesthetic",
                "macro of a cannabis product label showing dosage information, clean white background, educational product photography, soft even lighting",
                "close-up of a person's hand holding a cannabis pre-roll with a lighter nearby, approachable beginner lifestyle photography, soft natural light",
            ],
        },
        "legal": {
            "hero": [
                "state capitol building exterior under clear blue sky, American flags flying, classic government architecture, civic photography aesthetic",
                "scales of justice alongside a cannabis plant on a wooden desk, soft dramatic lighting, legal editorial photography, professional aesthetic",
                "modern courthouse exterior with cannabis leaves subtly visible in the foreground landscaping, civic photography, clear daylight",
            ],
            "section": [
                "close-up of cannabis legalization text in a state policy document, American flag softly blurred in background, civic photography",
                "macro of a government seal on a cannabis regulation document, professional document photography, clean desk surface, soft lighting",
                "close-up of a legal cannabis business license document on a desk, professional document photography, shallow depth of field",
            ],
        },
        # ── New buckets from B (image-diversity-refresh) ──────────────────────
        "grow": {
            "hero": [
                "lush indoor cannabis grow room under warm LED lights, rows of healthy cannabis plants in various stages, professional cultivation setup, green and vibrant, wide environmental shot",
                "outdoor cannabis garden under bright natural sunlight, tall healthy plants with large fan leaves, blue sky backdrop, professional cultivation photography",
                "cannabis plants in a high-tech hydroponic system with blue and red LED grow lights, clean modern cultivation facility, wide environmental shot",
            ],
            "section": [
                "close-up of cannabis plant leaves and developing buds under grow lights, rich green coloration, healthy trichome development, macro cultivation photography",
                "macro of a cannabis stem showing healthy growth nodes and developing colas under purple LED light, cultivation detail photography",
                "extreme close-up of a cannabis fan leaf with water droplets, vibrant green, backlit by grow light, macro botanical cultivation photography",
            ],
        },
        "germinat": {
            "hero": [
                "cannabis seeds on a damp paper towel showing white taproots beginning to emerge, warm soft lighting, close-up macro photography on a clean white surface, cultivation how-to aesthetic",
                "tiny cannabis seedling pushing up through dark moist soil, two cotyledon leaves unfurling, water droplets on leaves, shallow depth of field, natural daylight",
                "cannabis clones in small rockwool cubes under a humidity dome, warm propagation tray lighting, professional cultivation photography, clean setup",
            ],
            "section": [
                "extreme macro of a cannabis seed splitting open with a white taproot emerging, clean white surface, soft natural lighting, botanical macro photography",
                "close-up of a cannabis seedling's first true leaves emerging between cotyledons, macro botanical photography, warm grow light, shallow depth of field",
                "macro of a cannabis clone's root system emerging from a rockwool cube, white healthy roots visible, cultivation detail photography, soft lighting",
            ],
        },
        "harvest": {
            "hero": [
                "cannabis grower carefully trimming mature buds at a clean work station, large dense colas with heavy trichome coverage, professional cultivation photography, warm indoor lighting",
                "cannabis plants hanging upside down to dry in a dark curing room, rows of lush green colas, warm ambient lighting, professional harvest photography",
                "freshly harvested cannabis colas laid out on a drying rack, glistening trichomes, warm natural light, professional harvest and curing photography",
            ],
            "section": [
                "close-up of freshly harvested cannabis buds covered in mature amber and clear trichomes, rich colors, macro harvest photography",
                "macro of trimming scissors cutting away a sugar leaf from a cannabis bud, resin visible on the scissors, harvest detail photography, warm lighting",
                "extreme close-up of a cannabis cola's trichomes at harvest time, showing amber and clear resin heads, macro harvest photography, dark background",
            ],
        },
        "soil": {
            "hero": [
                "rich dark organic cannabis soil in a terracotta pot with a young cannabis plant thriving in it, natural daylight, clean cultivation aesthetic",
                "organic soil amendment ingredients — compost, perlite, worm castings, and kelp — arranged in small piles on a wooden workbench, cultivation preparation photography, natural light",
                "close-up of a cannabis plant's root ball being gently placed into rich living soil, hands visible, professional cultivation photography, warm natural lighting",
            ],
            "section": [
                "close-up of dark healthy organic soil showing rich texture and structure, cannabis roots visible at the edge, cultivation detail photography",
                "macro of soil components — mycorrhizal fungi threads, perlite, and organic matter — in rich living soil, scientific cultivation photography, soft natural lighting",
                "extreme close-up of a handful of rich cannabis soil being squeezed, showing moisture content and crumbly texture, cultivation photography, warm natural light",
            ],
        },
        "topical": {
            "hero": [
                "cannabis-infused topical products — jars of cream, salve tins, and roll-ons — arranged on a natural wood surface with hemp leaves, clean wellness product photography, soft natural light",
                "person applying a cannabis topical cream to their wrist, soft natural light, wellness lifestyle photography, clean bright environment",
                "artisanal cannabis balm in a small glass jar with fresh hemp leaves and beeswax nearby, natural product photography, soft warm lighting, organic wellness aesthetic",
            ],
            "section": [
                "close-up of a cannabis-infused cream being scooped from a jar, showing its smooth texture, wellness product macro photography, soft natural light",
                "macro of a cannabis topical being absorbed into skin, showing the cream's texture on the skin surface, wellness product photography, soft even lighting",
                "extreme close-up of a topical salve's texture showing herbal particles and oils, macro product photography, warm natural lighting, organic aesthetic",
            ],
        },
        "consumption": {
            "hero": [
                "various cannabis consumption methods — a rolled joint, a pipe, a vaporizer, and edibles — arranged on a wooden tray, comparison lifestyle photography, soft natural light",
                "person lighting a cannabis joint in a relaxed outdoor setting, warm golden-hour light, lifestyle photography, calm and social atmosphere",
                "cannabis consumption accessories — rolling papers, grinder, pipe, and lighter — arranged in a flat-lay on a dark slate surface, premium lifestyle product photography",
            ],
            "section": [
                "close-up of a cannabis joint being rolled, fingers shaping the paper, ground flower visible, macro lifestyle photography, warm natural lighting",
                "macro of a lit cannabis joint tip showing the cherry and rising smoke, dark background with warm glow, lifestyle macro photography",
                "extreme close-up of ground cannabis flower in a grinder, showing texture and consistency, product detail photography, soft natural light",
            ],
        },
    }

    # Find matching activity or use generic cannabis fallback.
    # Prefer the MOST SPECIFIC (longest) matching key so that e.g.
    # "best strains for anxiety" matches "anxiety"/"best strain" rather than
    # collapsing into the generic "strain" bucket that appears earlier.
    matched_key = None
    for key in activities:
        if key in keyword_lower and (matched_key is None or len(key) > len(matched_key)):
            matched_key = key
    # Also check trigger aliases for keywords that don't contain a bucket key
    # (e.g. "rosin" → concentrat, "testing" → lab result)
    for trigger, alias_target in _TRIGGER_ALIASES.items():
        if trigger in keyword_lower:
            # alias_target is the key in activities; use the trigger's length for specificity
            effective_len = len(trigger)
            if matched_key is None or effective_len > len(matched_key):
                matched_key = alias_target

    activity_hero, activity_section = None, None
    used_fallback = False

    if matched_key:
        bucket = activities[matched_key]
        hero_variants = bucket["hero"]
        section_variants = bucket["section"]
        if slug:
            activity_hero = _pick_variant(hero_variants, slug, "hero")
            activity_section = _pick_variant(section_variants, slug, "section")
        else:
            activity_hero = random.choice(hero_variants)
            activity_section = random.choice(section_variants)
    else:
        # Fallback: select from 5 varied fallback scenes deterministically
        if slug:
            fallback = _pick_variant(_FALLBACK_SCENES, slug, "fallback")
        else:
            fallback = random.choice(_FALLBACK_SCENES)
        activity_hero = fallback["hero"]
        activity_section = fallback["section"]
        matched_key = "fallback"
        used_fallback = True
        print(f"   ⚠️  WARNING: No keyword bucket match — using fallback scene for '{keyword}'")

    # Extract article-specific subject for prompt differentiation
    subject = _extract_subject(keyword, title or keyword)

    # Build prompt optimized for Nano Banana 2 (google:4@3).
    # A randomized variation clause (angle / lighting / composition / color grade)
    # is inserted per request so images built from the same base scene template
    # no longer look near-identical.
    variation = _variation_clause(image_type)
    if image_type == "hero":
        prompt = (
            f"Professional editorial photograph: {activity_hero}. "
            f"Subject context: {subject}. "
            f"{variation} "
            f"Shallow depth of field on the subject, ultra-sharp detail, photorealistic. "
            f"No text, no watermarks, no logos, no UI elements."
        )
    else:
        prompt = (
            f"Professional editorial photograph: {activity_section}. "
            f"Subject context: {subject}. "
            f"{variation} "
            f"Tight composition from a different angle than the hero shot, "
            f"tack-sharp focus on the subject, rich textures, photorealistic detail. "
            f"No text, no watermarks, no logos."
        )

    # Uniqueness guard: check and differentiate if needed
    if slug:
        prompt = _check_prompt_uniqueness(slug, prompt)
        _log_prompt(slug, matched_key, prompt, image_type)

    aspect_ratio = "16:9" if image_type == "hero" else "4:3"

    metadata = {
        "person_type": selected_person,
        "bucket": matched_key,
        "image_type": image_type,
        "season": season,
        "aspect_ratio": aspect_ratio,
        "used_fallback": used_fallback,
        "subject": subject,
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

        # Check not blank (pixel std-dev check).
        # Use ImageStat instead of Image.getdata(): getdata() is deprecated in
        # Pillow 12+ (slated for removal in Pillow 14), and its suggested
        # replacement get_flattened_data() does not exist in older Pillow, so we
        # can't rely on it. ImageStat is stable across Pillow versions and
        # computes the population std-dev in C (faster, no 700k-element Python
        # list). This matches the previous manual computation exactly.
        grayscale = image.convert("L")
        std_dev = ImageStat.Stat(grayscale).stddev[0]

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
                    "outputFormat": "JPEG",
                    # Random seed per request so identical prompts still produce
                    # distinct images (and never return a cached/deduped result).
                    "seed": random.randint(1, 2_147_483_647)
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


def generate_hero_image(keyword, slug, season, title=""):
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
        prompt, aspect_ratio, image_metadata = build_image_prompt(keyword, season, image_type="hero", slug=slug, title=title)
        width, height = IMAGE_SIZES["hero"]
        output_path = Path("site/public/images/articles") / f"{slug}.jpg"

        _generate_image_via_runware(prompt, width, height, output_path, image_type="hero")

        return f"/images/articles/{slug}.jpg", image_metadata

    except Exception as e:
        print(f"   ❌ Image generation failed: {e}")
        print("   Using default fallback image")
        return "/images/default-cannabis-hero.jpg", {}


def generate_section_image(keyword, slug, season, section_title, title=""):
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
        prompt, aspect_ratio, image_metadata = build_image_prompt(keyword, season, image_type="section", slug=slug, title=title or section_title)
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
    """Generate keyword ideas drawn from all strain content pillars."""
    keywords = []

    # Flatten all pillars and sample evenly
    all_pillar_topics = [kw for topics in STRAIN_TOPICS.values() for kw in topics]
    base = random.sample(all_pillar_topics, min(count // 2, len(all_pillar_topics)))
    keywords.extend(base)

    # Fill remainder with question-pattern keywords
    for _ in range(count - len(keywords)):
        pattern = random.choice(QUESTION_PATTERNS)
        if "{effect}" in pattern:
            keyword = pattern.format(effect=random.choice(STRAIN_EFFECTS))
        elif "{use_case}" in pattern:
            keyword = pattern.format(use_case=random.choice(STRAIN_EFFECTS))
        elif "{strain}" in pattern and "{strain1}" not in pattern:
            keyword = pattern.format(strain=random.choice(STRAIN_NAMES))
        elif "{strain1}" in pattern:
            pair = random.sample(STRAIN_NAMES, 2)
            keyword = pattern.format(strain1=pair[0], strain2=pair[1])
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

Return ONLY valid JSON, no other text. All string values — especially "content" — must be valid JSON strings: escape any double quotes and newlines inside them so the entire response parses with a strict JSON parser."""

    # Rate limit Claude API calls
    wait_for_claude()

    step_start = time.time()
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        timeout=CLAUDE_CALL_TIMEOUT,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    print(f"   ⏱️  Article draft generated in {time.time() - step_start:.1f}s")

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

    # Parse JSON response with robust extraction.
    # Build candidate JSON strings (whole response, ```json / ``` fenced blocks,
    # outermost {...} slice) and try each with the stdlib parser. Each candidate
    # is guarded independently — previously a malformed fenced block raised an
    # uncaught JSONDecodeError instead of falling through to the next strategy.
    # If every candidate fails, attempt a repair pass before giving up
    # (json_repair handles the common model edge cases: unescaped quotes in body
    # text, trailing commas). Only accept a parse that yields a JSON object.
    def _json_candidates(text):
        candidates = [text]
        if "```json" in text:
            candidates.append(text.split("```json")[1].split("```")[0].strip())
        if "```" in text:
            block = text.split("```")[1].split("```")[0].strip()
            if block.startswith("json\n"):
                block = block[5:]
            candidates.append(block)
        if "{" in text and "}" in text:
            candidates.append(text[text.index("{"):text.rindex("}") + 1])
        return [clean_json_string(c) for c in candidates]

    candidates = _json_candidates(response_text)
    article_data = None
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            article_data = parsed
            break

    if article_data is None:
        # Last resort: repair the most JSON-like candidate (the {...} slice if we
        # found one, else the raw response). json_repair is optional — if it isn't
        # installed we fall through to the informative error below.
        repair_target = candidates[-1] if candidates else response_text
        try:
            from json_repair import repair_json
            parsed = json.loads(repair_json(repair_target))
            if isinstance(parsed, dict):
                article_data = parsed
                print("   ⚠️  Article JSON was malformed; recovered with json_repair.")
        except Exception:
            article_data = None

    if article_data is None:
        # Log enough of the raw output to actually diagnose the bad response,
        # instead of a bare "Expecting ',' delimiter" with no context.
        print(f"   ❌ Could not parse article JSON ({len(response_text)} chars).")
        print(f"   ❌ Raw output (first 200 chars): {response_text[:200]!r}")
        print(f"   ❌ Raw output (last 200 chars):  {response_text[-200:]!r}")
        raise ValueError("Could not parse article JSON after repair attempt")
    
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
    season = "evergreen"
    slug = article_data["slug"]

    # Generate hero image (16:9 ratio - see IMAGE_SIZES in regenerate_images.py)
    step_start = time.time()
    hero_image_path, hero_metadata = generate_hero_image(keyword, slug, season, title=article_data["title"])
    print(f"   ⏱️  Hero image step took {time.time() - step_start:.1f}s")
    article_data["featured_image"] = hero_image_path
    article_data["featured_image_alt"] = generate_alt_text(keyword, article_data["title"], "hero")
    article_data["hero_image_metadata"] = hero_metadata

    # Generate section image (4:3 ratio - see IMAGE_SIZES in regenerate_images.py)
    step_start = time.time()
    section_title = article_data.get("section_image_title", "Main Section")
    section_image_path, section_metadata = generate_section_image(keyword, slug, season, section_title, title=article_data["title"])
    print(f"   ⏱️  Section image step took {time.time() - step_start:.1f}s")

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
        step_start = time.time()
        article_data = quality_assurance_pipeline(article_data)
        print(f"   ⏱️  QA pipeline took {time.time() - step_start:.1f}s")
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
            print(f"   ⚠️  {len(critical_issues)} critical SEO issue(s) remain (informational; does not block publish)")
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
        step_start = time.time()
        videos = find_videos_for_article(
            keyword=keyword,
            article_title=article_data["title"],
            article_summary=article_data["meta_description"],
            use_curated_only=False,  # Set True to only use curated channels
            min_score=7.0,
            max_videos=2
        )
        print(f"   ⏱️  YouTube video search took {time.time() - step_start:.1f}s")

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
        print(f"   ❌ Video search error after {time.time() - step_start:.1f}s: {e}")
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
    print(f"\n🌿 Cannabis Content Generator")
    print(f"Focus: STRAIN DATABASE + EDUCATION")
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
        "season": "evergreen",
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

        # Machine-readable result line for the pipeline's score gate (parsed by
        # weekly_content_pipeline.run_content_generator). Keep this format stable.
        _qa_eval = article.get('qa_evaluation') or {}
        _qa_score = _qa_eval.get('scores', {}).get('overall')
        print(f"PIPELINE_RESULT qa_passed={bool(article.get('qa_passed'))} "
              f"qa_score={_qa_score if _qa_score is not None else ''}")

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
