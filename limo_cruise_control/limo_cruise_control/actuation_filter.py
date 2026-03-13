import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool

class ActuationFilterNode(Node):
    def __init__(self):
        super().__init__('actuation_filter_node')

        # Parameters
        self.declare_parameter("zoh_period", 0.1)
        self.declare_parameter("initial_velocity", 0.5)
        self.declare_parameter("pt1_time_constant", 0.1)
        self.declare_parameter("pt1_gain", 1.4)

        self.zoh_period = self.get_parameter("zoh_period").get_parameter_value().double_value
        self.v0 = self.get_parameter("initial_velocity").get_parameter_value().double_value
        self.tau = self.get_parameter("pt1_time_constant").get_parameter_value().double_value
        self.k = self.get_parameter("pt1_gain").get_parameter_value().double_value

        # Initialize
        self.u = 0.0
        self.v = self.v0
        self.v_new = 0.0
        self.v_msg = Twist()
        self.start_pmp = False

        # Auxiliary variables
        self.alpha = math.exp(-self.zoh_period/self.tau)

        # Publishers 
        self.v_pub = self.create_publisher(Twist, '/limo_1/filter_vel', 10)

        # Subscribers
        self.manager_sub = self.create_subscription(Bool, '/limo_1/pmp', self.manager_callback, 10)
        self.limo_1_velocity_sub = self.create_subscription(Odometry, '/limo_1/odometry/filtered', self.limo_1_velocity_callback, 10)
        self.pmp_sub = self.create_subscription(Twist, '/limo_1/pmp_vel', self.pmp_callback, 10)

        # Timer
        self.create_timer(self.zoh_period, self.output_callback)


    def limo_1_velocity_callback(self, msg):
        self.v = msg.twist.twist.linear.x

    def pmp_callback(self, msg):
        self.u = msg.linear.x

    def manager_callback(self, msg):
        self.start_pmp = msg.data

    def output_callback(self):
        if self.start_pmp:
            self.v_new = self.alpha*self.v + self.k*(1-self.alpha)*self.u
            self.v_msg.linear.x = self.v_new
            self.v_pub.publish(self.v_msg)

        

def main(args=None):
    rclpy.init(args=args)
    node = ActuationFilterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()