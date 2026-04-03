#!/usr/bin/env python3
"""
Execute action sequence / 执行动作序列
Receive JSON format action list and execute / 接收 JSON 格式的 action 列表并执行
"""

import argparse
import json

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class ActionExecutor(Node):
    def __init__(self, topic_name='/controller/cmd_vel'):
        super().__init__('action_executor')
        self.topic_name = topic_name
        self.publisher = self.create_publisher(Twist, topic_name, 10)
        self.get_logger().info(f'Initialized, publishing to {topic_name} / 初始化完成，发布到 {topic_name}')
        
    def stop(self):
        """Send stop command / 发送停止命令"""
        twist = Twist()
        self.publisher.publish(twist)
        
    def execute(self, action_list):
        """Execute action sequence / 执行动作序列"""
        for action in action_list:
            x, y, z, t = action
            
            # If it's stop/pause command (x=y=z=0) / 如果是停止/暂停指令 (x=y=z=0)
            if x == 0 and y == 0 and z == 0:
                # t > 0 means pause, t = 0 means immediate stop / t > 0 表示暂停，t = 0 表示立即停止
                if t > 0:
                    self.get_logger().info(f'Pausing / 暂停: t={t}s')
                    start_time = self.get_clock().now()
                    timeout_duration = rclpy.duration.Duration(seconds=float(t))
                    while rclpy.ok():
                        self.stop()
                        rclpy.spin_once(self, timeout_sec=0.05)
                        elapsed = self.get_clock().now() - start_time
                        if elapsed > timeout_duration:
                            break
                else:
                    self.stop()
                continue
                
            twist = Twist()
            twist.linear.x = float(x)
            twist.linear.y = float(y)
            twist.linear.z = 0.0
            twist.angular.x = 0.0
            twist.angular.y = 0.0
            twist.angular.z = float(z)
            
            self.get_logger().info(f'Executing / 执行: x={x}, y={y}, z={z}, t={t}s')
            
            # Keep publishing / 持续发布
            start_time = self.get_clock().now()
            timeout_duration = rclpy.duration.Duration(seconds=float(t))
            
            while rclpy.ok():
                self.publisher.publish(twist)
                rclpy.spin_once(self, timeout_sec=0.05)
                elapsed = self.get_clock().now() - start_time
                if elapsed > timeout_duration:
                    break
            
            # Brief pause / 短暂停顿
            rclpy.spin_once(self, timeout_sec=0.2)
        
        # Final stop / 最后停止
        self.stop()
        self.get_logger().info('Action sequence completed, stopped / 动作序列执行完成，已停止')


def main(args=None):
    parser = argparse.ArgumentParser(description='Execute action sequence / 执行动作序列')
    parser.add_argument('--actions', '-a', type=str, required=True, help='JSON format action list, e.g. "[[0.15, 0, 0, 2], [0, 0, 0, 0]]" / JSON 格式的动作列表，如 "[[0.15, 0, 0, 2], [0, 0, 0, 0]]"')
    parser.add_argument('--topic', type=str, default='/controller/cmd_vel', help='cmd_vel topic / cmd_vel话题')
    
    parsed_args, _ = parser.parse_known_args(args)
    
    # Parse JSON / 解析 JSON
    try:
        action_list = json.loads(parsed_args.actions)
    except json.JSONDecodeError:
        print(f"JSON parse failed / JSON 解析失败: {parsed_args.actions}")
        return
    
    print(f"Executing actions / 执行动作: {action_list}")
    
    # Execute / 执行
    rclpy.init()
    node = ActionExecutor(parsed_args.topic)
    node.execute(action_list)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
