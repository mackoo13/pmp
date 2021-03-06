import os
import re
import matplotlib

from pmp.multigoal.visualize import draw_histogram

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pmp.multigoal import MultigoalExperiment
from pmp.multigoal.helpers import get_distribution_name, read_scores


def plot(filename, x, mins, rules, title=""):
    rule1_name = rules[0].__str__()
    rule2_name = rules[1].__str__()

    axes = plt.gca()
    axes.set_xlim([0, 1])
    plt.xlabel(rule2_name)
    axes.set_ylim([0, 1])
    plt.ylabel(rule1_name)
    plt.plot(np.array(x).astype('float')/100, mins)
    plt.title(title)
    plt.legend(['min'])

    plt.savefig(filename)
    plt.clf()


def get_multigoal_rules(multigoal_rule):
    return [threshold_rule.rule for threshold_rule in multigoal_rule().rules]


def get_repetition_from_filename(dir_name, filename):
    filename_pattern = '{}_ILP_(\d+).score'.format(dir_name)
    rep_match = re.match(filename_pattern, filename)

    if not rep_match:
        return None
    else:
        return int(rep_match.group(1))


def count_already_generated(current_dir):
    max_rep = 0
    if os.path.isdir(current_dir):
        for dir_name in os.listdir(current_dir):
            dir_path = os.path.join(current_dir, dir_name)
            if not os.path.isdir(dir_path):
                continue

            for filename in os.listdir(os.path.join(current_dir, dir_name)):
                rep = get_repetition_from_filename(dir_name, filename)
                max_rep = max(max_rep, rep)
    return max_rep


def draw_pareto_chart_from_winner_files(current_dir, m, n, k, multigoal_rule, distribution, distribution_params=None):
    print("{}, k={}".format(multigoal_rule.__name__, k))
    # We assume that there are "repetitions" files generated for each threshold.
    rule_name = multigoal_rule.__name__
    distribution_name = get_distribution_name(distribution)
    rules = get_multigoal_rules(multigoal_rule)
    if not rules:
        return

    xy = {}

    for dir_name in os.listdir(current_dir):
        dir_pattern = '{}_{}_(\d+)_\d+_k{}_n{}_m{}'.format(rule_name, distribution_name, k, n, m)
        r1_match = re.match(dir_pattern, dir_name)
        if r1_match is None:
            continue
        r1 = r1_match.group(1)

        for filename in os.listdir(os.path.join(current_dir, dir_name)):
            rep = get_repetition_from_filename(dir_name, filename)
            if not rep:
                continue

            win_filename = os.path.join(current_dir, dir_name, filename)
            best_filename = '{}_{}.best'.format(dir_name, rep)
            best_filename = os.path.join(current_dir, dir_name, best_filename)

            scores = read_scores(win_filename)
            best = read_scores(best_filename)

            approx = scores[1] / best[1]
            if r1 in xy:
                xy[r1].append(approx)
            else:
                xy[r1] = [approx]

    xy_list = list(xy.items())
    xy_list = sorted(xy_list, key=lambda e: int(e[0]))
    x = [int(x) for x, _ in xy_list]
    y_min = [np.min(ys) for _, ys in xy_list]

    if distribution_params is None:
        filename = '{}_{}_k{}_n{}_m{}'.format(rule_name, distribution_name, k, n, m)
    else:
        distribution_params_string = '_'.join([dpk + str(dpv) for dpk, dpv in distribution_params.items()])
        distribution_params_string = distribution_params_string.replace('.', '')
        filename = '{}_{}_{}_k{}_n{}_m{}'.format(rule_name, distribution_name, distribution_params_string, k, n, m)

    title = "voters: {}, candidates: {}, committee size: {}".format(n, m, k)
    plot(filename, x, y_min, rules, title=title)


def draw_transition_from_winner_files(current_dir, m, n, k, multigoal_rule, distribution, repetitions):
    print("{}, k={}".format(multigoal_rule.__name__, k))
    # We assume that there are "repetitions" files generated for each threshold.
    rule_name = multigoal_rule.__name__
    distribution_name = get_distribution_name(distribution)
    rules = get_multigoal_rules(multigoal_rule)
    if not rules:
        return

    for dir_name in os.listdir(current_dir):
        dir_path = os.path.join(current_dir, dir_name)
        if not os.path.isdir(dir_path):
            continue

        dir_pattern = '{}_{}_(\d+)_(\d+)_k{}_n{}_m{}'.format(rule_name, distribution_name, k, n, m)
        r1_r2_match = re.match(dir_pattern, dir_name)
        if r1_r2_match is None:
            continue

        percentages = r1_r2_match.group(1), r1_r2_match.group(2)

        draw_histogram(dir_path, multigoal_rule, k, percentages, distribution, repetitions, n, m, 'ILP')


def generate_winner_files_for_pareto(dir_name, configs, multigoal_rule, k, start=70, step=2, save_win=False):
    n_start = count_already_generated(dir_name)

    rules = get_multigoal_rules(multigoal_rule)
    if not rules:
        return

    x = np.array([a for a in range(start, 101, step)])

    for repetition, config in enumerate(configs[n_start:]):
        experiment = MultigoalExperiment(config, dir_name=dir_name)

        for i, r1 in enumerate(x):
            experiment.set_multigoal_election(multigoal_rule, k, percent_thresholds=(r1, 0))

            experiment.run(n=1, n_start=n_start + repetition + 1, criterion='rule2',
                           save_in=False, save_out=False, save_win=save_win, save_best=True, save_score=True)
