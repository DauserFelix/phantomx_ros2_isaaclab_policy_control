#!/usr/bin/env python3
# fake_joint_states.py
# Publiziert fake JointStates: alle Gelenke in Defaultposition

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState


# Muss exakt mit JOINT_NAMES in phantomx_rl_node.py übereinstimmen!
JOINT_NAMES = [
    "j_c1_lf",      "j_thigh_lf",   "j_tibia_lf",
    "j_c1_lm",      "j_thigh_lm",   "j_tibia_lm",
    "j_c1_lr",      "j_thigh_lr",   "j_tibia_lr",
    "j_c1_rf",      "j_thigh_rf",   "j_tibia_rf",
    "j_c1_rm",      "j_thigh_rm",   "j_tibia_rm",
    "j_c1_rr",      "j_thigh_rr",   "j_tibia_rr",
]

# Defaultpositionen — muss mit DEFAULT_JOINT_POS in phantomx_rl_node.py übereinstimmen!
DEFAULT_JOINT_POS = [0.0] * 18  # ← deine echten Defaultwerte eintragen


class FakeJointStatesPublisher(Node):
    def __init__(self):
        super().__init__("fake_joint_states_publisher")
        self.pub = self.create_publisher(JointState, "/joint_states", 10)
        self.timer = self.create_timer(0.02, self.publish)  # 50 Hz
        self.get_logger().info("Fake JointStates Publisher gestartet")

    def publish(self):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINT_NAMES
        msg.position = DEFAULT_JOINT_POS        # Gelenke in Defaultposition
        msg.velocity = [0.0] * 18              # keine Bewegung
        msg.effort   = [0.0] * 18              # keine Kräfte
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = FakeJointStatesPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()