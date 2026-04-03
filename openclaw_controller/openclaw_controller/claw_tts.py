#!/usr/bin/env python3
# encoding: utf-8
# Author: GCUSMS
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
import re


class LogColor:
    YELLOW = '\033[33m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    CYAN = '\033[36m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class MissionTts(Node):
    def __init__(self):
        super().__init__('mission_tts')

        self.play_audio_finish = True
        self.tts_queue = []

        self.create_subscription(String, '/mission/finish', self.mission_callback, 10)

        self.create_subscription(Bool, '/tts_node/play_finish', self.play_finish_callback, 10)

        self.tts_pub = self.create_publisher(String, '/tts_node/tts_text', 10)

        self.timer = self.create_timer(0.1, self.process_loop)

        self.get_logger().info(f'{LogColor.GREEN}[🦞 Node started]{LogColor.RESET}')

    def play_finish_callback(self, msg: Bool):
        self.play_audio_finish = msg.data

    def extract_mission_text(self, text):
        match = re.search(r'[Mm]ission:\s*(.+)', text)
        return match.group(1).strip() if match else None

    def mission_callback(self, msg: String):
        text = msg.data.strip()
        if text:
            mission_text = self.extract_mission_text(text)
            if mission_text:
                # self.get_logger().info(f'{LogColor.YELLOW}{LogColor.BOLD}[MISSION] {mission_text}{LogColor.RESET}')
                self.tts_queue.append(mission_text)

    def process_loop(self):
        if self.play_audio_finish and self.tts_queue:
            self.play_audio_finish = False
            text = self.tts_queue.pop(0)
            tts_msg = String()
            tts_msg.data = text
            self.tts_pub.publish(tts_msg)
            self.get_logger().info(f'{LogColor.CYAN}{LogColor.BOLD}{text}{LogColor.RESET}')


def main():
    rclpy.init()
    node = MissionTts()
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
