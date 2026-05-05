cmake_minimum_required(VERSION 3.8)
project(phantomx_package)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)

# Python package installation
ament_python_install_package(${PROJECT_NAME})

# Installiere den launch-Ordner
install(DIRECTORY
  launch
  scripts
  src
  DESTINATION share/${PROJECT_NAME}
)

# Install Python executables (REMOVE add_executable for .py files!)
install(PROGRAMS
  scripts/controll_joints/phantomx_node_single_joint.py
  scripts/controll_joints/phantomx_node_multi_joints.py
  scripts/policy/phantomx_apply_policy.py
  launch/launch_phantomx_policycontroll.launch.py
  src/fake_imu_data.py
  src/fake_joint_state.py
  DESTINATION lib/${PROJECT_NAME}
)

# Hier könntest du später C++ executables hinzufügen:
# add_executable(phantomx_cpp_node src/phantomx_cpp_node.cpp)
# target_include_directories(phantomx_cpp_node PUBLIC ...)
# ament_target_dependencies(phantomx_cpp_node "rclcpp" "std_msgs" "sensor_msgs")
# install(TARGETS phantomx_cpp_node DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()