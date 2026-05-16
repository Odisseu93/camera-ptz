# camera-ptz

Python project to view an RTSP stream and control camera PTZ (ONVIF) from the keyboard.

## Project Structure

- `app.py`: main CLI entrypoint (`viewer`, `ptz-test`, `smoke-test`).
- `camera_viewer.py`: opens OpenCV window, shows video, and maps keyboard to PTZ actions.
- `config.py`: loads `.env`, validates config, parses RTSP URL, and builds camera config object.
- `rtsp_capture.py`: opens RTSP stream and waits for a valid frame.
- `ptz_controller.py`: ONVIF SOAP PTZ client (continuous move + stop).
- `test_ptz.py`: probes common ONVIF PTZ endpoints and helps select a working one.
- `requirements.txt`: Python dependencies.
- `.env`: local runtime configuration (not committed).

## Python Version

Recommended:

- Python `3.11` or `3.12` (best compatibility for camera/OpenCV workflows).

Current code also runs with Python `3.14`, but OpenCV/codec behavior can vary by build.

## Virtual Environment Setup

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
```

## Environment Variables (`.env`)

Create a `.env` file in the project root.

Required:

- `RTSP_URL`: full RTSP URL including user and password.

Optional:

- `ONVIF_PTZ_URL`: ONVIF PTZ endpoint URL. Default: `http://<camera_host>:5000/onvif/PTZ`
- `RTSP_TRANSPORT`: `udp` or `tcp`. Default: `udp`
- `OPENCV_FFMPEG_CAPTURE_OPTIONS`: usually auto-filled from `RTSP_TRANSPORT` (`rtsp_transport;udp` or `rtsp_transport;tcp`).

Example:

```env
RTSP_URL='rtsp://admin:your_password@192.168.100.2:554/onvif1'
ONVIF_PTZ_URL='http://192.168.100.2:5000/onvif/PTZ'
RTSP_TRANSPORT='udp'
```

## Run Commands

From activated virtual environment:

```bash
python app.py viewer
python app.py ptz-test
python app.py smoke-test
```

What each command does:

- `viewer`: opens video window and enables PTZ control with arrow keys (also `W/A/S/D`).
- `ptz-test`: tests common ONVIF endpoints and prints the first working endpoint.
- `smoke-test`: non-interactive PTZ + video validation.

## Keyboard Controls

Inside viewer window:

- Arrow keys: PTZ move
- `W/A/S/D`: PTZ move alternative
- `Q` or `Esc`: quit

## Known Issue: HEVC Decoding (`PPS id out of range`)

Symptom:

- RTSP connection is reachable, but OpenCV logs errors like:
  - `hevc ... PPS id out of range: 0`
- `smoke-test` or `viewer` fails to get valid frames.

What this usually means:

- Stream codec/profile from camera is not being decoded correctly by the local OpenCV/FFmpeg build.

Practical mitigations:

1. In camera settings, switch stream codec to `H.264` (preferred) instead of `H.265/HEVC`.
2. Try camera substream (often lower bitrate and easier decode).
3. Keep `RTSP_TRANSPORT='udp'` for Yoosee setups (or test `tcp` if needed).
4. Test with Python `3.11`/`3.12` + fresh venv.
5. Validate the same RTSP URL in VLC first; if VLC fails too, issue is likely camera/path/config.

## PTZ Network Note

`ptz_controller.py` uses `requests.Session(trust_env=False)` so local PTZ calls are not hijacked by system proxy settings.

## Security Notes

- `.env` is gitignored.
- Do not commit camera credentials.
- Rotate camera password if credentials were ever exposed.
