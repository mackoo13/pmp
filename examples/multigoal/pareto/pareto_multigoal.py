import os

from pmp.experiments import generate_uniform
from pmp.multigoal import MultigoalExperimentConfig, MultigoalExperiment, generate_winner_files_for_pareto, \
    draw_pareto_chart_from_winner_files
from pmp.multigoal.helpers import get_distribution_name
from pmp.rules import MultigoalCCBorda


def make_dir(out_dirname, curr_dir):
    directory = os.path.join(curr_dir, 'results', out_dirname)
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

repetitions = 4
k = 5
n = 20
m = 10
multigoal_rule = MultigoalCCBorda
distribution = generate_uniform

start = 90
step = 2

config = MultigoalExperimentConfig()
config.add_candidates(lambda: distribution(-3, -3, 3, 3, m, 'None'))
config.add_voters(lambda: distribution(-3, -3, 3, 3, n, 'None'))
config.set_distribution_name(get_distribution_name(distribution))

generate_winner_files_for_pareto(config, multigoal_rule, k, repetitions, start=start, step=step)
draw_pareto_chart_from_winner_files('results', m, n, k, multigoal_rule, distribution)
