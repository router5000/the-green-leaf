#!/usr/bin/env python3
"""
Auto-Publish Module for The Green Leaf Cannabis Content Engine

Handles automatic Git operations after content generation:
- Promotes articles from drafts/ to site/content/posts/
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
DRAFTS_PATH = REPO_ROOT / "drafts"
STATES_CONTENT_PATH = SITE_PATH / "content" / "states"
IMAGES_PATH = SITE_PATH / "public" / "images" / "articles"
STATES_IMAGES_PATH = SITE_PATH / "public" / "images" / "states"
LOG_DIR = REPO_ROOT / "logs"
GIT_TIMEOUT = 300  # seconds — large repos with images need extra time

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


def clean_git_locks() -> None:
    """Remove stale lock files left by crashed git processes."""
    lock_files = [
        REPO_ROOT / ".git" / "index.lock",
        REPO_ROOT / ".git" / "HEAD.lock",
        REPO_ROOT / ".git" / "refs" / "heads" / "main.lock",
    ]
    for lock in lock_files:
        if lock.exists():
            lock.unlink()
            _log(f"   Removed stale lock: {lock.name}")


def run_git_command(args: list[str], cwd: Optional[Path] = None, timeout: Optional[int] = None) -> tuple[bool, str]:
    """
    Run a git command and return success status and output.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=timeout or GIT_TIMEOUT
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout or GIT_TIMEOUT}s"
    except Exception as e:
        return False, str(e)


def promote_draft(slug: str) -> bool:
    """
    Move an article from drafts/ to site/content/posts/ for publishing.
    Returns True if the file was promoted (or already exists in posts).
    """
    draft = DRAFTS_PATH / f"{slug}.md"
    target = CONTENT_PATH / f"{slug}.md"

    if target.exists():
        _log(f"   Article already in posts: {slug}.md")
        return True

    if not draft.exists():
        _log(f"   Draft not found: {draft}")
        return False

    import shutil
    CONTENT_PATH.mkdir(parents=True, exist_ok=True)
    shutil.move(str(draft), target)
    _log(f"   Promoted draft to posts: {slug}.md")
    return True


def promote_all_drafts(skip_qa: bool = False) -> list[str]:
    """
    Scan drafts/ and move all QA-passing articles to site/content/posts/.
    Returns a list of promoted slugs.
    """
    if not DRAFTS_PATH.exists():
        _log("   No drafts/ directory found — skipping promotion")
        return []

    draft_files = list(DRAFTS_PATH.glob("*.md"))
    if not draft_files:
        _log("   No drafts found to promote")
        return []

    _log(f"   Found {len(draft_files)} draft(s) to evaluate")
    CONTENT_PATH.mkdir(parents=True, exist_ok=True)

    import shutil
    promoted = []
    blocked = []

    for draft in draft_files:
        slug = draft.stem
        target = CONTENT_PATH / draft.name

        if target.exists():
            _log(f"   Skipping {draft.name} — already in posts/")
            continue

        if not skip_qa:
            passed, reason = check_article_qa(draft)
            if not passed:
                blocked.append(f"{draft.name}: {reason}")
                _log(f"   ⛔ Blocked {draft.name}: {reason}")
                continue
            _log(f"   ✅ QA passed {draft.name}: {reason}")

        shutil.move(str(draft), target)
        _log(f"   Promoted: {draft.name} → site/content/posts/")
        promoted.append(slug)

    if blocked:
        _log(f"\n   ⚠️  {len(blocked)} draft(s) blocked by QA:")
        for b in blocked:
            _log(f"      {b}")

    return promoted


def check_git_status() -> dict:
    """
    Check current git status and return info about changes.
    """
    status = {
        "clean": True,
        "new_articles": [],
        "new_state_articles": [],
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

        elif "content/states/" in filepath and filepath.endswith(".md"):
            if status_code.startswith("?") or status_code.startswith("A"):
                status["new_state_articles"].append(filepath)
            elif status_code.startswith("M"):
                status["modified"].append(filepath)

        elif "images/articles/" in filepath or "images/states/" in filepath:
            if status_code.startswith("?") or status_code.startswith("A"):
                status["new_images"].append(filepath)

    status["clean"] = not (status["new_articles"] or status["new_state_articles"] or status["new_images"] or status["modified"])

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
        return False, f"QA check error (blocking publish): {e}"


def stage_content_files(skip_qa: bool = False) -> tuple[bool, list[str]]:
    """
    Stage new/modified content files for commit.
    Validates QA scores before staging unless skip_qa is True.
    Returns success status and list of staged files.
    """
    staged = []
    blocked = []

    # Stage general markdown files with QA validation
    if CONTENT_PATH.exists():
        for md_file in CONTENT_PATH.glob("*.md"):
            if not skip_qa:
                passed, reason = check_article_qa(md_file)
                if not passed:
                    blocked.append(f"{md_file.name}: {reason}")
                    print(f"   ⛔ Blocked: {md_file.name} - {reason}")
                    continue

            success, _ = run_git_command(["add", str(md_file)])
            if success:
                staged.append(str(md_file))

    # Stage state markdown files with QA validation
    if STATES_CONTENT_PATH.exists():
        for state_dir in STATES_CONTENT_PATH.iterdir():
            if state_dir.is_dir():
                for md_file in state_dir.glob("*.md"):
                    if not skip_qa:
                        passed, reason = check_article_qa(md_file)
                        if not passed:
                            blocked.append(f"{state_dir.name}/{md_file.name}: {reason}")
                            print(f"   ⛔ Blocked: {state_dir.name}/{md_file.name} - {reason}")
                            continue

                    success, _ = run_git_command(["add", str(md_file)])
                    if success:
                        staged.append(str(md_file))

    if blocked:
        print(f"\n   ⚠️  {len(blocked)} article(s) blocked by QA validation")

    # Stage article images
    if IMAGES_PATH.exists():
        success, _ = run_git_command(["add", str(IMAGES_PATH)])
        if success:
            staged.append("public/images/articles/*")

    # Stage state images
    if STATES_IMAGES_PATH.exists():
        success, _ = run_git_command(["add", str(STATES_IMAGES_PATH)])
        if success:
            staged.append("public/images/states/*")

    return len(staged) > 0, staged


def create_commit_message(articles: list[str], state_articles: Optional[list[str]] = None, auto: bool = False) -> str:
    """
    Generate a descriptive commit message.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    state_articles = state_articles or []
    total = len(articles) + len(state_articles)
    prefix = "🤖 Auto-publish" if auto else "📝 Add"

    if total == 0:
        return f"📝 Content update ({timestamp})"
    elif total == 1:
        path = articles[0] if articles else state_articles[0]
        article_name = Path(path).stem.replace("-", " ").title()
        return f"{prefix}: {article_name}"
    elif state_articles and not articles:
        return f"{prefix}: {len(state_articles)} new state articles ({timestamp})"
    elif articles and not state_articles:
        return f"{prefix}: {len(articles)} new articles ({timestamp})"
    else:
        return f"{prefix}: {len(articles)} articles + {len(state_articles)} state articles ({timestamp})"


def commit_changes(message: Optional[str] = None, auto: bool = False) -> tuple[bool, str]:
    """
    Commit staged changes with a message.
    """
    status = check_git_status()
    
    if not message:
        message = create_commit_message(status["new_articles"], status.get("new_state_articles", []), auto=auto)
    
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
    skip_qa: bool = False,
    slug: Optional[str] = None
) -> bool:
    """
    Full auto-publish workflow:
    1. Optionally promote a draft by slug
    2. Check for changes
    3. Pull latest
    4. Stage files
    5. Commit
    6. Push

    Args:
        commit_message: Optional custom commit message
        branch: Branch to push to (default: main)
        dry_run: If True, show what would happen without actually doing it
        skip_qa: If True, skip QA validation checks
        slug: If provided, promote this draft to posts before publishing

    Returns:
        True if successful, False otherwise
    """
    _log("🚀 Starting auto-publish workflow...")

    # Clean stale lock files from any previously crashed git processes
    clean_git_locks()

    # Promote drafts to site/content/posts/
    if slug:
        # Promote a single named draft
        _log(f"\n📄 Promoting draft: {slug}")
        if not promote_draft(slug):
            _log("❌ Draft promotion failed")
            return False
    else:
        # Promote all QA-passing drafts
        _log("\n📄 Promoting all ready drafts...")
        promoted = promote_all_drafts(skip_qa=skip_qa)
        if promoted:
            _log(f"   Promoted {len(promoted)} draft(s): {', '.join(promoted)}")
        else:
            _log("   No drafts promoted")

    # Check current status
    status = check_git_status()
    _log(f"📍 Current branch: {status['branch']}")

    if status["clean"]:
        _log("✅ No changes to publish")
        return True

    _log(f"📄 New articles: {len(status['new_articles'])}")
    _log(f"🗺️  New state articles: {len(status['new_state_articles'])}")
    _log(f"🖼️  New images: {len(status['new_images'])}")
    _log(f"✏️  Modified: {len(status['modified'])}")

    if dry_run:
        _log("\n🔍 DRY RUN - No changes will be made")
        _log(f"Would commit with message: {commit_message or create_commit_message(status['new_articles'], status.get('new_state_articles', []), auto=True)}")
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
    message = commit_message or create_commit_message(status["new_articles"], status.get("new_state_articles", []), auto=True)
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
    run_git_command(["config", "user.email", "bot@thegreenleaf.com"])
    run_git_command(["config", "user.name", "Green Leaf Bot"])
    
    print("✅ Git configured for CI environment")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auto-publish content to GitHub")
    parser.add_argument("--message", "-m", type=str, help="Custom commit message")
    parser.add_argument("--branch", "-b", type=str, default="main", help="Branch to push to")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without doing it")
    parser.add_argument("--skip-qa", action="store_true", help="Skip QA validation checks")
    parser.add_argument("--slug", type=str, help="Promote a specific draft by slug before publishing")
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
        print(f"New state articles: {status['new_state_articles']}")
        print(f"New images: {status['new_images']}")
        print(f"Modified: {status['modified']}")
    else:
        success = auto_publish(
            commit_message=args.message,
            branch=args.branch,
            dry_run=args.dry_run,
            skip_qa=args.skip_qa,
            slug=args.slug
        )
        sys.exit(0 if success else 1)
