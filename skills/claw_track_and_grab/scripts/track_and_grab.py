#!/usr/bin/env python3
"""
机械臂追踪夹取技能脚本
提供状态查询和服务调用封装
"""

import argparse
import subprocess
import time
import sys

# 服务类型
SET_STRING_SERVICE = "interfaces/srv/SetString"
TRIGGER_SERVICE = "std_srvs/srv/Trigger"


def call_service(service, service_type, request_data=""):
    """调用ROS2服务"""
    cmd = f"ros2 service call {service} {service_type} '{request_data}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout


def get_track_method():
    """查询夹取方式"""
    print("查询夹取方式...")
    result = call_service("/claw_track_and_grab/get_track_method", TRIGGER_SERVICE, "{}")
    if "obj_track" in result:
        return "obj_track"
    elif "color_track" in result:
        return "color_track"
    return None


def get_pick_status():
    """查询夹取状态"""
    result = call_service("/claw_track_and_grab/pick_status", TRIGGER_SERVICE, "{}")
    for line in result.split('\n'):
        if 'message:' in line:
            status = line.split('message:')[1].strip().strip("'\"")
            return status
    return None


def start():
    """初始化机械臂姿态"""
    print("初始化机械臂姿态...")
    return call_service("/claw_track_and_grab/start", TRIGGER_SERVICE, "{}")


def stop():
    """停止所有"""
    print("停止所有...")
    return call_service("/claw_track_and_grab/stop", TRIGGER_SERVICE, "{}")


def set_color(color):
    """设置目标颜色"""
    print(f"设置目标颜色: {color}")
    return call_service("/claw_track_and_grab/set_color", SET_STRING_SERVICE, f"{{data: '{color}'}}")


def start_pick():
    """解锁夹取"""
    print("解锁夹取...")
    return call_service("/claw_track_and_grab/start_pick", TRIGGER_SERVICE, "{}")


def place():
    """放置"""
    print("执行放置...")
    return call_service("/claw_track_and_grab/place", TRIGGER_SERVICE, "{}")


def init_pose():
    """机械臂复位"""
    print("机械臂复位...")
    return call_service("/claw_track_and_grab/init_pose", TRIGGER_SERVICE, "{}")


def wait_for_status(target_status, timeout=60, interval=2):
    """等待状态变为目标状态"""
    print(f"等待状态变为 {target_status}...")
    elapsed = 0
    while elapsed < timeout:
        status = get_pick_status()
        print(f"  当前状态: {status}")
        if status == target_status:
            print(f"  状态已达到: {target_status}")
            return True
        time.sleep(interval)
        elapsed += interval
    print(f"  超时，未达到目标状态 {target_status}")
    return False


def main():
    parser = argparse.ArgumentParser(description='机械臂追踪夹取技能')
    parser.add_argument('--status', action='store_true', help='查看当前状态')
    parser.add_argument('--method', action='store_true', help='查看夹取方式')
    parser.add_argument('--start', action='store_true', help='初始化机械臂姿态')
    parser.add_argument('--stop', action='store_true', help='停止所有')
    parser.add_argument('--color', type=str, help='设置目标颜色')
    parser.add_argument('--pick', action='store_true', help='解锁夹取')
    parser.add_argument('--place', action='store_true', help='执行放置')
    parser.add_argument('--init', action='store_true', help='机械臂复位')
    args = parser.parse_args()

    if args.status:
        status = get_pick_status()
        print(f"当前状态: {status}")
        return

    if args.method:
        method = get_track_method()
        print(f"夹取方式: {method}")
        return

    if args.stop:
        stop()
        return

    if args.start:
        start()
        return

    if args.color:
        set_color(args.color)
        return

    if args.pick:
        start_pick()
        return

    if args.place:
        place()
        return

    if args.init:
        init_pose()
        return

    # 无参数时显示帮助
    parser.print_help()


if __name__ == '__main__':
    main()
