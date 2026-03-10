# Exercise 1 - Display an image of the camera feed to the screen

#from __future__ import division
import threading
import sys, time
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from rclpy.exceptions import ROSInterruptException
import signal


class colourIdentifier(Node):
    def __init__(self):
        super().__init__('cI')
        self.opencv = CvBridge()
        self.subscription = self.create_subscription(Image, "camera/image_raw", self.callback, 10)

        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)
        self.rate = self.create_rate(10)  # 10 Hz

        self.sensitivity = 10

        self.subscription  # prevent unused variable warning

    def walk_circle(self):
        desired_velocity = Twist()
        desired_velocity.angular.z = 2.0
        for _ in range(30):  # Stop for a brief moment
            self.publisher.publish(desired_velocity)
            self.rate.sleep()

    def walk_forward(self):
        desired_velocity = Twist()
        desired_velocity.linear.x = 0.2  # Forward with 0.2 m/s

        for _ in range(30):  # Stop for a brief moment
            self.publisher.publish(desired_velocity)
            self.rate.sleep()

    def stop(self):
        desired_velocity = Twist()
        desired_velocity.angular.z = 0.0  # Send zero velocity to stop the robot
        self.publisher.publish(desired_velocity)

    def callback(self, data):
        try:
            cv_image = self.opencv.imgmsg_to_cv2(data, "bgr8")
            hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)

            hsv_green_lower = np.array([60-self.sensitivity, 100, 100])
            hsv_green_upper = np.array([60+self.sensitivity, 255, 255])

            hsv_blue_lower = np.array([120-self.sensitivity, 100, 100])
            hsv_blue_upper = np.array([120+self.sensitivity, 255, 255])

            hsv_red_lower = np.array([-self.sensitivity, 100, 100])
            hsv_red_upper = np.array([self.sensitivity, 255, 255])
            hsv_red_lower_2 = np.array([180-self.sensitivity, 100, 100])
            hsv_red_upper_2 = np.array([180+self.sensitivity, 255, 255])
            
            red_mask_1 = cv2.inRange(hsv_image, hsv_red_lower, hsv_red_upper)
            red_mask_2 = cv2.inRange(hsv_image, hsv_red_lower_2, hsv_red_upper_2)
            red_mask_union = cv2.bitwise_or(red_mask_1,red_mask_2)

            green_mask = cv2.inRange(hsv_image, hsv_green_lower, hsv_green_upper)

            blue_mask = cv2.inRange(hsv_image, hsv_blue_lower, hsv_blue_upper)

            rg_mask = cv2.bitwise_or(red_mask_union,green_mask)
            rgb_mask = cv2.bitwise_or(blue_mask,rg_mask)

            contours, _ = cv2.findContours(green_mask,mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                print("Green found\n")
                self.stop()
                self.walk_forward()

            cv2.namedWindow('camera_Feed', cv2.WINDOW_NORMAL)
            cv2.imshow('camera_Feed', rgb_mask)
            cv2.resizeWindow('camera_Feed', 320, 240)
            cv2.waitKey(3)
        except CvBridgeError as e:
           print(e) 
        return
        

# Create a node of your class in the main and ensure it stays up and running
# handling exceptions and such
def main():

    def signal_handler(sig, frame):
        rclpy.shutdown()
    # Instantiate your class
    # And rclpy.init the entire node
    rclpy.init(args=None)
    CI = colourIdentifier()


    signal.signal(signal.SIGINT, signal_handler)
    thread = threading.Thread(target=rclpy.spin, args=(CI,), daemon=True)
    thread.start()

    try:
        while rclpy.ok():
            CI.walk_circle();
    except ROSInterruptException:
        pass

    # Remember to destroy all image windows before closing node
    cv2.destroyAllWindows()
    

# Check if the node is executing in the main path
if __name__ == '__main__':
    main()
