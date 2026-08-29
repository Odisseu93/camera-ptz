# ADR 002: REST API Commands over WebSocket for PTZ

## Context
PTZ commands are discrete directional movements emitted periodically (every 50-100ms during touch/drag) and on release.

## Decision
Use standard HTTP REST endpoints with client-side fetch debouncing rather than a continuous WebSocket connection.

## Consequences
- Eliminates heavy WebSocket dependencies (`flask-socketio`, `gevent`, `eventlet`), saving ~40-50MB RAM.
- Stateless HTTP requests are easier to authenticate, cache-control, and proxy across tunnels (e.g. Cloudflare Tunnels).
