from pmp.experiments import generate_uniform, generate_gauss, generate_circle, generate_winner_files, draw_histogram, \
    delete_winner_files
from pmp.experiments.multigoal_histograms import visualize_elections
from pmp.rules import MultigoalBlocBorda, MultigoalTBloc,  MultigoalCCBorda
import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
out_dir = os.path.join(current_dir, 'tmp_results')
if not os.path.exists(out_dir):
    os.mkdir(out_dir)

# Configuration
m = 200   # candidates number
n = 200   # voters number
k = 20   # committee_size

repetitions = 1000
distributions = (generate_circle, generate_gauss)
rules = (MultigoalTBloc, )

# BB, CCb percentages
# percentages = ((0, 0),)    # BB, CCB

# Multibloc percentages
# percentages = [[0] * (k - 1) + [100],
#                [100] + [0] * (k - 1),
#                [0] + [i for i in range(0, 96, 5)],
#                [i for i in range(95, -1, -5)] + [0],
#                [85] * k,
#                [0] * (k / 2) + [95] * (k / 2),
#                [90] * (k / 2) + [0] * (k / 2), ]
percentages = [[0] * k, ]

for multigoal_rule in rules:
    for distribution in distributions:
        for per in percentages:
            generate_winner_files(out_dir, m, n, k, multigoal_rule, per, distribution, repetitions, log_errors=True)
            draw_histogram(out_dir, multigoal_rule, k, per, distribution, repetitions)
            visualize_elections(out_dir, elections_num=1)
            delete_winner_files(out_dir)

