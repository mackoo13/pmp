from pmp.experiments import generate_uniform, generate_winner_files, draw_histogram, delete_winner_files
from pmp.rules import MultigoalCCBorda
import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)


# Configuration
m = 80   # candidates number
n = 30   # voters number
k = 9   # committee_size

multigoal_rule = MultigoalCCBorda

r1_percentage = 90
r2_percentage = 90
distribution = generate_uniform

repetitions = 99

for method in ('ILP', 'Approx_P', 'Approx_Greedy'):
    out_dir = os.path.join(current_dir, method)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    generate_winner_files(out_dir, m, n, k, multigoal_rule, [r1_percentage, r2_percentage], distribution,
                          repetitions, log_errors=True, method=method)
    draw_histogram(out_dir, MultigoalCCBorda, k, [r1_percentage, r2_percentage], distribution, repetitions)
    delete_winner_files(out_dir, multigoal_rule, k, [r1_percentage, r2_percentage], distribution, repetitions)

