---
name: web-architecture
description: Specifications for the lightweight Flask web server, auth middleware, and responsive UI.
---

# Web Architecture Guide

## Backend Architecture
- Lightweight Flask server running with bounded thread pool.
- Modular blueprints: Auth (`/api/auth`), Stream (`/api/stream`), PTZ (`/api/ptz`), Camera Settings (`/api/camera`).
- Security middleware validates JWT from `HttpOnly` cookie for protected routes.
- Low-overhead in-memory rate limiting.

## Frontend Architecture
- Zero-framework vanilla HTML5, CSS3, and JavaScript.
- Mobile-first responsive layout with viewport meta tags.
- Dual virtual joysticks powered by lightweight `nipplejs` for low-latency PTZ control.
- Dark theme optimized for camera monitoring.
