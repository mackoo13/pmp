from random import seed

import numpy as np
from cplex.exceptions import CplexSolverError

from pmp.experiments.experiment import preference_orders
from pmp.experiments.helpers import Command
from pmp.preferences import Profile
from pmp.rules import MultigoalCCBorda
from pmp.experiments import Experiment, multigoal_save_to_file, multigoal_save_scores, FileType, helpers, impartial
import os

from pmp.rules.utils import get_best_score


class MultigoalExperiment(Experiment):
    def __init__(self, conf=None):
        Experiment.__init__(self, conf)
        self.rule = MultigoalCCBorda
        self.thresholds = None
        self.percent_thresholds = None
        self.__config = conf
        self.__generated_dir_path = "generated"

    def compute_best_scores(self, profile):
        rule = self.rule([None, None])  # todo
        return np.array([get_best_score(rule.rule, profile, self.k) for rule in rule.rules])

    def get_filename(self):
        thresholds_str = '_'.join([str(t) for t in self.percent_thresholds])    # todo tres
        return '{}_{}_{}_k{}_n{}_m{}'.format(
            self.rule.__name__, self.__config.distribution_name, thresholds_str,
            self.k, len(self.__config.get_voters()), len(self.__config.get_candidates()))

    def set_election(self, rule, k):
        raise Exception('In MultigoalExperiment')

    def set_multigoal_election(self, rule, k, thresholds=None, percent_thresholds=None):
        self.rule = rule
        self.k = int(k)
        self.thresholds = thresholds
        self.percent_thresholds = percent_thresholds
        self.filename = self.get_filename()
        self.set_generated_dir_path(self.filename)

    def run(self, visualization=False, n=1, method='ILP',
            save_win=True, save_in=True, save_out=True, save_best=True, save_score=True):
        dir_path = self.get_generated_dir_path()

        try:
            helpers.make_dirs(dir_path, exist_ok=True)
        except OSError as e:
            if not os.path.isdir(dir_path):
                raise e

        for i in range(n):
            candidates, voters, preferences = self.__execute_commands()
            if save_in:
                multigoal_save_to_file(self, FileType.IN_FILE, i, candidates, voters)
            if save_out:
                multigoal_save_to_file(self, FileType.OUT_FILE, i, candidates, voters, preferences)

            candidates_list = list(range(len(candidates)))
            profile = Profile(candidates_list, preferences)
            best_scores = self.compute_best_scores(profile)

            if self.percent_thresholds is not None:
                self.thresholds = best_scores * np.array(self.percent_thresholds) / 100

            if save_best:
                multigoal_save_scores(self, FileType.BEST_FILE, i, best_scores)

            winners = self.__run_election(candidates, preferences)

            if save_win:
                multigoal_save_to_file(self, FileType.WIN_FILE, i, candidates, voters, preferences, winners, method)
            if save_score:
                score = self.rule([None, None]).committee_score(list(winners), profile)   # todo
                multigoal_save_scores(self, FileType.SCORE_FILE, i, score, method=method)

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
        if not preferences:
            preferences = preference_orders(candidates, voters)
        if any(isinstance(candidate, int) or len(candidate) != 3 for candidate in candidates ):
            self.two_dimensional = False
        return candidates, voters, preferences

    # run election, compute winners
    def __run_election(self, candidates, preferences):
        seed()

        candidates_list = list(range(len(candidates)))
        profile = Profile(candidates_list, preferences)
        if self.k > len(candidates):
            print("k is too big. Not enough candidates to find k winners.")
            return

        MAX_TRIALS = 9
        for i in range(MAX_TRIALS):
            try:
                return self.rule(self.thresholds).find_committee(self.k, profile, method='ILP')
            except CplexSolverError:
                continue
