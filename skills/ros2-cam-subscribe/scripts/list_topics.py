#!/usr/bin/env python3
"""
List available image-related topics in ROS2 / 列出ROS2中可用的图像相关话题
"""

import argparse
import sys

import rclpy
from rclpy.node import Node


class TopicLister(Node):
    def __init__(self, keyword):
        super().__init__('topic_lister')
        self.keyword = keyword
        
    def list_topics(self):
        topic_names_and_types = self.get_topic_names_and_types()
        
        print(f"\n{'='*60}")
        print(f"ROS2 Available Topics (Filter: {self.keyword}) / ROS2 可用话题列表 (过滤: {self.keyword})")
        print(f"{'='*60}\n")
        
        found = False
        for topic_name, types in topic_names_and_types:
            # Check if keyword matches / 检查是否匹配关键词
            if self.keyword:
                keywords = self.keyword.split('|')
                if not any(kw.lower() in topic_name.lower() for kw in keywords):
                    continue
            
            # Only show image-related types / 只显示图像相关类型
            relevant_types = [t for t in types if 'Image' in t or 'CompressedImage' in t]
            
            if relevant_types or not self.keyword:
                found = True
                print(f"Topic / 话题: {topic_name}")
                print(f"  Type / 类型: {', '.join(types)}")
                if relevant_types:
                    print(f"  ✓ Image topic / 图像话题")
                print()
        
        if not found:
            print("No matching topics found / 未找到匹配的话题")
            
        print(f"{'='*60}\n")


def main(args=None):
    parser = argparse.ArgumentParser(description='List ROS2 image topics / 列出ROS2图像话题')
    parser.add_argument('--keyword', type=str, default='rgb|image|camera', 
                        help='Filter keyword, separated by | / 过滤关键词，用|分隔')
    
    args = parser.parse_args()
    
    rclpy.init(args=args)
    
    node = TopicLister(args.keyword)
    node.list_topics()
    
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
