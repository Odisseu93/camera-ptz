"""Display RTSP with OpenCV and control PTZ with keyboard."""
from __future__ import annotations

import os
import subprocess
import sys
import time

from config import load_config, load_runtime_env
from ptz_controller import PTZController
from rtsp_capture import open_rtsp_capture

WINDOW = "Camera PTZ - arrows move | Q or Esc quits"
UP_KEYS = {2490368, 82, ord("w"), ord("W")}
DOWN_KEYS = {2621440, 84, ord("s"), ord("S")}
LEFT_KEYS = {2424832, 81, ord("a"), ord("A")}
RIGHT_KEYS = {2555904, 83, ord("d"), ord("D")}
_BOOT = "_CAMERA_PTZ_RTSP_READY"


def _bootstrap_rtsp_env() -> None:
    if os.environ.get(_BOOT):
        return
    load_runtime_env()
    env = os.environ.copy()
    env[_BOOT] = "1"
    result = subprocess.run([sys.executable, *sys.argv], env=env)
    raise SystemExit(result.returncode)


def main() -> int:
    _bootstrap_rtsp_env()
    cfg = load_config()
    ptz = PTZController(cfg.onvif_ptz_url, cfg.username, cfg.password)

    print(f"RTSP: {cfg.rtsp_url}")
    print(f"ONVIF PTZ: {cfg.onvif_ptz_url}")
    print(f"FFmpeg: {os.environ.get('OPENCV_FFMPEG_CAPTURE_OPTIONS')}")
    print("Arrows = move | Q or Esc = quit\n")

    cap = open_rtsp_capture(cfg.rtsp_url)
    if cap is None:
        return 1

    import cv2

    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)

    last_move = 0.0
    move_interval = 0.18

    try:
        while True:
            ok, frame = cap.read()
            if not ok or frame is None:
                time.sleep(0.05)
                continue

            cv2.imshow(WINDOW, frame)
            key = cv2.waitKeyEx(1)
            if key in (ord("q"), ord("Q"), 27):
                break

            now = time.monotonic()
            if now - last_move < move_interval:
                continue

            moved = False
            if key in UP_KEYS:
                ptz.up()
                moved = True
            elif key in DOWN_KEYS:
                ptz.down()
                moved = True
            elif key in LEFT_KEYS:
                ptz.left()
                moved = True
            elif key in RIGHT_KEYS:
                ptz.right()
                moved = True

            if moved:
                last_move = now
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    sys.exit(main())
