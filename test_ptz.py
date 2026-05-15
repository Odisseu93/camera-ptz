"""Test ONVIF PTZ connectivity."""
from __future__ import annotations

import sys

from config import candidate_ptz_urls, load_config
from ptz_controller import PTZController


def probe_url(url: str, username: str, password: str) -> tuple[bool, str]:
    ctrl = PTZController(url, username, password)
    try:
        ctrl.send_continuous_move_command(0, 0)
        ctrl.send_stop_command()
        return True, "command sent (zero movement + stop)"
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def main() -> int:
    cfg = load_config()
    urls = [cfg.onvif_ptz_url] + [
        u for u in candidate_ptz_urls(cfg.host) if u != cfg.onvif_ptz_url
    ]

    print(f"Host: {cfg.host} | User: {cfg.username}")
    print("Testing ONVIF PTZ endpoints...\n")

    for url in urls:
        ok, detail = probe_url(url, cfg.username, cfg.password)
        status = "OK" if ok else "FAILED"
        print(f"[{status}] {url}")
        print(f"       {detail}\n")
        if ok:
            print("Use this endpoint in .env:")
            print(f'  ONVIF_PTZ_URL="{url}"')
            return 0

    print(
        "No endpoint responded. Check whether ONVIF/PTZ is enabled in the Yoosee app "
        "and if this PC is on the same camera network."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
