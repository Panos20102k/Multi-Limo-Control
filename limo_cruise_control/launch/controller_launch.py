from launch import LaunchDescription
from launch_ros.actions import Node
import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    ld = LaunchDescription()

    package_name = 'limo_cruise_control' 
    twist_mux_1_params = os.path.join(get_package_share_directory(package_name),'config','twist_mux_1.yaml')
    twist_mux_2_params = os.path.join(get_package_share_directory(package_name),'config','twist_mux_2.yaml')
    transient_controller_params = os.path.join(get_package_share_directory(package_name),'config','transient_controller.yaml')
    pmp_controller_params = os.path.join(get_package_share_directory(package_name),'config','pmp_controller.yaml')
    manager_params = os.path.join(get_package_share_directory(package_name),'config','manager.yaml')
    actuation_filter_params = os.path.join(get_package_share_directory(package_name),'config','actuation_filter.yaml')


    start_transient_controller = Node(
        package=package_name,
        executable='transient_controller',
        name='transient_controller',
        parameters=[transient_controller_params]
    )

    start_twist_mux_1 = Node(
        package="twist_mux",
        executable="twist_mux",
        name="twist_mux_1",
        parameters=[twist_mux_1_params],
        remappings=[('/cmd_vel_out','/limo_1/cmd_vel')]
    )

    start_twist_mux_2 = Node(
        package="twist_mux",
        executable="twist_mux",
        name="twist_mux_2",
        parameters=[twist_mux_2_params],
        remappings=[('/cmd_vel_out','/limo_2/cmd_vel')]
    )

    start_manager = Node(
        package=package_name,
        executable='manager',
        name='manager',
        parameters=[manager_params]
    )

    start_pmp_controller = Node(
        package=package_name,
        executable='pmp_controller',
        name='pmp_controller',
        parameters=[pmp_controller_params]
    )

    start_actuation_filter = Node(
        package=package_name,
        executable='actuation_filter',
        name='actuation_filter',
        parameters=[actuation_filter_params]
    )


    ld.add_action(start_transient_controller)
    ld.add_action(start_twist_mux_1)
    ld.add_action(start_twist_mux_2)
    ld.add_action(start_manager)
    ld.add_action(start_pmp_controller)
    ld.add_action(start_actuation_filter)

    return ld