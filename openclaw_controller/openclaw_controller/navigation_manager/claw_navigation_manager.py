#!/usr/bin/env python3
# encoding: utf-8

import os
import yaml
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Int32
from std_srvs.srv import Trigger
from interfaces.srv import SetPose2D, SetString
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup


class ClawNavigationManager(Node):
    def __init__(self, name):
        super().__init__(name)

        self.navigation_status = "ready"
        self.reach_goal = False
        self.current_position = ""

        self.navigation_mode = self.declare_parameter('navigation_mode', 'normal').value

        if self.navigation_mode == 'smart_factory':
            self.position_dict = self.load_yaml_positions('smart_factory')
            self.reach_goal_topic = '/road_network_navigator/reach_final'
            self.nav_pub_type = 'int32'
            self.nav_topic = '/request_waypoint'
        elif self.navigation_mode == 'smart_community':
            self.position_dict = self.load_yaml_positions('smart_community')
            self.reach_goal_topic = '/road_network_navigator/reach_final'
            self.nav_pub_type = 'int32'
            self.nav_topic = '/request_waypoint'
        else:
            self.position_dict = self.load_yaml_positions('navigation_position')
            self.reach_goal_topic = 'navigation_controller/reach_goal'
            self.nav_pub_type = 'pose2d'
            self.nav_topic = 'navigation_controller/set_pose'

        timer_cb_group = ReentrantCallbackGroup()

        self.create_subscription(Bool, self.reach_goal_topic, self.reach_goal_callback, 1)

        if self.nav_pub_type == 'int32':
            self.nav_pub = self.create_publisher(Int32, self.nav_topic, 1)
        else:
            self.nav_client = self.create_client(SetPose2D, self.nav_topic)

        self.create_service(SetString, '~/set_pose', self.set_pose_callback)

        self.create_service(Trigger, '~/navigation_status', self.navigation_status_callback)

        self.create_service(Trigger, '~/list_positions', self.list_positions_callback)

        self.create_service(Trigger, '~/get_navigation_mode', self.get_navigation_mode_callback)
        

        self.client = self.create_client(Trigger, '/init_pose/init_finish')
        self.client.wait_for_service()
        self.get_logger().info('\033[1;32m%s\033[0m' % 'Navigation Manager started')
        self.get_logger().info('Navigation mode: %s' % self.navigation_mode)
        self.get_logger().info('Loaded %d navigation positions' % len(self.position_dict))
        self.get_logger().info('\033[1;32m[%s]\033[0m' % '🦞Node Start')

    def load_yaml_positions(self, config_name):
        config_path = '/home/ubuntu/ros2_ws/src/openclaw_controller/config/%s.yaml' % config_name
        position_dict = {}
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                if config_name == 'navigation_position':
                    if config and 'navigation_positions' in config:
                        for name, pose in config['navigation_positions'].items():
                            position_dict[name] = [
                                pose.get('x', 0.0),
                                pose.get('y', 0.0),
                                pose.get('roll', 0.0),
                                pose.get('pitch', 0.0),
                                pose.get('yaw', 0.0)
                            ]
                else:
                    if config:
                        for item in config:
                            for name, info in item.items():
                                if isinstance(info, list) and len(info) > 0:
                                    position_dict[name] = info[0].get('id', 0)
                                elif isinstance(info, dict):
                                    position_dict[name] = info.get('id', 0)
                                else:
                                    position_dict[name] = 0
            self.get_logger().info('\033[1;32mLoaded positions: %s\033[0m' % position_dict)
        except Exception as e:
            self.get_logger().error('Failed to load positions: %s' % str(e))
        return position_dict

    def reach_goal_callback(self, msg: Bool):
        self.get_logger().info('reach goal: %s' % msg.data)
        self.reach_goal = msg.data
        if msg.data:
            self.navigation_status = "finish"

    def set_pose_callback(self, request, response):
        position = request.data.strip()
        self.get_logger().info('Received target: %s' % position)
        
        if position not in self.position_dict:
            self.get_logger().warn("can't find the navigation goal: %s" % position)
            response.success = False
            response.message = "can't find the navigation goal: %s" % position
            return response
        
        self.get_logger().info('Moving to: %s' % position)
        self.reach_goal = False
        self.current_position = position
        self.navigation_status = 'moving to %s' % position
        
        if self.navigation_mode in ['smart_factory', 'smart_community']:
            msg = Int32()
            msg.data = self.position_dict[position]
            self.nav_pub.publish(msg)
        else:
            nav_msg = SetPose2D.Request()
            p = self.position_dict[position]
            nav_msg.data.x = float(p[0])
            nav_msg.data.y = float(p[1])
            nav_msg.data.roll = p[2]
            nav_msg.data.pitch = p[3]
            nav_msg.data.yaw = p[4]
            self.nav_client.call_async(nav_msg)
        
        response.success = True
        response.message = "true"
        return response

    def navigation_status_callback(self, request, response):
        self.get_logger().info('\033[1;32m Navigation status: [%s]\033[0m' % self.navigation_status)
        response.success = True
        response.message = self.navigation_status
        return response

    def list_positions_callback(self, request, response):
        positions = ",".join(sorted(self.position_dict.keys()))
        self.get_logger().info('\033[1;32m Available positions: %s\033[0m' % positions)
        response.success = True
        response.message = positions
        return response

    def get_navigation_mode_callback(self, request, response):
        self.get_logger().info('\033[1;32m Navigation mode: [%s]\033[0m' % self.navigation_mode)
        response.success = True
        response.message = self.navigation_mode
        return response


def main():
    rclpy.init()
    node = ClawNavigationManager('claw_navigation_manager')
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
