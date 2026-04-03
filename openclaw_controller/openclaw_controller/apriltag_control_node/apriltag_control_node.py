#!/usr/bin/env python3
# encoding: utf-8


import os
import cv2
import time
import math
import queue
import rclpy
import threading
import numpy as np
from sdk import common
from sdk.pid import PID
from rclpy.node import Node
from cv_bridge import CvBridge
from std_msgs.msg import Bool
from std_srvs.srv import Trigger, Empty
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from interfaces.srv import SetPose2D, SetPoint, SetString
from servo_controller_msgs.msg import ServosPosition

from servo_controller.bus_servo_control import set_servo_position
from servo_controller.action_group_controller import ActionGroupController

from dt_apriltags import Detector

class ApriltagControl(Node):
    config_path = '/home/ubuntu/ros2_ws/src/openclaw_controller/config/apriltag_control_roi.yaml'

    def __init__(self, name):
        rclpy.init()
        super().__init__(name, allow_undeclared_parameters=True, automatically_declare_parameters_from_overrides=True)
        self.name = name

        self.at_detector = Detector(searchpath=['apriltags'], families='tag36h11', nthreads=4, quad_decimate=1.0, quad_sigma=0.0, refine_edges=1, decode_sharpening=0.25, debug=0)
        
        self.target_tag_id = -1
        
        self.pick_finish = False
        self.place_finish = False

        self.running = True
        self.detect_count = 0
        
        self.start_pick_basket = False
        self.start_place_basket = False
        self.start_pick_exp = False
        
        self.pick_basket = False
        self.place_basket = False
        self.pick_exp = False
        
        self.linear_base_speed = 0.007
        self.angular_base_speed = 0.03

        self.yaw_pid = PID(P=0.015, I=0, D=0.000)
        self.linear_pid = PID(P=0.001, I=0, D=0)
        self.angular_pid = PID(P=0.001, I=0, D=0)

        self.linear_speed = 0
        self.angular_speed = 0
        self.yaw_angle = 90

        self.pick_basket_stop_x = 320
        self.pick_basket_stop_y = 388

        self.pick_exp_stop_x = 320
        self.pick_exp_stop_y = 388
        self.stop = True

        self.d_y = 15
        self.d_x = 15


        self.status = "approach"
        self.count_stop = 0
        self.count_turn = 0

        self.declare_parameter('status', 'start')
        self.bridge = CvBridge()
        self.image_queue = queue.Queue(maxsize=2)
        self.enable_display = self.get_parameter('enable_display').value
        self.debug = self.get_parameter('debug').value
        self.image_name = 'image'

        self.machine_type = os.environ['MACHINE_TYPE']

        self.joints_pub = self.create_publisher(ServosPosition, '/servo_controller', 1)
        self.mecanum_pub = self.create_publisher(Twist, '/controller/cmd_vel', 1)
        self.image_pub = self.create_publisher(Image, '~/image_result', 1)

        self.create_subscription(Image, 'depth_cam/rgb0/image_raw', self.image_callback, 1)

        self.arm_status = "ready"

        self.baskt_id = 1
        self.exp_id = 0

        self.create_service(Trigger, '~/pick_basket', self.start_pick_basket_callback)
        self.create_service(Trigger, '~/place_basket', self.start_place_basket_callback) 
        self.create_service(Trigger, '~/pick_exp', self.start_pick_exp_callback)
        self.create_service(Trigger, '~/place_exp', self.start_place_exp_callback) 

        self.create_service(SetPoint, '~/clear_target', self.clear_target_srv_callback)

        self.create_service(Trigger, '~/debug_pick_basket', self.debug_pick_basket_callback)
        self.create_service(Trigger, '~/debug_place_basket', self.debug_place_basket_callback)
        self.create_service(Trigger, '~/debug_pick_exp', self.debug_pick_exp_callback)
        self.create_service(SetString, '~/set_debug_mode', self.set_debug_mode_callback)
        

        self.create_service(Trigger, '~/get_arm_status', self.arm_status_srv_callback)

        self.create_service(Trigger, '~/init_pose', self.init_pose_callback)

        self.controller = ActionGroupController(self.create_publisher(ServosPosition, 'servo_controller', 1), '/home/ubuntu/software/arm_pc/ActionGroups')
        self.get_logger().info("Action Group Controller has been started")
        self.client = self.create_client(Trigger, '/controller_manager/init_finish')
        self.client.wait_for_service()

        self.action_finish_pub = self.create_publisher(Bool, '~/action_finish', 1)

        self.mecanum_pub.publish(Twist())

        self.get_logger().info("Automatic Pick Node has been started")

        threading.Thread(target=self.action_thread, daemon=True).start()
        threading.Thread(target=self.main, daemon=True).start()
        self.create_service(Empty, '~/init_finish', self.get_node_state)
        self.get_logger().info('\033[1;32m%s\033[0m' % 'start')

    def get_node_state(self, request, response):
        return response


    def arm_status_srv_callback(self, request, response):
        self.get_logger().info('\033[1;32m Arm status: [%s]\033[0m' % self.arm_status)
        return_status = self.arm_status
        response.success = True
        response.message = return_status
        return response


    def clear_target_srv_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % 'clear_target')
        self.target_tag_id = -1
        self.mecanum_pub.publish(Twist())
        response.success = True
        response.message = "clear_target"
        return response

    def init_pose_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % 'init_pose')
        set_servo_position(self.joints_pub, 2, ((1, 500), (2, 701), (3, 120), (4, 88), (5, 500), (10, 500)))
        time.sleep(2)
        response.success = True
        response.message = "init_pose"
        return response

    def debug_pick_basket_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % 'debug_pick_basket')
        self.debug = 'pick_basket'
        self.controller.run_action('pick_basket_debug')
        time.sleep(5)
        set_servo_position(self.joints_pub, 1, ((1, 500), (2, 534), (3, 107), (4, 334), (5, 125), (10, 200)))
        time.sleep(0.5)
        set_servo_position(self.joints_pub, 1, ((1, 500), (2, 701), (3, 120), (4, 88), (5, 500), (10, 200)))
        time.sleep(1)
        msg = Trigger.Request()
        self.start_pick_basket_callback(msg, Trigger.Response())
        response.success = True
        response.message = "debug_pick_basket"
        return response

    def debug_place_basket_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % 'debug_place_basket')
        self.controller.run_action('place_basket_debug')
        time.sleep(5)
        set_servo_position(self.joints_pub, 1, ((1, 500), (2, 500), (3, 122), (4, 506), (5, 125), (10, 500)))
        time.sleep(0.5)
        set_servo_position(self.joints_pub, 1, ((1, 500), (2, 701), (3, 120), (4, 88), (5, 500), (10, 200)))
        time.sleep(1)
        msg = Trigger.Request()
        self.start_place_basket_callback(msg, Trigger.Response())
        response.success = True
        response.message = "debug_place_basket"
        return response

    def debug_pick_exp_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % 'debug_pick_exp')
        self.debug = 'pick_exp'
        self.controller.run_action('pick_exp_debug')
        time.sleep(5)
        set_servo_position(self.joints_pub, 0.5, ((1, 500), (2, 246), (3, 425), (4, 152), (5, 143), (10, 200)))
        time.sleep(0.5)
        set_servo_position(self.joints_pub, 1, ((1, 500), (2, 736), (3, 15), (4, 180), (5, 500), (10, 200)))
        time.sleep(1)
        msg = Trigger.Request()
        self.start_pick_exp_callback(msg, Trigger.Response())
        response.success = True
        response.message = "debug_pick_exp"
        return response

    def set_debug_mode_callback(self, request, response):
        """设置调试模式：pick_basket / place_basket / pick_exp / off"""
        self.debug = request.data
        self.get_logger().info('\033[1;32m%s: %s\033[0m' % ('set_debug_mode', self.debug))
        response.success = True
        response.message = f"debug_mode set to: {self.debug}"
        return response

    def start_pick_basket_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % "start pick_basket")
        self.place_finish = False
        self.linear_speed = 0
        self.angular_speed = 0
        self.yaw_angle = 90


        param = self.get_parameter('pick_stop_pixel_coordinate').value
        self.get_logger().info('\033[1;32mget pick_basket stop pixel coordinate: %s\033[0m' % str(param))
        self.pick_basket_stop_x = param[0]
        self.pick_basket_stop_y = param[1]
        self.stop = True
        self.d_y = 15
        self.d_x = 15

        self.pick_basket = False
        self.place_basket = False
        self.pick_exp = False
        self.start_pick_exp = False

        self.status = "approach"
        self.count_stop = 0
        self.count_turn = 0
        self.linear_pid.clear()
        self.angular_pid.clear()
        
        self.start_pick_basket = True
        self.target_tag_id = self.baskt_id
        self.arm_status = "pick_basket"
        response.success = True
        response.message = "start_pick_basket"
        return response 

    def start_pick_exp_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % "start pick_exp")
        self.place_finish = False
        self.linear_speed = 0
        self.angular_speed = 0
        self.yaw_angle = 90

        set_servo_position(self.joints_pub, 1.0, ((1, 500), (2, 736), (3, 15), (4, 180), (5, 500), (10, 200)))
        time.sleep(1.0)

        try:
            param = self.get_parameter('pick_exp_stop_pixel_coordinate').value
            self.pick_exp_stop_x = param[0]
            self.pick_exp_stop_y = param[1]
        except:
            self.pick_exp_stop_x = 320
            self.pick_exp_stop_y = 388
            
        self.get_logger().info('\033[1;32mget pick_exp stop pixel coordinate: [%s, %s]\033[0m' % (self.pick_exp_stop_x, self.pick_exp_stop_y))
        
        self.stop = True
        self.d_y = 15
        self.d_x = 15

        self.pick_basket = False
        self.place_basket = False
        self.pick_exp = False
        self.start_pick_basket = False

        self.status = "approach"
        self.count_stop = 0
        self.count_turn = 0
        self.linear_pid.clear()
        self.angular_pid.clear()
        
        self.start_pick_exp = True
        self.target_tag_id = self.exp_id
        self.arm_status = "pick_exp"
        response.success = True
        response.message = "start_pick_exp"
        return response 

    def start_place_basket_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % "start place_basket")
        self.pick_finish = False
        self.linear_speed = 0
        self.angular_speed = 0
        self.d_y = 10
        self.d_x = 10
        self.stop = True
        self.pick_basket = False
        self.pick_exp = False
        
        self.start_place_basket = False 
        self.place_basket = True        

        self.linear_pid.clear()
        self.angular_pid.clear()
        self.target_tag_id = -1
        self.arm_status = "place_basket"
        response.success = True
        response.message = "start_place_basket"
        return response 

    def start_place_exp_callback(self, request, response):
        self.get_logger().info('\033[1;32m%s\033[0m' % "start place_exp ")
        self.pick_finish = False
        self.linear_speed = 0
        self.angular_speed = 0
        self.d_y = 10
        self.d_x = 10
        self.stop = True
        self.pick = False
        self.pick_exp = False
        self.place = False
        
        self.start_place = False 
        
        self.target_tag_id = -1
        self.arm_status = "place_exp"

        threading.Thread(target=self.place_exp_action, daemon=True).start()

        response.success = True
        response.message = "start_place_exp"
        return response 

    def place_exp_action(self):
        self.mecanum_pub.publish(Twist())
        time.sleep(1)
        self.controller.run_action('place_exp') 
        time.sleep(8)
        self.get_logger().info('place_exp finish')
        self.arm_status = "place_exp_finish"
        msg = Bool()
        msg.data = True
        self.action_finish_pub.publish(msg)
        self.place_finish = True

    def send_request(self, client, msg):
        future = client.call_async(msg)
        while rclpy.ok():
            if future.done() and future.result():
                return future.result()


    def apriltag_detect(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        tags = self.at_detector.detect(gray)
        
        center_x, center_y, angle = -1, -1, -1
        
        for tag in tags:
            if tag.tag_id == self.target_tag_id:
                corners = tag.corners.astype(int)
                cv2.drawContours(img, [corners], -1, (0, 255, 255), 2, cv2.LINE_AA)
                
                rect = cv2.minAreaRect(np.array(tag.corners).astype(np.float32))
                (center, (width, height), angle) = rect
                center_x, center_y = int(center[0]), int(center[1])
                
                cv2.circle(img, (center_x, center_y), 5, (0, 255, 255), -1)
                break
                
        return center_x, center_y, angle

    def action_thread(self):
        while True:
            if self.pick_basket:
                self.target_tag_id = -1 
                self.start_pick_basket = False
                self.mecanum_pub.publish(Twist())
                time.sleep(0.5)

                self.controller.run_action('pick_basket')
                time.sleep(6)
                
                self.pick_basket = False
                self.get_logger().info('pick_basket finish')
                msg = Bool()
                msg.data = True
                self.action_finish_pub.publish(msg)
                self.pick_finish = True
                self.arm_status = "pick_basket_finish"
            elif self.pick_exp:
                self.target_tag_id = -1 
                self.start_pick_exp = False
                self.mecanum_pub.publish(Twist())

                self.controller.run_action('pick_exp')
                time.sleep(6)
                
                self.pick_exp = False
                self.get_logger().info('pick_exp finish')
                msg = Bool()
                msg.data = True
                self.action_finish_pub.publish(msg)
                self.pick_finish = True
                self.arm_status = "pick_exp_finish"
            elif self.place_basket:
                self.target_tag_id = -1
                self.start_place_basket = False
                self.mecanum_pub.publish(Twist())
                time.sleep(1)
                self.controller.run_action('place_basket')
                time.sleep(8)
                self.get_logger().info('place_basket finish')
                self.place_basket = False
                msg = Bool()
                msg.data = True
                self.action_finish_pub.publish(msg)
                self.place_finish = True
                self.arm_status = "place_basket_finish"
            else:
                time.sleep(0.01)

    def pick_handle(self, image, is_exp=False):
            twist = Twist()

            check_pick = self.pick_exp if is_exp else self.pick_basket
            debug_str = 'pick_exp' if is_exp else 'pick_basket'
            cfg_path =  self.config_path
            
            stop_x = self.pick_exp_stop_x if is_exp else self.pick_basket_stop_x
            stop_y = self.pick_exp_stop_y if is_exp else self.pick_basket_stop_y

            if not check_pick or self.debug == debug_str:
                object_center_x, object_center_y, object_angle = self.apriltag_detect(image) 
                if self.debug == debug_str:
                    if object_center_x > 0 and object_center_y > 0:
                        self.detect_count += 1
                    if self.detect_count >= 10:
                        self.detect_count = 0
                        if object_center_x > 0 and object_center_y > 0:
                            if is_exp:
                                self.pick_exp_stop_x = object_center_x
                                self.pick_exp_stop_y = object_center_y
                            else:
                                self.pick_basket_stop_x = object_center_x
                                self.pick_basket_stop_y = object_center_y
                            
                            data = common.get_yaml_data(cfg_path)
                            if data is None or '/**' not in data:
                                data = {'/**': {'ros__parameters': {}}}
                                
                            key_name = 'pick_exp_stop_pixel_coordinate' if is_exp else 'pick_stop_pixel_coordinate'
                            data['/**']['ros__parameters'][key_name] = [object_center_x, object_center_y]
                            common.save_yaml_data(data, cfg_path)
                            self.get_logger().info(f'\033[1;32m[{debug_str}] 坐标已保存：[{object_center_x}, {object_center_y}]\033[0m')
                        else:
                            self.get_logger().warn(f'\033[1;31m[{debug_str}] 未检测到 Tag，跳过保存\033[0m')
                        self.debug = False
                    self.get_logger().info(f'[{debug_str}] x_y: ' + str([object_center_x, object_center_y]) + f' (count: {self.detect_count}/10)') 
                elif object_center_x > 0:
                    self.linear_pid.SetPoint = stop_y
                    if abs(object_center_y - stop_y) <= self.d_y:
                        object_center_y = stop_y
                    if self.status != "align":
                        self.linear_pid.update(object_center_y)  
                        output = self.linear_pid.output
                        tmp = math.copysign(self.linear_base_speed, output) + output
                        self.linear_speed = tmp
                        if tmp > 0.4:
                            self.linear_speed = 0.4
                        if tmp < -0.4:
                            self.linear_speed = -0.4
                        if abs(tmp) <= 0.0075:
                            self.linear_speed = 0

                    self.angular_pid.SetPoint = stop_x
                    if abs(object_center_x - stop_x) <= self.d_x:
                        object_center_x = stop_x
                    if self.status != "align":
                        self.angular_pid.update(object_center_x)  
                        output = self.angular_pid.output
                        tmp = math.copysign(self.angular_base_speed, output) + output
                        
                        self.angular_speed = tmp
                        if tmp > 1.5:
                            self.angular_speed = 1.5
                        if tmp < -1.5:
                            self.angular_speed = -1.5
                        if abs(tmp) <= 0.038:
                            self.angular_speed = 0
                            
                    if self.status != "align":

                        if object_angle < 40: 
                            object_angle += 90
                        
                        self.yaw_pid.SetPoint = 90
                        if abs(object_angle - 90) <= 3:
                            object_angle = 90
                        self.yaw_pid.update(object_angle)  

                        yaw_output = self.yaw_pid.output
                        if yaw_output > 0.5:
                            yaw_output = 0.5
                        elif yaw_output < -0.5:
                            yaw_output = -0.5
                        self.yaw_angle = yaw_output


                    if abs(self.linear_speed) == 0 and abs(self.angular_speed) == 0:
                        if 'Mecanum' in self.machine_type:
                            self.count_turn += 1
                            if self.count_turn >= 3:
                                self.count_turn = 3
                                self.status = "align"
                                if self.count_stop < 3: 
                                    if object_angle < 40: 
                                        object_angle += 90
                                    self.yaw_pid.SetPoint = 90
                                    if abs(object_angle - 90) <= 3:
                                        object_angle = 90
                                    self.yaw_pid.update(object_angle)  
                                    self.yaw_angle = self.yaw_pid.output
                                    if object_angle != 90:
                                        if abs(self.yaw_angle) <=0.038:
                                            self.count_stop += 1
                                        twist.linear.y = float(-2 * 0.3 * math.sin(self.yaw_angle / 2))
                                        twist.angular.z = float(self.yaw_angle)
                                    else:
                                        self.count_stop += 1
                                elif self.count_stop <=6:
                                    self.d_x = 5
                                    self.d_y = 5
                                    self.count_stop += 1
                                    self.status = "adjust"
                                else:
                                    self.count_stop = 0
                                    if is_exp:
                                        self.pick_exp = True
                                    else:
                                        self.pick_basket = True
                        else:
                            self.count_stop += 1
                            if self.count_stop > 15:
                                self.count_stop = 0
                                if is_exp:
                                    self.pick_exp = True
                                else:
                                    self.pick_basket = True
                    else:
                        if self.count_stop >= 3:
                            self.count_stop = 3
                        self.count_turn = 0
                        
                        if self.status != 'align':
                            twist.linear.x = float(self.linear_speed) 
                            lateral_speed = float(self.angular_speed) 
                            if lateral_speed > 0.15:
                                lateral_speed = 0.15
                            elif lateral_speed < -0.15:
                                lateral_speed = -0.15
                            twist.linear.y = lateral_speed
                            if object_angle != 90:
                                twist.angular.z = float(self.yaw_angle)
                            else:
                                twist.angular.z = 0.0

            self.mecanum_pub.publish(twist)

            return image

    def image_callback(self, ros_image):
        cv_image = self.bridge.imgmsg_to_cv2(ros_image, "rgb8")
        rgb_image = np.array(cv_image, dtype=np.uint8)
        if self.image_queue.full():
            self.image_queue.get()
        self.image_queue.put(cv2.resize(rgb_image, (640, 480)))

    def main(self):
        while self.running:
            try:
                image = self.image_queue.get(block=True, timeout=1)
            except queue.Empty:
                if not self.running:
                    break
                else:
                    continue

            result_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if self.target_tag_id != -1:

                if self.start_pick_basket:
                    self.stop = True
                    stop_x = self.pick_basket_stop_x
                    stop_y = self.pick_basket_stop_y
                    result_image = self.pick_handle(cv2.cvtColor(image, cv2.COLOR_RGB2BGR), is_exp=False)
                elif self.start_pick_exp:
                    self.stop = True
                    stop_x = self.pick_exp_stop_x
                    stop_y = self.pick_exp_stop_y
                    result_image = self.pick_handle(cv2.cvtColor(image, cv2.COLOR_RGB2BGR), is_exp=True)
                else:
                    if self.stop:
                        self.stop = False
                        self.mecanum_pub.publish(Twist())
                    result_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    stop_x = self.pick_basket_stop_x
                    stop_y = self.pick_basket_stop_y

                cv2.line(result_image, (stop_x, stop_y - 10), (stop_x, stop_y + 10), (0, 255, 255), 2)
                cv2.line(result_image, (stop_x - 10, stop_y), (stop_x + 10, stop_y), (0, 255, 255), 2)
            
            if self.enable_display:
                cv2.imshow(self.image_name, result_image)
                cv2.waitKey(1)
            self.image_pub.publish(self.bridge.cv2_to_imgmsg(result_image, "bgr8"))

        set_servo_position(self.joints_pub, 2, ((1, 500), (2, 701), (3, 120), (4, 88), (5, 500), (10, 200)))
        self.mecanum_pub.publish(Twist())
        rclpy.shutdown()

def main():
    node = ApriltagControl('apriltag_control_node')
    rclpy.spin(node)
    node.destroy_node()
 
if __name__ == "__main__":
    main()