import os

from pmp.experiments import generate_uniform
from pmp.experiments.multigoal_histograms import get_distribution_name
from pmp.experiments.multigoal_pareto import generate_winner_files_for_pareto, draw_pareto_chart_from_winner_files
from pmp.rules import MultigoalBlocBorda, MultigoalCCBorda


def make_dir(out_dirname, curr_dir):
    directory = os.path.join(curr_dir, 'results')
    directory = os.path.join(directory, out_dirname)
    if not os.path.exists(directory):
        os.mkdir(directory)
    return directory


current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

repetitions = 2
ks = (5, 15, )
n = 20
m = 20
distributions = (generate_uniform, )

for k in ks:
    for distribution in distributions:
        distribution_name = get_distribution_name(distribution)
        rules = ((MultigoalCCBorda, 'MultigoalCCBorda-{}-k{}-n{}-m{}'.format(distribution_name, k, n, m)),
                 (MultigoalBlocBorda, 'MultigoalBlocBorda-{}-k{}-n{}-m{}'.format(distribution_name, k, n, m)))

        for multigoal_rule, filename in rules:
            out_dir = make_dir(filename, current_dir)
            generate_winner_files_for_pareto(out_dir, m, n, k, multigoal_rule, distribution, repetitions, log_errors=True,
                                             start=70, step=2)
            draw_pareto_chart_from_winner_files(out_dir, m, n, k, multigoal_rule, distribution, repetitions, start=70,
                                                step=2)
