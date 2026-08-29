# ADR 001: Selection of Flask over FastAPI

## Context
The host machine has 4 GB RAM and an Intel Core i5 (1st Gen) CPU. The application requires serving an MJPEG stream, static assets, and a few REST endpoints.

## Decision
Use standard Flask instead of FastAPI/Uvicorn/AsyncIO.

## Consequences
- Lower memory footprint (Flask baseline RSS is ~15-20MB vs ~45-60MB for FastAPI/uvicorn).
- Simple multipart/x-mixed-replace generator for MJPEG streaming.
- Avoids async event loop overhead in a CPU-constrained environment.
