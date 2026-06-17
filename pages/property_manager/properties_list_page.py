import re

from playwright.sync_api import Locator, Page, expect

from config.settings import Settings
from core.base_page import BasePage
from data.property_factory import PROPERTY_TYPES
from pages.property_manager.create_property_page import CreatePropertyPage
from pages.property_manager.property_detail_page import PropertyDetailPage


class PropertiesListPage(BasePage):
    """Page object for the PM properties list (/property-manager/properties)."""

    PATH = "/property-manager/properties"
    PAGE_TITLE = "Properties"
    PAGE_SUBTITLE = re.compile(r"Manage and monitor your properties", re.I)
    EMPTY_STATE_TEXT = re.compile(r"no propert", re.IGNORECASE)
    SEARCH_PLACEHOLDER = re.compile(r"Search properties", re.I)
    ADD_PROPERTY_TEXT = re.compile(r"^Add Property$", re.I)
    TYPE_TAG_PATTERN = re.compile(
        r"|".join(re.escape(t) for t in PROPERTY_TYPES),
        re.I,
    )
    RFP_STATUS_PATTERN = re.compile(r"(\d+\s*RFP|No active RFPs)", re.I)
    NO_PHOTOS_PATTERN = re.compile(r"no photos", re.I)

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        super().__init__(page, settings)

    @property
    def main(self) -> Locator:
        return self.page.get_by_role("main")

    @property
    def search_field(self) -> Locator:
        return self.main.get_by_role("textbox", name=self.SEARCH_PLACEHOLDER)

    @property
    def type_filter(self) -> Locator:
        return self._toolbar_comboboxes().nth(0)

    @property
    def sort_by_filter(self) -> Locator:
        return self._toolbar_comboboxes().nth(1)

    @property
    def density_filter(self) -> Locator:
        return self._toolbar_comboboxes().nth(2)

    def _toolbar_comboboxes(self) -> Locator:
        return self.main.get_by_role("combobox")

    def property_card_headings(self) -> Locator:
        return self.main.get_by_role("heading", level=6).filter(
            has_not_text=self.ADD_PROPERTY_TEXT
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def open(self) -> "PropertiesListPage":
        self.navigate(self.PATH)
        self.dismiss_app_modals()
        self.expect_loaded()
        return self

    def _sidebar_properties_link(self) -> Locator:
        return self.page.locator('a[href="/property-manager/properties"]').first

    def open_via_sidebar(self) -> "PropertiesListPage":
        self._sidebar_properties_link().click()
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

    def _create_property_button(self) -> Locator:
        return self.main.get_by_role("button", name=re.compile(r"new property", re.I))

    def start_create_property(self) -> CreatePropertyPage:
        self._create_property_button().click()
        create_page = CreatePropertyPage(self.page, self.settings)
        create_page.expect_loaded()
        return create_page

    def start_create_from_add_card(self) -> CreatePropertyPage:
        self.main.get_by_text(self.ADD_PROPERTY_TEXT).click()
        create_page = CreatePropertyPage(self.page, self.settings)
        create_page.expect_loaded()
        return create_page

    def open_property(self, name: str) -> PropertyDetailPage:
        card_link = self.main.locator('a[href*="/property-manager/properties/"]').filter(
            has=self.main.get_by_role("heading", name=name, level=6)
        )
        if card_link.count() > 0:
            card_link.first.click()
        else:
            self.main.get_by_role("heading", name=name, level=6).click()
        detail = PropertyDetailPage(self.page, self.settings)
        detail.expect_loaded()
        return detail

    # ------------------------------------------------------------------
    # Toolbar interactions
    # ------------------------------------------------------------------

    def search(self, query: str) -> "PropertiesListPage":
        self.search_field.click()
        self.search_field.fill(query)
        return self

    def clear_search(self) -> "PropertiesListPage":
        self.search_field.click()
        self.search_field.fill("")
        return self

    def _select_listbox_option(self, option_name: str | re.Pattern[str]) -> None:
        listbox = self.page.get_by_role("listbox").last
        expect(listbox).to_be_visible(timeout=self.assertion_timeout)
        if isinstance(option_name, re.Pattern):
            option = listbox.get_by_role("option", name=option_name)
        else:
            option = listbox.get_by_role("option", disabled=False).filter(
                has_text=re.compile(rf"^{re.escape(option_name)}$", re.I)
            )
        expect(option.first).to_be_visible(timeout=self.assertion_timeout)
        option.first.click()

    def select_type_filter(self, option: str) -> "PropertiesListPage":
        self.type_filter.click()
        self._select_listbox_option(option)
        return self

    def select_sort_by(self, option: str) -> "PropertiesListPage":
        self.sort_by_filter.click()
        self._select_listbox_option(option)
        return self

    def select_density(self, option: str) -> "PropertiesListPage":
        self.density_filter.click()
        self._select_listbox_option(option)
        return self

    def get_type_filter_options(self) -> list[str]:
        self.type_filter.click()
        options = self._read_visible_listbox_options()
        self.page.keyboard.press("Escape")
        return options

    def get_sort_by_options(self) -> list[str]:
        self.sort_by_filter.click()
        options = self._read_visible_listbox_options()
        self.page.keyboard.press("Escape")
        return options

    def get_density_options(self) -> list[str]:
        self.density_filter.click()
        options = self._read_visible_listbox_options()
        self.page.keyboard.press("Escape")
        return options

    def _read_visible_listbox_options(self) -> list[str]:
        listbox = self.page.get_by_role("listbox").last
        expect(listbox).to_be_visible(timeout=self.assertion_timeout)
        options = listbox.get_by_role("option", disabled=False)
        return [options.nth(i).inner_text().strip() for i in range(options.count())]

    def select_grid_view(self) -> "PropertiesListPage":
        self.main.get_by_role("button", name=re.compile(r"grid", re.I)).click()
        return self

    def select_list_view(self) -> "PropertiesListPage":
        self.main.get_by_role("button", name=re.compile(r"list", re.I)).click()
        return self

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def get_property_names(self) -> list[str]:
        headings = self.property_card_headings()
        return [
            headings.nth(i).inner_text().strip()
            for i in range(headings.count())
            if headings.nth(i).inner_text().strip()
        ]

    def property_card_count(self) -> int:
        return self.property_card_headings().count()

    def _card_for_name(self, name: str) -> Locator:
        heading = self.main.get_by_role("heading", name=name, level=6)
        link = self.main.locator('a[href*="/property-manager/properties/"]').filter(
            has=heading
        )
        if link.count() > 0:
            return link.first
        return heading.locator(
            "xpath=ancestor::*[contains(@class,'MuiCard-root')][1]"
        )

    def get_card_type_tag(self, name: str) -> str | None:
        card = self._card_for_name(name)
        text = card.inner_text()
        match = self.TYPE_TAG_PATTERN.search(text)
        return match.group(0) if match else None

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------

    def expect_page_header(self) -> None:
        expect(self.main.get_by_role("heading", name=self.PAGE_TITLE)).to_be_visible(
            timeout=self.assertion_timeout
        )
        expect(self.main.get_by_text(self.PAGE_SUBTITLE)).to_be_visible(
            timeout=self.assertion_timeout
        )

    def expect_properties_navigation_active(self) -> None:
        """Sidebar Properties link is visible (no breadcrumb trail on this build)."""
        expect(self._sidebar_properties_link()).to_be_visible(
            timeout=self.assertion_timeout
        )

    def expect_property_visible(self, name: str) -> None:
        expect(
            self.main.get_by_role("heading", name=name, level=6, exact=True)
        ).to_be_visible(timeout=self.assertion_timeout)

    def expect_property_hidden(self, name: str) -> None:
        expect(
            self.main.get_by_role("heading", name=name, level=6, exact=True)
        ).to_be_hidden(timeout=self.assertion_timeout)

    def expect_only_property_visible(self, name: str) -> None:
        expect(self.property_card_headings()).to_have_count(1)
        self.expect_property_visible(name)

    def expect_empty_state_or_cards(self) -> None:
        expect(self.main.get_by_role("heading", name=self.PAGE_TITLE)).to_be_visible(
            timeout=self.assertion_timeout
        )
        expect(
            self.property_card_headings().first.or_(
                self.main.get_by_text(self.EMPTY_STATE_TEXT)
            )
        ).to_be_visible(timeout=self.assertion_timeout)

    def expect_no_search_results(self) -> None:
        """No property cards remain; app hides non-matches without a message."""
        expect(self.property_card_headings()).to_have_count(0)
        self.expect_add_property_card_visible()

    def expect_search_field_empty(self) -> None:
        expect(self.search_field).to_have_value("")

    def expect_type_filter(self, label: str | re.Pattern[str]) -> None:
        expect(self.type_filter).to_contain_text(label, timeout=self.assertion_timeout)

    def expect_sort_by(self, label: str) -> None:
        expect(self.sort_by_filter).to_contain_text(
            label, timeout=self.assertion_timeout
        )

    def expect_density(self, label: str) -> None:
        expect(self.density_filter).to_contain_text(
            label, timeout=self.assertion_timeout
        )

    def expect_all_type_filter_matches_card_count(self) -> None:
        count = self.property_card_count()
        expect(self.type_filter).to_contain_text(
            re.compile(rf"All\s*\(\s*{count}\s*\)", re.I),
            timeout=self.assertion_timeout,
        )

    def expect_card_structure(self, name: str) -> None:
        card = self._card_for_name(name)
        expect(card).to_be_visible(timeout=self.assertion_timeout)
        expect(card.get_by_role("heading", name=name, level=6, exact=True)).to_be_visible()
        expect(card.locator("img").first).to_be_visible()
        expect(card.get_by_text(self.TYPE_TAG_PATTERN)).to_be_visible()
        expect(card.get_by_text(self.RFP_STATUS_PATTERN)).to_be_visible()
        # Card body includes address and metadata beyond the title alone.
        assert len(card.inner_text()) > len(name) + 10

    def expect_card_has_photo_or_placeholder(self, name: str) -> None:
        card = self._card_for_name(name)
        expect(
            card.locator("img").first.or_(card.get_by_text(self.NO_PHOTOS_PATTERN))
        ).to_be_visible(timeout=self.assertion_timeout)

    def expect_add_property_card_visible(self) -> None:
        expect(self.main.get_by_text(self.ADD_PROPERTY_TEXT)).to_be_visible(
            timeout=self.assertion_timeout
        )
