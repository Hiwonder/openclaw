# OpenClaw

[English](README.md) | 中文

<p align="center">
  基于 ROSOrin Pro 的 OpenClaw 交互方案，让机器人从“能控制”进一步走向“更自然、更好玩、更适合展示与教学”。
</p>

## 产品概述

### 关于 OpenClaw

OpenClaw 是接入 ROSOrin Pro 产品中的一套机器人交互与玩法方案。它将自然语言交互能力与底盘、机械臂、摄像头、导航等机器人能力打通，让用户可以用更直观的方式体验移动、识别、追踪、夹取和导航等完整流程。

相较于传统只面向开发调试的控制方式，OpenClaw 更强调“可体验、可展示、可扩展”。对于创客、大学生、机器人社团、教学实验室以及需要快速搭建演示场景的用户来说，它能够明显降低体验门槛，同时保留足够的扩展空间。

依托 ROSOrin Pro 的硬件与 ROS2 能力，OpenClaw 可以把常见的机器人功能组织成更自然的交互体验，让一台机器人不只是“能动起来”，而是真正具备更完整的互动表现力。

### 为什么它更适合展示与教学

OpenClaw 的价值不只是把多个功能拼在一起，而是把它们整理成用户容易理解、容易复现、也更容易继续扩展的玩法体系。

**更自然的交互方式**：用户不需要只记一堆底层话题和参数，而是可以围绕实际任务来体验机器人能力。

**更完整的功能闭环**：从底盘移动、机械臂动作，到视觉识别、目标追踪、自动夹取，再到按地点导航，体验链路更加完整。

**更适合教学展示**：无论是课堂演示、创客活动、实验室展示，还是比赛项目验证，都更容易快速形成可见成果。

**更适合继续拓展**：在现有玩法基础上，可以继续增加场景、动作、技能和交互逻辑，逐步形成更丰富的应用内容。

## 功能与架构

### 核心玩法

OpenClaw 已经围绕用户体验整理出几类典型玩法：

**自然语言控制机器人**：通过 OpenClaw 作为交互入口，让机器人更容易进入“能听懂、能执行、能反馈”的体验模式。

**底盘移动与机械臂联动**：机器人可以先移动到指定位置，再执行拿取、递送、复位等动作，适合做导览、递物和互动展示。

**视觉识别与追踪夹取**：支持目标识别追踪和颜色追踪两类方式，适合做“找到目标并抓取”的应用演示。

**场景化导航**：支持普通导航、智能工厂、智能社区等模式，能够围绕地点名称完成更具场景感的任务流程。

### 能力组成

从整体能力上看，这套方案主要由几部分组成：

**交互层**：负责接收用户在 OpenClaw 中发出的自然语言指令，并组织对应任务流程。

**控制层**：负责连接 ROS2 下的底盘运动、机械臂动作组、视觉追踪、夹取控制与导航功能。

**玩法层**：围绕移动、抓取、递送、导航等实际使用场景，将能力组合成更容易演示和体验的机器人玩法。

这也意味着，OpenClaw 在 ROSOrin Pro 上不仅是一个控制入口，更是一套面向用户体验和场景展示的机器人交互方案。

## 官方资源

### 幻尔科技官方

- **官方网站**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **技术支持**: support@hiwonder.com

### OpenClaw 官方

- **OpenClaw 仓库**: [https://github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)

## 快速开始

### 基础准备

在开始体验之前，建议准备以下环境：

- 已集成 OpenClaw 方案的 ROSOrin Pro 设备
- 可正常运行的 ROS2 机器人环境
- 已接入的底盘、机械臂、摄像头及导航相关功能

### OpenClaw 命令行

以下是常用的 OpenClaw 基础命令：

```bash
# 启动网关
openclaw gateway run

# 查看日志
openclaw logs --follow

# 检查网关状态
openclaw gateway status

# 打开可视化面板
openclaw dashboard

# 打开命令行终端界面
openclaw tui

# 配置 models / channels
openclaw configure

# 禁用开机自启
systemctl --user disable openclaw-gateway

# 停止当前服务
systemctl --user stop openclaw-gateway
```

### 模型思考模式

在交互过程中，可以根据任务复杂度切换模型思考强度：

```text
/think:low
/think:medium
/thinking big
/think:off
```

### 智能体与技能

OpenClaw 支持查看智能体绑定情况、直接向主智能体发送指令，以及查看当前可用技能：

```bash
# 查看智能体列表和绑定信息
openclaw agents list --bindings

# 给主智能体发送消息
openclaw agent --agent main --message "帮我查一下今天的天气"

# 查看可用 skills
openclaw skills list --eligible

# 安装新的 skill
npm clawhub install xxxx
```

### ROS2 启动与控制

ROS2 功能包通常存放在：

```text
/home/ubuntu/ros2_ws/src
```

启动机器人底层控制：

```bash
ros2 launch openclaw_controller robot_base_control.launch.py
```

### 底盘移动示例

调试时，可以直接发送 ROS2 话题：

```bash
ros2 topic pub --once /claw_move_control/chassis_command std_msgs/msg/String "{data: 'forward 1, stop 0.5, backward 2'}"
```

在 OpenClaw 中，用户可以直接发送类似指令：

```text
前进1秒，后退两秒
```

### 摄像头识别示例

使用支持视觉的模型时，可以直接让机器人描述画面内容，例如：

```text
看看前面有什么，然后告诉我
```

### 机械臂动作组示例

调试时，可以直接发送机械臂动作组命令：

```bash
ros2 topic pub --once /claw_arm_group_control/arm_group_control std_msgs/msg/String "{data: 'voice_pick'}"
```

在 OpenClaw 中，用户可以直接输入：

```text
拔个萝卜
拿给我
```

### 典型体验内容

- **移动控制**：体验前进、后退、转向和连续运动控制。
- **动作组体验**：体验机械臂拿取、递送、初始化等固定动作。
- **目标夹取**：体验颜色追踪夹取或目标识别夹取。
- **场景导航**：体验“家、超市、快递站、原料仓、生产线、质检处、发货仓”等地点任务。

### 配置清理

如果需要输出镜像或清理本地配置，可以使用仓库内附带的清理脚本。该脚本会删除模型、会话、记忆等本地配置数据。

```bash
chmod +x .clear_openclaw_confing.sh
zsh .clear_openclaw_confing.sh
```

部署时，这个脚本通常放在：

```text
/home/ubuntu/.openclaw/.clear_openclaw_confing.sh
```

## 仓库结构

```text
openclaw/
├── openclaw_controller/         # ROS2 控制与启动文件
├── skills/                      # OpenClaw 技能与脚本
├── MEMORY.md                    # 项目侧长期规则与说明
├── USER.md                      # 用户配置说明
├── ROSOrinPro_Command           # 部署命令参考
└── .clear_openclaw_confing.sh   # 本地配置清理脚本
```

## 社区与支持

- **GitHub Issues**: 提交问题反馈和功能建议
- **邮件支持**: support@hiwonder.com
- **文档资料**: 完整的教程指南

## 许可证

本项目开源，可用于教育和研究目的。

---

**幻尔科技** - 赋能机器人教育创新
