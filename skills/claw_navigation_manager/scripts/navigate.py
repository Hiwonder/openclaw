#!/usr/bin/env python3
"""
导航管理脚本 - Navigation Manager Script
支持查询状态、获取位置列表、发送导航目标
"""

import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from interfaces.srv import SetString


class NavigationClient(Node):
    def __init__(self):
        super().__init__('navigation_client')
        
    def get_status(self):
        """查询导航状态"""
        client = self.create_client(Trigger, '/claw_navigation_manager/navigation_status')
        client.wait_for_service()
        future = client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self, future)
        return future.result().message
    
    def list_positions(self):
        """获取可用位置列表"""
        client = self.create_client(Trigger, '/claw_navigation_manager/list_positions')
        client.wait_for_service()
        future = client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self, future)
        return future.result().message
    
    def set_pose(self, position):
        """发送导航目标"""
        client = self.create_client(SetString, '/claw_navigation_manager/set_pose')
        client.wait_for_service()
        req = SetString.Request()
        req.data = position
        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future)
        result = future.result()
        return result.success, result.message


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Navigation Manager Client')
    parser.add_argument('--status', action='store_true', help='查询导航状态')
    parser.add_argument('--list', action='store_true', help='获取可用位置列表')
    parser.add_argument('--go', type=str, help='发送导航目标，如 --go "动物园"')
    args = parser.parse_args()
    
    rclpy.init()
    node = NavigationClient()
    
    if args.status:
        status = node.get_status()
        print(f"导航状态: {status}")
    elif args.list:
        positions = node.list_positions()
        print(f"可用位置: {positions}")
    elif args.go:
        success, message = node.set_pose(args.go)
        print(f"发送结果: success={success}, message={message}")
    else:
        print("请使用 --status, --list 或 --go 参数")
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
