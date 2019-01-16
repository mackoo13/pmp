import os

import matplotlib.pyplot as plt
import numpy as np
from cplex.exceptions import CplexSolverError
from pmp.MW2D import create_pref_orders

from pmp.experiments import generate_uniform
from pmp.experiments.experiment import preference_orders
from pmp.experiments.visualize import read_data
from pmp.experiments.multigoal_histograms import generate_preference_file, get_distribution_name
from pmp.preferences import Profile
from pmp.rules import Bloc, Borda, ChamberlinCourant
from pmp.rules.utils import get_best_score


def get_profile(voters_number, candidates_number, voters=None, candidates=None):
    if not voters:
        voters = generate_uniform(-3, -3, 3, 3, voters_number, 'None')
    if not candidates:
        candidates = generate_uniform(-3, -3, 3, 3, candidates_number, 'None')
    preferences = preference_orders(candidates, voters)
    candidates = list(range(candidates_number))
    return Profile(candidates, preferences)


def plot(x, y, rule1_name, rule2_name, title=""):
    axes = plt.gca()
    axes.set_xlim([0, 100])
    plt.xlabel(rule2_name)
    axes.set_ylim([0, y[0]])
    plt.ylabel(rule1_name)
    plt.plot(x, y)
    plt.title(title)
    plt.legend(['avg', 'min'])


def get_multigoal_rules(multigoal_rule):
    rule_name = multigoal_rule.__name__
    if rule_name == 'MultigoalBlocBorda':
        return Bloc(), Borda()
    elif rule_name == 'MultigoalCCBorda':
        return ChamberlinCourant(), Borda()
    return ()


def draw_pareto_chart_from_winner_files(current_dir, m, n, k, multigoal_rule, distribution, repetitions, start=70, step=2):
    print("{}, k={}".format(multigoal_rule.__name__, k))
    # We assume that there are "repetitions" files generated for each threshold.
    rule_name = multigoal_rule.__name__
    rules = get_multigoal_rules(multigoal_rule)
    if not rules:
        return

    x = np.array([a for a in range(start, 101, step)])
    y_samples = np.array([np.zeros(repetitions) for _ in x])

    y = np.zeros(len(x))
    mins = np.zeros(len(x))
    maxs = np.zeros(len(x))
    e = np.zeros(len(x))
    for i, r2 in enumerate(x):
        for j in range(repetitions):
            distribution_name = get_distribution_name(distribution)
            in_filename = '{}_{}_{}_k{}-{}.win'.format(rule_name, distribution_name, r2, k, j + 1)
            in_filename = os.path.join(current_dir, in_filename)
            if not os.path.isfile(in_filename):
                break
            with open(in_filename, "r") as f:
                _, _, _, C, V, W = read_data(f)
                profile = get_profile(n, m, voters=V, candidates=C)
                rule1_best = get_best_score(rules[0], profile, k)
                y_samples[i][j] = multigoal_rule((0, 0)).committee_score(W, profile)[0] / float(rule1_best) * 100
        y[i] = np.mean(y_samples[i])
        mins[i] = np.min(y_samples[i])
        maxs[i] = np.max(y_samples[i])
        e[i] = np.std(y_samples[i])
        print("r1: {:3.0f}% - r2: {:3.0f}%, r2_min: {:10.3f}, error: {:10.3f}".format(r2, y[i], mins[i], e[i]))
        if y[i] == 0:
            break

    title = "voters: {}, candidates: {}, committee size: {}".format(n, m, k)
    label1 = rules[0].__str__()
    label2 = rules[1].__str__()

    plot(x, y, label1, label2, title=title)
    plot(x, mins, label1, label2, title=title)
    plt.savefig(current_dir)
    plt.clf()


def generate_winner_files_for_pareto(current_dir, m, n, k, multigoal_rule, distribution, repetitions, log_errors=False,
                                     start=70, step=2):
    tmp_filename = 'tmp.in'
    tmp_filename = os.path.join(current_dir, tmp_filename)

    rule_name = multigoal_rule.__name__
    rules = get_multigoal_rules(multigoal_rule)
    if not rules:
        return

    x = np.array([a for a in range(start, 101, step)])

    for i, r2 in enumerate(x):
        repetition = 1
        while repetition <= repetitions:
            for r1 in range(100, 0, -step):
                # Generating candidates, voters and their preferences
                distribution_name, profile, candidates_map = generate_preference_file(distribution, tmp_filename, m, n)

                rule1_best = get_best_score(rules[0], profile, k)
                rule2_best = get_best_score(rules[1], profile, k)
                rule1_threshold = rule1_best * r1 / 100
                rule2_threshold = rule2_best * r2 / 100

                out_filename = '{}_{}_{}_k{}-{}.win'.format(rule_name, distribution_name, r2, k, repetition)
                out_filename = os.path.join(current_dir, out_filename)
                if os.path.isfile(out_filename):
                    repetition += 1
                    break

                rule = multigoal_rule((rule1_threshold, rule2_threshold), log_errors=log_errors)
                try:
                    committee = list(rule.find_committees(k, profile, method='ILP'))

                    # Generating winners file
                    with open(out_filename, 'w') as out_file:
                        preference = create_pref_orders(tmp_filename, k)
                        out_file.write(preference)
                        for c in committee:
                            out_file.write('{}\t{} {}\n'.format(c, candidates_map[c][0], candidates_map[c][1]))
                    print('Generated: {}'.format(out_filename))
                    repetition += 1
                    break
                except CplexSolverError:
                    continue

    os.remove(tmp_filename)
