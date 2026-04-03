# OpenClaw

English | [中文](README_cn.md)

<p align="center">
  An OpenClaw experience built on ROSOrin Pro, designed to make robot interaction more natural, more engaging, and better suited for demos, education, and creative projects.
</p>

## Product Overview

### About OpenClaw

OpenClaw is an interaction and play-style solution integrated into the ROSOrin Pro product line. It connects natural-language interaction with the robot's mobile base, robotic arm, camera, and navigation capabilities, making it easier to experience complete workflows such as movement, recognition, tracking, grasping, and scene-based navigation.

Compared with traditional robot control flows that are mainly oriented toward low-level debugging, OpenClaw is designed to be more approachable, more presentable, and more expandable. It is well suited for makers, university students, robotics clubs, teaching labs, and anyone who wants to build compelling robot demos on top of ROSOrin Pro.

By building on ROSOrin Pro hardware and ROS2 capabilities, OpenClaw helps turn core robot functions into a smoother and more engaging user experience, so the robot is not only controllable, but also expressive and ready for real interaction scenarios.

### Why It Fits Demos And Education

OpenClaw is not simply a collection of robot functions. It organizes those functions into a user-facing experience that is easier to understand, easier to demonstrate, and easier to extend.

**More natural interaction**: Users can approach the robot through task-oriented instructions instead of relying only on low-level topics and parameters.

**A more complete workflow**: Chassis movement, arm actions, visual tracking, automatic grasping, and destination-based navigation are connected into a more coherent experience.

**Better for teaching and showcasing**: It is easier to build visible outcomes for classrooms, maker activities, lab demos, and robotics project presentations.

**Ready for extension**: Existing play modes can be expanded with new scenes, actions, skills, and interaction logic as projects grow.

## Features & Architecture

### Core Experiences

OpenClaw already supports several user-facing robot experiences:

**Natural-language interaction**: OpenClaw provides an entry point that helps the robot feel easier to instruct, easier to demonstrate, and easier to interact with.

**Mobile base and arm collaboration**: The robot can move first, then perform pickup, handover, or reset actions, which works well for guided demos and interactive presentations.

**Visual tracking and grasping**: Both object-based tracking and color-based tracking are supported for pick-and-grab style applications.

**Scene-based navigation**: Normal navigation, smart factory, and smart community modes make it possible to build more scenario-driven experiences around named destinations.

### Capability Layout

At a high level, this solution is organized into several layers:

**Interaction layer**: Receives natural-language instructions from OpenClaw and organizes the corresponding task flow.

**Control layer**: Connects ROS2-based chassis control, arm action groups, visual tracking, grasping, and navigation features.

**Experience layer**: Combines movement, pickup, handover, and navigation into play styles that are easier for users to understand and enjoy.

This makes OpenClaw more than a control entry point on ROSOrin Pro. It becomes a user-oriented interaction layer that helps transform robot capabilities into clearer, richer, and more engaging experiences.

## Official Resources

### Official Hiwonder

- **Official Website**: [https://www.hiwonder.com/](https://www.hiwonder.com/)
- **Technical Support**: support@hiwonder.com

### OpenClaw Official

- **OpenClaw Repository**: [https://github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)

## Getting Started

### Basic Preparation

Before getting started, prepare the following:

- A ROSOrin Pro device with the OpenClaw solution integrated
- A working ROS2 robot environment
- Connected robot hardware such as the mobile base, robotic arm, camera, and navigation-related modules

### OpenClaw CLI

Here are the most common OpenClaw commands for daily use:

```bash
# Start the gateway
openclaw gateway run

# View logs
openclaw logs --follow

# Check gateway status
openclaw gateway status

# Open the dashboard
openclaw dashboard

# Open the terminal UI
openclaw tui

# Configure models / channels
openclaw configure

# Disable auto-start
systemctl --user disable openclaw-gateway

# Stop the current service
systemctl --user stop openclaw-gateway
```

### Thinking Modes

You can switch the model thinking level based on task complexity:

```text
/think:low
/think:medium
/thinking big
/think:off
```

### Agents And Skills

OpenClaw supports checking agent bindings, sending direct instructions to the main agent, and listing available skills:

```bash
# List agents and bindings
openclaw agents list --bindings

# Send a message to the main agent
openclaw agent --agent main --message "Help me check today's weather"

# List available skills
openclaw skills list --eligible

# Install a new skill
npm clawhub install xxxx
```

### ROS2 Startup And Control

ROS2 packages are typically located in:

```text
/home/ubuntu/ros2_ws/src
```

Start the robot control stack:

```bash
ros2 launch openclaw_controller robot_base_control.launch.py
```

### Chassis Control Example

For debugging, you can publish directly to the ROS2 topic:

```bash
ros2 topic pub --once /claw_move_control/chassis_command std_msgs/msg/String "{data: 'forward 1, stop 0.5, backward 2'}"
```

In OpenClaw, a user can send a natural instruction such as:

```text
Move forward for 1 second, then backward for 2 seconds
```

### Camera Recognition Example

With a vision-capable model enabled, the robot can be asked to describe what it sees:

```text
Look at what is in front of you and tell me what you see
```

### Preset Arm Action Example

For debugging, you can trigger a preset arm action directly:

```bash
ros2 topic pub --once /claw_arm_group_control/arm_group_control std_msgs/msg/String "{data: 'voice_pick'}"
```

In OpenClaw, a user can simply type:

```text
Pick it up
Hand it to me
```

### Typical Experiences

- **Movement control**: Try forward, backward, turning, and chained motion control.
- **Preset arm actions**: Experience arm pickup, handover, and initialization actions.
- **Target pickup**: Try color-based grasping or object-aware grasping.
- **Scene navigation**: Run tasks among places such as home, supermarket, express station, raw material warehouse, production line, quality check, and shipping area.

### Configuration Cleanup

If you need to prepare an image or clear local configuration data, you can use the cleanup script included in this repository. It removes local model, session, and memory-related data.

```bash
chmod +x .clear_openclaw_confing.sh
zsh .clear_openclaw_confing.sh
```

In deployment environments, this script is typically placed at:

```text
/home/ubuntu/.openclaw/.clear_openclaw_confing.sh
```

## Repository Structure

```text
openclaw/
├── openclaw_controller/         # ROS2 control package and launch files
├── skills/                      # OpenClaw skills and helper scripts
├── MEMORY.md                    # Project-side notes and rules
├── USER.md                      # User-side configuration notes
├── ROSOrinPro_Command           # Deployment command reference
└── .clear_openclaw_confing.sh   # Local configuration cleanup script
```

## Community & Support

- **GitHub Issues**: Report issues and submit feature suggestions
- **Email Support**: support@hiwonder.com
- **Documentation**: Complete tutorials and guides

## License

This project is open-source and available for educational and research purposes.

---

**Hiwonder** - Empowering innovation in robotics education
