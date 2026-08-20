import numpy as np

from limo_four_stage_learning.core import FourStageLearner


def test_four_stages_freeze_and_reuse_policies():
    learner = FourStageLearner(
        dt=0.01, interval=0.02, policy_window=0.04,
        learning_duration=0.08, stage_duration=0.10,
    )
    samples = []
    velocity = 0.1
    for _ in range(learner.total_steps):
        sample = learner.step(velocity)
        samples.append(sample)
        velocity += learner.dt * (-2.0 * velocity + 2.4 * sample.control)

    assert [samples[i * learner.stage_steps].stage for i in range(4)] == [1, 2, 3, 4]
    assert all(sample.exploration == 0.0 for sample in samples[2 * learner.stage_steps:])
    stage3 = samples[2 * learner.stage_steps].policy
    stage4 = samples[3 * learner.stage_steps].policy
    assert np.allclose(stage3, learner.learned_policies[0.6])
    assert np.allclose(stage4, learner.learned_policies[0.1])


def test_completion_is_safe_zero_command():
    learner = FourStageLearner(
        dt=0.01, interval=0.02, policy_window=0.04,
        learning_duration=0.08, stage_duration=0.10,
    )
    for _ in range(learner.total_steps):
        learner.step(0.1)
    final = learner.step(0.1)
    assert final.complete
    assert final.control == 0.0
