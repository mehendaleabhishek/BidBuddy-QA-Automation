from __future__ import annotations

from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page

SCREENSHOTS_ROOT = Path(__file__).resolve().parent.parent / "screenshots"


def create_run_directory(root: Path | None = None) -> Path:
    """Create a timestamped folder for the current pytest session."""
    base = root or SCREENSHOTS_ROOT
    run_dir = base / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run_info.txt").write_text(
        f"Test run started: {datetime.now().isoformat()}\n",
        encoding="utf-8",
    )
    return run_dir


def build_screenshot_path(run_dir: Path, nodeid: str) -> Path:
    """
    Build an organized screenshot path:
    screenshots/<run-timestamp>/<test_module>/<test_name>.png
    """
    parts = nodeid.split("::")
    module_name = Path(parts[0]).stem if parts else "unknown"
    test_name = "__".join(parts[1:]) if len(parts) > 1 else "unknown"
    safe_name = (
        test_name.replace("/", "_")
        .replace("[", "_")
        .replace("]", "")
        .replace(" ", "_")
    )
    target_dir = run_dir / module_name
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / f"{safe_name}.png"


def capture_failure_screenshot(page: Page, run_dir: Path, nodeid: str) -> Path:
    screenshot_path = build_screenshot_path(run_dir, nodeid)
    page.screenshot(path=str(screenshot_path), full_page=True)
    return screenshot_path
