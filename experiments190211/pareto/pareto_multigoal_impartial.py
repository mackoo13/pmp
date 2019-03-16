import os
from pmp.experiments import impartial
from pmp.multigoal import MultigoalExperimentConfig, generate_winner_files_for_pareto, \
    draw_pareto_chart_from_winner_files
from pmp.multigoal.helpers import get_distribution_name
# noinspection PyUnresolvedReferences
from pmp.rules import MultigoalCCBorda, MultigoalBlocBorda, MultigoalBlocSNTV, MultigoalBordaSNTV

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

repetitions = 19
k = 5
n = 20
m = 20

multigoal_rule = MultigoalCCBorda
# multigoal_rule = MultigoalBlocBorda
# multigoal_rule = MultigoalBordaSNTV
# multigoal_rule = MultigoalBlocSNTV
distribution = impartial
distribution_name = get_distribution_name(distribution)

start = 80
step = 1
dir_name = 'results_{}_{}_{}_{}_k{}_n{}_m{}'.format(start, step, multigoal_rule.__name__, distribution_name, k, n, m)

configs = []
for _ in range(repetitions):
    config = MultigoalExperimentConfig()
    config.impartial(m, n)
    config.set_distribution_name(distribution_name)

    configs.append(config)

generate_winner_files_for_pareto(dir_name, configs, multigoal_rule, k, start=start, step=step)
draw_pareto_chart_from_winner_files(dir_name, m, n, k, multigoal_rule, distribution)
