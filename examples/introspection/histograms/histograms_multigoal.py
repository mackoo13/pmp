from pmp.experiments import generate_uniform, generate_winner_files, draw_histogram, delete_winner_files
from pmp.experiments.multigoal_histograms import visualize_elections
from pmp.rules import MultigoalBlocBorda as BB
import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

# Configuration
m = 200   # candidates number
n = 200   # voters number
k = 20   # committee_size

multigoal_rule = BB

r1_percentage = 0
r2_percentage = 0
distribution = generate_uniform

repetitions = 1000


out_dirname = '{}_{}_{}_{}_k{}_n{}_m{}'.format(multigoal_rule.__name__, distribution.__name__,
                                               r1_percentage, r2_percentage, k, n, m)
out_dir = os.path.join(current_dir, 'results', out_dirname)
if not os.path.exists(out_dir):
    os.makedirs(out_dir)


generate_winner_files(out_dir, m, n, k, multigoal_rule, [r1_percentage, r2_percentage], distribution,
                      repetitions, log_errors=True)
draw_histogram(out_dir, multigoal_rule, k, [r1_percentage, r2_percentage], distribution, repetitions, n, m)
visualize_elections(out_dir)

