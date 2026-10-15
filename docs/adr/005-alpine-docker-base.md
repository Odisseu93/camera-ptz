# ADR 005: Lightweight Alpine / Slim Base for Docker

## Context
Containerized deployments should be minimal in size and resource usage.

## Decision
Use `python:3.12-slim-bookworm` or `python:3.12-alpine` with `opencv-python-headless` for headless container execution.

## Consequences
- Image size reduced to < 180MB.
- Strips unused X11/GUI libraries from container runtime.
