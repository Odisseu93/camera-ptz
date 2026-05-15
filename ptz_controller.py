"""
ONVIF PTZ control for Yoosee cameras (minimal SOAP, requests only).
Based on: https://gist.github.com/raspiduino/549803f87bc593c726e55d79eb987b2c
"""
from __future__ import annotations

import base64
import hashlib
import os
from datetime import datetime, timezone

import requests


def generate_soap_header_values(plain_password: str) -> dict[str, str]:
    nonce_bytes = os.urandom(16)
    nonce_b64 = base64.b64encode(nonce_bytes).decode("utf-8")

    now_utc = datetime.now(timezone.utc)
    created_timestamp = now_utc.isoformat(timespec="milliseconds").replace("+00:00", "Z")

    created_bytes = created_timestamp.encode("utf-8")
    password_bytes = plain_password.encode("utf-8")
    concatenated_bytes = nonce_bytes + created_bytes + password_bytes
    password_digest_b64 = base64.b64encode(
        hashlib.sha1(concatenated_bytes).digest()
    ).decode("utf-8")

    return {
        "password_digest": password_digest_b64,
        "nonce": nonce_b64,
        "created": created_timestamp,
    }


class PTZController:
    PROFILE_TOKEN = "IPCProfilesToken0"
    VELOCITY = 0.5

    def __init__(self, url: str, username: str, password: str) -> None:
        self.onvif_ptz_url = url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.trust_env = False

    def send_continuous_move_command(self, x: float, y: float) -> None:
        header_values = generate_soap_header_values(self.password)
        headers = {
            "Content-Type": (
                'application/soap+xml; charset=utf-8; '
                'action="http://www.onvif.org/ver20/ptz/wsdl/ContinuousMove"'
            ),
            "Connection": "Close",
        }
        data = (
            '<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">'
            "<s:Header>"
            '<Security s:mustUnderstand="1" '
            'xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">'
            "<UsernameToken>"
            f"<Username>{self.username}</Username>"
            '<Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">'
            f'{header_values["password_digest"]}</Password>'
            '<Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">'
            f'{header_values["nonce"]}</Nonce>'
            '<Created xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">'
            f'{header_values["created"]}</Created>'
            "</UsernameToken></Security></s:Header>"
            '<s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
            '<ContinuousMove xmlns="http://www.onvif.org/ver20/ptz/wsdl">'
            f"<ProfileToken>{self.PROFILE_TOKEN}</ProfileToken>"
            "<Velocity>"
            f'<PanTilt x="{x}" y="{y}" xmlns="http://www.onvif.org/ver10/schema"/>'
            "</Velocity></ContinuousMove></s:Body></s:Envelope>"
        )

        try:
            self.session.post(
                self.onvif_ptz_url,
                headers=headers,
                data=data,
                timeout=(3, 0.001),
            )
        except requests.exceptions.ReadTimeout:
            pass

    def send_stop_command(self) -> bool:
        header_values = generate_soap_header_values(self.password)
        headers = {
            "Content-Type": (
                'application/soap+xml; charset=utf-8; '
                'action="http://www.onvif.org/ver20/ptz/wsdl/Stop"'
            ),
            "Connection": "Close",
        }
        data = (
            '<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">'
            "<s:Header>"
            '<Security s:mustUnderstand="1" '
            'xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">'
            "<UsernameToken>"
            f"<Username>{self.username}</Username>"
            '<Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordDigest">'
            f'{header_values["password_digest"]}</Password>'
            '<Nonce EncodingType="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary">'
            f'{header_values["nonce"]}</Nonce>'
            '<Created xmlns="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">'
            f'{header_values["created"]}</Created>'
            "</UsernameToken></Security></s:Header>"
            '<s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
            '<Stop xmlns="http://www.onvif.org/ver20/ptz/wsdl">'
            f"<ProfileToken>{self.PROFILE_TOKEN}</ProfileToken>"
            "<PanTilt>true</PanTilt><Zoom>false</Zoom>"
            "</Stop></s:Body></s:Envelope>"
        )

        try:
            response = self.session.post(
                self.onvif_ptz_url, headers=headers, data=data, timeout=5
            )
            return response.ok
        except requests.RequestException as exc:
            msg = str(exc)
            if "Remote end closed connection without response" in msg:
                return True
            raise

    def continuous_move(self, x: float, y: float) -> None:
        self.send_continuous_move_command(x, y)
        self.send_stop_command()

    def up(self) -> None:
        self.continuous_move(0, self.VELOCITY)

    def down(self) -> None:
        self.continuous_move(0, -self.VELOCITY)

    def left(self) -> None:
        self.continuous_move(-self.VELOCITY, 0)

    def right(self) -> None:
        self.continuous_move(self.VELOCITY, 0)
