from __future__ import annotations

from typing import Literal, Pattern, Union

from playwright.sync_api import Locator, Page, expect

from config.settings import Settings, get_settings
from core.app_modals import AppModals

Selector = Union[str, Pattern[str]]


class BasePage:
    """Base page object with shared wait helpers and navigation utilities."""

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        self.page = page
        self.settings = settings or get_settings()
        self.page.set_default_timeout(self.settings.default_timeout_ms)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def navigate(self, path: str = "") -> None:
        base = self.settings.base_url.rstrip("/")
        url = f"{base}{path}" if path.startswith("/") else f"{base}/{path}"
        self.page.goto(url, wait_until="domcontentloaded")

    def dismiss_app_modals(self) -> None:
        AppModals(self.page, timeout_ms=5_000).dismiss_all()

    def wait_for_url(
        self,
        url: str | Pattern[str],
        *,
        timeout: int | None = None,
    ) -> None:
        self.page.wait_for_url(url, timeout=timeout)

    # ------------------------------------------------------------------
    # Locator helpers (prefer data-testid > role > text)
    # ------------------------------------------------------------------

    def locator(self, selector: Selector) -> Locator:
        return self.page.locator(selector)

    def get_by_test_id(self, test_id: str) -> Locator:
        return self.page.get_by_test_id(test_id)

    def get_by_role(
        self,
        role: Literal[
            "alert",
            "alertdialog",
            "button",
            "checkbox",
            "combobox",
            "dialog",
            "grid",
            "heading",
            "link",
            "listbox",
            "menuitem",
            "option",
            "radio",
            "tab",
            "textbox",
        ],
        *,
        name: str | Pattern[str] | None = None,
        exact: bool = False,
    ) -> Locator:
        return self.page.get_by_role(role, name=name, exact=exact)

    # ------------------------------------------------------------------
    # Interaction helpers with built-in stability checks
    # ------------------------------------------------------------------

    def fill(self, selector: Selector, value: str) -> None:
        locator = self.locator(selector)
        locator.wait_for(state="visible")
        locator.fill(value)

    def click(self, selector: Selector) -> None:
        locator = self.locator(selector)
        locator.wait_for(state="visible")
        locator.click()

    def click_role(
        self,
        role: Literal["button", "link", "menuitem", "tab"],
        *,
        name: str | Pattern[str],
        exact: bool = False,
    ) -> None:
        locator = self.get_by_role(role, name=name, exact=exact)
        locator.wait_for(state="visible")
        locator.click()

    # ------------------------------------------------------------------
    # Assertion helpers (Playwright auto-retries until timeout)
    # ------------------------------------------------------------------

    @property
    def assertion_timeout(self) -> int:
        return self.settings.default_timeout_ms

    def expect_visible(self, selector: Selector) -> None:
        expect(self.locator(selector)).to_be_visible(timeout=self.assertion_timeout)

    def expect_hidden(self, selector: Selector) -> None:
        expect(self.locator(selector)).to_be_hidden(timeout=self.assertion_timeout)

    def expect_text(self, selector: Selector, text: str | Pattern[str]) -> None:
        expect(self.locator(selector)).to_contain_text(
            text, timeout=self.assertion_timeout
        )

    def expect_url(self, url: str | Pattern[str]) -> None:
        expect(self.page).to_have_url(url, timeout=self.assertion_timeout)
