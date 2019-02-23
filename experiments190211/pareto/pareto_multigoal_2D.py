import os
from pmp.experiments import generate_uniform
from pmp.multigoal import MultigoalExperimentConfig, generate_winner_files_for_pareto, \
    draw_pareto_chart_from_winner_files, draw_pareto_chart_from_winner_files_one_vs_all, \
    draw_pareto_chart_from_winner_files_dots
from pmp.multigoal.helpers import get_distribution_name
from pmp.rules import MultigoalCCBorda, MultigoalBlocBorda, MultigoalBordaSNTV, MultigoalBlocSNTV
from pmp.rules.multigoal_bloc_cc import MultigoalBlocCC
from pmp.rules.multigoal_borda_bloc import MultigoalBordaBloc
from pmp.rules.multigoal_borda_cc import MultigoalBordaCC
from pmp.rules.multigoal_cc_bloc import MultigoalCCBloc
from pmp.rules.multigoal_cc_sntv import MultigoalCCSNTV
from pmp.rules.multigoal_sntv_bloc import MultigoalSNTVBloc
from pmp.rules.multigoal_sntv_borda import MultigoalSNTVBorda
from pmp.rules.multigoal_sntv_cc import MultigoalSNTVCC

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

repetitions = 100
k = 10
n = 100
m = 100


# multigoal_rules = [MultigoalBlocBorda, MultigoalBordaBloc, MultigoalSNTVBloc, MultigoalBordaSNTV, MultigoalBlocSNTV, MultigoalBordaCC]
multigoal_rules = [MultigoalBordaCC]

distribution = generate_uniform

start = 10
step = 1

# rules = ['Borda', 'Bloc', 'CC', 'SNTV']
# for rule in rules:
#     draw_pareto_chart_from_winner_files_one_vs_all(rule, 10, 1, m, n, k, distribution)
#     draw_pareto_chart_from_winner_files_one_vs_all(rule, 10, 1, m, n, k, distribution, minimum=True)
#     draw_pareto_chart_from_winner_files_dots(rule, 10, 1, m, n, k, distribution)

for multigoal_rule in multigoal_rules:

    configs = []
    dir_name = 'results_{}_{}_{}_{}_k{}_n{}_m{}'.format(start, step, multigoal_rule.__name__,
                                                        get_distribution_name(distribution), k, n, m)

    for _ in range(repetitions):
        config = MultigoalExperimentConfig()
        config.add_candidates(distribution(-3, -3, 3, 3, m, 'None'))
        config.add_voters(distribution(-3, -3, 3, 3, n, 'None'))
        config.set_distribution_name(get_distribution_name(distribution))

        configs.append(config)

        generate_winner_files_for_pareto(dir_name, configs, multigoal_rule, k, start=start, step=step)
        # draw_pareto_chart_from_winner_files(dir_name, m, n, k, multigoal_rule, distribution)

