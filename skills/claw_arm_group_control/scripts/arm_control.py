#!/usr/bin/env python3
"""
Execute arm action via topic / 通过话题发送机械臂动作命令
"""

import argparse
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ArmController(Node):
    def __init__(self, topic_name='/claw_arm_group_control/arm_group_control'):
        super().__init__('arm_controller')
        self.topic_name = topic_name
        self.publisher = self.create_publisher(String, topic_name, 10)
        self.get_logger().info(f'Publishing to / 发布到: {topic_name}')

    def execute(self, cmd_string):
        """Publish command string to topic / 发布命令字符串到话题"""
        msg = String()
        msg.data = cmd_string
        
        self.get_logger().info(f'Publishing / 发布: {cmd_string}')
        self.publisher.publish(msg)
        self.get_logger().info(f'Command sent / 命令已发送')


def main(args=None):
    parser = argparse.ArgumentParser(description='Execute arm action / 执行机械臂动作')
    parser.add_argument('--cmd', '-c', type=str, required=True, 
                        help='Action command: voice_pick, voice_give, init, camera_up')
    parser.add_argument('--topic', '-t', type=str, 
                        default='/claw_arm_group_control/arm_group_control',
                        help='Topic name / 话题名')
    
    parsed_args, _ = parser.parse_known_args(args)
    
    print(f'Executing action / 执行动作: {parsed_args.cmd}')
    
    rclpy.init()
    node = ArmController(parsed_args.topic)
    node.execute(parsed_args.cmd)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
