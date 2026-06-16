"""
Smoke-level create property checks.

Full CSV coverage (TC-01 – TC-40): tests/regression/test_create_property_modal.py
"""

import pytest

from pages.property_manager.properties_list_page import PropertiesListPage


@pytest.mark.regression
@pytest.mark.property_manager
@pytest.mark.create_property
class TestCreatePropertySmoke:
    def test_properties_page_reachable(
        self,
        pm_properties_list_page: PropertiesListPage,
    ) -> None:
        pm_properties_list_page.expect_loaded()
