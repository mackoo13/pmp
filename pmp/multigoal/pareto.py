import os
import re
import matplotlib.pyplot as plt
import numpy as np
from cplex.exceptions import CplexSolverError
from pmp.experiments.experiment import preference_orders
from pmp.multigoal import MultigoalExperiment
from pmp.multigoal.helpers import get_distribution_name, read_scores
from pmp.preferences import Profile


def get_profile(voters, candidates):
    preferences = preference_orders(candidates, voters)
    candidates = list(range(len(candidates)))
    return Profile(candidates, preferences)


def plot(current_dir, x, y, mins, rules, title=""):
    rule1_name = rules[0].__str__()
    rule2_name = rules[1].__str__()

    axes = plt.gca()
    axes.set_xlim([0, 100])
    plt.xlabel(rule2_name)
    axes.set_ylim([0, y[0]])
    plt.ylabel(rule1_name)
    plt.plot(x, y)
    plt.plot(x, mins)
    plt.title(title)
    plt.legend(['avg', 'min'])

    plt.savefig(current_dir)
    plt.clf()


def get_multigoal_rules(multigoal_rule):
    return [threshold_rule.rule for threshold_rule in multigoal_rule().rules]


def draw_pareto_chart_from_winner_files(current_dir, m, n, k, multigoal_rule, distribution):
    print("{}, k={}".format(multigoal_rule.__name__, k))
    # We assume that there are "repetitions" files generated for each threshold.
    rule_name = multigoal_rule.__name__
    distribution_name = get_distribution_name(distribution)
    rules = get_multigoal_rules(multigoal_rule)
    if not rules:
        return

    # y_samples = np.zeros((len(x), repetitions))

    for dir_name in os.listdir(current_dir):
        dir_pattern = '{}_{}_(\d+)_(\d+)_k{}_n{}_m{}'.format(rule_name, distribution_name, k, n, m)
        r1_r2_match = re.match(dir_pattern, dir_name)
        if r1_r2_match is None:
            continue
        r1 = r1_r2_match.group(1)

        for filename in os.listdir(os.path.join(current_dir, dir_name)):
            win_pattern = '{}_ILP_(\d+).score'.format(dir_name)
            rm = re.match(win_pattern, filename)

            if not rm:
                continue

            r  =rm.group(1)
            win_filename = os.path.join(current_dir, dir_name, filename)
            bf='{}_{}.best'.format(dir_name,r)
            bf=os.path.join(current_dir, dir_name, bf)

            scores = read_scores(win_filename)
            best = read_scores(bf)

            approx2 = scores[1] / best[1]
            print(r1, approx2)

    # title = "voters: {}, candidates: {}, committee size: {}".format(n, m, k)
    # plot(current_dir, x, np.mean(y_samples, axis=0), np.min(y_samples, axis=0), rules, title=title)


def generate_winner_files_for_pareto(config, multigoal_rule, k, repetitions, start=70, step=2):
    rules = get_multigoal_rules(multigoal_rule)
    if not rules:
        return

    x = np.array([a for a in range(start, 101, step)])

    for i, r1 in enumerate(x):
        repetition = 1
        while repetition <= repetitions:
            experiment = MultigoalExperiment(config)

            for r2 in range(100, 0, -step):
                experiment.set_multigoal_election(multigoal_rule, k, percent_thresholds=(r1, r2))

                try:
                    experiment.run(n=1, n_start=repetition,
                                   save_in=False, save_out=False, save_win=True, save_best=True, save_score=True)
                    repetition += 1
                    break
                except CplexSolverError:
                    continue
