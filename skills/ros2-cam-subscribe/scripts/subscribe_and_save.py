#!/usr/bin/env python3
"""
Subscribe to ROS2 image topic and save single frame to local / 订阅ROS2图像话题并保存单帧图像到本地
支持带边界框标注保存
"""

import argparse
import os
import sys
from datetime import datetime

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
import numpy as np
from cv_bridge import CvBridge


def parse_xyxy(xyxy_str):
    """解析 xyxy 字符串为归一化坐标列表"""
    if not xyxy_str:
        return None
    try:
        coords = [float(x.strip()) for x in xyxy_str.split(',')]
        if len(coords) != 4:
            raise ValueError(f"Expected 4 values, got {len(coords)}")
        return coords  # [xmin, ymin, xmax, ymax]
    except Exception as e:
        raise ValueError(f"Invalid xyxy format: {xyxy_str}. Expected: xmin,ymin,xmax,ymax")


def xyxy_to_pixels(xyxy, img_width, img_height):
    """将归一化 xyxy 转换为像素坐标"""
    xmin, ymin, xmax, ymax = xyxy
    pxmin = int(xmin * img_width)
    pymin = int(ymin * img_height)
    pxmax = int(xmax * img_width)
    pymax = int(ymax * img_height)
    return pxmin, pymin, pxmax, pymax


def draw_bounding_box(image, xyxy, color=(0, 255, 0), thickness=3):
    """在图像上绘制边界框"""
    h, w = image.shape[:2]
    pxmin, pymin, pxmax, pymax = xyxy_to_pixels(xyxy, w, h)
    
    # 绘制矩形
    cv2.rectangle(image, (pxmin, pymin), (pxmax, pymax), color, thickness)
    
    # 添加坐标标签
    label = f"({xyxy[0]:.2f}, {xyxy[1]:.2f})"
    label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    cv2.rectangle(image, (pxmin, pymin - label_size[1] - 5), (pxmin + label_size[0], pymin), color, -1)
    cv2.putText(image, label, (pxmin, pymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
    
    return image


class ImageSubscriber(Node):
    def __init__(self, topic_name, output_dir, timeout, img_format, xyxy=None):
        super().__init__('image_saver')
        self.topic_name = topic_name
        self.output_dir = output_dir
        self.timeout = timeout
        self.img_format = img_format.lower()
        self.xyxy = parse_xyxy(xyxy) if xyxy else None
        self.bridge = CvBridge()
        self.image_received = False
        self.image_data = None
        
        # Create subscriber / 创建订阅者
        self.subscription = self.create_subscription(
            Image,
            topic_name,
            self.listener_callback,
            10)
        
        # Create output directory / 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.get_logger().info(f'Subscribing to topic / 订阅话题: {topic_name}')
        self.get_logger().info(f'Output directory / 输出目录: {output_dir}')
        self.get_logger().info(f'Timeout / 超时设置: {timeout}s')
        if self.xyxy:
            self.get_logger().info(f'Bounding box / 边界框: {self.xyxy}')
        
    def listener_callback(self, msg):
        if not self.image_received:
            try:
                # Convert ROS image to OpenCV format / 转换ROS图像消息到OpenCV格式
                self.image_data = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
                self.image_received = True
                self.get_logger().info('Image received / 已收到图像数据')
            except Exception as e:
                self.get_logger().error(f'Image conversion failed / 图像转换失败: {e}')
                sys.exit(1)
    
    def save_image(self):
        if self.image_data is None:
            self.get_logger().error('No image data received / 未收到图像数据')
            return False, None
        
        # Generate filename: timestamp / 生成文件名：时间戳
        now = datetime.now()
        timestamp = now.strftime('%Y%m%d_%H%M%S')
        
        filename = f'{timestamp}.{self.img_format}'
        filepath = os.path.join(self.output_dir, filename)
        
        # 如果有 xyxy，绘制边界框
        if self.xyxy:
            marked_image = draw_bounding_box(self.image_data.copy(), self.xyxy)
            marked_filename = f'{timestamp}_marked.{self.img_format}'
            marked_filepath = os.path.join(self.output_dir, marked_filename)
            
            # 保存带框图像
            if self.img_format == 'jpg' or self.img_format == 'jpeg':
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
                cv2.imwrite(marked_filepath, marked_image, encode_param)
            else:
                cv2.imwrite(marked_filepath, marked_image)
            
            self.get_logger().info(f'Marked image saved / 带框图像已保存: {marked_filepath}')
        
        # 保存原始图像
        if self.img_format == 'jpg' or self.img_format == 'jpeg':
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            cv2.imwrite(filepath, self.image_data, encode_param)
        else:
            cv2.imwrite(filepath, self.image_data)
        
        self.get_logger().info(f'Image saved / 图像已保存: {filepath}')
        return True, filepath


def main(args=None):
    parser = argparse.ArgumentParser(description='Subscribe to ROS2 image topic and save / 订阅ROS2图像话题并保存')
    parser.add_argument('--topic', type=str, required=True, help='ROS2 topic to subscribe / 要订阅的ROS2话题')
    parser.add_argument('--output-dir', type=str, default='~/ros2_images', help='Output directory / 输出目录')
    parser.add_argument('--timeout', type=int, default=5, help='Timeout in seconds / 超时时间(秒)')
    parser.add_argument('--format', type=str, default='jpg', choices=['jpg', 'png'], help='Output format / 输出格式')
    parser.add_argument('--xyxy', type=str, default=None, help='Normalized bounding box coords: xmin,ymin,xmax,ymax (0-1) / 归一化边界框坐标')
    
    parsed_args, _ = parser.parse_known_args()
    
    output_dir = os.path.expanduser(parsed_args.output_dir)
    
    # 验证 xyxy 格式
    if parsed_args.xyxy:
        xyxy = parse_xyxy(parsed_args.xyxy)
        for coord in xyxy:
            if not (0 <= coord <= 1):
                print(f"Warning: xyxy values should be in [0, 1], got {xyxy}", file=sys.stderr)
                break
    
    rclpy.init()
    
    node = ImageSubscriber(
        parsed_args.topic, 
        output_dir, 
        parsed_args.timeout, 
        parsed_args.format,
        parsed_args.xyxy
    )
    
    # Wait for image or timeout / 等待图像或超时
    start_time = node.get_clock().now()
    timeout_duration = rclpy.duration.Duration(seconds=parsed_args.timeout)
    
    while rclpy.ok() and not node.image_received:
        rclpy.spin_once(node, timeout_sec=0.1)
        elapsed = node.get_clock().now() - start_time
        if elapsed > timeout_duration:
            node.get_logger().error(f'Image wait timeout / 等待图像超时 ({parsed_args.timeout}s)')
            break
    
    # Save image / 保存图像
    if node.image_received:
        success, filepath = node.save_image()
        if success and parsed_args.xyxy:
            # 输出结果供解析
            print(f"SAVED_ORIGINAL:{filepath}")
            base, ext = os.path.splitext(filepath)
            print(f"SAVED_MARKED:{base}_marked{ext}")
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
