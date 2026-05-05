#!/usr/bin/env python3
# phantomx_rl_node.py
# ROS2 Node: lädt die trainierte Policy und steuert den PhantomX Roboter
#
# Subscriptions:
#   /joint_states          → sensor_msgs/JointState
#   /imu/data              → sensor_msgs/Imu
#   /cmd_vel               → geometry_msgs/Twist   (velocity commands)
#
# Publications:
#   /joint_position_targets → sensor_msgs/JointState

import rclpy
from rclpy.node import Node

import numpy as np
import torch
import yaml
import os

from sensor_msgs.msg import JointState, Imu
from geometry_msgs.msg import Twist




# ⚠️ Zwei Dinge musst du noch anpassen im phantomx_rl_node.py:

# DEFAULT_JOINT_POS → die Defaultwerte aus deiner PhantomxThesisEnvCfg eintragen
# ACTION_SCALE → den action_scale Wert aus deiner Config eintragen
# Lineare Geschwindigkeit (lin_vel_b) → kommt nicht aus dem IMU, sondern aus einem Odometrie-Schätzer — da brauchst du noch eine Quelle (z.B. /odom Topic)  


# ---------------------------------------------------------------
# Gelenkreihenfolge muss exakt mit Isaac Lab übereinstimmen!
# Passe diese Liste an deine joint_names aus der YAML an.
# ---------------------------------------------------------------
JOINT_NAMES = [
    "j_c1_lf",      "j_thigh_lf",   "j_tibia_lf",
    "j_c1_lm",      "j_thigh_lm",   "j_tibia_lm",
    "j_c1_lr",      "j_thigh_lr",   "j_tibia_lr",
    "j_c1_rf",      "j_thigh_rf",   "j_tibia_rf",
    "j_c1_rm",      "j_thigh_rm",   "j_tibia_rm",
    "j_c1_rr",      "j_thigh_rr",   "j_tibia_rr",
]

# Default-Gelenkpositionen (aus IsaacLab cfg übernehmen!)
# Muss mit PhantomxThesisEnvCfg.default_joint_pos übereinstimmen
DEFAULT_JOINT_POS = np.zeros(18)  # ← Hier deine Defaultwerte eintragen!

# Action Scale (aus PhantomxThesisEnvCfg.action_scale)
ACTION_SCALE = 0.5  # ← Hier deinen Wert eintragen!


class PhantomxRLNode(Node):
    def __init__(self):
        super().__init__("phantomx_rl_node")

        # -------------------------------------------------------
        # Parameter
        # -------------------------------------------------------
        self.declare_parameter("policy_path", "")
        self.declare_parameter("io_descriptors_path", "")
        self.declare_parameter("control_frequency", 50.0)  # Hz

        policy_path = self.get_parameter("policy_path").get_parameter_value().string_value
        io_path = self.get_parameter("io_descriptors_path").get_parameter_value().string_value
        freq = self.get_parameter("control_frequency").get_parameter_value().double_value

        # -------------------------------------------------------
        # Policy laden
        # -------------------------------------------------------
        if not os.path.exists(policy_path):
            self.get_logger().error(f"Policy nicht gefunden: {policy_path}")
            raise FileNotFoundError(policy_path)

        self.get_logger().info(f"Lade Policy: {policy_path}")
        self.policy = torch.jit.load(policy_path, map_location="cpu")
        self.policy.eval()
        self.get_logger().info("Policy geladen ✓")

        # IO Descriptors laden (optional, für Logging)
        if io_path and os.path.exists(io_path):
            with open(io_path, "r") as f:
                self.io_desc = yaml.safe_load(f)
            self.get_logger().info("IO Descriptors geladen ✓")

        # -------------------------------------------------------
        # State-Variablen (entsprechen _get_observations in env)
        # -------------------------------------------------------
        self.joint_pos = np.zeros(18)        # aktuelle Gelenkpositionen
        self.joint_vel = np.zeros(18)        # aktuelle Gelenkgeschwindigkeiten
        self.lin_vel_b = np.zeros(3)         # lineare Geschwindigkeit im Body-Frame
        self.ang_vel_b = np.zeros(3)         # Winkelgeschwindigkeit im Body-Frame
        self.gravity_b = np.array([0, 0, -1]) # projizierter Schwerkraftvektor
        self.commands = np.zeros(3)          # [vx, vy, yaw_rate]
        self.last_actions = np.zeros(18)     # vorherige Aktionen

        self._joint_states_received = False
        self._imu_received = False

        # -------------------------------------------------------
        # ROS2 Subscriptions & Publications
        # -------------------------------------------------------
        self.sub_joints = self.create_subscription(
            JointState, "/joint_states", self.joint_states_callback, 10
        )
        self.sub_imu = self.create_subscription(
            Imu, "/imu/data", self.imu_callback, 10
        )
        self.sub_cmd = self.create_subscription(
            Twist, "/cmd_vel", self.cmd_vel_callback, 10
        )

        self.pub_joints = self.create_publisher(
            JointState, "/joint_position_targets", 10
        )

        # Control Loop Timer
        self.timer = self.create_timer(1.0 / freq, self.control_loop)
        self.get_logger().info(f"Control loop gestartet @ {freq} Hz")

    # -----------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------
    def joint_states_callback(self, msg: JointState):
        """Liest Gelenkpositionen und -geschwindigkeiten."""
        for i, name in enumerate(JOINT_NAMES):
            if name in msg.name:
                idx = msg.name.index(name)
                self.joint_pos[i] = msg.position[idx]
                if len(msg.velocity) > idx:
                    self.joint_vel[i] = msg.velocity[idx]
        self._joint_states_received = True

    def imu_callback(self, msg: Imu):
        """Liest IMU-Daten: lineare/angulare Geschwindigkeit + Orientierung."""
        # Angulare Geschwindigkeit (Body-Frame)
        self.ang_vel_b[0] = msg.angular_velocity.x
        self.ang_vel_b[1] = msg.angular_velocity.y
        self.ang_vel_b[2] = msg.angular_velocity.z

        # Lineare Beschleunigung → Schwerkraftvektor projizieren
        # Normalisieren der Schwerkraftkomponente
        ax = msg.linear_acceleration.x
        ay = msg.linear_acceleration.y
        az = msg.linear_acceleration.z
        norm = np.sqrt(ax**2 + ay**2 + az**2)
        if norm > 0.1:
            self.gravity_b = np.array([ax, ay, az]) / norm

        # Lineare Geschwindigkeit: muss aus Odometrie oder Zustandsschätzer kommen!
        # Hier Platzhalter - ersetze mit deiner Odometrie-Quelle
        # self.lin_vel_b = ...
        self._imu_received = True

    def cmd_vel_callback(self, msg: Twist):
        """Empfängt Velocity Commands."""
        self.commands[0] = msg.linear.x   # vx
        self.commands[1] = msg.linear.y   # vy
        self.commands[2] = msg.angular.z  # yaw_rate

    # -----------------------------------------------------------
    # Control Loop
    # -----------------------------------------------------------
    def control_loop(self):
        """Hauptloop: Observation → Policy → Action → Publish"""

        if not self._joint_states_received or not self._imu_received:
            self.get_logger().warn("Warte auf Sensordaten...", throttle_duration_sec=2.0)
            return

        # --- Observation bauen (muss exakt _get_observations() entsprechen!) ---
        obs = np.concatenate([
            self.lin_vel_b,                              # 3
            self.ang_vel_b,                              # 3
            self.gravity_b,                              # 3
            self.commands,                               # 3
            self.joint_pos - DEFAULT_JOINT_POS,          # 18 (relativ!)
            self.joint_vel,                              # 18
            self.last_actions,                           # 18
        ])  # = 66 total

        # --- Policy Inferenz ---
        with torch.no_grad():
            obs_tensor = torch.FloatTensor(obs).unsqueeze(0)  # [1, 66]
            action_tensor = self.policy(obs_tensor)            # [1, 18]
            actions = action_tensor.squeeze(0).numpy()         # [18]

        # --- Action → Gelenkposition (aus _pre_physics_step) ---
        # processed_actions = action_scale * actions + default_joint_pos
        joint_targets = ACTION_SCALE * actions + DEFAULT_JOINT_POS

        # --- Vorherige Aktion speichern ---
        self.last_actions = actions.copy()

        # --- Publishen ---
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINT_NAMES
        msg.position = joint_targets.tolist()
        self.pub_joints.publish(msg)

    # -----------------------------------------------------------


def main(args=None):
    rclpy.init(args=args)
    node = PhantomxRLNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()