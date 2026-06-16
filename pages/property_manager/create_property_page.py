import re
from pathlib import Path

from playwright.sync_api import Locator, Page, expect

from config.settings import Settings
from core.base_page import BasePage
from data.property_factory import PropertyData

US_STATE_CODES = (
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
)

from data.property_factory import PROPERTY_TYPES as EXPECTED_PROPERTY_TYPES


class CreatePropertyPage(BasePage):
    """Page object for the Create New Property modal."""

    DIALOG_TITLE = re.compile(r"create new property", re.I)
    NAME_PLACEHOLDER = re.compile(
        r"Sunset Apartments, Building A, Property ID: 12345", re.I
    )
    NAME_HELPER_TEXT = "Enter a unique name or identifier for this property"
    PHOTOS_HELPER_TEXT = re.compile(r"Map image will be used if no photos", re.I)
    DOCUMENT_CATEGORY_HELPER = "Selected category is saved to the file metadata"
    VALIDATION_ERROR = (
        ".MuiFormHelperText-root.Mui-error, "
        '[role="alert"].MuiAlert-colorError, '
        "p.Mui-error"
    )

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        super().__init__(page, settings)

    @property
    def dialog(self) -> Locator:
        return self.page.get_by_role("dialog", name=self.DIALOG_TITLE)

    # ------------------------------------------------------------------
    # Locators
    # ------------------------------------------------------------------

    @property
    def name_field(self) -> Locator:
        return self.dialog.get_by_role(
            "textbox",
            name=re.compile(r"Sunset Apartments|Property ID", re.I),
        )

    @property
    def address_field(self) -> Locator:
        return self.dialog.get_by_role(
            "combobox",
            name=re.compile(r"Start typing an address", re.I),
        )

    @property
    def city_field(self) -> Locator:
        return self.dialog.get_by_role("textbox", name="City")

    @property
    def state_field(self) -> Locator:
        return self.dialog.get_by_role("combobox").nth(1)

    @property
    def zip_field(self) -> Locator:
        return self.dialog.get_by_role("textbox", name="ZIP Code")

    @property
    def property_type_field(self) -> Locator:
        return self._property_type_combobox()

    @property
    def square_footage_field(self) -> Locator:
        return self.dialog.get_by_role("textbox", name="Total sq ft")

    @property
    def year_built_field(self) -> Locator:
        return self.dialog.get_by_role("textbox", name="YYYY")

    @property
    def notes_field(self) -> Locator:
        return self.dialog.get_by_role(
            "textbox",
            name=re.compile(r"Additional notes", re.I),
        )

    @property
    def category_field(self) -> Locator:
        return self.dialog.get_by_role("combobox", name=re.compile(r"Category", re.I))

    @property
    def photos_file_input(self) -> Locator:
        return self.dialog.locator('input[type="file"]').nth(0)

    @property
    def documents_file_input(self) -> Locator:
        return self.dialog.locator('input[type="file"]').nth(1)

    @property
    def photos_upload_area(self) -> Locator:
        return self.dialog.get_by_text(re.compile(r"Click to upload or drag", re.I))

    @property
    def documents_upload_area(self) -> Locator:
        return self.dialog.get_by_text(re.compile(r"Click to upload documents", re.I))

    @property
    def submit_button(self) -> Locator:
        return self.dialog.get_by_role("button", name="Create Property", exact=True)

    @property
    def cancel_button(self) -> Locator:
        return self.dialog.get_by_role("button", name="Cancel", exact=True)

    @property
    def close_button(self) -> Locator:
        return self.dialog.get_by_role(
            "button", name=re.compile(r"close create property modal", re.I)
        )

    # ------------------------------------------------------------------
    # Navigation / modal lifecycle
    # ------------------------------------------------------------------

    def expect_loaded(self) -> None:
        expect(self.dialog).to_be_visible(timeout=self.assertion_timeout)
        expect(self.name_field).to_be_visible(timeout=self.assertion_timeout)
        expect(self.address_field).to_be_visible(timeout=self.assertion_timeout)
        expect(self.submit_button).to_be_visible(timeout=self.assertion_timeout)

    def expect_modal_closed(self) -> None:
        expect(self.dialog).to_be_hidden(timeout=self.assertion_timeout)

    def close_via_x(self) -> None:
        self.close_button.click()
        self.expect_modal_closed()

    def close_via_cancel(self) -> None:
        self.cancel_button.click()
        self.expect_modal_closed()

    # ------------------------------------------------------------------
    # Fill helpers
    # ------------------------------------------------------------------

    def fill_name(self, name: str) -> "CreatePropertyPage":
        self.name_field.fill(name)
        return self

    @staticmethod
    def _street_query(full_query: str) -> str:
        """Mapbox triggers suggestions best on street-level partial input."""
        return full_query.split(",")[0].strip()

    def type_address_query(self, query: str) -> "CreatePropertyPage":
        street = self._street_query(query)
        self.address_field.click()
        self.address_field.fill("")
        self.address_field.press_sequentially(street, delay=30)
        return self

    def _confirm_address_or_fallback(
        self,
        fallback: PropertyData | None,
        query: str,
    ) -> None:
        suggestion = self.page.get_by_role("listbox").get_by_role("option").first
        try:
            expect(suggestion).to_be_visible(timeout=8_000)
            suggestion.click()
        except AssertionError:
            if fallback is None:
                raise
            self.fill_city(fallback.city)
            self.select_state(fallback.state)
            self.fill_zip(fallback.zip_code)
            if not self.address_field.input_value():
                self.address_field.fill(self._street_query(query))

    def fill_address(
        self,
        query: str,
        *,
        confirm_suggestion: bool = True,
        fallback: PropertyData | None = None,
    ) -> "CreatePropertyPage":
        self.type_address_query(query)
        if confirm_suggestion:
            self._confirm_address_or_fallback(fallback, query)
        return self

    def fill_address_with_autocomplete(
        self, query: str, fallback: PropertyData | None = None
    ) -> "CreatePropertyPage":
        return self.fill_address(query, confirm_suggestion=True, fallback=fallback)

    def fill_city(self, city: str) -> "CreatePropertyPage":
        self.city_field.fill(city)
        return self

    def _select_listbox_option(self, option_name: str) -> None:
        listbox = self.page.get_by_role("listbox").last
        expect(listbox).to_be_visible(timeout=self.assertion_timeout)
        option = listbox.get_by_role("option", disabled=False).filter(
            has_text=re.compile(rf"^{re.escape(option_name)}$", re.I)
        )
        expect(option.first).to_be_visible(timeout=self.assertion_timeout)
        option.first.click()

    def select_state(self, state: str) -> "CreatePropertyPage":
        self.state_field.click()
        self._select_listbox_option(state)
        return self

    def fill_zip(self, zip_code: str) -> "CreatePropertyPage":
        self.zip_field.fill(zip_code)
        return self

    def _property_type_combobox(self) -> Locator:
        # Exact names only — regex breaks on "Warehouse/Industrial" (unescaped /).
        combobox = self.dialog.get_by_role("combobox", name="Select type")
        for option_name in EXPECTED_PROPERTY_TYPES:
            combobox = combobox.or_(
                self.dialog.get_by_role("combobox", name=option_name, exact=True)
            )
        return combobox.first

    def select_property_type(self, property_type: str) -> "CreatePropertyPage":
        self._property_type_combobox().click()
        self._select_listbox_option(property_type)
        return self

    def fill_square_footage(self, value: str) -> "CreatePropertyPage":
        self.square_footage_field.fill(value)
        return self

    def fill_year_built(self, year: str) -> "CreatePropertyPage":
        self.year_built_field.fill(year)
        return self

    def fill_notes(self, notes: str) -> "CreatePropertyPage":
        if notes:
            self.notes_field.fill(notes)
        return self

    def select_document_category(self, category: str) -> "CreatePropertyPage":
        self.category_field.click()
        self._select_listbox_option(category)
        return self

    def upload_photo(self, file_path: str | Path) -> "CreatePropertyPage":
        self.photos_file_input.set_input_files(str(file_path))
        return self

    def upload_document(self, file_path: str | Path) -> "CreatePropertyPage":
        self.documents_file_input.set_input_files(str(file_path))
        return self

    def fill_all_required_fields_manual(self, data: PropertyData) -> "CreatePropertyPage":
        """Fill required fields manually (no address autocomplete selection)."""
        return self.fill_required_except(data, field="")

    def fill_required_except(
        self, data: PropertyData, field: str
    ) -> "CreatePropertyPage":
        """Fill all required fields except the one specified (empty string = fill all)."""
        if field != "name":
            self.fill_name(data.name)

        if field != "address":
            # Selecting a suggestion auto-fills city/state/zip — avoid that when
            # testing those fields in isolation.
            if field in ("city", "state", "zip"):
                self.type_address_query(data.address_query)
            else:
                self.fill_address(
                    data.address_query,
                    confirm_suggestion=True,
                    fallback=data,
                )

        if field != "city":
            self.fill_city(data.city)
        if field != "state":
            self.select_state(data.state)
        if field != "zip":
            self.fill_zip(data.zip_code)
        if field != "property_type":
            self.select_property_type(data.property_type)

        return self

    def fill_all_required_fields(self, data: PropertyData) -> "CreatePropertyPage":
        """Fill required fields using address autocomplete when possible."""
        self.fill_name(data.name)
        self.fill_address_with_autocomplete(data.address_query, fallback=data)
        self.select_property_type(data.property_type)
        return self

    def submit(self) -> None:
        expect(self.submit_button).to_be_enabled(timeout=self.assertion_timeout)
        self.submit_button.click()

    def create_property(self, data: PropertyData) -> None:
        self.fill_all_required_fields(data)
        if data.square_footage:
            self.fill_square_footage(data.square_footage)
        if data.year_built:
            self.fill_year_built(data.year_built)
        if data.notes:
            self.fill_notes(data.notes)
        self.submit()
        self._wait_for_submit_outcome(data.name)

    def _wait_for_submit_outcome(self, property_name: str) -> None:
        self.page.wait_for_function(
            """([name]) => {
                const dialogOpen = !!document.querySelector('[role="dialog"]');
                const hasError = !!document.querySelector(
                    '.MuiFormHelperText-root.Mui-error, [role="alert"].MuiAlert-colorError'
                );
                const nameOnPage = (document.body?.innerText || '').includes(name);
                return hasError || (!dialogOpen && nameOnPage);
            }""",
            arg=[property_name],
            timeout=self.assertion_timeout,
        )
        self.page.wait_for_load_state("domcontentloaded")

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------

    def expect_submit_disabled(self) -> None:
        expect(self.submit_button).to_be_disabled(timeout=self.assertion_timeout)

    def expect_submit_enabled(self) -> None:
        expect(self.submit_button).to_be_enabled(timeout=self.assertion_timeout)

    def expect_all_required_fields_empty(self) -> None:
        expect(self.name_field).to_be_empty()
        expect(self.city_field).to_be_empty()
        expect(self.zip_field).to_be_empty()

    def expect_name_value(self, name: str) -> None:
        expect(self.name_field).to_have_value(name)

    def expect_name_placeholder_visible(self) -> None:
        expect(self.name_field).to_have_attribute(
            "placeholder", self.NAME_PLACEHOLDER
        )

    def expect_name_helper_text(self) -> None:
        expect(self.dialog.get_by_text(self.NAME_HELPER_TEXT)).to_be_visible()

    def expect_address_suggestions_visible(self) -> None:
        expect(
            self.page.get_by_role("listbox").get_by_role("option").first
        ).to_be_visible(timeout=self.assertion_timeout)

    def expect_city_value(self, city: str) -> None:
        expect(self.city_field).to_have_value(city)

    def expect_zip_value(self, zip_code: str) -> None:
        expect(self.zip_field).to_have_value(zip_code)

    def expect_state_selected(self, state: str) -> None:
        expect(self.state_field).to_contain_text(re.compile(state, re.I))

    def expect_property_type_selected(self, property_type: str) -> None:
        expect(
            self.dialog.get_by_role("combobox", name=property_type, exact=True)
        ).to_be_visible(timeout=self.assertion_timeout)

    def expect_property_type_options_available(self) -> None:
        self.dialog.get_by_role("combobox", name="Select type").click()
        listbox = self.page.get_by_role("listbox").last
        expect(listbox).to_be_visible(timeout=self.assertion_timeout)
        for option_name in EXPECTED_PROPERTY_TYPES:
            expect(
                listbox.get_by_role("option", disabled=False).filter(
                    has_text=re.compile(rf"^{re.escape(option_name)}$", re.I)
                )
            ).to_be_visible()
        self.page.keyboard.press("Escape")

    def expect_state_options_include_us_states(self) -> None:
        self.state_field.click()
        listbox = self.page.get_by_role("listbox")
        expect(listbox).to_be_visible(timeout=self.assertion_timeout)
        for code in ("FL", "CA", "NY"):
            expect(
                listbox.get_by_role("option", name=re.compile(code, re.I))
            ).to_be_visible()
        self.page.keyboard.press("Escape")

    def expect_square_footage_value(self, value: str) -> None:
        expect(self.square_footage_field).to_have_value(value)

    def expect_year_built_value(self, year: str) -> None:
        expect(self.year_built_field).to_have_value(year)

    def expect_notes_value(self, notes: str) -> None:
        expect(self.notes_field).to_have_value(notes)

    def expect_category_default_other(self) -> None:
        expect(self.category_field).to_contain_text(re.compile(r"other", re.I))

    def expect_category_selected(self, category: str) -> None:
        expect(self.category_field).to_contain_text(re.compile(category, re.I))
        expect(self.dialog.get_by_text(self.DOCUMENT_CATEGORY_HELPER)).to_be_visible()

    def expect_photos_helper_text(self) -> None:
        expect(self.dialog.get_by_text(self.PHOTOS_HELPER_TEXT)).to_be_visible()

    def expect_validation_errors(self) -> None:
        expect(self.dialog.locator(self.VALIDATION_ERROR).first).to_be_visible(
            timeout=self.assertion_timeout
        )

    def expect_form_not_submitted(self) -> None:
        expect(self.dialog).to_be_visible(timeout=self.assertion_timeout)

    def expect_address_fields_populated(self) -> None:
        expect(self.city_field).not_to_be_empty(timeout=self.assertion_timeout)
        expect(self.zip_field).not_to_be_empty(timeout=self.assertion_timeout)
        expect(self.state_field).to_contain_text(
            re.compile(r"\w{2,}"), timeout=self.assertion_timeout
        )

    def expect_upload_success(self) -> None:
        expect(
            self.dialog.locator("img").or_(
                self.dialog.get_by_text(
                    re.compile(r"uploaded|remove|delete|\.pdf|\.png|\.jpg", re.I)
                )
            ).first
        ).to_be_visible(timeout=self.assertion_timeout)

    def expect_photo_uploaded(self) -> None:
        self.expect_upload_success()

    def expect_upload_error(self) -> None:
        expect(
            self.dialog.locator(self.VALIDATION_ERROR).or_(
                self.dialog.get_by_text(
                    re.compile(r"invalid|not accepted|only|size|limit|10\s*mb", re.I)
                )
            ).first
        ).to_be_visible(timeout=self.assertion_timeout)
