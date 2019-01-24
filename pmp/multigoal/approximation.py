import os
import matplotlib.pyplot as plt
import numpy as np
from pmp.multigoal.helpers import get_distribution_name


def calculate_approx(experiment, methods, reps):
    file_prefix = experiment.filename
    out_dir = experiment.get_generated_dir_path()
    n_rules = experiment.n_rules()

    def read_scores(file_path):
        with open(file_path, 'r') as f:
            scores = f.read().strip().split()
            scores = np.array(scores).astype('float')
        return scores

    def get_winner_scores(method, rep):
        score_file_name = '{}_{}_{}.score'.format(file_prefix, method, rep)
        score_file_path = os.path.join(out_dir, score_file_name)
        return read_scores(score_file_path)

    def get_best_scores(rep):
        best_file_name = '{}_{}.best'.format(file_prefix, rep)
        best_file_path = os.path.join(out_dir, best_file_name)
        return read_scores(best_file_path)

    res = np.zeros((len(methods), n_rules, reps))

    for rep in range(1, reps+1):
        optimal_scores = get_best_scores(rep)

        for i, method in enumerate(methods):
            approx_score = get_winner_scores(method, rep)
            res[i, :, rep-1] = approx_score / optimal_scores

    res = np.min(res, axis=1)
    res = np.mean(res, axis=1)
    return res


def draw_approximation_charts(experiment, ms, k_percs, distribution, approximations):
    out_dir = experiment.get_generated_dir_path()
    distribution_name = get_distribution_name(distribution)

    for im, m in enumerate(ms):
        filename = os.path.join(out_dir, 'approx_{}_m{}'.format(distribution_name, m))
        ks = k_percs * m

        axes = plt.gca()

        axes.set_xlim([0, m])
        axes.set_ylim([0, 1.1])

        plt.xlabel('k')
        plt.ylabel('approximation')

        plt.plot(ks, approximations['Approx_Greedy'][im, :])
        plt.plot(ks, approximations['Approx_P'][im, :])
        plt.legend(['Greedy', 'P'])
        plt.title('Approximation in CC+kB')
        plt.savefig(filename)
        plt.clf()
