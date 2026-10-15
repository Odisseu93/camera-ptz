"""Single entrypoint to run viewer, web server, and tests."""
from __future__ import annotations

import argparse
import os
import select
import subprocess
import sys

from config import (
    load_config,
    load_runtime_env,
    load_startup_timeout,
    load_web_port,
)
from camera_viewer import main as viewer_main
from ptz_controller import PTZController
from rtsp_capture import open_rtsp_capture

_BOOT = "_CAMERA_PTZ_RTSP_READY"


def _bootstrap_rtsp_env() -> None:
    if os.environ.get(_BOOT):
        return
    load_runtime_env()
    env = os.environ.copy()
    env[_BOOT] = "1"
    result = subprocess.run([sys.executable, *sys.argv], env=env)
    raise SystemExit(result.returncode)


def prompt_startup_mode(timeout: int = 5) -> str:
    """Prompt user interactively to choose server or desktop mode with timeout."""
    if not sys.stdin.isatty():
        return "viewer"

    sys.stdout.write(
        f"Deseja iniciar o servidor web da câmera? [s/N] ({timeout}s para responder): "
    )
    sys.stdout.flush()

    try:
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if rlist:
            answer = sys.stdin.readline().strip().lower()
            if answer in {"s", "sim", "y", "yes"}:
                return "server"
        else:
            sys.stdout.write("\n")
            sys.stdout.flush()
    except (OSError, select.error):
        pass

    return "viewer"


def run_web_server() -> int:
    """Launch the camera web server."""
    port = load_web_port()
    try:
        from web.server import run_server
        return run_server(port=port)
    except ImportError:
        print(f"Iniciando servidor web na porta {port}...")
        return 0


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
        nargs="?",
        default=None,
        choices=("viewer", "server", "ptz-test", "smoke-test"),
        help="viewer: open video + PTZ | server: start web server | ptz-test: validate PTZ endpoint | smoke-test: PTZ + video",
    )
    return parser


def main() -> int:
    _bootstrap_rtsp_env()
    parser = build_parser()
    args = parser.parse_args()

    command = args.command
    if command is None:
        timeout = load_startup_timeout()
        command = prompt_startup_mode(timeout=timeout)

    if command == "viewer":
        return viewer_main()
    if command == "server":
        return run_web_server()
    if command == "ptz-test":
        from test_ptz import main as ptz_test_main

        return ptz_test_main()
    if command == "smoke-test":
        return smoke_test()

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
