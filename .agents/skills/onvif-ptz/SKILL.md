---
name: onvif-ptz
description: Guidelines and specifications for ONVIF SOAP PTZ continuous movement and camera control commands in the camera-ptz project.
---

# ONVIF PTZ Protocol Guide

## Overview
This project communicates with ONVIF Profile S compatible cameras (such as Yoosee IP cameras) using raw HTTP/SOAP XML envelopes over standard `requests.Session` without heavyweight external SOAP frameworks.

## Key Mechanisms
1. **WS-Security Password Digest**:
   - `Nonce`: 16 random bytes (Base64 encoded).
   - `Created`: UTC timestamp formatted as `YYYY-MM-DDTHH:MM:SS.mmmZ`.
   - `PasswordDigest`: `Base64(SHA1(Raw_Nonce + Created_Bytes + Password_Bytes))`.
2. **ContinuousMove & Stop Pattern**:
   - Camera movement is executed via `ContinuousMove(x, y)` followed by `Stop()` after a duration or on touch release.
   - Profile token defaults to `IPCProfilesToken0`.
   - Velocity values are clamped and scaled.
   - Fire-and-forget read timeout (`timeout=(3, 0.001)`) prevents blocking the main event loop.
