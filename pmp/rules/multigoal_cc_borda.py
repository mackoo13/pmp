from __future__ import division
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

    def __init__(self, (s1, s2)=(0, 0), weights=None, log_errors=True):
        MultigoalRule.__init__(self,
                               [ThresholdRule(ChamberlinCourant(), s1),
                                ThresholdRule(Borda(), s2)],
                               log_errors=log_errors)
        self.weights = weights

    def find_committee(self, k, profile, method=None, k_cc=None, criterion='max_appr'):
        if method is None:
            committee = algorithm.registry.default(self, k, profile, k_cc=k_cc, criterion=criterion)
        else:
            committee = algorithm.registry.all[method](self, k, profile, k_cc=k_cc, criterion=criterion)
        return committee

    @algorithm('Bruteforce', 'Exponential.')
    def _brute_cc_kb(self, k, profile, k_cc=None, criterion='max_appr'):
        return self._brute(k, profile, criterion=criterion)

    @algorithm('ILP', default=True)
    def _ilp_cc_kb(self, k, profile, k_cc=None, criterion='max_appr'):
        if criterion not in ('any', 'max_appr'):
            raise ValueError('ILP method supports the following criteria: \'any\', \'max_appr\'')

        self.rules[0].rule.initialise_weights(k, profile)
        self.rules[1].rule.initialise_weights(k, profile)
        self.rules[1].rule.compute_candidate_scores(k, profile)

        max_scores = self.get_max_scores(k, profile) if criterion == 'max_appr' else []
        resolution = 100 if criterion == 'max_appr' else None

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

        # A - estimation of worst approximation
        if criterion == 'max_appr':
            model.add_variable('a', 0, resolution)

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
        objective_iterable = (self.rules[0].rule.satisfaction(profile.preferences[j], profile.candidates[i]) for (i, j)
                              in all_ij)
        yij_weights = np.fromiter(objective_iterable, int, n * m)
        model.add_constraint(y, yij_weights, Sense.gt, self.rules[0].s)

        # Constraint5 - CC approximation estimation
        if criterion == 'max_appr':
            model.add_constraint(y + ['a'],
                                 list(yij_weights / float(max_scores[0]) * resolution) + [-1],
                                 Sense.gt, 0)

        # Constraint6 - kBorda
        model.add_constraint(x, [profile.scores[i] for i in range(m)], Sense.gt, self.rules[1].s)

        # Constraint7 - CC approximation estimation
        if criterion == 'max_appr':
            model.add_constraint(x + ['a'],
                                 [profile.scores[i] / float(max_scores[1]) * resolution for i in range(m)] + [-1],
                                 Sense.gt, 0)

        # Maximise the worst approximation
        if criterion == 'max_appr':
            model.set_objective_sense(Objective.maximize)
            model.set_objective(['a'], [1])

        # End of definition

        model.solve()

        solution = model.get_solution()
        committee = (i for i in range(m) if abs(solution['x{}'.format(i)] - 1) <= 1e-05)

        return committee

    @algorithm('Approx_Greedy')
    def _greedy(self, k, profile, k_cc=None, criterion='max_appr'):
        if k_cc is None:
            l_cc = np.real(lambertw(1))
            k_cc = int(np.ceil(l_cc * k))

        # print('Greedy: selecting {} candidates with CC Greedy and {} candidates with Borda'.format(k_cc, k - k_cc))

        committee = set(self.rules[0].rule.find_committee(k_cc, profile, method='Approx_Greedy'))

        self.rules[1].rule.initialise_weights(k, profile)
        self.rules[1].rule.compute_candidate_scores(k, profile)

        for cand in sorted(profile.scores, key=lambda c: profile.scores.get(c), reverse=True):
            committee.add(cand)
            if len(committee) == k:
                return committee

    @algorithm('Approx_P')
    def _p(self, k, profile, k_cc=None, criterion='max_appr'):
        if k_cc is None:
            x = int(np.math.ceil(profile.num_cand * np.real(lambertw(k)) / k))
            A = 1 - (np.real(lambertw(k))) / k
            M = 1 - (profile.num_cand - x) / (profile.num_cand - 1)
            C = np.log(A) * k * (M - 1) * np.power(A, k * M)
            l_cc = M - np.real(lambertw(C)) / (np.log(A) * k)
            k_cc = int(np.ceil(l_cc * k))

        # print('P: selecting {} candidates with CC Alg-P and {} candidates with Borda'.format(k_cc, k - k_cc))

        committee = self.rules[0].rule.find_committee(k, profile, method='Approx_P')
        committee = set(committee[:k_cc])

        self.rules[1].rule.initialise_weights(k, profile)
        self.rules[1].rule.compute_candidate_scores(k, profile)

        if len(committee) == k:
            return committee

        for cand in sorted(profile.scores, key=lambda c: profile.scores.get(c), reverse=True):
            committee.add(cand)
            if len(committee) == k:
                return committee
