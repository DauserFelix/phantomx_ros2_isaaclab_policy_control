#!/usr/bin/env python3
# fake_imu_publisher.py
# Publiziert fake IMU-Daten: Roboter bewegt sich vorwärts (x), y und z konstant

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
import math


class FakeImuPublisher(Node):
    def __init__(self):
        super().__init__("fake_imu_publisher")
        self.pub = self.create_publisher(Imu, "/imu/data", 10)
        self.timer = self.create_timer(0.02, self.publish_imu)  # 50 Hz
        self.get_logger().info("Fake IMU Publisher gestartet")

    def publish_imu(self):
        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "imu_link"

        # Orientierung: aufrecht (keine Neigung)
        msg.orientation.x = 0.0
        msg.orientation.y = 0.0
        msg.orientation.z = 0.0
        msg.orientation.w = 1.0

        # Lineare Beschleunigung: Schwerkraft nach unten → gravity_b = [0, 0, -1]
        msg.linear_acceleration.x = 0.0
        msg.linear_acceleration.y = 0.0
        msg.linear_acceleration.z = -9.81  # Schwerkraft

        # Angulare Geschwindigkeit: keine Rotation
        msg.angular_velocity.x = 0.0
        msg.angular_velocity.y = 0.0
        msg.angular_velocity.z = 0.0

        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = FakeImuPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()