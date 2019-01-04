from pmp.experiments import generate_uniform, generate_gauss, generate_circle, generate_winner_files, draw_histogram, \
    delete_winner_files
from pmp.rules import MultigoalBlocBorda, MultigoalTBloc,  MultigoalCCBorda
import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)


# Configuration
m = 200   # candidates number
n = 200   # voters number
k = 20   # committee_size

repetitions = 200
distributions = [generate_uniform, generate_circle, generate_gauss]
rules = [MultigoalTBloc, ]

# BB, CCb percentages
# percentages = [(0, 100), (80, 80), (90, 90), (90, 95), (95, 90), (100, 0), ]    # BB, CCB

# Multibloc percentages
percentages = [[0] * (k - 1) + [100],
               [100] + [0] * (k - 1),
               [0] + [i for i in range(0, 96, 5)],
               [i for i in range(95, -1, -5)] + [0],
               [85] * k,
               [0] * (k / 2) + [95] * (k / 2),
               [90] * (k / 2) + [0] * (k / 2), ]

for multigoal_rule in rules:
    for distribution in distributions:
        for per in percentages:
            generate_winner_files(current_dir, m, n, k, multigoal_rule, per, distribution, repetitions, log_errors=True)
            draw_histogram(current_dir, multigoal_rule, k, per, distribution, repetitions)
            delete_winner_files(current_dir, multigoal_rule, k, per, distribution, repetitions)
