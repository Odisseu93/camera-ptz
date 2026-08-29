"""REST API endpoints for ONVIF PTZ camera movement."""
from __future__ import annotations

import logging
import time
from typing import Any

from flask import Blueprint, Response, jsonify, request

from config import load_config
from ptz_controller import PTZController
from web.auth import login_required

logger = logging.getLogger(__name__)

ptz_bp = Blueprint("ptz", __name__, url_prefix="/api/ptz")

_controller: PTZController | None = None
_last_command_time: float = 0.0
_MIN_COMMAND_INTERVAL = 0.04  # 40ms minimum interval (~25 requests/sec maximum)


def get_ptz_controller() -> PTZController:
    """Return singleton PTZ controller instance."""
    global _controller
    if _controller is None:
        cfg = load_config()
        _controller = PTZController(cfg.onvif_ptz_url, cfg.username, cfg.password)
    return _controller


def _clamp(value: float, min_val: float, max_val: float) -> float:
    return max(min_val, min(max_val, value))


@ptz_bp.route("/move", methods=["POST"])
@login_required
def move() -> Response:
    """Execute continuous movement command with validated velocities."""
    global _last_command_time

    now = time.monotonic()
    if now - _last_command_time < _MIN_COMMAND_INTERVAL:
        return jsonify({"status": "rate_limited"}), 429
    _last_command_time = now

    data = request.get_json(silent=True) or {}
    try:
        raw_x = float(data.get("x", 0.0))
        raw_y = float(data.get("y", 0.0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid coordinate format."}), 400

    # Bounds check: inputs expected in range [-100.0, 100.0] or [-1.0, 1.0]
    # Normalize to [-1.0, 1.0] if larger scale passed
    if abs(raw_x) > 1.0 or abs(raw_y) > 1.0:
        raw_x = _clamp(raw_x / 100.0, -1.0, 1.0)
        raw_y = _clamp(raw_y / 100.0, -1.0, 1.0)

    # Scale by controller velocity
    ctrl = get_ptz_controller()
    scaled_x = round(raw_x * ctrl.VELOCITY, 2)
    scaled_y = round(raw_y * ctrl.VELOCITY, 2)

    try:
        ctrl.send_continuous_move_command(scaled_x, scaled_y)
        return jsonify({"status": "ok", "x": scaled_x, "y": scaled_y})
    except Exception as exc:  # noqa: BLE001
        logger.warning("PTZ move failed: %s", exc)
        return jsonify({"error": "Failed to send PTZ command."}), 502


@ptz_bp.route("/stop", methods=["POST"])
@login_required
def stop() -> Response:
    """Halt active continuous camera movements."""
    try:
        ctrl = get_ptz_controller()
        success = ctrl.send_stop_command()
        return jsonify({"status": "stopped", "success": success})
    except Exception as exc:  # noqa: BLE001
        logger.warning("PTZ stop failed: %s", exc)
        return jsonify({"error": "Failed to send stop command."}), 502
