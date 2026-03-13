import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist, Quaternion, PoseStamped
from sensor_msgs.msg import LaserScan
from tf_transformations import quaternion_from_euler
from builtin_interfaces.msg import Time
from rclpy.executors import MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup
from rclpy.qos import ReliabilityPolicy, QoSProfile
import time
import numpy as np

PI = 3.14159265

class WanderControllerNode(Node):
    def __init__(self):
        super().__init__('wander_controller_node')

        self.declare_parameter("linear_velocity_gain", 1/25)
        self.declare_parameter("angular_velocity_gain", 1/(4 * PI))
        self.declare_parameter("linear_attraction_vector", 30.0)
        self.declare_parameter("max_lookahead", 0.6)
        self.declare_parameter("min_lookahead", 0.08)
        self.declare_parameter("max_linear_velocity", 0.5)

        # Parameters for sign change detection
        self.declare_parameter("sign_change_slack", 0.1) # Slack for considering a sign change
        self.declare_parameter("sign_change_threshold", 3) # Maximum number of sign changes allowed
        self.declare_parameter("time_window", 4.0) # Time period in seconds to monitor sign changes
        self.declare_parameter("constant_angular_z", 0.2) # The constant twist.angular.z value to set if too many sign changes occur
        self.declare_parameter("cap_duration", 4.0) # Duration for which to hold the capped angular.z (in seconds)

        self.Kx = self.get_parameter("linear_velocity_gain").get_parameter_value().double_value
        self.Kz = self.get_parameter("angular_velocity_gain").get_parameter_value().double_value
        self.Vx = self.get_parameter("linear_attraction_vector").get_parameter_value().double_value
        self.dmax = self.get_parameter("max_lookahead").get_parameter_value().double_value
        self.dmin = self.get_parameter("min_lookahead").get_parameter_value().double_value
        self.v_lin_max = self.get_parameter("max_linear_velocity").get_parameter_value().double_value

        self.slack = self.get_parameter("sign_change_slack").get_parameter_value().double_value
        self.threshold = self.get_parameter("sign_change_threshold").get_parameter_value().integer_value
        self.window = self.get_parameter("time_window").get_parameter_value().double_value
        self.const = self.get_parameter("constant_angular_z").get_parameter_value().double_value
        self.cap_dur = self.get_parameter("cap_duration").get_parameter_value().double_value

        self.mutuallyexclusive_group_1 = MutuallyExclusiveCallbackGroup()
        self.mutuallyexclusive_group_2 = MutuallyExclusiveCallbackGroup()
        
        # Publishers
        self.twist = Twist()
        self.cmd_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.att_pub = self.create_publisher(PoseStamped, 'attraction_vector', 10)
        self.rep_pub = self.create_publisher(PoseStamped, 'repulsion_vector', 10)
        self.fin_pub = self.create_publisher(PoseStamped, 'final_vector', 10)
        
        # Create Subscriber for laser data
        self.sub_scan = self.create_subscription(LaserScan, 'scan', self.scan_callback, QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT), callback_group=self.mutuallyexclusive_group_1)
        
        # Create Timer for main control loop
        self.timer_period = 0.1
        self.create_timer(self.timer_period, self.controller, self.mutuallyexclusive_group_2)

        
        # Create attraction and  repulsion vectors
        self.V_attraction = [self.Vx, 0.0]
        self.attraction_vector = self.create_vector_pose(self.V_attraction[0], self.V_attraction[1])
        self.V_repulsion = [0.0, 0.0]
        self.repulsion_vector = PoseStamped()
        
        # Variables to track state of sign change detection
        self.capped_angular_z = None # The actual capped twist.angular.z value: +/- the constant twist.angular.z
        self.previous_sign = None  # To track the previous sign of final_vector.pose.orientation.z
        self.sign_change_times = []  # To track times when sign changes occurred
        self.cap_active = False  # Whether the capping is currently active
        self.cap_start_time = None  # Time when capping was triggered

    def controller(self):
        
        # Create final vector
        self.x_final = self.V_attraction[0] + self.V_repulsion[0]
        self.y_final = self.V_attraction[1] + self.V_repulsion[1]
        self.final_vector = self.create_vector_pose(self.x_final, self.y_final)
        
        # Publish all vectors to corresponding topics
        self.att_pub.publish(self.attraction_vector)
        self.rep_pub.publish(self.repulsion_vector)
        self.fin_pub.publish(self.final_vector)

         # Compute linear and angular velocities
        if self.x_final < 0.0:
            v_lin = 0.0
        else:
            v_lin = math.sqrt(math.pow(self.x_final,2) + math.pow(self.y_final,2))

        v_ang = math.atan2(self.y_final, self.x_final)

        

        self.twist.linear.x = min(v_lin * self.Kx, self.v_lin_max)
        self.twist.angular.z = v_ang * self.Kz

        # Check for frequent sign changes in final_vector.pose.orientation.z
        self.detect_frequent_sign_changes()

        self.cmd_pub.publish(self.twist)

    def create_vector_pose(self, x, y):
        # Method to create a PoseStaamped vector
        vector = PoseStamped()
        vector.header.frame_id = "base_link"
        now = self.get_clock().now() 
        vector.header.stamp = Time(sec=int(now.nanoseconds // 1e9), nanosec=int(now.nanoseconds % 1e9))
        vector.pose.position.x = 0.0
        vector.pose.position.y = 0.0
        vector.pose.position.z = 0.0

        angle = math.atan2(y, x)
        q = quaternion_from_euler(0, 0, angle)
        quaternion_msg = Quaternion()
        quaternion_msg.x = q[0]
        quaternion_msg.y = q[1]
        quaternion_msg.z = q[2]
        quaternion_msg.w = q[3]
        vector.pose.orientation = quaternion_msg
        
        return vector

    def scan_callback(self, _msg):
        # Analyze laser data and create the repulsion vector
        angle_min = _msg.angle_min
        angle_increment = _msg.angle_increment
        scan = _msg.ranges
        x_r = 0.0
        y_r = 0.0

        for i in range(len(scan)):
            if scan[i] < self.dmax and scan[i] > self.dmin:
                repulsion_strength = 1 / (scan[i] ** 2)
                x_r -= repulsion_strength*math.cos(angle_min + angle_increment * i)
                y_r -= repulsion_strength*math.sin(angle_min + angle_increment * i)

        self.V_repulsion = [x_r, y_r]

        self.repulsion_vector = self.create_vector_pose(self.V_repulsion[0], self.V_repulsion[1])

    def detect_frequent_sign_changes(self):
        # Function to detect frequent sign changes in final_vector.pose.orientation.z and 
        # cap twist.angular.z to a constant value if the threshold is exceeded.
 
        current_time = time.time()  # Get the current time
        
        if self.cap_active:
            # Capping is already active, check if the duration has passed
            if current_time - self.cap_start_time < self.cap_dur:
                # Continue publishing the capped value
                self.twist.angular.z = self.capped_angular_z
            else:
                # Capping duration has expired, return to normal control
                self.cap_active = False
        else:
            # If capping is not active, detect frequent sign changes
            if self.final_vector.pose.orientation.z >= self.slack:
                current_sign = 1
            elif self.final_vector.pose.orientation.z <= -self.slack:
                current_sign = -1
            else:
                return
            
            if self.previous_sign is None:
                # This is the first time running, so initialize the previous sign
                self.previous_sign = current_sign
            elif current_sign != self.previous_sign:
                # Sign has changed
                self.sign_change_times.append(current_time)  # Record the time of the sign change
                self.previous_sign = current_sign  # Update the previous sign
            
            # Remove sign change times that are outside the time window (older than t seconds)
            self.sign_change_times = [t for t in self.sign_change_times if current_time - t <= self.window]

            # If there have been more than x sign changes within the time window, trigger capping
            if len(self.sign_change_times) > self.threshold:
                self.cap_active = True  # Activate capping
                self.cap_start_time = current_time  # Record the time capping started
                sign = np.random.choice([1, -1])
                self.capped_angular_z = sign * self.const
                self.twist.angular.z = self.capped_angular_z  # Set twist.angular.z to the constant value
                self.sign_change_times.clear()  # Clear the sign change list to reset detection

def main(args=None):
    rclpy.init(args=args)

    potential_field = WanderControllerNode()

    # Use MultiThreadedExecutor
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(potential_field)
    
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        potential_field.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()