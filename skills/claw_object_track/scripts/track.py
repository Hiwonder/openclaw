#!/usr/bin/env python3
"""
目标追踪技能脚本 - ROS通信部分
图像分析由Agent通过image()工具完成
"""

import argparse
import subprocess
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger
import json


class TrackClient(Node):
    def __init__(self, namespace='claw_object_track'):
        super().__init__('track_client')
        self.namespace = namespace
        
        # 服务
        self.status_client = self.create_client(Trigger, f'/{self.namespace}/track_status')
        self.stop_client = self.create_client(Trigger, f'/{self.namespace}/stop_track')
        
        # 话题发布
        self.box_pub = self.create_publisher(String, f'/{self.namespace}/get_box', 10)
        
    def wait_for_service(self, client, timeout_sec=10.0):
        """等待服务就绪"""
        if not client.wait_for_service(timeout_sec=timeout_sec):
            raise RuntimeError(f'Service {client.srv_name} not available')
        
    def get_status(self):
        """获取追踪状态"""
        self.wait_for_service(self.status_client)
        future = self.status_client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.result():
            return future.result().message
        return None
    
    def stop_track(self):
        """停止追踪"""
        self.wait_for_service(self.stop_client)
        future = self.stop_client.call_async(Trigger.Request())
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.result():
            return future.result().success
        return False
    
    def send_box(self, target_name, box):
        """发送目标框"""
        msg = String()
        msg.data = json.dumps({
            'object': target_name,
            'box': box
        })
        self.box_pub.publish(msg)
        return True


def capture_image(output_dir='/home/ubuntu/.openclaw/workspace/images', timeout=5):
    """拍照"""
    script_path = '/home/ubuntu/.openclaw/workspace/skills/ros2-cam-subscribe/scripts/cam_subscribe.sh'
    cmd = ['bash', script_path, '--topic', '/depth_cam/rgb0/image_raw', 
           '--output-dir', output_dir, '--timeout', str(timeout)]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
    
    for line in result.stdout.split('\n'):
        if 'Image saved' in line or '图像已保存' in line:
            parts = line.split('saved:')
            if len(parts) > 1:
                return parts[1].strip()
    return None


def main():
    parser = argparse.ArgumentParser(description='目标追踪 - ROS通信')
    parser.add_argument('--status', action='store_true', help='查看当前状态')
    parser.add_argument('--stop', action='store_true', help='停止追踪')
    parser.add_argument('--target', type=str, help='目标名称')
    parser.add_argument('--box', type=str, help='归一化坐标 [xmin,ymin,xmax,ymax]')
    args = parser.parse_args()
    
    rclpy.init()
    node = TrackClient()
    
    try:
        if args.status:
            status = node.get_status()
            print(f'当前状态: {status}')
            return
        
        if args.stop:
            print('正在停止追踪...')
            success = node.stop_track()
            if success:
                print('已停止追踪')
            else:
                print('停止追踪失败')
            time.sleep(0.5)
            status = node.get_status()
            print(f'当前状态: {status}')
            return
        
        if args.target and args.box:
            # 解析坐标
            box_str = args.box.strip('[]')
            box = [float(x.strip()) for x in box_str.split(',')]
            
            # 检查状态
            status = node.get_status()
            print(f'当前状态: {status}')
            
            if status == 'track_running':
                print('正在停止旧追踪...')
                node.stop_track()
                time.sleep(0.5)
                status = node.get_status()
                print(f'停止后状态: {status}')
            
            if status != 'track_ready':
                print(f'状态异常，无法开始追踪')
                return
            
            # 发送目标
            print(f'发送目标: {args.target}, 坐标: {box}')
            node.send_box(args.target, box)
            
            time.sleep(0.3)
            status = node.get_status()
            print(f'当前状态: {status}')
            return
        
        print('用法:')
        print('  查看状态: --status')
        print('  停止追踪: --stop')
        print('  追踪目标: --target "红色方块" --box "[0.5,0.5,0.8,0.8]"')
        
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
