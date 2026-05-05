#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import numpy as np
from builtin_interfaces.msg import Time

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
        
        # Hexapod hat typischerweise 18 Gelenke (6 Beine x 3 Gelenke)
        # Passe die Namen an deine URDF/Robot-Konfiguration an
        self.joint_names = [
            # Bein 1
            'leg1_coxa_joint', 'leg1_femur_joint', 'leg1_tibia_joint',
            # Bein 2
            'leg2_coxa_joint', 'leg2_femur_joint', 'leg2_tibia_joint',
            # Bein 3
            'leg3_coxa_joint', 'leg3_femur_joint', 'leg3_tibia_joint',
            # Bein 4
            'leg4_coxa_joint', 'leg4_femur_joint', 'leg4_tibia_joint',
            # Bein 5
            'leg5_coxa_joint', 'leg5_femur_joint', 'leg5_tibia_joint',
            # Bein 6
            'leg6_coxa_joint', 'leg6_femur_joint', 'leg6_tibia_joint',
        ]
        
        self.num_joints = len(self.joint_names)
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
        # In der Praxis würdest du hier echte Trajektorien berechnen
        positions = []
        velocities = []
        efforts = []
        
        for i in range(self.num_joints):
            # Verschiedene Frequenzen für verschiedene Gelenke
            freq = 0.5 + (i % 3) * 0.2
            amplitude = 0.3  # Radians
            
            # Position als Sinuswelle
            pos = amplitude * np.sin(2 * np.pi * freq * self.time_step)
            positions.append(pos)
            
            # Velocity (Ableitung der Position)
            vel = amplitude * 2 * np.pi * freq * np.cos(2 * np.pi * freq * self.time_step)
            velocities.append(vel)
            
            # Effort (kannst du auf 0 setzen wenn nicht benötigt)
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