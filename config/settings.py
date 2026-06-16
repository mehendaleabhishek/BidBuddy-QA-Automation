from dataclasses import dataclass
from functools import lru_cache
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    base_url: str
    default_timeout_ms: int
    headless: bool
    slow_mo_ms: int
    pm_email: str
    pm_password: str
    vendor_email: str
    vendor_password: str

    @property
    def login_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/auth/sign-in"

    @property
    def pm_dashboard_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/property-manager"

    @property
    def pm_properties_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/property-manager/properties"

    @property
    def vendor_dashboard_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/vendor"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        base_url=os.getenv("BASE_URL", "https://dev.bidbuddy.com"),
        default_timeout_ms=int(os.getenv("DEFAULT_TIMEOUT_MS", "30000")),
        headless=os.getenv("HEADLESS", "true").lower() == "true",
        slow_mo_ms=int(os.getenv("SLOW_MO_MS", "0")),
        pm_email=os.getenv("PM_EMAIL", ""),
        pm_password=os.getenv("PM_PASSWORD", ""),
        vendor_email=os.getenv("VENDOR_EMAIL", ""),
        vendor_password=os.getenv("VENDOR_PASSWORD", ""),
    )
