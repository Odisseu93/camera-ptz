"""Authentication, JWT session management, and rate limiting."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from functools import wraps
import logging
import os
import secrets
import time
from typing import Any, Callable

import bcrypt
from flask import Blueprint, Response, jsonify, make_response, redirect, request
import jwt

from config import load_config

logger = logging.getLogger(__name__)

COOKIE_NAME = "camera_ptz_session"


class RateLimiter:
    """Sliding-window in-memory rate limiter per IP address."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 60) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._records: dict[str, list[float]] = {}
        self._request_counter = 0

    def is_allowed(self, ip: str) -> bool:
        now = time.monotonic()
        self._request_counter += 1
        if self._request_counter % 100 == 0:
            self._cleanup(now)

        attempts = self._records.setdefault(ip, [])
        valid_attempts = [t for t in attempts if now - t < self.window_seconds]
        self._records[ip] = valid_attempts

        if len(valid_attempts) >= self.max_attempts:
            return False

        valid_attempts.append(now)
        return True

    def _cleanup(self, now: float) -> None:
        stale_ips = [
            ip for ip, timestamps in self._records.items()
            if not timestamps or now - timestamps[-1] >= self.window_seconds
        ]
        for ip in stale_ips:
            del self._records[ip]


class AuthManager:
    """Handles credentials verification, JWT generation, and token validation."""

    def __init__(self) -> None:
        self.jwt_secret = secrets.token_hex(32)
        self.expiry_minutes = self._load_expiry_minutes()
        self.username, self.password_hash = self._initialize_credentials()
        self.rate_limiter = RateLimiter(max_attempts=5, window_seconds=60)

    @staticmethod
    def _load_expiry_minutes() -> int:
        raw = os.environ.get("JWT_EXPIRY_MINUTES", "30").strip()
        try:
            val = int(raw)
            return max(5, min(1440, val))
        except ValueError:
            return 30

    @staticmethod
    def _initialize_credentials() -> tuple[str, bytes]:
        user = os.environ.get("WEB_USERNAME")
        raw_password = os.environ.get("WEB_PASSWORD")

        if not user or not raw_password:
            try:
                cfg = load_config()
                user = user or cfg.username
                raw_password = raw_password or cfg.password
            except Exception:  # noqa: BLE001
                user = user or "admin"
                raw_password = raw_password or "admin"

        pw_bytes = raw_password.encode("utf-8")
        pw_hash = bcrypt.hashpw(pw_bytes, bcrypt.gensalt(rounds=12))
        return user, pw_hash

    def verify_password(self, username: str, password: str) -> bool:
        if len(password) > 128 or len(username) > 128:
            return False
        if not secrets.compare_digest(username, self.username):
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password_hash)

    def create_token(self) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": self.username,
            "iat": now,
            "exp": now + timedelta(minutes=self.expiry_minutes),
        }
        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def verify_token(self, token: str) -> dict[str, Any] | None:
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return payload
        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
            return None


auth_manager = AuthManager()
auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def get_authenticated_user() -> str | None:
    """Extract and verify JWT from request cookie or Authorization header."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()

    if not token:
        return None

    payload = auth_manager.verify_token(token)
    if payload and "sub" in payload:
        return str(payload["sub"])
    return None


def login_required(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator guarding views and API routes with authentication checks."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        user = get_authenticated_user()
        if not user:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Unauthorized"}), 401
            return redirect("/login")
        return func(*args, **kwargs)
    return wrapper


@auth_bp.route("/login", methods=["POST"])
def api_login() -> Response:
    client_ip = request.remote_addr or "unknown"
    if not auth_manager.rate_limiter.is_allowed(client_ip):
        return jsonify({"error": "Too many failed attempts. Try again in 1 minute."}), 429

    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    if not username or not password:
        return jsonify({"error": "Username and password required."}), 400

    if not auth_manager.verify_password(username, password):
        return jsonify({"error": "Invalid credentials."}), 401

    token = auth_manager.create_token()
    response = make_response(jsonify({"status": "ok", "user": username}))
    is_secure = request.is_secure or request.headers.get("X-Forwarded-Proto") == "https"
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=auth_manager.expiry_minutes * 60,
        httponly=True,
        samesite="Strict",
        secure=is_secure,
        path="/",
    )
    return response


@auth_bp.route("/logout", methods=["POST"])
def api_logout() -> Response:
    response = make_response(jsonify({"status": "logged_out"}))
    response.set_cookie(
        COOKIE_NAME,
        "",
        max_age=0,
        httponly=True,
        samesite="Strict",
        path="/",
    )
    return response


@auth_bp.route("/status", methods=["GET"])
def api_status() -> Response:
    user = get_authenticated_user()
    if user:
        return jsonify({"authenticated": True, "username": user})
    return jsonify({"authenticated": False, "username": None})
