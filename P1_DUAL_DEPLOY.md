# Dual-deploy cleanup (P1)

**Confirmed:** `auto_publish.py` pushes to `main` and logs that Vercel auto-deploys from main.

**Intended Actions workflow change** (`.github/workflows/weekly-content.yml`):
- Remove the `Deploy to Vercel` CLI step (and its `VERCEL_TOKEN` / `VERCEL_ORG_ID` / `VERCEL_PROJECT_ID` usage in that step).
- Rename Configure Git `user.name` from `Green Leaf Bot` to `Strain Report Bot` (keep `bot@strainreport.com`).
- Keep `dry_run` input and pipeline `--dry-run` safety.

**Blocked in this PR:** GitHub returned `403 Resource not accessible by personal access token` when updating `.github/workflows/*` (PAT lacks `workflow` scope). Bot rename for commits is applied in `auto_publish.setup_git_for_ci()` which the pipeline calls under `--ci`.
