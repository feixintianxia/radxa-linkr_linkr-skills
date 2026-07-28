# Linkr Universal Controller

OpenClaw skill for the standard Linkr control interface, providing a universal HTTP-based way to capture screens and send keyboard and mouse events. Python helpers are optional.

## Features

- 📸 **Screenshot**: Capture real-time screen images from the target machine
- 🖱️ **Mouse control**: Supports absolute coordinates `[0.00, 1.00]` and relative (pixel) modes
- ⌨️ **Keyboard simulation**: Full key press/release control
- 📝 **Text input**: Auto-chunking with 1000ms pause every 30 characters
- ⏱️ **Delay control**: Ensure correct execution sequence of operations

## Quick Start

### 1. Environment Setup

The following environment variables are required:

#### Bash

```bash
export Linkr_IP="192.168.x.x"
export Linkr_TOKEN="your_api_token"
```

#### PowerShell

```powershell
[System.Environment]::SetEnvironmentVariable("Linkr_IP", "192.168.x.x", "User")
[System.Environment]::SetEnvironmentVariable("Linkr_TOKEN", "your_api_token", "User")
```

### Execution Rules

When executing this skill, first read the environment variables `Linkr_IP` and `Linkr_TOKEN`, compose the base URL `http://${Linkr_IP}:80`, then call the Linkr HTTP API.

- Screenshot endpoint: `GET /api/public/snapshot`
- Control endpoint: `POST /api/public/control`
- All requests must include the header: `Authorization: token ${Linkr_TOKEN}`

> **Note**:
> - `Linkr_IP` and `Linkr_TOKEN` in the docs are variable names only — they are not auto-replaced with real values
> - Real values must come from environment variables readable by OpenClaw at runtime
> - After modifying environment variables, you typically need to restart OpenClaw

```text
Read Linkr_IP and Linkr_TOKEN
-> Compose http://${Linkr_IP}:80
-> Call snapshot / control endpoints
-> Parse results and proceed
```

### 2. Usage Examples

#### Bash

```bash
# Send control commands
./scripts/send_control.sh '{"events":[["text","hello"],["delay",300]]}'

# Capture screenshot
curl -X GET "http://${Linkr_IP}:80/api/public/snapshot" -H "Authorization: token ${Linkr_TOKEN}" -o screen.jpeg
```

#### Python (optional)

```python
from scripts.linkr_client import LinkrClient

client = LinkrClient()

# Capture screenshot
client.screenshot("desktop.jpeg")

# Input text (auto-chunked: 1000ms pause every 30 chars)
client.text("This is a long text that will be automatically split into chunks...")

# Key combo Win+R
client.key_combo("MetaLeft", "KeyR")

# Click screen center
client.click(0.5, 0.5)
```

### 3. JSON Example

```bash
# Open browser and visit a URL
curl -X POST "http://${Linkr_IP}:80/api/public/control" \
  -H "Content-Type: application/json" \
  -H "Authorization: token ${Linkr_TOKEN}" \
  -d @examples/open_browser.json
```

## Directory Structure

```
linkr-skills/
├── SKILL.md                     # Main skill document (OpenClaw spec)
├── README.md                    # This file
├── README.zh-cn.md              # Chinese README
├── scripts/
│   ├── send_control.sh          # Bash quick-call script
│   ├── linkr_client.py          # Python client wrapper (supports auto-chunking)
├── examples/
│   ├── open_browser.json        # Open browser example
│   ├── open_notepad.json        # Open notepad example
│   ├── mouse_demo.json          # Mouse operation demo
│   ├── keyboard_shortcuts.json  # Keyboard shortcuts demo
│   └── long_text_input.json     # Long text chunked input demo
└── references/
    └── web_keycodes.md          # Keyboard code reference table
```

## Event Type Quick Reference

| Event | Format | Description |
|:---|:---|:---|
| Keyboard | `["keyboard", "KeyA", true]` | Press key A |
| Absolute Mouse | `["mouse_abs", 0, 0.5, 0.5, 0, 0]` | Move to screen center |
| Relative Mouse | `["mouse_rel", 0, 100, 100, 0, 0]` | Move 100px right and down |
| Text | `["text", "hello"]` | Input text |
| Delay | `["delay", 1000]` | Pause 1000 milliseconds |

## Important: Long Text Input

Per Linkr documentation requirements, **text of about 30 characters needs a 1000ms pause** to ensure complete input.

### Manual Chunking Example

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

### Python Client Auto-Chunking

```python
# Automatic: 1000ms pause every 30 characters
client.text("This is a long text that will be automatically split into chunks...")
```

## Installing into OpenClaw

```bash
# Copy to OpenClaw skills directory
cp -r linkr-skills ~/.openclaw/skills/

# Verify installation
openclaw skills list
```

## Dependencies

- `curl`: for HTTP requests
- `python3` + `requests`: for Python client (optional)