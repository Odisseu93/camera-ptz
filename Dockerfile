# Stage 1: Build stage with compiler toolchain
FROM python:3.12-slim-bookworm AS builder

WORKDIR /build

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libglib2.0-0 \
    libglib2.0-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Replace standard opencv-python with lightweight headless version for containers
RUN sed -i 's/opencv-python>=/opencv-python-headless>=/' requirements.txt && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Minimal hardened runtime stage
FROM python:3.12-slim-bookworm AS runtime

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/install/bin:${PATH}" \
    PYTHONPATH="/install/lib/python3.12/site-packages:${PYTHONPATH}"

# Install minimal runtime libraries required by OpenCV headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create unprivileged non-root user
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /sbin/nologin -d /app appuser

# Copy installed packages from builder
COPY --from=builder /install /install

# Copy application source code
COPY --chown=appuser:appgroup app.py config.py camera_viewer.py test_ptz.py ptz_controller.py rtsp_capture.py ./
COPY --chown=appuser:appgroup web/ ./web/

USER appuser:appgroup

EXPOSE 8085

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python3 -c "import os, urllib.request; port = os.environ.get('WEB_PORT', '8085'); urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health')" || exit 1

ENTRYPOINT ["python3", "app.py", "server"]
