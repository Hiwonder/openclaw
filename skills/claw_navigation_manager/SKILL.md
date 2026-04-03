---
name: claw_navigation_manager
description: "机器人导航管理技能。支持普通导航(navigation_position.yaml)、智能工厂导航(smart_factory.yaml)、智能社区导航(smart_community.yaml)三种模式。通过获取导航模式、查询状态、获取位置列表、发送导航目标、等待到达等流程完成导航任务。"
---

# 导航管理器 / Navigation Manager

## 导航模式

通过参数 `navigation_mode` 设置，支持三种模式：

| 模式 | 配置文件 | 订阅状态话题 | 发布导航话题 | 消息类型 |
|------|----------|--------------|--------------|----------|
| `normal` | navigation_position.yaml | navigation_controller/reach_goal | navigation_controller/set_pose | SetPose2D |
| `smart_factory` | smart_factory.yaml | /road_network_navigator/reach_final | /request_waypoint | Int32 |
| `smart_community` | smart_community.yaml | /road_network_navigator/reach_final | /request_waypoint | Int32 |

## 服务列表 / Services

### 1. 获取导航模式
- **服务名**: `/claw_navigation_manager/get_navigation_mode`
- **类型**: `std_srvs/srv/Trigger`
- **用途**: 获取当前导航模式
- **返回**: `message` 字段，值为 `normal` / `smart_factory` / `smart_community`

```bash
ros2 service call /claw_navigation_manager/get_navigation_mode std_srvs/srv/Trigger {}
```

### 2. 导航状态查询
- **服务名**: `/claw_navigation_manager/navigation_status`
- **类型**: `std_srvs/srv/Trigger`
- **用途**: 查询当前导航状态
- **返回**: `message` 字段：
  - `ready` - 空闲，可接受新目标
  - `finish` - 已到达目标，任务完成
  - `moving to xxx` - 正在前往 xxx

```bash
ros2 service call /claw_navigation_manager/navigation_status std_srvs/srv/Trigger {}
```

### 3. 可用目的地列表
- **服务名**: `/claw_navigation_manager/list_positions`
- **类型**: `std_srvs/srv/Trigger`
- **用途**: 获取当前模式下的所有可用导航目的地
- **返回**: `message` 字段，逗号分隔的位置名列表

```bash
ros2 service call /claw_navigation_manager/list_positions std_srvs/srv/Trigger {}
```

### 4. 发送导航目标
- **服务名**: `/claw_navigation_manager/set_pose`
- **类型**: `interfaces/srv/SetString`
- **用途**: 发送导航目标位置名
- **请求**: `data: "位置名"`
- **返回**: 
  - `success: true, message: "true"` - 发送成功
  - `success: false, message: "can't find the navigation goal: xxx"` - 位置不存在

```bash
ros2 service call /claw_navigation_manager/set_pose interfaces/srv/SetString "{data: '动物园'}"
```

## 执行流程 / Execution Flow

### 完整导航流程

1. **获取导航模式** - 调用 `get_navigation_mode` 确认当前模式
2. **查询状态** - 调用 `navigation_status`，如果不是 `finish` 需要等待
3. **获取目的地列表** - 调用 `list_positions` 确认目的地存在
4. **发送目标** - 调用 `set_pose` 发送目的地名称
5. **发布 Mission 开始** - `Mission: 前往xxx`
6. **轮询状态** - 轮询 `navigation_status` 直到 `finish`
7. **发布 Mission 完成** - `Mission: 到达xxx`

### 示例：去超市

```bash
# 1. 获取导航模式
ros2 service call /claw_navigation_manager/get_navigation_mode std_srvs/srv/Trigger {}

# 2. 查询状态
ros2 service call /claw_navigation_manager/navigation_status std_srvs/srv/Trigger {}

# 3. 获取位置列表
ros2 service call /claw_navigation_manager/list_positions std_srvs/srv/Trigger {}

# 4. 发送目标
ros2 service call /claw_navigation_manager/set_pose interfaces/srv/SetString "{data: '超市'}"

# 5. 轮询直到到达
ros2 service call /claw_navigation_manager/navigation_status std_srvs/srv/Trigger {}
```

## 各模式可用目的地

### normal 模式
| 位置名 | 说明 |
|--------|------|
| 动物园 | zoo |
| 前台 | front desk |
| 家 / 原点 | home / origin |
| 航天基地 | space base |
| 足球场 | football field |
| 水果超市 | fruit supermarket |
| 图书馆 | library |

### smart_factory 模式
| 位置名 | ID |
|--------|-----|
| 原料仓 | 100 |
| 生产线 | 6 |
| 质检处 | 11 |
| 发货仓 | 14 |

### smart_community 模式
| 位置名 | ID |
|--------|-----|
| 超市 | 13 |
| 快递站 | 17 |
| 超市路口 | 5 |
| 公园 | 15 |
| 家 | 0 |

## 启动方式

```bash
# normal 模式
ros2 run openclaw_controller claw_navigation_manager --ros-args -p navigation_mode:=normal

# 智能工厂模式
ros2 run openclaw_controller claw_navigation_manager --ros-args -p navigation_mode:=smart_factory

# 智能社区模式
ros2 run openclaw_controller claw_navigation_manager --ros-args -p navigation_mode:=smart_community
```

## ⚠️ 重要规则

1. **发送前查状态** - 如果正在导航（`moving to xxx`），必须等 `finish` 才能发新目标
2. **确认目的地在列表中** - 发送前调用 `list_positions` 确认位置存在
3. **等待到达** - 发送目标后要轮询 `navigation_status` 确认到达（`finish`）
4. **Mission 播报** - 导航任务也需要发 Mission 开始和完成
   - 开始: `Mission: 前往xxx`
   - 完成: `Mission: 到达xxx`
