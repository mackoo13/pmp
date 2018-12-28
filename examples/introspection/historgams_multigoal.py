from pmp.experiments import generate_uniform, generate_winner_files, draw_histogram, delete_winner_files
from pmp.rules import MultigoalBlocBorda as BB, Bloc, Borda, ChamberlinCourant
from pmp.rules import MultigoalCCBorda as CCB
import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)


# Configuration
m = 100   # candidates number
n = 200   # voters number
k = 20   # committee_size

multigoal_rule = BB
rule1 = Bloc
rule2 = Borda

# multigoal_rule = CCB
# rule1 = ChamberlinCourant
# rule2 = Borda

r1_percentage = 100
r2_percentage = 0
distribution = generate_uniform
repetitions = 500

generate_winner_files(current_dir, m, n, k, multigoal_rule, rule1, rule2, r1_percentage, r2_percentage, distribution, repetitions)
draw_histogram(current_dir, multigoal_rule, k, r1_percentage, r2_percentage, repetitions)
delete_winner_files(current_dir, multigoal_rule, k, r1_percentage, r2_percentage, repetitions)

