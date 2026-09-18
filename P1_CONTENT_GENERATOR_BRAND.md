# P1 Content generator brand

`content_generator.py` on this branch is a multipart zlib loader that expands
`_cg_payload_{0,1,2}.txt` at import time (GitHub MCP push size limits).

Expanded source replaces writer + SITE FOCUS branding:
- `The Green Leaf` → `The Strain Report` (2 prompt strings)
- Amazon affiliate tag `thegreenleaf2-20` unchanged (if present elsewhere)

All three payload parts are present on this branch. Runtime behavior matches
plain `content_generator.py` with the brand strings updated.
