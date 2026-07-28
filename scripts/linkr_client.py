#!/usr/bin/env python3
"""
Linkr Python client wrapper.
Provides a friendly API for remote control of target machines.

Environment variables:
    Linkr_IP: Linkr device IP (required, e.g. 192.168.x.x)
    Linkr_TOKEN: Linkr access token (required)

Example:
    from linkr_client import LinkrClient

    client = LinkrClient()

    client.screenshot("desktop.jpeg")

    client.text("This is a long text that will be automatically split into chunks...")

    client.key_combo("MetaLeft", "KeyR")

    client.click(0.5, 0.5)
"""

import os
import time
import requests
from typing import List, Union, Optional
from dataclasses import dataclass

DEFAULT_LINKR_PORT = 80


def resolve_linkr_url(ip: Optional[str] = None, port: int = DEFAULT_LINKR_PORT) -> str:
    resolved_ip = ip or os.getenv("Linkr_IP")
    if not resolved_ip:
        raise ValueError("Missing Linkr_IP. Set the environment variable Linkr_IP or pass ip to LinkrClient.")
    return f"http://{resolved_ip}:{port}"


@dataclass
class Point:
    """Coordinate point."""
    x: float
    y: float


class LinkrClient:
    """Linkr HTTP API client."""

    KEY_WIN = "MetaLeft"
    KEY_CTRL = "ControlLeft"
    KEY_ALT = "AltLeft"
    KEY_SHIFT = "ShiftLeft"
    KEY_ENTER = "Enter"
    KEY_ESC = "Escape"
    KEY_TAB = "Tab"
    KEY_SPACE = "Space"

    TEXT_CHUNK_SIZE = 30
    TEXT_DELAY_MS = 1000
    MAX_TEXT_LENGTH = 1024

    def __init__(self, ip: Optional[str] = None, token: Optional[str] = None):
        """
        Initialize the client.

        Args:
            ip: Linkr device IP, defaults to env var Linkr_IP.
            token: Linkr access token, defaults to env var Linkr_TOKEN.
        """
        self.url = resolve_linkr_url(ip=ip)
        self.token = token or os.getenv("Linkr_TOKEN")
        self.session = requests.Session()
        if not self.token:
            raise ValueError(
                "Missing Linkr_TOKEN. Set the environment variable Linkr_TOKEN or pass token to LinkrClient."
            )
        self.session.headers.update({"Authorization": f"token {self.token}"})

    @staticmethod
    def _validate_unit_interval(name: str, value: float) -> None:
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be in [0.0, 1.0], got: {value}")

    @staticmethod
    def _validate_wheel(name: str, value: int) -> None:
        if not -20 <= value <= 20:
            raise ValueError(f"{name} must be in [-20, 20], got: {value}")

    @classmethod
    def _validate_text_content(cls, content: str) -> None:
        if len(content) > cls.MAX_TEXT_LENGTH:
            raise ValueError(f"text event max length is {cls.MAX_TEXT_LENGTH}, got: {len(content)}")
        for ch in content:
            code = ord(ch)
            if code in (9, 10):
                continue
            if not 32 <= code <= 126:
                raise ValueError(
                    "text event only supports ASCII control chars Tab/Enter and printable chars 32~126."
                )

    def _request(self, method: str, endpoint: str, timeout: int = 30, **kwargs) -> requests.Response:
        url = f"{self.url}{endpoint}"
        response = self.session.request(method, url, timeout=timeout, **kwargs)
        response.raise_for_status()
        return response

    def _request_json(self, method: str, endpoint: str, timeout: int = 30, **kwargs) -> dict:
        response = self._request(method, endpoint, timeout=timeout, **kwargs)
        return response.json() if response.content else {}

    def _request_bytes(self, method: str, endpoint: str, timeout: int = 30, **kwargs) -> bytes:
        response = self._request(method, endpoint, timeout=timeout, **kwargs)
        return response.content

    def screenshot(self, save_path: Optional[str] = None) -> bytes:
        """
        Capture a screenshot.

        Args:
            save_path: Optional file path to save the image. Returns raw bytes if None.

        Returns:
            JPEG image binary data.
        """
        data = self._request_bytes("GET", "/api/public/snapshot", timeout=10)
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(data)
            print(f"Screenshot saved: {save_path}")
        return data

    def control(self, events: List[List[Union[str, int, float, bool]]]) -> dict:
        """
        Send a sequence of control commands.

        Args:
            events: List of event arrays.

        Returns:
            API response JSON.
        """
        result = self._request_json(
            "POST",
            "/api/public/control",
            json={"events": events},
            headers={"Content-Type": "application/json"},
        )
        if result.get("code", 0) != 0:
            raise RuntimeError(f"Linkr control failed: {result}")
        return result

    def delay(self, milliseconds: int) -> dict:
        """Pause for the specified number of milliseconds."""
        return self.control([["delay", milliseconds]])

    def text(self, content: str, auto_split: bool = True) -> dict:
        """
        Input text.

        Per the API docs, text of about 30 characters requires a 1000ms pause.
        By default, text is auto-chunked with a 1000ms pause after every 30 characters.

        Args:
            content: Text to input (ASCII characters).
            auto_split: Whether to auto-chunk (default True).

        Returns:
            API response JSON.
        """
        self._validate_text_content(content)
        if not auto_split or len(content) <= self.TEXT_CHUNK_SIZE:
            delay = self.TEXT_DELAY_MS if len(content) >= self.TEXT_CHUNK_SIZE else 300
            return self.control([
                ["text", content],
                ["delay", delay]
            ])

        events = []
        for i in range(0, len(content), self.TEXT_CHUNK_SIZE):
            chunk = content[i:i+self.TEXT_CHUNK_SIZE]
            events.append(["text", chunk])
            events.append(["delay", self.TEXT_DELAY_MS])

        return self.control(events)

    def key(self, key_code: str, pressed: bool = True) -> dict:
        """
        Send a single keyboard event.

        Args:
            key_code: Key identifier, e.g. "MetaLeft", "KeyA".
            pressed: True=press, False=release.
        """
        return self.control([["keyboard", key_code, pressed]])

    def key_combo(self, *keys: str, press_delay: int = 50, post_delay: int = 100) -> dict:
        """
        Send a key combination (auto press/release ordering).

        Args:
            *keys: Key sequence, e.g. "MetaLeft", "KeyR".
            press_delay: Delay between key presses (milliseconds).
            post_delay: Delay after release (milliseconds).
        """
        events = []

        for key in keys:
            events.append(["keyboard", key, True])
            if press_delay > 0:
                events.append(["delay", press_delay])

        for key in reversed(keys):
            events.append(["keyboard", key, False])
            if press_delay > 0:
                events.append(["delay", press_delay])

        if post_delay > 0:
            events.append(["delay", post_delay])

        return self.control(events)

    def mouse_abs(self, x: float, y: float, buttons: int = 0, 
                  wheel_y: int = 0, wheel_x: int = 0) -> dict:
        """
        Absolute coordinate mouse operation.

        Args:
            x: Absolute X coordinate [0.00, 1.00].
            y: Absolute Y coordinate [0.00, 1.00].
            buttons: Button state bitmask (0=none, 1=left, 2=right, 4=middle).
            wheel_y: Vertical scroll [-20, 20], positive scrolls down.
            wheel_x: Horizontal scroll [-20, 20], positive scrolls right.
        """
        self._validate_unit_interval("x", x)
        self._validate_unit_interval("y", y)
        self._validate_wheel("wheel_y", wheel_y)
        self._validate_wheel("wheel_x", wheel_x)
        return self.control([["mouse_abs", buttons, x, y, wheel_y, wheel_x]])

    def mouse_rel(self, dx: int, dy: int, buttons: int = 0,
                  wheel_y: int = 0, wheel_x: int = 0) -> dict:
        """
        Relative coordinate mouse operation.

        Args:
            dx: X-axis relative displacement (pixels), positive right.
            dy: Y-axis relative displacement (pixels), positive down.
            buttons: Button state bitmask.
            wheel_y: Vertical scroll [-20, 20].
            wheel_x: Horizontal scroll [-20, 20].
        """
        self._validate_wheel("wheel_y", wheel_y)
        self._validate_wheel("wheel_x", wheel_x)
        return self.control([["mouse_rel", buttons, dx, dy, wheel_y, wheel_x]])

    def move_mouse(self, x: float, y: float, delay_ms: int = 0) -> dict:
        """Move mouse to absolute coordinates, with an optional render wait."""
        events: List[List[Union[str, int, float, bool]]] = [["mouse_abs", 0, x, y, 0, 0]]
        if delay_ms > 0:
            events.append(["delay", delay_ms])
        return self.control(events)

    def click(self, x: float, y: float, button: str = "left", 
              absolute: bool = True, post_delay: int = 200) -> dict:
        """
        Click at a specified position.

        Args:
            x: X coordinate (absolute 0-1 or relative pixels).
            y: Y coordinate (absolute 0-1 or relative pixels).
            button: Button type ("left", "right", "middle").
            absolute: Use absolute coordinates.
            post_delay: Delay after the click.
        """
        if absolute:
            self._validate_unit_interval("x", x)
            self._validate_unit_interval("y", y)

        button_map = {"left": 1, "right": 2, "middle": 4}
        btn_code = button_map.get(button, 1)

        event_type = "mouse_abs" if absolute else "mouse_rel"

        events = [
            [event_type, btn_code, x, y, 0, 0],
            ["delay", 100],
            [event_type, 0, x, y, 0, 0]
        ]

        if post_delay > 0:
            events.append(["delay", post_delay])

        return self.control(events)

    def double_click(self, x: float, y: float, absolute: bool = True) -> dict:
        """Double-click at a specified position."""
        self.click(x, y, absolute=absolute, post_delay=50)
        time.sleep(0.05)
        return self.click(x, y, absolute=absolute)

    def scroll(self, dy: int = 0, dx: int = 0, at_point: Optional[Point] = None) -> dict:
        """
        Scroll the mouse wheel.

        Args:
            dy: Vertical scroll amount [-20, 20], positive scrolls down.
            dx: Horizontal scroll amount [-20, 20], positive scrolls right.
            at_point: Move to this position (absolute coords) before scrolling.
        """
        events = []

        if at_point:
            self._validate_unit_interval("at_point.x", at_point.x)
            self._validate_unit_interval("at_point.y", at_point.y)
            events.append(["mouse_abs", 0, at_point.x, at_point.y, 0, 0])
            events.append(["delay", 50])
            events.append(["mouse_abs", 0, at_point.x, at_point.y, dy, dx])
        else:
            events.append(["mouse_rel", 0, 0, 0, dy, dx])

        return self.control(events)

    def run_command(self, command: str, wait: int = 500) -> dict:
        """
        Run a command via Win+R.

        Args:
            command: The command to run.
            wait: Wait time after opening the Run dialog (milliseconds).
        """
        self._validate_text_content(command)
        events = [
            ["keyboard", "MetaLeft", True],
            ["keyboard", "KeyR", True],
            ["delay", 50],
            ["keyboard", "KeyR", False],
            ["keyboard", "MetaLeft", False],
            ["delay", wait],
            ["text", command],
            ["delay", 1000],
            ["keyboard", "Enter", True],
            ["keyboard", "Enter", False]
        ]
        return self.control(events)


def quick_text(
    text: str, ip: Optional[str] = None, token: Optional[str] = None, auto_split: bool = True
) -> dict:
    """Quick text input (auto-chunked)."""
    client = LinkrClient(ip=ip, token=token)
    return client.text(text, auto_split=auto_split)


def quick_screenshot(
    save_path: str = "screen.jpeg", ip: Optional[str] = None, token: Optional[str] = None
) -> bytes:
    """Quick screenshot capture."""
    client = LinkrClient(ip=ip, token=token)
    return client.screenshot(save_path)


if __name__ == "__main__":
    import sys

    client = LinkrClient()

    if len(sys.argv) < 2:
        print("Linkr Client - Remote Control Tool")
        print()
        print("Usage: python linkr_client.py <command> [args]")
        print()
        print("Commands:")
        print("  screenshot [path]       - Capture screenshot (default: screen.jpeg)")
        print("  text <content>          - Input text (auto-chunked)")
        print("  run <command>           - Run a command via Win+R")
        print("  click <x> <y>           - Click at position (0-1 absolute coords)")
        print("  key <key_code>          - Send a single key")
        print("  combo <key1> <key2>...  - Send a key combination")
        print()
        print("Environment:")
        print("  Linkr_IP - Linkr device IP (required, e.g. 192.168.x.x)")
        print("  Linkr_TOKEN - Linkr access token (required)")
        print()
        print("Examples:")
        print('  python linkr_client.py text "Hello World"')
        print('  python linkr_client.py run notepad')
        print('  python linkr_client.py click 0.5 0.5')
        print('  python linkr_client.py combo MetaLeft KeyR')
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "screenshot":
        path = sys.argv[2] if len(sys.argv) > 2 else "screen.jpeg"
        client.screenshot(path)

    elif cmd == "text":
        if len(sys.argv) < 3:
            print("Error: text content is required")
            sys.exit(1)
        content = sys.argv[2]
        result = client.text(content)
        print(f"Input {len(content)} characters (auto-chunked)")
        print(f"Response: {result}")

    elif cmd == "run":
        if len(sys.argv) < 3:
            print("Error: command is required")
            sys.exit(1)
        result = client.run_command(sys.argv[2])
        print(f"Response: {result}")

    elif cmd == "click":
        if len(sys.argv) < 4:
            print("Error: x and y coordinates required")
            sys.exit(1)
        x, y = float(sys.argv[2]), float(sys.argv[3])
        result = client.click(x, y)
        print(f"Response: {result}")

    elif cmd == "key":
        if len(sys.argv) < 3:
            print("Error: key code is required")
            sys.exit(1)
        result = client.key(sys.argv[2])
        print(f"Response: {result}")

    elif cmd == "combo":
        if len(sys.argv) < 3:
            print("Error: at least one key required")
            sys.exit(1)
        keys = sys.argv[2:]
        result = client.key_combo(*keys)
        print(f"Combo {'+'.join(keys)} sent")
        print(f"Response: {result}")

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
