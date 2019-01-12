from pmp.experiments import generate_uniform, generate_winner_files, draw_histogram, delete_winner_files
from pmp.experiments.multigoal_histograms import visualize_elections
from pmp.rules import MultigoalBlocBorda as BB
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

multigoal_rule = BB

r1_percentage = 90
r2_percentage = 90
distribution = generate_uniform

repetitions = 2


generate_winner_files(out_dir, m, n, k, multigoal_rule, [r1_percentage, r2_percentage], distribution,
                      repetitions, log_errors=True)
draw_histogram(out_dir, multigoal_rule, k, [r1_percentage, r2_percentage], distribution, repetitions)
visualize_elections(out_dir)
delete_winner_files(out_dir)

