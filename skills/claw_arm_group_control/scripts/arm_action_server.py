#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机械臂动作控制服务
长期运行，接收动作名称后执行对应动作
"""

import sys
import time
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from interfaces.srv import SetString
from servo_controller_msgs.msg import ServosPosition
from servo_controller.action_group_controller import ActionGroupController
from servo_controller.bus_servo_control import set_servo_position

# 动作组文件路径
ACTION_GROUP_PATH = '/home/ubuntu/software/arm_pc/ActionGroups'

# 普通动作列表（等待2秒）
NORMAL_ACTIONS = [
    'garbage_pick_init',
    'pick_init',
    'navigation_pick_init',
    'startup_init',
    'horizontal',
    'line_follow_init',
]

# 放置/夹取动作列表（等待5秒）
PICK_PLACE_ACTIONS = [
    'navigation_place',
    'navigation_place_llm',
    'pick',
    'navigation_pick',
    'navigation_pick_llm',
    'garbage_pick',
    'place_left',
    'place_right',
    'place_center',
    'place_food_waste',
    'place_hazardous_waste',
    'place_recyclable_waste',
    'place_residual_waste',
]

# 直接控制的动作
DIRECT_ACTIONS = ['camera_up', 'init', 'voice_pick', 'voice_give']

# 所有可用动作
AVAILABLE_ACTIONS = DIRECT_ACTIONS + NORMAL_ACTIONS + PICK_PLACE_ACTIONS


class ArmActionServer(Node):
    def __init__(self):
        super().__init__('arm_action_server')
        
        # 创建发布者
        self.servo_pub = self.create_publisher(
            ServosPosition, 
            'servo_controller', 
            1
        )
        
        # 创建动作组控制器
        self.controller = ActionGroupController(
            self.servo_pub,
            ACTION_GROUP_PATH
        )
        
        # 创建服务 - 接收动作名称
        self.srv = self.create_service(
            SetString, 
            '~/execute_action', 
            self.execute_callback
        )
        
        self.get_logger().info('机械臂动作服务已启动')
        self.get_logger().info(f'可用动作: {", ".join(AVAILABLE_ACTIONS)}')
        self.get_logger().info('等待动作请求...')
    
    def camera_up(self):
        """抬高相机"""
        self.get_logger().info('执行 camera_up...')
        set_servo_position(self.servo_pub, 1, ((1, 500), (2, 750), (3, 10), (4, 255), (5, 500), (10, 150)))
        time.sleep(2)
        self.get_logger().info('camera_up 完成')
        return True
    
    def init(self):
        """初始化位置"""
        self.get_logger().info('执行 init...')
        set_servo_position(self.servo_pub, 1, ((1, 500), (2, 700), (3, 50), (4, 150), (5, 500), (10, 500)))
        time.sleep(2)
        self.get_logger().info('init 完成')
        return True
    
    def execute_callback(self, request, response):
        """服务回调：根据动作名称执行对应动作"""
        action_name = request.data
        self.get_logger().info(f'收到动作请求: {action_name}')
        
        if action_name not in AVAILABLE_ACTIONS:
            self.get_logger().error(f'未知的动作: {action_name}')
            response.success = False
            response.message = f'未知的动作: {action_name}。可用动作: {", ".join(AVAILABLE_ACTIONS)}'
            return response
        
        try:
            if action_name == 'camera_up':
                success = self.camera_up()
            elif action_name == 'init':
                success = self.init()
            else:
                success = self._run_action_group(action_name)
            
            response.success = success
            response.message = f'{action_name} 执行{"成功" if success else "失败"}'
            
        except Exception as e:
            self.get_logger().error(f'执行失败: {e}')
            response.success = False
            response.message = str(e)
        
        self.get_logger().info('等待下一个动作请求...')
        return response
    
    def _run_action_group(self, action_name):
        """执行动作组"""
        self.get_logger().info(f'执行动作组: {action_name}')
        self.controller.run_action(action_name)
        
        # 根据动作类型设置等待时间
        if action_name in PICK_PLACE_ACTIONS:
            wait_time = 5
            self.get_logger().info(f'等待{wait_time}秒（放置/夹取动作）...')
        else:
            wait_time = 2
            self.get_logger().info(f'等待{wait_time}秒（普通动作）...')
        
        time.sleep(wait_time)
        self.get_logger().info(f'动作组执行完成: {action_name}')
        return True


def main():
    rclpy.init()
    node = ArmActionServer()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
