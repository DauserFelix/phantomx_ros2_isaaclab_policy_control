#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import numpy as np

class PhantomXNode(Node):
    def __init__(self):
        super().__init__('phantomx_node')
        
        # Publisher erstellen
        self.joint_pub = self.create_publisher(
            JointState,
            '/joint_command',
            10
        )
        
        # Timer für regelmäßiges Publishing (50Hz = 0.02s)
        self.timer = self.create_timer(0.02, self.publish_joint_commands)
        
        # Echte Joint-Namen aus IsaacLab
        # lf = left front, lm = left middle, lr = left rear
        # rf = right front, rm = right middle, rr = right rear
        # c1, c2 = coxa joints, thigh = femur, tibia = tibia
        self.joint_names = [
            'j_c1_lf', 'j_thigh_lf', 'j_tibia_lf',
            'j_c1_lm', 'j_thigh_lm', 'j_tibia_lm',
            'j_c1_lr', 'j_thigh_lr', 'j_tibia_lr',
            'j_c1_rf', 'j_thigh_rf', 'j_tibia_rf',
            'j_c1_rm', 'j_thigh_rm', 'j_tibia_rm',
            'j_c1_rr', 'j_thigh_rr', 'j_tibia_rr',
        ]
        
        self.num_joints = len(self.joint_names)  # 24 Joints
        self.time_step = 0.0
        
        self.get_logger().info('PhantomX ROS2 Publisher Node Started!')
        self.get_logger().info(f'Publishing to /joint_command with {self.num_joints} joints')

    def publish_joint_commands(self):
        msg = JointState()
        
        # Timestamp setzen
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = ''
        
        # Joint Namen
        msg.name = self.joint_names
        
        # Beispiel: Sinuswellen-Bewegung für Demo
        positions = []
        velocities = []
        efforts = []
        
        for i in range(self.num_joints):
            # Verschiedene Frequenzen für verschiedene Gelenke
            # c1 (i%4==0), c2 (i%4==1), thigh (i%4==2), tibia (i%4==3)
            freq = 0.4 + (i % 4) * 0.15
            amplitude = 0.2  # Radians (reduziert für sicherere Bewegung)
            
            # Position als Sinuswelle
            pos = amplitude * np.sin(2 * np.pi * freq * self.time_step)
            positions.append(pos)
            
            # Velocity (Ableitung der Position)
            vel = amplitude * 2 * np.pi * freq * np.cos(2 * np.pi * freq * self.time_step)
            velocities.append(vel)
            
            # Effort
            efforts.append(0.0)
        
        msg.position = positions
        msg.velocity = velocities
        msg.effort = efforts
        
        # Publishen
        self.joint_pub.publish(msg)
        
        # Zeit inkrementieren
        self.time_step += 0.02

def main(args=None):
    rclpy.init(args=args)
    node = PhantomXNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()