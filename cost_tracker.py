#!/usr/bin/env python3
"""
Cost Tracker for API Calls
Tracks API costs per article and generates monthly reports.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Cost log directory
COST_LOG_DIR = Path(".logs")

# Claude pricing (per 1K tokens) - Update as pricing changes
CLAUDE_PRICING = {
    "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
}

# YouTube API quota costs (units per operation)
YOUTUBE_QUOTA_COSTS = {
    "search": 100,
    "videos": 1,  # videos.list for stats
}


class CostTracker:
    """
    Track API costs during article generation.

    Usage:
        tracker = CostTracker("my-article-slug")
        tracker.log_claude_usage(message.usage, "claude-sonnet-4-20250514")
        tracker.log_runware_cost("hero", 0.002)
        tracker.save()
    """

    def __init__(self, article_slug: str):
        self.article_slug = article_slug
        self.start_time = datetime.now()
        self.claude_calls = []
        self.runware_calls = []
        self.youtube_calls = []

    def log_claude_usage(self, usage, model: str):
        """
        Log Claude API usage from message.usage object.

        Args:
            usage: The message.usage object from Claude API response
            model: Model name (e.g., "claude-sonnet-4-20250514")
        """
        input_tokens = getattr(usage, 'input_tokens', 0)
        output_tokens = getattr(usage, 'output_tokens', 0)

        # Calculate cost
        pricing = CLAUDE_PRICING.get(model, {"input": 0.003, "output": 0.015})
        cost = (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])

        self.claude_calls.append({
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(cost, 6)
        })

    def log_runware_cost(self, image_type: str, cost: float):
        """
        Log Runware cost from API response.

        Args:
            image_type: "hero" or "section"
            cost: Cost value from API response
        """
        self.runware_calls.append({
            "image_type": image_type,
            "cost_usd": cost if cost else 0.002  # Default estimate if not provided
        })

    def log_youtube_quota(self, operation: str, count: int = 1):
        """
        Log YouTube API quota usage.

        Args:
            operation: "search" or "videos"
            count: Number of API calls
        """
        units = YOUTUBE_QUOTA_COSTS.get(operation, 1) * count
        self.youtube_calls.append({
            "operation": operation,
            "calls": count,
            "quota_units": units
        })

    def _summarize(self) -> dict:
        """Summarize costs by category."""
        claude_total = sum(c["cost_usd"] for c in self.claude_calls)
        claude_input_tokens = sum(c["input_tokens"] for c in self.claude_calls)
        claude_output_tokens = sum(c["output_tokens"] for c in self.claude_calls)

        runware_total = sum(c["cost_usd"] for c in self.runware_calls)

        youtube_quota = sum(c["quota_units"] for c in self.youtube_calls)

        return {
            "claude": {
                "calls": len(self.claude_calls),
                "input_tokens": claude_input_tokens,
                "output_tokens": claude_output_tokens,
                "total_cost_usd": round(claude_total, 4)
            },
            "runware": {
                "images": len(self.runware_calls),
                "total_cost_usd": round(runware_total, 4)
            },
            "youtube": {
                "calls": len(self.youtube_calls),
                "quota_units": youtube_quota
            },
            "total_estimated_usd": round(claude_total + runware_total, 4)
        }

    def save(self):
        """Save costs to monthly JSONL log."""
        COST_LOG_DIR.mkdir(exist_ok=True)

        log_file = COST_LOG_DIR / f"costs_{datetime.now().strftime('%Y%m')}.jsonl"

        entry = {
            "timestamp": datetime.now().isoformat(),
            "article_slug": self.article_slug,
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "costs": self._summarize(),
            "details": {
                "claude_calls": self.claude_calls,
                "runware_calls": self.runware_calls,
                "youtube_calls": self.youtube_calls
            }
        }

        with open(log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

        summary = self._summarize()
        print(f"   💰 Cost tracked: ${summary['total_estimated_usd']:.4f} "
              f"(Claude: ${summary['claude']['total_cost_usd']:.4f}, "
              f"Runware: ${summary['runware']['total_cost_usd']:.4f})")


def generate_monthly_cost_report(month: Optional[str] = None) -> dict:
    """
    Generate cost report for a given month.

    Args:
        month: Month in YYYYMM format (default: current month)

    Returns:
        Report dictionary with aggregated costs
    """
    if month is None:
        month = datetime.now().strftime("%Y%m")

    log_file = COST_LOG_DIR / f"costs_{month}.jsonl"

    if not log_file.exists():
        return {"error": f"No cost log found for {month}", "month": month}

    entries = []
    with open(log_file) as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    if not entries:
        return {"error": "Empty cost log", "month": month}

    # Aggregate costs
    total_claude = sum(e["costs"]["claude"]["total_cost_usd"] for e in entries)
    total_runware = sum(e["costs"]["runware"]["total_cost_usd"] for e in entries)
    total_tokens_in = sum(e["costs"]["claude"]["input_tokens"] for e in entries)
    total_tokens_out = sum(e["costs"]["claude"]["output_tokens"] for e in entries)
    total_images = sum(e["costs"]["runware"]["images"] for e in entries)
    total_youtube_quota = sum(e["costs"]["youtube"]["quota_units"] for e in entries)

    # Per-article breakdown
    articles = [
        {
            "slug": e["article_slug"],
            "date": e["timestamp"][:10],
            "cost_usd": e["costs"]["total_estimated_usd"]
        }
        for e in entries
    ]

    report = {
        "month": month,
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_articles": len(entries),
            "total_cost_usd": round(total_claude + total_runware, 2),
            "avg_cost_per_article": round((total_claude + total_runware) / len(entries), 4) if entries else 0,
            "claude": {
                "total_cost_usd": round(total_claude, 2),
                "input_tokens": total_tokens_in,
                "output_tokens": total_tokens_out
            },
            "runware": {
                "total_cost_usd": round(total_runware, 2),
                "total_images": total_images
            },
            "youtube": {
                "total_quota_units": total_youtube_quota,
                "estimated_daily_quota_pct": round(total_youtube_quota / 10000 * 100, 1)  # 10K daily quota
            }
        },
        "articles": sorted(articles, key=lambda x: x["date"], reverse=True)
    }

    return report


def print_cost_report(month: Optional[str] = None):
    """Print formatted cost report to console."""
    report = generate_monthly_cost_report(month)

    if "error" in report:
        print(f"❌ {report['error']}")
        return

    print("\n" + "=" * 60)
    print(f"💰 COST REPORT - {report['month']}")
    print("=" * 60)

    s = report["summary"]
    print(f"\n📊 Summary:")
    print(f"   Articles generated: {s['total_articles']}")
    print(f"   Total cost: ${s['total_cost_usd']:.2f}")
    print(f"   Avg per article: ${s['avg_cost_per_article']:.4f}")

    print(f"\n🤖 Claude API:")
    print(f"   Cost: ${s['claude']['total_cost_usd']:.2f}")
    print(f"   Input tokens: {s['claude']['input_tokens']:,}")
    print(f"   Output tokens: {s['claude']['output_tokens']:,}")

    print(f"\n🎨 Runware (Images):")
    print(f"   Cost: ${s['runware']['total_cost_usd']:.2f}")
    print(f"   Images generated: {s['runware']['total_images']}")

    print(f"\n📺 YouTube API:")
    print(f"   Quota used: {s['youtube']['total_quota_units']:,} units")
    print(f"   Daily quota: {s['youtube']['estimated_daily_quota_pct']}%")

    print(f"\n📝 Articles:")
    for article in report["articles"][:10]:  # Show top 10
        print(f"   {article['date']} | ${article['cost_usd']:.4f} | {article['slug']}")

    if len(report["articles"]) > 10:
        print(f"   ... and {len(report['articles']) - 10} more")

    print("=" * 60 + "\n")


# Global tracker instance for current article (set by content_generator)
_current_tracker: Optional[CostTracker] = None


def get_tracker() -> Optional[CostTracker]:
    """Get current cost tracker instance."""
    return _current_tracker


def set_tracker(tracker: CostTracker):
    """Set current cost tracker instance."""
    global _current_tracker
    _current_tracker = tracker


def clear_tracker():
    """Clear current cost tracker."""
    global _current_tracker
    _current_tracker = None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cost tracking and reports")
    parser.add_argument("--report", action="store_true", help="Generate cost report")
    parser.add_argument("--month", type=str, help="Month in YYYYMM format (default: current)")

    args = parser.parse_args()

    if args.report:
        print_cost_report(args.month)
    else:
        print("Usage:")
        print("  python cost_tracker.py --report")
        print("  python cost_tracker.py --report --month 202601")
