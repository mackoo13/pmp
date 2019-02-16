import os
from pmp.experiments import mallows
from pmp.multigoal import MultigoalExperimentConfig, generate_winner_files_for_pareto, \
    draw_pareto_chart_from_winner_files
from pmp.multigoal.helpers import get_distribution_name
from pmp.rules import MultigoalBlocBorda

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

repetitions = 4
k = 10
n = 100
m = 100
phi = 0.1

multigoal_rule = MultigoalBlocBorda
distribution = mallows
distribution_name = get_distribution_name(distribution)

start = 90
step = 2
dir_name = 'results_{}_{}_{}_{}_phi{}_k{}_n{}_m{}'.format(start, step, multigoal_rule.__name__, distribution_name, phi,
                                                          k, n, m)

configs = []
for _ in range(repetitions):
    config = MultigoalExperimentConfig()
    config.mallows(phi, m, n)
    config.set_distribution_name(distribution_name)

    configs.append(config)

generate_winner_files_for_pareto(dir_name, configs, multigoal_rule, k, start=start, step=step)
draw_pareto_chart_from_winner_files(dir_name, m, n, k, multigoal_rule, distribution)