#!/usr/bin/env zsh
# ROS2 摄像头图像订阅包装脚本 / ROS2 Camera Image Subscribe Wrapper
# 自动加载环境并执行 Python 脚本 / Auto-source environment and run Python script

# 加载 ROS2 环境 / Load ROS2 environment
source ~/.zshrc

# 转发所有参数给 Python 脚本 / Forward all args to Python script
exec python3 ~/.openclaw/workspace/skills/ros2-cam-subscribe/scripts/subscribe_and_save.py "$@"
