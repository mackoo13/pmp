from pmp.experiments import generate_uniform, generate_gauss, generate_circle, generate_winner_files, draw_histogram, \
    delete_winner_files
from pmp.rules import MultigoalBlocBorda as BB, MultigoalTBloc
from pmp.rules import MultigoalCCBorda as CCB
import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)


# Configuration
m = 2   # candidates number
n = 200   # voters number
k = 2   # committee_size

distributions = [generate_uniform, generate_circle, generate_gauss]
repetitions = 500
rules = [MultigoalTBloc, ]
# percentages = [(0, 100), (80, 80), (90, 90), (90, 95), (95, 90), (100, 0), ]    # BB, CCB
# percentages = [(80, 80, 80), (90, 90, 90), (90, 95, 90), (95, 90, 90), (90, 90, 95), (100, 0, 0), (0, 100, 0), (0, 0, 100), ]
th = [0] * (k - 1)
th.append(100)
percentages = [[95] * k, th, ]

for multigoal_rule in rules:
    for distribution in distributions:
        for per in percentages:
            generate_winner_files(current_dir, m, n, k, multigoal_rule, per, distribution, repetitions, log_errors=True)
            draw_histogram(current_dir, multigoal_rule, k, per, distribution, repetitions)
            delete_winner_files(current_dir, multigoal_rule, k, per, distribution, repetitions)

