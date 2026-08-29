---
name: rtsp-stream
description: Guidelines for RTSP video capture, OpenCV FFmpeg backend configuration, and frame distribution.
---

# RTSP Stream Guide

## Environment Initialization
OpenCV reads FFmpeg transport options during backend initialization. The project uses a sentinel environment variable `_CAMERA_PTZ_RTSP_READY` to ensure `OPENCV_FFMPEG_CAPTURE_OPTIONS=rtsp_transport;udp` (or tcp) is exported before `cv2` is imported.

## Capture Pipeline
- Capture source: `cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)`.
- Warmup polling loop discards initial corrupt/incomplete frames.
- Frame generator for web MJPEG streaming encodes frames as JPEG (`cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])`).
- Synchronized frame reading using a single background thread and thread-safe lock prevents concurrent decode conflicts.
