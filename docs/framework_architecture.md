# BidBuddy UI Automation Framework — Architecture

## Overview

Playwright + Python + Pytest framework using the **Page Object Model (POM)**. Designed for two distinct user roles (Property Manager and Vendor), multi-step wizards, and long-running regression suites.

```
┌─────────────────────────────────────────────────────────────┐
│                        Test Layer                           │
│  tests/smoke/  tests/regression/  tests/e2e/                │
│  (pytest markers: smoke, regression, property_manager, ...) │
└──────────────────────────┬──────────────────────────────────┘
                           │ uses fixtures
┌──────────────────────────▼──────────────────────────────────┐
│                     Fixture Layer                           │
│  tests/conftest.py — browser, page, auth sessions, artifacts│
└──────────────────────────┬──────────────────────────────────┘
                           │ instantiates
┌──────────────────────────▼──────────────────────────────────┐
│                   Page Object Layer                         │
│  pages/auth/login_page.py  pages/pm/...  pages/vendor/...   │
└──────────────────────────┬──────────────────────────────────┘
                           │ extends
┌──────────────────────────▼──────────────────────────────────┐
│                     Core Layer                              │
│  core/base_page.py — waits, locators, navigation, asserts   │
└──────────────────────────┬──────────────────────────────────┘
                           │ reads
┌──────────────────────────▼──────────────────────────────────┐
│                    Config Layer                             │
│  config/settings.py — env vars, URLs, timeouts, credentials │
└─────────────────────────────────────────────────────────────┘
```

## Folder Structure

```
BidBuddy_automation/
├── config/                  # Environment & app settings
│   ├── __init__.py
│   └── settings.py
├── core/                    # Framework primitives
│   ├── __init__.py
│   └── base_page.py
├── pages/                   # Page Object Model
│   ├── auth/
│   │   └── login_page.py
│   ├── property_manager/    # (future) PM-specific pages
│   └── vendor/              # (future) Vendor-specific pages
├── tests/
│   ├── conftest.py          # Shared fixtures
│   ├── smoke/               # Fast critical-path tests
│   ├── regression/          # Full flow coverage (future)
│   └── e2e/                 # Cross-role end-to-end (future)
├── docs/                    # Product & framework docs
├── .auth/                   # Cached login sessions (gitignored)
├── screenshots/             # Failure screenshots (gitignored)
├── .env.example
├── pytest.ini
└── requirements.txt
```

## Design Principles

### 1. Page Object Model

- **Pages** expose user-facing actions (`login()`, `create_property()`), not raw selectors in tests.
- **Locators** live in one place per page; update once when UI changes.
- **Tests** read like scenarios: arrange → act → assert.

### 2. Selector Strategy

Priority order (most stable first):

1. `data-testid` — add to app components where possible
2. `role` + accessible name — semantic, resilient
3. `name` attribute on form fields
4. CSS class / text — last resort

### 3. Wait Strategy (anti-flakiness)

| Do | Don't |
|----|-------|
| `expect(locator).to_be_visible()` | `time.sleep()` |
| `page.wait_for_url()` | Fixed hard waits |
| `locator.wait_for(state="visible")` before click | Click immediately after navigation |
| Playwright auto-wait on actions | Polling loops |

`BasePage` wraps Playwright's built-in retry assertions so every check auto-waits until timeout.

### 4. Fixture Layers

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `settings` | session | Centralized config |
| `page` | function | Fresh page per test (from pytest-playwright) |
| `login_page` | function | Ready-to-use LoginPage instance |
| `authenticated_pm_page` | function | Pre-logged PM session (storage state cache) |
| `authenticated_vendor_page` | function | Pre-logged Vendor session |

Auth fixtures cache `storage_state` in `.auth/` so login runs once per role per session.

### 5. Test Organization

| Directory | Marker | When to use |
|-----------|--------|-------------|
| `tests/smoke/` | `@pytest.mark.smoke` | Login, nav, critical paths (< 5 min) |
| `tests/regression/` | `@pytest.mark.regression` | Feature-level coverage |
| `tests/e2e/` | both role markers | PM ↔ Vendor cross-role flows |

### 6. Failure Diagnostics

- Screenshots captured automatically on test failure (`conftest.py` hook)
- Playwright trace/video can be enabled per-run via CLI flags

## Scaling Roadmap

1. **Phase 1 (current)** — Auth smoke tests, base framework
2. **Phase 2** — PM pages: Properties, RFP wizard, RFP Manager
3. **Phase 3** — Vendor pages: invitations, bid submission
4. **Phase 4** — Cross-role E2E (PM creates RFP → Vendor bids → PM awards)
5. **Phase 5** — CI integration (GitHub Actions), parallel shards, reporting

## Running Tests

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # fill in credentials

# Smoke suite
pytest -m smoke

# PM login only
pytest -m "smoke and property_manager"

# Headed debug run
HEADLESS=false pytest tests/smoke/test_login.py -s
```
