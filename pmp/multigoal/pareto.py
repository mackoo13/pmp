import os
import re
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
from cplex.exceptions import CplexSolverError
from pmp.multigoal import MultigoalExperiment
from pmp.multigoal.helpers import get_distribution_name, read_scores


def plot(filename, x, y, mins, rules, title=""):
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

    plt.savefig(filename)
    plt.clf()


def plot_single(x, y, rule):
    axes = plt.gca()
    axes.set_xlim([0, 1])
    plt.xlabel(rule)
    axes.set_ylim([0, 1])
    plt.ylabel('approximation ratio')
    plt.plot(x, y)


def plot_dots(filename, x, y, rules, title=""):
    rule1_name = rules[0].__str__()
    rule2_name = rules[1].__str__()

    plt.xlabel(rule2_name)
    plt.ylabel(rule1_name)
    plt.scatter(x, y, s=3)
    plt.title(title)
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
            for filename in os.listdir(os.path.join(current_dir, dir_name)):
                rep = get_repetition_from_filename(dir_name, filename)
                max_rep = max(max_rep, rep)
    return max_rep


def draw_pareto_chart_from_winner_files(current_dir, m, n, k, multigoal_rule, distribution):
    print("{}, k={}".format(multigoal_rule.__name__, k))
    # We assume that there are "repetitions" files generated for each threshold.
    rule_name = multigoal_rule.__name__
    distribution_name = get_distribution_name(distribution)
    rules = get_multigoal_rules(multigoal_rule)
    if not rules:
        return

    xy = {}

    for dir_name in os.listdir(current_dir):
        dir_pattern = '{}_{}_(\d+)_(\d+)_k{}_n{}_m{}'.format(rule_name, distribution_name, k, n, m)
        r1_r2_match = re.match(dir_pattern, dir_name)
        if r1_r2_match is None:
            continue
        r1 = r1_r2_match.group(1)

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
    y_mean = [np.mean(ys) for _, ys in xy_list]
    y_min = [np.min(ys) for _, ys in xy_list]

    filename = '{}_{}_k{}_n{}_m{}'.format(rule_name, distribution_name, k, n, m)
    title = "voters: {}, candidates: {}, committee size: {}".format(n, m, k)
    plot(filename, x, y_mean, y_min, rules, title=title)


def generate_winner_files_for_pareto(dir_name, configs, multigoal_rule, k, start=70, step=2):
    n_start = count_already_generated(dir_name)

    rules = get_multigoal_rules(multigoal_rule)
    if not rules:
        return

    x = np.array([a for a in range(start, 101, step)])

    for repetition, config in enumerate(configs[n_start:]):
        experiment = MultigoalExperiment(config, dir_name=dir_name)

        for i, r1 in enumerate(x):
            for r2 in range(100, 0, -step):
                experiment.set_multigoal_election(multigoal_rule, k, percent_thresholds=(r1, r2))

                try:
                    experiment.run(n=1, n_start=n_start + repetition + 1,
                                   save_in=False, save_out=False, save_win=True, save_best=True, save_score=True)
                    break
                except CplexSolverError:
                    best_filename = '{}_{}.best'.format(experiment.filename, n_start + repetition + 1)
                    os.remove(os.path.join(dir_name, experiment.filename, best_filename))
                    continue


def draw_pareto_chart_from_winner_files_one_vs_all(rule_name, start, step, m, n, k, distribution):
    distribution_name = get_distribution_name(distribution)

    r2_names = []
    for result_dir_name in os.listdir('.'):
        result_dir_pattern = r'results_{}_{}_(\w+)_k{}_n{}_m{}'.format(start, step, k, n, m)
        if rule_name in result_dir_name and re.match(result_dir_pattern, result_dir_name):
            xy = defaultdict(lambda: [])
            r2_name = result_dir_name.split('_')[3]
            reverse = r2_name.startswith('Multigoal' + rule_name)

            r2_name = r2_name.replace('Multigoal', '')
            r2_name = r2_name.replace(rule_name, '')
            r2_names.append(r2_name)

            for dir_name in os.listdir(result_dir_name):
                dir_pattern = r'\w+_{}_(\d+)_(\d+)_k{}_n{}_m{}'.format(distribution_name, k, n, m)
                r1_r2_match = re.match(dir_pattern, dir_name)
                if r1_r2_match is None:
                    continue

                r1 = r1_r2_match.group(1)

                for filename in os.listdir(os.path.join(result_dir_name, dir_name)):
                    rep = get_repetition_from_filename(dir_name, filename)
                    if not rep:
                        continue

                    win_filename = os.path.join(result_dir_name, dir_name, filename)
                    best_filename = '{}_{}.best'.format(dir_name, rep)
                    best_filename = os.path.join(result_dir_name, dir_name, best_filename)
                    scores = read_scores(win_filename)
                    best = read_scores(best_filename)

                    approx = scores[1] / best[1]
                    xy[r1].append(approx)

            xy_list = list(xy.items())
            xy_list = sorted(xy_list, key=lambda e: int(e[0]))
            x = [float(x) / 100 for x, _ in xy_list]
            y_min = [np.min(ys) for _, ys in xy_list]

            if reverse:
                plot_single(y_min, x, rule_name)
            else:
                plot_single(x, y_min, rule_name)

    title = "voters: {}, candidates: {}, committee size: {}".format(n, m, k)
    filename = '{}_{}_k{}_n{}_m{}'.format(rule_name, distribution_name, k, n, m)
    plt.title(title)
    plt.legend(r2_names)
    plt.savefig(filename)
    plt.clf()


def compute_rule_max(rule_name, n, m, k):
    if rule_name == 'SNTV':
        return n
    if rule_name == 'Bloc':
        return k * n
    if rule_name == 'Chamberlin-Courant':
        return (m - 1) * n
    if rule_name == 'k-Borda':
        return k * (m - 1) * n
    return 0


def draw_pareto_chart_from_winner_files_dots(current_dir, m, n, k, multigoal_rule, distribution):
    print("{}, k={}".format(multigoal_rule.__name__, k))
    rule_name = multigoal_rule.__name__
    distribution_name = get_distribution_name(distribution)
    rules = get_multigoal_rules(multigoal_rule)

    rule_1_max = compute_rule_max(str(rules[0]), n, m, k)
    rule_2_max = compute_rule_max(str(rules[1]), n, m, k)

    if not rules:
        return

    x = []
    y = []

    for dir_name in os.listdir(current_dir):
        dir_pattern = r'{}_{}_(\d+)_(\d+)_k{}_n{}_m{}'.format(rule_name, distribution_name, k, n, m)
        r1_r2_match = re.match(dir_pattern, dir_name)
        if r1_r2_match is None:
            continue

        for filename in os.listdir(os.path.join(current_dir, dir_name)):
            rep = get_repetition_from_filename(dir_name, filename)
            if not rep:
                continue

            win_filename = os.path.join(current_dir, dir_name, filename)
            best_filename = '{}_{}.best'.format(dir_name, rep)
            best_filename = os.path.join(current_dir, dir_name, best_filename)

            scores = read_scores(win_filename)
            best = read_scores(best_filename)

            best_mis_score_1 = rule_1_max - best[0]
            best_mis_score_2 = rule_2_max - best[1]

            mis_score_1 = rule_1_max - scores[0]
            mis_score_2 = rule_2_max - scores[1]

            x.append(mis_score_2 / best_mis_score_2)
            y.append(mis_score_1 / best_mis_score_1)

    filename = '{}_{}_k{}_n{}_m{}_dots'.format(rule_name, distribution_name, k, n, m)
    title = "voters: {}, candidates: {}, committee size: {}".format(n, m, k)
    plot_dots(filename, x, y, rules, title=title)

