"""Flask web server application, security middleware, and route registration."""
from __future__ import annotations

import logging
import os
from typing import Any

from flask import Flask, Response, jsonify, send_from_directory

from web.auth import auth_bp, login_required
from web.browser import launch_browser_in_background
from web.ptz import ptz_bp
from web.stream import get_stream_manager

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    """Create and configure the Flask web application."""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    app = Flask(__name__, static_folder=static_dir, static_url_path="/static")
    app.config["SECRET_KEY"] = os.urandom(32)

    app.register_blueprint(auth_bp)
    app.register_blueprint(ptz_bp)

    @app.after_request
    def set_security_headers(response: Response) -> Response:
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "img-src 'self' data: blob:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com; "
            "connect-src 'self';"
        )
        return response

    @app.route("/login", methods=["GET"])
    def login_page() -> Any:
        return send_from_directory(static_dir, "login.html")

    @app.route("/", methods=["GET"])
    @login_required
    def index() -> Any:
        return send_from_directory(static_dir, "index.html")

    @app.route("/api/health", methods=["GET"])
    def health() -> Any:
        return jsonify({"status": "ok"})

    @app.route("/api/stream", methods=["GET"])
    @login_required
    def video_stream() -> Response:
        manager = get_stream_manager()
        return Response(
            manager.generate_mjpeg_stream(),
            mimetype="multipart/x-mixed-replace; boundary=frame",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )

    return app


def run_server(port: int = 8085, host: str = "0.0.0.0") -> int:
    """Run the Flask web server and launch browser kiosk."""
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    )
    app = create_app()
    url = f"http://localhost:{port}"
    print(f"Servidor web da câmera iniciado em {url}")

    launch_browser_in_background(url)

    app.run(host=host, port=port, threaded=True, debug=False)
    return 0
