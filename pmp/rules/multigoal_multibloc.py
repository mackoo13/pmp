from pmp.rules.tbloc import TBloc
from .._common import solve_methods_registry

from .threshold_rule import ThresholdRule
from .multigoal_rule import MultigoalRule

algorithm = solve_methods_registry()


class MultigoalTBloc(MultigoalRule):
    """Multi-Bloc Voting Rule."""

    methods = algorithm.registry

    def __init__(self, thresholds, weights=None, log_errors=True):
        MultigoalRule.__init__(self,
                               [ThresholdRule(TBloc(i + 1), t) for i, t in enumerate(thresholds)],
                               log_errors=log_errors)
        self.weights = weights
