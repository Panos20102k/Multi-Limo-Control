"""ROS 2 node for the fully online single-stage notebook experiment."""

import rclpy
from nav_msgs.msg import Odometry
from rclpy.node import Node
from std_msgs.msg import Bool, Float64, Float64MultiArray, String, UInt8

from .core import SingleStageLearner


class LearningNode(Node):
    def __init__(self):
        super().__init__('single_stage_learning')
        defaults = {
            'control_period': 0.01, 'rls_interval': 0.10,
            'policy_window': 3.0, 'learning_duration': 16.0,
            'experiment_duration': 20.0, 'reference_velocity': 0.6,
            'q': 2.0, 'r': 0.5, 'rho': 0.3, 'rls_forgetting': 1.0,
            'covariance_scale': 1e6, 'policy_blend': 0.40,
            'initial_policy_slope': -0.60,
            'initial_policy_intercept': 0.20,
            'exploration_amplitude': 0.18, 'exploration_decay': 0.92,
            'validation_model_tau': 0.5, 'validation_model_gain': 1.2,
            'wait_for_odometry': True,
            'velocity_topic': '/limo_1/ground_truth',
        }
        for name, value in defaults.items():
            self.declare_parameter(name, value)

        def p(name):
            return self.get_parameter(name).value

        reference = float(p('reference_velocity'))
        if reference != 0.6:
            raise ValueError('This notebook-equivalent experiment requires vref=0.6')
        self.learner = SingleStageLearner(
            dt=p('control_period'), interval=p('rls_interval'),
            policy_window=p('policy_window'),
            learning_duration=p('learning_duration'),
            stage_duration=p('experiment_duration'), q=p('q'), r=p('r'),
            rho=p('rho'), forgetting=p('rls_forgetting'),
            covariance_scale=p('covariance_scale'),
            policy_blend=p('policy_blend'),
            initial_slope=p('initial_policy_slope'),
            initial_intercept=p('initial_policy_intercept'),
            exploration_amplitude=p('exploration_amplitude'),
            exploration_decay=p('exploration_decay'),
            model_tau=p('validation_model_tau'),
            model_gain=p('validation_model_gain'),
        )
        self.wait_for_odometry = p('wait_for_odometry')
        self.velocity = 0.0
        self.have_odometry = False
        self.finished = False
        self.create_subscription(
            Odometry, p('velocity_topic'), self._odom, 20)
        self.command_pub = self.create_publisher(
            Float64, '~/control_input', 20)
        names = (
            'velocity', 'reference', 'error', 'policy_control', 'exploration',
            'learned_gradient', 'model_gradient', 'gradient_rmse', 'elapsed',
        )
        self.scalar_pubs = {
            name: self.create_publisher(Float64, '~/' + name, 20)
            for name in names
        }
        self.policy_pub = self.create_publisher(
            Float64MultiArray, '~/policy', 20)
        self.theta_pub = self.create_publisher(
            Float64MultiArray, '~/theta', 20)
        self.stage_pub = self.create_publisher(UInt8, '~/stage', 20)
        self.phase_pub = self.create_publisher(String, '~/phase', 20)
        self.update_pub = self.create_publisher(
            Bool, '~/policy_updated', 20)
        self.complete_pub = self.create_publisher(Bool, '~/complete', 1)
        self.create_timer(p('control_period'), self._tick)
        self.get_logger().info(
            'Waiting for ground-truth velocity; experiment starts from the measured state')

    def _odom(self, msg):
        self.velocity = msg.twist.twist.linear.x
        self.have_odometry = True

    @staticmethod
    def _float(value):
        return Float64(data=float(value))

    def _tick(self):
        if self.finished or (self.wait_for_odometry and not self.have_odometry):
            return
        sample = self.learner.step(self.velocity)
        self.command_pub.publish(self._float(sample.control))
        values = {
            'velocity': sample.velocity, 'reference': sample.reference,
            'error': sample.error, 'policy_control': sample.policy_control,
            'exploration': sample.exploration,
            'learned_gradient': sample.learned_gradient,
            'model_gradient': sample.model_gradient,
            'gradient_rmse': sample.gradient_rmse, 'elapsed': sample.elapsed,
        }
        for name, value in values.items():
            self.scalar_pubs[name].publish(self._float(value))
        self.policy_pub.publish(Float64MultiArray(data=sample.policy.tolist()))
        self.theta_pub.publish(Float64MultiArray(data=sample.theta.tolist()))
        self.stage_pub.publish(UInt8(data=1))
        self.phase_pub.publish(String(data=sample.phase))
        self.update_pub.publish(Bool(data=sample.policy_updated))
        if self.learner.step_index >= self.learner.total_steps:
            self.command_pub.publish(self._float(0.0))
            self.complete_pub.publish(Bool(data=True))
            self.finished = True
            self.get_logger().info(
                'Single-stage experiment complete; zero command published')


def main(args=None):
    rclpy.init(args=args)
    node = LearningNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
