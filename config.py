"""Load RTSP_URL and derive credentials/host for ONVIF PTZ."""
from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse

from dotenv import load_dotenv


@dataclass(frozen=True)
class CameraConfig:
    rtsp_url: str
    host: str
    username: str
    password: str
    rtsp_port: int
    onvif_ptz_url: str


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def load_config() -> CameraConfig:
    load_dotenv(override=False)

    # Ensure default RTSP transport before any OpenCV usage.
    transport = os.environ.get("RTSP_TRANSPORT", "udp").strip().lower()
    if transport not in {"udp", "tcp"}:
        raise RuntimeError("RTSP_TRANSPORT no .env deve ser 'udp' ou 'tcp'")
    os.environ["RTSP_TRANSPORT"] = transport
    os.environ.setdefault(
        "OPENCV_FFMPEG_CAPTURE_OPTIONS", f"rtsp_transport;{transport}"
    )

    raw = os.environ.get("RTSP_URL")
    if not raw:
        raise RuntimeError(
            "Define RTSP_URL in the .env file, for example:\n"
            "RTSP_URL='rtsp://usuario:senha@192.168.100.2:554/onvif1'"
        )

    rtsp_url = _strip_quotes(raw)
    parsed = urlparse(rtsp_url)
    if parsed.scheme.lower() != "rtsp":
        raise RuntimeError(f"RTSP_URL must start with rtsp:// (received: {parsed.scheme})")
    if not parsed.hostname:
        raise RuntimeError("RTSP_URL has no valid host")
    if not parsed.username or parsed.password is None:
        raise RuntimeError("RTSP_URL must include username and password (rtsp://user:pass@host/...)")

    host = parsed.hostname
    username = parsed.username
    password = parsed.password
    rtsp_port = parsed.port or 554

    # Allow override; otherwise use common Yoosee/ONVIF paths.
    onvif_ptz_url = os.environ.get("ONVIF_PTZ_URL")
    if onvif_ptz_url:
        onvif_ptz_url = _strip_quotes(onvif_ptz_url)
    else:
        onvif_ptz_url = f"http://{host}:5000/onvif/PTZ"

    return CameraConfig(
        rtsp_url=rtsp_url,
        host=host,
        username=username,
        password=password,
        rtsp_port=rtsp_port,
        onvif_ptz_url=onvif_ptz_url,
    )


def load_runtime_env() -> None:
    """Load .env and set RTSP_TRANSPORT/FFMPEG options with UDP default."""
    load_dotenv(override=False)
    transport = os.environ.get("RTSP_TRANSPORT", "udp").strip().lower()
    if transport not in {"udp", "tcp"}:
        raise RuntimeError("RTSP_TRANSPORT in .env must be 'udp' or 'tcp'")
    os.environ["RTSP_TRANSPORT"] = transport
    os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", f"rtsp_transport;{transport}")


def candidate_ptz_urls(host: str) -> list[str]:
    """Common ONVIF PTZ URLs (Yoosee and compatible devices)."""
    return [
        f"http://{host}:5000/onvif/PTZ",
        f"http://{host}:5000/onvif/device_service",
        f"http://{host}:5000/onvif/deviceio_service",
        f"http://{host}:8899/onvif/PTZ",
        f"http://{host}/onvif/PTZ",
        f"http://{host}:80/onvif/PTZ",
        f"http://{host}:8899/onvif/device_service",
        f"http://{host}/onvif/device_service",
        f"http://{host}:8899/onvif/deviceio_service",
        f"http://{host}/onvif/deviceio_service",
        f"http://{host}:80/onvif2/PTZ",
    ]


def load_startup_timeout() -> int:
    load_dotenv(override=False)
    raw = os.environ.get('STARTUP_TIMEOUT', '5').strip()
    try:
        val = int(raw)
        return max(1, val)
    except ValueError:
        return 5


def load_web_port() -> int:
    load_dotenv(override=False)
    raw = os.environ.get('WEB_PORT', '8085').strip()
    try:
        val = int(raw)
        if 1 <= val <= 65535:
            return val
    except ValueError:
        pass
    return 8085
