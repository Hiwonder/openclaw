---
name: claw_track_and_grab
description: "机械臂追踪夹取技能。根据夹取方式(obj_track/color_track)执行追踪和夹取任务。节点: /claw_track_and_grab，支持两种模式：AI物体追踪和颜色追踪。"
---

# 机械臂追踪夹取技能 / Claw Track and Grab Skill

## 节点信息

- **节点名**: `/claw_track_and_grab`
- **节点包**: `openclaw_controller`

### 启动节点

```bash
# obj_track 模式（物体追踪）
ros2 run openclaw_controller claw_track_and_grab --ros-args -p track_method:=obj_track -p enable_disp:=true

# color_track 模式（颜色追踪）
ros2 run openclaw_controller claw_track_and_grab --ros-args -p track_method:=color_track -p enable_disp:=true
```

## 服务列表

| 服务 | 类型 | 功能 |
|------|------|------|
| `/claw_track_and_grab/get_track_method` | `std_srvs/srv/Trigger` | 查询夹取方式 |
| `/claw_track_and_grab/start` | `std_srvs/srv/Trigger` | 初始化机械臂姿态 |
| `/claw_track_and_grab/stop` | `std_srvs/srv/Trigger` | 停止所有 |
| `/claw_track_and_grab/set_color` | `interfaces/srv/SetString` | 设置目标颜色 |
| `/claw_track_and_grab/start_pick` | `std_srvs/srv/Trigger` | 解锁夹取 |
| `/claw_track_and_grab/pick_status` | `std_srvs/srv/Trigger` | 查询夹取状态 |
| `/claw_track_and_grab/place` | `std_srvs/srv/Trigger` | 执行放置动作 |
| `/claw_track_and_grab/init_pose` | `std_srvs/srv/Trigger` | 机械臂回到初始姿态 |

## 状态说明

| 状态 | 含义 | 后续动作 |
|------|------|---------|
| `pick_ready` | 可以开始夹取任务了 | 触发 `start` 开始追踪 |
| `pick_finish` | 夹取完成 | 触发 `place` 放置 |
| `place_finish` | 放置完成 | 触发 `init_pose` 复位 |
| `init_finish` | 复位完成 | 可以开始下一次任务 |

## 两种夹取模式

### 模式1: obj_track（物体追踪）

通过 `claw_object_track` 节点识别物体，发送中心点给本节点。

**适用场景**: 目标复杂、颜色不明显、需要精确识别特定物体

**流程**:
```
1. get_track_method → "obj_track"
       ↓
2. start → pick_ready
       ↓
3. claw_object_track 识别目标 + 发 get_box
       ↓
4. start_pick → 中心点追踪 → 自动夹取
       ↓
5. place（如需要）→ place_finish
       ↓
6. init_pose → init_finish
```

### 模式2: color_track（颜色追踪）

本节点直接通过LAB颜色空间识别目标。

**适用场景**: 目标颜色单一明显、背景干扰少

**支持颜色**: `red`, `blue`, `green`, `yellow`, `white`, `black`

**流程**:
```
1. get_track_method → "color_track"
       ↓
2. start → pick_ready
       ↓
3. set_color("颜色") → 开始颜色追踪
       ↓
4. start_pick → 颜色追踪 → 自动夹取
       ↓
5. place（如需要）→ place_finish
       ↓
6. init_pose → init_finish
```

## 完整执行流程

### 每次任务前必做

**1. 查询夹取方式**
```bash
ros2 service call /claw_track_and_grab/get_track_method std_srvs/srv/Trigger "{}"
```

### obj_track 模式完整命令

```bash
# 1. 初始化姿态
ros2 service call /claw_track_and_grab/start std_srvs/srv/Trigger "{}"

# 2. claw_object_track 识别目标
#    - stop_track → track_ready
#    - 拍照分析坐标
#    - 发 get_box → track_running

# 3. 解锁夹取
ros2 service call /claw_track_and_grab/start_pick std_srvs/srv/Trigger "{}"

# 4. 等待夹取完成（轮询 pick_status）
ros2 service call /claw_track_and_grab/pick_status std_srvs/srv/Trigger "{}"

# 5. 放置（如需要）
ros2 service call /claw_track_and_grab/place std_srvs/srv/Trigger "{}"

# 6. 复位
ros2 service call /claw_track_and_grab/init_pose std_srvs/srv/Trigger "{}"
```

### color_track 模式完整命令

```bash
# 1. 初始化姿态
ros2 service call /claw_track_and_grab/start std_srvs/srv/Trigger "{}"

# 2. 设置颜色（red/blue/green/yellow/white/black）
ros2 service call /claw_track_and_grab/set_color interfaces/srv/SetString "{data: 'blue'}"

# 3. 解锁夹取
ros2 service call /claw_track_and_grab/start_pick std_srvs/srv/Trigger "{}"

# 4. 等待夹取完成
ros2 service call /claw_track_and_grab/pick_status std_srvs/srv/Trigger "{}"

# 5. 放置（如需要）
ros2 service call /claw_track_and_grab/place std_srvs/srv/Trigger "{}"

# 6. 复位
ros2 service call /claw_track_and_grab/init_pose std_srvs/srv/Trigger "{}"
```

## 协作节点

### claw_object_track（物体追踪模式）

| 服务/话题 | 类型 | 功能 |
|------|------|------|
| `/claw_object_track/stop_track` | 服务 | 停止追踪 |
| `/claw_object_track/track_status` | 服务 | 查询追踪状态 |
| `/claw_object_track/get_box` | 话题 | 发送目标边界框 |
| `/claw_object_track/track_center` | 话题 | 发布追踪中心点 |

**注意**: obj_track 模式需要先启动 `claw_object_track` 节点并设置目标

## 关键规则

1. **每次任务前先查 `get_track_method`**，确认是哪种模式
2. **`start` 必须最先发**，初始化机械臂姿态
3. **每次操作前查 `pick_status`**，确认状态再执行下一步
4. **obj_track 模式**: 需要 `claw_object_track` 配合识别物体
5. **color_track 模式**: 直接 `set_color`，颜色用英文小写

## ⚠️ 重要操作流程（必须遵循）

### 标准流程（所有模式通用）

```
【任务开始】
    ↓
1. get_track_method → 确定是 obj_track 还是 color_track
    ↓
2. start → 初始化机械臂姿态 → pick_ready
    ↓
【根据模式选择下一步】
    ↓
【color_track 模式】
    set_color("blue") → start_pick → 等待 pick_finish
    ↓
【obj_track 模式】
    claw_object_track 发目标 → start_pick → 等待 pick_finish
    ↓
【pick_finish 后】
    ↓
3. place（如需要）→ place_finish
    ↓
4. init_pose → init_finish
    ↓
【任务完成】
```

### 状态轮询规则

- **每次操作后都要查 `pick_status`**，确认状态变了再继续
- 等待夹取时每2-3秒查一次
- 状态变了才执行下一步

### obj_track 模式详细流程

```
1. get_track_method → "obj_track"
    ↓
2. start → pick_ready
    ↓
3. claw_object_track 操作（见claw_object_track skill）
   - stop_track → track_ready
   - 拍照分析坐标
   - 发 get_box → track_running
    ↓
4. start_pick → pick_enabled
    ↓
5. 轮询 pick_status 直到 pick_finish
    ↓
6. place（如需要）→ place_finish
    ↓
7. init_pose → init_finish
```

### color_track 模式详细流程

```
1. get_track_method → "color_track"
    ↓
2. start → pick_ready
    ↓
3. set_color("颜色") → 支持: red, blue, green, yellow, white, black
    ↓
4. start_pick → pick_enabled
    ↓
5. 轮询 pick_status 直到 pick_finish
    ↓
6. place（如需要）→ place_finish
    ↓
7. init_pose → init_finish
```

### 与 claw_object_track 协作

obj_track 模式需要两个节点配合：

| 节点 | 负责 |
|------|------|
| `claw_object_track` | 视觉识别 + 追踪 + 发布中心点 |
| `claw_track_and_grab` | 接收中心点 + 云台跟随 + 夹取 |

**顺序**：先启动 claw_object_track 追踪目标，再让 claw_track_and_grab 接收中心点开始夹取

## 自然语言触发参考

| 中文 | 模式 | 命令 |
|------|------|------|
| 追踪夹取前面的红色方块 | obj_track | 拍照+分析+发送 |
| 追踪夹取前面的蓝色物体 | obj_track | 拍照+分析+发送 |
| 夹取前面的红色方块 | color_track | set_color("red") |
| 夹取蓝色的东西 | color_track | set_color("blue") |
| 停止追踪夹取 | - | stop |
| 机械臂复位 | - | init_pose |
