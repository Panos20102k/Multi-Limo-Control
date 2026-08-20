"""PT1 filter implementing the notebook plant dynamics on the LIMO."""

import math

import rclpy
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Float64


class ActuationFilterNode(Node):
    def __init__(self):
        super().__init__('single_stage_actuation_filter')
        self.declare_parameter('zoh_period', 0.01)
        self.declare_parameter('pt1_time_constant', 0.5)
        self.declare_parameter('pt1_gain', 1.2)
        self.declare_parameter('minimum_velocity', -1.0)
        self.declare_parameter('maximum_velocity', 1.0)
        self.declare_parameter('command_timeout', 0.25)
        self.declare_parameter('velocity_topic', '/limo_1/ground_truth')

        def p(name):
            return self.get_parameter(name).value

        self.period = p('zoh_period')
        self.alpha = math.exp(-self.period / p('pt1_time_constant'))
        self.gain = p('pt1_gain')
        self.minimum = p('minimum_velocity')
        self.maximum = p('maximum_velocity')
        self.timeout = p('command_timeout')
        self.filter_state = 0.0
        self.control = 0.0
        self.initialized = False
        self.last_command = None
        self.create_subscription(
            Odometry, p('velocity_topic'), self._odom, 20)
        self.create_subscription(
            Float64, '/single_stage_learning/control_input', self._control, 20)
        self.command_pub = self.create_publisher(
            Twist, '/limo_1/single_stage_vel', 20)
        self.filtered_pub = self.create_publisher(
            Float64, '~/filtered_velocity', 20)
        self.create_timer(self.period, self._tick)

    def _odom(self, msg):
        # Ground truth initializes the simulated plant state. After that, the
        # PT1 recursion advances at its own rate rather than reusing 50 Hz
        # odometry samples in a 100 Hz timer.
        if not self.initialized:
            self.filter_state = msg.twist.twist.linear.x
            self.initialized = True

    def _control(self, msg):
        self.control = msg.data
        self.last_command = self.get_clock().now()

    def _tick(self):
        if not self.initialized:
            return
        stale = self.last_command is None
        if not stale:
            age = (self.get_clock().now() - self.last_command).nanoseconds / 1e9
            stale = age > self.timeout
        effective_control = 0.0 if stale else self.control
        self.filter_state = (
            self.alpha * self.filter_state
            + self.gain * (1.0 - self.alpha) * effective_control
        )
        self.filter_state = min(
            max(self.filter_state, self.minimum), self.maximum)
        command = Twist()
        command.linear.x = self.filter_state
        self.command_pub.publish(command)
        self.filtered_pub.publish(Float64(data=self.filter_state))


def main(args=None):
    rclpy.init(args=args)
    node = ActuationFilterNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
