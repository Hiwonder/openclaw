# OpenClaw

English | [中文](README_cn.md)

<p align="center">
  OpenClaw source code and playbook for one user-facing robot setup, combining natural-language control, ROS2 skills, navigation, vision tracking, and grasping.
</p>

## Product Overview

### About OpenClaw

This repository contains the OpenClaw integration source code used in the ROSOrin Pro product. It serves as the connection layer between natural-language interaction and robot-side capabilities, bringing together the mobile base, robotic arm, camera, navigation modules, and skill invocation pipeline for demos, scenario extensions, and secondary development.

With this codebase, user instructions received by OpenClaw can be translated into practical ROS2 robot actions, including chassis movement, preset arm motions, target detection and tracking, automatic grasping, and destination-based navigation.

For developers and integrators who want to extend interaction workflows, enrich application scenarios, or build on top of ROSOrin Pro, this repository provides a concrete and reusable reference implementation.

### Built Around Real Robot Tasks

Instead of exposing only low-level ROS2 topics, this codebase packages common robot behaviors into reusable capabilities:

**Move the robot**: The chassis can execute single or chained commands such as forward, backward, left, right, and stop.

**Run arm actions quickly**: Preset arm-group motions like pick, give, init, and camera-up are ready for direct use.

**Track and grab objects**: The system supports both object-based tracking and color-based tracking, then hands the target over to the grab pipeline.

**Navigate by scene**: The robot can move to named destinations in normal maps, smart factory scenes, and smart community scenes.

## Features & Architecture

### What Users Can Do

This repository already covers several user-facing play styles:

**Natural-language robot control**: OpenClaw can serve as the front end through commands such as `openclaw gateway run`, `openclaw tui`, and `openclaw agent --agent main --message "..."`.

**Mobile manipulation**: Users can ask the robot to move, then perform an arm action, which is a practical pattern for delivery, presentation, and classroom interaction.

**Visual pick-and-place**: The robot can track a detected object or a target color, then perform grasping and optional placement.

**Scene-based navigation**: The built-in configs already define destination sets for factory-style and community-style demos, such as home, supermarket, express station, raw material warehouse, production line, quality check, and shipping area.

### How The Stack Is Organized

The project is split into two main layers:

**`openclaw_controller/`**: A ROS2 Python package that provides executable nodes and launch files for chassis control, arm-group control, navigation, object tracking, track-and-grab, TTS, and voice integration.

**`skills/`**: User-oriented skill definitions and helper scripts that describe how OpenClaw should call ROS2 services and topics for movement, navigation, tracking, grasping, and camera subscription.

The current launch and config files show that this repository is designed to sit inside a larger ROS2 workspace and work together with packages such as `controller`, `kinematics`, `navigation`, `large_models`, `large_models_examples`, and related robot drivers.

## Official Resources

### Official Hiwonder

- **Official Website**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **Product Page**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **Official Documentation**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **Technical Support**: support@hiwonder.com

## Getting Started

### Hardware Requirements

- An OpenClaw-compatible robot setup with a mobile base, robotic arm, and RGB camera
- A Linux device with ROS2 already prepared for the robot
- A working OpenClaw environment on the target machine
- The required upstream ROS2 packages used by this repository, including controller, kinematics, navigation, and large-model related packages

### Software Setup

1. Put this repository into your ROS2 workspace, typically as `src/openclaw_controller` or in a matching source layout used by your robot image.
2. Make sure the dependent ROS2 packages and OpenClaw runtime are already installed and working.
3. Start the OpenClaw gateway:

```bash
openclaw gateway run
```

4. Start the core robot control launch:

```bash
ros2 launch openclaw_controller robot_base_control.launch.py
```

5. If you need navigation, start the navigation manager with the right mode:

```bash
# normal map navigation
ros2 launch openclaw_controller navigation_manager.launch.py navigation_mode:=normal

# smart factory demo
ros2 launch openclaw_controller navigation_manager.launch.py navigation_mode:=smart_factory

# smart community demo
ros2 launch openclaw_controller navigation_manager.launch.py navigation_mode:=smart_community
```

6. Use the OpenClaw interface that fits your workflow:

```bash
# Web/dashboard
openclaw dashboard

# Terminal UI
openclaw tui

# Send a direct instruction to the main agent
openclaw agent --agent main --message "Move forward for 1 second, then give me the item"
```

### Example Play Modes

- **Drive the robot**: Send movement commands through the `claw_move_control` skill.
- **Pick and hand over**: Trigger preset arm actions such as `voice_pick` and `voice_give`.
- **Grab by color**: Use `claw_track_and_grab` in `color_track` mode for simple color-based pickup tasks.
- **Grab by target**: Pair `claw_object_track` with `claw_track_and_grab` for object-aware pickup.
- **Run scene demos**: Navigate among named places like home, supermarket, express station, raw material warehouse, production line, quality check, and shipping area.

## Repository Structure

```text
openclaw/
├── openclaw_controller/
│   ├── config/                  # Navigation and scene configuration
│   ├── launch/                  # ROS2 launch files for core features
│   ├── openclaw_controller/     # ROS2 Python nodes
│   ├── scripts/                 # Helper scripts
│   └── test/                    # Basic package tests
├── skills/
│   ├── claw_arm_group_control/  # Preset robotic arm actions
│   ├── claw_move_control/       # Chassis movement control
│   ├── claw_navigation_manager/ # Named-destination navigation
│   ├── claw_object_track/       # Visual target tracking
│   ├── claw_track_and_grab/     # Tracking-based grasping
│   └── ros2-cam-subscribe/      # Camera capture helpers
├── MEMORY.md                    # Project-side long-term usage notes
├── USER.md                      # Human/operator profile notes
├── ROSOrinPro_Command           # Command memo for deployed environments
└── .clear_openclaw_confing.sh   # Cleanup script for local OpenClaw config
```

## Community & Support

- **GitHub Issues**: Use Issues for bug reports, usage questions, and feature requests
- **Email Support**: support@hiwonder.com
- **Project Customization**: Suitable for internal demos, teaching projects, and secondary development on top of an existing OpenClaw robot deployment

## License

This repository does not currently include a standalone `LICENSE` file. If you plan to redistribute, modify for commercial delivery, or integrate it into a public project, confirm the licensing terms with the project owner first.

---

**Hiwonder** - Making robot interaction easier to build, demo, and extend
