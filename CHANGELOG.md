# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-08-29
### Added
- Interactive startup prompt with configurable timeout (`STARTUP_TIMEOUT=5`) to select between desktop viewer and web server mode.
- Lightweight Flask web server (`app.py server` / `/api/stream`) serving MJPEG stream with adaptive JPEG quality and FPS control.
- Security-first authentication subsystem with bcrypt password hashing, cryptographically signed JWT tokens, `HttpOnly` `SameSite=Strict` session cookies, and sliding-window rate limiting.
- Dual virtual joysticks powered by `nipplejs` with responsive overlay and low-latency REST PTZ control endpoints (`/api/ptz/move`, `/api/ptz/stop`).
- Camera management endpoints and UI controls for stream reconnection, audio monitoring toggle (default muted), fullscreen mode, resolution switching, and auxiliary flashlight/illuminator control.
- Mobile-first responsive dark theme interface with slide-out settings panel and inline SVG icons.
- Automated Chromium kiosk launcher in `--app` mode with memory-limiting flags (`--js-flags="--max-old-space-size=128"`, `--disable-gpu`).
- Hardened multi-stage `Dockerfile` and `docker-compose.yml` with non-root unprivileged execution (`appuser`), read-only root filesystem, dropped Linux capabilities (`cap_drop: ALL`), and 512MB resource limits.
- Project architecture rules, decision records (ADRs 001–005), and Antigravity developer skills in `.agents/`.

## [0.1.0] - 2026-08-28
### Added
- Initial desktop RTSP camera viewer with OpenCV and fullscreen display.
- Raw ONVIF SOAP PTZ client with WS-Security Password Digest auth.
- Directional movement with keyboard hotkeys and Portuguese text-to-speech feedback via espeak.
- Diagnostic scripts for PTZ endpoint probing and smoke tests.
