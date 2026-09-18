# P1 Dual Deploy / Workflow note

## Confirmed
- `auto_publish.py` pushes commits to `main`, which triggers Vercel git integration.
- Dry-run safety in the weekly pipeline is preserved (`INPUT_DRY_RUN` / `--dry-run`).

## Blocked by PAT scope
Editing `.github/workflows/weekly-content.yml` via the GitHub Contents API returns:

`403 Resource not accessible by personal access token`

The connected GitHub PAT lacks the `workflow` scope required to change workflow files.

## Intended YAML change (apply manually or with a workflow-scoped token)
1. Configure Git: `user.name` → `Strain Report Bot` (keep `bot@strainreport.com`).
2. Remove the entire **Deploy to Vercel** CLI step and its `VERCEL_TOKEN` / org / project secret usage.
3. Leave a short comment that deploy is git-push-only via `auto_publish.py` → main → Vercel.

Bot rename in `auto_publish.py` `setup_git_for_ci()` is already on this branch and covers CI commits when `--ci` runs.
