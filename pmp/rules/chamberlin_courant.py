from itertools import combinations, product, chain
from operator import itemgetter
from scipy.special import lambertw

import numpy as np
from six import iteritems

from .._common import solve_methods_registry

from ..utils.ilp import *
from .rule import Rule

algorithm = solve_methods_registry()


class ChamberlinCourant(Rule):
    """Chamberlin-Courant vote scoring rule."""

    methods = algorithm.registry

    def __init__(self, weights=None):
        Rule.__init__(self)
        self.weights = weights
        self.scores = {}

    def __str__(self):
        return "Chamberlin-Courant"

    def initialise_weights(self, _k, profile):
        self.weights = self._borda_weights(len(profile.candidates))

    def find_committee(self, k, profile, method='ILP', random_winning_committee=False):
        self.scores = {}
        if self.weights is None:
            self.weights = self._borda_weights(len(profile.candidates))

        if method is None:
            committee = algorithm.registry.default(self, k, profile)
        else:
            committee = algorithm.registry.all[method](self, k, profile)
        return committee

    @algorithm('Bruteforce', 'Exponential.')
    def _brute(self, k, profile):
        self.scores = self.compute_scores(k, profile)
        return max(iteritems(self.scores), key=itemgetter(1))[0]

    @algorithm('ILP', default=True)
    def _ilp(self, k, profile):
        m = len(profile.candidates)
        n = len(profile.preferences)
        all_ij = np.fromiter(chain.from_iterable(product(range(m), range(n))), int, n * m * 2)
        all_ij.shape = n * m, 2

        model = Model()

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

        # Objective - alpha_j(i) * yij
        model.set_objective_sense(Objective.maximize)

        objective_iterable = (self.satisfaction(profile.preferences[j], profile.candidates[i]) for (i, j) in all_ij)
        yij_weights = np.fromiter(objective_iterable, int, n * m)
        model.set_objective(y, yij_weights)

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

        # End of definition

        model.solve()

        solution = model.get_solution()
        committee = (i for i in range(m) if abs(solution['x{}'.format(i)] - 1) <= 1e-05)

        self.scores[committee] = model.get_objective_value()
        return committee

    @algorithm('Approx_Greedy')
    def _greedy(self, k, profile):
        # satisfactions may be interpreted as follows: if we add candidate c to existing committee, its score will
        # increase by satisfactions[v][c] for each voter v. Initially, the committee is empty, so the array holds the
        # points assigned to each candidate by each voter.
        satisfactions = np.zeros((len(profile.preferences), profile.num_cand))
        for v, pref in enumerate(profile.preferences):
            for pos, c in enumerate(pref.order):
                satisfactions[v][c] = len(pref.order) - 1 - pos

        committee = []
        candidates = set(profile.candidates)

        while len(committee) < k:
            best_candidate = next(iter(candidates))
            best_income = 0

            for c in candidates:
                income = sum(satisfactions[:, c])
                if income > best_income:
                    best_candidate = c
                    best_income = income

            committee.append(best_candidate)
            candidates.remove(best_candidate)

            satisfactions -= satisfactions[:, best_candidate][:, np.newaxis]
            np.clip(satisfactions, 0, None, out=satisfactions)

        return committee

    @algorithm('Approx_P')
    def _p(self, k, profile):
        x = int(np.math.ceil(profile.num_cand * np.real(lambertw(k)) / k))
        top_x_candidates = [p.order[:x] for p in profile.preferences]

        unique, counts = np.unique(top_x_candidates, return_counts=True)
        counts = dict(zip(unique, counts))
        counts = [counts[i] if i in counts else 0 for i in range(profile.num_cand)]

        committee = []
        while len(committee) < k:
            best_candidate = np.argmax(counts)

            for i, v in enumerate(top_x_candidates):
                if best_candidate in v:
                    for c in v:
                        counts[c] -= 1
                    top_x_candidates[i] = []

            committee.append(best_candidate)

        return committee

    def compute_scores(self, k, profile):
        scores = {}
        all = list(combinations(profile.candidates, k))
        for comm in all:
            scores[comm] = self.committee_score(comm, profile)
        return scores

    def committee_score(self, committee, profile):
        if self.weights is None:
            self.weights = self._borda_weights(len(profile.candidates))

        score = 0
        for pref in profile.preferences:
            satisfaction = [self.satisfaction(pref, cand) for cand in committee]
            score += max(satisfaction)
        return score

    def satisfaction(self, pref, cand):
        i = pref.order.index(cand)
        return self.weights[i]

    @staticmethod
    def _borda_weights(size):
        weights = [size - i for i in range(1, size + 1)]
        return weights
