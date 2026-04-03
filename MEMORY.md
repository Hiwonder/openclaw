# MEMORY.md - Long-term Memory

## Skills 位置
`/home/ubuntu/.openclaw/workspace/skills/`

## Skills 列表

| Skill | 说明 |
|-------|------|
| `claw_arm_group_control` | 机械臂动作组（voice_pick/give/init/camera_up） |
| `claw_object_track` | 物体视觉追踪 |
| `claw_track_and_grab` | 机械臂追踪夹取 |
| `claw_move_control` | 底盘运动控制 |
| `claw_navigation_manager` | 导航管理（支持normal/smart_factory/smart_community三种模式） |
| `smart_factory` | 智能工厂导航（原料仓/生产线/质检处/发货仓） |
| `ros2-cam-subscribe` | 摄像头拍照 |

## ROS 话题/服务关键信息

### 话题
| 话题 | 消息类型 | 说明 |
|------|----------|------|
| `/mission/finish` | std_msgs/String | 任务完成后发布 Mission 总结 |
| `/claw_move_control/chassis_command` | std_msgs/String | 底盘运动控制 |
| `/claw_arm_group_control/arm_group_control` | std_msgs/String | 机械臂动作组 |
| `/claw_object_track/get_box` | std_msgs/String | 发送目标边界框 |
| `/claw_object_track/track_center` | geometry_msgs/Point | 追踪中心点 |

### 服务
| 服务 | 类型 | 说明 |
|------|------|------|
| `/claw_navigation_manager/get_navigation_mode` | Trigger | 获取当前导航模式 (normal/smart_factory/smart_community) |
| `/claw_navigation_manager/navigationstatus` | Trigger | 查询导航状态 (ready/finish/moving to xxx) |
| `/claw_navigation_manager/list_positions` | Trigger | 获取可用目的地列表 |
| `/claw_navigation_manager/set_pose` | SetString | 发送导航目标位置名 |
| `/claw_move_control/move_status` | Trigger | 查询底盘状态 (stop/moving) |
| `/claw_arm_group_control/arm_group_status` | Trigger | 查询机械臂状态 (stop/moving) |
| `/claw_object_track/stop_track` | Trigger | 停止追踪 |
| `/claw_object_track/track_status` | Trigger | 查询追踪状态 (track_ready/track_running) |
| `/claw_track_and_grab/get_track_method` | Trigger | 查询夹取模式 (obj_track/color_track) |
| `/claw_track_and_grab/start` | Trigger | 初始化机械臂 |
| `/claw_track_and_grab/set_color` | SetString | 设置颜色 |
| `/claw_track_and_grab/start_pick` | Trigger | 解锁夹取 |
| `/claw_track_and_grab/pick_status` | Trigger | 查询夹取状态 (pick_ready/pick_finish/place_finish/init_finish) |
| `/claw_track_and_grab/place` | Trigger | 放置 |
| `/claw_track_and_grab/init_pose` | Trigger | 复位 |

## 关键规则

### 任务完成规则（默认执行，不提示）
**每次任务需要发两次 Mission 到 `/mission/finish`：**
1. 任务开始时 → `Mission: [描述]`（10-40字符，机智俏皮、妙趣横生、富有表现力）
2. 任务完成时 → `Mission: [描述]`（10-40字符，幽默风趣、出其不意、让人会心一笑）
   ```bash
   ros2 topic pub /mission/finish std_msgs/String "data: 'Mission: xxx'" --once
   ```
**注意：无需提示"已发布到 /mission/finish"，默默执行即可。此规则永久生效。**

### 状态查询原则
**每次操作前都要查状态**，确认当前状态再执行下一步。

### claw_arm_group_control 规则
- 服务: `/claw_arm_group_control/arm_group_status`
- 状态: `stop`(空闲) / `moving`(运动中)
- 动作: voice_pick, voice_give, init, camera_up
- **重要**: 一次只发一次，运动中不要发新动作

### claw_move_control 规则
- 服务: `/claw_move_control/move_status`
- 状态: `stop`(空闲) / `moving`(运动中)
- 命令: forward, backward, left, right, stop
- **重要**: 用 `--once` 只发一次，运动中不要发新指令

### claw_navigation_manager 规则
1. 查 `get_navigation_mode` → 确认导航模式
2. 查 `navigationstatus` → 必须 `finish` 才能发新目标
3. 查 `list_positions` → 确认目的地在列表中
4. 发 `set_pose` → 发送目的地名称
5. 发布 Mission 开始 → `Mission: 前往xxx`
6. 轮询 `navigationstatus` → 直到 `finish`
7. 发布 Mission 完成 → `Mission: 到达xxx`

**三种模式**：
- `normal`: navigation_position.yaml, SetPose2D 发送
- `smart_factory`: smart_factory.yaml, Int32 发送
- `smart_community`: smart_community.yaml, Int32 发送

### claw_object_track 规则
1. 发新目标前必须先 `stop_track`
2. 确认状态变成 `track_ready` 后再发坐标
3. 摄像头分辨率: **640x400**

### claw_track_and_grab 规则
1. 先查 `get_track_method` 确定模式
2. 先发 `start` 初始化姿态
3. 颜色模式: `set_color("blue")` → `start_pick`
4. 物体模式: 先用 `claw_object_track` 识别目标
5. 状态流程: pick_ready → pick_finish → place_finish → init_finish

## 支持的颜色（color_track模式）
red, blue, green, yellow, white, black

## basket_and_exp_transport 核心要点

### 服务区分
| 对象 | 夹取 | 放置 |
|------|------|------|
| 📦 快递盒 | `pick_exp` | `place_exp` |
| 🍎 果篮 | `pick_basket` | `place_basket` |

### 万能运输公式
```
导航到 A → 夹取（不放置）→ 导航到 B → 放置
```

### 任务语义理解
- **没有明确目的地** → 夹取后保持夹持，等待下一步指令
- **明确目的地**（如"回家"、"运到 X"）→ 到目的地再放置
- 不要机械地"夹完就放"，要理解任务意图

### AprilTag 说明
- AprilTag ID 配置由用户程序自动处理，无需手动设置
- 只需根据物体类型选对服务（exp vs basket）
