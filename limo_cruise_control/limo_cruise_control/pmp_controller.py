import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from std_msgs.msg import Bool

class PMPControllerNode(Node):
    def __init__(self):
        super().__init__('pmp_controller_node')
        self.start_time = self.get_clock().now()

        # Parameters
        self.declare_parameter("optimal_control_mode", True)
        self.declare_parameter("stop_time", 15.0)
        self.declare_parameter("zoh_period", 0.1)
        self.declare_parameter("reference_velocity", 0.6)
        self.declare_parameter("initial_velocity", 0.5)

        self.declare_parameter("state_penalty_coefficient", 1.0)
        self.declare_parameter("control_penalty_coefficient", 0.5)
        self.declare_parameter("final_state_penalty_coefficient", 1.0)
        self.declare_parameter("safety_distance", 1.0)
        self.declare_parameter("reaction_time_coefficient", 1.0)
        self.declare_parameter("lower_control_bound", 0.1)
        self.declare_parameter("upper_control_bound", 0.4)

        self.optimal = self.get_parameter("optimal_control_mode").get_parameter_value().bool_value
        self.stop_time = self.get_parameter("stop_time").get_parameter_value().double_value
        self.zoh_period = self.get_parameter("zoh_period").get_parameter_value().double_value
        self.vref = self.get_parameter("reference_velocity").get_parameter_value().double_value
        self.v0 = self.get_parameter("initial_velocity").get_parameter_value().double_value
        self.q = self.get_parameter("state_penalty_coefficient").get_parameter_value().double_value
        self.r = self.get_parameter("control_penalty_coefficient").get_parameter_value().double_value
        self.h = self.get_parameter("final_state_penalty_coefficient").get_parameter_value().double_value
        self.delta = self.get_parameter("safety_distance").get_parameter_value().double_value
        self.xi = self.get_parameter("reaction_time_coefficient").get_parameter_value().double_value
        self.lower = self.get_parameter("lower_control_bound").get_parameter_value().double_value
        self.upper = self.get_parameter("upper_control_bound").get_parameter_value().double_value

        self.bounds = [self.lower, self.upper]

        if self.optimal:
            self.tau = 0.1
            self.k = 1.4
        else:
            self.tau = 0.3
            self.k = 1.2

        # Initialize
        self.start_pmp = False
        self.p = 0.0
        self.pf = 0.0
        self.vf = 0.1
        self.u = 0.0
        self.u_msg = Twist()

        # Auxiliary variables
        self.omega = (self.q/self.r)**(1/2)
        self.A = self.v0 - self.vref
        self.T = self.stop_time
        self.B_num = -self.A*(self.h/self.r*math.cosh(self.omega*self.T)+self.omega*math.sinh(self.omega*self.T))
        self.B_denum = (self.omega*math.cosh(self.omega*self.T)+self.h/self.r*math.sinh(self.omega*self.T))
        self.B = self.B_num/self.B_denum


        # Publishers 
        self.u_pub = self.create_publisher(Twist, '/limo_1/pmp_vel', 10)

        # Subscribers
        self.manager_sub = self.create_subscription(Bool, '/limo_1/pmp', self.manager_callback, 10)
        self.limo_1_position_sub = self.create_subscription(Odometry, '/limo_1/odometry/filtered', self.limo_1_position_callback, 10)
        self.limo_2_position_sub = self.create_subscription(Odometry, '/limo_2/odometry/filtered', self.limo_2_position_callback, 10)

        # Timer
        self.create_timer(self.zoh_period, self.output_callback)


    def manager_callback(self, msg):
        self.start_pmp = msg.data

    def limo_1_position_callback(self, msg):
        self.p = msg.pose.pose.position.x 

    def limo_2_position_callback(self, msg):
        self.pf = msg.pose.pose.position.x 


    def output_callback(self):
        if self.start_pmp:
            s = self.delta - self.xi*(self.pf - self.p)
            if s < 0:
                now = self.get_clock().now()
                t = (now - self.start_time).nanoseconds / 1e9
                u_first = self.vref+(self.A+self.tau*self.omega*self.B)*math.cosh(self.omega*t)
                u_second = (self.B+self.tau*self.omega*self.A)*math.sinh(self.omega*t)
                self.u = (u_first + u_second)/self.k
            else:
                self.u = self.vf/self.k
            
            self.u_msg.linear.x = min(max(self.u, self.bounds[0]), self.bounds[1])
            self.u_pub.publish(self.u_msg)

        

def main(args=None):
    rclpy.init(args=args)
    node = PMPControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()