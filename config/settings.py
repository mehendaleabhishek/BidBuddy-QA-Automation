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
    def _env(name: str, default: str = "") -> str:
        return os.getenv(name, default).strip()

    return Settings(
        base_url=_env("BASE_URL", "https://dev.bidbuddy.com"),
        default_timeout_ms=int(_env("DEFAULT_TIMEOUT_MS", "30000")),
        headless=_env("HEADLESS", "true").lower() == "true",
        slow_mo_ms=int(_env("SLOW_MO_MS", "0")),
        pm_email=_env("PM_EMAIL"),
        pm_password=_env("PM_PASSWORD"),
        vendor_email=_env("VENDOR_EMAIL"),
        vendor_password=_env("VENDOR_PASSWORD"),
    )
