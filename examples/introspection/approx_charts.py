from pmp.experiments import generate_uniform, generate_urn, generate_winner_files, delete_winner_files
from pmp.experiments.multigoal_charts import draw_approximation_charts
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
ms = [51]
k_intervals = 20
k_percs = np.array(range(1, k_intervals)) / float(k_intervals)

if k_intervals > max(ms):
    raise ValueError

methods = ('Approx_P', 'Approx_Greedy')
multigoal_rule = MultigoalCCBorda
distribution = generate_urn
# distribution = generate_uniform

repetitions = 5
res = {}
for method in methods:
    res[method] = np.zeros((len(ms), len(k_percs)))

for im, m in enumerate(ms):
    for ik, k_perc in enumerate(k_percs):
        k = int(k_perc * m)
        print('m={}, k={} ({})'.format(m, k, k_perc))

        approximations = generate_winner_files(tmp_dir, m, n, k, multigoal_rule, [100, 100], distribution,
                                               repetitions, log_errors=True, methods=methods,
                                               approximation=True, return_approximations=True)
        delete_winner_files(tmp_dir)

        for method in methods:
            res[method][im, ik] = np.mean(np.min(approximations[method], axis=1))

draw_approximation_charts(out_dir, ms, k_percs, res)
