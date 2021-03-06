import os
from pmp.experiments import generate_uniform
from pmp.multigoal import MultigoalExperimentConfig, generate_winner_files_for_pareto, \
    draw_pareto_chart_from_winner_files
from pmp.multigoal.helpers import get_distribution_name
from pmp.rules import MultigoalCCBorda


current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

repetitions = 1
k = 5
n = 20
m = 20
multigoal_rule = MultigoalCCBorda
distribution = generate_uniform

start = 90
step = 2
dir_name = 'results_{}_{}_{}_k{}_n{}_m{}'.format(start, step, multigoal_rule.__name__, k, n, m)

configs = []
for _ in range(repetitions):
    config = MultigoalExperimentConfig()
    config.add_candidates(distribution(-3, -3, 3, 3, m, 'None'))
    config.add_voters(distribution(-3, -3, 3, 3, n, 'None'))
    config.set_distribution_name(get_distribution_name(distribution))

    configs.append(config)

generate_winner_files_for_pareto(dir_name, configs, multigoal_rule, k, start=start, step=step)
draw_pareto_chart_from_winner_files(dir_name, m, n, k, multigoal_rule, distribution)
