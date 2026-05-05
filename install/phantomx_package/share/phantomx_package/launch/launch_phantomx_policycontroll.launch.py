#!/usr/bin/env python3
# phantomx_rl.launch.py
# Verwendung:
#   ros2 launch phantomx_package phantomx_rl.launch.py \
#     policy_path:=/workspace/ros2_ws/src/phantomx_package/scripts/policy.pt \
#     io_descriptors_path:=/workspace/ros2_ws/src/phantomx_package/scripts/template_phantomx_thesis_direct_v0_IO_descriptors.yaml

# ros2 launch phantomx_package launch_phantomx_policycontroll.launch.py policy_path:=/workspace/ros2_ws/src/phantomx_package/scripts/policy/policy.pt io_descriptors_path:=/workspace/ros2_ws/src/phantomx_package/scripts/policy/template_phantomx_thesis_direct_v0_IO_descriptors.yaml



from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("policy_path", description="Pfad zur exportierten policy.pt"),
        DeclareLaunchArgument("io_descriptors_path", default_value="", description="Pfad zur IO-Descriptors YAML"),
        DeclareLaunchArgument("control_frequency", default_value="50.0", description="Control loop Frequenz in Hz"),

        Node(
            package="phantomx_package",
            executable="phantomx_apply_policy.py",
            name="phantomx_rl_node",
            output="screen",
            parameters=[{
                "policy_path": LaunchConfiguration("policy_path"),
                "io_descriptors_path": LaunchConfiguration("io_descriptors_path"),
                "control_frequency": LaunchConfiguration("control_frequency"),
            }],
        ),
    ])