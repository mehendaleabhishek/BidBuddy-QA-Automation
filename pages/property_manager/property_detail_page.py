import re

from playwright.sync_api import Page, expect

from config.settings import Settings
from core.base_page import BasePage


class PropertyDetailPage(BasePage):
    """Page object for a single property detail view."""

    PATH_PATTERN = re.compile(r".*/property-manager/properties/[^/]+")

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        super().__init__(page, settings)

    def expect_loaded(self) -> None:
        expect(self.page).to_have_url(self.PATH_PATTERN, timeout=self.assertion_timeout)

    def expect_property_name(self, name: str) -> None:
        expect(
            self.page.get_by_role("heading", name=name).or_(
                self.page.get_by_text(name, exact=True)
            )
        ).to_be_visible(timeout=self.assertion_timeout)

    def expect_notes(self, notes: str) -> None:
        expect(self.page.get_by_text(notes)).to_be_visible(timeout=self.assertion_timeout)
