# Web KeyboardEvent.code Reference

A complete list of keyboard key identifiers for `keyboard` events.

## Letter Keys

| Code | Description |
|:---|:---|
| `KeyA` | A key |
| `KeyB` | B key |
| `KeyC` | C key |
| `KeyD` | D key |
| `KeyE` | E key |
| `KeyF` | F key |
| `KeyG` | G key |
| `KeyH` | H key |
| `KeyI` | I key |
| `KeyJ` | J key |
| `KeyK` | K key |
| `KeyL` | L key |
| `KeyM` | M key |
| `KeyN` | N key |
| `KeyO` | O key |
| `KeyP` | P key |
| `KeyQ` | Q key |
| `KeyR` | R key |
| `KeyS` | S key |
| `KeyT` | T key |
| `KeyU` | U key |
| `KeyV` | V key |
| `KeyW` | W key |
| `KeyX` | X key |
| `KeyY` | Y key |
| `KeyZ` | Z key |

## Number Keys

| Code | Description |
|:---|:---|
| `Digit0` | 0 key |
| `Digit1` | 1 key |
| `Digit2` | 2 key |
| `Digit3` | 3 key |
| `Digit4` | 4 key |
| `Digit5` | 5 key |
| `Digit6` | 6 key |
| `Digit7` | 7 key |
| `Digit8` | 8 key |
| `Digit9` | 9 key |

## Function Keys

| Code | Description |
|:---|:---|
| `F1` | F1 key |
| `F2` | F2 key |
| `F3` | F3 key |
| `F4` | F4 key |
| `F5` | F5 key |
| `F6` | F6 key |
| `F7` | F7 key |
| `F8` | F8 key |
| `F9` | F9 key |
| `F10` | F10 key |
| `F11` | F11 key |
| `F12` | F12 key |

## Control Keys

| Code | Description |
|:---|:---|
| `Escape` | ESC key |
| `Tab` | Tab key |
| `CapsLock` | Caps Lock |
| `ShiftLeft` | Left Shift |
| `ShiftRight` | Right Shift |
| `ControlLeft` | Left Ctrl |
| `ControlRight` | Right Ctrl |
| `AltLeft` | Left Alt |
| `AltRight` | Right Alt |
| `MetaLeft` | Left Meta (Windows/Command) |
| `MetaRight` | Right Meta |
| `Space` | Space key |
| `Enter` | Enter key |
| `Backspace` | Backspace key |
| `Delete` | Delete key |
| `Insert` | Insert key |
| `Home` | Home key |
| `End` | End key |
| `PageUp` | Page Up |
| `PageDown` | Page Down |

## Arrow Keys

| Code | Description |
|:---|:---|
| `ArrowUp` | Up Arrow |
| `ArrowDown` | Down Arrow |
| `ArrowLeft` | Left Arrow |
| `ArrowRight` | Right Arrow |

## Symbol Keys

| Code | Description |
|:---|:---|
| `Backquote` | `` ` `` |
| `Minus` | `-` |
| `Equal` | `=` |
| `BracketLeft` | `[` |
| `BracketRight` | `]` |
| `Backslash` | `\` |
| `Semicolon` | `;` |
| `Quote` | `'` |
| `Comma` | `,` |
| `Period` | `.` |
| `Slash` | `/` |

## Numpad

| Code | Description |
|:---|:---|
| `NumLock` | Num Lock |
| `Numpad0` ~ `Numpad9` | Number keys 0-9 |
| `NumpadAdd` | `+` |
| `NumpadSubtract` | `-` |
| `NumpadMultiply` | `*` |
| `NumpadDivide` | `/` |
| `NumpadDecimal` | `.` |
| `NumpadEnter` | Enter |

## Common Combo Key Examples

| Action | Event Sequence |
|:---|:---|
| **Copy** | `["keyboard", "ControlLeft", true]`, `["keyboard", "KeyC", true]`, `["delay", 50]`, `["keyboard", "KeyC", false]`, `["keyboard", "ControlLeft", false]` |
| **Paste** | `["keyboard", "ControlLeft", true]`, `["keyboard", "KeyV", true]`, `["delay", 50]`, `["keyboard", "KeyV", false]`, `["keyboard", "ControlLeft", false]` |
| **Select All** | `["keyboard", "ControlLeft", true]`, `["keyboard", "KeyA", true]`, `["delay", 50]`, `["keyboard", "KeyA", false]`, `["keyboard", "ControlLeft", false]` |
| **Save** | `["keyboard", "ControlLeft", true]`, `["keyboard", "KeyS", true]`, `["delay", 50]`, `["keyboard", "KeyS", false]`, `["keyboard", "ControlLeft", false]` |
| **Run** | `["keyboard", "MetaLeft", true]`, `["keyboard", "KeyR", true]`, `["delay", 50]`, `["keyboard", "KeyR", false]`, `["keyboard", "MetaLeft", false]` |
| **Task Manager** | `["keyboard", "ControlLeft", true]`, `["keyboard", "ShiftLeft", true]`, `["keyboard", "Escape", true]`, ... |
| **Alt+Tab** | `["keyboard", "AltLeft", true]`, `["keyboard", "Tab", true]`, `["delay", 50]`, `["keyboard", "Tab", false]`, `["keyboard", "AltLeft", false]` |
| **Screenshot** | `["keyboard", "MetaLeft", true]`, `["keyboard", "ShiftLeft", true]`, `["keyboard", "KeyS", true]`, ... |

## References

- [MDN - KeyboardEvent.code](https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent/code)
- [W3C - UI Events KeyboardEvent code Values](https://www.w3.org/TR/uievents-code/)
