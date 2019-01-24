from pmp.experiments import generate_uniform
from pmp.multigoal import MultigoalExperimentConfig, MultigoalExperiment
from pmp.multigoal.helpers import get_distribution_name
from pmp.multigoal.visualize import draw_histogram, visualize_elections
from pmp.rules import MultigoalCCBorda

# Configuration
m = 200   # candidates number
n = 200   # voters number
k = 20   # committee_size
repetitions = 33
multigoal_rule = MultigoalCCBorda
percentages = [90, 90]

distribution = generate_uniform
methods = ['ILP', 'Approx_P', 'Approx_Greedy']

config = MultigoalExperimentConfig()
config.add_candidates(lambda: distribution(-3, -3, 3, 3, m, 'None'))
config.add_voters(lambda: distribution(-3, -3, 3, 3, n, 'None'))
config.set_distribution_name(get_distribution_name(distribution))

experiment = MultigoalExperiment(config)
experiment.set_multigoal_election(multigoal_rule, k, percent_thresholds=percentages)
experiment.run(visualization=True, n=repetitions, methods=methods)

out_dir = experiment.get_generated_dir_path()
for method in methods:
    draw_histogram(out_dir, multigoal_rule, k, percentages, distribution, repetitions, n, m, method)
visualize_elections(out_dir)
