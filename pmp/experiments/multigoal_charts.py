import os
import matplotlib.pyplot as plt
import numpy as np
from cplex.exceptions import CplexSolverError

from pmp.experiments import generate_uniform
from pmp.experiments.experiment import preference_orders
from pmp.preferences import Profile
from pmp.rules.utils import get_best_score


def get_profile(voters_number, candidates_number):
    voters = generate_uniform(-3, -3, 3, 3, voters_number, 'None')
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


def draw_chart(filename, k, n, m, repetitions, rule1, rule2, multigoal_rule, start=70, step=5, log_errors=True):
    print('----------------------------------------------------------')
    print multigoal_rule.__name__, ', committee size:', k
    print('----------------------------------------------------------')
    x = np.array([a for a in range(start, 101, step)])
    y_samples = np.array([np.zeros(repetitions) for _ in x])

    y = np.zeros(len(x))
    mins = np.zeros(len(x))
    maxs = np.zeros(len(x))
    e = np.zeros(len(x))
    for i, r2 in enumerate(x):
        for j in range(repetitions):
            for r1 in range(100, 0, -step):
                profile = get_profile(n, m)
                rule1_best = get_best_score(rule1, profile, k)
                rule2_best = get_best_score(rule2, profile, k)
                rule1_threshold = rule1_best * r1 / 100
                rule2_threshold = rule2_best * r2 / 100
                rule = multigoal_rule((rule1_threshold, rule2_threshold), log_errors=log_errors)
                try:
                    committee = list(rule.find_committees(k, profile, method='ILP'))
                    y_samples[i][j] = rule.committee_score(committee, profile)[0] / float(rule1_best) * 100
                    break
                except CplexSolverError:
                    continue
        y[i] = np.mean(y_samples[i])
        mins[i] = np.min(y_samples[i])
        maxs[i] = np.max(y_samples[i])
        e[i] = np.std(y_samples[i])
        print("r1: {:3.0f}% - r2: {:3.0f}%, r2_min: {:10.3f}, error: {:10.3f}".format(r2, y[i], mins[i], e[i]))
        if y[i] == 0:
            break

    title = "voters: {}, candidates: {}, committee size: {}".format(n, m, k)
    label1 = rule1.__str__()
    label2 = rule2.__str__()

    plot(x, y, label1, label2, title=title)
    plot(x, mins, label1, label2, title=title)
    plt.savefig(filename)
    plt.clf()


def draw_approximation_charts(out_dir, ms, k_percs, res):
    for im, m in enumerate(ms):
        filename = os.path.join(out_dir, 'approx_m{}'.format(m))
        ks = k_percs * m

        axes = plt.gca()

        axes.set_xlim([0, m])
        axes.set_ylim([0, 1])

        plt.xlabel('k')
        plt.ylabel('approximation')

        plt.plot(ks, res['Approx_Greedy'][im, :])
        plt.plot(ks, res['Approx_P'][im, :])
        plt.legend(['Greedy', 'P'])
        plt.title('Approximation in CC+kB')
        plt.savefig(filename)
        plt.clf()