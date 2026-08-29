"""Automated lightweight browser launcher for kiosk/app mode."""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import threading
import time

logger = logging.getLogger(__name__)

MEMORY_SAVING_FLAGS = [
    "--disable-gpu",
    "--disable-software-rasterizer",
    "--disable-extensions",
    "--disable-background-networking",
    "--disable-sync",
    "--disable-translate",
    "--no-first-run",
    '--js-flags=--max-old-space-size=128',
]


def _find_browser_binary() -> str | None:
    custom = os.environ.get("WEB_BROWSER")
    if custom and shutil.which(custom):
        return custom

    candidates = [
        "chromium-browser",
        "chromium",
        "google-chrome-stable",
        "google-chrome",
        "brave-browser",
        "firefox",
        "xdg-open",
    ]
    for binary in candidates:
        path = shutil.which(binary)
        if path:
            return path
    return None


def launch_browser(url: str) -> None:
    """Launch the browser pointing to target URL with resource-saving flags."""
    if os.environ.get("WEB_NO_BROWSER", "0").strip() in {"1", "true", "yes"}:
        logger.info("Automatic browser launch disabled via WEB_NO_BROWSER.")
        return

    binary = _find_browser_binary()
    if not binary:
        logger.warning("No suitable web browser found to auto-launch.")
        return

    is_chromium = any(
        name in os.path.basename(binary).lower()
        for name in ("chromium", "chrome", "brave")
    )

    if is_chromium:
        cmd = [
            binary,
            f"--app={url}",
            "--window-size=1024,600",
            *MEMORY_SAVING_FLAGS,
        ]
    else:
        cmd = [binary, url]

    logger.info("Launching browser: %s", " ".join(cmd))
    try:
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError as exc:
        logger.warning("Failed to launch browser %s: %s", binary, exc)


def launch_browser_in_background(url: str, delay_seconds: float = 1.0) -> None:
    """Launch browser asynchronously after a brief warmup delay."""
    def _runner() -> None:
        time.sleep(delay_seconds)
        launch_browser(url)

    thread = threading.Thread(target=_runner, daemon=True, name="BrowserLauncher")
    thread.start()
