import numpy as np
from itertools import combinations
from pmp.rules.utils import get_best_score
from .._common import solve_methods_registry
from .tie_breaking import random_winner
from ..utils.ilp import *

algorithm = solve_methods_registry()


class MultigoalRule:
    def __init__(self, rules, tie_break=random_winner, log_errors=True):
        self.rules = rules
        self.tie_break = tie_break
        self.scores = {}
        self.log_errors = log_errors

    def __str__(self):
        return "MultigoalRule(" + ", ".join([rule.__str__() for rule in self.rules]) + ")"

    def find_committee(self, k, profile, method=None, k_cc=None, criterion='max_appr'):
        if method is None:
            committee = algorithm.registry.default(self, k, profile, criterion=criterion)
        else:
            committee = algorithm.registry.all[method](self, k, profile, criterion=criterion)
        return committee

    def compute_scores(self, k, profile):
        self.scores = {}
        all = list(combinations(profile.candidates, k))
        for comm in all:
            self.scores[comm] = self.committee_score(comm, profile)
        return self.scores

    def get_max_scores(self, k, profile):
        return [get_best_score(rule.rule, profile, k) for rule in self.rules]

    def committee_score(self, committee, profile):
        return np.array([rule.rule.committee_score(committee, profile) for rule in self.rules])

    @algorithm('Bruteforce', 'Exponential.')
    def _brute(self, k, profile, criterion='max_appr'):
        if criterion not in ('all', 'any', 'max_appr'):
            raise ValueError('Brute method suports the following criteria: \'all\', \'any\', \'max_appr\'')

        def get_worst_appr(c, max_scores):
            worst_appr = 1
            for rule1, max_score in zip(self.rules, max_scores):
                score = rule1.rule.committee_score(c, profile)
                worst_appr = min(worst_appr, score / float(max_score))
            return worst_appr

        self.compute_scores(k, profile)
        res = []
        for comm in self.scores:
            if all(self.scores[comm] >= [rule.s for rule in self.rules]):
                if criterion == 'any':
                    return comm
                else:
                    res.append(comm)

        if criterion == 'all':
            return res
        if criterion == 'max_appr':
            max_scores = self.get_max_scores(k, profile) if criterion == 'max_appr' else None
            return max(res, key=lambda c: get_worst_appr(c, max_scores))

    @algorithm('ILP')
    def _ilp_weakly_separable(self, k, profile, criterion='max_appr'):
        criterion_options = ['any', 'max_appr'] + ['rule' + str(i+1) for i in range(len(self.rules))]
        if criterion not in criterion_options:
            raise ValueError('ILP method supports the following criteria: ' + ', '.join(criterion_options))

        rule_to_maximize = int(criterion[4:]) - 1 if criterion.startswith('rule') else None

        max_scores = self.get_max_scores(k, profile) if criterion == 'max_appr' else [None] * len(self.rules)
        resolution = 100 if criterion == 'max_appr' else None

        # ILP
        m = len(profile.candidates)

        model = Model(log_errors=self.log_errors)

        # Xi - ith candidate is in committee
        x = ['x{}'.format(i) for i in range(m)]
        x_lb = np.zeros(m)
        x_ub = np.ones(m)
        model.add_variables(x, x_lb, x_ub)

        if criterion == 'max_appr':
            model.add_variable('a', 0, resolution)

        # Constraint1 - Vi Ei xi = k
        # K candidates are chosen
        xi = np.ones(m)
        model.add_constraint(x, xi, Sense.eq, k)

        # Constraint2 - thresholds
        for i_rule, (rule, max_score) in enumerate(zip(self.rules, max_scores)):
            profile.scores = {}
            rule.rule.initialise_weights(k, profile)
            rule.rule.compute_candidate_scores(k, profile)
            model.add_constraint(x, [profile.scores[i] for i in range(m)], Sense.gt, rule.s)

            if rule_to_maximize == i_rule:
                model.set_objective_sense(Objective.maximize)
                model.set_objective(x, [profile.scores[i] for i in range(m)])

            if criterion == 'max_appr':
                model.add_constraint(x + ['a'],
                                     [profile.scores[i] / float(max_score) * resolution for i in range(m)] + [-1],
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
