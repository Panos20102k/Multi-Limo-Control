import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TransientControllerNode(Node):
    def __init__(self):
        super().__init__('transient_controller_node')
        self.get_logger().info("Transient Control has started")

        # Parameters
        self.declare_parameter("transient_velocity", 0.5)
        self.declare_parameter("front_car_velocity", 0.1)
        self.declare_parameter("zoh_period", 0.1)

        self.limo_1_vel = self.get_parameter("transient_velocity").get_parameter_value().double_value
        self.limo_2_vel = self.get_parameter("front_car_velocity").get_parameter_value().double_value
        self.zoh_period = self.get_parameter("zoh_period").get_parameter_value().double_value

        # Initialize
        self.limo_1_vel_msg = Twist()
        self.limo_2_vel_msg = Twist()

        # Publishers 
        self.limo_1_pub = self.create_publisher(Twist, '/limo_1/transient_vel', 10)
        self.limo_2_pub = self.create_publisher(Twist, '/limo_2/transient_vel', 10)

        # Timer
        self.create_timer(self.zoh_period, self.output_callback)

    def output_callback(self):
        self.limo_1_vel_msg.linear.x = self.limo_1_vel
        self.limo_2_vel_msg.linear.x = self.limo_2_vel
        self.limo_1_pub.publish(self.limo_1_vel_msg)
        self.limo_2_pub.publish(self.limo_2_vel_msg)
        

def main(args=None):
    rclpy.init(args=args)
    node = TransientControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()