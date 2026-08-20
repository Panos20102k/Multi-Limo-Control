import numpy as np

from limo_single_stage_learning.core import SingleStageLearner


def test_notebook_schedule_and_frozen_exploitation():
    learner = SingleStageLearner()
    velocity = 0.0
    samples = []
    for _ in range(learner.total_steps):
        sample = learner.step(velocity)
        samples.append(sample)
        velocity += learner.dt * (-2.0 * velocity + 2.4 * sample.control)

    assert learner.total_steps == 2000
    assert samples[0].velocity == 0.0
    assert all(sample.reference == 0.6 for sample in samples)
    assert samples[1599].phase == 'learning'
    assert samples[1600].phase == 'exploitation'
    assert all(sample.exploration == 0.0 for sample in samples[1600:])
    frozen = samples[1600].policy
    assert all(np.allclose(sample.policy, frozen) for sample in samples[1600:])
    assert np.all(np.isfinite(samples[-1].theta))


def test_post_experiment_command_is_zero():
    learner = SingleStageLearner(
        dt=0.01, interval=0.02, policy_window=0.04,
        learning_duration=0.08, stage_duration=0.10,
    )
    for _ in range(learner.total_steps):
        learner.step(0.0)
    final = learner.step(0.0)
    assert final.complete
    assert final.control == 0.0
