"""PT1 plant-dynamics filter between learned input and LIMO velocity command."""

import math

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float64


class ActuationFilterNode(Node):
    def __init__(self):
        super().__init__('four_stage_actuation_filter')
        self.declare_parameter('zoh_period', 0.01)
        self.declare_parameter('pt1_time_constant', 0.5)
        self.declare_parameter('pt1_gain', 1.2)
        self.declare_parameter('minimum_velocity', -1.0)
        self.declare_parameter('maximum_velocity', 1.0)
        self.declare_parameter('command_timeout', 0.25)

        def p(name):
            return self.get_parameter(name).value
        self.period = p('zoh_period')
        self.alpha = math.exp(-self.period / p('pt1_time_constant'))
        self.gain = p('pt1_gain')
        self.minimum = p('minimum_velocity')
        self.maximum = p('maximum_velocity')
        self.timeout = p('command_timeout')
        self.velocity = 0.0
        self.control = 0.0
        self.have_odom = False
        self.last_command = None
        self.create_subscription(Odometry, '/limo_1/odometry/filtered', self._odom, 20)
        self.create_subscription(Float64, '/four_stage_learning/control_input', self._control, 20)
        self.command_pub = self.create_publisher(Twist, '/limo_1/four_stage_vel', 20)
        self.filtered_pub = self.create_publisher(Float64, '~/filtered_velocity', 20)
        self.create_timer(self.period, self._tick)

    def _odom(self, msg):
        self.velocity = msg.twist.twist.linear.x
        self.have_odom = True

    def _control(self, msg):
        self.control = msg.data
        self.last_command = self.get_clock().now()

    def _tick(self):
        if not self.have_odom:
            return
        stale = self.last_command is None
        if not stale:
            stale = (self.get_clock().now() - self.last_command).nanoseconds / 1e9 > self.timeout
        desired = 0.0 if stale else (
            self.alpha * self.velocity + self.gain * (1.0 - self.alpha) * self.control
        )
        desired = min(max(desired, self.minimum), self.maximum)
        msg = Twist()
        msg.linear.x = desired
        self.command_pub.publish(msg)
        self.filtered_pub.publish(Float64(data=desired))


def main(args=None):
    rclpy.init(args=args)
    node = ActuationFilterNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
