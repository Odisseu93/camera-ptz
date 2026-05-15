"""Open RTSP stream with OpenCV/FFmpeg."""
from __future__ import annotations

import os
import time


def open_rtsp_capture(url: str, warmup_frames: int = 50, warmup_timeout: float = 15.0):
    """Return cv2.VideoCapture with valid frames or None."""
    ffmpeg_opts = os.environ.get("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;udp")
    print(f"RTSP FFmpeg: {ffmpeg_opts}")

    import cv2

    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    deadline = time.monotonic() + warmup_timeout
    attempts = 0
    while attempts < warmup_frames and time.monotonic() < deadline:
        ok, frame = cap.read()
        attempts += 1
        if ok and frame is not None and frame.size > 0:
            print(f"Stream OK - frame {frame.shape} (attempt {attempts})")
            return cap
        time.sleep(0.2)

    cap.release()

    print(
        f"Failure: no frames in {attempts} attempts.\n"
        "Check RTSP_URL and credentials in the .env file."
    )
    return None
