# Camera PTZ — Real-time IP Camera Viewer & Web Server

Lightweight, high-performance ONVIF PTZ controller and RTSP streaming server engineered for low-resource hardware (e.g. Intel Core i5 1st Gen, 4GB RAM).

---

## Features

- **Dual-Mode Execution**:
  - **Desktop Mode**: Borderless fullscreen OpenCV window with keyboard navigation (arrows/WASD) and Portuguese text-to-speech feedback via `espeak`.
  - **Web Server Mode**: Lightweight Flask backend serving live MJPEG video with adaptive JPEG quality and mobile-first touch UI.
- **Interactive Startup Prompt**: Starts in desktop mode by default after a 5-second countdown unless web mode is explicitly chosen.
- **Dual Virtual Joysticks**: Low-latency directional pan/tilt and vertical adjustment powered by `nipplejs`.
- **Camera Settings & Controls**:
  - Reconnect / restart stream with automatic retry.
  - Audio toggle (default muted).
  - Fullscreen toggle (default enabled).
  - Dynamic resolution auto-detection and switching.
  - Auxiliary flashlight / torch toggle (on compatible ONVIF cameras).
- **Security-First Architecture**:
  - Password hashing with `bcrypt`.
  - Signed JWT session tokens in `HttpOnly; SameSite=Strict` cookies.
  - Sliding-window in-memory rate limiting against brute-force attacks.
  - Hardened HTTP security headers (CSP, X-Frame-Options DENY, nosniff).
- **Automated Browser Launcher**: Automatically opens Chromium in `--app` mode with memory-limiting flags.
- **Hardened Docker Support**: Multi-stage image (< 180MB), non-root execution (`appuser`), read-only root filesystem, dropped capabilities (`ALL`), and 512MB RAM bounds.

---

## Configuration (`.env`)

Copy `.env.example` to `.env` and fill in your camera parameters:

```env
# Camera Connection
RTSP_URL='rtsp://admin:your_password@192.168.100.2:554/onvif1'
ONVIF_PTZ_URL='http://192.168.100.2:5000/onvif/PTZ'
RTSP_TRANSPORT='udp'

# Server & Startup Settings
STARTUP_TIMEOUT=5
WEB_PORT=8085
WEB_USERNAME='admin'
WEB_PASSWORD='your_web_password'

# Video Stream Tuning
MJPEG_FPS=15
MJPEG_QUALITY=70

# Optional Browser Override
WEB_NO_BROWSER=0
```

---

## Quick Start

### 1. Local Python Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run interactive starter (prompts for mode)
python app.py

# Or start directly in desired mode:
python app.py viewer     # Desktop OpenCV viewer
python app.py server     # Web server on port 8085
python app.py ptz-test   # ONVIF endpoint diagnostic
python app.py smoke-test # Automated headless diagnostic
```

### 2. Docker & Docker Compose

```bash
# Build and start containerized web server
docker compose up -d

# View container logs
docker compose logs -f
```

---

## Architecture & Documentation

- [System Architecture](docs/ARCHITECTURE.md)
- [REST API Reference](docs/api/REST-API.md)
- [Security Policy](docs/SECURITY.md)
- [Architecture Decision Records (ADRs)](docs/adr/)
- [Changelog](CHANGELOG.md)

---

## License

MIT License.
