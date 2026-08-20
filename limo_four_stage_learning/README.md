# LIMO four-stage learning experiment

This package runs one uninterrupted four-stage experiment starting directly
from the measured Gazebo state (normally 0.0 m/s): learn and exploit at
0.6 m/s, learn and exploit at 0.0 m/s, then reuse the two frozen policies
without exploration. The learner waits for filtered odometry before starting
its 80-second clock; it does not perform a velocity pre-roll.

Bring up `limo_gazebo` first, then run:

```bash
ros2 launch limo_four_stage_learning four_stage_experiment.launch.py
```

Do not run another node that publishes `/limo_1/cmd_vel` at the same time.
Record every experiment signal with:

```bash
ros2 bag record /limo_1/odometry/filtered /limo_1/cmd_vel \
  /limo_1/four_stage_vel /four_stage_actuation_filter/filtered_velocity \
  /four_stage_learning/control_input /four_stage_learning/velocity \
  /four_stage_learning/reference /four_stage_learning/error \
  /four_stage_learning/policy_control /four_stage_learning/exploration \
  /four_stage_learning/policy /four_stage_learning/theta \
  /four_stage_learning/learned_gradient /four_stage_learning/model_gradient \
  /four_stage_learning/gradient_rmse /four_stage_learning/stage \
  /four_stage_learning/phase /four_stage_learning/policy_updated \
  /four_stage_learning/elapsed /four_stage_learning/complete
```

The velocity/reference, control/policy/exploration, policy, theta,
Hamiltonian-gradient, and fixed-domain RMSE topics reproduce the notebook's
six figures. `theta.data` is `[P_hat, s_hat, c_hat, gamma1_hat, gamma0_hat]`;
`policy.data` is `[k_e, k_0]`.
