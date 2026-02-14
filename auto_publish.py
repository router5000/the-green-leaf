#!/usr/bin/env python3
"""
Auto-Publish Module for Lawn Care Content Engine

Handles automatic Git operations after content generation:
- Commits new articles and images
- Pushes to main branch
- Triggers Vercel deployment

Can be run standalone or imported by the pipeline.
"""

import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import yaml

# Configuration
REPO_ROOT = Path(__file__).parent  # Assumes script is in repo root
SITE_PATH = REPO_ROOT / "site"
CONTENT_PATH = SITE_PATH / "content" / "posts"
IMAGES_PATH = SITE_PATH / "public" / "images" / "articles"
LOG_DIR = REPO_ROOT / "logs"

# Logging setup
LOG_DIR.mkdir(exist_ok=True)
logger = logging.getLogger("auto_publish")
logger.setLevel(logging.INFO)
_file_handler = logging.FileHandler(LOG_DIR / "auto_publish.log")
_file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(_file_handler)


def _log(msg: str) -> None:
    """Print to stdout and write to log file."""
    print(msg)
    logger.info(msg)


def run_git_command(args: list[str], cwd: Optional[Path] = None) -> tuple[bool, str]:
    """
    Run a git command and return success status and output.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_git_status() -> dict:
    """
    Check current git status and return info about changes.
    """
    status = {
        "clean": True,
        "new_articles": [],
        "new_images": [],
        "modified": [],
        "branch": "unknown"
    }
    
    # Get current branch
    success, output = run_git_command(["branch", "--show-current"])
    if success:
        status["branch"] = output.strip()
    
    # Get status
    success, output = run_git_command(["status", "--porcelain"])
    if not success:
        return status
    
    for line in output.strip().split("\n"):
        if not line:
            continue
        
        status_code = line[:2]
        filepath = line[3:]
        
        if "content/posts/" in filepath and filepath.endswith(".md"):
            if status_code.startswith("?") or status_code.startswith("A"):
                status["new_articles"].append(filepath)
            elif status_code.startswith("M"):
                status["modified"].append(filepath)
                
        elif "images/articles/" in filepath:
            if status_code.startswith("?") or status_code.startswith("A"):
                status["new_images"].append(filepath)
    
    status["clean"] = not (status["new_articles"] or status["new_images"] or status["modified"])
    
    return status


def check_article_qa(md_file: Path, min_score: float = 7.0) -> tuple[bool, str]:
    """
    Check if an article passes QA thresholds before publishing.
    Returns (passed, reason).
    """
    try:
        content = md_file.read_text(encoding='utf-8')
        if not content.startswith('---'):
            return True, "No frontmatter (legacy article)"

        parts = content.split('---', 2)
        if len(parts) < 3:
            return True, "Malformed frontmatter"

        fm = yaml.safe_load(parts[1])
        if not fm:
            return True, "Empty frontmatter"

        qa_passed = fm.get('qa_passed')
        qa_score = fm.get('qa_score', 0)
        needs_review = fm.get('needs_manual_review', False)

        if needs_review:
            return False, f"Flagged for manual review (score: {qa_score})"

        if qa_passed is False:
            return False, f"QA failed (score: {qa_score})"

        if qa_score and float(qa_score) < min_score:
            return False, f"QA score {qa_score} below threshold {min_score}"

        return True, f"QA passed (score: {qa_score or 'N/A'})"
    except Exception as e:
        return True, f"QA check error (publishing anyway): {e}"


def stage_content_files(skip_qa: bool = False) -> tuple[bool, list[str]]:
    """
    Stage new/modified content files for commit.
    Validates QA scores before staging unless skip_qa is True.
    Returns success status and list of staged files.
    """
    staged = []
    blocked = []

    # Stage markdown files with QA validation
    if CONTENT_PATH.exists():
        for md_file in CONTENT_PATH.glob("*.md"):
            if not skip_qa:
                passed, reason = check_article_qa(md_file)
                if not passed:
                    blocked.append(f"{md_file.name}: {reason}")
                    print(f"   ⛔ Blocked: {md_file.name} - {reason}")
                    continue

            success, _ = run_git_command(["add", str(md_file)])
        if blocked:
            print(f"\n   ⚠️  {len(blocked)} article(s) blocked by QA validation")
        staged.append("content/posts/*.md")

    # Stage images
    if IMAGES_PATH.exists():
        success, _ = run_git_command(["add", str(IMAGES_PATH)])
        if success:
            staged.append("public/images/articles/*")

    return len(staged) > 0, staged


def create_commit_message(articles: list[str], auto: bool = False) -> str:
    """
    Generate a descriptive commit message.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    if len(articles) == 1:
        # Extract article name from path
        article_name = Path(articles[0]).stem.replace("-", " ").title()
        prefix = "🤖 Auto-publish" if auto else "📝 Add"
        return f"{prefix}: {article_name}"
    elif len(articles) > 1:
        prefix = "🤖 Auto-publish" if auto else "📝 Add"
        return f"{prefix}: {len(articles)} new articles ({timestamp})"
    else:
        return f"📝 Content update ({timestamp})"


def commit_changes(message: Optional[str] = None, auto: bool = False) -> tuple[bool, str]:
    """
    Commit staged changes with a message.
    """
    status = check_git_status()
    
    if not message:
        message = create_commit_message(status["new_articles"], auto=auto)
    
    success, output = run_git_command(["commit", "-m", message])
    return success, output


def push_to_remote(branch: str = "main", force: bool = False) -> tuple[bool, str]:
    """
    Push commits to remote repository.
    """
    args = ["push", "origin", branch]
    if force:
        args.insert(1, "--force")
    
    success, output = run_git_command(args)
    return success, output


def pull_latest(branch: str = "main") -> tuple[bool, str]:
    """
    Pull latest changes from remote before publishing.
    """
    success, output = run_git_command(["pull", "origin", branch, "--rebase"])
    return success, output


def auto_publish(
    commit_message: Optional[str] = None,
    branch: str = "main",
    dry_run: bool = False,
    skip_qa: bool = False
) -> bool:
    """
    Full auto-publish workflow:
    1. Check for changes
    2. Pull latest
    3. Stage files
    4. Commit
    5. Push
    
    Args:
        commit_message: Optional custom commit message
        branch: Branch to push to (default: main)
        dry_run: If True, show what would happen without actually doing it
    
    Returns:
        True if successful, False otherwise
    """
    _log("🚀 Starting auto-publish workflow...")

    # Check current status
    status = check_git_status()
    _log(f"📍 Current branch: {status['branch']}")

    if status["clean"]:
        _log("✅ No changes to publish")
        return True

    _log(f"📄 New articles: {len(status['new_articles'])}")
    _log(f"🖼️  New images: {len(status['new_images'])}")
    _log(f"✏️  Modified: {len(status['modified'])}")

    if dry_run:
        _log("\n🔍 DRY RUN - No changes will be made")
        _log(f"Would commit with message: {commit_message or create_commit_message(status['new_articles'], auto=True)}")
        return True

    # Pull latest changes
    _log("\n📥 Pulling latest changes...")
    success, output = pull_latest(branch)
    if not success:
        _log(f"⚠️  Pull failed (continuing anyway): {output}")

    # Stage files (with QA validation)
    _log("\n📦 Staging content files...")
    if skip_qa:
        _log("   ⏭️  QA validation skipped (--skip-qa)")
    success, staged = stage_content_files(skip_qa=skip_qa)
    if not success:
        _log("❌ Failed to stage files")
        return False
    _log(f"   Staged: {', '.join(staged)}")

    # Commit
    _log("\n💾 Creating commit...")
    message = commit_message or create_commit_message(status["new_articles"], auto=True)
    success, output = commit_changes(message, auto=True)
    if not success:
        _log(f"❌ Commit failed: {output}")
        return False
    _log(f"   Message: {message}")

    # Push
    _log("\n📤 Pushing to remote...")
    success, output = push_to_remote(branch)
    if not success:
        _log(f"❌ Push failed: {output}")
        return False

    _log("\n✅ Auto-publish complete!")
    _log("🔄 Vercel will auto-deploy from main branch")
    
    return True


def setup_git_for_ci():
    """
    Configure git for CI environment (GitHub Actions).
    """
    # Set git user for commits
    run_git_command(["config", "user.email", "bot@lawncare.center"])
    run_git_command(["config", "user.name", "Lawn Care Bot"])
    
    print("✅ Git configured for CI environment")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-publish content to GitHub")
    parser.add_argument("--message", "-m", type=str, help="Custom commit message")
    parser.add_argument("--branch", "-b", type=str, default="main", help="Branch to push to")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without doing it")
    parser.add_argument("--skip-qa", action="store_true", help="Skip QA validation checks")
    parser.add_argument("--status", action="store_true", help="Just show current git status")
    parser.add_argument("--setup-ci", action="store_true", help="Configure git for CI environment")
    
    args = parser.parse_args()
    
    if args.setup_ci:
        setup_git_for_ci()
    elif args.status:
        status = check_git_status()
        print(f"Branch: {status['branch']}")
        print(f"Clean: {status['clean']}")
        print(f"New articles: {status['new_articles']}")
        print(f"New images: {status['new_images']}")
        print(f"Modified: {status['modified']}")
    else:
        success = auto_publish(
            commit_message=args.message,
            branch=args.branch,
            dry_run=args.dry_run,
            skip_qa=args.skip_qa
        )
        sys.exit(0 if success else 1)
