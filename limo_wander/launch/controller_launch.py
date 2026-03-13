from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    ld = LaunchDescription()

    package_name = 'limo_wander' 

    start_wander_controller_1 = Node(
        package='limo_wander',
        executable='wander_controller',
        namespace='limo_1'
    )

    start_wander_controller_2 = Node(
        package='limo_wander',
        executable='wander_controller',
        namespace='limo_2'
    )

    start_wander_controller_3 = Node(
        package='limo_wander',
        executable='wander_controller',
        namespace='limo_3'
    )

    start_wander_controller_4 = Node(
        package='limo_wander',
        executable='wander_controller',
        namespace='limo_4'
    )

    start_wander_controller_5 = Node(
        package='limo_wander',
        executable='wander_controller',
        namespace='limo_5'
    )

    start_wander_controller_6 = Node(
        package='limo_wander',
        executable='wander_controller',
        namespace='limo_6'
    )

    start_wander_controller_7 = Node(
        package='limo_wander',
        executable='wander_controller',
        namespace='limo_7'
    )

    start_wander_controller_8 = Node(
        package='limo_wander',
        executable='wander_controller',
        namespace='limo_8'
    )



    ld.add_action(start_wander_controller_1)
    ld.add_action(start_wander_controller_2)
    ld.add_action(start_wander_controller_3)
    ld.add_action(start_wander_controller_4)
    ld.add_action(start_wander_controller_5)
    ld.add_action(start_wander_controller_6)
    ld.add_action(start_wander_controller_7)
    ld.add_action(start_wander_controller_8)

    return ld