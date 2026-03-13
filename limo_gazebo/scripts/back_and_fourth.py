#!/usr/bin/env python3
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
import tf_transformations

def create_pose_stamped(navigator: BasicNavigator, position_x, position_y, orientation_z):
    q_x, q_y, q_z, q_w = tf_transformations.quaternion_from_euler(0.0, 0.0, orientation_z)
    pose = PoseStamped()
    pose.header.frame_id = 'map'
    pose.header.stamp = navigator.get_clock().now().to_msg()
    pose.pose.position.x = position_x
    pose.pose.position.y = position_y
    pose.pose.position.z = 0.0
    pose.pose.orientation.x = q_x
    pose.pose.orientation.y = q_y
    pose.pose.orientation.z = q_z
    pose.pose.orientation.w = q_w
    return pose

def main():
    # --- Init
    rclpy.init()
    nav = BasicNavigator()

    # --- Set initial pose
    #initial_pose = create_pose_stamped(nav, 0.0, 0.0, 0.0)
    #nav.setInitialPose(initial_pose)

    # --- Wait for Nav2
    nav.waitUntilNav2Active()

    # --- Send Nav2 goal
    waypoints = []
    #waypoints.append(create_pose_stamped(nav, 1.8, -1.8, -1.57))
    #waypoints.append(create_pose_stamped(nav, 0.2, 0.2, 2.36))
    # 113_plane back and fourth
    #waypoints.append(create_pose_stamped(nav, 0.7, -2.0, -1.57))
    #waypoints.append(create_pose_stamped(nav, 0.6, -0.1, 1.57))
    # 113_cone back and fourth
    waypoints.append(create_pose_stamped(nav, 0.5, -2.5, -1.57))
    waypoints.append(create_pose_stamped(nav, 0.5, 0.0, 1.57))
    
    # --- Go to one pose
    # nav.goToPose(goal_pose1)
    # while not nav.isTaskComplete():
    #     feedback = nav.getFeedback()
    #     # print(feedback)

    # --- Follow waypoints
    while rclpy.ok():
        nav.followWaypoints(waypoints)
        while not nav.isTaskComplete():
            feedback = nav.getFeedback()
        # print(feedback)
        result = nav.getResult()
        if result == TaskResult.SUCCEEDED:
            print('Route complete! Restartin ...')
        elif result == TaskResult.CANCELED:
            print('Route was canceled! Exiting ...')
            exit(1)
        elif result == TaskResult.FAILED:
            print('Route failed!')

    # --- Shutdown
    rclpy.shutdown()

if __name__ == '__main__':
    main()