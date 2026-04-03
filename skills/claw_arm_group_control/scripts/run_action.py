#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机械臂动作组控制器
用于执行机械臂的预设动作，如抬高相机、放置、夹取等
"""

import sys
import time
import rclpy
from rclpy.node import Node
from servo_controller_msgs.msg import ServosPosition, ServoPosition
from servo_controller.action_group_controller import ActionGroupController
from servo_controller.bus_servo_control import set_servo_position

# 动作组文件路径
ACTION_GROUP_PATH = '/home/ubuntu/software/arm_pc/ActionGroups'

# 普通动作列表（等待2秒）
NORMAL_ACTIONS = [
    'garbage_pick_init', # 垃圾拾取初始化
    'pick_init',        # 拾取初始化
    'navigation_pick_init', # 导航拾取初始化
    'startup_init',     # 启动初始化
    'horizontal',       # 水平位置
    'line_follow_init', # 巡线初始化
]

# 放置/夹取动作列表（等待5秒）
PICK_PLACE_ACTIONS = [
    'navigation_place',      # 导航放置
    'navigation_place_llm',  # 导航放置(LLM版)
    'pick',                  # 夹取
    'navigation_pick',       # 导航夹取
    'navigation_pick_llm',   # 导航夹取(LLM版)
    'garbage_pick',          # 垃圾拾取
    'place_left',            # 放置到左边
    'place_right',           # 放置到右边
    'place_center',          # 放置到中间
    'place_food_waste',      # 放置厨余垃圾
    'place_hazardous_waste', # 放置有害垃圾
    'place_recyclable_waste', # 放置可回收垃圾
    'place_residual_waste',  # 放置其他垃圾
]

# 所有可用动作 / All available actions
AVAILABLE_ACTIONS = ['camera_up', 'init', 'voice_pick', 'voice_give'] + NORMAL_ACTIONS + PICK_PLACE_ACTIONS

class ArmActionController:
    def __init__(self):
        rclpy.init()
        self.node = Node('arm_action_controller')
        
        # 创建发布者
        self.servo_pub = self.node.create_publisher(
            ServosPosition, 
            'servo_controller', 
            1
        )
        
        # 创建动作组控制器（用于执行动作组）
        self.controller = ActionGroupController(
            self.servo_pub,
            ACTION_GROUP_PATH
        )
        
    def camera_up(self):
        """抬高相机 - 使用set_servo_position直接控制"""
        print("执行 camera_up（抬高相机）...")
        # 舵机位置：((1, 500), (2, 750), (3, 10), (4, 255), (5, 500), (10, 150))
        set_servo_position(self.servo_pub, 1, ((1, 500), (2, 750), (3, 10), (4, 255), (5, 500), (10, 150)))
        time.sleep(2)  # 等待机械臂到位
        print("camera_up 完成")
        return True
    
    def init(self):
        """初始化位置 - 使用set_servo_position直接控制 / Initialize position"""
        print("执行 init（初始化位置）... / Executing init...")
        # 舵机位置：((1, 500), (2, 700), (3, 50), (4, 150), (5, 500), (10, 500))
        set_servo_position(self.servo_pub, 1, ((1, 500), (2, 700), (3, 50), (4, 150), (5, 500), (10, 500)))
        time.sleep(2)  # 等待机械臂到位 / Wait for arm to reach position
        print("init 完成 / init completed")
        return True
    
    def voice_pick(self):
        """拿个萝卜 - 夹取萝卜 / Pick a carrot"""
        print("执行 voice_pick（拿个萝卜）... / Executing voice_pick (pick a carrot)...")
        # 舵机位置：需要根据实际动作组设置 / Servo positions: need to set based on actual action group
        # TODO: 根据实际动作组配置舵机位置
        set_servo_position(self.servo_pub, 1, ((1, 500), (2, 750), (3, 10), (4, 255), (5, 500), (10, 150)))
        time.sleep(2)  # 等待机械臂到位 / Wait for arm to reach position
        print("voice_pick 完成 / voice_pick completed")
        return True
    
    def voice_give(self):
        """拿给我 - 把物品递给用户 / Pass me the item"""
        print("执行 voice_give（拿给我）... / Executing voice_give (pass me)...")
        # 舵机位置：需要根据实际动作组设置 / Servo positions: need to set based on actual action group
        # TODO: 根据实际动作组配置舵机位置
        set_servo_position(self.servo_pub, 1, ((1, 500), (2, 700), (3, 50), (4, 150), (5, 500), (10, 500)))
        time.sleep(2)  # 等待机械臂到位 / Wait for arm to reach position
        print("voice_give 完成 / voice_give completed")
        return True
        
    def run_action(self, action_name):
        """执行指定动作"""
        if action_name not in AVAILABLE_ACTIONS:
            print(f"错误: 未知的动作 '{action_name}'")
            print(f"可用动作: {', '.join(AVAILABLE_ACTIONS)}")
            return False
        
        try:
            # camera_up, init, voice_pick, voice_give 使用直接控制 / Direct control actions
            if action_name == 'camera_up':
                return self.camera_up()
            elif action_name == 'init':
                return self.init()
            elif action_name == 'voice_pick':
                return self.voice_pick()
            elif action_name == 'voice_give':
                return self.voice_give()
            
            # 其他动作使用动作组
            print(f"执行动作: {action_name}")
            self.controller.run_action(action_name)
            
            # 根据动作类型设置不同的等待时间
            if action_name in PICK_PLACE_ACTIONS:
                wait_time = 5  # 放置/夹取动作等待5秒
                print(f"等待动作完成（放置/夹取动作，等待{wait_time}秒）...")
            else:
                wait_time = 2  # 普通动作等待2秒
                print(f"等待动作完成（普通动作，等待{wait_time}秒）...")
            
            time.sleep(wait_time)
            print(f"动作执行完成: {action_name}")
            return True
        except Exception as e:
            print(f"执行动作失败: {e}")
            return False
    
    def shutdown(self):
        """关闭节点"""
        self.node.destroy_node()
        rclpy.shutdown()


def main():
    if len(sys.argv) < 2:
        print("用法 / Usage: python3 run_action.py <动作名称 / action_name>")
        print(f"\n直接控制动作 / Direct control actions: camera_up, init, voice_pick, voice_give")
        print(f"\n普通动作（等待2秒）/ Normal actions (wait 2s): {', '.join(NORMAL_ACTIONS)}")
        print(f"\n放置/夹取动作（等待5秒）/ Pick/Place actions (wait 5s): {', '.join(PICK_PLACE_ACTIONS)}")
        sys.exit(1)
    
    action_name = sys.argv[1]
    
    controller = ArmActionController()
    try:
        success = controller.run_action(action_name)
    finally:
        controller.shutdown()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
