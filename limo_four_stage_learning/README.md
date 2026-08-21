# LIMO four-stage learning experiment

This package runs one uninterrupted four-stage experiment starting directly
from the measured Gazebo state (normally 0.0 m/s): learn and exploit at
0.8 m/s, learn and exploit at 0.0 m/s, then reuse the two frozen policies
without exploration. The learner waits for velocity feedback before starting
its 160-second clock; it does not perform a velocity pre-roll. Learning is
active for the first 30 seconds of stages 1 and 2; the remaining 10 seconds
are pure exploitation.

Bring up `limo_gazebo` first, then run:

```bash
ros2 launch limo_four_stage_learning four_stage_experiment.launch.py
```

The command above preserves the successful Gazebo ground-truth experiment.
To test the estimator-backed path instead, run:

```bash
ros2 launch limo_four_stage_learning four_stage_ekf_experiment.launch.py
```

On a physical LIMO, use wall time:

```bash
ros2 launch limo_four_stage_learning four_stage_ekf_experiment.launch.py \
  use_sim_time:=false
```

If the robot bringup already provides an EKF configured to publish forward
velocity on `/limo_1/odometry/filtered`, add `start_ekf:=false` to avoid
starting a duplicate estimator.

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

Both the learner and PT1 filter use `/limo_1/ground_truth` by default. The
filter uses ground truth only to initialize its state, then advances the PT1
recursion internally at 100 Hz. This avoids weakening the excitation by
reusing Gazebo's 50 Hz feedback sample twice. The feedback topic remains
configurable through `velocity_topic`.

The separate EKF launch uses `ekf_feedback.yaml` to switch both nodes to
`/limo_1/odometry/filtered`. Its estimator configuration explicitly fuses
wheel-odometry `vx` and publishes at 100 Hz. Gazebo uses simulation time, so
160 seconds of experiment time may take longer than 160 wall-clock seconds when
the simulator real-time factor is below one; the physical-LIMO launch uses
wall time and therefore runs for approximately 160 real seconds.
