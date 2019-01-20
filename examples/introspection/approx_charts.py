from pmp.experiments import generate_mallows
from pmp.experiments.multigoal_approx import draw_approximation_charts, calculate_approx
from pmp.rules import MultigoalCCBorda
import os
import numpy as np


current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
out_dir = os.path.join(current_dir, 'results_charts', 'approx_charts')
tmp_dir = os.path.join(current_dir, 'results_charts', 'tmp_results')

if not os.path.exists(out_dir):
    os.mkdir(out_dir)
if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

n = 50
ms = [21]
k_intervals = 3
k_percs = np.array(range(1, k_intervals)) / float(k_intervals)

if k_intervals > max(ms):
    raise ValueError

methods = ['Approx_P', 'Approx_Greedy']
distributions = [generate_mallows]
multigoal_rule = MultigoalCCBorda
# distribution = generate_uniform

repetitions = 2
perc = [100, 100]

for distribution in distributions:
    res = np.zeros((len(methods), len(ms), len(k_percs)))

    for im, m in enumerate(ms):
        for ik, k_perc in enumerate(k_percs):
            k = int(k_perc * m)
            print('m={}, k={} (k/m={})'.format(m, k, k_perc))
            approximations = calculate_approx(tmp_dir, methods, multigoal_rule, distribution, perc, k, n, m, repetitions)

            res[:, im, ik] = approximations

    draw_approximation_charts(out_dir, ms, k_percs, distribution, res)
