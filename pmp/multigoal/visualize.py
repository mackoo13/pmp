import os

from pmp.MW2D import mw2d_generate_histogram, mw2d_draw_histogram
from pmp.multigoal.helpers import get_distribution_name


def draw_histogram(out_dir, multigoal_rule, k, percentages, distribution, reps, n, m, method, threshold=None):
    distribution_name = get_distribution_name(distribution)
    perc = '_'.join([str(p) for p in percentages])

    winner_filename = '{}_{}_{}_k{}_n{}_m{}_{}'.format(multigoal_rule.__name__, distribution_name, perc, k, n, m, method)
    file_path = os.path.join(out_dir, winner_filename)
    mw2d_generate_histogram(file_path, reps)

    histogram_filename = file_path + '.hist'
    mw2d_draw_histogram(histogram_filename, threshold)

    os.remove(histogram_filename)