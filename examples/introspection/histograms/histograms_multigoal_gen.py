from pmp.experiments import generate_uniform, generate_gauss, generate_circle, generate_winner_files, draw_histogram, \
    delete_winner_files
from pmp.experiments.multigoal_histograms import visualize_elections
from pmp.rules import MultigoalBlocBorda, MultigoalTBloc,  MultigoalCCBorda
import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

# Configuration
m = 200   # candidates number
n = 200   # voters number
k = 20   # committee_size

repetitions = 200
distributions = (generate_uniform, generate_circle, generate_gauss)
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
            out_dirname = '{}_{}_{}_{}_k{}'.format(multigoal_rule.__name__, distribution.__name__, per[0], per[1], k)
            out_dir = os.path.join(current_dir, 'results')
            out_dir = os.path.join(out_dir, out_dirname)
            if not os.path.exists(out_dir):
                os.mkdir(out_dir)

            generate_winner_files(out_dir, m, n, k, multigoal_rule, per, distribution, repetitions, log_errors=True)
            draw_histogram(out_dir, multigoal_rule, k, per, distribution, repetitions)
            visualize_elections(out_dir, elections_num=1)

