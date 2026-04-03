---
name: claw_object_track
description: "目标追踪技能。流程：检查状态 -> 停止旧追踪 -> 拍照 -> 图像分析获取归一化坐标 -> 发送目标 -> 确认状态。追踪节点名字前缀为 /claw_object_track。"
---

# 目标追踪技能 / Object Tracking Skill

## 前提条件

追踪节点必须已启动：
```bash
ros2 run openclaw_controller object_track --ros-args -p enable_tracking:=true -p debug:=true
```

## 话题和服务（已改名为 claw_object_track）

| 类型 | 名字 | 用途 |
|------|------|------|
| 服务 | `/claw_object_track/stop_track` | 停止追踪 |
| 服务 | `/claw_object_track/track_status` | 查状态 |
| 话题 | `/claw_object_track/get_box` | 发新目标坐标 |
| 话题 | `/claw_object_track/track_center` | 追踪中心点 |

## 状态说明

- `track_ready` = 可以接收新目标
- `track_running` = 正在追踪中

## 完整追踪流程（Agent执行步骤）

### 1. 检查状态
```bash
ros2 service call /claw_object_track/track_status std_srvs/srv/Trigger {}
```

### 2. 如果是 track_running，先停止
```bash
ros2 service call /claw_object_track/stop_track std_srvs/srv/Trigger {}
# 等待0.5秒后确认状态变成 track_ready
```

### 3. 拍照
```bash
~/.openclaw/workspace/skills/ros2-cam-subscribe/scripts/cam_subscribe.sh \
  --topic /depth_cam/rgb0/image_raw \
  --output-dir ~/.openclaw/workspace/images \
  --timeout 5
```

### 4. 图像分析（Agent用image()工具）
- 分析图片找出目标
- 图像分辨率：640x400
- 返回归一化坐标 `[xmin, ymin, xmax, ymax]`，范围0-1

### 5. 发送目标
```bash
ros2 topic pub --once /claw_object_track/get_box std_msgs/msg/String \
  "{data: '{\"object\": \"目标名称\", \"box\": [xmin, ymin, xmax, ymax]}'}"
```

### 6. 确认状态
```bash
ros2 service call /claw_object_track/track_status std_srvs/srv/Trigger {}
# 应返回 track_running
```

## 辅助脚本

```bash
# 查看状态
python3 ~/.openclaw/workspace/skills/claw_object_track/scripts/track.py --status

# 停止追踪
python3 ~/.openclaw/workspace/skills/claw_object_track/scripts/track.py --stop

# 追踪目标（需要先分析好坐标）
python3 ~/.openclaw/workspace/skills/claw_object_track/scripts/track.py \
  --target "红色方块" --box "[0.5,0.5,0.8,0.8]"
```

## ⚠️ 分辨率校验

如果框选不准，可能是图像分辨率不匹配。需要**实际查询ROS2话题获取真实分辨率**：

```bash
# 查询摄像头实际分辨率
ros2 topic echo /depth_cam/rgb0/camera_info --once | grep -E "width:|height:"
```

当前记录分辨率：**640x400**

**图像分析时必须使用实际分辨率**，否则归一化坐标会偏差。

## ⚠️ 关键操作规则（重要！）

### 每次追踪新目标必须遵循以下流程：

```
1. 先查 track_status 确认状态
   ros2 service call /claw_object_track/track_status std_srvs/srv/Trigger {}

   - track_ready = 可以接收新目标
   - track_running = 正在追踪中

2. 如果是 track_running，必须先 stop_track
   ros2 service call /claw_object_track/stop_track std_srvs/srv/Trigger {}

3. 确认状态变成 track_ready 后，再发新目标坐标

4. 发送后确认状态变成 track_running
```

### 常见错误

❌ **没先 stop 就发新坐标** → 新目标被忽略，追踪的还是旧目标

✅ **正确流程**: stop → 确认track_ready → 发坐标 → 确认track_running

### 追踪夹取协作

当与 claw_track_and_grab 配合使用时：
- **先**用 claw_object_track 识别目标并追踪
- **再**用 claw_track_and_grab 的 start_pick 解锁夹取
- claw_track_and_grab 会自动接收 /claw_object_track/track_center 的中心点

## 关键规则

1. **每次发新目标前必须先 stop**
2. **确认状态变成 track_ready 后再发新坐标**
3. **发送后确认状态变成 track_running**
4. **图像分析时告诉模型分辨率是640x400，输出归一化坐标（0-1范围）**
