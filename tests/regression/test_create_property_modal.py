"""
Automated tests for Create New Property modal.

Mapped to: test_cases/BidBuddy Test Cases - Create new property modal.csv (TC-01 – TC-40)
"""

from pathlib import Path

import pytest
from playwright.sync_api import expect

from data.property_factory import PropertyData
from pages.property_manager.create_property_page import CreatePropertyPage
from pages.property_manager.properties_list_page import PropertiesListPage


pytestmark = [pytest.mark.regression, pytest.mark.property_manager, pytest.mark.create_property]


# =============================================================================
# TC-01 – TC-03: Modal open / close
# =============================================================================


class TestModalOpenClose:
    def test_tc01_open_create_new_property_modal(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """TC-01: Open Create New Property modal via '+ New Property' button."""
        modal = pm_properties_list_page.start_create_property()

        modal.expect_loaded()
        modal.expect_all_required_fields_empty()
        modal.expect_submit_disabled()

    def test_tc02_close_modal_via_x_button(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """TC-02: Close modal via X button — no data saved."""
        modal = pm_properties_list_page.start_create_property()
        modal.close_via_x()

        pm_properties_list_page.expect_loaded()

    def test_tc03_close_modal_via_cancel_button(
        self,
        create_property_modal: CreatePropertyPage,
        required_property_data: PropertyData,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """TC-03: Cancel discards entered data and closes modal."""
        create_property_modal.fill_name(required_property_data.name)
        create_property_modal.fill_city(required_property_data.city)
        create_property_modal.close_via_cancel()

        pm_properties_list_page.expect_loaded()
        expect(
            pm_properties_list_page.main.get_by_role(
                "heading", name=required_property_data.name, level=6
            )
        ).to_be_hidden()


# =============================================================================
# TC-04 – TC-06: Property Name
# =============================================================================


class TestPropertyNameField:
    def test_tc04_property_name_valid_input(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-04: Valid property name is accepted."""
        name = "Sunset Apartments"
        create_property_modal.fill_name(name)
        create_property_modal.expect_name_value(name)

    def test_tc05_property_name_empty_required(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-05: Empty property name prevents submission."""
        create_property_modal.expect_submit_disabled()
        create_property_modal.expect_form_not_submitted()

    def test_tc06_property_name_placeholder_and_helper(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-06: Placeholder and helper text visible on name field."""
        create_property_modal.expect_name_placeholder_visible()
        create_property_modal.expect_name_helper_text()


# =============================================================================
# TC-07 – TC-08: Property Address
# =============================================================================


class TestPropertyAddressField:
    def test_tc07_property_address_autocomplete_suggestions(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-07: Address autocomplete suggestions appear while typing."""
        create_property_modal.type_address_query("3151 South Babcock")
        create_property_modal.expect_address_suggestions_visible()

    def test_tc08_property_address_empty_required(
        self,
        create_property_modal: CreatePropertyPage,
        required_property_data: PropertyData,
    ) -> None:
        """TC-08: Empty address prevents submission."""
        create_property_modal.fill_required_except(required_property_data, field="address")
        create_property_modal.expect_submit_disabled()


# =============================================================================
# TC-09 – TC-10: City
# =============================================================================


class TestCityField:
    def test_tc09_city_valid_input(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-09: Valid city name accepted."""
        create_property_modal.fill_city("Melbourne")
        create_property_modal.expect_city_value("Melbourne")

    def test_tc10_city_empty_required(
        self,
        create_property_modal: CreatePropertyPage,
        required_property_data: PropertyData,
    ) -> None:
        """TC-10: Empty city prevents submission."""
        create_property_modal.fill_required_except(required_property_data, field="city")
        create_property_modal.expect_submit_disabled()


# =============================================================================
# TC-11 – TC-12: State
# =============================================================================


class TestStateField:
    def test_tc11_state_select_from_dropdown(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-11: State can be selected from dropdown."""
        create_property_modal.select_state("FL")
        create_property_modal.expect_state_selected("FL")

    def test_tc11_state_dropdown_lists_us_states(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-11 (extra): Dropdown includes major US state codes."""
        create_property_modal.expect_state_options_include_us_states()

    def test_tc12_state_empty_required(
        self,
        create_property_modal: CreatePropertyPage,
        required_property_data: PropertyData,
    ) -> None:
        """TC-12: Unselected state prevents submission."""
        create_property_modal.fill_required_except(required_property_data, field="state")
        create_property_modal.expect_submit_disabled()


# =============================================================================
# TC-13 – TC-15: ZIP Code
# =============================================================================


class TestZipCodeField:
    def test_tc13_zip_valid_5_digit_input(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-13: Valid 5-digit ZIP accepted."""
        create_property_modal.fill_zip("32901")
        create_property_modal.expect_zip_value("32901")

    def test_tc14_zip_invalid_format(
        self,
        create_property_modal: CreatePropertyPage,
        required_property_data: PropertyData,
    ) -> None:
        """TC-14: Alphabetic ZIP is accepted in field; submit not blocked client-side."""
        create_property_modal.fill_all_required_fields_manual(required_property_data)
        create_property_modal.fill_zip("ABCDE")
        create_property_modal.expect_zip_value("ABCDE")
        create_property_modal.expect_submit_enabled()

    def test_tc14_zip_too_short(
        self,
        create_property_modal: CreatePropertyPage,
        required_property_data: PropertyData,
    ) -> None:
        """TC-14 (extra): ZIP '123' is rejected."""
        create_property_modal.fill_all_required_fields_manual(required_property_data)
        create_property_modal.fill_zip("123")
        create_property_modal.expect_submit_disabled()

    def test_tc15_zip_empty_required(
        self,
        create_property_modal: CreatePropertyPage,
        required_property_data: PropertyData,
    ) -> None:
        """TC-15: Empty ZIP prevents submission."""
        create_property_modal.fill_required_except(required_property_data, field="zip")
        create_property_modal.expect_submit_disabled()


# =============================================================================
# TC-16 – TC-18: Property Type
# =============================================================================


class TestPropertyTypeField:
    def test_tc16_property_type_select_valid(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-16: Valid property type can be selected."""
        create_property_modal.select_property_type("Multifamily")
        create_property_modal.expect_property_type_selected("Multifamily")

    def test_tc17_property_type_empty_required(
        self,
        create_property_modal: CreatePropertyPage,
        required_property_data: PropertyData,
    ) -> None:
        """TC-17: Unselected property type prevents submission."""
        create_property_modal.fill_required_except(
            required_property_data, field="property_type"
        )
        create_property_modal.expect_submit_disabled()

    def test_tc18_property_type_available_options(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-18: Property type dropdown shows available options."""
        create_property_modal.expect_property_type_options_available()


# =============================================================================
# TC-19 – TC-21: Square Footage
# =============================================================================


class TestSquareFootageField:
    def test_tc19_square_footage_valid_numeric(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-19: Valid numeric square footage accepted."""
        create_property_modal.fill_square_footage("25000")
        create_property_modal.expect_square_footage_value("25000")

    def test_tc20_square_footage_non_numeric_input(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-20: Square footage accepts typed input (optional field, no hard block)."""
        create_property_modal.fill_square_footage("abc")
        create_property_modal.expect_square_footage_value("abc")

    def test_tc21_square_footage_optional_on_submit(
        self,
        pm_properties_list_page: PropertiesListPage,
        property_data: PropertyData,
    ) -> None:
        """TC-21: Form submits without square footage when required fields filled."""
        modal = pm_properties_list_page.start_create_property()
        modal.create_property(property_data)
        pm_properties_list_page.expect_property_visible(property_data.name)


# =============================================================================
# TC-22 – TC-24: Year Built
# =============================================================================


class TestYearBuiltField:
    def test_tc22_year_built_valid_4_digit(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-22: Valid 4-digit year accepted."""
        create_property_modal.fill_year_built("1998")
        create_property_modal.expect_year_built_value("1998")

    @pytest.mark.parametrize("invalid_year", ["99", "2999"])
    def test_tc23_year_built_invalid_format(
        self,
        create_property_modal: CreatePropertyPage,
        required_property_data: PropertyData,
        invalid_year: str,
    ) -> None:
        """TC-23: Invalid year is stored; optional field does not block submit."""
        create_property_modal.fill_all_required_fields_manual(required_property_data)
        create_property_modal.fill_year_built(invalid_year)
        create_property_modal.expect_year_built_value(invalid_year)

    def test_tc24_year_built_optional_on_submit(
        self,
        pm_properties_list_page: PropertiesListPage,
        property_data: PropertyData,
    ) -> None:
        """TC-24: Form submits without year built."""
        modal = pm_properties_list_page.start_create_property()
        modal.create_property(property_data)
        pm_properties_list_page.expect_property_visible(property_data.name)


# =============================================================================
# TC-25 – TC-26: Notes
# =============================================================================


class TestNotesField:
    def test_tc25_notes_accepts_optional_text(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-25: Notes textarea accepts free-form text."""
        notes = "Corner unit with recent roof replacement."
        create_property_modal.fill_notes(notes)
        create_property_modal.expect_notes_value(notes)

    def test_tc26_notes_optional_on_submit(
        self,
        pm_properties_list_page: PropertiesListPage,
        required_property_data: PropertyData,
    ) -> None:
        """TC-26: Form submits with notes left blank."""
        modal = pm_properties_list_page.start_create_property()
        modal.create_property(required_property_data)
        pm_properties_list_page.expect_property_visible(required_property_data.name)


# =============================================================================
# TC-27 – TC-31: Photos
# =============================================================================


class TestPhotosUpload:
    def test_tc27_photos_upload_valid_image(
        self,
        create_property_modal: CreatePropertyPage,
        upload_test_files: dict[str, Path],
    ) -> None:
        """TC-27: Valid PNG/JPG image uploads successfully."""
        create_property_modal.upload_photo(upload_test_files["valid_png"])
        create_property_modal.expect_photo_uploaded()

    def test_tc28_photos_upload_invalid_file_type(
        self,
        create_property_modal: CreatePropertyPage,
        upload_test_files: dict[str, Path],
    ) -> None:
        """TC-28: Unsupported photo file type rejected."""
        create_property_modal.upload_photo(upload_test_files["invalid_photo_gif"])
        create_property_modal.expect_upload_error()

    def test_tc29_photos_upload_file_over_10mb(
        self,
        create_property_modal: CreatePropertyPage,
        upload_test_files: dict[str, Path],
    ) -> None:
        """TC-29: Photo over 10MB rejected."""
        create_property_modal.upload_photo(upload_test_files["oversized_photo"])
        create_property_modal.expect_upload_error()

    def test_tc30_photos_drag_and_drop_upload(
        self,
        create_property_modal: CreatePropertyPage,
        upload_test_files: dict[str, Path],
    ) -> None:
        """TC-30: File accepted via upload area (drag-drop equivalent via input)."""
        create_property_modal.photos_upload_area.click()
        create_property_modal.upload_photo(upload_test_files["valid_jpg"])
        create_property_modal.expect_photo_uploaded()

    def test_tc31_photos_optional_on_submit(
        self,
        create_property_modal: CreatePropertyPage,
        pm_properties_list_page: PropertiesListPage,
        required_property_data: PropertyData,
    ) -> None:
        """TC-31: Submit without photos — map image used as default."""
        create_property_modal.expect_photos_helper_text()
        create_property_modal.fill_all_required_fields_manual(required_property_data)
        create_property_modal.expect_submit_enabled()
        create_property_modal.submit()
        create_property_modal._wait_for_submit_outcome(required_property_data.name)
        pm_properties_list_page.expect_property_visible(required_property_data.name)


# =============================================================================
# TC-32 – TC-36: Documents
# =============================================================================


class TestDocumentsUpload:
    def test_tc32_documents_upload_valid_file(
        self,
        create_property_modal: CreatePropertyPage,
        upload_test_files: dict[str, Path],
    ) -> None:
        """TC-32: Valid PDF document uploads successfully."""
        create_property_modal.upload_document(upload_test_files["valid_pdf"])
        create_property_modal.expect_upload_success()

    def test_tc33_documents_upload_invalid_file_type(
        self,
        create_property_modal: CreatePropertyPage,
        upload_test_files: dict[str, Path],
    ) -> None:
        """TC-33: Unsupported document type rejected."""
        create_property_modal.upload_document(upload_test_files["invalid_doc_mp4"])
        create_property_modal.expect_upload_error()

    def test_tc33_documents_upload_zip_rejected(
        self,
        create_property_modal: CreatePropertyPage,
        upload_test_files: dict[str, Path],
    ) -> None:
        """TC-33 (extra): ZIP file rejected for documents."""
        create_property_modal.upload_document(upload_test_files["invalid_doc_zip"])
        create_property_modal.expect_upload_error()

    def test_tc34_documents_upload_file_over_10mb(
        self,
        create_property_modal: CreatePropertyPage,
        upload_test_files: dict[str, Path],
    ) -> None:
        """TC-34: Document over 10MB rejected."""
        create_property_modal.upload_document(upload_test_files["oversized_document"])
        create_property_modal.expect_upload_error()

    def test_tc35_documents_select_category(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-35: Document category can be changed."""
        create_property_modal.select_document_category("Insurance")
        create_property_modal.expect_category_selected("Insurance")

    def test_tc36_documents_default_category_is_other(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-36: Default document category is 'Other'."""
        create_property_modal.expect_category_default_other()


# =============================================================================
# TC-37 – TC-40: Form submission & button states
# =============================================================================


class TestFormSubmission:
    def test_tc37_submit_all_required_fields_creates_property(
        self,
        pm_properties_list_page: PropertiesListPage,
        required_property_data: PropertyData,
    ) -> None:
        """TC-37: All required fields filled — property created and modal closes."""
        modal = pm_properties_list_page.start_create_property()
        modal.fill_all_required_fields_manual(required_property_data)
        modal.expect_submit_enabled()
        modal.submit()
        modal._wait_for_submit_outcome(required_property_data.name)
        modal.expect_modal_closed()
        pm_properties_list_page.expect_property_visible(required_property_data.name)

    @pytest.mark.parametrize(
        "missing_field",
        ["name", "address", "city", "state", "zip", "property_type"],
    )
    def test_tc38_submit_missing_one_required_field(
        self,
        create_property_modal: CreatePropertyPage,
        required_property_data: PropertyData,
        missing_field: str,
    ) -> None:
        """TC-38: Missing any single required field prevents submission."""
        create_property_modal.fill_required_except(
            required_property_data, field=missing_field
        )
        create_property_modal.expect_submit_disabled()
        create_property_modal.expect_form_not_submitted()

    def test_tc39_create_property_button_disabled_initially(
        self,
        create_property_modal: CreatePropertyPage,
    ) -> None:
        """TC-39: Create Property button disabled when form is empty."""
        create_property_modal.expect_submit_disabled()

    def test_tc40_create_property_button_enabled_when_complete(
        self,
        create_property_modal: CreatePropertyPage,
        required_property_data: PropertyData,
    ) -> None:
        """TC-40: Create Property button enabled when all required fields filled."""
        create_property_modal.fill_all_required_fields_manual(required_property_data)
        create_property_modal.expect_submit_enabled()


# =============================================================================
# Additional coverage (framework / integration)
# =============================================================================


class TestCreatePropertyIntegration:
    def test_address_autocomplete_populates_city_state_zip(
        self,
        create_property_modal: CreatePropertyPage,
        property_data: PropertyData,
    ) -> None:
        """Extra: Mapbox autocomplete auto-fills location fields."""
        create_property_modal.fill_name(property_data.name)
        create_property_modal.fill_address(
            property_data.address_query,
            confirm_suggestion=True,
            fallback=None,
        )
        create_property_modal.expect_address_fields_populated()

    def test_properties_list_page_loads(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """Extra: Properties list page renders with cards or empty state."""
        pm_properties_list_page.expect_loaded()
        pm_properties_list_page.expect_empty_state_or_cards()
