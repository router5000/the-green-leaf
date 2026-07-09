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

# Randomized photographic variation attributes — mirrors content_generator.py.
# Give each generated image a distinct angle, light, framing and color grade so
# images built from the same base scene template no longer look near-identical.
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
    """Return a randomized photographic-variation sentence to append to a prompt."""
    key = "hero" if image_type == "hero" else "section"
    angle = random.choice(_VARIATION_ANGLES[key])
    lighting = random.choice(_VARIATION_LIGHTING)
    composition = random.choice(_VARIATION_COMPOSITION[key])
    palette = random.choice(_VARIATION_PALETTE)
    return f"Shot from {angle} in {lighting}, {composition}, {palette}."


# ── Deterministic variant selection — mirrors content_generator.py ───────────
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
    import json as _json
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
        f.write(_json.dumps(entry) + "\n")


def _check_prompt_uniqueness(slug, prompt):
    """Check if exact prompt was already used for a different slug.
    If so, append a differentiating detail from the slug."""
    import json as _json
    log_path = Path(".logs/image_prompts.jsonl")
    if not log_path.exists():
        return prompt
    existing_slugs = set()
    for line in log_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            entry = _json.loads(line)
            if entry.get("prompt") == prompt:
                existing_slugs.add(entry.get("slug", ""))
        except _json.JSONDecodeError:
            continue
    if existing_slugs and slug not in existing_slugs:
        detail = slug.replace("-", " ").split(":")[0].strip()
        prompt = f"{prompt} Distinctive subject context: {detail}."
    return prompt


# Trigger aliases — mirrors content_generator.py
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
    Build an optimized cannabis image prompt for Nano Banana 2 (google:4@3).

    Merged system mirroring content_generator.py — keep both in sync.
    Combines: _variation_clause randomization, longest-match bucket selection,
    2-3 scene variants per bucket with deterministic slug-hash selection,
    article-specific subject injection, 5 varied fallback scenes,
    prompt uniqueness logging + collision guard, distinct hero/section composition.
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

    # Activity descriptions by keyword theme.
    # Each key maps to {"hero": [2-3 variants], "section": [2-3 variants]}.
    # Hero: wide cinematic environmental shot | Section: tight detail/texture shot.
    activities = {
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

    # Prefer the MOST SPECIFIC (longest) matching key so articles stop
    # collapsing into the generic "strain" bucket that appears earlier.
    matched_key = None
    for key in activities:
        if key in keyword_lower and (matched_key is None or len(key) > len(matched_key)):
            matched_key = key
    # Also check trigger aliases
    for trigger, alias_target in _TRIGGER_ALIASES.items():
        if trigger in keyword_lower:
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

    # Randomized variation clause per request keeps same-template images distinct.
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
    print(f"   📷 Keyword match: '{matched_key or 'fallback'}' | Type: {image_type}")

    return prompt, aspect_ratio


def generate_image(keyword, slug, season, image_type="hero", title=""):
    """Generate a single image using Runware API"""

    print(f"🎨 Generating {image_type} image for: {keyword}")

    try:
        # Build prompt
        prompt, aspect_ratio = build_image_prompt(keyword, season, image_type, slug=slug, title=title)

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
                "outputFormat": "JPEG",
                # Random seed per request so identical prompts still produce
                # distinct images (and never return a cached/deduped result).
                "seed": random.randint(1, 2_147_483_647)
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
    hero_path = generate_image(keyword, slug, season, image_type="hero", title=keyword)

    # Generate section image
    section_path = generate_image(keyword, slug, season, image_type="section", title=keyword)

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
