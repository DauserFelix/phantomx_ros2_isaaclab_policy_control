#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import numpy as np

class PhantomXTestNode(Node):
    def __init__(self):
        super().__init__('phantomx_test_node')
        
        # Publisher erstellen
        self.joint_pub = self.create_publisher(
            JointState,
            '/joint_command',
            10
        )
        
        # Timer für regelmäßiges Publishing (50Hz)
        self.timer = self.create_timer(0.02, self.publish_joint_command)
        
        self.time_step = 0.0
        
        self.get_logger().info('PhantomX Test Node - Publishing single joint')

    def publish_joint_command(self):
        msg = JointState()
        
        # Timestamp
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = ''
        
        # NUR EIN JOINT testen - z.B. c1_lf
        msg.name = ['j_tibia_lf']
        
        # Sinuswelle zwischen -0.5 und +0.5 Radians
        pos = 0.5 * np.sin(2 * np.pi * 0.5 * self.time_step)
        
        msg.position = [pos]
        msg.velocity = [0.0]
        msg.effort = [0.0]
        
        # Publishen
        self.joint_pub.publish(msg)
        
        self.get_logger().info(f'Publishing j_tibia_lf = {pos:.3f}', throttle_duration_sec=1.0)
        
        self.time_step += 0.02

def main(args=None):
    rclpy.init(args=args)
    node = PhantomXTestNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()