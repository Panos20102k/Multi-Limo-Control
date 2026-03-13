from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    limo_navigation_dir = get_package_share_directory('limo_bringup')
    rviz_config_dir = os.path.join(limo_navigation_dir, 'config', 'rviz2.rviz')
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Launch the RViz node with the specified configuration 
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_dir],
        parameters=[{'use_sim_time': use_sim_time}],
        output='screen'
    )

    return LaunchDescription([
        rviz_node
    ])