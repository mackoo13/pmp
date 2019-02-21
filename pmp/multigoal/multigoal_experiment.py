from random import seed
from cplex.exceptions import CplexSolverError
from pmp.experiments.experiment import preference_orders
from pmp.experiments.helpers import Command
from pmp.multigoal.helpers import get_profile
from pmp.rules import MultigoalCCBorda
from pmp.experiments import Experiment, multigoal_save_to_file, multigoal_save_scores, FileType, helpers, impartial, \
    urn, mallows
from pmp.rules.utils import get_best_score
import numpy as np
import os


class MultigoalExperiment(Experiment):
    def __init__(self, conf=None, dir_name='results'):
        Experiment.__init__(self, conf)
        self.rule = MultigoalCCBorda
        self.rule_instance = None
        self.thresholds = None
        self.percent_thresholds = None
        self.filename = None
        self.dir_name = dir_name
        self.__config = conf
        self.__generated_dir_path = "generated"

    def compute_best_scores(self, profile):
        return np.array([get_best_score(rule.rule, profile, self.k)
                         for rule in self.rule([0] * len(self.percent_thresholds)).rules])

    def refresh_filename(self):
        if self.percent_thresholds is not None:
            thresholds_str = '_'.join([str(t) for t in self.percent_thresholds])
        else:
            thresholds_str = '_'.join([str(t) for t in self.thresholds])

        candidates, voters, _ = self.__execute_commands()

        self.filename = '{}_{}_{}_k{}_n{}_m{}'.format(
            self.rule.__name__, self.__config.distribution_name, thresholds_str,
            self.k, len(voters), len(candidates))

    def set_election(self, rule, k):
        raise Exception('In MultigoalExperiment')

    def set_multigoal_election(self, rule, k, thresholds=None, percent_thresholds=None):
        self.rule = rule
        self.k = int(k)
        self.thresholds = thresholds
        self.percent_thresholds = percent_thresholds
        self.refresh_filename()
        self.set_generated_dir_path(os.path.join(self.dir_name, self.filename))

    def n_rules(self):
        if self.percent_thresholds is not None:
            return len(self.percent_thresholds)
        if self.thresholds is not None:
            return len(self.thresholds)

    def run(self, visualization=False, n=1, n_start=1, cplex_trials=1, methods=None, k_cc=None,
            save_win=True, save_in=True, save_out=True, save_best=True, save_score=True):
        dir_path = self.get_generated_dir_path()
        if methods is None:
            methods = ['ILP']

        try:
            helpers.make_dirs(dir_path, exist_ok=True)
        except OSError as e:
            if not os.path.isdir(dir_path):
                raise e

        i = 1
        cplex_failures = 0
        while i <= n * len(methods):

            i_per_method = (i-1) / len(methods) + n_start
            candidates, voters, preferences = self.__execute_commands()
            if save_in:
                multigoal_save_to_file(self, FileType.IN_FILE, i_per_method, candidates, voters)
            if save_out:
                multigoal_save_to_file(self, FileType.OUT_FILE, i_per_method, candidates, voters, preferences)

            for method in methods:
                filename = self.filename
                score_filename = '{}_{}_{}.score'.format(filename, method, i_per_method)
                score_filename = os.path.join(dir_path, score_filename)
                win_filename = '{}_{}_{}.win'.format(filename, method, i_per_method)
                win_filename = os.path.join(dir_path, win_filename)

                if os.path.isfile(score_filename) or os.path.isfile(win_filename):
                    print('Skipping: {} (already generated)'.format(filename))
                    i += 1
                    continue

                profile = get_profile(candidates, preferences)
                best_scores = self.compute_best_scores(profile)

                if self.percent_thresholds is not None:
                    self.thresholds = best_scores * np.array(self.percent_thresholds) / 100
                n_thresholds = len(self.thresholds)

                if save_best:
                    multigoal_save_scores(self, FileType.BEST_FILE, i_per_method, best_scores)

                try:
                    winners = list(self.__run_election(candidates, preferences, method=method, k_cc=k_cc))
                    i += 1
                    cplex_failures = 0
                except CplexSolverError as e:
                    if cplex_failures < cplex_trials:
                        print('No solution found by Cplex: retry')
                        cplex_failures += 1
                        continue
                    else:
                        print('No solution found by Cplex: trials limit exceeded')
                        raise e

                if save_win:
                    multigoal_save_to_file(
                        self, FileType.WIN_FILE, i_per_method, candidates, voters, preferences, winners, method=method)
                    print('Generated: {} ({})'.format(method, i_per_method))
                if save_score:
                    score = self.rule([0] * n_thresholds).committee_score(winners, profile)
                    multigoal_save_scores(self, FileType.SCORE_FILE, i_per_method, score, method=method)

    def __execute_commands(self):
        candidates = self.__config.get_candidates()
        voters = self.__config.get_voters()
        preferences = []

        for experiment_command in self.__config.get_commands():
            command_type = experiment_command[0]
            args = experiment_command[1]
            if command_type == Command.GEN_CANDIDATES:
                candidates += experiment_command[1]()
            elif command_type == Command.GEN_VOTERS:
                voters += experiment_command[1]()
            elif command_type == Command.GEN_FROM_CANDIDATES:
                _, voters, preferences = experiment_command[1](candidates)
            elif command_type == Command.IMPARTIAL:
                candidates, voters, preferences = impartial(*args)
            elif command_type == Command.URN:
                candidates, voters, preferences = urn(*args)
            elif command_type == Command.MALLOWS:
                candidates, voters, preferences = mallows(*args)
        if not preferences:
            preferences = preference_orders(candidates, voters)
        if any(isinstance(candidate, int) or len(candidate) != 3 for candidate in candidates):
            self.two_dimensional = False
        return candidates, voters, preferences

    # run election, compute winners
    def __run_election(self, candidates, preferences, method='ILP', k_cc=None):
        seed()

        profile = get_profile(candidates, preferences)
        if self.k > len(candidates):
            print("k is too big. Not enough candidates to find k winners.")
            return

        if k_cc is not None:
            return self.rule(self.thresholds).find_committee(self.k, profile, method=method, k_cc=k_cc)
        else:
            return self.rule(self.thresholds).find_committee(self.k, profile, method=method)
