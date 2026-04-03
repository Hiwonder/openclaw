#!/usr/bin/env python3
# encoding: utf-8
"""
Publish object detection box to /object_track_detect/get_box topic
"""

import sys
import json
import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ObjectBox(Node):
    def __init__(self):
        super().__init__('object_box_publisher')
        self.pub = self.create_publisher(String, '/object_track_detect/get_box', 10)
        self.get_logger().info('Publisher created')

    def publish(self, object_name, box, response):
        msg = String()
        msg.data = json.dumps({
            "object": object_name,
            "box": box,           # normalized [xmin, ymin, xmax, ymax]
            "response": response
        })
        self.pub.publish(msg)
        self.get_logger().info(f'Published: {object_name}, box={box}')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        # Use a temporary node to output error, but we'll just print to stderr
        # Since node not yet initialized, using print for error message is acceptable
        print("Usage: publish_box.py <object_name> <box> <response>", file=sys.stderr)
        print("Example: publish_box.py 'blue trash can' '[0.45,0.40,0.56,0.57]' 'Blue trash can found'", file=sys.stderr)
        sys.exit(1)

    object_name = sys.argv[1]
    box_str = sys.argv[2]
    response = sys.argv[3]

    try:
        box = json.loads(box_str)
    except:
        box = [float(x.strip()) for x in box_str.strip('[]').split(',')]

    rclpy.init()
    node = ObjectBox()

    # Publish after a short delay to ensure subscriber is ready
    time.sleep(2)
    node.get_logger().info('Publishing message...')
    for i in range(2):
        node.publish(object_name, box, response)

    time.sleep(0.3)
    node.destroy_node()
    rclpy.shutdown()