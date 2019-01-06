from pmp.experiments import generate_uniform, generate_winner_files, draw_histogram, delete_winner_files
from pmp.rules import MultigoalCCBorda
import os
import numpy as np


# noinspection PyShadowingNames
def approx_report(approximations):
    res = ''

    for method, results in approximations.items():
        res += method + '\n'
        res += '\tmean: {}\n'.format(np.mean(results, axis=0))
        res += '\tstd:  {}\n'.format(np.std(results, axis=0))
        res += '\tmin:  {}\n'.format(np.min(results, axis=0))
        res += '\tmax:  {}\n'.format(np.max(results, axis=0))

    return res


current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
out_dir = os.path.join(current_dir, 'tmp_results')
if not os.path.exists(out_dir):
    os.mkdir(out_dir)


# Configuration
m = 200   # candidates number
n = 200   # voters number
k = 20   # committee_size

methods = ('Approx_P', 'Approx_Greedy')
multigoal_rule = MultigoalCCBorda

r1_percentage = 100
r2_percentage = 100
distribution = generate_uniform

repetitions = 99
return_approximations = True

approximations = generate_winner_files(out_dir, m, n, k, multigoal_rule, [r1_percentage, r2_percentage], distribution,
                                       repetitions, log_errors=True, methods=methods,
                                       approximation=True, return_approximations=return_approximations)
draw_histogram(out_dir, MultigoalCCBorda, k, [r1_percentage, r2_percentage], distribution, repetitions, methods=methods)
delete_winner_files(out_dir)

if return_approximations:
    report = approx_report(approximations)
    print(report)
    with open(os.path.join(out_dir, 'approximations.txt'), 'w') as f:
        f.write(report)
