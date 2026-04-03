# OpenClaw

[English](README.md) | 中文

<p align="center">
  这是一个面向用户玩法的 OpenClaw 机器人源码仓库，把自然语言交互、ROS2 技能、导航、视觉追踪和夹取流程串到了一台具体机器人上。
</p>

## 产品概述

### 关于 OpenClaw

本仓库是接入 ROSOrin Pro 产品的 OpenClaw 功能源码，主要承担自然语言交互与机器人能力之间的连接工作。项目已经完成了移动底盘、机械臂、摄像头、导航模块以及技能调用链路的整合，可用于产品演示、场景扩展和功能二次开发。

基于这套源码，用户在 OpenClaw 中发出的指令可以进一步映射为具体的 ROS2 机器人动作，例如底盘移动、机械臂动作组执行、目标识别与追踪、自动夹取以及按地点名称进行导航。

对于希望在 ROSOrin Pro 上扩展交互能力、丰富场景玩法，或继续完善机器人应用流程的开发者和集成者来说，这个仓库提供了较为完整的参考实现。

### 它解决的是“机器人能用起来”这件事

这个项目不是只给你一堆底层话题名，而是把常用能力整理成用户能直接理解的玩法：

**底盘移动**：支持前进、后退、左转、右转、停止，也支持连续动作编排。

**机械臂动作组**：已经内置了拿取、递给用户、初始化、抬臂等预设动作，适合快速做互动演示。

**追踪夹取**：既支持按目标物体追踪，也支持按颜色追踪，然后进入自动夹取流程。

**场景导航**：支持普通导航、智能工厂、智能社区等模式，可以按地点名称直接导航。

## 功能与架构

### 用户可以怎么玩

从仓库内容来看，这套源码已经覆盖了几类很典型的用户玩法：

**自然语言控制机器人**：通过 `openclaw gateway run`、`openclaw tui`、`openclaw agent --agent main --message "..."` 等入口，把用户语言接入机器人控制。

**移动 + 机械臂联动**：先让机器人移动到位，再执行拿取、递送、复位等动作，适合导览、递物、课堂互动。

**看见再去抓**：支持目标追踪或颜色追踪，再接自动夹取，适合做“抓蓝色积木”“夹前面的目标物”这类玩法。

**按场景跑任务**：仓库已经内置了智能工厂和智能社区两套地点配置，可以跑“去超市”“去快递站”“去原料仓”“去发货仓”这类场景任务。

### 代码是怎么组织的

整个项目主要分成两层：

**`openclaw_controller/`**：一个 ROS2 Python 功能包，里面放了节点和启动文件，负责底盘控制、机械臂动作组、导航管理、目标追踪、追踪夹取、语音和 TTS 等能力。

**`skills/`**：OpenClaw 侧的技能定义和辅助脚本，告诉智能体该怎么调用 ROS2 的话题和服务，把“用户说的话”落成具体动作流程。

从启动文件和依赖关系可以看出来，这个仓库不是单独跑一条命令就完事的类型，而是要放进更大的 ROS2 工作空间里，和 `controller`、`kinematics`、`navigation`、`large_models`、`large_models_examples` 等包一起工作。

## 官方资源

### 幻尔科技官方

- **官方网站**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **产品页面**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **官方文档**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **技术支持**: support@hiwonder.com

## 快速开始

### 硬件准备

- 一套兼容 OpenClaw 的机器人硬件，通常包含移动底盘、机械臂和 RGB 摄像头
- 一台已经配置好 ROS2 的 Linux 设备
- 目标设备上已经安装并能正常运行 OpenClaw
- 与本仓库配套的上游 ROS2 功能包，例如控制、运动学、导航和大模型相关包

### 软件环境搭建

1. 把本仓库放进 ROS2 工作空间，常见方式是放到 `src/openclaw_controller`，或者放到你的机器人镜像约定的源码目录里。
2. 确认依赖的 ROS2 包和 OpenClaw 运行环境已经就绪。
3. 先启动 OpenClaw 网关：

```bash
openclaw gateway run
```

4. 再启动核心机器人控制：

```bash
ros2 launch openclaw_controller robot_base_control.launch.py
```

5. 如果要用导航能力，根据场景选择导航模式：

```bash
# 普通地图导航
ros2 launch openclaw_controller navigation_manager.launch.py navigation_mode:=normal

# 智能工厂演示
ros2 launch openclaw_controller navigation_manager.launch.py navigation_mode:=smart_factory

# 智能社区演示
ros2 launch openclaw_controller navigation_manager.launch.py navigation_mode:=smart_community
```

6. 按你的使用习惯选择 OpenClaw 入口：

```bash
# 面板
openclaw dashboard

# 终端界面
openclaw tui

# 直接给主智能体发一条指令
openclaw agent --agent main --message "前进1秒，然后把东西拿给我"
```

### 典型玩法

- **控制底盘移动**：通过 `claw_move_control` 技能执行单步或连续移动。
- **体验动作组**：通过 `voice_pick`、`voice_give`、`init`、`camera_up` 等动作快速完成演示。
- **按颜色夹取**：使用 `claw_track_and_grab` 的 `color_track` 模式，适合抓取颜色明显的目标。
- **按目标识别夹取**：结合 `claw_object_track` 和 `claw_track_and_grab` 做更明确的目标夹取。
- **跑场景任务**：在“家、超市、快递站、原料仓、生产线、质检处、发货仓”等地点之间执行导航任务。

## 仓库结构

```text
openclaw/
├── openclaw_controller/
│   ├── config/                  # 导航和场景配置
│   ├── launch/                  # ROS2 启动文件
│   ├── openclaw_controller/     # ROS2 Python 节点实现
│   ├── scripts/                 # 辅助脚本
│   └── test/                    # 基础测试
├── skills/
│   ├── claw_arm_group_control/  # 机械臂动作组
│   ├── claw_move_control/       # 底盘移动控制
│   ├── claw_navigation_manager/ # 按地点名导航
│   ├── claw_object_track/       # 视觉目标追踪
│   ├── claw_track_and_grab/     # 追踪夹取
│   └── ros2-cam-subscribe/      # 摄像头取图辅助
├── MEMORY.md                    # 项目侧长期记忆和规则
├── USER.md                      # 操作者配置说明
├── ROSOrinPro_Command           # 部署环境命令备忘
└── .clear_openclaw_confing.sh   # OpenClaw 本地配置清理脚本
```

## 社区与支持

- **GitHub Issues**: 用于提交 Bug、使用问题和功能建议
- **邮件支持**: support@hiwonder.com
- **项目定位**: 适合已有 OpenClaw 机器人方案上的演示、教学和二次开发

## 许可证

当前仓库里没有单独提供 `LICENSE` 文件。如果你准备二次分发、商用集成，或者公开发布基于它修改后的版本，建议先和项目维护方确认授权范围。

---

**幻尔科技** - 让机器人交互更容易搭起来，也更容易玩起来
