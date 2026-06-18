# Continuous Integration

GitHub Actions runs Playwright + Pytest against `dev.bidbuddy.com` (or a custom base URL).

## Workflows

| Workflow | Trigger | What runs |
|----------|---------|-----------|
| **CI (Smoke)** | Push / PR to `main` | `pytest -m smoke` (~5 min) |
| **Regression** | Manual / Mondays 06:00 UTC | `pytest -m regression` (~1–2 hrs) |

### Manual regression with a custom scope

Actions → **Regression** → **Run workflow** → set **test path**, e.g.:

- `-m regression` — full suite (default)
- `tests/regression/test_properties_list.py` — one file
- `-m properties_list` — by marker

## Required GitHub configuration

### Secrets (Settings → Secrets and variables → Actions → Secrets)

| Secret | Required | Description |
|--------|----------|-------------|
| `PM_EMAIL` | Yes | Property Manager test account email |
| `PM_PASSWORD` | Yes | Property Manager test account password |
| `VENDOR_EMAIL` | No | Vendor account (vendor smoke tests skip if unset) |
| `VENDOR_PASSWORD` | No | Vendor account password |

Secrets are injected as environment variables at runtime and are **masked in logs**.

### Variables (optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `https://dev.bidbuddy.com` | Target environment URL |

## Local setup (same variables)

```bash
cp .env.example .env
# Edit .env with real credentials — never commit .env
pip install -r requirements.txt
playwright install chromium
pytest -m smoke -v
```

## Failure artifacts

When a job fails, screenshots from `screenshots/<run-timestamp>/` are uploaded as a workflow artifact (retained 7–14 days).

## Security notes

- `.env` and `.auth/` are gitignored; only `.env.example` with placeholders is committed.
- Rotate any credentials that were ever committed to the repository history.
- Do not print `PM_PASSWORD` or `VENDOR_PASSWORD` in workflow steps — GitHub masks secret values automatically.
