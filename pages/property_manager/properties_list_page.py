import re

from playwright.sync_api import Page, expect

from config.settings import Settings
from core.base_page import BasePage
from pages.property_manager.create_property_page import CreatePropertyPage


class PropertiesListPage(BasePage):
    """Page object for the PM properties list (/property-manager/properties)."""

    PATH = "/property-manager/properties"
    EMPTY_STATE_TEXT = re.compile(r"no propert", re.IGNORECASE)

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        super().__init__(page, settings)

    @property
    def main(self):
        return self.page.get_by_role("main")

    def open(self) -> "PropertiesListPage":
        self.navigate(self.PATH)
        self.dismiss_app_modals()
        self.expect_loaded()
        return self

    def expect_loaded(self) -> None:
        pattern = re.compile(r".*/property-manager/properties/?(\?.*)?$")
        expect(self.page).to_have_url(pattern, timeout=self.assertion_timeout)
        self.dismiss_app_modals()
        self._expect_create_entry_point_visible()

    def _expect_create_entry_point_visible(self) -> None:
        expect(self._create_property_button()).to_be_visible(
            timeout=self.assertion_timeout
        )

    def _create_property_button(self):
        return self.main.get_by_role("button", name=re.compile(r"new property", re.I))

    def start_create_property(self) -> CreatePropertyPage:
        self._create_property_button().click()
        create_page = CreatePropertyPage(self.page, self.settings)
        create_page.expect_loaded()
        return create_page

    def expect_property_visible(self, name: str) -> None:
        expect(
            self.main.get_by_role("heading", name=name, level=6).or_(
                self.main.get_by_text(name, exact=True)
            )
        ).to_be_visible(timeout=self.assertion_timeout)

    def expect_empty_state_or_cards(self) -> None:
        expect(self.main.get_by_role("heading", name="Properties")).to_be_visible(
            timeout=self.assertion_timeout
        )
        # Use .first so the union resolves to a single element (not all h6 cards).
        expect(
            self.main.get_by_role("heading", level=6).first.or_(
                self.main.get_by_text(self.EMPTY_STATE_TEXT)
            )
        ).to_be_visible(timeout=self.assertion_timeout)
