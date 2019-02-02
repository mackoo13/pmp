from pmp.experiments import ExperimentConfig


class MultigoalExperimentConfig(ExperimentConfig):
    def __init__(self):
        ExperimentConfig.__init__(self)
        self.distribution_name = None

    def set_distribution_name(self, name):
        self.distribution_name = name
