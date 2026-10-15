# System Architecture

## Overview
`camera-ptz` provides dual-mode monitoring and PTZ control for IP cameras (ONVIF Profile S):
1. **Desktop GUI Mode**: OpenCV fullscreen window with keyboard hotkeys and text-to-speech status announcements.
2. **Web Server Mode**: Lightweight Flask backend serving an MJPEG stream, REST API endpoints, and a mobile-first responsive web client with virtual joysticks.

## Architecture Diagram
```
                     +---------------------------------------+
                     |                app.py                 |
                     |     (CLI & Startup Prompt 5s)         |
                     +-------------------+-------------------+
                                         |
           +-----------------------------+-----------------------------+
           |                                                           |
           v                                                           v
   [ Desktop Mode ]                                            [ Web Server Mode ]
   camera_viewer.py                                            web/server.py
           |                                                           |
           |                                       +-------------------+-------------------+
           |                                       |                   |                   |
           |                                       v                   v                   v
           |                                Auth Middleware      MJPEG Streamer        PTZ & Settings
           |                                (JWT + bcrypt)       (/api/stream)         (/api/ptz, /api/camera)
           |                                       |                   |                   |
           +-----------------------+---------------+-------------------+-------------------+
                                   |                                   |
                                   v                                   v
                         +--------------------+              +-------------------+
                         |  ptz_controller.py |              |  rtsp_capture.py  |
                         |  (ONVIF SOAP HTTP) |              |  (OpenCV FFmpeg)  |
                         +---------+----------+              +---------+---------+
                                   |                                   |
                                   +-----------------+-----------------+
                                                     |
                                                     v
                                               [ IP Camera ]
```

## Core Modules
- `config.py`: Environment variable validation and camera connection settings.
- `ptz_controller.py`: ONVIF SOAP client with WS-Security Password Digest auth.
- `rtsp_capture.py`: Video capture initialization and warmup validation.
- `camera_viewer.py`: Desktop OpenCV viewer with keyboard mapping.
- `web/server.py`: Flask application factory, security headers, and route registration.
- `web/auth.py`: JWT token generation, verification, and bcrypt password hashing.
- `web/stream.py`: Thread-safe MJPEG frame generator.
