#!/usr/bin/env python3
# encoding: utf-8
# Author: GCUSMS
import time
import rclpy
import threading
import queue
from rclpy.node import Node
from std_srvs.srv import Trigger
from geometry_msgs.msg import Twist
from std_msgs.msg import String


class ChassisController(Node):
    def __init__(self, name='claw_move_control'):
        super().__init__(name)

        self.default_linear = 0.15
        self.default_angular = 0.45
        self.default_stop_duration = 0.5

        self.cmd_vel_pub = self.create_publisher(Twist, '/controller/cmd_vel', 1)
        self.subscription = self.create_subscription(
            String, '~/chassis_command', self.command_callback, 10)
        self.move_status = 'stop'
        self.create_service(Trigger, '~/move_status', self.move_status_srv_callback)

        self.command_queue = queue.Queue()
        self.client = self.create_client(Trigger, '/init_pose/init_finish')
        self.client.wait_for_service()
        self.worker_thread = threading.Thread(target=self.process_commands, daemon=True)
        self.worker_thread.start()
        
        self.get_logger().info('\033[1;32m[%s]\033[0m' % '🦞Node Start')


    def move_status_srv_callback(self, request, response):
        self.get_logger().info('\033[1;32m Move status: [%s]\033[0m' % self.move_status)
        response.success = True
        response.message = self.move_status
        return response

    def parse_twist(self, direction):
        twist = Twist()
        self.move_status = 'moving'
        if direction == 'forward':
            twist.linear.x = self.default_linear
        elif direction == 'backward':
            twist.linear.x = -self.default_linear
        elif direction == 'left':
            twist.linear.x = self.default_linear
            twist.angular.z = self.default_angular
        elif direction == 'right':
            twist.linear.x = self.default_linear
            twist.angular.z = -self.default_angular
        elif direction == 'stop':
            pass
        else:
            return None
        return twist

    def command_callback(self, msg):
        cmd = msg.data.strip()
        if not cmd:
            return
        self.get_logger().info(f'\033[1;34m Command: {cmd}\033[0m')
        self.command_queue.put(cmd)

    def process_commands(self):
        while rclpy.ok():
            try:
                cmd = self.command_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            self.execute_command(cmd)
            self.command_queue.task_done()

    def execute_command(self, cmd):
        try:
            cmd = cmd.replace('，', ',')
            parts = [p.strip() for p in cmd.split(',') if p.strip()]
            actions = []
            self.move_status = 'moving'
            for p in parts:
                w = p.split()
                dir = w[0].lower()
                dur = float(w[1]) if len(w) > 1 else self.default_stop_duration
                actions.append((dir, dur))
            
            for i, (dir, dur) in enumerate(actions):
                twist = self.parse_twist(dir)
                if twist is None:
                    self.get_logger().error(f'\033[91mUnknown direction: {dir}\033[0m')
                    self._stop()
                    return
                self.cmd_vel_pub.publish(twist)
                time.sleep(dur)
                if i < len(actions) - 1:
                    self._stop()
                    time.sleep(self.default_stop_duration)
            self._stop()
            self.get_logger().info(f'\033[1;33m Command done\033[0m')
        except Exception as e:
            self.get_logger().error(f'Execution error: {e}')
            self._stop()

    def _stop(self):
        self.move_status = 'finished'
        self.cmd_vel_pub.publish(Twist())


def main():
    rclpy.init()
    node = ChassisController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()