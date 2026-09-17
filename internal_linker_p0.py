"""P0 shim: body-only internal linking + Related Reading fallback.

content_generator imports add_internal_links_to_new_article from here instead of
internal_linker so we can fix the frontmatter early-return without rewriting the
whole linker module in one MCP payload.
"""
from typing import Dict, List, Tuple

from internal_linker import (
    find_internal_link_opportunities,
    insert_internal_links,
    load_article_index,
)


def _split_frontmatter(content: str) -> Tuple[str, str]:
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[0] + "---" + parts[1] + "---", parts[2]
    return "", content


def _append_related_reading(
    body: str,
    slug: str,
    article_index: List[Dict],
    already_linked: List[Dict],
    target_total: int = 5,
) -> Tuple[str, List[Dict]]:
    linked = {link.get("target_slug") or link.get("slug") for link in already_linked}
    linked.add(slug)
    candidates = [a for a in article_index if a.get("slug") and a["slug"] not in linked]
    needed = max(0, target_total - len(already_linked))
    picks = candidates[:needed]
    if not picks:
        return body, already_linked

    lines = ["", "## Related Reading", ""]
    inserted = list(already_linked)
    for article in picks:
        title = article.get("title") or article["slug"].replace("-", " ").title()
        url = f"/articles/{article['slug']}"
        lines.append(f"- [{title}]({url})")
        inserted.append(
            {
                "target_slug": article["slug"],
                "target_title": title,
                "anchor_text": title,
                "url": url,
            }
        )
    lines.append("")
    return body.rstrip() + "\n" + "\n".join(lines), inserted


def add_internal_links_to_new_article(content: str, slug: str) -> Tuple[str, List[Dict]]:
    """Supports body-only markdown (publish path passes body before frontmatter)."""
    article_index = load_article_index()
    frontmatter_text, body = _split_frontmatter(content)

    opportunities = find_internal_link_opportunities(body, slug, article_index, max_links=5)
    modified_body, inserted = (
        insert_internal_links(body, opportunities) if opportunities else (body, [])
    )

    if len(inserted) < 3 and article_index:
        modified_body, inserted = _append_related_reading(
            modified_body, slug, article_index, inserted, target_total=5
        )

    if not inserted:
        return content, []

    return frontmatter_text + modified_body, inserted
