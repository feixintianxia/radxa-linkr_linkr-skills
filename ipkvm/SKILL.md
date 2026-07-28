---
name: ipkvm
description: >
  A universal skill for the standardized Linkr control interface, providing
  screen capture and mouse/keyboard automation via HTTP API.
  Suitable for remote server management, automated testing, and unattended operations.
  Supports absolute/relative mouse control, keyboard simulation, text input, and delays.
metadata: { "openclaw": { "emoji": "🖥️" }}
---

# Linkr Universal Controller

OpenClaw directly calls the standard HTTP interface provided by Linkr (screenshot, keyboard, and mouse control) to automate the remote target machine. Python scripts are optional helpers.

## Prerequisites

Before using this skill, set the following required environment variables:

- `Linkr_IP`
- `Linkr_TOKEN`

Without them, the skill can still be recognized and enabled by OpenClaw, but screenshot and control requests will fail due to missing configuration.

### PowerShell (recommended)

> Run in PowerShell before first use:
> ```powershell
> [System.Environment]::SetEnvironmentVariable("Linkr_IP", "192.168.x.x", "User")
> [System.Environment]::SetEnvironmentVariable("Linkr_TOKEN", "your_api_token", "User")
> ```

### Bash

```bash
export Linkr_IP="192.168.x.x"
export Linkr_TOKEN="your_api_token"
```

## Execution Rules

When executing this skill, follow this order:

1. Read environment variables `Linkr_IP` and `Linkr_TOKEN`
2. Compose the base URL: `http://${Linkr_IP}:80`
3. For screenshots, call: `GET /api/public/snapshot`
4. For control, call: `POST /api/public/control`
5. All HTTP requests must include the header: `Authorization: token ${Linkr_TOKEN}`

> **Note**:
> - `Linkr_IP` and `Linkr_TOKEN` in `SKILL.md` are variable names only — they will not be auto-replaced with real values
> - Real values must come from environment variables readable by OpenClaw at runtime
> - After updating environment variables, restart OpenClaw or reopen your terminal before executing

**Recommended execution model**:

```text
Read Linkr_IP and Linkr_TOKEN
-> Compose http://${Linkr_IP}:80
-> Call snapshot / control endpoints
-> Parse results and continue decision-making
```

## System Architecture

```
┌─────────────┐      HTTP API      ┌─────────────┐      KVM Signal      ┌─────────────┐
│   OpenClaw  │ ◄────────────────► │    Linkr    │ ◄──────────────────► │   Target    │
│    (PC)     │                    │             │                      │   Machine   │
└─────────────┘                    └─────────────┘                      └─────────────┘

    HTTP interface (provided by Linkr):
    ├── Screenshot endpoint: /api/public/snapshot
    └── Control endpoint:   /api/public/control
```

## API Reference

### 1. Screenshot

Capture a real-time screen image from the target machine for AI model analysis.

| Property | Value |
|:---|:---|
| URL | `http://${Linkr_IP}:80/api/public/snapshot` |
| Method | GET |
| Returns | JPEG image binary data |

**Example**:
```bash
curl -X GET "http://${Linkr_IP}:80/api/public/snapshot" -H "Authorization: token ${Linkr_TOKEN}" -o screen.jpeg
```

### 2. Device Control

Send sequences of mouse, keyboard, and text input control commands.

| Property | Value |
|:---|:---|
| URL | `http://${Linkr_IP}:80/api/public/control` |
| Method | POST |
| Content-Type | `application/json` |

**Request body**:
```json
{
  "events": [
    ["text", "Hello World"],
    ["delay", 300],
    ["mouse_abs", 0, 0.5, 0.5, 0, 0],
    ["keyboard", "MetaLeft", true],
    ["keyboard", "MetaLeft", false]
  ]
}
```

**Response**:
```json
{
  "code": 0,
  "data": null,
  "message": "Request succeeded!"
}
```

- `code`: 0 = success, non-zero = failure
- `message`: Linkr debug information

## Event Types

### Keyboard Event (keyboard)

Simulate key press and release.

**Format**: `["keyboard", keyCode, isPressed]`

| Index | Field | Type | Description |
|:---|:---|:---|:---|
| 0 | `type` | `string` | Fixed value `"keyboard"` |
| 1 | `keyCode` | `string` | Key identifier using [Web standard KeyboardEvent.code](https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/code) |
| 2 | `isPressed` | `boolean` | `true`=press, `false`=release |

**Common key identifiers**:

| Identifier | Description |
|:---|:---|
| `MetaLeft` | Left Meta key (Windows/Command) |
| `ControlLeft` | Left Ctrl key |
| `AltLeft` | Left Alt key |
| `ShiftLeft` | Left Shift key |
| `KeyA` ~ `KeyZ` | Letter keys A-Z |
| `Enter` | Enter key |
| `Escape` | ESC key |
| `Tab` | Tab key |
| `Space` | Space key |

**Example**:
```json
["keyboard", "MetaLeft", true]   // Press Windows key
["keyboard", "MetaLeft", false]  // Release Windows key
["keyboard", "KeyR", true]       // Press R key
["keyboard", "KeyR", false]      // Release R key
```

### Absolute Mouse Event (mouse_abs)

Move the mouse to an absolute screen position.

**Format**: `["mouse_abs", buttons, x, y, wheelY, wheelX]`

| Index | Field | Type | Description |
|:---|:---|:---|:---|
| 0 | `type` | `string` | Fixed value `"mouse_abs"` |
| 1 | `buttons` | `number` | Mouse button state (bitmask) |
| 2 | `x` | `number` | Absolute X coordinate, `[0.00, 1.00]`, origin at top-left |
| 3 | `y` | `number` | Absolute Y coordinate, `[0.00, 1.00]`, origin at top-left |
| 4 | `wheelY` | `number` | Vertical scroll, `[-20, 20]`, positive scrolls down |
| 5 | `wheelX` | `number` | Horizontal scroll, `[-20, 20]`, positive scrolls right |

**Button bitmask**:
- `0`: No button / release all
- `1` (bit 0): Left button
- `2` (bit 1): Right button
- `4` (bit 2): Middle button
- `3` (1+2): Left + Right simultaneously

**Example**:
```json
["mouse_abs", 0, 0.5, 0.5, 0, 0]      // Move mouse to screen center
["mouse_abs", 1, 0.5, 0.5, 0, 0]      // Move to center and left-click
["mouse_abs", 0, 0.5, 0.5, 0, 0]      // Move to center and release
["mouse_abs", 0, 0.5, 0.5, 20, 10]    // Move to center, scroll down 20px, right 10px
```

### Relative Mouse Event (mouse_rel)

Move the mouse relative to its current position, in pixels.

**Format**: `["mouse_rel", buttons, deltaX, deltaY, wheelY, wheelX]`

| Index | Field | Type | Description |
|:---|:---|:---|:---|
| 0 | `type` | `string` | Fixed value `"mouse_rel"` |
| 1 | `buttons` | `number` | Mouse button state (bitmask, same as `mouse_abs`) |
| 2 | `deltaX` | `number` | X-axis relative displacement (pixels), positive right, negative left |
| 3 | `deltaY` | `number` | Y-axis relative displacement (pixels), positive down, negative up |
| 4 | `wheelY` | `number` | Vertical scroll, `[-20, 20]`, positive scrolls down |
| 5 | `wheelX` | `number` | Horizontal scroll, `[-20, 20]`, positive scrolls right |

**Example**:
```json
["mouse_rel", 0, 10, 10, 0, 0]        // Move 10px right and 10px down
["mouse_rel", 1, 0, 0, 0, 0]          // Left-click at current position
["mouse_rel", 0, 0, 0, 0, 0]          // Release button at current position
["mouse_rel", 0, 10, 10, 20, 10]      // Move 10px right+down, scroll down 20px, right 10px
```

### Text Event (text)

Input a text string at the current cursor position.

**Format**: `["text", "text_to_type"]`

| Index | Field | Type | Description |
|:---|:---|:---|:---|
| 0 | `type` | `string` | Fixed value `"text"` |
| 1 | `content` | `string` | Text to input, max 1024 characters |

**Character set restrictions**:
- Control characters: `9` (Tab), `10` (Enter)
- Printable characters: `32` (Space) ~ `126` (`~`)

**Example**:
```json
["text", "https://www.example.com"]  // Input a URL at the current cursor position
```

### Delay Event (delay)

Pause execution to ensure Linkr finished the previous operation.

**Format**: `["delay", milliseconds]`

| Index | Field | Type | Description |
|:---|:---|:---|:---|
| 0 | `type` | `string` | Fixed value `"delay"` |
| 1 | `duration` | `number` | Pause duration in milliseconds |

> **Important**:
> - A `delay` event **must** follow a `text` event to ensure complete input
> - For text around 30 characters, a **1000ms** pause is recommended
> - Long text must be chunked, with a pause after every 30 characters
> - Complex operations may require multiple `delay` events

**Example**:
```json
["text", "https://www.example.com"]
["delay", 1000]
```

## Complete Task Example

### Open Browser and Visit a Website

```json
{
  "events": [
    ["keyboard", "MetaLeft", true],
    ["keyboard", "KeyR", true],
    ["delay", 50],
    ["keyboard", "KeyR", false],
    ["keyboard", "MetaLeft", false],
    ["delay", 500],
    ["text", "chrome"],
    ["delay", 300],
    ["keyboard", "Enter", true],
    ["keyboard", "Enter", false],
    ["delay", 3000],
    ["mouse_abs", 0, 0.5, 0.08, 0, 0],
    ["delay", 200],
    ["text", "example.com"],
    ["delay", 1000],
    ["keyboard", "Enter", true],
    ["keyboard", "Enter", false]
  ]
}
```

**Step breakdown**:
1. `Win+R` to open the Run dialog
2. Type `chrome` and press Enter to launch the browser
3. Wait 3 seconds for the browser to start
4. Move mouse to the address bar (top center)
5. Type `example.com`
6. Pause 1000ms to ensure complete text input
7. Press Enter to navigate

## Best Practices

### 1. Coordinate Positioning
- Prefer `mouse_abs` (absolute coords), range `[0.00, 1.00]` adapts to different resolutions
- Capture a screenshot before critical operations to confirm the current state
- Use AI vision analysis for UI element localization

### 2. Timing Control (important)

| Scenario | Recommended Delay | Notes |
|:---|:---|:---|
| After short text (<10 chars) | 300ms | Simple text |
| After medium text (10-30 chars) | 500-800ms | e.g. URLs |
| **After long text (~30 chars)** | **1000ms** | Required to ensure complete input |
| After launching an app | 2000-5000ms | Depends on app startup time |
| After page load | 1000-3000ms | Depends on network |
| Between consecutive keys | 50-100ms | Prevent dropped keys |

### 3. Long Text Input Strategy

Text exceeding 30 characters must be chunked:

```json
{
  "events": [
    ["text", "This is a long text that needs"],
    ["delay", 1000],
    ["text", " to be split into multiple parts"],
    ["delay", 1000],
    ["text", " to ensure complete input."],
    ["delay", 1000]
  ]
}
```

### 4. Key Operation Rules
- Always pair press and release: `[key, true]` and `[key, false]`
- Modifier key order: press modifier (Ctrl/Alt/Shift/Win) first, then the main key
- Release order: release the main key first, then the modifier

### 5. Scroll Operations
- Vertical scroll `wheelY`: `[-20, 20]`, positive scrolls down
- Horizontal scroll `wheelX`: `[-20, 20]`, positive scrolls right

### 6. Error Handling
- Check the `code` field — non-zero indicates failure
- If screenshot fails, check the network and Linkr status
- If control is unresponsive, verify the JSON format and event parameters

## Troubleshooting

| Symptom | Possible Cause | Solution |
|:---|:---|:---|
| Screenshot fails | Network issue / Linkr not running | Check `Linkr_IP` connectivity |
| Control unresponsive | Invalid event format | Verify JSON array length and types |
| Coordinates inaccurate | Resolution changed | Use `mouse_abs` absolute coords `[0.00, 1.00]` |
| Garbled text input | IME in wrong state | Switch to English input method first |
| Incomplete text input | Insufficient delay | Add 1000ms pause after every 30 chars |
| Operations out of order | Insufficient delay | Increase `delay` duration |
| Long text truncated | Buffer overflow | Chunk input with pauses every 30 chars |

## Helper Scripts

### Bash Quick Call

```bash
#!/bin/bash
# scripts/send_control.sh

Linkr_IP="${Linkr_IP:-}"
Linkr_TOKEN="${Linkr_TOKEN:-}"

curl -X POST "http://${Linkr_IP}:80/api/public/control" \
  -H "Content-Type: application/json" \
  -H "Authorization: token ${Linkr_TOKEN}" \
  -d "$1"
```

### Python Wrapper

```python
#!/usr/bin/env python3
# scripts/linkr_client.py

import os
import requests
from typing import List, Union

class LinkrClient:
    def __init__(self):
        ip = os.getenv("Linkr_IP")
        if not ip:
            raise ValueError("Missing Linkr_IP")
        self.url = f"http://{ip}:80"
        self.token = os.getenv("Linkr_TOKEN")
        if not self.token:
            raise ValueError("Missing Linkr_TOKEN")

    def screenshot(self, save_path: str = "screen.jpeg") -> bytes:
        resp = requests.get(
            f"{self.url}/api/public/snapshot",
            timeout=10,
            headers={"Authorization": f"token {self.token}"},
        )
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(resp.content)
        return resp.content

    def control(self, events: List[List[Union[str, int, float, bool]]]) -> dict:
        resp = requests.post(
            f"{self.url}/api/public/control",
            json={"events": events},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"token {self.token}",
            },
            timeout=30
        )
        return resp.json()

    def text(self, content: str) -> dict:
        events = []
        chunk_size = 30
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            events.append(["text", chunk])
            events.append(["delay", 1000])
        return self.control(events)
```

## Related Resources

- **scripts/**: Helper scripts for common operations
- **examples/**: Typical automation task examples
- **references/web_keycodes.md**: Complete KeyboardEvent.code reference table
