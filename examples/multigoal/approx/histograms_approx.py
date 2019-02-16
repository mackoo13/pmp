from pmp.experiments import generate_uniform
from pmp.multigoal import MultigoalExperimentConfig, MultigoalExperiment
from pmp.multigoal.approximation import calculate_approx
from pmp.multigoal.helpers import get_distribution_name
from pmp.rules import MultigoalCCBorda
import os

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)

# Configuration
m = 10   # candidates number
n = 20   # voters number
k = 3   # committee_size

methods = ['Approx_P', 'Approx_Greedy']
multigoal_rule = MultigoalCCBorda
thresholds = [10, 10]

distribution = generate_uniform

repetitions = 3

config = MultigoalExperimentConfig()
config.add_candidates(lambda: distribution(-3, -3, 3, 3, m, 'None'))
config.add_voters(lambda: distribution(-3, -3, 3, 3, n, 'None'))
config.set_distribution_name(get_distribution_name(distribution))

experiment = MultigoalExperiment(config)
experiment.set_multigoal_election(MultigoalCCBorda, k, percent_thresholds=thresholds)
experiment.run(n=repetitions, methods=methods, cplex_trials=5)

approximations = calculate_approx(experiment, methods, repetitions)
# draw_approximation_charts(experiment)
