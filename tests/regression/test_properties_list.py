"""
Automated tests for the Properties List page.

Mapped to: test_cases/BidBuddy Test Cases - Properties List page.csv (TC-01 – TC-14)
"""

import re

import pytest
from playwright.sync_api import expect

from pages.property_manager.properties_list_page import PropertiesListPage


pytestmark = [
    pytest.mark.regression,
    pytest.mark.property_manager,
    pytest.mark.properties_list,
]


# =============================================================================
# TC-01: View Properties List Page
# =============================================================================


class TestPropertiesListPageView:
    def test_tc01_view_properties_list_page(
        self,
        authenticated_pm_page,
        settings,
    ) -> None:
        """TC-01: Properties page loads with title and sidebar navigation."""
        list_page = PropertiesListPage(authenticated_pm_page, settings)
        list_page.navigate("/property-manager/rfps")
        list_page.dismiss_app_modals()
        list_page.open_via_sidebar()

        list_page.expect_loaded()
        list_page.expect_page_header()
        list_page.expect_properties_navigation_active()

    def test_extra_page_subtitle_and_toolbar_visible(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """Extra: Search and filter controls are visible."""
        pm_properties_list_page.expect_page_header()
        pm_properties_list_page.search_field.wait_for(state="visible")
        pm_properties_list_page.type_filter.wait_for(state="visible")
        pm_properties_list_page.sort_by_filter.wait_for(state="visible")
        pm_properties_list_page.density_filter.wait_for(state="visible")

    def test_extra_add_property_card_visible(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """Extra: Dashed 'Add Property' card is shown in the grid."""
        pm_properties_list_page.expect_add_property_card_visible()


# =============================================================================
# TC-02: Create New Property
# =============================================================================


class TestCreatePropertyEntryPoints:
    def test_tc02_new_property_button_opens_modal(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """TC-02: '+ New Property' opens the create modal."""
        modal = pm_properties_list_page.start_create_property()

        modal.expect_loaded()
        modal.expect_submit_disabled()

    def test_extra_add_property_card_opens_modal(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """Extra: 'Add Property' grid card opens the create modal."""
        modal = pm_properties_list_page.start_create_from_add_card()

        modal.expect_loaded()
        modal.expect_submit_disabled()


# =============================================================================
# TC-03 – TC-05: Search
# =============================================================================


class TestPropertiesSearch:
    def test_tc03_search_filters_to_matching_property(
        self,
        pm_properties_list_page: PropertiesListPage,
        existing_property_names: list[str],
    ) -> None:
        """TC-03: Search filters to properties matching name or address."""
        target = existing_property_names[0]
        pm_properties_list_page.search(target)

        pm_properties_list_page.expect_property_visible(target)
        for other in existing_property_names[1:]:
            pm_properties_list_page.expect_property_hidden(other)

    def test_tc03_search_partial_name(
        self,
        pm_properties_list_page: PropertiesListPage,
        first_property_name: str,
    ) -> None:
        """TC-03 (extra): Partial name search still shows the property."""
        partial = first_property_name[: max(4, len(first_property_name) // 2)]
        pm_properties_list_page.search(partial)

        pm_properties_list_page.expect_property_visible(first_property_name)

    def test_tc04_search_with_no_match(
        self,
        pm_properties_list_page: PropertiesListPage,
        existing_property_names: list[str],
    ) -> None:
        """TC-04: Nonsense query hides property cards (no explicit empty message)."""
        pm_properties_list_page.search("XYZABC_NO_MATCH_AUTOMATION")

        pm_properties_list_page.expect_no_search_results()
        for name in existing_property_names:
            pm_properties_list_page.expect_property_hidden(name)

    def test_tc05_search_with_empty_input(
        self,
        pm_properties_list_page: PropertiesListPage,
        existing_property_names: list[str],
    ) -> None:
        """TC-05: Clearing search restores the full property list."""
        pm_properties_list_page.search("XYZABC_NO_MATCH_AUTOMATION")
        pm_properties_list_page.expect_no_search_results()

        pm_properties_list_page.clear_search()
        pm_properties_list_page.expect_search_field_empty()

        for name in existing_property_names:
            pm_properties_list_page.expect_property_visible(name)


# =============================================================================
# TC-06 – TC-07: Sort By
# =============================================================================


class TestPropertiesSort:
    def test_tc06_sort_by_most_recent(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """TC-06: 'Most Recent' sort option can be selected."""
        options = pm_properties_list_page.get_sort_by_options()
        if "Most Recent" not in options:
            pytest.skip("'Most Recent' not in Sort By dropdown on this environment.")

        pm_properties_list_page.select_sort_by("Most Recent")
        pm_properties_list_page.expect_sort_by("Most Recent")
        pm_properties_list_page.expect_empty_state_or_cards()

    def test_tc07_sort_by_each_option(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """TC-07: Each Sort By option re-orders without breaking the page."""
        options = pm_properties_list_page.get_sort_by_options()
        if not options:
            pytest.skip("No Sort By options available.")

        for option in options:
            pm_properties_list_page.select_sort_by(option)
            pm_properties_list_page.expect_sort_by(option)
            pm_properties_list_page.expect_empty_state_or_cards()


# =============================================================================
# TC-08 – TC-09: Density
# =============================================================================


class TestPropertiesDensity:
    def test_tc08_density_compact(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """TC-08: 'Compact' density can be selected."""
        options = pm_properties_list_page.get_density_options()
        if "Compact" not in options:
            pytest.skip("'Compact' not in Density dropdown on this environment.")

        pm_properties_list_page.select_density("Compact")
        pm_properties_list_page.expect_density("Compact")
        pm_properties_list_page.expect_empty_state_or_cards()

    def test_tc09_density_each_option(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """TC-09: Each density option updates the toolbar selection."""
        options = pm_properties_list_page.get_density_options()
        if not options:
            pytest.skip("No Density options available.")

        for option in options:
            pm_properties_list_page.select_density(option)
            pm_properties_list_page.expect_density(option)
            pm_properties_list_page.expect_empty_state_or_cards()


# =============================================================================
# TC-10 – TC-11: Type Filter
# =============================================================================


class TestPropertiesTypeFilter:
    def test_tc10_filter_by_property_type(
        self,
        pm_properties_list_page: PropertiesListPage,
        first_property_name: str,
    ) -> None:
        """TC-10: Type filter shows only properties of the selected type."""
        type_tag = pm_properties_list_page.get_card_type_tag(first_property_name)
        if not type_tag:
            pytest.skip(f"Could not read type tag for '{first_property_name}'.")

        filter_options = pm_properties_list_page.get_type_filter_options()
        matching_option = next(
            (opt for opt in filter_options if type_tag.lower() in opt.lower()),
            None,
        )
        if not matching_option:
            pytest.skip(f"No type filter option matching '{type_tag}'.")

        pm_properties_list_page.select_type_filter(matching_option)
        pm_properties_list_page.expect_type_filter(
            re.compile(re.escape(type_tag), re.I)
        )
        pm_properties_list_page.expect_property_visible(first_property_name)

        for name in pm_properties_list_page.get_property_names():
            card_type = pm_properties_list_page.get_card_type_tag(name)
            assert card_type and type_tag.lower() in card_type.lower()

    def test_tc11_type_filter_all(
        self,
        pm_properties_list_page: PropertiesListPage,
        existing_property_names: list[str],
    ) -> None:
        """TC-11: 'All' filter restores the full list with count label."""
        filter_options = pm_properties_list_page.get_type_filter_options()
        all_option = next(
            (opt for opt in filter_options if re.match(r"^All\s*\(", opt, re.I)),
            None,
        )
        if not all_option:
            pytest.skip("'All (n)' option not found in Type filter.")

        pm_properties_list_page.select_type_filter(all_option)
        pm_properties_list_page.expect_type_filter(all_option)
        pm_properties_list_page.expect_all_type_filter_matches_card_count()

        for name in existing_property_names:
            pm_properties_list_page.expect_property_visible(name)


# =============================================================================
# TC-12 – TC-14: Property Cards
# =============================================================================


class TestPropertyCards:
    def test_tc12_property_card_displays_correct_info(
        self,
        pm_properties_list_page: PropertiesListPage,
        first_property_name: str,
    ) -> None:
        """TC-12: Card shows image, type tag, name, and RFP count."""
        pm_properties_list_page.expect_card_structure(first_property_name)

    def test_tc13_click_property_card_navigates_to_detail(
        self,
        pm_properties_list_page: PropertiesListPage,
        first_property_name: str,
    ) -> None:
        """TC-13: Clicking a card opens the property detail page."""
        detail = pm_properties_list_page.open_property(first_property_name)

        detail.expect_loaded()
        detail.expect_property_name(first_property_name)

    def test_tc14_property_with_no_photos_shows_placeholder(
        self,
        pm_properties_list_page: PropertiesListPage,
        existing_property_names: list[str],
    ) -> None:
        """TC-14: Cards without photos still show image or placeholder."""
        for name in existing_property_names:
            pm_properties_list_page.expect_card_has_photo_or_placeholder(name)


# =============================================================================
# Extra coverage
# =============================================================================


class TestPropertiesListExtras:
    def test_grid_and_list_view_toggle(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """Extra: Grid and list view toggles are usable."""
        pm_properties_list_page.select_list_view()
        pm_properties_list_page.expect_empty_state_or_cards()

        pm_properties_list_page.select_grid_view()
        pm_properties_list_page.expect_empty_state_or_cards()

    def test_search_field_placeholder(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """Extra: Search field shows expected placeholder."""
        expect(pm_properties_list_page.search_field).to_have_attribute(
            "placeholder", re.compile(r"Search properties", re.I)
        )

    def test_type_filter_options_include_all(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        """Extra: Type filter includes an 'All (n)' option."""
        options = pm_properties_list_page.get_type_filter_options()
        assert any(re.match(r"^All\s*\(", opt, re.I) for opt in options)
