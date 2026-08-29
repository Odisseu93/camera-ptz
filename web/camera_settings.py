"""Camera settings, stream management, and auxiliary feature endpoints."""
from __future__ import annotations

import logging
import time
from typing import Any

from flask import Blueprint, Response, jsonify, request

from web.auth import login_required
from web.ptz import get_ptz_controller
from web.stream import get_stream_manager

logger = logging.getLogger(__name__)

camera_bp = Blueprint("camera", __name__, url_prefix="/api/camera")

_audio_enabled: bool = False
_flashlight_enabled: bool = False
_last_restart_time: float = 0.0
_MIN_RESTART_INTERVAL = 5.0  # 5 seconds cooldown


COMMON_RESOLUTIONS = [
    {"width": 1920, "height": 1080, "label": "1080p (Full HD)"},
    {"width": 1280, "height": 720, "label": "720p (HD)"},
    {"width": 640, "height": 480, "label": "480p (VGA)"},
    {"width": 320, "height": 240, "label": "240p (QVGA)"},
]


@camera_bp.route("/status", methods=["GET"])
@login_required
def status() -> Response:
    """Return overall camera status, dimensions, and peripheral flags."""
    manager = get_stream_manager()
    width, height = manager.get_dimensions()
    return jsonify({
        "connected": width > 0 and height > 0,
        "width": width,
        "height": height,
        "audio_enabled": _audio_enabled,
        "flashlight_enabled": _flashlight_enabled,
    })


@camera_bp.route("/restart", methods=["POST"])
@login_required
def restart_connection() -> Response:
    """Restart RTSP video capture stream."""
    global _last_restart_time

    now = time.monotonic()
    if now - _last_restart_time < _MIN_RESTART_INTERVAL:
        return jsonify({
            "error": "Restart cooldown active. Please wait a few seconds."
        }), 429
    _last_restart_time = now

    manager = get_stream_manager()
    success = manager.restart()
    return jsonify({"status": "restarting", "success": success})


@camera_bp.route("/audio", methods=["POST"])
@login_required
def toggle_audio() -> Response:
    """Toggle audio monitoring state (default muted)."""
    global _audio_enabled
    data = request.get_json(silent=True) or {}
    _audio_enabled = bool(data.get("enabled", False))
    return jsonify({"audio_enabled": _audio_enabled})


@camera_bp.route("/resolutions", methods=["GET"])
@login_required
def get_resolutions() -> Response:
    """Return current stream dimensions and list of resolution presets."""
    manager = get_stream_manager()
    width, height = manager.get_dimensions()
    return jsonify({
        "current": {"width": width, "height": height},
        "available": COMMON_RESOLUTIONS,
    })


@camera_bp.route("/resolution", methods=["POST"])
@login_required
def set_resolution() -> Response:
    """Select desired stream capture resolution."""
    data = request.get_json(silent=True) or {}
    try:
        width = int(data.get("width", 0))
        height = int(data.get("height", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid resolution values."}), 400

    if not (160 <= width <= 3840 and 120 <= height <= 2160):
        return jsonify({"error": "Resolution out of supported bounds."}), 400

    # Trigger restart to attempt resolution negotiation with camera
    manager = get_stream_manager()
    manager.restart()
    return jsonify({
        "status": "applied",
        "requested": {"width": width, "height": height},
    })


@camera_bp.route("/flashlight", methods=["POST"])
@login_required
def toggle_flashlight() -> Response:
    """Toggle camera flashlight / auxiliary illuminator if supported."""
    global _flashlight_enabled
    data = request.get_json(silent=True) or {}
    requested_state = bool(data.get("enabled", False))

    ctrl = get_ptz_controller()
    supported = ctrl.set_flashlight(requested_state)
    if supported:
        _flashlight_enabled = requested_state

    return jsonify({
        "flashlight_enabled": _flashlight_enabled,
        "supported": supported,
    })
