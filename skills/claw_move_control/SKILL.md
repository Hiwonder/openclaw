---
name: claw_move_control
description: "控制ROS2机器人底盘移动。通过话题 /claw_move_control/chassis_command 发送字符串命令，支持单动作和多动作连续执行。/ Control ROS2 robot chassis movement via topic /claw_move_control/chassis_command (std_msgs/msg/String). Supports single and multi-action sequences."
---

# 底盘运动控制器 / Chassis Move Controller

## 话题 / Topic

- **话题名 / Topic name**: `/claw_move_control/chassis_command`
- **消息类型 / Message type**: `std_msgs/msg/String`

## 服务 / Service

- **服务名 / Service name**: `/claw_move_control/move_status`
- **类型 / Type**: `std_srvs/srv/Trigger`
- **用途**: 查询底盘运动状态

### 状态说明

| 状态 | 含义 |
|------|------|
| `stop` | 空闲/运动完成，可以执行新指令 |
| `moving` | 运动中，执行动作期间 |

## 命令格式 / Command Format

```
<direction> <time>
```

多动作用逗号分隔 / Multi-actions separated by comma:
```
forward 1, stop 0.5, backward 2
```

## 支持的动作 / Supported Actions

| 命令 / Command | 说明 / Description |
|------|------|
| `forward <t>` | 前进 t 秒（默认速度 0.15 m/s）/ Move forward for t seconds |
| `backward <t>` | 后退 t 秒 / Move backward for t seconds |
| `left <t>` | 左转 t 秒（角速度 0.45 rad/s）/ Turn left for t seconds |
| `right <t>` | 右转 t 秒 / Turn right for t seconds |
| `stop <t>` | 停止 t 秒 / Stop for t seconds |

- 时间省略时：移动类默认 2 秒，stop 默认 0.5 秒
- 多动作之间自动插入 0.5 秒停止

## 执行方式 / Usage

### 查询状态
```bash
ros2 service call /claw_move_control/move_status std_srvs/srv/Trigger {}
# 返回: stop = 空闲, moving = 运动中
```

### 执行命令（使用前先查状态）

```bash
# 查状态
ros2 service call /claw_move_control/move_status std_srvs/srv/Trigger {}

# 如果是 stop，发命令
ros2 topic pub --once /claw_move_control/chassis_command std_msgs/msg/String "{data: 'forward 2'}"

# 运动期间不要发新指令
```

### 命令示例

```bash
# 单动作
ros2 topic pub --once /claw_move_control/chassis_command std_msgs/msg/String "{data: 'forward 2'}"

# 多动作连续
ros2 topic pub --once /claw_move_control/chassis_command std_msgs/msg/String "{data: 'forward 1, stop 0.5, backward 2'}"

# 左转1秒
ros2 topic pub --once /claw_move_control/chassis_command std_msgs/msg/String "{data: 'left 1'}"
```

## 参数说明 / Parameters

| 参数 / Parameter | 说明 / Description | 默认值 / Default |
|------|------|--------|
| `--cmd`, `-c` | 命令字符串 / Command string (required) | required |
| `--topic` | 话题名 / Topic name | /claw_move_control/chassis_command |

## 自然语言转命令参考 / Natural Language to Command Reference

| 中文 | English | 命令 / Command |
|------|---------|------|
| 前进2秒 | Move forward 2s | `forward 2` |
| 后退1秒 | Move backward 1s | `backward 1` |
| 左转1秒 | Turn left 1s | `left 1` |
| 右转2秒 | Turn right 2s | `right 2` |
| 停止0.5秒 | Stop 0.5s | `stop 0.5` |
| 前进1秒，停止0.5秒，后退2秒 | Forward 1s, stop 0.5s, backward 2s | `forward 1, stop 0.5, backward 2` |

## ⚠️ 重要规则

1. **使用 `--once` 只发一次**，重复发送会导致冲突
2. **执行前先查 `move_status`**，如果是 `moving` 要等完成再发新指令
3. 多动作连续执行时，内部已包含停止间隔，不需要额外发 stop
