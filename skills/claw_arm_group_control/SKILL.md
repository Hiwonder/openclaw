---
name: claw_arm_group_control
description: "控制机械臂执行预设动作组。通过话题 /claw_arm_group_control/arm_group_control 发送字符串命令。适用于单一目的、明确指令的场景，如夹萝卜、拿给我、初始化、抬机械臂等。"
---

# 机械臂动作组控制器 / Robot Arm Group Controller

## 话题 / Topic

- **话题名 / Topic name**: `/claw_arm_group_control/arm_group_control`
- **消息类型 / Message type**: `std_msgs/msg/String`

## 服务 / Service

- **服务名 / Service name**: `/claw_arm_group_control/arm_group_status`
- **类型 / Type**: `std_srvs/srv/Trigger`
- **用途**: 查询机械臂动作状态

### 状态说明

| 状态 | 含义 |
|------|------|
| `stop` | 空闲/运动完成，可以执行新动作 |
| `moving` | 运动中，执行动作期间 |

## 支持的动作 / Supported Actions

| 动作 | 说明 / Description |
|------|------|
| `voice_pick` | 夹个萝卜 / Pick a carrot |
| `voice_give` | 拿给我 / Pass me the item |
| `init` | 回到初始姿态 / Return to initial position |
| `camera_up` | 抬起机械臂 / Lift robot arm |

## 执行方式 / Usage

### 查询状态
```bash
ros2 service call /claw_arm_group_control/arm_group_status std_srvs/srv/Trigger {}
# 返回: stop = 空闲, moving = 运动中
```

### 执行动作（使用前先查状态）

```bash
# 查状态
ros2 service call /claw_arm_group_control/arm_group_status std_srvs/srv/Trigger {}

# 如果是 stop，发动作
ros2 topic pub --once /claw_arm_group_control/arm_group_control std_msgs/msg/String "{data: 'voice_pick'}"

# 运动期间不要发新动作
```

### 动作示例

```bash
# 夹个萝卜
ros2 topic pub --once /claw_arm_group_control/arm_group_control std_msgs/msg/String "{data: 'voice_pick'}"

# 拿给我
ros2 topic pub --once /claw_arm_group_control/arm_group_control std_msgs/msg/String "{data: 'voice_give'}"

# 回到初始姿态
ros2 topic pub --once /claw_arm_group_control/arm_group_control std_msgs/msg/String "{data: 'init'}"

# 抬起机械臂
ros2 topic pub --once /claw_arm_group_control/arm_group_control std_msgs/msg/String "{data: 'camera_up'}"
```

## 自然语言触发 / Natural Language Triggers

| 中文 | English | 动作 / Action |
|------|---------|---------------|
| 夹个萝卜 | pick a carrot | `voice_pick` |
| 拿给我 / 拿过来 | give me, pass me | `voice_give` |
| 初始化 / 回到初始 | init, initialize, reset | `init` |
| 抬起机械臂 / 抬高 | lift arm, raise arm | `camera_up` |

## 使用场景

### 单一目的、明确指令时调用

当用户指令**明确且单一**时使用，例如：
- "帮我夹个萝卜"
- "把东西拿给我"
- "机械臂初始化"
- "抬起机械臂"

## ⚠️ 重要规则

1. **一次只发送一次**，不然会冲突
2. **执行前先查 `arm_group_status`**，如果是 `moving` 要等完成再发新动作
3. 动作执行期间（约2-3秒）不要发送其他动作指令
4. 动作组文件位于 `/home/ubuntu/software/arm_pc/ActionGroups/`

## 脚本方式 / Script

```bash
python3 ~/.openclaw/workspace/skills/claw_arm_group_control/scripts/arm_control.py --cmd voice_pick
```
