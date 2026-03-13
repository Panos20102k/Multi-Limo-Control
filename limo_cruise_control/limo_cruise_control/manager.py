import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool

class ManagerNode(Node):
    def __init__(self):
        super().__init__('manager_node')

        self.declare_parameter("zoh_period", 0.1)
        self.declare_parameter("stop_time", 15.0)

        self.zoh_period = self.get_parameter("zoh_period").get_parameter_value().double_value
        self.stop_time = self.get_parameter("stop_time").get_parameter_value().double_value
        

        # Initialize
        self.limo_1_vel_msg = Twist()
        self.limo_2_vel_msg = Twist()
        self.started_pmp = False
        self.published_started_pmp = False
        self.started_timing = False
        self.start_time = None

        self.started_pmp_msg = Bool()
        self.limo_1_position = 0.0
        self.limo_2_position = 6.0

        # Publishers
        self.pmp_pub = self.create_publisher(Bool, '/limo_1/pmp', 10)
        self.limo_1_pub = self.create_publisher(Twist, '/limo_1/manager_vel', 10)
        self.limo_2_pub = self.create_publisher(Twist, '/limo_2/manager_vel', 10)

        # Subscribers
        self.limo_1_position_sub = self.create_subscription(Odometry, '/limo_1/odometry/filtered', self.limo_1_position_callback, 10)
        self.limo_2_position_sub = self.create_subscription(Odometry, '/limo_2/odometry/filtered', self.limo_2_position_callback, 10)

        # Timer
        self.create_timer(self.zoh_period, self.output_callback)

    def limo_1_position_callback(self, msg):
        self.limo_1_position = msg.pose.pose.position.x

    def limo_2_position_callback(self, msg):
        self.limo_2_position = msg.pose.pose.position.x

    def output_callback(self):
        gap = self.limo_2_position - self.limo_1_position

        #self.get_logger().info(f"gap = {gap:.3f}, started_pmp = {self.started_pmp}")

        if gap <= 4.0 and not self.published_started_pmp:
            self.started_pmp = True
            self.started_pmp_msg.data = True
            self.pmp_pub.publish(self.started_pmp_msg)
            self.published_started_pmp = True

            self.start_time = self.get_clock().now()
            self.started_timing = True

            self.get_logger().info("PMP Control has started")

        if self.started_timing:
            now = self.get_clock().now()
            elapsed = (now - self.start_time).nanoseconds / 1e9

            if elapsed >= self.stop_time:
                self.limo_1_vel_msg.linear.x = 0.0
                self.limo_2_vel_msg.linear.x = 0.0
                self.limo_1_pub.publish(self.limo_1_vel_msg)
                self.limo_2_pub.publish(self.limo_2_vel_msg)
                self.get_logger().info("End of experiment")

def main(args=None):
    rclpy.init(args=args)
    node = ManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()