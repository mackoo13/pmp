import os
from pmp.experiments import generate_uniform
from pmp.multigoal import MultigoalExperimentConfig, generate_winner_files_for_pareto, \
    draw_pareto_chart_from_winner_files, draw_pareto_chart_from_winner_files_one_vs_all, \
    draw_pareto_chart_from_winner_files_dots
from pmp.multigoal.helpers import get_distribution_name
from pmp.rules import MultigoalCCBorda, MultigoalBlocBorda

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

repetitions = 1
k = 10
n = 100
m = 100
multigoal_rule = MultigoalCCBorda
distribution = generate_uniform

start = 70
step = 2
dir_name = 'results_{}_{}_{}_{}_k{}_n{}_m{}'.format(start, step, multigoal_rule.__name__,
                                                    get_distribution_name(distribution), k, n, m)

configs = []
for _ in range(repetitions):
    config = MultigoalExperimentConfig()
    config.add_candidates(distribution(-3, -3, 3, 3, m, 'None'))
    config.add_voters(distribution(-3, -3, 3, 3, n, 'None'))
    config.set_distribution_name(get_distribution_name(distribution))

    configs.append(config)

generate_winner_files_for_pareto(dir_name, configs, multigoal_rule, k, start=start, step=step)
draw_pareto_chart_from_winner_files(dir_name, m, n, k, multigoal_rule, distribution)
draw_pareto_chart_from_winner_files_one_vs_all('Borda', 90, 2, m, n, k, distribution)
draw_pareto_chart_from_winner_files_dots(dir_name, m, n, k, multigoal_rule, distribution)

