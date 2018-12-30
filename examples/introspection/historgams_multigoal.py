from pmp.experiments import generate_uniform, generate_winner_files, draw_histogram, delete_winner_files
from pmp.rules import MultigoalBlocBorda as BB, Bloc, Borda, ChamberlinCourant
from pmp.rules import MultigoalCCBorda as CCB
import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)


# Configuration
m = 2   # candidates number
n = 200   # voters number
k = 20   # committee_size

multigoal_rule = BB
rule1 = Bloc
rule2 = Borda

# multigoal_rule = CCB
# rule1 = ChamberlinCourant
# rule2 = Borda

r1_percentage = 100
r2_percentage = 90
distribution = generate_uniform

repetitions = 1000


generate_winner_files(current_dir, m, n, k, multigoal_rule, [r1_percentage, r2_percentage], distribution,
                      repetitions, log_errors=True)
draw_histogram(current_dir, multigoal_rule, k, [r1_percentage, r2_percentage], distribution, repetitions)
delete_winner_files(current_dir, multigoal_rule, k, [r1_percentage, r2_percentage], distribution, repetitions)

