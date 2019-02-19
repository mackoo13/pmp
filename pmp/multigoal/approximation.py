import os
import matplotlib.pyplot as plt
import numpy as np
from pmp.multigoal.helpers import get_distribution_name, read_scores


def get_winner_scores(out_dir, file_prefix, method, rep):
    score_file_name = '{}_{}_{}.score'.format(file_prefix, method, rep)
    score_file_path = os.path.join(out_dir, score_file_name)
    return read_scores(score_file_path)


def get_best_scores(out_dir, file_prefix, rep):
    best_file_name = '{}_{}.best'.format(file_prefix, rep)
    best_file_path = os.path.join(out_dir, best_file_name)
    return read_scores(best_file_path)


def calculate_approx(experiment, methods, reps):
    file_prefix = experiment.filename
    out_dir = experiment.get_generated_dir_path()
    n_rules = experiment.n_rules()

    res = np.zeros((len(methods), n_rules, reps))

    for rep in range(1, reps+1):
        optimal_scores = get_best_scores(out_dir, file_prefix, rep)

        for i, method in enumerate(methods):
            approx_score = get_winner_scores(out_dir, file_prefix, method, rep)
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


def calculate_approx_ccborda_ratio(out_dir, file_prefixes, methods, reps):
    res = np.zeros((len(methods), len(file_prefixes), 2, reps))

    for rep in range(1, reps+1):
        optimal_scores = get_best_scores(out_dir, file_prefixes[0], rep)

        for fi, file_prefix in enumerate(file_prefixes):
            for mi, method in enumerate(methods):
                approx_score = get_winner_scores(out_dir, file_prefix, method, rep)
                res[mi, fi, :, rep-1] = approx_score / optimal_scores

    return res


def draw_approx_ccborda_ratio(res, methods, k_ccs):
    res = np.mean(res, axis=3)

    for mi, method in enumerate(methods):
        filename = 'approx_{}'.format(method)

        axes = plt.gca()
        axes.set_ylim([0, 1.1])
        plt.xlabel('Committee members selected by CC')
        plt.ylabel('approximation')

        plt.plot(k_ccs, res[mi, :, 0])
        plt.plot(k_ccs, res[mi, :, 1])
        plt.legend(['CC', 'kB'])
        plt.title('Approximation in CC+kB ({})'.format(method))
        plt.savefig(filename)
        plt.clf()


def draw_approx_ccborda_pareto(res, methods, k_ccs):
    res = np.min(res, axis=3)
    k_ccs = ['   k_CC={}'.format(kcc) for kcc in k_ccs]

    for mi, method in enumerate(methods):
        filename = 'approx_pareto_{}'.format(method)

        # axes = plt.gca()
        # axes.set_xlim([0, 1.1])
        # axes.set_ylim([0, 1.1])
        plt.xlabel('CC')
        plt.ylabel('k-Borda')

        plt.plot(res[mi, :, 0], res[mi, :, 1], '.-')
        for ki, k_cc in enumerate(k_ccs):
            plt.annotate(k_cc, (res[mi, ki, 0], res[mi, ki, 1]), fontsize='xx-small')
        plt.title('Approximation in CC+kB ({})'.format(method))
        plt.savefig(filename)
        plt.clf()
