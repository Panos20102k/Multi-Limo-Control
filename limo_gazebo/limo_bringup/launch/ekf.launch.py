import launch
from launch.substitutions import Command, LaunchConfiguration
import launch_ros
import os

def generate_launch_description():
    limo_bringup_pkg_share = launch_ros.substitutions.FindPackageShare(package='limo_bringup').find('limo_bringup')

    # launch ekf nodes for different limos
    robot_localization_node_1 = launch_ros.actions.Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node_1',  
        output='screen',
        parameters=[
            os.path.join(limo_bringup_pkg_share, 'config/ekf_1.yaml'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ], 
        remappings=[
        ('/odometry/filtered', '/limo_1/odometry/filtered'),
        ('/diagnostics', '/limo_1/diagnostics'),
        ('/set_pose', '/limo_1/set_pose')
        ]
    )

    robot_localization_node_2 = launch_ros.actions.Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node_2', 
        output='screen',
        parameters=[
            os.path.join(limo_bringup_pkg_share, 'config/ekf_2.yaml'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ], 
        remappings=[
        ('/odometry/filtered', '/limo_2/odometry/filtered'),
        ('/diagnostics', '/limo_2/diagnostics'),
        ('/set_pose', '/limo_2/set_pose')
        ]
    )

    robot_localization_node_3 = launch_ros.actions.Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node_3', 
        output='screen',
        parameters=[
            os.path.join(limo_bringup_pkg_share, 'config/ekf_3.yaml'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ], 
        remappings=[
        ('/odometry/filtered', '/limo_3/odometry/filtered'),
        ('/diagnostics', '/limo_3/diagnostics'),
        ('/set_pose', '/limo_3/set_pose')
        ]
    )

    return launch.LaunchDescription([
        launch.actions.DeclareLaunchArgument(name='use_sim_time', default_value='true',
                                            description='Flag to enable use_sim_time'),
        robot_localization_node_1,
        robot_localization_node_2,
        #robot_localization_node_3

    ])