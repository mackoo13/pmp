from random import seed

from pmp.experiments.experiment import preference_orders, image_import_fail, visualize
from pmp.experiments.helpers import Command
from pmp.preferences import Profile
from pmp.rules import MultigoalCCBorda
from pmp.experiments import Experiment, save_to_file, FileType, helpers, impartial
import os


class MultigoalExperiment(Experiment):
    def __init__(self, conf=None):
        Experiment.__init__(self, conf)
        self.rule = MultigoalCCBorda
        self.thresholds = None
        self.__config = conf
        self.__generated_dir_path = "generated"

    def set_election(self, rule, k):
        raise Exception('In MultigoalExperiment')

    def set_multigoal_election(self, rule, thresholds, k):
        self.rule = rule
        self.thresholds = thresholds
        self.k = int(k)

    def run(self, visualization=False, n=1, save_win=False, save_in=False, save_out=False):
        dir_path = self.__generated_dir_path

        try:
            helpers.make_dirs(dir_path, exist_ok=True)
        except OSError as e:
            if not os.path.isdir(dir_path):
                raise e

        for i in range(n):
            candidates, voters, preferences = self.__execute_commands()
            if save_in:
                save_to_file(self, FileType.IN_FILE, i, candidates, voters)
            if save_out:
                save_to_file(self, FileType.OUT_FILE, i, candidates, voters, preferences)

            winners = self.__run_election(candidates, preferences)

            if save_win:
                save_to_file(self, FileType.WIN_FILE, i, candidates, voters, preferences, winners)

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

        return self.rule(self.thresholds).find_committee(self.k, profile, method='ILP')
