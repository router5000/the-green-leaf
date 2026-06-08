#!/usr/bin/env python3
"""
Seed the Supabase strains database with cannabis strain data generated via Claude.

Requirements: pip install anthropic supabase
Usage:        python seed_strains.py
Env vars:     ANTHROPIC_API_KEY, SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL), SUPABASE_SECRET_KEY
"""

import os
import sys
import json
import re
import time
import logging
from typing import Any

import anthropic
from supabase import create_client, Client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Strain list ───────────────────────────────────────────────────────────────

STRAINS = [
    # Classics (already seeded)
    "Blue Dream", "OG Kush", "Girl Scout Cookies", "Sour Diesel",
    "Granddaddy Purple", "Jack Herer", "White Widow", "Northern Lights",
    "AK-47", "Gorilla Glue", "Wedding Cake", "Gelato", "Pineapple Express",
    "Purple Haze", "Green Crack", "Trainwreck", "Bubba Kush", "Afghan Kush",
    "Amnesia Haze", "Chemdawg",

    # Indica Dominant
    "Blueberry", "Purple Kush", "Skywalker OG", "Death Star", "Kosher Kush",
    "Master Kush", "Hindu Kush", "Blackberry Kush", "Platinum OG",
    "LA Confidential", "Tahoe OG", "SFV OG", "Pre-98 Bubba Kush",
    "Violator Kush", "Critical Kush", "Banana Kush", "Grape Ape", "GDP",
    "Ice Cream Cake", "Runtz", "Zkittlez", "Gelato 41", "Purple Punch",
    "Do-Si-Dos", "Biscotti", "Mimosa", "Sherbet", "Animal Cookies",
    "Slurricane", "Mac 1",

    # Sativa Dominant
    "Durban Poison", "Super Silver Haze", "Strawberry Cough", "Maui Wowie",
    "Acapulco Gold", "Lemon Haze", "Super Lemon Haze", "Chocolope", "Tangie",
    "Candyland", "Ghost Train Haze", "Moby Dick", "Lamb's Bread",
    "Panama Red", "Kali Mist", "Neville's Haze", "Cinderella 99",
    "Casey Jones", "Citrique", "Electra", "Lemon Skunk", "Grapefruit",
    "Jet Fuel", "Bruce Banner", "Headband", "Carnival", "Golden Goat",
    "Island Sweet Skunk", "Clementine", "Tropicana Cookies",

    # Hybrid Balanced
    "Blue Cheese", "Cheese", "Critical Mass", "White Russian", "Lemon OG",
    "Fire OG", "Larry OG", "Cookies and Cream", "Cherry Pie", "Sunset Sherbet",
    "Forbidden Fruit", "Papaya", "Mango Kush", "Pineapple Kush",
    "Strawberry Banana", "Watermelon", "Gushers", "Permanent Marker",
    "Jealousy", "Cereal Milk", "Gary Payton", "Wonka Bars", "Pink Panties",
    "Tropicana Punch", "Apples and Bananas", "Gastro Pop", "Grease Monkey",
    "Motorbreath", "Sundae Driver", "Lemon Cherry Gelato", "Obama Runtz",
    "White Runtz", "Pink Runtz", "Space Runtz", "Grape Runtz",
    "Watermelon Runtz", "Peach Ringz", "Candy Rain", "Modified Grapes", "RS11",

    # High CBD / Medical
    "Charlotte's Web", "ACDC", "Harlequin", "Cannatonic", "Ringo's Gift",
    "Sour Tsunami", "Pennywise", "Harle-Tsu", "CBD Critical Mass",
    "CBD Shark", "Dance World", "Remedy", "Stephen Hawking Kush",
    "Sweet and Sour Widow", "Canna-Tsu", "Omrita Rx3", "Argyle",
    "Valentine X", "Trident", "CBD Mango Haze",

    # Autoflowering
    "Amnesia Haze Auto", "Northern Lights Auto", "Blueberry Auto",
    "Girl Scout Cookies Auto", "Gorilla Glue Auto", "Wedding Cake Auto",
    "Blue Dream Auto", "OG Kush Auto", "White Widow Auto", "Zkittlez Auto",
    "Gelato Auto", "Runtz Auto", "Critical Auto", "Royal Dwarf", "Quick One",
    "Easy Bud", "Cream Caramel Auto", "Pineapple Express Auto",
    "Strawberry Auto", "Purple Kush Auto",

    # Legendary / Heritage
    "Skunk #1", "Haze", "Afghani", "Colombian Gold", "Thai",
    "Mexican Sativa", "Nepalese", "Malawi Gold", "Congolese",
    "Punto Rojo", "Durban", "Hindu Kush Original", "Mazar I Sharif",
    "Chitral", "Kerala", "Oaxacan Highland", "Swazi Gold",
    "Kilimanjaro", "Red Congolese", "Aceh",
]

BATCH_SIZE = 5

# ── Helpers ───────────────────────────────────────────────────────────────────

def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"[''']", "", s)
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"\s+", "-", s.strip())
    return s


def extract_json(text: str) -> Any:
    """Extract a JSON array from a response that may include markdown fences."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"(\[.*\])", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    raise ValueError("No JSON array found in Claude response")

# ── AI generation ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a cannabis cultivation and pharmacology expert with deep knowledge of "
    "strains, terpenes, genetics, and growing characteristics. "
    "Return only valid JSON — no prose, no markdown fences, no commentary."
)


def generate_batch(client: anthropic.Anthropic, names: list[str]) -> list[dict]:
    prompt = f"""Generate detailed, accurate cannabis strain data for these strains: {', '.join(names)}

Return a JSON array with one object per strain. Each object must include ALL of these fields exactly:

{{
  "name": string,
  "slug": string,                          // URL-friendly, lowercase, hyphens only
  "aka": string[],                         // 2-4 alternative names
  "strain_type": "indica"|"sativa"|"hybrid",
  "thc_min": number,
  "thc_max": number,
  "cbd_min": number,
  "cbd_max": number,
  "description": string,                   // 300-400 words, SEO-optimized, factual, unique
  "short_description": string,             // 2-3 sentences
  "flavors": string[],                     // 3-5 items, lowercase
  "aromas": string[],                      // 3-5 items, lowercase
  "colors": string[],                      // 2-3 items, lowercase
  "difficulty": "easy"|"moderate"|"difficult",
  "flowering_time_days": integer,
  "yield_indoor": string,                  // e.g. "400-500g/m²"
  "yield_outdoor": string,                 // e.g. "500-600g/plant"
  "height_indoor": string,                 // e.g. "100-150cm"
  "height_outdoor": string,               // e.g. "150-200cm"
  "origin_country": string,
  "effects": [                             // 5-8 effects total
    {{"effect_name": string, "effect_type": "positive"|"negative"|"medical", "intensity": 1-5}}
  ],
  "terpenes": [                            // 3-5 terpenes, percentages summing ~1.0-2.5
    {{"terpene_name": string, "percentage": number}}
  ],
  "genetics": [                            // 1-3 parent strains
    {{"parent_strain_name": string, "parent_type": "mother"|"father"}}
  ],
  "seo": {{
    "meta_title": string,                  // max 60 chars, include strain name + "Strain"
    "meta_description": string,            // max 160 chars
    "focus_keyword": string,
    "og_image_url": ""
  }}
}}

Return ONLY the JSON array. No other text."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text
    return extract_json(raw)

# ── Supabase insertion ────────────────────────────────────────────────────────

def strain_exists(sb: Client, slug: str) -> bool:
    result = sb.table("strains").select("id").eq("slug", slug).execute()
    return len(result.data) > 0


def insert_strain(sb: Client, data: dict) -> bool:
    slug = data.get("slug") or slugify(data["name"])

    if strain_exists(sb, slug):
        log.info("  skip     %s (already exists)", slug)
        return False

    strain_row = {
        "slug":                slug,
        "name":                data["name"],
        "aka":                 data.get("aka", []),
        "strain_type":         data["strain_type"],
        "thc_min":             data.get("thc_min"),
        "thc_max":             data.get("thc_max"),
        "cbd_min":             data.get("cbd_min"),
        "cbd_max":             data.get("cbd_max"),
        "description":         data.get("description"),
        "short_description":   data.get("short_description"),
        "flavors":             data.get("flavors", []),
        "aromas":              data.get("aromas", []),
        "colors":              data.get("colors", []),
        "difficulty":          data.get("difficulty"),
        "flowering_time_days": data.get("flowering_time_days"),
        "yield_indoor":        data.get("yield_indoor"),
        "yield_outdoor":       data.get("yield_outdoor"),
        "height_indoor":       data.get("height_indoor"),
        "height_outdoor":      data.get("height_outdoor"),
        "origin_country":      data.get("origin_country"),
        "published":           True,
    }

    result = sb.table("strains").insert(strain_row).execute()
    strain_id = result.data[0]["id"]

    if effects := data.get("effects"):
        sb.table("effects").insert([
            {"strain_id": strain_id, **e} for e in effects
        ]).execute()

    if terpenes := data.get("terpenes"):
        sb.table("terpenes").insert([
            {"strain_id": strain_id, **t} for t in terpenes
        ]).execute()

    if genetics := data.get("genetics"):
        sb.table("genetics").insert([
            {"strain_id": strain_id, **g} for g in genetics
        ]).execute()

    if seo := data.get("seo"):
        sb.table("strain_seo").insert({
            "strain_id": strain_id, **seo
        }).execute()

    log.info("  inserted %s (%s)", data["name"], slug)
    return True

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    supabase_url = os.environ.get("SUPABASE_URL") or os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SECRET_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")

    if not supabase_url or not supabase_key:
        sys.exit("ERROR: Missing SUPABASE_URL (or NEXT_PUBLIC_SUPABASE_URL) and SUPABASE_SECRET_KEY")
    if not anthropic_key:
        sys.exit("ERROR: Missing ANTHROPIC_API_KEY")

    sb = create_client(supabase_url, supabase_key)
    ai = anthropic.Anthropic(api_key=anthropic_key)

    batches = [STRAINS[i:i + BATCH_SIZE] for i in range(0, len(STRAINS), BATCH_SIZE)]
    total_inserted = total_skipped = total_errors = 0

    for batch_num, batch in enumerate(batches, 1):
        log.info("Batch %d/%d — generating: %s", batch_num, len(batches), ", ".join(batch))

        try:
            strains_data = generate_batch(ai, batch)
        except Exception as e:
            log.error("  Claude generation failed for batch %d: %s", batch_num, e)
            total_errors += len(batch)
            continue

        for strain_data in strains_data:
            try:
                if insert_strain(sb, strain_data):
                    total_inserted += 1
                else:
                    total_skipped += 1
            except Exception as e:
                log.error("  Insert failed for %s: %s", strain_data.get("name", "?"), e)
                total_errors += 1

        if batch_num < len(batches):
            log.info("Sleeping 2s before next batch...")
            time.sleep(2)

    log.info("Done — inserted: %d  skipped: %d  errors: %d", total_inserted, total_skipped, total_errors)


if __name__ == "__main__":
    main()
