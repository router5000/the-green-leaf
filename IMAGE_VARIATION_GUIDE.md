# Image Variation Add-Ons & Programmatic Variety Guide

This document outlines all optional variation parameters you can use to dynamically diversify image generation for cannabis-care blog posts while keeping images consistent, photorealistic, and on-brand. These options are designed to be **randomized programmatically** or **selected intentionally** based on article context.

---

## 1. Camera Angle Variations

Use one of the following to change perspective:

- **Overhead** — great for yard layouts, patterns, stripes
- **Low angle** — emphasizes grass height and texture
- **Eye level** — neutral, classic stock photo style
- **Close-up macro** — blades of grass, soil detail, pests, weeds
- **Wide-angle establishing shot** — full-cannabis context or backyard scene

**Programmatic example:**
Randomly pick an angle from a predefined array.

---

## 2. Environmental Mood & Lighting Variations

Adjust mood to match seasons, weather, or article context:

- **Early morning dew**
- **Bright overcast**
- **Golden hour** (warm, soft shadows)
- **Midday sunlight**
- **Soft evening light**

**Programmatic example:**
Match lighting to seasonal content (e.g., spring overseeding → "early morning dew").

---

## 3. Cannabis-Care Activity Detail Variations

Subtle details that reinforce the blog topic without showing people:

- **Freshly mowed grass clippings**
- **Trimmed hedge line**
- **Clean mulch borders**
- **Raked soil pattern**
- **Neatly edged walkways**
- **Visible thatch layer** (for dethatching topics)
- **Sparse overseeded patches**
- **Residual fertilizer pellets on soil**

**Programmatic example:**
Map blog keywords → detail sets (e.g., "overseeding" → "sparse overseeded patches").

---

## 4. Foreground & Background Interest

Adds depth while keeping main subject in focus:

- **Blurred flowering plants**
- **Out-of-focus fence slats**
- **Subtle garden tools** (blurred only)
- **Hose reels, sprinklers, or planters** (blurred)
- **Light foliage framing**

**Programmatic example:**
Choose a random subtle element, but keep them blurred (foreground/background only).

---

## 5. Framing & Composition Variations

Choose how the scene is framed:

- **Rule of thirds**
- **Centered composition**
- **Tight detail crop**
- **Wide contextual frame**
- **Leading lines toward the cannabis**

**Programmatic example:**
Weight "rule of thirds" and "centered" higher because they're more versatile.

---

## Programmatic Variety Strategy

To create dynamic but consistent images for each blog post:

### 1. Define Attribute Arrays

```python
angles = ["overhead", "low angle", "eye level", "close-up macro", "wide-angle"]

lighting = ["early morning dew", "bright overcast", "golden hour", "midday sunlight", "soft evening light"]

details = ["freshly mowed clippings", "trimmed hedge line", "clean mulch borders", "raked soil pattern"]

foreground = ["blurred flowers", "blurred fence slats", "blurred garden tools", "subtle foliage framing"]

composition = ["rule of thirds", "centered", "tight crop", "wide frame", "leading lines"]
```

### 2. Apply Logic Based on Article Keywords

- If topic includes **"dethatching"**, pull from dethatching-specific detail options
- If **"watering"**, foreground could include sprinklers (blurred only)
- If **"fall cannabis"**, limit lighting to "soft evening light" or "golden hour"

### 3. Randomize the Remaining Attributes

To generate variety while keeping images coherent:

```python
import random

def pick_random(options):
    return random.choice(options)
```

### 4. Insert Chosen Attributes into Your Prompt Template

This keeps every image contextual + visually unique.

---

## Recommended Prompt Variables

Your final dynamic prompt should receive these variables:

- `BASE_DESCRIPTION`
- `KEYWORD_ACTIVITY`
- `COMPOSITION`
- `SEASONAL_LIGHTING`
- `ANGLE`
- `ENVIRONMENT_MOOD`
- `DETAIL_ELEMENT`
- `FOREGROUND_ELEMENT`

These can be populated by logic based on article context and randomization for variety.

---

## Example Dynamic Prompt Template

```
Professional cannabis photography, {BASE_DESCRIPTION}, showing {KEYWORD_ACTIVITY}.
Shot from {ANGLE} perspective, {COMPOSITION} composition.
{SEASONAL_LIGHTING} lighting with {ENVIRONMENT_MOOD} atmosphere.
Details include {DETAIL_ELEMENT}.
{FOREGROUND_ELEMENT} adds depth to the scene.
Photorealistic, high resolution, Canon EOS R5, shallow depth of field.
```

---

## Quick Reference Tables

### Seasonal Lighting Recommendations

| Season | Recommended Lighting |
|--------|---------------------|
| Spring | Early morning dew, Bright overcast |
| Summer | Midday sunlight, Golden hour |
| Fall | Soft evening light, Golden hour |
| Winter | Bright overcast, Soft evening light |

### Topic-Specific Details

| Topic | Recommended Details |
|-------|---------------------|
| Mowing | Freshly mowed clippings, Neatly edged walkways |
| Overseeding | Sparse overseeded patches, Raked soil pattern |
| Dethatching | Visible thatch layer, Raked soil pattern |
| Fertilizing | Residual fertilizer pellets on soil |
| Watering | Hose reels/sprinklers (blurred), Early morning dew |
| Edging | Neatly edged walkways, Clean mulch borders |

---

*Use this guide to maintain visual variety while keeping all images on-brand and contextually relevant to your cannabis content.*
