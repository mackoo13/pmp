from scipy.special import lambertw
from .._common import solve_methods_registry
from itertools import chain, product
import numpy as np

from .threshold_rule import ThresholdRule
from .multigoal_rule import MultigoalRule
from .chamberlin_courant import ChamberlinCourant
from .borda import Borda
from ..utils.ilp import *

algorithm = solve_methods_registry()


class MultigoalCCBorda(MultigoalRule):

    methods = algorithm.registry

    def __init__(self, (s1, s2), weights=None, log_errors=True):
        MultigoalRule.__init__(self,
                               [ThresholdRule(ChamberlinCourant(), s1),
                                ThresholdRule(Borda(), s2)],
                               log_errors=log_errors)
        self.weights = weights

    def find_committees(self, k, profile, method=None):
        if method is None:
            committee = algorithm.registry.default(self, k, profile)
        else:
            committee = algorithm.registry.all[method](self, k, profile)
        return committee

    @algorithm('Bruteforce', 'Exponential.')
    def _brute_cc_kb(self, k, profile):
        return self._brute(k, profile)

    @algorithm('ILP', default=True)
    def _ilp(self, k, profile):
        self.rules[0].rule.initialise_weights(k, profile)
        self.rules[1].rule.initialise_weights(k, profile)
        self.rules[1].rule.compute_candidate_scores(k, profile)

        # ILP
        m = len(profile.candidates)
        n = len(profile.preferences)
        all_ij = np.fromiter(chain.from_iterable(product(range(m), range(n))), int, n * m * 2)
        all_ij.shape = n * m, 2

        model = Model(log_errors=self.log_errors)

        # Xi - ith candidate is in committee
        x = ['x{}'.format(i) for i in range(m)]
        x_lb = np.zeros(m)
        x_ub = np.ones(m)
        model.add_variables(x, x_lb, x_ub)

        # Yij - ith candidate represents jth voter
        y = ['y{}_{}'.format(i, j) for (i, j) in all_ij]
        y_lb = np.zeros(n * m)
        y_ub = np.ones(n * m)
        model.add_variables(y, y_lb, y_ub)

        # Constraint1 - Vi Ei xi = k
        # K candidates are chosen
        xi = np.ones(m)
        model.add_constraint(x, xi, Sense.eq, k)

        # Constraint2 - Vi Ej yij = 1
        # Each voter is represented by one candidate
        c2_variables = [['y{}_{}'.format(i, j) for i in range(m)] for j in range(n)]
        c2_coefficients = np.ones((n, m))
        c2_senses = np.full(n, Sense.eq)
        c2_rights = np.ones(n)
        model.add_constraints(c2_variables, c2_coefficients, c2_senses, c2_rights)

        # Constraint3 - Vji yij <= xi
        # Candidate represent voter only if is chosen
        c3_variables = [['y{}_{}'.format(i, j), 'x{}'.format(i)] for (i, j) in all_ij]
        c3_coefficients = np.tile(np.array((1, -1)), n * m)
        c3_coefficients.shape = n * m, 2
        c3_senses = np.full(n * m, Sense.lt)
        c3_rights = np.zeros(n * m)
        model.add_constraints(c3_variables, c3_coefficients, c3_senses, c3_rights)

        # Constraint4 - CC
        objective_iterable = (self.rules[0].rule.satisfaction(profile.preferences[j], profile.candidates[i]) for (i, j) in
                              all_ij)
        yij_weights = np.fromiter(objective_iterable, int, n * m)
        model.add_constraint(y, yij_weights, Sense.gt, self.rules[0].s)

        # Constraint5 - kBorda
        model.add_constraint(x, [profile.scores[i] for i in range(m)], Sense.gt, self.rules[1].s)

        # End of definition

        model.solve()

        solution = model.get_solution()
        committee = (i for i in range(m) if abs(solution['x{}'.format(i)] - 1) <= 1e-05)

        return committee

    @algorithm('Approx_Greedy')
    def _greedy(self, k, profile):
        satisfactions = np.zeros((len(profile.preferences), profile.num_cand))
        for v, pref in enumerate(profile.preferences):
            for score, c in enumerate(pref.order):
                satisfactions[v][c] = len(pref.order) - 1 - score

        committee = set()
        candidates = set(profile.candidates)

        while len(committee) < k:
            best_candidate = None
            best_income = 0

            for c in candidates:
                income = sum(satisfactions[:, c])
                if income > best_income:
                    best_candidate = c
                    best_income = income

            committee.add(best_candidate)
            candidates.remove(best_candidate)

            satisfactions -= satisfactions[:, best_candidate][:, np.newaxis]
            np.clip(satisfactions, 0, None, out=satisfactions)

        return [committee]

    @algorithm('Approx_P')
    def _p(self, k, profile):
        x = int(np.math.ceil(profile.num_cand * lambertw(k) / k))
        top_candidates = [p.order[:x] for p in profile.preferences]
        unique, counts = np.unique(top_candidates, return_counts=True)
        counts = dict(zip(unique, counts))
        counts = [counts[i] if i in counts else 0 for i in range(profile.num_cand)]

        committee = set()

        while len(committee) < k:
            best_candidate = np.argmax(counts)

            for i, v in enumerate(top_candidates):
                if best_candidate in v:
                    for c in v:
                        counts[c] -= 1
                    top_candidates[i] = []

            committee.add(best_candidate)

        return [committee]
