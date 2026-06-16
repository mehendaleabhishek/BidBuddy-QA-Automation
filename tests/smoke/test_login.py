import re

import pytest

from pages.auth.login_page import LoginPage


@pytest.mark.smoke
class TestLogin:
    def test_login_page_loads(self, login_page: LoginPage) -> None:
        login_page.open()
        login_page.expect_login_form_visible()

    def test_login_with_invalid_credentials_shows_error(
        self,
        login_page: LoginPage,
    ) -> None:
        login_page.open()
        login_page.login("invalid@example.com", "wrong-password")

        login_page.expect_error_message()

    @pytest.mark.property_manager
    def test_property_manager_login_redirects_to_dashboard(
        self,
        login_page: LoginPage,
        settings,
    ) -> None:
        if not settings.pm_email or not settings.pm_password:
            pytest.skip("PM credentials not configured in .env")

        login_page.open()
        login_page.login(settings.pm_email, settings.pm_password)
        login_page.expect_redirect_to_dashboard(role="property-manager")

    @pytest.mark.vendor
    def test_vendor_login_redirects_to_dashboard(
        self,
        login_page: LoginPage,
        settings,
    ) -> None:
        if not settings.vendor_email or not settings.vendor_password:
            pytest.skip("Vendor credentials not configured in .env")

        login_page.open()
        login_page.login(settings.vendor_email, settings.vendor_password)
        login_page.expect_redirect_to_dashboard(role="vendor")

    def test_unauthenticated_dashboard_access_redirects_to_login(
        self,
        page,
        settings,
    ) -> None:
        page.goto(f"{settings.base_url}/dashboard/property-manager/properties")
        page.wait_for_url(re.compile(r".*/auth/sign-in.*"))
