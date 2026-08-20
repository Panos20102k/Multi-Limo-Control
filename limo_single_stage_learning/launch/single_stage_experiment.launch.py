import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('limo_single_stage_learning')
    parameters = os.path.join(share, 'config', 'single_stage.yaml')
    mux_parameters = os.path.join(share, 'config', 'twist_mux.yaml')
    ekf_parameters = os.path.join(share, 'config', 'ekf_velocity.yaml')
    return LaunchDescription([
        DeclareLaunchArgument('start_ekf', default_value='true'),
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        Node(
            package='robot_localization', executable='ekf_node',
            name='ekf_filter_node_1', parameters=[
                ekf_parameters,
                {'use_sim_time': LaunchConfiguration('use_sim_time')},
            ],
            remappings=[
                ('/odometry/filtered', '/limo_1/odometry/filtered'),
                ('/diagnostics', '/limo_1/diagnostics'),
                ('/set_pose', '/limo_1/set_pose'),
            ],
            condition=IfCondition(LaunchConfiguration('start_ekf')),
            output='screen',
        ),
        Node(
            package='limo_single_stage_learning',
            executable='single_stage_learning', name='single_stage_learning',
            parameters=[
                parameters,
                {'use_sim_time': LaunchConfiguration('use_sim_time')},
            ], output='screen',
        ),
        Node(
            package='limo_single_stage_learning', executable='actuation_filter',
            name='single_stage_actuation_filter', parameters=[
                parameters,
                {'use_sim_time': LaunchConfiguration('use_sim_time')},
            ],
            output='screen',
        ),
        Node(
            package='twist_mux', executable='twist_mux',
            name='single_stage_twist_mux', parameters=[mux_parameters],
            remappings=[('/cmd_vel_out', '/limo_1/cmd_vel')],
            output='screen',
        ),
    ])
