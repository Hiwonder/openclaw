#!/usr/bin/env python3
# encoding: utf-8
# Author: GCUSMS

import rclpy
import signal
import threading
from rclpy.node import Node
from std_msgs.msg import String
from std_srvs.srv import Trigger
from servo_controller_msgs.msg import ServosPosition
from servo_controller.action_group_controller import ActionGroupController


class ArmController(Node):
    def __init__(self, name='claw_arm_group_control'):
        super().__init__(name)
        
        self.controller = ActionGroupController(
            self.create_publisher(ServosPosition, 'servo_controller', 1),
            '/home/ubuntu/software/arm_pc/ActionGroups'
        )
        
        self.subscription = self.create_subscription(
            String,
            '~/arm_group_control',
            self.command_callback,
            10
        )

        self._execution_lock = threading.Lock()
        self._is_executing = False
        self.arm_status = 'stop'
        self.create_service(Trigger, '~/arm_group_status', self.arm_group_status_srv_callback)
        self.supported_actions = ['voice_pick', 'voice_give', 'init', 'camera_up']

        signal.signal(signal.SIGINT, self.shutdown)
        self.client = self.create_client(Trigger, '/init_pose/init_finish')
        self.client.wait_for_service()
        self.get_logger().info('\033[1;32m[%s]\033[0m' % '🦞Node Start')

    def arm_group_status_srv_callback(self, request, response):
        self.get_logger().info('\033[1;32mArm status: [%s]\033[0m' % self.arm_status)
        response.success = True
        response.message = self.arm_status
        return response

    def command_callback(self, msg):
        cmd = msg.data.strip()
        if not cmd:
            return
        
        self.get_logger().info(f'\033[1;34mCommand received: {cmd}\033[0m')
        
        with self._execution_lock:
            if self._is_executing:
                self.get_logger().warn(f'\033[93mBusy, ignoring command: {cmd}\033[0m')
                return
        
        if cmd not in self.supported_actions:
            self.get_logger().error(f'\033[91mUnsupported action: {cmd}\033[0m')
            return

        with self._execution_lock:
            self._is_executing = True
        self.arm_status = 'moving'
        threading.Thread(target=self.execute_action, args=(cmd,), daemon=True).start()

    def execute_action(self, cmd):
        try:
            self.controller.run_action(cmd)
            self.arm_status = 'finished'
            self.get_logger().info(f'\033[1;32mAction {cmd} completed\033[0m')
        except Exception as e:
            self.get_logger().error(f'\033[91mError executing {cmd}: {e}\033[0m')
        finally:
            with self._execution_lock:
                self._is_executing = False

    def shutdown(self, signum, frame):
        self.get_logger().info('\033[1;33mShutting down...\033[0m')
        rclpy.shutdown()


def main():
    rclpy.init()
    node = ArmController()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()