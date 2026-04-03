---
name: ros2-cam-subscribe
description: "订阅ROS2摄像头图像话题并保存单帧图像到本地。用于：(1)订阅指定的图像话题 (2)获取并保存单帧图像 (3)如果指定话题不存在，自动检索环境中的rgb/image相关话题 (4)图像命名包含时间戳、话题名，便于追溯 (5)支持定位追踪模式，自动识别物体并发布xyxy坐标到追踪话题 / Subscribe to ROS2 camera image topics and save single frames locally. Features: (1) subscribe to specified image topic (2) capture and save single frame (3) auto-detect rgb/image topics (4) filename includes timestamp (5) support locate & track mode with automatic object detection and xyxy publishing."
---


# ROS2 摄像头图像订阅 / ROS2 Camera Image Subscription

## 功能模式 / Operation Modes

### 模式1: 拍照看图 (Take Photo)
用户说："拍照"、"看看"、"你看到了什么"
- 保存原始图像
- 返回图像内容描述

### 模式2: 定位并标框 (Locate & Mark)
用户说："找找xxx"、"帮我找xxx在哪里"
- 保存原始图像
- 调用图像分析获取 xyxy 坐标
- **在图像上绘制绿色矩形框**
- 保存带标注的图片
- 返回坐标 + 描述 + 图片路径

---

## 快速开始 / Quick Start

### 1. 环境说明 / Environment

⚠️ **重要**: 包装脚本 `cam_subscribe.sh` 会自动 `source ~/.zshrc` 加载 ROS2 环境（如 ROS_DOMAIN_ID 等）

### 2. 订阅并保存单帧图像 / Subscribe and Save Single Frame

```bash
~/.openclaw/workspace/skills/ros2-cam-subscribe/scripts/cam_subscribe.sh \
  --topic /depth_cam/rgb0/image_raw \
  --output-dir ~/.openclaw/workspace/images \
  --timeout 5
```

### 3. 发布 xyxy 到追踪话题 / Publish xyxy to Track Topic

```bash
~/.openclaw/workspace/skills/ros2-cam-subscribe/scripts/object_box.py \
  "blue trash can" "[0.15,0.42,0.35,0.78]" "已找到蓝色垃圾桶"
```

### 4. 带框标注保存 / Save with Bounding Box

```bash
~/.openclaw/workspace/skills/ros2-cam-subscribe/scripts/cam_subscribe.sh \
  --topic /depth_cam/rgb0/image_raw \
  --output-dir ~/.openclaw/workspace/images \
  --timeout 5 \
  --xyxy "0.15,0.42,0.35,0.78"
```

---

## 图像命名规则 / Filename Format

- 原始图像：`{YYYYMMDD_HHMMSS}.{ext}`
- 带框图像：`{YYYYMMDD_HHMMSS}_marked.{ext}`

---

## 脚本说明 / Scripts

### subscribe_and_save.py

功能：订阅 ROS2 话题，接收一帧图像后保存到本地

参数 / Parameters:
- `--topic` (必填)：要订阅的话题
- `--output-dir` (可选)：保存目录，默认 `~/ros2_images`
- `--timeout` (可选)：超时时间(秒)，默认 5
- `--format` (可选)：输出格式 `jpg` 或 `png`，默认 `jpg`
- `--xyxy` (可选)：归一化边界框坐标 `xmin,ymin,xmax,ymax`
