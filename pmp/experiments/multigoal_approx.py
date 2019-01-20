import os
import matplotlib.pyplot as plt
import numpy as np

from pmp.MW2D import create_pref_orders
from pmp.experiments import generate_winner_files
from pmp.experiments.distributions import get_distribution_name
from pmp.experiments.read_files import read_preferences


def read_pref_file(in_filename):
    with open(in_filename, 'r') as f:
        lines = f.readlines()
        n = lines[0].strip()
        n = int(n)

        preferences = read_preferences(lines[1:n+1])

        return preferences


def generate_approx_files(current_dir, methods, multigoal_rule, distribution, perc, k, n, m, reps):
    rule_name = multigoal_rule.__name__
    distribution_name = get_distribution_name(distribution)

    file_prefix = '{}_{}_{}_k{}_n{}_m{}_{}'.format(rule_name, distribution_name, perc, k, n, m, repetition)
    in_filename = os.path.join(current_dir, file_prefix + '.in')
    pref_filename = os.path.join(current_dir, file_prefix + '.pref')

    candidates, voters = read_in_file(in_filename)
    profile, candidates_map = read_pref_file(pref_filename)

    rule = multigoal_rule([100] * 2)

    for method in methods:
        out_filename = '{}_{}'.format(file_prefix, method)
        win_filename = os.path.join(current_dir, out_filename + '.win')
        score_filename = os.path.join(current_dir, out_filename + '.score')

        committee = list(rule.find_committees(k, profile, method=method))

        # Creating winners file
        with open(win_filename, 'w') as out_file:
            preference = create_pref_orders(in_filename, k)
            out_file.write(preference)
            for c in committee:
                out_file.write('{}\t{} {}\n'.format(c, candidates_map[c][0], candidates_map[c][1]))

        # Creating score file
        with open(score_filename, 'w') as out_file:
            out_file.write(' '.join(rule.committee_score(committee, profile).astype('str')))


def calculate_approx(win_dir, methods, multigoal_rule, distribution, perc, k, n, m, reps):
    generate_winner_files(win_dir, m, n, k, multigoal_rule, perc, distribution, reps, log_errors=True)
    # generate_winner_files(win_dir, m, n, k, multigoal_rule, perc, distribution, reps, log_errors=True, methods=methods)

    distribution_name = get_distribution_name(distribution)
    perc_str = '_'.join([str(p) for p in perc])

    # noinspection PyShadowingNames
    def score_file_path(method, rep):
        winner_filename = '{}_{}_{}_k{}_n{}_m{}_{}_{}.score'.format(
            multigoal_rule.__name__, distribution_name, perc_str, k, n, m, method, rep)
        return os.path.join(win_dir, winner_filename)

    def get_winner_scores(method, rep):
        with open(score_file_path(method, rep), 'r') as f_ilp:
            scores = f_ilp.read().strip().split()
            scores = np.array(scores).astype('float')
        return scores

    res = np.zeros((len(methods), len(perc), reps))

    for rep in range(1, reps+1):
        optimal_scores = get_winner_scores('Best_Scores', rep)

        for i, method in enumerate(methods):
            approx_score = get_winner_scores(method, rep)
            res[i, :, rep-1] = approx_score / optimal_scores

    res = np.min(res, axis=1)
    res = np.mean(res, axis=1)
    return res


def draw_approximation_charts(out_dir, ms, k_percs, distribution, res):
    distribution_name = get_distribution_name(distribution)

    for im, m in enumerate(ms):
        filename = os.path.join(out_dir, 'approx_{}_m{}'.format(distribution_name, m))
        ks = k_percs * m

        axes = plt.gca()

        axes.set_xlim([0, m])
        axes.set_ylim([0, 1.1])

        plt.xlabel('k')
        plt.ylabel('approximation')

        plt.plot(ks, res['Approx_Greedy'][im, :])
        plt.plot(ks, res['Approx_P'][im, :])
        plt.legend(['Greedy', 'P'])
        plt.title('Approximation in CC+kB')
        plt.savefig(filename)
        plt.clf()
