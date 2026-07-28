# Linkr Universal Controller

OpenClaw skill for the standard Linkr control interface, providing a universal HTTP-based way to capture screens and send keyboard and mouse events. Python helpers are optional.

## 功能特性

- 📸 **屏幕截图**: 获取被控机实时屏幕图像
- 🖱️ **鼠标控制**: 支持绝对坐标 `[0.00, 1.00]` 和相对坐标（像素）模式
- ⌨️ **键盘模拟**: 完整的按键按下/释放控制
- 📝 **文本输入**: 自动分段，每30字符后暂停1000ms确保完整输入
- ⏱️ **延时控制**: 确保操作序列正确执行

## 快速开始

### 1. 环境配置

以下环境变量均为必填：

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

### 执行规则

执行本 skill 时，请先读取环境变量 `Linkr_IP` 和 `Linkr_TOKEN`，再组合出基础地址 `http://${Linkr_IP}:80`，最后调用 Linkr 的 HTTP API。

- 截图接口：`GET /api/public/snapshot`
- 控制接口：`POST /api/public/control`
- 所有请求都必须带上请求头：`Authorization: token ${Linkr_TOKEN}`

> **注意**：
> - 文档中的 `Linkr_IP`、`Linkr_TOKEN` 只是变量名说明，不会自动替换成真实值
> - 真实值必须来自 OpenClaw 运行时能读取到的环境变量
> - 如果你刚修改了环境变量，通常需要重启 OpenClaw 后再执行

```text
读取 Linkr_IP 和 Linkr_TOKEN
-> 组合出 http://${Linkr_IP}:80
-> 调用 snapshot / control 接口
-> 解析结果并继续执行
```

### 2. 使用示例

#### Bash 方式
```bash
# 发送控制指令
./scripts/send_control.sh '{"events":[["text","hello"],["delay",300]]}'

# 获取截图
curl -X GET "http://${Linkr_IP}:80/api/public/snapshot" -H "Authorization: token ${Linkr_TOKEN}" -o screen.jpeg
```

#### Python 方式（可选）
```python
from scripts.linkr_client import LinkrClient

client = LinkrClient()

# 获取截图
client.screenshot("desktop.jpeg")

# 输入文本（自动分段：每30字符后暂停1000ms）
client.text("This is a long text that will be automatically split into chunks...")

# 组合键 Win+R
client.key_combo("MetaLeft", "KeyR")

# 点击屏幕中心
client.click(0.5, 0.5)
```

### 3. 使用示例JSON

```bash
# 打开浏览器访问百度
curl -X POST "http://${Linkr_IP}:80/api/public/control"   -H "Content-Type: application/json"   -H "Authorization: token ${Linkr_TOKEN}"   -d @examples/open_browser.json
```

## 文档结构

```
linkr-skills/
├── SKILL.md                    # 主技能文档（OpenClaw规范）
├── README.md                   # 本文件
├── scripts/
│   ├── send_control.sh         # Bash快速调用脚本
│   ├── linkr_client.py         # Python客户端封装（支持自动分段）
├── examples/
│   ├── open_browser.json       # 打开浏览器访问百度
│   ├── open_notepad.json       # 打开记事本
│   ├── mouse_demo.json         # 鼠标操作演示
│   ├── keyboard_shortcuts.json # 组合键演示
│   └── long_text_input.json    # 长文本分段输入演示
└── references/
    └── web_keycodes.md         # 按键代码参考表
```

## 事件类型速查

| 事件 | 格式 | 说明 |
|:---|:---|:---|
| 键盘 | `["keyboard", "KeyA", true]` | 按下A键 |
| 鼠标绝对 | `["mouse_abs", 0, 0.5, 0.5, 0, 0]` | 移动到屏幕中心 |
| 鼠标相对 | `["mouse_rel", 0, 100, 100, 0, 0]` | 右下移100像素 |
| 文本 | `["text", "hello"]` | 输入文本 |
| 延时 | `["delay", 1000]` | 暂停1000毫秒 |

## 重要提示：长文本输入

根据Linkr文档要求，**文本长度约30字符时需要暂停1000毫秒**确保完整输入。

### 手动分段示例
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

### Python客户端自动分段
```python
# 自动处理：每30字符后添加1000ms暂停
client.text("This is a long text that will be automatically split into chunks...")
```

## 安装到 OpenClaw

```bash
# 复制到 OpenClaw skills 目录
cp -r linkr-skills ~/.openclaw/skills/

# 验证安装
openclaw skills list
```

## 依赖

- `curl`: 用于HTTP请求
- `python3` + `requests`: 用于Python客户端（可选）