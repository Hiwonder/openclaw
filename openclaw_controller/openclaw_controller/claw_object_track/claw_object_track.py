#!/usr/bin/env python3
# encoding: utf-8
# Author: GCUSMS
import os
import cv2
import json
import queue
import threading
import numpy as np

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from std_srvs.srv import Trigger
from sdk.fps import FPS
from geometry_msgs.msg import Point


class ObjectTrackDetect(Node):
    def __init__(self, name='claw_object_track'):
        rclpy.init()
        super().__init__(name)

        # Declare parameters
        self.declare_parameter('enable_tracking', False)
        self.enable_tracking = self.get_parameter('enable_tracking').value

        self.declare_parameter('object_track_debug', False)
        self.object_track_debug = self.get_parameter('object_track_debug').value
        
        if self.object_track_debug:
            self.pick_debug_param_init()
            self.lock = threading.RLock()
            cv2.namedWindow('image', 1)
            cv2.setMouseCallback('image', self.onmouse)
        self.get_logger().info('\033[1;32m%s\033[0m' % "debug_param")

        self.fps = FPS()
        self.image_queue = queue.Queue(maxsize=2)
        self.box = []               # [x, y, w, h] in pixel coordinates
        self.mouse_click = False    # 记录鼠标点击状态
        self.running = True
        self.set_above = False
        self.start_track = False
        self.track = None

        # Store actual image dimensions (updated on first received image)
        self.img_width = None
        self.img_height = None

        # Subscribe to RGB image
        self.rgb_sub = self.create_subscription(
            Image, 'depth_cam/rgb0/image_raw', self.rgb_callback, 1
        )

        # Subscribe to box published by agent
        self.box_sub = self.create_subscription(
            String, '~/get_box', self.box_callback, 1
        )
        self.center_pub = self.create_publisher(Point, '~/track_center', 10)
        self.track_status = 'track_ready'
        self.create_service(Trigger, '~/track_status', self.track_status_srv_callback)

        self.create_service(Trigger, '~/stop_track', self.stop_obj_track_callback)
        self.client = self.create_client(Trigger, '/init_pose/init_finish')
        self.client.wait_for_service()
        self.get_logger().info('\033[1;32m[%s]\033[0m' % '🦞Node Start')

        # Tracking-related objects, initially None
        self._tracker = None
        self._ctx = None
        self.ObjectTracker = None
        self._Tracker = None
        
        self.target_center_x = None
        self.target_center_y = None
        self.track_window = None
        self.selection = None
        
        # 只创建一次 ObjectTracker，像 vllm_track.py 一样复用
        self.track = None

    def pick_debug_param_init(self):
        self.mouse_click = False
        self.drag_start = None
        self.get_logger().info('Mouse callback initialized')


    def onmouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:  # 鼠标左键按下
            self.mouse_click = True
            self.drag_start = (x, y)  # 鼠标起始位置
            self.track_window = None
            self.get_logger().info(f'LBUTTONDOWN: drag_start={self.drag_start}')
        if self.drag_start:  # 是否开始拖动鼠标，记录鼠标位置
            xmin = min(x, self.drag_start[0])
            ymin = min(y, self.drag_start[1])
            xmax = max(x, self.drag_start[0])
            ymax = max(y, self.drag_start[1])
            self.selection = (xmin, ymin, xmax, ymax)
        if event == cv2.EVENT_LBUTTONUP:  # 鼠标左键松开
            self.mouse_click = False
            self.drag_start = None
            self.track_window = self.selection
            # 将 track_window (xmin,ymin,xmax,ymax) 转换为 box (x,y,w,h) 格式
            xmin, ymin, xmax, ymax = self.selection
            self.box = [xmin, ymin, xmax - xmin, ymax - ymin]
            self.get_logger().info(f'LBUTTONUP: track_window={self.track_window}, box={self.box}')
            self.selection = None
        if event == cv2.EVENT_RBUTTONDOWN:
            self.mouse_click = False
            self.selection = None  # 实时跟踪鼠标的跟踪区域
            self.track_window = None  # 要检测的物体所在区域
            self.drag_start = None  # 标记，是否开始拖动鼠标
            self.start_track = False  # 重置追踪状态，允许重新绘制
            self.box = []  # 清空 box，允许重新设置
            self.track_status = 'track_ready'
            if self.track is not None:
                self.track.stop()
            # 注意：不销毁 self.track，只停止追踪，以便复用
            self.get_logger().info(f'RBUTTONDOWN: reset tracking state')

    def rgb_callback(self, msg):
        try:
            rgb_image = np.ndarray(
                shape=(msg.height, msg.width, 3),
                dtype=np.uint8,
                buffer=msg.data
            )

            # Store image dimensions on first receipt
            if self.img_width is None:
                self.img_width = msg.width
                self.img_height = msg.height
                self.get_logger().info(f'Image size: {self.img_width}x{self.img_height}')

            if self.image_queue.full():
                self.image_queue.get()
            self.image_queue.put(rgb_image)

        except Exception as e:
            self.get_logger().error(f'Image conversion failed: {e}')


    def track_status_srv_callback(self, request, response):
        self.get_logger().info('\033[1;32m Track status: [%s]\033[0m' % self.track_status)
        return_status = self.track_status
        response.success = True
        response.message = return_status
        return response



    def box_callback(self, msg):
        if not self.enable_tracking:
            self.get_logger().debug('Tracking disabled, ignoring box message')
            return

        try:
            data = json.loads(msg.data)
            object_name = data.get('object', '')
            box_coords = data.get('box', [])   # normalized [xmin, ymin, xmax, ymax]

            if box_coords and len(box_coords) == 4:
                # Convert normalized coordinates to pixel coordinates using actual image size
                if self.img_width is not None and self.img_height is not None:
                    xmin, ymin, xmax, ymax = box_coords
                    pixel_box = [
                        int(xmin * self.img_width),
                        int(ymin * self.img_height),
                        int(xmax * self.img_width),
                        int(ymax * self.img_height)
                    ]
                    # Convert to [x, y, w, h] format
                    self.box = [pixel_box[0], pixel_box[1], pixel_box[2] - pixel_box[0], pixel_box[3] - pixel_box[1]]
                    self.get_logger().info(f'Received recognition result: {object_name}, box={self.box}')
                else:
                    self.get_logger().warn('No image size available yet, skipping box conversion')
            else:
                self.get_logger().warn(f'Invalid box coordinates: {box_coords}')
        except Exception as e:
            self.get_logger().error(f'Failed to parse box message: {e}')

    def stop_obj_track_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % "stop_track")
        self.start_track = False  # 重置追踪状态
        self.track_status = 'track_ready'
        if self.track is not None:
            self.track.stop()
        # 注意：不销毁 self.track，只停止追踪，以便复用
        self.get_logger().info('\033[1;32m%s\033[0m' % "stop track finish")
        response.success = True
        response.message = "stop"
        return response

    def spin(self):
        if self.enable_tracking:
            # Dynamically import tracking-related modules only when needed
            import pycuda.driver as cuda
            from large_models_examples.track_anything import ObjectTracker
            from large_models_examples.tracker import Tracker

            # Store classes for later use in display thread
            self.ObjectTracker = ObjectTracker
            self._Tracker = Tracker

            self.get_logger().info('Will initialize CUDA and Tracker in display_thread...')
        else:
            self.get_logger().info('Tracking disabled, running in display-only mode')

        # Start display thread
        thread = threading.Thread(target=self.display_thread, args=(self,))
        thread.start()

        while self.running and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.1)

        self.running = False
        thread.join()

        self.destroy_node()
        rclpy.shutdown()

    def display_thread(self, node):
        if self.enable_tracking:
            import pycuda.driver as cuda
            self.get_logger().info('Initializing CUDA and Tracker in display_thread...')
            dev = cuda.Device(0)
            self._ctx = dev.make_context()
            
            model_path = '/home/ubuntu/ros2_ws/src/large_models_examples/large_models_examples'
            back_exam_engine_path = os.path.join(model_path, "resources/models/nanotrack_backbone_exam.engine")
            back_temp_engine_path = os.path.join(model_path, "resources/models/nanotrack_backbone_temp.engine")
            head_engine_path = os.path.join(model_path, "resources/models/nanotrack_head.engine")
            
            self._tracker = self._Tracker(back_exam_engine_path, back_temp_engine_path, head_engine_path)
            self.get_logger().info('Tracker initialized in display_thread')

        frame_count = 0
        p1 = None
        p2 = None

        try:
            while self.running:
                try:
                    image = self.image_queue.get(block=True, timeout=1.0)
                    frame_count += 1
                except queue.Empty:
                    continue

                img_h, img_w = image.shape[:2]

                # Only perform tracking if enabled and we have a target
                if self.enable_tracking and self.box and not self.start_track:
                    self.get_logger().info(f'Starting tracking with box={self.box}')
                    if self.track is None:
                        # use_mouse=False 避免与 ObjectTrackDetect 的鼠标回调冲突
                        self.track = self.ObjectTracker(use_mouse=False, automatic=True)
                    self.track.set_track_target(self._tracker, self.box, image)
                    self.start_track = True
                    self.box = []
                    self.get_logger().info(f'Tracking started, box cleared')

                if self.enable_tracking and self.start_track and self.track is not None:
                    if not self.mouse_click:
                        self.track_window = None

                    depth_image = np.zeros((img_h, img_w), dtype=np.uint16)
                    data = self.track.track(self._tracker, image, depth_image)
                    p1 = data[2]
                    p2 = data[3]
                    self.track_status = 'track_running'
                    
                    if data is not None:
                        image = data[-1]
                        if data[2] is not None and data[3] is not None:
                            self.target_center_x = (data[2][0] + data[3][0]) / 2
                            self.target_center_y = (data[2][1] + data[3][1]) / 2
                            # self.get_logger().info(f'self.target_center_x:{self.target_center_x},self.target_center_y:{self.target_center_y}')

                        center_msg = Point(x=self.target_center_x, y=self.target_center_y, z=0.0)
                        self.center_pub.publish(center_msg)     


                if self.selection:
                    cv2.rectangle(image, (self.selection[0], self.selection[1]), (self.selection[2], self.selection[3]),
                                  (0, 255, 255), 2)
                elif self.track_window is not None: 
                    cv2.rectangle(image, (self.track_window[0], self.track_window[1]),
                                  (self.track_window[2], self.track_window[3]), (0, 0, 255), 2)
                self.fps.update()
                # self.fps.show_fps(image)
                cv2.imshow('image', image)
                key = cv2.waitKey(1)

                if key == ord('q') or key == 27:
                    self.running = False

                if not self.set_above:
                    try:
                        # Move window to top-right corner based on actual width
                        cv2.moveWindow('Image', 1920 - img_w, 0)
                        self.set_above = True
                    except:
                        pass

            cv2.destroyAllWindows()
        finally:
            if self._ctx is not None:
                self._ctx.pop()
            self.get_logger().info('Display thread ended')
            self.destroy_node()
            rclpy.shutdown()


def main():
    node = ObjectTrackDetect()
    node.spin()


if __name__ == "__main__":
    main()