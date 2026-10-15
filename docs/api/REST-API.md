# REST API Reference

## Authentication
- `POST /api/auth/login`: Authenticate with username and password. Returns JWT in `HttpOnly` cookie.
  - Body: `{"username": "...", "password": "..."}`
- `POST /api/auth/logout`: Clear authentication cookie.
- `GET /api/auth/status`: Check current session authentication status.

## Video Stream
- `GET /api/stream`: Multipart MJPEG video stream (`multipart/x-mixed-replace; boundary=frame`).

## PTZ Control
- `POST /api/ptz/move`: Continuous directional move command.
  - Body: `{"x": float, "y": float}` (values clamped to [-100.0, 100.0])
- `POST /api/ptz/stop`: Send stop command to halt active pan/tilt movements.

## Camera Settings
- `GET /api/camera/status`: Returns camera connection and stream status.
- `POST /api/camera/restart`: Force reconnection to the RTSP camera stream.
- `GET /api/camera/resolutions`: Get current and candidate stream resolutions.
- `POST /api/camera/resolution`: Set stream resolution.
  - Body: `{"width": int, "height": int}`
- `POST /api/camera/flashlight`: Toggle camera auxiliary illuminator/flashlight (if supported).
  - Body: `{"enabled": bool}`
- `POST /api/camera/audio`: Toggle audio monitoring flag.
  - Body: `{"enabled": bool}`

## Health
- `GET /api/health`: Healthcheck endpoint returning HTTP 200 OK.
