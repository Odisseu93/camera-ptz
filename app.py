"""Single entrypoint to run viewer and tests without shell scripts."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

from config import load_config, load_runtime_env
from camera_viewer import main as viewer_main
from ptz_controller import PTZController
from rtsp_capture import open_rtsp_capture
from test_ptz import main as ptz_test_main

_BOOT = "_CAMERA_PTZ_RTSP_READY"


def _bootstrap_rtsp_env() -> None:
    if os.environ.get(_BOOT):
        return
    load_runtime_env()
    env = os.environ.copy()
    env[_BOOT] = "1"
    result = subprocess.run([sys.executable, *sys.argv], env=env)
    raise SystemExit(result.returncode)


def smoke_test() -> int:
    """Validate PTZ and video without GUI/keyboard interaction."""
    cfg = load_config()
    print("Testing PTZ...")
    try:
        ctrl = PTZController(cfg.onvif_ptz_url, cfg.username, cfg.password)
        ctrl.send_continuous_move_command(0, 0)
        ctrl.send_stop_command()
        print("PTZ OK")
    except Exception as exc:  # noqa: BLE001
        print(f"PTZ FAILED: {exc}")
        return 1

    print("Testing RTSP video...")
    cap = open_rtsp_capture(cfg.rtsp_url, warmup_frames=40, warmup_timeout=12.0)
    if cap is None:
        print("VIDEO FAILED")
        return 1

    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None or frame.size == 0:
        print("VIDEO FAILED")
        return 1

    print(f"VIDEO OK: frame {frame.shape}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="app", description="Camera PTZ runner")
    parser.add_argument(
        "command",
        choices=("viewer", "ptz-test", "smoke-test"),
        help="viewer: open video + PTZ | ptz-test: validate PTZ endpoint | smoke-test: PTZ + video",
    )
    return parser


def main() -> int:
    _bootstrap_rtsp_env()
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "viewer":
        return viewer_main()
    if args.command == "ptz-test":
        return ptz_test_main()
    if args.command == "smoke-test":
        return smoke_test()
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
