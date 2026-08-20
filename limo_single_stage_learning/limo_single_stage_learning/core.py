"""ROS-independent single-stage learner."""

from limo_four_stage_learning.core import FourStageLearner


class SingleStageLearner(FourStageLearner):
    """Notebook-equivalent 0.0 to 0.6 m/s learn/exploit experiment."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.references = (0.6,)
        self.learn_stage = (True,)
        self.total_steps = self.stage_steps
        self.stage = -1
        self.step_index = 0
        self.learned_policies = {}
        self.learned_critics = {}

    def _sample(self, velocity, control, exploration, policy_updated,
                complete, policy_control=0.0):
        # The shared implementation only uses the current reference and stage
        # schedule; both contain exactly one entry in this experiment.
        return super()._sample(
            velocity, control, exploration, policy_updated, complete,
            policy_control=policy_control,
        )
