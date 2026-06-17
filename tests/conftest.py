from __future__ import annotations

from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

from config.settings import Settings, get_settings
from core.app_modals import AppModals
from core.screenshot_capture import capture_failure_screenshot, create_run_directory
from data.property_factory import PropertyData, build_property, build_required_property
from pages.auth.login_page import LoginPage
from pages.property_manager.create_property_page import CreatePropertyPage
from pages.property_manager.properties_list_page import PropertiesListPage
from tests.fixtures.files.generate_fixtures import ensure_fixtures

ROOT_DIR = Path(__file__).resolve().parent.parent
AUTH_DIR = ROOT_DIR / ".auth"
SCREENSHOTS_DIR = ROOT_DIR / "screenshots"


def pytest_configure(config: pytest.Config) -> None:
    config.screenshot_run_dir = create_run_directory(SCREENSHOTS_DIR)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    run_dir = getattr(session.config, "screenshot_run_dir", None)
    if run_dir and run_dir.exists():
        from datetime import datetime

        with (run_dir / "run_info.txt").open("a", encoding="utf-8") as handle:
            handle.write(f"Test run finished: {datetime.now().isoformat()}\n")
            handle.write(f"Exit status: {exitstatus}\n")


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def settings() -> Settings:
    return get_settings()


# ---------------------------------------------------------------------------
# Browser configuration (pytest-playwright hooks)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def browser_type_launch_args(settings: Settings) -> dict:
    return {
        "headless": settings.headless,
        "slow_mo": settings.slow_mo_ms,
    }


@pytest.fixture(scope="session")
def browser_context_args(settings: Settings) -> dict:
    return {
        "base_url": settings.base_url,
        "viewport": {"width": 1440, "height": 900},
        "ignore_https_errors": True,
    }


# ---------------------------------------------------------------------------
# Page fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def login_page(page: Page, settings: Settings) -> LoginPage:
    return LoginPage(page, settings)


@pytest.fixture
def property_data() -> PropertyData:
    return build_property()


@pytest.fixture
def required_property_data() -> PropertyData:
    return build_required_property()


@pytest.fixture(scope="session")
def upload_test_files() -> dict[str, Path]:
    return ensure_fixtures()


@pytest.fixture
def create_property_modal(
    pm_properties_list_page: PropertiesListPage,
) -> CreatePropertyPage:
    return pm_properties_list_page.start_create_property()


@pytest.fixture
def pm_properties_list_page(
    authenticated_pm_page: Page,
    settings: Settings,
) -> PropertiesListPage:
    properties_page = PropertiesListPage(authenticated_pm_page, settings)
    properties_page.open()
    return properties_page


@pytest.fixture
def existing_property_names(
    pm_properties_list_page: PropertiesListPage,
) -> list[str]:
    """Names of properties currently on the list (skips if none exist)."""
    names = pm_properties_list_page.get_property_names()
    if not names:
        pytest.skip("No properties on list page — seed data required for this test.")
    return names


@pytest.fixture
def first_property_name(existing_property_names: list[str]) -> str:
    return existing_property_names[0]


# ---------------------------------------------------------------------------
# Authenticated session fixtures (reusable across tests)
# ---------------------------------------------------------------------------


def _require_credentials(email: str, password: str, role: str) -> None:
    if not email or not password:
        pytest.skip(
            f"{role} credentials not configured. "
            f"Set credentials in .env (see .env.example)."
        )


@pytest.fixture
def authenticated_pm_context(
    browser: Browser,
    settings: Settings,
) -> Generator[BrowserContext, None, None]:
    """Browser context with a logged-in Property Manager session."""
    _require_credentials(settings.pm_email, settings.pm_password, "PM")

    AUTH_DIR.mkdir(exist_ok=True)
    storage_path = AUTH_DIR / "pm.json"

    context = browser.new_context(
        base_url=settings.base_url,
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True,
        storage_state=storage_path if storage_path.exists() else None,
    )
    page = context.new_page()

    if not storage_path.exists():
        login = LoginPage(page, settings)
        login.open()
        login.login(settings.pm_email, settings.pm_password)
        login.expect_redirect_to_dashboard(role="property-manager")
        AppModals(page, timeout_ms=settings.default_timeout_ms).dismiss_all()
        context.storage_state(path=storage_path)

    yield context
    context.close()


@pytest.fixture
def authenticated_pm_page(authenticated_pm_context: BrowserContext) -> Page:
    page = authenticated_pm_context.new_page()
    yield page
    page.close()


@pytest.fixture
def authenticated_vendor_context(
    browser: Browser,
    settings: Settings,
) -> Generator[BrowserContext, None, None]:
    """Browser context with a logged-in Vendor session."""
    _require_credentials(settings.vendor_email, settings.vendor_password, "Vendor")

    AUTH_DIR.mkdir(exist_ok=True)
    storage_path = AUTH_DIR / "vendor.json"

    context = browser.new_context(
        base_url=settings.base_url,
        viewport={"width": 1440, "height": 900},
        ignore_https_errors=True,
        storage_state=storage_path if storage_path.exists() else None,
    )
    page = context.new_page()

    if not storage_path.exists():
        login = LoginPage(page, settings)
        login.open()
        login.login(settings.vendor_email, settings.vendor_password)
        login.expect_redirect_to_dashboard(role="vendor")
        context.storage_state(path=storage_path)

    yield context
    context.close()


@pytest.fixture
def authenticated_vendor_page(authenticated_vendor_context: BrowserContext) -> Page:
    page = authenticated_vendor_context.new_page()
    yield page
    page.close()


# ---------------------------------------------------------------------------
# Failure artifacts
# ---------------------------------------------------------------------------


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call" or report.passed:
        return

    page: Page | None = None
    for fixture_name in ("page", "authenticated_pm_page", "authenticated_vendor_page"):
        candidate = item.funcargs.get(fixture_name)
        if candidate is not None and not candidate.is_closed():
            page = candidate
            break

    if page is None:
        return

    run_dir = getattr(item.config, "screenshot_run_dir", SCREENSHOTS_DIR)
    capture_failure_screenshot(page, run_dir, item.nodeid)
