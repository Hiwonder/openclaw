---
name: bask_and_exp_transport
description: "快递盒和果篮夹取运输技能。支持两种模式的 AprilTag 识别夹取：快递盒 (exp) 和果篮 (basket)。节点：/apriltag_control_node，通过状态轮询完成夹取和放置任务。"
---

# 快递盒和果篮夹取运输技能 / Basket & Exp Transport Skill

## 节点信息

- **节点名**: `/apriltag_control_node`
- **节点包**: `openclaw_controller`

### 启动节点

```bash
ros2 launch openclaw_controller apriltag_control_node.launch.py
```

## 服务列表

| 服务 | 类型 | 功能 |
|------|------|------|
| `/apriltag_control_node/get_arm_status` | `std_srvs/srv/Trigger` | 查询机械臂当前状态 |
| `/apriltag_control_node/pick_basket` | `std_srvs/srv/Trigger` | 果篮拾取 |
| `/apriltag_control_node/place_basket` | `std_srvs/srv/Trigger` | 果篮放置 |
| `/apriltag_control_node/pick_exp` | `std_srvs/srv/Trigger` | 快递盒拾取 |
| `/apriltag_control_node/place_exp` | `std_srvs/srv/Trigger` | 快递盒放置 |
| `/apriltag_control_node/init_pose` | `std_srvs/srv/Trigger` | 机械臂复位 |
| `/apriltag_control_node/clear_target` | `interfaces/srv/SetString` | 清空追踪目标 |
| `/apriltag_control_node/debug_pick_basket` | `std_srvs/srv/Trigger` | 调试 - 果篮拾取（带坐标校准） |
| `/apriltag_control_node/debug_pick_exp` | `std_srvs/srv/Trigger` | 调试 - 快递盒拾取（带坐标校准） |
| `/apriltag_control_node/set_debug_mode` | `interfaces/srv/SetString` | 设置调试模式 |

## 状态说明

| 状态 | 含义 | 后续动作 |
|------|------|---------|
| `ready` | 机械臂空闲，可以开始任务 | 触发 `pick_basket` 或 `pick_exp` |
| `pick_basket` / `pick_exp` | 夹取进行中 | 轮询等待完成 |
| `pick_basket_finish` / `pick_exp_finish` | 夹取完成 | 触发 `place_basket` 或 `place_exp`（如需要） |
| `place_basket` / `place_exp` | 放置进行中 | 轮询等待完成 |
| `place_basket_finish` / `place_exp_finish` | 放置完成 | 任务结束，可触发 `init_pose` 复位 |

## 两种夹取模式

### 模式 1: 果篮夹取 (basket)

通过 AprilTag ID `1` 识别果篮，使用独立的停止坐标参数。

**适用场景**: 夹取和运输果篮

**流程**:
```
1. get_arm_status → "ready"
       ↓
2. pick_basket → 视觉追踪 + 夹取
       ↓
3. 轮询 get_arm_status → "pick_basket_finish"
       ↓
4. place_basket（如需要）→ 放置
       ↓
5. 轮询 get_arm_status → "place_basket_finish"
       ↓
6. init_pose（如需要）→ 复位
```

### 模式 2: 快递盒夹取 (exp)

通过 AprilTag ID `0` 识别快递盒，使用独立的停止坐标参数。

**适用场景**: 夹取和运输快递盒

**流程**:
```
1. get_arm_status → "ready"
       ↓
2. pick_exp → 视觉追踪 + 夹取
       ↓
3. 轮询 get_arm_status → "pick_exp_finish"
       ↓
4. place_exp（如需要）→ 放置
       ↓
5. 轮询 get_arm_status → "place_exp_finish"
       ↓
6. init_pose（如需要）→ 复位
```

## 完整执行流程

### 果篮夹取完整命令

```bash
# 1. 检查初始状态
ros2 service call /apriltag_control_node/get_arm_status std_srvs/srv/Trigger "{}"
# 期望返回：message='ready'

# 2. 开始夹取
ros2 service call /apriltag_control_node/pick_basket std_srvs/srv/Trigger "{}"

# 3. 轮询夹取状态（每 3 秒一次，直到 pick_basket_finish）
ros2 service call /apriltag_control_node/get_arm_status std_srvs/srv/Trigger "{}"

# 4. 放置（如需要）
ros2 service call /apriltag_control_node/place_basket std_srvs/srv/Trigger "{}"

# 5. 轮询放置状态（每 3 秒一次，直到 place_basket_finish）
ros2 service call /apriltag_control_node/get_arm_status std_srvs/srv/Trigger "{}"

# 6. 复位（如需要）
ros2 service call /apriltag_control_node/init_pose std_srvs/srv/Trigger "{}"
```

### 快递盒夹取完整命令

```bash
# 1. 检查初始状态
ros2 service call /apriltag_control_node/get_arm_status std_srvs/srv/Trigger "{}"
# 期望返回：message='ready'

# 2. 开始夹取
ros2 service call /apriltag_control_node/pick_exp std_srvs/srv/Trigger "{}"

# 3. 轮询夹取状态（每 3 秒一次，直到 pick_exp_finish）
ros2 service call /apriltag_control_node/get_arm_status std_srvs/srv/Trigger "{}"

# 4. 放置（如需要）
ros2 service call /apriltag_control_node/place_exp std_srvs/srv/Trigger "{}"

# 5. 轮询放置状态（每 3 秒一次，直到 place_exp_finish）
ros2 service call /apriltag_control_node/get_arm_status std_srvs/srv/Trigger "{}"

# 6. 复位（如需要）
ros2 service call /apriltag_control_node/init_pose std_srvs/srv/Trigger "{}"
```

## 调试模式（坐标校准）

### 果篮坐标校准

```bash
# 触发调试模式（检测 10 次后自动保存坐标到 yaml）
ros2 service call /apriltag_control_node/debug_pick_basket std_srvs/srv/Trigger "{}"
```

### 快递盒坐标校准

```bash
# 触发调试模式（检测 10 次后自动保存坐标到 yaml）
ros2 service call /apriltag_control_node/debug_pick_exp std_srvs/srv/Trigger "{}"
```

### 配置文件位置

```yaml
# /home/ubuntu/ros2_ws/src/openclaw_controller/config/apriltag_control_roi.yaml
/**:
  ros__parameters:
    pick_stop_pixel_coordinate: [x, y]        # 果篮停止坐标
    pick_exp_stop_pixel_coordinate: [x, y]    # 快递盒停止坐标
```

## 两种模式对比

| 项目 | 果篮 (basket) | 快递盒 (exp) |
|------|--------------|-------------|
| **夹取服务** | `pick_basket` | `pick_exp` |
| **放置服务** | `place_basket` | `place_exp` |
| **状态值** | `pick_basket` / `pick_basket_finish` | `pick_exp` / `pick_exp_finish` |
| **AprilTag ID** | `1` | `0` |
| **YAML 参数** | `pick_stop_pixel_coordinate` | `pick_exp_stop_pixel_coordinate` |
| **调试服务** | `debug_pick_basket` | `debug_pick_exp` |
| **动作组** | `pick_basket` / `place_basket` | `pick_exp` / `place_exp` |

## 关键规则

1. **每次任务前先查 `get_arm_status`**，确认状态为 `ready` 再开始
2. **夹取和放置后都要轮询状态**，每 3 秒查询一次，直到对应的 `*_finish` 状态
3. **果篮和快递盒使用不同的 AprilTag ID**，不要混淆
4. **坐标校准模式**：使用 `debug_pick_basket` 或 `debug_pick_exp`，检测 10 次后自动保存
5. **放置是可选的**：根据任务需求决定是否执行 `place_*`

## 🧠 任务语义理解（重要）

### 万能运输公式
```
导航到 A → 夹取（不放置）→ 导航到 B → 放置
```

### 是否放置的判断原则
| 任务描述 | 理解 | 是否放置 |
|----------|------|----------|
| "去快递站取快递" | 只说取，没说放哪 | ❌ 不放置，等指令 |
| "取快递回家" | 目的地是家 | ✅ 到家再放 |
| "把快递从 A 运到 B" | 明确 A→B | ✅ 到 B 再放 |
| "去超市买水果" | 只说买，没说放哪 | ❌ 不放置，等指令 |

**核心原则**：没有明确最终目的地 → 夹取后保持夹持，等待下一步指令

## 自然语言触发参考

| 中文 | 模式 | 动作 |
|------|------|------|
| 夹取果篮 | basket | pick_basket |
| 放置果篮 | basket | place_basket |
| 夹取快递 | exp | pick_exp |
| 放置快递 | exp | place_exp |
| 机械臂复位 | - | init_pose |
| 校准果篮坐标 | basket | debug_pick_basket |
| 校准快递坐标 | exp | debug_pick_exp |
