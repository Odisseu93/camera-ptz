"""Thread-safe video capture and MJPEG frame distribution."""
from __future__ import annotations

import logging
import os
import threading
import time
from typing import Generator

import cv2

from config import load_config
from rtsp_capture import open_rtsp_capture

logger = logging.getLogger(__name__)


def _load_stream_parameters() -> tuple[int, int]:
    raw_fps = os.environ.get("MJPEG_FPS", "15").strip()
    raw_quality = os.environ.get("MJPEG_QUALITY", "70").strip()
    try:
        fps = max(1, min(30, int(raw_fps)))
    except ValueError:
        fps = 15
    try:
        quality = max(30, min(95, int(raw_quality)))
    except ValueError:
        quality = 70
    return fps, quality


class VideoStreamManager:
    """Manages a single RTSP capture thread and encodes MJPEG frames."""

    def __init__(self) -> None:
        self.fps, self.jpeg_quality = _load_stream_parameters()
        self._frame_interval = 1.0 / self.fps
        self._lock = threading.Lock()
        self._capture: cv2.VideoCapture | None = None
        self._running = False
        self._worker_thread: threading.Thread | None = None
        self._latest_jpeg: bytes | None = None
        self._width = 0
        self._height = 0
        self._last_frame_time = 0.0

    def start(self) -> None:
        """Start the background RTSP acquisition thread."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._worker_thread = threading.Thread(
                target=self._capture_loop, daemon=True, name="RTSPCaptureWorker"
            )
            self._worker_thread.start()

    def stop(self) -> None:
        """Stop background worker and release video capture."""
        with self._lock:
            self._running = False
            if self._capture is not None:
                self._capture.release()
                self._capture = None

    def restart(self) -> bool:
        """Force restart of the underlying capture stream."""
        logger.info("Restarting RTSP capture stream...")
        self.stop()
        time.sleep(0.5)
        self.start()
        return True

    def get_dimensions(self) -> tuple[int, int]:
        """Return current frame width and height."""
        with self._lock:
            return self._width, self._height

    def get_latest_jpeg(self) -> bytes | None:
        """Return the most recently encoded JPEG frame."""
        with self._lock:
            return self._latest_jpeg

    def generate_mjpeg_stream(self) -> Generator[bytes, None, None]:
        """Yield multipart MJPEG stream chunks bounded by FPS."""
        boundary = b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"
        while self._running:
            jpeg = self.get_latest_jpeg()
            if jpeg is not None:
                yield boundary + jpeg + b"\r\n"
            time.sleep(self._frame_interval)

    def _capture_loop(self) -> None:
        cfg = load_config()
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.jpeg_quality]

        while self._running:
            logger.info("Opening RTSP stream from %s", cfg.rtsp_url)
            cap = open_rtsp_capture(cfg.rtsp_url, warmup_frames=30, warmup_timeout=10.0)
            if cap is None:
                logger.warning("Failed to open RTSP stream. Retrying in 3 seconds...")
                time.sleep(3.0)
                continue

            with self._lock:
                self._capture = cap
                self._width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self._height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            consecutive_failures = 0
            while self._running:
                start_time = time.monotonic()
                ok, frame = cap.read()
                if not ok or frame is None or frame.size == 0:
                    consecutive_failures += 1
                    if consecutive_failures > 20:
                        logger.warning("Too many consecutive read failures. Reconnecting...")
                        break
                    time.sleep(0.05)
                    continue

                consecutive_failures = 0
                success, encoded_img = cv2.imencode(".jpg", frame, encode_param)
                if success:
                    jpeg_bytes = encoded_img.tobytes()
                    with self._lock:
                        self._latest_jpeg = jpeg_bytes
                        self._last_frame_time = time.monotonic()

                elapsed = time.monotonic() - start_time
                sleep_duration = self._frame_interval - elapsed
                if sleep_duration > 0.002:
                    time.sleep(sleep_duration)

            with self._lock:
                if self._capture is not None:
                    self._capture.release()
                    self._capture = None


_global_stream_manager: VideoStreamManager | None = None


def get_stream_manager() -> VideoStreamManager:
    """Return singleton video stream manager."""
    global _global_stream_manager
    if _global_stream_manager is None:
        _global_stream_manager = VideoStreamManager()
        _global_stream_manager.start()
    return _global_stream_manager
