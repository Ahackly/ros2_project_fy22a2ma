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

class pathPlanner(Node):
    def __init__(self):
        super().__init__('pp')
        
    def read_map(self):
        self.map_image = cv2.imread("/uolstore/home/users/fy22a2ma/ros2_ws/src/ros2_project_fy22a2ma/map/map.pgm", cv2.IMREAD_GRAYSCALE)
        height, width = self.map_image.shape
        cell_size = 5
        cells = []
        world_cells = []
        for i in range(0,height):
            for j in range(0,width): 
                cell = self.map_image[i:i + cell_size, j:j + cell_size]
                if np.mean(cell) > 250:
                    cells.append((i,j))
        
        for r,c in cells:
            r_center = r + cell_size/2
            c_center = c + cell_size/2

            x_map = r_center * 0.05 + -12.2
            y_map = c_center * 0.05 + -15.8

            world_cells.append((x_map,y_map))
            
            
        
def main():
    
    def signal_handler(sig, frame):
        rclpy.shutdown()

    rclpy.init(args=None)
    pp = pathPlanner()
  
    signal.signal(signal.SIGINT, signal_handler)
    thread = threading.Thread(target=rclpy.spin, args=(pp,), daemon=True)
    thread.start()
    try:
        while rclpy.ok():
            pp.read_map()
            continue
    except ROSInterruptException:
        pass
    cv2.destroyAllWindows() 

if __name__ == '__main__':
    main()