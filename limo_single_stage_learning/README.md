# LIMO single-stage online learning

This package implements the experiment in
`fully_online_limo_hamiltonian_learning.ipynb`: start directly from the first
ground-truth LIMO velocity (normally 0.0 m/s), track 0.6 m/s, learn online for
16 seconds, and reuse the frozen policy without exploration for the remaining
4 seconds. There is no pre-roll or state reset.

After bringing up `limo_gazebo`, build and run:

```bash
colcon build --packages-select limo_four_stage_learning limo_single_stage_learning --symlink-install
source install/setup.bash
ros2 launch limo_single_stage_learning single_stage_experiment.launch.py
```

Do not run another controller or twist mux that publishes `/limo_1/cmd_vel`.

Record the complete plot dataset with:

```bash
ros2 bag record /limo_1/odometry/filtered /limo_1/cmd_vel \
  /limo_1/single_stage_vel /single_stage_actuation_filter/filtered_velocity \
  /single_stage_learning/control_input /single_stage_learning/velocity \
  /single_stage_learning/reference /single_stage_learning/error \
  /single_stage_learning/policy_control /single_stage_learning/exploration \
  /single_stage_learning/policy /single_stage_learning/theta \
  /single_stage_learning/learned_gradient /single_stage_learning/model_gradient \
  /single_stage_learning/gradient_rmse /single_stage_learning/phase \
  /single_stage_learning/policy_updated /single_stage_learning/elapsed \
  /single_stage_learning/complete
```

These topics reproduce all six notebook figures. `policy.data` is
`[k_e, k_0]`; `theta.data` is
`[P_hat, s_hat, c_hat, gamma1_hat, gamma0_hat]`.

The learner and PT1 filter use `/limo_1/ground_truth` by default. This is
intentional: the current EKF configuration does not fuse linear velocity into
`/limo_1/odometry/filtered`. The topic can be changed with the
`velocity_topic` parameter if the estimator configuration is later updated.
