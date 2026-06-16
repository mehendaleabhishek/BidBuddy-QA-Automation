import re

from playwright.sync_api import Page, expect


class AppModals:
    """Dismiss first-run and announcement overlays that block PM workflows."""

    def __init__(self, page: Page, timeout_ms: int = 5000) -> None:
        self.page = page
        self.timeout_ms = timeout_ms

    def dismiss_all(self) -> None:
        for _ in range(3):
            dismissed = self.dismiss_welcome_dialog() or self.dismiss_whats_new_banner()
            if not dismissed:
                break

    def dismiss_welcome_dialog(self) -> bool:
        understand = self.page.get_by_role("button", name="I Understand")
        try:
            expect(understand).to_be_visible(timeout=self.timeout_ms)
            understand.click()
            expect(understand).to_be_hidden(timeout=self.timeout_ms)
            return True
        except AssertionError:
            return False

    def dismiss_whats_new_banner(self) -> bool:
        banner = self.page.get_by_text("New update available!", exact=False)
        try:
            expect(banner).to_be_visible(timeout=self.timeout_ms)
        except AssertionError:
            return False

        close_button = (
            self.page.get_by_role("button", name=re.compile(r"close", re.I))
            .or_(self.page.locator('[aria-label="Close"], [aria-label="close"]'))
        )
        if close_button.first.is_visible():
            close_button.first.click()
        else:
            icon_close = banner.locator(
                "xpath=ancestor::*[contains(@class,'Mui')][1]"
            ).get_by_role("button").last
            if icon_close.is_visible():
                icon_close.click()
            else:
                self.page.keyboard.press("Escape")

        try:
            expect(banner).to_be_hidden(timeout=self.timeout_ms)
            return True
        except AssertionError:
            return False
