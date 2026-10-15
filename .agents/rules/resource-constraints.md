# Resource Optimization & Hardware Limits

- Target Host: Intel Core i5 1st Gen, 4GB RAM.
- Process Memory: Target RSS <= 300MB in web server mode, <= 150MB in desktop viewer mode.
- Video Streaming: Encode MJPEG dynamically with bounded FPS (default 15) and configurable JPEG quality (default 70).
- Single Capture Source: Share a single `cv2.VideoCapture` pipeline across connected clients to prevent duplicate RTSP decoding.
- Web Client: Use lightweight, native Vanilla JS and standard browser APIs. Avoid heavy client-side frameworks.
- Browser Kiosk: Launch Chromium in `--app` mode with memory-limiting flags (`--js-flags="--max-old-space-size=128"`, `--disable-extensions`, `--disable-gpu`).
