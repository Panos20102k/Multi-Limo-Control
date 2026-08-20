import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('limo_single_stage_learning')
    parameters = os.path.join(share, 'config', 'single_stage.yaml')
    mux_parameters = os.path.join(share, 'config', 'twist_mux.yaml')
    return LaunchDescription([
        Node(
            package='limo_single_stage_learning',
            executable='single_stage_learning', name='single_stage_learning',
            parameters=[parameters], output='screen',
        ),
        Node(
            package='limo_single_stage_learning', executable='actuation_filter',
            name='single_stage_actuation_filter', parameters=[parameters],
            output='screen',
        ),
        Node(
            package='twist_mux', executable='twist_mux',
            name='single_stage_twist_mux', parameters=[mux_parameters],
            remappings=[('/cmd_vel_out', '/limo_1/cmd_vel')],
            output='screen',
        ),
    ])
