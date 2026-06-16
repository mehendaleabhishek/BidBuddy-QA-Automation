import re

from playwright.sync_api import Locator, Page, expect

from config.settings import Settings
from core.base_page import BasePage


class LoginPage(BasePage):
    """Page object for /auth/sign-in."""

    EMAIL_INPUT = 'input[name="email"], input[type="email"]'
    PASSWORD_INPUT = 'input[name="password"], input[type="password"]'
    SUBMIT_BUTTON = 'button[type="submit"]'
    # MUI renders multiple alerts; target only the error variant.
    ERROR_ALERT = '[role="alert"].MuiAlert-colorError'

    def __init__(self, page: Page, settings: Settings | None = None) -> None:
        super().__init__(page, settings)

    @property
    def email_field(self) -> Locator:
        return self.page.locator(self.EMAIL_INPUT).first

    @property
    def password_field(self) -> Locator:
        return self.page.locator(self.PASSWORD_INPUT).first

    @property
    def submit_button(self) -> Locator:
        return self.page.locator(self.SUBMIT_BUTTON).first

    @property
    def error_alert(self) -> Locator:
        return self.page.locator(self.ERROR_ALERT)

    def open(self, return_to: str | None = None) -> "LoginPage":
        url = self.settings.login_url
        if return_to:
            url = f"{url}?returnTo={return_to}"
        self.page.goto(url, wait_until="domcontentloaded")
        self.expect_login_form_visible()
        return self

    def expect_login_form_visible(self) -> None:
        expect(self.email_field).to_be_visible(timeout=self.assertion_timeout)
        expect(self.password_field).to_be_visible(timeout=self.assertion_timeout)
        expect(self.submit_button).to_be_visible(timeout=self.assertion_timeout)

    def fill_email(self, email: str) -> "LoginPage":
        self.email_field.fill(email)
        return self

    def fill_password(self, password: str) -> "LoginPage":
        self.password_field.fill(password)
        return self

    def submit(self) -> None:
        self.submit_button.click()

    def login(self, email: str, password: str) -> None:
        self.fill_email(email).fill_password(password).submit()
        self._wait_for_login_outcome()

    def _wait_for_login_outcome(self) -> None:
        """Wait until login either redirects away from sign-in or shows an error."""
        sign_in = re.compile(r".*/auth/sign-in.*")
        self.page.wait_for_function(
            """() => {
                const onSignIn = window.location.pathname.includes('/auth/sign-in');
                const hasError = !!document.querySelector('[role="alert"].MuiAlert-colorError');
                return !onSignIn || hasError;
            }""",
            timeout=self.assertion_timeout,
        )
        if sign_in.match(self.page.url) and self.error_alert.is_visible():
            return
        self.page.wait_for_load_state("domcontentloaded")

    def expect_error_message(self, message: str | re.Pattern[str] | None = None) -> None:
        expect(self.error_alert).to_be_visible(timeout=self.assertion_timeout)
        if message is not None:
            expect(self.error_alert).to_contain_text(
                message, timeout=self.assertion_timeout
            )

    def expect_redirect_to_dashboard(self, role: str = "property-manager") -> None:
        if self.error_alert.is_visible():
            error_text = self.error_alert.inner_text()
            raise AssertionError(
                f"Login failed with error: {error_text!r}. "
                "Check credentials in .env."
            )

        # App may redirect to /property-manager/* or /dashboard/property-manager/*
        pattern = re.compile(rf".*/(dashboard/)?{re.escape(role)}(/|$|\?)")
        expect(self.page).to_have_url(pattern, timeout=self.assertion_timeout)
