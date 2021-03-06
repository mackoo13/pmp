from pmp.rules import SNTV, Borda
from .._common import solve_methods_registry
from .threshold_rule import ThresholdRule
from .multigoal_rule import MultigoalRule

algorithm = solve_methods_registry()


class MultigoalBordaSNTV(MultigoalRule):
    methods = algorithm.registry

    def __init__(self, (s1, s2)=(0, 0), weights=None, log_errors=True):
        MultigoalRule.__init__(self,
                               [ThresholdRule(Borda(), s1),
                                ThresholdRule(SNTV(), s2)],
                               log_errors=log_errors)
        self.weights = weights

    def find_committee(self, k, profile, method=None, k_cc=None, criterion='max_appr'):
        if method is None:
            committee = algorithm.registry.default(self, k, profile, criterion=criterion)
        else:
            committee = algorithm.registry.all[method](self, k, profile, criterion=criterion)
        return committee

    @algorithm('Bruteforce', 'Exponential.')
    def _brute_bloc_borda(self, k, profile, criterion='max_appr'):
        return self._brute(k, profile, criterion=criterion)

    @algorithm('ILP', default=True)
    def _ilp(self, k, profile, criterion='max_appr'):
        return self._ilp_weakly_separable(k, profile, criterion=criterion)
