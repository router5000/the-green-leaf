# Runware AI Image Integration - Complete

## Summary

✅ Successfully migrated from Reve Image to Runware AI
✅ Updated to candid documentary-style images with people (no faces)
✅ All image generation functions updated
✅ API integration tested and working

## Changes Made

### 1. API Configuration
- **Endpoint**: `https://api.runware.ai/v1`
- **API Key**: `aSGjkn0N1yQ019hlPP62INlzuwryN1vA`
- **Authentication**: Body authentication with `apiKey` in request

### 2. Image Style Changes
**Old Style**: Static lawn photos without people
**New Style**: Candid documentary photos showing people actively performing lawn care tasks

Key features:
- Person shot from behind, side, or overhead (no faces visible)
- Natural working posture and body language
- Authentic outdoor work clothes (jeans, t-shirt, gloves)
- Real-life candid moments captured
- Photorealistic documentary feel

### 3. Technical Implementation

**Hero Images (16:9 landscape)**
- Resolution: 1792x1024px
- Shows person performing the main task (mowing, aerating, fertilizing, etc.)
- Wide environmental shot showing person in their yard

**Section Images (4:3)**
- Resolution: 1536x1152px
- Close-up of hands performing the task
- Detail shots showing authentic hands-on work

**API Parameters**:
- Model: `runware:100@1` (default Runware model)
- Steps: 25
- CFG Scale: 7.0
- Output: URL (JPG format)

### 4. Response Format
Runware wraps results in a `data` array:
```json
{
  "data": [
    {
      "taskType": "imageInference",
      "imageUUID": "...",
      "taskUUID": "...",
      "seed": 123456,
      "imageURL": "https://im.runware.ai/image/ws/2/ii/..."
    }
  ]
}
```

## Testing

Run the test script to verify integration:
```bash
python3 test_runware.py
```

Expected output:
- ✅ API connection successful
- ✅ Image generated and downloaded
- ✅ Test image saved to `test_output/test_runware_lawn_mowing.jpg`

## Sample Prompt for Runware Playground

Use this prompt to test in Runware's playground:

```
Candid documentary-style photograph of person performing lawn care, Candid action shot of person pushing walk-behind lawn mower across yard, photographed from behind or side angle (face not visible), wearing casual outdoor clothes, fresh mowing stripes visible behind them, mid-stride natural movement.

Shot with professional DSLR camera, Canon EOS R5 with 24-70mm f/2.8 lens, candid documentary photography style. Wide environmental shot showing person in their yard, authentic moment. Eye level candid angle perspective.

Person shot from behind, side angle, or overhead - FACE NOT VISIBLE, no identifiable facial features, back of head or body only.

Lighting: warm golden hour backlight (late afternoon sun), clear azure blue sky, vibrant saturated green colors, long shadows creating depth. Golden hour warmth atmosphere.

Photography style: natural shallow depth of field, candid authentic moment, rule of thirds composition, natural moment captured, authentic real-life scene, ultra-sharp focus.

Casual authentic work clothes appropriate for lawn care - jeans, t-shirt, work gloves, boots - realistic worn-in appearance.

Suburban residential setting, well-maintained yard, real homeowner doing their own lawn care.

Candid documentary feel: person mid-action, natural body language, unposed authentic moment, real work in progress.

Color grading: natural realistic tones, vibrant greens, slight warmth, authentic documentary style.

Photorealistic quality: looks like real candid photograph from home improvement blog or lawn care guide, genuine moment captured.

Ultra-high resolution, lifestyle photography quality, relatable and aspirational.

IMPORTANT: No faces visible, no identifiable facial features, shot from behind or side angles only.

Absolutely no text, no watermarks, no logos, no graphics, no artificial overlays.
```

**Settings for Playground**:
- Width: 1792
- Height: 1024
- Model: runware:100@1
- Steps: 25
- CFG Scale: 7.0

## Activity-Specific Prompts

The system automatically generates appropriate prompts for:
- ✅ Mowing (person pushing mower)
- ✅ Aerating (person operating aerator)
- ✅ Watering (person watering with hose)
- ✅ Fertilizing (person using broadcast spreader)
- ✅ Weeding (person pulling weeds or spraying)
- ✅ Dethatching (person using power dethatcher)
- ✅ Overseeding (person spreading seed)
- ✅ Edging/Trimming (person using string trimmer)
- ✅ Raking (person raking leaves)
- ✅ Soil Testing (person collecting soil samples)

## Next Steps

1. ✅ Test the integration with `python3 test_runware.py`
2. Test in Runware playground with the sample prompt above
3. Generate a full article to see both hero and section images
4. Adjust CFG Scale or steps if needed for style refinement

## Cost Tracking

Runware API responses include a `cost` field for tracking usage per image generation.

## Documentation

- [Runware API Docs](https://runware.ai/docs/en/image-inference/api-reference)
- [How to Connect](https://runware.ai/docs/en/getting-started/how-to-connect)
- [Python SDK](https://runware.ai/docs/en/libraries/python)
