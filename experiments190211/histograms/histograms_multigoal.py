# noinspection PyUnresolvedReferences
from pmp.experiments import generate_uniform, generate_circle, generate_gauss
from pmp.multigoal import MultigoalExperimentConfig, MultigoalExperiment
from pmp.multigoal.helpers import get_distribution_name
from pmp.multigoal.visualize import draw_histogram
from pmp.rules import MultigoalTBloc

m = 100   # candidates number
n = 100   # voters number
k = 10   # committee_size
repetitions = 3
multigoal_rule = MultigoalTBloc
percentages = [0] * k

distribution = generate_uniform
# distribution = generate_gauss
methods = ['ILP']

config = MultigoalExperimentConfig()
config.add_candidates(lambda: distribution(-3, -3, 3, 3, m, 'None'))
config.add_voters(lambda: distribution(-3, -3, 3, 3, n, 'None'))
# config.add_candidates(lambda: distribution(0, 0, 1, m, 'None'))
# config.add_voters(lambda: distribution(0, 0, 1, n, 'None'))
config.set_distribution_name(get_distribution_name(distribution))

experiment = MultigoalExperiment(config)
experiment.set_multigoal_election(multigoal_rule, k, percent_thresholds=percentages)
experiment.run(visualization=True, n=repetitions, methods=methods,
               save_win=True, save_in=False, save_out=False, save_best=True, save_score=True)

out_dir = experiment.get_generated_dir_path()
for method in methods:
    draw_histogram(out_dir, multigoal_rule, k, percentages, distribution, repetitions, n, m, method)
