"""ROS-independent four-stage Hamiltonian-gradient learner."""

from dataclasses import dataclass
import math

import numpy as np


@dataclass(frozen=True)
class Sample:
    """All scalar signals produced by one controller step."""

    stage: int
    phase: str
    elapsed: float
    stage_elapsed: float
    velocity: float
    reference: float
    error: float
    control: float
    policy_control: float
    exploration: float
    policy: np.ndarray
    theta: np.ndarray
    learned_gradient: float
    model_gradient: float
    gradient_rmse: float
    policy_updated: bool
    complete: bool


class FourStageLearner:
    """Online RLS learner matching the four-stage notebook experiment."""

    def __init__(
        self, dt=0.01, interval=0.10, policy_window=3.0,
        learning_duration=30.0, stage_duration=40.0, q=2.0, r=0.5,
        rho=0.3, forgetting=1.0, covariance_scale=1e6,
        policy_blend=0.40, initial_slope=-0.60, initial_intercept=0.20,
        exploration_amplitude=0.18, exploration_decay=0.92,
        model_tau=0.5, model_gain=1.2, error_grid_min=-0.7,
        error_grid_max=0.4, error_grid_size=250,
    ):
        if dt <= 0.0 or interval < dt or policy_window < dt:
            raise ValueError("time parameters must be positive and ordered")
        if stage_duration <= learning_duration:
            raise ValueError("stage_duration must exceed learning_duration")
        self.dt = float(dt)
        self.interval_steps = max(1, int(round(interval / dt)))
        self.policy_steps = max(1, int(round(policy_window / dt)))
        self.learning_steps = int(round(learning_duration / dt))
        self.stage_steps = int(round(stage_duration / dt))
        self.q, self.r, self.rho = float(q), float(r), float(rho)
        self.forgetting = float(forgetting)
        self.covariance_scale = float(covariance_scale)
        self.policy_blend = float(policy_blend)
        self.initial_policy = np.array([initial_slope, initial_intercept], dtype=float)
        self.exploration_amplitude = float(exploration_amplitude)
        self.exploration_decay = float(exploration_decay)
        self.model_a = -1.0 / float(model_tau)
        self.model_b = float(model_gain) / float(model_tau)
        self.error_grid = np.linspace(error_grid_min, error_grid_max, error_grid_size)
        self.references = (0.8, 0.0, 0.8, 0.0)
        self.learn_stage = (True, True, False, False)
        self.total_steps = 4 * self.stage_steps
        self.exact = {ref: self._exact_solution(ref) for ref in set(self.references)}
        self.learned_policies = {}
        self.learned_critics = {}
        self.step_index = 0
        self.stage = -1
        self.policy = self.initial_policy.copy()
        self.theta = np.zeros(5)
        self.covariance = self.covariance_scale * np.eye(5)
        self.policy_index = 0
        self._reset_interval(0.0)

    def _exact_solution(self, reference):
        coefficients = [
            self.model_b ** 2 / self.r,
            -(2.0 * self.model_a - self.rho),
            -self.q,
        ]
        p_star = float(np.max(np.roots(coefficients)))
        d_ref = self.model_a * reference
        s_star = float(
            -p_star * d_ref /
            (self.model_a - self.rho - (self.model_b ** 2 / self.r) * p_star)
        )
        gamma1 = 2.0 * self.model_b * p_star
        gamma0 = 2.0 * self.model_b * s_star
        return np.array([p_star, s_star, gamma1, gamma0], dtype=float)

    def _reset_interval(self, error):
        self.interval_start_error = float(error)
        self.interval_cost = 0.0
        self.interval_e_du = 0.0
        self.interval_du = 0.0
        self.interval_sample = 0

    def _enter_stage(self, stage, error):
        if self.stage >= 0 and self.learn_stage[self.stage]:
            ref = self.references[self.stage]
            self.learned_policies[ref] = self.policy.copy()
            self.learned_critics[ref] = self.theta.copy()
        self.stage = stage
        if self.learn_stage[stage]:
            self.policy = self.initial_policy.copy()
            self.theta = np.zeros(5)
            self.covariance = self.covariance_scale * np.eye(5)
            self.policy_index = 0
        else:
            ref = self.references[stage]
            self.policy = self.learned_policies[ref].copy()
            self.theta = self.learned_critics[ref].copy()
        self._reset_interval(error)

    def _rls_update(self, end_error):
        discount = math.exp(-self.rho * self.interval_steps * self.dt)
        phi_start = np.array([
            self.interval_start_error ** 2,
            2.0 * self.interval_start_error,
            1.0,
        ])
        phi_end = np.array([end_error ** 2, 2.0 * end_error, 1.0])
        psi = np.concatenate((
            phi_start - discount * phi_end,
            np.array([self.interval_e_du, self.interval_du]),
        ))
        denominator = self.forgetting + psi @ self.covariance @ psi
        gain = self.covariance @ psi / denominator
        self.theta += gain * (self.interval_cost - psi @ self.theta)
        self.covariance = (
            self.covariance - np.outer(gain, psi) @ self.covariance
        ) / self.forgetting
        self._reset_interval(end_error)

    def step(self, velocity):
        """Advance using the newest measured velocity and return a control sample."""
        if self.step_index >= self.total_steps:
            return self._sample(float(velocity), 0.0, 0.0, False, True)
        stage = self.step_index // self.stage_steps
        local_step = self.step_index % self.stage_steps
        reference = self.references[stage]
        error = float(velocity) - reference
        if stage != self.stage:
            self._enter_stage(stage, error)

        learning = self.learn_stage[stage] and local_step < self.learning_steps
        policy_updated = False
        if learning and local_step > 0 and local_step % self.policy_steps == 0:
            proposed = np.array([
                -self.theta[3] / (2.0 * self.r),
                -self.theta[4] / (2.0 * self.r),
            ])
            proposed[0] = np.clip(proposed[0], -3.0, -0.05)
            proposed[1] = np.clip(proposed[1], -0.5, 1.0)
            self.policy = ((1.0 - self.policy_blend) * self.policy
                           + self.policy_blend * proposed)
            self.covariance = self.covariance_scale * np.eye(5)
            self.policy_index += 1
            policy_updated = True

        stage_time = local_step * self.dt
        exploration = 0.0
        if learning:
            amplitude = self.exploration_amplitude * self.exploration_decay ** self.policy_index
            exploration = amplitude * (
                math.sin(0.70 * stage_time)
                + 0.80 * math.sin(1.31 * stage_time + 0.30)
                + 0.60 * math.sin(2.17 * stage_time + 1.00)
                + 0.40 * math.sin(3.73 * stage_time + 0.70)
            )
        policy_control = float(self.policy @ np.array([error, 1.0]))
        control = policy_control + exploration

        if learning:
            # The current odometry sample is the end state of the preceding
            # interval; close that interval before accumulating this sample.
            if self.interval_sample >= self.interval_steps:
                self._rls_update(error)
            discount = math.exp(-self.rho * self.interval_sample * self.dt)
            self.interval_cost += discount * (
                self.q * error ** 2 + self.r * policy_control ** 2
            ) * self.dt
            self.interval_e_du += discount * error * exploration * self.dt
            self.interval_du += discount * exploration * self.dt
            self.interval_sample += 1

        sample = self._sample(
            float(velocity), control, exploration, policy_updated, False,
            policy_control=policy_control,
        )
        self.step_index += 1
        if self.step_index == self.total_steps:
            ref = self.references[self.stage]
            if self.learn_stage[self.stage]:
                self.learned_policies[ref] = self.policy.copy()
                self.learned_critics[ref] = self.theta.copy()
        return sample

    def _sample(self, velocity, control, exploration, policy_updated,
                complete, policy_control=0.0):
        stage = min(max(self.stage, 0), 3)
        reference = self.references[stage]
        error = velocity - reference
        exact = self.exact[reference]
        learned_gradient = 2.0 * self.r * control + self.theta[3] * error + self.theta[4]
        model_gradient = 2.0 * self.r * control + exact[2] * error + exact[3]
        difference = ((self.theta[3] - exact[2]) * self.error_grid
                      + self.theta[4] - exact[3])
        phase = "complete" if complete else (
            "learning" if self.learn_stage[stage]
            and self.step_index % self.stage_steps < self.learning_steps
            else "exploitation"
        )
        return Sample(
            stage=stage + 1, phase=phase, elapsed=self.step_index * self.dt,
            stage_elapsed=(self.step_index % self.stage_steps) * self.dt,
            velocity=velocity, reference=reference, error=error,
            control=control, policy_control=policy_control,
            exploration=exploration, policy=self.policy.copy(), theta=self.theta.copy(),
            learned_gradient=float(learned_gradient), model_gradient=float(model_gradient),
            gradient_rmse=float(np.sqrt(np.mean(difference ** 2))),
            policy_updated=policy_updated, complete=complete,
        )
