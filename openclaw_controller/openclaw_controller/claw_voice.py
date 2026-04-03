#!/usr/bin/env python3
# encoding: utf-8
# Author: GCUSMS

import os
import json
import uuid
import rclpy
import threading
import time
import requests
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from std_msgs.msg import String, Bool
from std_srvs.srv import SetBool
from speech import speech
from std_srvs.srv import Trigger

class LogColor:
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    CYAN = '\033[36m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

CONFIG_PATH = os.path.expanduser("~/.openclaw/openclaw.json")
with open(CONFIG_PATH) as f:
    _config = json.load(f)
    _TOKEN = _config['gateway']['auth']['token']

GATEWAY_URL = "http://127.0.0.1:18789"
SESSION_KEY = "claw_voice"

class VoiceOpenClaw(Node):
    def __init__(self, name):
        rclpy.init()
        super().__init__(name)

        timer_cb_group = ReentrantCallbackGroup()

        self.wakeup_flag = False
        self.running = True
        self.processing = False

        self.create_subscription(Bool, '/vocal_detect/wakeup', self.wakeup_callback, 1)
        self.create_subscription(String, '/vocal_detect/asr_result', self.asr_callback, 1)

        self.awake_client = self.create_client(SetBool, '/vocal_detect/enable_wakeup')
        self.awake_client.wait_for_service()
        self.get_logger().info('Wakeup service found')

        self.get_logger().info(f'{LogColor.GREEN}[🦞 Node started]{LogColor.RESET}')
        
        threading.Thread(target=self.process_loop, daemon=True).start()
        
    def send_request(self, client, msg):
        future = client.call_async(msg)
        while rclpy.ok():
            if future.done() and future.result():
                return future.result()

    def wakeup_callback(self, msg):
        if msg.data:
            self.get_logger().info(f'{LogColor.GREEN}Wakeup detected{LogColor.RESET}')
            self.wakeup_flag = True

    def asr_callback(self, msg):
        if msg.data and not self.processing:
            self.get_logger().info(f'{LogColor.BLUE}Claw ASR Result: {msg.data}{LogColor.RESET}')
            self.processing = True
            threading.Thread(target=self.process_asr, args=(msg.data,), daemon=True).start()
            
    def send_to_openclaw(self, text):
        url = f"{GATEWAY_URL}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openclaw/default",
            "messages": [{"role": "user", "content": text}],
            "user": SESSION_KEY
        }
        try:
            resp = requests.post(url, headers=headers, json=payload)
            result = resp.json()
            self.get_logger().info(f'Full response: {result}')
            return result['choices'][0]['message']['content']
        except Exception as e:
            self.get_logger().error(f'{LogColor.RED}OpenClaw request failed: {e}{LogColor.RESET}')
            try:
                self.get_logger().error(f'{LogColor.RED}Response: {resp.text}{LogColor.RESET}')
            except:
                pass
            return None

    def process_asr(self, text):
        if text and text.strip():
            try:

                # self.get_logger().info(f'{LogColor.CYAN}Sending to OpenClaw: {text}{LogColor.RESET}')
                reply = self.send_to_openclaw(text)
                
                if reply:
                    self.get_logger().info(f'{LogColor.YELLOW}{LogColor.BOLD}OpenClaw Reply: {reply}{LogColor.RESET}')
                else:
                    self.get_logger().error(f'{LogColor.RED}Failed to get OpenClaw reply{LogColor.RESET}')
                    
            except Exception as e:
                self.get_logger().error(f'{LogColor.RED}Error: {e}{LogColor.RESET}')

            # reset state
            self.reset_state()
        else:
            self.get_logger().info('No speech detected')

    def reset_state(self):
        self.get_logger().info(f'{LogColor.GREEN}Reply done, ready for next round{LogColor.RESET}')
        self.wakeup_flag = False
        self.processing = False
        
        msg = SetBool.Request()
        msg.data = True
        self.send_request(self.awake_client, msg)
        self.get_logger().info(f'{LogColor.GREEN}Wakeup re-enabled{LogColor.RESET}')
            
    def process_loop(self):
        while self.running:
            time.sleep(0.1)
        rclpy.shutdown()


def main():
    node = VoiceOpenClaw('claw_voice')
    executor = rclpy.executors.MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    node.destroy_node()

if __name__ == "__main__":
    main()
