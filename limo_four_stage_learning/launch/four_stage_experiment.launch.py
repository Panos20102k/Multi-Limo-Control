import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    share = get_package_share_directory('limo_four_stage_learning')
    parameters = os.path.join(share, 'config', 'four_stage.yaml')
    mux_parameters = os.path.join(share, 'config', 'twist_mux.yaml')
    return LaunchDescription([
        Node(
            package='limo_four_stage_learning', executable='four_stage_learning',
            name='four_stage_learning', parameters=[parameters], output='screen',
        ),
        Node(
            package='limo_four_stage_learning', executable='actuation_filter',
            name='four_stage_actuation_filter', parameters=[parameters], output='screen',
        ),
        Node(
            package='twist_mux', executable='twist_mux', name='four_stage_twist_mux',
            parameters=[mux_parameters],
            remappings=[('/cmd_vel_out', '/limo_1/cmd_vel')], output='screen',
        ),
    ])
