#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机械臂动作服务节点
接收服务请求后执行动作，完成后退出
"""

import sys
import time
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
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

# 所有可用动作
AVAILABLE_ACTIONS = ['camera_up', 'init'] + NORMAL_ACTIONS + PICK_PLACE_ACTIONS


class ArmActionServiceNode(Node):
    def __init__(self, action_name):
        super().__init__('arm_action_service')
        self.action_name = action_name
        
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
        
        # 创建服务
        self.srv = self.create_service(
            Trigger, 
            '~/execute', 
            self.execute_callback
        )
        
        self.get_logger().info(f'动作服务已启动: {action_name}')
        self.get_logger().info('等待触发请求...')
    
    def camera_up(self):
        """抬高相机"""
        self.get_logger().info('执行 camera_up（抬高相机）...')
        set_servo_position(self.servo_pub, 1, ((1, 500), (2, 750), (3, 10), (4, 255), (5, 500), (10, 150)))
        time.sleep(2)
        self.get_logger().info('camera_up 完成')
        return True
    
    def init(self):
        """初始化位置"""
        self.get_logger().info('执行 init（初始化位置）...')
        set_servo_position(self.servo_pub, 1, ((1, 500), (2, 700), (3, 50), (4, 150), (5, 500), (10, 500)))
        time.sleep(2)
        self.get_logger().info('init 完成')
        return True
    
    def execute_callback(self, request, response):
        """服务回调：执行动作"""
        self.get_logger().info(f'收到执行请求: {self.action_name}')
        
        try:
            if self.action_name == 'camera_up':
                success = self.camera_up()
            elif self.action_name == 'init':
                success = self.init()
            elif self.action_name in AVAILABLE_ACTIONS:
                success = self._run_action_group()
            else:
                self.get_logger().error(f'未知的动作: {self.action_name}')
                response.success = False
                response.message = f'未知的动作: {self.action_name}'
                return response
            
            response.success = success
            response.message = f'{self.action_name} 执行{"成功" if success else "失败"}'
            
            # 执行完成后关闭节点
            self.get_logger().info('动作执行完成，节点即将退出...')
            time.sleep(0.5)
            self.destroy_node()
            rclpy.shutdown()
            
        except Exception as e:
            self.get_logger().error(f'执行失败: {e}')
            response.success = False
            response.message = str(e)
        
        return response
    
    def _run_action_group(self):
        """执行动作组"""
        self.get_logger().info(f'执行动作组: {self.action_name}')
        self.controller.run_action(self.action_name)
        
        # 根据动作类型设置等待时间
        if self.action_name in PICK_PLACE_ACTIONS:
            wait_time = 5
            self.get_logger().info(f'等待{wait_time}秒（放置/夹取动作）...')
        else:
            wait_time = 2
            self.get_logger().info(f'等待{wait_time}秒（普通动作）...')
        
        time.sleep(wait_time)
        self.get_logger().info(f'动作组执行完成: {self.action_name}')
        return True


def main():
    if len(sys.argv) < 2:
        print("用法: python3 arm_action_service.py <动作名称>")
        print(f"可用动作: {', '.join(AVAILABLE_ACTIONS)}")
        sys.exit(1)
    
    action_name = sys.argv[1]
    
    rclpy.init()
    node = ArmActionServiceNode(action_name)
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()


if __name__ == '__main__':
    main()
