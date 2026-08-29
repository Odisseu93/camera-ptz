# ADR 004: JWT in HttpOnly Cookies

## Context
The web interface needs authentication when accessed locally or across public networks.

## Decision
Store signed JWT tokens in `HttpOnly`, `SameSite=Strict` cookies rather than browser `localStorage`.

## Consequences
- Prevents Cross-Site Scripting (XSS) scripts from extracting session tokens.
- Automatic cookie inclusion on video stream and API requests.
